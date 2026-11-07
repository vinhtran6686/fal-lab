"""Swirl frame: centre fit, polar unwrapping, decomposition of a mask into polar bands (one run per angle).

A band is {(theta, r): theta0 <= theta <= theta1, lo(theta) <= r <= hi(theta)}. Every flat-colour shape of a swirl
(crescent, tongue, feather, rim, hook) is one band or a few bands joined at a fork."""
import numpy as np
from scipy import ndimage as ndi

NT = 1440          # angle bins (0.25 deg)
DR = 0.5           # radius step (px)
RMAX = 430

def fit_centre(union):
    """Kasa circle fit on the outer outline of the union: the swirl's pivot."""
    edge = union & ~ndi.binary_erosion(union, iterations=1)
    ys, xs = np.nonzero(edge)
    A = np.c_[2 * xs, 2 * ys, np.ones(len(xs))]
    b = xs**2 + ys**2
    cx, cy, k = np.linalg.lstsq(A, b, rcond=None)[0]
    return float(cx), float(cy), float(np.sqrt(k + cx * cx + cy * cy))

def to_polar(mask, c, seam=0.0):
    """Polar image P[j, i]: angle bin j (seam + j*dtheta, clockwise on screen = +theta in image coords), radius i*DR."""
    th = seam + np.arange(NT) * 2 * np.pi / NT
    r = np.arange(0, RMAX, DR)
    T, R = np.meshgrid(th, r, indexing="ij")
    x = c[0] + R * np.cos(T)
    y = c[1] + R * np.sin(T)
    return ndi.map_coordinates(mask.astype(float), [y, x], order=1, cval=0) > 0.5

def seam_angle(union, c):
    P = to_polar(union, c)
    cov = ndi.uniform_filter1d(P.sum(1).astype(float), 9, mode="wrap")
    return float(np.argmin(cov) * 2 * np.pi / NT)

def runs(col):
    d = np.diff(np.r_[0, col.astype(np.int8), 0])
    s, e = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
    return list(zip(s, e))  # [s, e) in radius bins

def bands(P, min_cols=2, ext=4, scale=DR, offset=0.0):
    """Link runs column to column; at a fork the run with the biggest overlap keeps the band, others start new ones."""
    open_b = []   # (band_id, (s, e))
    fork_start, fork_end = {}, {}
    out = {}
    nid = 0
    for j in range(P.shape[0]):
        rs = runs(P[j])
        claimed = {}
        # each open band picks the run with most overlap; each run goes to the band with most overlap
        pairs = []
        for bi, (bid, (s0, e0)) in enumerate(open_b):
            for ri, (s1, e1) in enumerate(rs):
                ov = min(e0, e1) - max(s0, s1)
                if ov > 0:
                    pairs.append((ov, bi, ri))
        used_b, used_r = set(), set()
        for ov, bi, ri in sorted(pairs, reverse=True):
            if bi in used_b or ri in used_r:
                continue
            used_b.add(bi); used_r.add(ri)
            claimed[ri] = open_b[bi][0]
        new_open = []
        for ri, (s, e) in enumerate(rs):
            if ri in claimed:
                bid = claimed[ri]
            else:
                bid = nid; nid += 1
                out[bid] = []
                # born at a fork: a run of the previous column overlaps it but was kept by another band
                par = [(b, se) for b, se in open_b if min(se[1], e) - max(se[0], s) > 0]
                fork_start[bid] = par[0] if par else None
            out[bid].append((j, s, e))
            new_open.append((bid, (s, e)))
        # bands that stop here although a run of this column overlaps them: they merge into another band
        for bi, (bid, (s0, e0)) in enumerate(open_b):
            if bi not in used_b:
                par = [(s1, e1) for s1, e1 in rs if min(e0, e1) - max(s0, s1) > 0]
                fork_end[bid] = par[0] if par else None
        open_b = new_open
    res = []
    for bid, cols in out.items():
        if len(cols) < min_cols:
            continue
        cols = list(cols)
        f0, f1 = fork_start.get(bid), fork_end.get(bid)
        # a branch born at / dying into a fork overlaps its parent by `ext` columns (a stroke drawn INTO the parent,
        # never cut flush against it): keeps the union seamless after smoothing
        if f0 is not None:
            j0, s0, e0 = cols[0]
            cols = [(j0 - k, s0, e0) for k in range(ext, 0, -1)] + cols
        if f1 is not None:
            j1, s1, e1 = cols[-1]
            cols = cols + [(j1 + k, s1, e1) for k in range(1, ext + 1)]
        a = np.array(cols, float)
        res.append(dict(j=a[:, 0], lo=offset + a[:, 1] * scale, hi=offset + a[:, 2] * scale, fork0=f0 is not None, fork1=f1 is not None))
    return res


RS = 200.0  # radius used to turn angles into px for strokes that run along the radius

def bands_any(P, seam, axis="theta"):
    """axis 'theta': strokes along the sweep (most shapes). axis 'r': strokes along the radius (hook tips pointing
    in/out); their angle is stored as arc length at radius RS so the same width formula applies."""
    if axis == "theta":
        return bands(P)
    return bands(P.T, scale=2 * np.pi / NT * RS, offset=seam * RS)
