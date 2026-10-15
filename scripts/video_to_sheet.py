#!/usr/bin/env python3
"""Export one finished action of a video-sprite set into the asset format
(see .claude/skills/video-sprite/SKILL.md), so build_playtest.py, motion_check.py and leg_check.py
work on it.

Usage:
  python scripts/video_to_sheet.py --set out/enemies/bandit/.work/side --action walk
                                   --asset out/enemies/bandit --id bandit --sheet walk_side
                                   [--kind enemy] [--cell 256x128] [--flip-to left] [--move-speed 60]
                                   [--despill]

What it does:
  1. reads the set's set_state.json: the chosen take of --action, its finished frames (one canvas,
     one feet anchor, one body scale for the whole set) and its frame selection (loop window or
     retimed one-shot: frame order, durations, the hit event)
  2. ONE canvas for every action of the asset (meta.json "cell", set by the first export, default
     --cell 256x128 at 1x for Level 1 enemies): move, attack, death ... share the same frame size and
     pivot, so the engine never rescales one action against another. A state that does not fit is
     refused (never shrunk): re-export the whole asset with a larger --cell
  3. ONE body size: the first export records the body height (@2x, the largest solid blob, median of the
     rest frames); every later export is compared with it and rescaled when it differs by more than 4%
  4. places every frame with one fixed transform: the feet anchor on the pivot (x 0.5, y 0.88); no
     per-frame crop or re-centering, so registered motion (bob, lean, a fall, a spin) is kept
  5. moves the clip out of the set to <asset>/<category>/<sheet>/clip_tNN.mp4 (+ .json: model, prompt,
     cost); category = move, attack, death ... (scripts/asset_layout.py); set_state.json follows the clip
  6. writes <asset>/<category>/<sheet>/vNN/ (frames/@2x and @1x, sheet.png, preview.gif,
     check/take_review.png), records the state in <asset>/meta.json and the export in <set>/exports.json
     (video_prune.py only drops frames of exported takes)
Prints a one-line summary; warnings go to stderr.
"""
import argparse, json, math, os, pathlib, shutil, sys
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from asset_layout import sheet_dir as layout_dir, sheet_rel  # noqa: E402

DEFAULT_CELL = (256, 128)   # Level 1 enemy canvas at 1x (fal-image/classes/enemy.md)
BODY_TOLERANCE = 0.04       # rescale a sheet whose body height differs more than this from the asset's

BASELINE = 0.12     # feet sit this fraction of the cell above its bottom edge (same as sprite_pack.py)
ALPHA = 24


def read_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def chosen_take(set_dir: pathlib.Path, action: str) -> tuple[dict, dict, str]:
    state = read_json(set_dir / "set_state.json")
    st = (state.get("actions") or {}).get(action)
    if not st:
        sys.exit(f"{set_dir} has no action {action!r}")
    out = st.get("output") if st.get("status") in ("done", "done-warn") else None
    if not out and st.get("accepted") and st.get("chosen"):
        # an accepted take whose engine package was refused (e.g. key spill on a motion smear): the finished
        # frames and the selection are all this export needs; the package is not part of the game format
        out = st["chosen"]
    if not out:
        sys.exit(f"{action} is {st.get('status')!r}, not done: run, review and accept it first (sprite_set.py)")
    record = next((t for t in st["takes"] if t["take"] == out["take"]), None)
    if record is None:
        sys.exit(f"{action}: take {out['take']} is missing from set_state.json")
    tag = out.get("tag", "")
    if not {"finished" + tag, "selection" + tag} <= set(record.get("stages", {})):
        sys.exit(f"{action}: take {out['take']} has no finished frames and selection yet (sprite_set.py run)")
    if st.get("status") not in ("done", "done-warn"):
        print(f"note: {action} is {st.get('status')!r} ({st.get('message', '')[:120]}); exporting its accepted "
              f"take {out['take']} from the finished frames", file=sys.stderr)
    return st, record, tag


