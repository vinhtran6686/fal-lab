#!/usr/bin/env python3
"""Turn a raw AI sprite sheet into game-ready frames (see .claude/skills/fal-image/format.md).

Usage:
  python scripts/sprite_pack.py out/enemies/spider/source/design/walk_side_v02.png
                                --asset out/enemies/spider --kind enemy --id spider
                                --state walk --dir side --frames 6 --grid 3x2 --cell 96
                                [--fps 12] [--no-loop] [--hit-frame 3] [--fill 0.72]
                                [--flip-to left]

What it does:
  1. splits the raw sheet (a COLSxROWS grid, row-major) into N frames
     by transparent gaps, else equal cells
  2. crops each frame to its pixels and scales it. The first packed sheet (walk_side) sets
     the asset's base scale and reference body area; every later sheet is scaled so its
     median body area (largest solid blob: detached weapons and translucent smears are
     ignored) matches, because the model often draws a sheet a bit smaller or bigger
  3. puts the feet on a shared baseline (12% above the cell bottom), centered
  4. writes <asset>/<state>_<dir>/vNN/ (frames/@2x and @1x, sheet.png, preview.gif; checks go to
     vNN/check/), where vNN is the raw file's version, and records it in <asset>/meta.json.
     Earlier packed versions are kept; the highest vNN is the final one.
Prints a one-line summary; warnings go to stderr.
"""
import argparse, json, math, pathlib, re, shutil, sys
from collections import deque
from PIL import Image, ImageChops, ImageFilter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from asset_layout import sheet_dir, sheet_rel  # noqa: E402

ALPHA = 24          # alpha above this counts as sprite pixels
BASELINE = 0.12     # feet sit this fraction of the cell above its bottom edge


def key_out(img: Image.Image, key=(255, 0, 255), hard=90) -> Image.Image:
    """Chroma-key a flat magenta background to transparency.

    Pixels near pure magenta become fully transparent. Every other pixel with a magenta tint
    (anti-aliased edges, translucent motion smears or glows the model blended over the
    background) is un-mixed: c = alpha*fg + (1-alpha)*magenta, with the magenta share taken
    as min(r, b) - g, which restores its true color and partial transparency.
    """
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            d = ((r - key[0]) ** 2 + (g - key[1]) ** 2 + (b - key[2]) ** 2) ** 0.5
            if d < hard:
                px[x, y] = (0, 0, 0, 0)
            else:
                k = min(r, b) - g
                if k > 12:
                    keep = 1 - k / 255
                    fg = [(c - (1 - keep) * kc) / keep for c, kc in zip((r, g, b), key)]
                    px[x, y] = (*(max(0, min(255, round(c))) for c in fg), round(a * keep))
    return img


