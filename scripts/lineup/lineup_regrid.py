#!/usr/bin/env python3
"""Re-place the characters of a lineup image: shrink each one and centre it in its own cell (costs nothing).

    python scripts/lineup/lineup_regrid.py <lineup.png> --out <new.png> [--cols 5 --rows 2] [--scale 0.68]
                                            [--feet 0.70] [--min-area 400]

The image model ignores sizes and positions asked in a prompt (fal-image/style-chunky.md section 9), so the room
between characters is made here, by code: the magenta background is keyed, the connected pieces are grouped by the
cell that holds their centre of mass, every group (one character with its weapon) is scaled by --scale and pasted on
a clean magenta canvas of the same size: horizontally centred on the middle of its cell, the lowest point of the
group (the feet; a weapon hanging lower counts) on the line --feet x cell height. Prints the size of every character
(width and height as a share of the cell) and warns when a cell holds nothing or more than one big group.
Needs numpy, scipy and Pillow.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
from lineup_split import key_magenta  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--rows", type=int, default=2)
    ap.add_argument("--scale", type=float, default=0.68, help="shrink factor of every character")
    ap.add_argument("--feet", type=float, default=0.70, help="where the lowest point of a character sits, as a share of the cell height")
    ap.add_argument("--min-area", type=int, default=400, help="pieces smaller than this many pixels are noise")
    a = ap.parse_args()

    rgb = np.array(Image.open(a.image).convert("RGB"))
    H, W = rgb.shape[:2]
    cw, ch = W / a.cols, H / a.rows
    rgba = key_magenta(rgb)
    mask = rgba[..., 3] > 128
    lab, n = ndimage.label(mask)
    areas = ndimage.sum(mask, lab, range(1, n + 1))
    coms = ndimage.center_of_mass(mask, lab, range(1, n + 1))
    groups = {}
    for i in range(n):
        if areas[i] < a.min_area:
            continue
        cy, cx = coms[i]
        cell = int(cy // ch) * a.cols + int(cx // cw)
        groups.setdefault(cell, []).append(i + 1)

    canvas = Image.new("RGBA", (W, H), (255, 0, 255, 255))
    full = Image.fromarray(rgba, "RGBA")
    for cell in range(a.cols * a.rows):
        ids = groups.get(cell)
        if not ids:
            print(f"warning: cell {cell + 1}: empty", file=sys.stderr)
            continue
        keep = np.isin(lab, ids)
        # every pixel of the pieces, plus the soft edge around them (alpha > 0 within 3 px)
        near = ndimage.binary_dilation(keep, iterations=3)
        part = rgba.copy()
        part[..., 3] = np.where(near, rgba[..., 3], 0)
        ys, xs = np.where(part[..., 3] > 0)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        crop = Image.fromarray(part[y0:y1, x0:x1], "RGBA")
        w, h = max(1, round(crop.width * a.scale)), max(1, round(crop.height * a.scale))
        crop = crop.resize((w, h), Image.LANCZOS)
        r, c = divmod(cell, a.cols)
        px = int(round(c * cw + cw / 2 - w / 2))
        py = int(round(r * ch + a.feet * ch - h))
        canvas.alpha_composite(crop, (px, py))
        print(f"cell {cell + 1}: {len(ids)} piece(s), {100 * w / cw:.0f}% wide, {100 * h / ch:.0f}% tall, left {100 * (px - c * cw) / cw:.0f}%, top {100 * (py - r * ch) / ch:.0f}%")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(a.out)
    print(f"saved {a.out}")


if __name__ == "__main__":
    main()