def despill(im: Image.Image, floor: int = 25, ramp: int = 60) -> Image.Image:
    """Turn magenta-tinted pixels neutral grey (lightness and alpha kept): the model blends motion smears with
    the magenta backdrop, which the key cannot fully separate; grey reads as a steel blur instead of pink."""
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    t = np.clip((np.minimum(r, b) - g - floor) / ramp, 0, 1) * (a[..., 3] > 0)
    grey = 0.3 * r + 0.59 * g + 0.11 * b
    for c in range(3):
        a[..., c] = a[..., c] * (1 - t) + grey * t
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def timeline(selection: dict) -> tuple[list[int], list[int], dict]:
    """(source frame index per shown frame, ms per shown frame, events) from a forge frame selection."""
    start, end = int(selection["start"]), int(selection["endExclusive"])
    indices = selection.get("sourceIndices") or list(range(start, end))
    durations = selection.get("durations_ms") or selection.get("durationsMs")
    if not durations:
        fps = selection.get("fps") or 12
        num, _, den = str(fps).partition("/")
        durations = [round(1000 * float(den or 1) / float(num))] * len(indices)
    return [int(i) for i in indices], [int(d) for d in durations], selection


def even_fps(durations: list[int]) -> tuple[int, list[int]]:
    """One constant fps for the engine: the shortest frame is one tick, longer frames (holds) repeat."""
    tick = max(1, min(durations))
    repeats = [max(1, round(d / tick)) for d in durations]
    return max(1, round(1000 / tick)), repeats


def hit_index(selection: dict, durations: list[int]) -> int | None:
    """1-based shown frame of the hit event (attacks), None when the take has none."""
    at = selection.get("impactMs")
    for event in selection.get("events") or []:
        if event.get("name") == "hit":
            at = event.get("atMs", at)
    if at is None:
        return None
    t = 0
    for i, d in enumerate(durations):
        if t <= at < t + d:
            return i + 1
        t += d
    return len(durations)


def next_version(sheet_dir: pathlib.Path, sheet: str) -> int:
    nums = [int(d.name[1:]) for d in sheet_dir.glob("v[0-9]*") if d.is_dir() and d.name[1:].isdigit()]
    nums += [int(f.stem.rsplit("_v", 1)[1]) for f in (sheet_dir / "raw").glob(f"{sheet}_v*.*")
             if f.stem.rsplit("_v", 1)[-1].isdigit()]
    return max(nums, default=0) + 1


def move_clip(set_dir: pathlib.Path, sheet_dir: pathlib.Path, record: dict) -> pathlib.Path:
    """Move the take's clip (+ its job.json) out of the set to <sheet>/clip_tNN.mp4 (+ .json), the one place a
    reader looks for the source video, and point set_state.json at it (sprite_set reads it from there to
    rebuild). A clip already moved is left alone."""
    clip = (set_dir / record["clip"]["path"]).resolve()
    dest = (sheet_dir / f"clip_t{record['take']:02d}.mp4").resolve()
    if clip == dest:
        return dest
    if dest.exists():
        sys.exit(f"{dest} already exists and is not this take's clip; rename it first")
    sheet_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(clip), dest)
    if (clip.parent / "job.json").exists():
        shutil.move(str(clip.parent / "job.json"), dest.with_suffix(".json"))
    if clip.parent.name == "media" and not any(clip.parent.iterdir()):
        clip.parent.rmdir()
    state_path = set_dir / "set_state.json"
    state = read_json(state_path)
    for st in state["actions"].values():
        for take in st["takes"]:
            if take.get("clip", {}).get("path") == record["clip"]["path"]:
                take["clip"]["path"] = pathlib.Path(os.path.relpath(dest, set_dir.resolve())).as_posix()
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return dest


def body_height(im: Image.Image) -> int:
    """Height of the largest solid blob (alpha > 200): the body with what it holds, not detached smears."""
    a = np.asarray(im)[..., 3] > 200
    lab, n = ndimage.label(a)
    if not n:
        return 0
    k = int(np.argmax(ndimage.sum(a, lab, range(1, n + 1)))) + 1
    ys = np.nonzero(lab == k)[0]
    return int(ys.max() - ys.min() + 1)


