#!/usr/bin/env python3
"""Study a reference VFX clip (GIF, MP4, WEBM, or a folder of frames) before redrawing it with lib-fx. 0 USD, no model.

Usage (repo root):
  python lib-fx/_tools/study_ref.py REF.gif [--name NAME] [--bg auto|median|R,G,B|alpha] [--thr 38] [--k 8]
  python lib-fx/_tools/study_ref.py REF.gif --compare lib-fx/<group>/<family>/<id>/frames   (our frames next to the reference)

Writes lib-fx/_study/<name>/ (git-ignored: references are study material, never shipped):
  frames/NN.png     every source frame                 fg/NN.png    the effect keyed off its background (RGBA)
  contact.png       every frame with its index and time  onion.png    all silhouettes in one picture, tinted by time
  palette.png       the main colours (k-means on effect pixels) with their share, as a strip
  curves.png        area, brightness and blob count per frame (beats: build-up, burst, peak, dissipation)
  report.json       timing (durations, fps), per-frame bbox/area/centroid/blobs (sizes sorted: hero/medium/small rhythm),
                    the palette, the beats found, and the scale to lib-fx @2x
  compare.png       (with --compare) reference and our frames side by side, resampled to the same clock
Method and how to use the numbers: lib-fx/_core/formulas/rules/REFERENCE-GIF.md.
"""
import argparse, json, math, pathlib, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageSequence
from scipy import ndimage

HERE = pathlib.Path(__file__).resolve().parents[1]


def load(src):
    """Frames (RGBA) and their durations in ms."""
    p = pathlib.Path(src)
    if p.is_dir():
        files = sorted(f for f in p.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"))
        return [Image.open(f).convert("RGBA") for f in files], [1000 / 30] * len(files)
    if p.suffix.lower() in (".gif", ".webp", ".apng", ".png"):
        im = Image.open(p)
        frames, durs = [], []
        for f in ImageSequence.Iterator(im):
            frames.append(f.convert("RGBA")); durs.append(f.info.get("duration", im.info.get("duration", 33)) or 33)
        return frames, durs
    tmp = pathlib.Path(tempfile.mkdtemp())                                  # video: let ffmpeg cut it into frames
    rate = subprocess.run(["ffprobe", "-v", "0", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", str(p)],
                          capture_output=True, text=True).stdout.strip() or "30/1"
    a, b = (rate.split("/") + ["1"])[:2]
    fps = float(a) / float(b or 1)
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), str(tmp / "%04d.png")], check=True)
    files = sorted(tmp.glob("*.png"))
    return [Image.open(f).convert("RGBA") for f in files], [1000 / fps] * len(files)


def key(frames, bg, thr):
    """Foreground masks: by alpha when the source has it, else by distance to a background colour (the median of the corners
    over all frames, or the colour given)."""
    arrs = [np.asarray(f).astype(np.int16) for f in frames]
    if bg == "alpha" or (bg == "auto" and min(a[..., 3].min() for a in arrs) < 250):
        return [a[..., 3] > 16 for a in arrs], None
    if bg == "median":                                                      # a static but uneven background (gradient, floor)
        med = np.median(np.stack([a[..., :3] for a in arrs]), axis=0)
        masks = [ndimage.binary_opening(np.sqrt(((a[..., :3] - med) ** 2).sum(-1)) > thr, iterations=1) for a in arrs]
        Image.fromarray(med.astype(np.uint8)).save(HERE / "_study" / "_last_background.png")
        return masks, "median"
    if bg == "auto":
        corners = np.concatenate([np.concatenate([a[:6, :6, :3].reshape(-1, 3), a[:6, -6:, :3].reshape(-1, 3), a[-6:, :6, :3].reshape(-1, 3),
                                                  a[-6:, -6:, :3].reshape(-1, 3)]) for a in arrs])
        col = np.median(corners, axis=0)
    else:
        col = np.array([int(v) for v in bg.split(",")])
    masks = []
    for a in arrs:
        dist = np.sqrt(((a[..., :3] - col) ** 2).sum(-1))
        m = ndimage.binary_opening(dist > thr, iterations=1)
        masks.append(m)
    return masks, tuple(int(v) for v in col)


