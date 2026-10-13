#!/usr/bin/env python3
"""Turn a raw AI sprite sheet into game-ready frames (see .claude/skills/fal-image/format.md).

Usage:
  python scripts/sprite_pack.py out/enemies/spider/walk_side/raw/walk_side_v02.png
                                --asset out/enemies/spider --kind enemy --id spider
                                --state walk --dir side --frames 6 --grid 3x2 --cell 96
                                [--fps 12] [--no-loop] [--hit-frame 3] [--fill 0.72]
                                [--flip-to left]

What it does:
  1. splits the raw sheet (a COLSxROWS grid, row-major) into N frames
     by transparent gaps, else equal cells
  2. crops each frame to its pixels and scales ALL states of the asset by one shared
     factor (fixed by the first packed state, so walk_side should go first)
  3. puts the feet on a shared baseline (12% above the cell bottom), centered
  4. writes <asset>/<state>_<dir>/vNN/ (frames @2x and @1x, a horizontal sheet, a GIF
     preview), where vNN is the raw file's version, and records it in <asset>/meta.json.
     Earlier packed versions are kept; the highest vNN is the final one.
Prints a one-line summary; warnings go to stderr.
"""
import argparse, json, pathlib, re, sys
from PIL import Image

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
    p.add_argument("--dir", default="side", choices=["side", "up", "down", "none"])
    p.add_argument("--frames", type=int, required=True)
    p.add_argument("--grid", default="3x2", help="raw sheet layout COLSxROWS, row-major (default 3x2)")
    p.add_argument("--cell", type=int, required=True, help="cell size at 1x (square)")
    p.add_argument("--fps", type=int, default=12)
    p.add_argument("--no-loop", action="store_true")
    p.add_argument("--hit-frame", type=int, help="1-based frame where damage lands")
    p.add_argument("--fill", type=float, default=0.72, help="body size (larger of width/height) / cell (first state only)")
    p.add_argument("--center", action="store_true", help="center vertically instead of the feet baseline (icons, projectiles)")
    p.add_argument("--own-scale", action="store_true", help="fit this file alone, ignore the asset scale (icons)")
    p.add_argument("--flip-to", help="direction produced by mirroring this one, e.g. left")
    a = p.parse_args()

    asset = pathlib.Path(a.asset)
    meta_path = asset / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {
        "id": a.id, "kind": a.kind, "cell": [a.cell, a.cell], "scale_2x": 2,
        "pivot": [0.5, round(1 - BASELINE, 2)], "states": {}}
    if meta["cell"][0] != a.cell and not a.own_scale:
        sys.exit(f"cell {a.cell} does not match this asset's cell {meta['cell'][0]} (only --own-scale states may differ)")
    c2 = a.cell * 2

    key = a.state if a.dir == "none" else f"{a.state}_{a.dir}"
    m = re.search(r"_v(\d+)$", pathlib.Path(a.raw).stem)
    if not m:
        sys.exit("raw file must be versioned (<name>_vNN.png); generate it with gen_image.py --versioned")
    version = f"v{int(m.group(1)):02d}"
    packed = sorted(int(d.name[1:]) for d in (asset / key).glob("v[0-9]*") if d.is_dir() and d.name[1:].isdigit())
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

    # one scale for the whole asset: set from the first packed state's median body size
    sizes = sorted(max(c.width, c.height) for c in crops)
    if a.own_scale:
        scale = c2 * a.fill / sizes[-1]
    else:
        if "raw_body_size" not in meta:
            meta["raw_body_size"] = sizes[len(sizes) // 2]
            meta["fill"] = a.fill
        scale = c2 * meta["fill"] / meta["raw_body_size"]
    widest, tallest = max(c.width for c in crops), max(c.height for c in crops)
    limit = min((c2 * 0.98) / (widest * scale), (c2 * (1 - BASELINE) * 0.98) / (tallest * scale), 1.0)
    if limit < 1.0:
        print(f"warn: {a.state} would overflow the cell; shrunk by {limit:.2f} for this state", file=sys.stderr)
        scale *= limit

    tag = f"{a.kind}_{a.id}_{key}"
    vdir = asset / key / version
    d2, d1, ds = vdir / "frames" / "@2x", vdir / "frames" / "@1x", vdir
    for d in (d2, d1, ds):
        d.mkdir(parents=True, exist_ok=True)
    base_y = round(c2 * (1 - BASELINE))
    cells = []
    for i, c in enumerate(crops, 1):
        s = c.resize((max(1, round(c.width * scale)), max(1, round(c.height * scale))), Image.LANCZOS)
        cell = Image.new("RGBA", (c2, c2), (0, 0, 0, 0))
        y = (c2 - s.height) // 2 if a.center else base_y - s.height
        cell.alpha_composite(s, ((c2 - s.width) // 2, y))
        cell.save(d2 / f"{tag}_{i:02d}.png")
        cell.resize((a.cell, a.cell), Image.LANCZOS).save(d1 / f"{tag}_{i:02d}.png")
        cells.append(cell)

    strip = Image.new("RGBA", (c2 * len(cells), c2), (0, 0, 0, 0))
    for i, cell in enumerate(cells):
        strip.paste(cell, (i * c2, 0))
    strip.save(ds / f"{tag}.png")
    preview = [Image.alpha_composite(Image.new("RGBA", cell.size, (200, 200, 190, 255)), cell).convert("P")
               for cell in cells]
    preview[0].save(ds / f"{tag}_preview.gif", save_all=True, append_images=preview[1:],
                    duration=round(1000 / a.fps), loop=0)

    rel = lambda path: path.resolve().relative_to(asset.resolve()).as_posix()
    entry = {"version": version, "source": rel(pathlib.Path(a.raw)), "frames": len(cells), "fps": a.fps,
             "loop": not a.no_loop, "files": f"{key}/{version}/frames/@1x/{tag}_NN.png",
             "sheet": f"{key}/{version}/{tag}.png", "split": method}
    if a.cell != meta["cell"][0]:
        entry["cell"] = [a.cell, a.cell]
    if a.center:
        entry["pivot"] = [0.5, 0.5]
    if a.hit_frame:
        entry["hit_frame"] = a.hit_frame
    meta["states"][key] = entry
    if a.flip_to:
        meta.setdefault("mirrored", {})[f"{a.state}_{a.flip_to}"] = key
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"packed {key}: {len(cells)} frames, cell {a.cell}px (@2x {c2}px), split={method}, scale={scale:.3f} -> {vdir}")


if __name__ == "__main__":
    main()
