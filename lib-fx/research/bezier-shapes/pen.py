"""Pen-tool pass: turn a rendered layer (union of formula strokes) into clean closed Bezier paths, the way a designer
redraws a rough shape with the pen tool.

  1. drop crumbs: islands and holes smaller than `min_area` px
  2. outline at sub-pixel precision
  3. keep only TRUE corners: tips/notches whose inner angle < `corner_deg` over a +-`k` px window
  4. between two corners, the outline is smoothed along its length (gaussian, sigma px) with the corners pinned,
     so the joins between strokes stop showing as small kinks
  5. fit cubic Beziers (Schneider) with G1 joints: one smooth curve from corner to corner, few anchors"""
import numpy as np
from scipy import ndimage as ndi
from skimage import measure
from bezier import resample, turning, fit_cubic, _unit, sample_path

def _clean(mask, min_area):
    m = mask.copy()
    for inv in (False, True):
        tgt = ~m if inv else m
        lab, n = ndi.label(tgt)
        if n:
            sizes = ndi.sum(tgt, lab, range(1, n + 1))
            small = np.isin(lab, 1 + np.flatnonzero(sizes < min_area))
            m[small] = inv
    return m

def _corners(c, k, corner_deg):
    turn, sgn, inner = turning(c, k)
    n = len(c)
    idx = []
    for i in np.argsort(inner):
        if inner[i] >= corner_deg:
            break
        if all(min(abs(i - j), n - abs(i - j)) > 2 * k for j in idx):
            idx.append(int(i))
    return sorted(idx)

def _smooth_run(run, sigma, pin=True):
    if len(run) < 5:
        return run
    s = np.c_[ndi.gaussian_filter1d(run[:, 0], sigma, mode="nearest"), ndi.gaussian_filter1d(run[:, 1], sigma, mode="nearest")]
    if pin:  # blend back to the exact corner positions at both ends
        n = len(run)
        w = np.minimum(np.arange(n), np.arange(n)[::-1]).astype(float)
        w = np.clip(w / (2 * sigma), 0, 1)[:, None]
        s = w * s + (1 - w) * run
    return s

def pen_paths(cover, ss=1, min_area=30, k=5, corner_deg=115, sigma=3.0, tol=0.8):
    """cover: float or bool coverage image at `ss` x the frame resolution. Returns list of closed paths (segment lists)
    in frame pixels, to be filled even-odd (holes are separate paths)."""
    m = cover > 0.5 if cover.dtype != bool else cover
    m = _clean(m, min_area * ss * ss)
    f = ndi.gaussian_filter(np.pad(m.astype(float), 2), 0.6 * ss)
    paths = []
    for c in measure.find_contours(f, 0.5):
        c = (c[:, ::-1] - 2 + 0.5) / ss - 0.5
        if len(c) < 8:
            continue
        c = resample(c, 1.0)
        n = len(c)
        if n < 10:
            continue
        sigma_c = min(sigma, n / 25.0)  # small shards keep their shape
        cs = _corners(c, k, corner_deg)
        segs = []
        if not cs:
            sm = np.c_[ndi.gaussian_filter1d(c[:, 0], sigma_c, mode="wrap"), ndi.gaussian_filter1d(c[:, 1], sigma_c, mode="wrap")]
            a, b = 0, n // 2
            for s0, s1 in ((a, b), (b, n)):
                run = sm[np.arange(s0, s1 + 1) % n]
                t1 = _unit(sm[(s0 + 1) % n] - sm[(s0 - 1) % n])
                t2 = _unit(sm[(s1 - 1) % n] - sm[(s1 + 1) % n])
                segs += fit_cubic(run, t1, t2, tol)
        else:
            for a, b in zip(cs, cs[1:] + [cs[0] + n]):
                run = _smooth_run(c[np.arange(a, b + 1) % n], sigma_c)
                if len(run) < 2:
                    continue
                t1 = _unit(run[min(3, len(run) - 1)] - run[0])
                t2 = _unit(run[max(-4, -len(run))] - run[-1])
                segs += fit_cubic(run, t1, t2, tol)
        paths.append(segs)
    return paths

def kinks_per_100px(mask, lo=15, hi=80, k=3):
    """Smoothness meter: count of mid-size bends (turning lo..hi degrees over +-k px, local maxima) per 100 px of outline.
    Real tips turn more than `hi`; smooth curves turn less than `lo`; what is left are kinks."""
    f = ndi.gaussian_filter(np.pad(mask.astype(float), 2), 0.7)
    tot, L = 0, 0.0
    for c in measure.find_contours(f, 0.5):
        if len(c) < 20:
            continue
        c = resample(c[:, ::-1], 1.0)
        turn, _, _ = turning(c, k)
        pk = (turn >= np.roll(turn, 1)) & (turn > np.roll(turn, -1)) & (turn > lo) & (turn < hi)
        tot += int(pk.sum()); L += len(c)
    return 100.0 * tot / max(L, 1)
