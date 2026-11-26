#!/usr/bin/env python3
"""Recolour pink or magenta paint on a character of a lineup image, before keying (costs nothing).

    python scripts/lineup/lineup_fix_pink.py <lineup.png> --out <fixed.png> [--target 62,88,122]

The image model sometimes paints a part of a character pink (a pair of trousers, a charm) although the prompt
forbids it; the key then eats the part. Pixels that are pink (red and blue well above green) but are NOT the
background (the background is red > 215, blue > 205, green < 70) are recoloured to --target (a steel blue by
default), keeping their lightness, so the shading stays. Pure background-blend edge pixels (very low green next
to the background) are left alone for the key. Prints the number of recoloured pixels. Needs numpy, scipy, Pillow.
"""
import argparse

import numpy as np
from PIL import Image
from scipy import ndimage


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--out", required=True)
    ap.add_argument("--target", default="62,88,122", help="R,G,B of the replacement colour")
    a = ap.parse_args()
    im = np.array(Image.open(a.image).convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    bg = (r > 215) & (b > 205) & (g < 70)
    pink = (~bg) & (r - g > 55) & (b - g > 45) & (abs(r - b) < 90)
    near = ndimage.binary_dilation(bg, iterations=2)
    m = pink & ~(near & (g < 50))
    t = np.array([int(x) for x in a.target.split(",")])
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    k = np.clip(lum / (0.299 * t[0] + 0.587 * t[1] + 0.114 * t[2]), 0.35, 1.6)[..., None]
    out = im.copy()
    new = np.clip(t[None, None, :] * k, 0, 255)
    out[m] = new[m].astype(int)
    Image.fromarray(out.astype(np.uint8)).save(a.out)
    print(f"recoloured {int(m.sum())} pixels -> {a.out}")


if __name__ == "__main__":
    main()
