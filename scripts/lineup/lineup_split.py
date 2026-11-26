#!/usr/bin/env python3
"""Split ONE lineup clip (a grid of characters on a magenta background) into one frame set per character.

    python scripts/lineup/lineup_split.py <clip.mp4> --out <dir> [--cols 5 --rows 2] [--frames 13 | --step N]
                                           [--names a,b,c,...] [--scales s1,s2,...] [--fps 12]

Per character <out>/<name>/: frames/f01.png ... (RGBA, magenta keyed), sheet.png (one horizontal strip),
preview.gif. Cells are cut with fixed cuts (clip width / cols, clip height / rows). One fixed transform per
character: the feet anchor (bottom of the silhouette in the first frame, horizontal centre of the silhouette)
goes to (cell width / 2, 0.88 x cell height); frames are never re-centred one by one, so the motion is kept.
The window of each character is its cell plus --pad pixels on every side (so a weapon that swings past the cell
line is kept whole); then only the main body is kept: the largest connected piece that crosses the window's centre column, plus any
piece within --gap pixels of it. Pieces that belong to a neighbour
(a weapon head crossing the line) are dropped. --scales shrinks each character about its feet anchor afterwards (rank size: the small ones are enlarged for the video).
Warning: a kept silhouette touching the window edge.
Needs ffmpeg on PATH, numpy, scipy and Pillow. Costs nothing.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


def key_magenta(rgb):
    """rgb uint8 HxWx3 -> RGBA with the magenta background removed and the magenta fringe despilled."""
    f = rgb.astype(np.float32)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    score = np.minimum(r, b) - g                      # magenta-ness: high for #FF00FF and its tints
    bg = np.clip((score - 70.0) / 70.0, 0.0, 1.0)     # 0 = subject, 1 = background
    bg = np.where((r > 120) & (b > 120), bg, 0.0)
    alpha = 1.0 - bg
    # despill: pull the excess of red and blue over green back on partly transparent edge pixels
    edge = (alpha < 0.999) & (alpha > 0.0)
    excess = np.clip(np.minimum(r, b) - g, 0, None) * edge
    r2, b2 = r - excess * 0.8, b - excess * 0.8
    out = np.dstack([np.clip(r2, 0, 255), g, np.clip(b2, 0, 255), alpha * 255]).astype(np.uint8)
    return out


def keep_main(rgba, cx, gap):
    """Zero the alpha of every piece that is not the main body (the biggest piece nearest the window centre) or a
    close fragment of it."""
    a = rgba[..., 3] > 128
    lab, n = ndimage.label(a)
    if n <= 1:
        return rgba
    objs = ndimage.find_objects(lab)
    areas = ndimage.sum(a, lab, range(1, n + 1))
    # main = largest piece among those whose horizontal span covers the window centre column
    cover = [i for i, s in enumerate(objs) if s[1].start <= cx < s[1].stop]
    pool = cover or list(range(n))
    main = max(pool, key=lambda i: areas[i])
    dist = ndimage.distance_transform_edt(lab != main + 1)   # distance of every pixel to the main body
    keep = np.zeros(n + 1, bool)
    keep[main + 1] = True
    for i in range(n):
        if i != main and areas[i] >= 30 and dist[lab == i + 1].min() <= gap:
            keep[i + 1] = True
    out = rgba.copy()
    out[..., 3] = np.where(keep[lab], rgba[..., 3], 0)
    return out


def silhouette_box(rgba):
    a = rgba[..., 3] > 128
    ys, xs = np.where(a)
    if len(ys) == 0:
        return None
    return xs.min(), ys.min(), xs.max(), ys.max()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--rows", type=int, default=2)
    ap.add_argument("--frames", type=int, default=13, help="number of frames, sampled evenly over the clip")
    ap.add_argument("--step", type=int, default=0, help="take every Nth frame instead of --frames")
    ap.add_argument("--names", default="", help="comma separated names, row by row (default c01..cNN)")
    ap.add_argument("--pad", type=int, default=96, help="pixels added around each cell so swings past the line stay whole")
    ap.add_argument("--gap", type=int, default=14, help="a piece within this many px of the main body is kept")
    ap.add_argument("--scales", default="", help="comma separated shrink factor per character, in reading order (e.g. 0.55,0.55,0.78,0.78,0.78,1,1,1,1,1): the whole frame is scaled about the feet anchor after the cut, to bring characters that were enlarged for the video back to their true rank size")
    ap.add_argument("--fps", type=int, default=12, help="playback rate of preview.gif")
    a = ap.parse_args()

    out = Path(a.out)
    n_cells = a.cols * a.rows
    scales = [float(x) for x in a.scales.split(",") if x.strip()]
    if scales and len(scales) != a.cols * a.rows:
        sys.exit(f"error: {len(scales)} scales for {a.cols * a.rows} cells")
    names = [s.strip() for s in a.names.split(",") if s.strip()] or [f"c{i + 1:02d}" for i in range(n_cells)]
    if len(names) != n_cells:
        sys.exit(f"error: {len(names)} names for {n_cells} cells")

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.clip, str(Path(tmp) / "%04d.png")], check=True)
        files = sorted(Path(tmp).glob("*.png"))
        if not files:
            sys.exit("error: no frames read")
        if a.step > 0:
            pick = list(range(0, len(files), a.step))
        else:
            pick = sorted(set(np.linspace(0, len(files) - 1, a.frames).round().astype(int).tolist()))
        frames = [np.array(Image.open(files[i]).convert("RGB")) for i in pick]

    H, W = frames[0].shape[:2]
    cw0, ch0 = W // a.cols, H // a.rows
    P = a.pad
    cw, ch = cw0 + 2 * P, ch0 + 2 * P
    anchor = (cw // 2, P + int(round(0.88 * ch0)))
    padded = []
    for fr in frames:
        big = np.empty((H + 2 * P, W + 2 * P, 3), np.uint8)
        big[:] = (255, 0, 255)                      # outside the clip counts as background
        big[P:P + H, P:P + W] = fr
        padded.append(big)
    print(f"clip {W}x{H}, {len(files)} frames read, {len(pick)} kept, cell {cw}x{ch}", file=sys.stderr)

    for idx, name in enumerate(names):
        r, c = divmod(idx, a.cols)
        cell = [fr[r * ch0:r * ch0 + ch, c * cw0:c * cw0 + cw] for fr in padded]
        keyed = [keep_main(key_magenta(x), cw // 2, a.gap) for x in cell]
        box = silhouette_box(keyed[0])
        if box is None:
            print(f"warning: {name}: empty first frame", file=sys.stderr)
            continue
        dx = anchor[0] - (box[0] + box[2]) // 2
        dy = anchor[1] - box[3]
        d = out / name / "frames"
        d.mkdir(parents=True, exist_ok=True)
        placed = []
        touches = []
        for k, rgba in enumerate(keyed):
            canvas = np.zeros((ch, cw, 4), np.uint8)
            ys0, xs0 = max(0, dy), max(0, dx)
            ys1, xs1 = min(ch, ch + dy), min(cw, cw + dx)
            canvas[ys0:ys1, xs0:xs1] = rgba[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
            img = Image.fromarray(canvas, "RGBA")
            s = scales[idx] if scales else 1.0
            if s != 1.0:
                small = img.resize((max(1, round(cw * s)), max(1, round(ch * s))), Image.LANCZOS)
                img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
                img.paste(small, (round(anchor[0] - anchor[0] * s), round(anchor[1] - anchor[1] * s)))
            img.save(d / f"f{k + 1:02d}.png")
            placed.append(img)
            bx = silhouette_box(rgba)
            if bx and (bx[0] <= 1 or bx[2] >= cw - 2 or bx[1] <= 1 or bx[3] >= ch - 2):
                touches.append(k + 1)
        sheet = Image.new("RGBA", (cw * len(placed), ch))
        for k, img in enumerate(placed):
            sheet.paste(img, (k * cw, 0))
        sheet.save(out / name / "sheet.png")
        gif = []
        for img in placed:
            bgc = Image.new("RGBA", img.size, (60, 60, 70, 255))
            bgc.alpha_composite(img)
            gif.append(bgc.convert("P", palette=Image.ADAPTIVE))
        gif[0].save(out / name / "preview.gif", save_all=True, append_images=gif[1:], duration=int(1000 / a.fps), loop=0, disposal=2)
        if touches:
            print(f"warning: {name}: silhouette touches the window edge in frames {touches}", file=sys.stderr)
        print(f"{name}: {len(placed)} frames -> {out / name}")


if __name__ == "__main__":
    main()
