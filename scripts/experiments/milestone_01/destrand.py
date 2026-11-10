# Milestone 01 experiment (not a core tool). Removes thin leftover strands of a model-drawn slash arc from EXPORTED RGBA frames.
# Usage: python destrand.py <state dir> <first> <last>   (frame numbers as in the file names, 1-based); rewrites @2x and re-derives @1x (LANCZOS, as video_to_sheet).
# Rule: the body and the blade have dark outlines; arc strands are light lines with none. Light pixels farther than R px (@2x) from any
# non-light opaque pixel (outline, armour colour) are strands. Then detached small opaque pieces are dropped.
import sys, pathlib, numpy as np
from PIL import Image
from scipy import ndimage as ndi
d, a, b = pathlib.Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); R = 3.5
for f2 in sorted((d / 'frames' / '@2x').glob('*.png')):
    n = int(f2.stem.rsplit('_', 1)[1])
    if not a <= n <= b: continue
    im = np.asarray(Image.open(f2).convert('RGBA')).astype(int); rgb, al = im[..., :3], im[..., 3]
    mn, mx = rgb.min(axis=2), rgb.max(axis=2)
    light = (al > 0) & (mn > 175) & (mx - mn < 60)
    core = (al > 128) & ~light
    far = ndi.distance_transform_edt(~core) > R
    rm = light & far
    keep = (al > 0) & ~rm
    lab, k = ndi.label(keep, structure=np.ones((3, 3)))
    if k > 1:
        size = ndi.sum(np.ones_like(lab), lab, np.arange(1, k + 1))
        keep = np.isin(lab, 1 + np.where(size >= max(40, 0.01 * size.max()))[0])
    out = im.copy(); out[~keep] = 0
    Image.fromarray(out.astype(np.uint8), 'RGBA').save(f2)
    f1 = d / 'frames' / '@1x' / f2.name
    Image.fromarray(out.astype(np.uint8), 'RGBA').resize((out.shape[1] // 2, out.shape[0] // 2), Image.LANCZOS).save(f1)
    print(f2.name, 'removed px', int(((al > 0) & ~keep).sum()))
