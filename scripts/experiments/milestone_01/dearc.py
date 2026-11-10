# Milestone 01 experiment (not a core tool). Usage: python dearc.py in.png out.png [far_px]
"""Remove a model-drawn slash arc from magenta-key frames.
Arc = white -> pink -> magenta blends with no grey, gold, red or dark outline in it. Armour highlights are also white but always
sit within a few pixels of the character's real colours; the arc is a wide band far from them. So: candidate pixels (white or
pink-white) that are more than FAR px from any real character pixel are arc seeds; the arc is then grown back through connected
candidate pixels up to the character's edge (a thin fringe next to the blade may stay)."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst, *rest = sys.argv[1:]
FAR = float(rest[0]) if rest else 4.0
a = np.asarray(Image.open(src).convert('RGB')).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
mn = np.minimum(np.minimum(R, G), B)
bg = (R > 170) & (B > 170) & (G < 90)
pink = (np.minimum(R, B) - G > 18) & (np.minimum(R, B) > 150) & ~bg
white = mn > 232
cand = (pink | white) & ~bg
body = ~bg & ~cand                                        # grey, gold, red, outlines
dist = ndi.distance_transform_edt(~body)                  # px to the nearest real character pixel
seed = cand & (dist > FAR)
lab, n = ndi.label(seed, structure=np.ones((3, 3)))
if n:  # ignore tiny seeds (noise inside wide armour highlights)
    size = ndi.sum(np.ones_like(lab), lab, np.arange(1, n + 1))
    seed = np.isin(lab, 1 + np.where(size >= 25)[0])
# grow the seeds through candidate pixels, but not into pixels hugging the body (<= 1.5 px): keeps highlights' rims
grow = cand & (dist > 1.5)
remove = ndi.binary_propagation(seed, mask=grow)
remove = ndi.binary_dilation(remove, iterations=1) & ~body
out = a.copy(); out[remove] = (255, 0, 255)
# last pass: thin leftovers of the arc rim are detached from the character; keep the main body and big parts only
o = out.astype(int); r, g, b = o[..., 0], o[..., 1], o[..., 2]
fg = ~((np.minimum(r, b) - g > 60) & (np.minimum(r, b) > 150))            # not magenta-ish
lab, n = ndi.label(fg, structure=np.ones((3, 3)))
if n > 1:
    size = ndi.sum(np.ones_like(lab), lab, np.arange(1, n + 1))
    keep = 1 + np.where(size >= max(300, 0.02 * size.max()))[0]
    stray = fg & ~np.isin(lab, keep)
    out[stray] = (255, 0, 255); remove |= stray
Image.fromarray(out.astype(np.uint8)).save(dst)
print(src, int(remove.sum()))
