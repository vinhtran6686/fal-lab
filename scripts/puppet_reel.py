#!/usr/bin/env python3
"""Pose reel tools (docs/scripts/puppet_kit/puppet-kit-pose-reel.md): the padded input canvas of a clip, and cutting a paid clip into frames.

  python scripts/puppet_reel.py input <asset> <still.png> --name master [--mirror] [--match <other canvas name>]
      -> <asset>/.work/reel/<name>_canvas.png : the still at scale S on a flat-key canvas with headroom (one fixed placement
         for every clip of the reel, recorded in <asset>/.work/reel/canvas.json)
  python scripts/puppet_reel.py cut <asset> <clip.mp4> --name turn_a [--fps 15]
      -> <asset>/source/video/reel_<name>.mp4, <asset>/source/rig/reel/<name>/NNN.png + reel.json + check/contact.png
"""
import argparse, json, pathlib, shutil, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageOps

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from puppet_kit.core import key_magenta  # noqa: E402

CANVAS, SCALE, BOTTOM = 1024, 0.70, 60     # canvas side, still scale, margin under the lowest pixel: ~26% headroom


def fg_box(img):
    a = key_magenta(img)[..., 3] > 128
    ys, xs = np.where(a)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def cmd_input(a):
    asset = pathlib.Path(a.asset)
    work = asset / ".work" / "reel"
    work.mkdir(parents=True, exist_ok=True)
    rec_path = work / "canvas.json"
    rec = json.loads(rec_path.read_text()) if rec_path.exists() else {}
    img = Image.open(a.still).convert("RGB")
    if a.mirror:
        img = ImageOps.mirror(img)
    key = img.getpixel((4, 4))
    scale = SCALE
    x0, y0, x1, y1 = fg_box(img)
    if a.match:                              # a still drawn at another size: same body height and feet line as that canvas
        ref = rec[a.match]
        scale = ref["body_h"] / (y1 - y0)
    w, h = round(img.width * scale), round(img.height * scale)
    key = (255, 0, 255)                      # one exact flat key: the still is keyed and laid on it, so no paste seam shows
    rgba = Image.fromarray(key_magenta(img).clip(0, 255).astype(np.uint8), "RGBA")
    flat = Image.new("RGBA", img.size, key + (255,))
    flat.alpha_composite(rgba)
    small = flat.convert("RGB").resize((w, h), Image.LANCZOS)
    canvas = Image.new("RGB", (CANVAS, CANVAS), key)
    feet_y = CANVAS - BOTTOM
    oy = feet_y - round(y1 * scale)
    ox = round(CANVAS / 2 - (x0 + x1) / 2 * scale) if (a.match or a.mirror) else round((CANVAS - w) / 2)
    canvas.paste(small, (ox, oy))
    out = work / f"{a.name}_canvas.png"
    canvas.save(out)
    rec[a.name] = {"still": str(a.still), "scale": scale, "offset": [ox, oy], "mirror": bool(a.mirror), "body_h": (y1 - y0) * scale,
                   "canvas": CANVAS}
    rec_path.write_text(json.dumps(rec, indent=1))
    print(f"wrote {out}: scale {scale:.3f}, offset {ox},{oy}, headroom {oy + y0 * scale:.0f}px")


def cmd_cut(a):
    asset = pathlib.Path(a.asset)
    rec = json.loads((asset / ".work" / "reel" / "canvas.json").read_text())[a.canvas]
    rig = json.loads((asset / "source" / "rig" / "rig.json").read_text(encoding="utf-8"))
    clip = asset / "source" / "video" / f"reel_{a.name}.mp4"
    clip.parent.mkdir(parents=True, exist_ok=True)
    if pathlib.Path(a.clip).resolve() != clip.resolve():
        shutil.copyfile(a.clip, clip)
    job = pathlib.Path(a.clip).parent / "job.json"
    if job.exists():
        shutil.copyfile(job, clip.with_suffix(".json"))
    out = asset / "source" / "rig" / "reel" / a.name
    if out.exists():
        shutil.rmtree(out)
    (out / "check").mkdir(parents=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(clip), "-vf", f"fps={a.fps}", str(out / "%03d.png")], check=True)
    frames = sorted(out.glob("[0-9]*.png"))
    W = Image.open(frames[0]).width
    k = W / rec["canvas"]
    gx, gy = rig["ground"]
    if rec["mirror"]:
        gx = 1024 - gx
    ground = [round((gx * rec["scale"] + rec["offset"][0]) * k, 2), round((gy * rec["scale"] + rec["offset"][1]) * k, 2)]
    unit = round(rig["unit"] * rec["scale"] * k, 2)
    rows, tiles = [], []
    for f in frames:
        im = Image.open(f).convert("RGB")
        al = key_magenta(im)[..., 3] > 128
        ys, xs = np.where(al)
        edge = bool(xs.min() <= 1 or ys.min() <= 1 or xs.max() >= im.width - 2 or ys.max() >= im.height - 2)
        rows.append({"frame": int(f.stem), "body_h": int(ys.max() - ys.min()), "feet_y": int(ys.max()), "cx": round(float(xs.mean()), 1), "edge": edge})
        t = im.resize((240, round(240 * im.height / im.width)), Image.LANCZOS)
        ImageDraw.Draw(t).text((4, 4), f.stem + (" EDGE" if edge else ""), fill=(255, 255, 255))
        tiles.append(t)
    cols = 8
    sheet = Image.new("RGB", (240 * cols, tiles[0].height * ((len(tiles) + cols - 1) // cols)), (40, 40, 40))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * 240, (i // cols) * t.height))
    sheet.save(out / "check" / "contact.png")
    h0 = rows[0]["body_h"]
    doc = {"clip": f"source/video/{clip.name}", "fps": a.fps, "frames": len(frames), "frame_size": [W, Image.open(frames[0]).height],
           "canvas": rec, "ground": ground, "unit": unit,
           "note": "ground and unit come from the main rig through the canvas placement (scale, offset): no per-frame registration.",
           "metrics": rows}
    (out / "reel.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    meta_p = asset / "meta.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    lst = meta.setdefault("sources", {}).setdefault("video", [])
    for n in (clip.name, clip.with_suffix(".json").name):
        if n not in lst and (clip.parent / n).exists():
            lst.append(n)
    lst.sort()
    meta_p.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    hs = [r["body_h"] for r in rows]
    print(f"{a.name}: {len(frames)} frames {W}px; body height {min(hs)}..{max(hs)} (first {h0}); feet y {min(r['feet_y'] for r in rows)}..{max(r['feet_y'] for r in rows)}; "
          f"edge frames {[r['frame'] for r in rows if r['edge']]}; ground {ground}, unit {unit}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    i = sp.add_parser("input"); i.add_argument("asset"); i.add_argument("still"); i.add_argument("--name", required=True)
    i.add_argument("--mirror", action="store_true"); i.add_argument("--match"); i.set_defaults(fn=cmd_input)
    c = sp.add_parser("cut"); c.add_argument("asset"); c.add_argument("clip"); c.add_argument("--name", required=True)
    c.add_argument("--canvas", default="master", help="which input canvas the clip STARTED from (canvas.json key)")
    c.add_argument("--fps", type=int, default=15); c.set_defaults(fn=cmd_cut)
    a = p.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