def kmeans(px, k, iters=12, seed=0):
    rng = np.random.default_rng(seed)
    c = px[rng.choice(len(px), size=min(k, len(px)), replace=False)].astype(float)
    for _ in range(iters):
        lab = ((px[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)
        for j in range(len(c)):
            if (lab == j).any(): c[j] = px[lab == j].mean(0)
    lab = ((px[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)
    share = np.bincount(lab, minlength=len(c)) / len(lab)
    order = np.argsort(-share)
    return c[order].round().astype(int), share[order]


def font():
    from PIL import ImageFont
    for f in ("DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"):
        try: return ImageFont.truetype(f, 13)
        except OSError: pass
    return ImageFont.load_default()


def contact(frames, durs, out, cols=6, tag=None):
    W, H = frames[0].size
    sc = min(1.0, 260 / W)
    w, h = int(W * sc), int(H * sc)
    rows = math.ceil(len(frames) / cols)
    sheet = Image.new("RGB", (cols * w, rows * (h + 18)), (30, 32, 36))
    d = ImageDraw.Draw(sheet); f = font(); t = 0.0
    for i, fr in enumerate(frames):
        bg = Image.new("RGBA", fr.size, (52, 56, 62, 255)); bg.alpha_composite(fr)
        x, y = (i % cols) * w, (i // cols) * (h + 18)
        sheet.paste(bg.convert("RGB").resize((w, h), Image.LANCZOS), (x, y + 18))
        d.text((x + 4, y + 2), f"{i + 1:02d}  {t / 1000:.2f}s" + (f"  {tag}" if tag else ""), fill=(220, 220, 200), font=f)
        t += durs[i]
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("--name"); ap.add_argument("--bg", default="auto")
    ap.add_argument("--thr", type=float, default=38); ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--hero-px", type=float, default=0, help="height of a character in the reference (px), to scale to lib-fx @2x (120 px)")
    ap.add_argument("--compare")
    a = ap.parse_args()
    frames, durs = load(a.src)
    name = a.name or pathlib.Path(a.src).stem
    out = HERE / "_study" / name
    (out / "frames").mkdir(parents=True, exist_ok=True); (out / "fg").mkdir(exist_ok=True)
    masks, bgcol = key(frames, a.bg, a.thr)
    W, H = frames[0].size
    per, fgs, allpx = [], [], []
    for i, (fr, m) in enumerate(zip(frames, masks)):
        fr.save(out / "frames" / f"{i + 1:02d}.png")
        arr = np.asarray(fr).copy(); arr[..., 3] = np.where(m, 255, 0)
        fg = Image.fromarray(arr, "RGBA"); fg.save(out / "fg" / f"{i + 1:02d}.png"); fgs.append(fg)
        lab, n = ndimage.label(m)
        sizes = sorted((int(v) for v in np.bincount(lab.ravel())[1:]), reverse=True)
        ys, xs = np.nonzero(m)
        rgb = np.asarray(fr)[..., :3][m]
        if len(rgb): allpx.append(rgb[:: max(1, len(rgb) // 4000)])
        per.append(dict(frame=i + 1, t_ms=round(sum(durs[:i])), area=int(m.sum()),
                        bbox=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None,
                        centroid=[round(float(xs.mean()), 1), round(float(ys.mean()), 1)] if len(xs) else None,
                        brightness=round(float(rgb.mean()), 1) if len(rgb) else 0.0,
                        blobs=n, blob_sizes=sizes[:12]))
    # palette of the effect
    px = np.concatenate(allpx) if allpx else np.zeros((1, 3))
    cols, share = kmeans(px.astype(float), a.k)
    pal = Image.new("RGB", (60 * len(cols), 80), (30, 32, 36)); d = ImageDraw.Draw(pal); f = font()
    for j, (c, sh) in enumerate(zip(cols, share)):
        d.rectangle([j * 60, 0, j * 60 + 58, 56], fill=tuple(int(v) for v in c)); d.text((j * 60 + 4, 60), f"{sh * 100:.0f}%", fill=(220, 220, 200), font=f)
    pal.save(out / "palette.png")
    # onion skin: every silhouette tinted from blue (early) to red (late)
    onion = np.zeros((H, W, 3), float); cnt = np.zeros((H, W), float)
    for i, m in enumerate(masks):
        k = i / max(1, len(masks) - 1)
        onion[m] += (255 * k, 80, 255 * (1 - k)); cnt[m] += 1
    onion = (onion / np.maximum(cnt, 1)[..., None]).astype(np.uint8)
    Image.fromarray(onion).save(out / "onion.png")
    # curves
    n = len(per); cw, ch = max(300, n * 14), 220
    cv = Image.new("RGB", (cw, ch), (24, 26, 30)); d = ImageDraw.Draw(cv)
    for key_, col in (("area", (120, 200, 255)), ("brightness", (255, 220, 120)), ("blobs", (255, 120, 160))):
        vals = [p[key_] for p in per]; mx = max(vals) or 1
        d.line([(10 + i * (cw - 20) / max(1, n - 1), ch - 20 - v / mx * (ch - 40)) for i, v in enumerate(vals)], fill=col, width=2)
        d.text((10, 6 + 14 * ["area", "brightness", "blobs"].index(key_)), key_, fill=col, font=f)
    cv.save(out / "curves.png")
    # beats
    areas = [p["area"] for p in per]
    vis = [i for i, v in enumerate(areas) if v > 0]
    peak = int(np.argmax(areas)) if areas else 0
    bri = [p["brightness"] for p in per]
    flash = int(np.argmax(bri)) if bri else 0
    beats = dict(first_visible=(vis[0] + 1) if vis else None, brightest=flash + 1, biggest=peak + 1,
                 gone_after=(vis[-1] + 1) if vis else None,
                 fade_from=next((i + 1 for i in range(peak, n) if areas[i] < 0.5 * areas[peak]), None) if areas else None)
    total = sum(durs)
    report = dict(source=str(a.src), frames=n, size=[W, H], durations_ms=[round(x) for x in durs], total_ms=round(total),
                  fps=round(1000 * n / total, 2) if total else None, background=bgcol, palette=[dict(rgb=[int(v) for v in c], share=round(float(s), 3))
                  for c, s in zip(cols, share)], beats=beats,
                  scale_to_libfx_2x=(round(120 / a.hero_px, 3) if a.hero_px else None), per_frame=per)
    (out / "report.json").write_text(json.dumps(report, indent=1), encoding="utf8")
    contact(fgs, durs, out / "contact.png")
    if a.compare:                                                           # ours next to the reference, on the reference's clock
        ours = sorted(pathlib.Path(a.compare).glob("*.png"))
        if ours:
            oursf = [Image.open(o).convert("RGBA") for o in ours]
            pairs, t = [], 0.0
            for i, fg in enumerate(fgs):
                j = min(len(oursf) - 1, int(round(t / 1000 * 30)))
                o = oursf[j]
                sc = fg.height / o.height
                o2 = o.resize((max(1, int(o.width * sc)), fg.height), Image.LANCZOS)
                pair = Image.new("RGBA", (fg.width + o2.width + 6, fg.height), (0, 0, 0, 0))
                pair.alpha_composite(fg, (0, 0)); pair.alpha_composite(o2, (fg.width + 6, 0))
                pairs.append(pair); t += durs[i]
            contact(pairs, durs, out / "compare.png", cols=3, tag="ref | ours")
    print(f"{n} frames, {round(total)} ms, {report['fps']} fps -> {out.relative_to(HERE.parent)}")
    print("beats:", beats)
    print("palette:", [tuple(int(v) for v in c) for c in cols])


if __name__ == "__main__":
    main()
