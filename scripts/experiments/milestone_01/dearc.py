# Milestone 01 experiment (not a core tool). Usage: python dearc.py in.png out.png [min_component_px]
"""Remove a model-drawn slash arc from magenta-key frames by colour + connectivity.
Arc pixels are white -> pink -> magenta blends (no grey, no outline). A connected group of such pixels that touches the
magenta background and is big enough is the arc; small bright groups enclosed by the character (armour highlights) stay."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst, *rest = sys.argv[1:]
MIN = int(rest[0]) if rest else 120
a = np.asarray(Image.open(src).convert('RGB')).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
bg = (R > 170) & (B > 170) & (G < 90)
pink = (np.minimum(R, B) - G > 18) & (np.minimum(R, B) > 150) & ~bg          # white->magenta blend
white = (np.minimum(np.minimum(R, G), B) > 232)                                   # arc core (and highlights)
cand = pink | white
lab, n = ndi.label(cand, structure=np.ones((3, 3)))
remove = np.zeros_like(cand)
if n:
    bgd = ndi.binary_dilation(bg, iterations=2)
    idx = np.arange(1, n + 1)
    size = ndi.sum(np.ones_like(lab), lab, idx)
    touch = ndi.sum(bgd, lab, idx)
    pinkshare = ndi.sum(pink, lab, idx) / np.maximum(size, 1)
    bad = idx[(size >= MIN) & (touch > 0.15 * np.sqrt(size)) & (pinkshare > 0.15)]
    remove = np.isin(lab, bad)
    remove = ndi.binary_dilation(remove, iterations=1) & ~ (np.maximum(np.maximum(R, G), B) < 110)  # eat the soft edge, keep dark outline
out = a.copy(); out[remove] = (255, 0, 255)
Image.fromarray(out.astype(np.uint8)).save(dst)
print(src, int(remove.sum()))
