#!/usr/bin/env python3
"""Replace ONE character of a lineup image with a character drawn in another image (costs nothing).

    python scripts/lineup/lineup_replace.py <base.png> --new <other.png> --cell 2 --pick 1 --out <result.png>
                                             [--cols 5 --rows 2] [--min-area 400]

Why: redrawing a whole grid changes every character; to fix one or two, draw them again alone (or in a small
sheet, large, so the detail is sharper) and swap them in. Characters are found as in lineup_regrid.py (per row,
the biggest pieces from left to right). --cell is the 1-based cell of the BASE image to replace (reading order),
--pick the 1-based character of the NEW image (reading order). The old character is erased (magenta), the new one
is scaled so that its silhouette area equals the old one's and placed with its feet (lowest point) and its
horizontal centre on the old ones. Run lineup_regrid.py afterwards. Needs numpy, scipy, Pillow.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
from lineup_split import key_magenta  # noqa: E402


def characters(rgb, cols, rows, min_area):
    """Return the keyed RGBA and a list (reading order) of boolean masks, one per character, for an image."""
    rgba = key_magenta(rgb)
    mask = rgba[..., 3] > 128
    lab, n = ndimage.label(mask)
    areas = ndimage.sum(mask, lab, range(1, n + 1))
    coms = ndimage.center_of_mass(mask, lab, range(1, n + 1))
    ch = rgb.shape[0] / rows
    groups = []
    for r in range(rows):
        pieces = [i for i in range(n) if areas[i] >= min_area and int(coms[i][0] // ch) == r]
        seeds = sorted(sorted(pieces, key=lambda i: -areas[i])[:cols], key=lambda i: coms[i][1])
        g = {s: [s + 1] for s in seeds}
        for i in pieces:
            if i not in g:
                near = min(seeds, key=lambda s: (coms[i][0] - coms[s][0]) ** 2 + (coms[i][1] - coms[s][1]) ** 2)
                g[near].append(i + 1)
        groups += [np.isin(lab, g[s]) for s in seeds]
    return rgba, groups


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base")
    ap.add_argument("--new", required=True)
    ap.add_argument("--cell", type=int, required=True)
    ap.add_argument("--pick", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--rows", type=int, default=2)
    ap.add_argument("--new-cols", type=int, default=2, help="characters per row in the NEW image")
    ap.add_argument("--new-rows", type=int, default=1)
    ap.add_argument("--min-area", type=int, default=400)
    a = ap.parse_args()

    base = np.array(Image.open(a.base).convert("RGB"))
    new = np.array(Image.open(a.new).convert("RGB"))
    brgba, bgroups = characters(base, a.cols, a.rows, a.min_area)
    nrgba, ngroups = characters(new, a.new_cols, a.new_rows, a.min_area)
    old = bgroups[a.cell - 1]
    nw = ngroups[a.pick - 1]

    ys, xs = np.where(old)
    ox, oy_bottom, oarea = (xs.min() + xs.max()) / 2, ys.max(), old.sum()
    # erase the old character and its soft edge
    erase = ndimage.binary_dilation(old, iterations=4)
    out = base.copy()
    out[erase] = (255, 0, 255)

    nys, nxs = np.where(nw)
    crop = nrgba[nys.min():nys.max() + 1, nxs.min():nxs.max() + 1].copy()
    cm = nw[nys.min():nys.max() + 1, nxs.min():nxs.max() + 1]
    near = ndimage.binary_dilation(cm, iterations=3)
    crop[..., 3] = np.where(near, crop[..., 3], 0)
    s = (oarea / float(nw.sum())) ** 0.5
    img = Image.fromarray(crop, "RGBA")
    img = img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)
    layer = Image.fromarray(out, "RGB").convert("RGBA")
    px, py = int(round(ox - img.width / 2)), int(round(oy_bottom - img.height + 1))
    layer.alpha_composite(img, (max(px, 0), max(py, 0))) if px >= 0 and py >= 0 else layer.alpha_composite(img.crop((max(-px, 0), max(-py, 0), img.width, img.height)), (max(px, 0), max(py, 0)))
    layer.convert("RGB").save(a.out)
    print(f"cell {a.cell}: replaced by character {a.pick} of {a.new}, scale {s:.2f}, saved {a.out}")


if __name__ == "__main__":
    main()