def parse_cell(text: str) -> tuple[int, int]:
    w, _, h = text.lower().partition("x")
    return int(w), int(h or w)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--set", required=True, help="sprite_set.py output dir (holds set_plan.json, set_state.json)")
    p.add_argument("--action", required=True, help="action id in the set: walk, front-walk, attack, death ...")
    p.add_argument("--asset", required=True, help="asset folder, e.g. out/enemies/bandit")
    p.add_argument("--id", required=True)
    p.add_argument("--kind", default="enemy")
    p.add_argument("--sheet", required=True, help="our sheet name: walk_side, walk_down_side, attack_side ...")
    p.add_argument("--cell", help="canvas WxH at 1x for a NEW asset (default 256x128); an existing asset keeps its own")
    p.add_argument("--flip-to", help="direction produced by mirroring this one, e.g. left")
    p.add_argument("--move-speed", type=float, help="walking speed in px/s at 1x (stored in meta.json)")
    p.add_argument("--despill", action="store_true",
                   help="turn magenta-tinted motion smears neutral grey (a fast blade the key left pink)")
    a = p.parse_args()

    set_dir, asset = pathlib.Path(a.set), pathlib.Path(a.asset)
    st, record, tag = chosen_take(set_dir, a.action)
    stages = record["stages"]
    finished, selection_stage = stages["finished" + tag], stages["selection" + tag]
    finish = read_json(set_dir / finished["metadata"]) if finished.get("metadata") else {}
    frames_dir = set_dir / finished["framesDir"]
    files = sorted(frames_dir.glob("*.png"))
    indices, durations, selection = timeline(read_json(set_dir / selection_stage["selection"]))
    anchor = finish.get("anchor") or finished.get("anchor")
    if not files or anchor is None:
        sys.exit(f"{a.action}: no finished frames or no anchor in {frames_dir}")
    ax, ay = float(anchor[0]), float(anchor[1])
    fps, repeats = even_fps(durations)
    hit = hit_index(selection, durations)
    order = [i for i, n in zip(indices, repeats) for _ in range(n)]
    if hit:   # the hit frame moves with the repeats
        hit = sum(repeats[:hit - 1]) + 1
    loop = selection.get("loopPolicy", "cycle") != "oneshot"

    meta_path = asset / "meta.json"
    if meta_path.exists():
        meta = read_json(meta_path)
        if a.cell and list(parse_cell(a.cell)) != list(meta["cell"]):
            sys.exit(f"this asset's canvas is {meta['cell'][0]}x{meta['cell'][1]}; every action shares it. To change "
                     "it, delete meta.json and re-export every sheet with the new --cell")
    else:
        meta = {"id": a.id, "kind": a.kind, "cell": list(parse_cell(a.cell) if a.cell else DEFAULT_CELL),
                "scale_2x": 2, "pivot": [0.5, round(1 - BASELINE, 2)], "states": {}}
    c2w, c2 = meta["cell"][0] * 2, meta["cell"][1] * 2
    px, py = c2w / 2, round(c2 * (1 - BASELINE))   # the pivot in the @2x canvas

    images = {i: Image.open(files[i]).convert("RGBA") for i in sorted(set(indices))}
    if a.despill:
        images = {i: despill(im) for i, im in images.items()}

    # one body size per asset: rest frames = the first frames of a one-shot, every frame of a loop
    rest = list(dict.fromkeys(indices if loop else indices[:2]))
    body = float(np.median([body_height(images[i]) for i in rest]))
    scale, note = 1.0, ""
    ref = meta.get("body_height_2x")
    if ref is None:
        meta["body_height_2x"] = round(body)
    elif abs(body / ref - 1) > BODY_TOLERANCE:
        scale = ref / body
        note = f", body {body:.0f}px rescaled x{scale:.3f} to the asset's {ref}px"

    # every frame must fit the shared canvas around the pivot; nothing is shrunk to make it fit
    left = right = up = down = 0.0
    for im in images.values():
        box = im.getchannel("A").point(lambda v: 255 if v > ALPHA else 0).getbbox()
        if box:
            left, right = max(left, (ax - box[0]) * scale), max(right, (box[2] - ax) * scale)
            up, down = max(up, (ay - box[1]) * scale), max(down, (box[3] - ay) * scale)
    if max(left, right) > px or up > py or down > c2 - py:
        need_w = max(c2w // 2, math.ceil(max(left, right) / 16) * 16)
        need_h = max(c2 // 2, math.ceil(max(up / (1 - BASELINE), down / BASELINE) / 2 / 16) * 16)
        sys.exit(f"{a.sheet} does not fit the asset canvas {c2w // 2}x{c2 // 2} (needs about {need_w}x{need_h} "
                 "at 1x). Keep one canvas for every action: delete meta.json and re-export every sheet with a "
                 "larger --cell")

    folder = layout_dir(asset, a.sheet)
    version = f"v{next_version(folder, a.sheet):02d}"
    tagname = f"{a.kind}_{a.id}_{a.sheet}"
    vdir = folder / version
    d2, d1 = vdir / "frames" / "@2x", vdir / "frames" / "@1x"
    for d in (d2, d1):
        d.mkdir(parents=True, exist_ok=True)
    cells = []
    for n, i in enumerate(order, 1):
        im = images[i]
        if scale != 1.0:
            im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        cell = Image.new("RGBA", (c2w, c2), (0, 0, 0, 0))
        cell.paste(im, (round(px - ax * scale), round(py - ay * scale)))   # empty cell: a plain copy
        cell.save(d2 / f"{tagname}_{n:02d}.png")
        cell.resize((c2w // 2, c2 // 2), Image.LANCZOS).save(d1 / f"{tagname}_{n:02d}.png")
        cells.append(cell)

    strip = Image.new("RGBA", (c2w * len(cells), c2), (0, 0, 0, 0))
    for n, cell in enumerate(cells):
        strip.paste(cell, (n * c2w, 0))
    strip.save(vdir / "sheet.png")
    preview = [Image.alpha_composite(Image.new("RGBA", cell.size, (200, 200, 190, 255)), cell).convert("P")
               for cell in cells]
    preview[0].save(vdir / "preview.gif", save_all=True, append_images=preview[1:],
                    duration=round(1000 / fps), loop=0)
    review = set_dir / "review" / a.action / f"t{record['take']:02d}{tag}-sheet.png"
    review = review if review.exists() else set_dir / "review" / a.action / f"t{record['take']:02d}-sheet.png"
    if review.exists():   # the take's contact sheet, looked at before accepting it
        (vdir / "check").mkdir(exist_ok=True)
        shutil.copyfile(review, vdir / "check" / "take_review.png")

    clip = move_clip(set_dir, folder, record)
    def rel(path: pathlib.Path) -> str:
        path = path.resolve()
        return path.relative_to(asset.resolve()).as_posix() if path.is_relative_to(asset.resolve()) else str(path)
    base = f"{sheet_rel(a.sheet)}/{version}"
    entry = {"version": version, "dir": base, "source": rel(clip), "frames": len(cells), "fps": fps, "loop": loop,
             "files": f"{base}/frames/@1x/{tagname}_NN.png", "sheet": f"{base}/sheet.png", "split": "video",
             "video": {"set": rel(set_dir), "action": a.action, "take": record["take"],
                       "route": record.get("route")}}
    if hit:
        entry["hit_frame"] = hit
    if a.despill:
        entry["despill"] = True
    if scale != 1.0:
        entry["body_rescale"] = round(scale, 4)
    meta["states"][a.sheet] = entry
    if a.flip_to:
        state, _, _ = a.sheet.partition("_")
        meta.setdefault("mirrored", {})[f"{state}_{a.flip_to}"] = a.sheet
    if a.move_speed:
        meta["move_speed"] = a.move_speed
    elif a.sheet == "walk_side" and "move_speed" not in meta:
        # default: two steps per cycle, each step about 0.4 of the body height (tune in the playtest)
        meta["move_speed"] = round(2 * 0.4 * (meta["body_height_2x"] / 2) / (len(cells) / fps), 1)
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    # the set remembers what was exported, so video_prune.py knows the take's frames are safe to drop
    exports_path = set_dir / "exports.json"
    exports = read_json(exports_path) if exports_path.exists() else []
    exports.append({"action": a.action, "take": record["take"], "tag": tag, "asset": str(asset.resolve()),
                    "sheet": a.sheet, "version": version})
    exports_path.write_text(json.dumps(exports, indent=2), encoding="utf-8")
    extra = f", hit frame {hit}" if hit else ""
    print(f"exported {a.sheet} from {a.action} take {record['take']}: {len(cells)} frames @ {fps} fps, "
          f"{'loop' if loop else 'once'}, canvas {c2w // 2}x{c2 // 2}, body {body * scale:.0f}px@2x{note}{extra} "
          f"-> {vdir}")


if __name__ == "__main__":
    main()