def body_area(img: Image.Image) -> int:
    """Pixel area of the largest solid blob (alpha > 200), measured on a 1/4-size mask."""
    a = img.getchannel("A").resize((max(1, img.width // 4), max(1, img.height // 4)))
    w, h = a.size
    px = a.load()
    seen, best = bytearray(w * h), 0
    for y0 in range(h):
        for x0 in range(w):
            if px[x0, y0] <= 200 or seen[y0 * w + x0]:
                continue
            q, n = deque([(x0, y0)]), 0
            seen[y0 * w + x0] = 1
            while q:
                x, y = q.popleft(); n += 1
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx] and px[nx, ny] > 200:
                        seen[ny * w + nx] = 1; q.append((nx, ny))
            best = max(best, n)
    return best * 16


def torso_x(img: Image.Image) -> float:
    """Horizontal centre of the upper half (head + torso); limbs swing, this should not."""
    a = img.getchannel("A").point(lambda v: 255 if v > ALPHA else 0)
    up = a.crop((0, 0, img.width, max(1, img.height // 2)))
    cols = [up.crop((x, 0, x + 1, up.height)).histogram()[255] for x in range(up.width)]
    mass = sum(cols)
    return sum(x * n for x, n in enumerate(cols)) / mass if mass else img.width / 2


def has_alpha(img: Image.Image) -> bool:
    return img.getchannel("A").getextrema()[0] < 250


def bbox(img: Image.Image):
    return img.getchannel("A").point(lambda v: 255 if v > ALPHA else 0).getbbox()


def gap_runs(img: Image.Image, axis: str):
    """Runs of non-empty columns (axis='x') or rows (axis='y'), split at transparent gaps."""
    a = img.getchannel("A").point(lambda v: 255 if v > ALPHA else 0)
    w, h = img.size
    px = a.load()
    length = w if axis == "x" else h
    if axis == "x":
        filled = [any(px[x, y] for y in range(0, h, 2)) for x in range(w)]
    else:
        filled = [any(px[x, y] for x in range(0, w, 2)) for y in range(h)]
    runs, start = [], None
    for i, f in enumerate(filled + [False]):
        if f and start is None:
            start = i
        elif not f and start is not None:
            runs.append([start, i]); start = None
    # merge runs separated by tiny gaps (detached weapon tips, sparks), drop specks
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < length * 0.01:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [r for r in merged if r[1] - r[0] > length * 0.02]


def split_by_blobs(sheet: Image.Image, cols: int, rows: int, n: int):
    """Give every connected blob to the grid cell holding its centroid.

    Handles props that poke into the neighbouring cell (a sword tip, a flying weapon), where
    neither transparent gaps nor equal cells work. Returns None if a cell ends up empty.
    """
    q = 4
    a = sheet.getchannel("A").resize((max(1, sheet.width // q), max(1, sheet.height // q)))
    w, h = a.size
    px = a.load()
    label = [0] * (w * h)
    owner = {}
    cw, ch = w / cols, h / rows
    nxt = 0
    for y0 in range(h):
        for x0 in range(w):
            if px[x0, y0] <= ALPHA or label[y0 * w + x0]:
                continue
            nxt += 1
            stack, pts = [(x0, y0)], []
            label[y0 * w + x0] = nxt
            while stack:
                x, y = stack.pop(); pts.append((x, y))
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not label[ny * w + nx] and px[nx, ny] > ALPHA:
                        label[ny * w + nx] = nxt; stack.append((nx, ny))
            if len(pts) < 6:   # specks
                continue
            cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
            owner[nxt] = min(int(cy // ch), rows - 1) * cols + min(int(cx // cw), cols - 1)
    frames = []
    for cell in range(n):
        ids = {k for k, c in owner.items() if c == cell}
        if not ids:
            return None
        small = Image.new("L", (w, h), 0)
        sp = small.load()
        for i, lab in enumerate(label):
            if lab in ids:
                sp[i % w, i // w] = 255
        mask = small.resize(sheet.size, Image.NEAREST).filter(ImageFilter.MaxFilter(5))
        f = sheet.copy()
        f.putalpha(ImageChops.multiply(sheet.getchannel("A"), mask))
        frames.append(f.crop(f.getchannel("A").getbbox()))
    return frames


def split_frames(sheet: Image.Image, cols: int, rows: int, n: int):
    """Row-major frames from a cols x rows grid: cut at transparent gaps, else equal cells."""
    w, h = sheet.size
    row_runs = gap_runs(sheet, "y") if rows > 1 else [[0, h]]
    if len(row_runs) == rows:
        frames = []
        for y0, y1 in row_runs:
            band = sheet.crop((0, y0, w, y1))
            col_runs = gap_runs(band, "x")
            if len(col_runs) != cols:
                break
            frames += [band.crop((x0, 0, x1, band.height)) for x0, x1 in col_runs]
        else:
            return frames[:n], "gaps"
    blob_frames = split_by_blobs(sheet, cols, rows, n)
    if blob_frames:
        return blob_frames, "blobs"
    print(f"warn: figures touch or the grid is not {cols}x{rows}; using equal cells", file=sys.stderr)
    cw, ch = w / cols, h / rows
    cells = [sheet.crop((round(c * cw), round(r * ch), round((c + 1) * cw), round((r + 1) * ch)))
             for r in range(rows) for c in range(cols)]
    return cells[:n], "equal"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("raw")
    p.add_argument("--asset", required=True, help="asset folder, e.g. out/enemies/spider")
    p.add_argument("--kind", default="enemy")
    p.add_argument("--id", required=True)
    p.add_argument("--state", required=True)
    p.add_argument("--dir", default="side", choices=["side", "up", "down", "up_side", "down_side", "none"])
    p.add_argument("--frames", type=int, required=True)
    p.add_argument("--grid", default="3x2", help="raw sheet layout COLSxROWS, row-major (default 3x2)")
    p.add_argument("--cell", type=int, required=True, help="cell height at 1x (and width, unless --cell-w)")
    p.add_argument("--cell-w", type=int, help="wider cell at 1x for sprawling states (death, big swings); feet stay centered")
    p.add_argument("--fps", type=int, default=12)
    p.add_argument("--no-loop", action="store_true")
    p.add_argument("--hit-frame", type=int, help="1-based frame where damage lands")
    p.add_argument("--fill", type=float, default=0.72, help="body size (larger of width/height) / cell (first state only)")
    p.add_argument("--center", action="store_true", help="center vertically instead of the feet baseline (icons, projectiles)")
    p.add_argument("--own-scale", action="store_true", help="fit this file alone, ignore the asset scale (icons)")
    p.add_argument("--flip-to", help="direction produced by mirroring this one, e.g. left")
    p.add_argument("--no-match", action="store_true", help="do not match this sheet's body size to the reference")
    p.add_argument("--align", choices=["bbox", "torso"], default="bbox",
                   help="horizontal registration: bbox centre (default) or head+torso centre (walks/idles: "
                        "stops the body sliding sideways when the stride changes width)")
    p.add_argument("--order", help="re-time or fix a sheet without regenerating: 1-based frame list, e.g. 1,2,3,4,5,4,3,8")
    p.add_argument("--move-speed", type=float, help="walking speed in px/s at 1x (stored in meta.json)")
    a = p.parse_args()

    asset = pathlib.Path(a.asset)
    meta_path = asset / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {
        "id": a.id, "kind": a.kind, "cell": [a.cell, a.cell], "scale_2x": 2,
        "pivot": [0.5, round(1 - BASELINE, 2)], "states": {}}
    if meta["cell"][0] != a.cell and not a.own_scale:
        sys.exit(f"cell {a.cell} does not match this asset's cell {meta['cell'][0]} (only --own-scale states may differ)")
    c2 = a.cell * 2
    c2w = (a.cell_w or a.cell) * 2

    key = a.state if a.dir == "none" else f"{a.state}_{a.dir}"
    m = re.search(r"_v(\d+)$", pathlib.Path(a.raw).stem)
    if not m:
        sys.exit("raw file must be versioned (<name>_vNN.png); generate it with gen_image.py --versioned")
    version = f"v{int(m.group(1)):02d}"
    packed = sorted(int(d.name[1:]) for d in sheet_dir(asset, key).glob("v[0-9]*") if d.is_dir() and d.name[1:].isdigit())
    if packed and packed[-1] > int(version[1:]):
        sys.exit(f"{key} already has packed v{packed[-1]:02d}; to go back to {version}, copy its raw "
                 f"to the next version number and pack that (the highest version is always the final one)")

    sheet = Image.open(a.raw).convert("RGBA")
    if not has_alpha(sheet):  # opaque output from gpt-image-2: remove the flat magenta background
        sheet = key_out(sheet)
    cols, rows = (int(v) for v in a.grid.lower().split("x"))
    if a.frames > cols * rows:
        sys.exit(f"--frames {a.frames} does not fit a {a.grid} grid")
    raw_frames, method = split_frames(sheet, cols, rows, a.frames)
    crops = []
    for f in raw_frames:
        b = bbox(f)
        if not b:
            sys.exit("an empty frame was found; regenerate the sheet")
        crops.append(f.crop(b))

    if a.order:
        idx = [int(v) for v in a.order.split(",")]
        if not all(1 <= i <= len(crops) for i in idx):
            sys.exit(f"--order uses frames 1..{len(crops)} only")
        crops = [crops[i - 1] for i in idx]
    sizes = sorted(max(c.width, c.height) for c in crops)
    areas = sorted(body_area(c) for c in crops)
    med_area = areas[len(areas) // 2]
    match = ""
    if a.own_scale:
        scale = c2 * a.fill / sizes[-1]
    elif "base_scale" not in meta:
        if "raw_body_size" in meta:
            sys.exit("meta.json comes from an older packer: delete it and pack walk_side first, then the other sheets")
        # first sheet (walk_side): its median body size fills `fill` of the cell
        meta["fill"] = a.fill
        meta["base_scale"] = round(c2 * a.fill / sizes[len(sizes) // 2], 5)
        meta["ref_body_area"] = med_area
        scale = meta["base_scale"]
    else:
        scale = meta["base_scale"]
        if not a.no_match:
            k = math.sqrt(meta["ref_body_area"] / med_area)
            scale *= k
            match = f", body matched x{k:.2f}"
    widest, tallest = max(c.width for c in crops), max(c.height for c in crops)
    limit = min((c2w * 0.98) / (widest * scale), (c2 * (1 - BASELINE) * 0.98) / (tallest * scale), 1.0)
    if limit < 1.0:
        print(f"warn: {a.state} would overflow the cell; shrunk by {limit:.2f} for this state"
              + ("" if a.center else " (a wider --cell-w keeps the character's size)"), file=sys.stderr)
        scale *= limit

    tag = f"{a.kind}_{a.id}_{key}"
    vdir = sheet_dir(asset, key)   # one final version per sheet; the raw still keeps its version number
    if (vdir / "frames").exists():   # replace the previous final version
        shutil.rmtree(vdir / "frames")
    d2, d1, ds = vdir / "frames" / "@2x", vdir / "frames" / "@1x", vdir
    for d in (d2, d1, ds):
        d.mkdir(parents=True, exist_ok=True)
    base_y = round(c2 * (1 - BASELINE))
    cells = []
    for i, c in enumerate(crops, 1):
        s = c.resize((max(1, round(c.width * scale)), max(1, round(c.height * scale))), Image.LANCZOS)
        cell = Image.new("RGBA", (c2w, c2), (0, 0, 0, 0))
        y = (c2 - s.height) // 2 if a.center else base_y - s.height
        x = round(c2w / 2 - torso_x(s)) if a.align == "torso" else (c2w - s.width) // 2
        x = max(0, min(c2w - s.width, x))
        cell.alpha_composite(s, (x, y))
        cell.save(d2 / f"{tag}_{i:02d}.png")
        cell.resize((c2w // 2, a.cell), Image.LANCZOS).save(d1 / f"{tag}_{i:02d}.png")
        cells.append(cell)

    strip = Image.new("RGBA", (c2w * len(cells), c2), (0, 0, 0, 0))
    for i, cell in enumerate(cells):
        strip.paste(cell, (i * c2w, 0))
    strip.save(ds / "sheet.png")
    preview = [Image.alpha_composite(Image.new("RGBA", cell.size, (200, 200, 190, 255)), cell).convert("P")
               for cell in cells]
    preview[0].save(ds / "preview.gif", save_all=True, append_images=preview[1:],
                    duration=round(1000 / a.fps), loop=0)

    rel = lambda path: path.resolve().relative_to(asset.resolve()).as_posix()
    entry = {"version": version, "source": rel(pathlib.Path(a.raw)), "frames": len(cells), "fps": a.fps,
             "loop": not a.no_loop, "dir": sheet_rel(key),
             "files": f"{sheet_rel(key)}/frames/@1x/{tag}_NN.png",
             "sheet": f"{sheet_rel(key)}/sheet.png", "split": method}
    if a.cell != meta["cell"][0] or a.cell_w:
        entry["cell"] = [c2w // 2, a.cell]
    if a.center:
        entry["pivot"] = [0.5, 0.5]
    if a.hit_frame:
        entry["hit_frame"] = a.hit_frame
    if a.order:
        entry["order"] = a.order
    if a.align != "bbox":
        entry["align"] = a.align
    meta["states"][key] = entry
    if a.flip_to:
        meta.setdefault("mirrored", {})[f"{a.state}_{a.flip_to}"] = key
    if a.move_speed:
        meta["move_speed"] = a.move_speed
    elif key == "walk_side" and "move_speed" not in meta:
        # default: two steps per cycle, each step about 0.4 of the body height (tune in the playtest)
        body_h1 = sorted(c.height for c in crops)[len(crops) // 2] * scale / 2
        meta["move_speed"] = round(2 * 0.4 * body_h1 / (len(cells) / a.fps), 1)
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"packed {key}: {len(cells)} frames, cell {c2w // 2}x{a.cell}px, split={method}, scale={scale:.3f}{match} -> {vdir}")


if __name__ == "__main__":
    main()
