"""Smooth & Simplify: the vector-editor clean-up applied to every outline (v3, 2026-11-08).

Modelled on three known tools:
  * Illustrator Object > Path > Simplify: 'curve precision' + 'corner point angle threshold' (corners sharper than the
    threshold are kept, everything else becomes smooth anchors).
  * Potrace (the engine behind most 'image trace'): corner parameter `alphamax`, then 'curve optimization'
    (`opttolerance`): neighbouring Bezier segments are merged into one when the merged curve stays within tolerance.
  * Curve fairing (Moreton 1992, minimum variation curves): a fair curve is one whose curvature changes as little as
    possible, so wobbles and kinks are removed by minimising the 3rd difference (curvature variation) of the outline.

Steps for one closed outline (1 px samples):
  1. JOIN    : before outlining, gaps < ~1.5 px inside a layer are closed and crumbs dropped (Illustrator Join).
  2. CORNERS : a point is a corner only if it is sharp at two scales (k=4 and k=8 px): inner angle < corner_deg and
               < corner_deg + 20. Noise bends fail the large scale test; real tips pass both (potrace alphamax idea).
  3. FAIR    : between two corners (pinned), solve  min |q-p|^2 + l2 |D2 q|^2 + l3 |D3 q|^2  (bending + curvature
               variation). Then the loop is pushed out along its normals to give back the area fairing removed.
  4. FIT     : Schneider cubic fit (tolerance `tol`), G1 at every smooth anchor (collinear handles).
  5. MERGE   : potrace-style curve optimisation: repeatedly merge two neighbouring segments across a smooth anchor
               when one cubic still fits all their samples within `merge_tol`. Fewer, longer, rounder curves.
  5b. KINKS  : an anchor whose handles turn < 35 deg becomes smooth (Illustrator corner angle threshold) before MERGE.
  6. HANDLES : handle length capped at 0.45 x chord (designer paths measure 0.21-0.38) so no loops or bulges."""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy import ndimage as ndi
from skimage import measure
from bezier import resample, turning, fit_cubic, _unit, bez

# ---------- 1. join ----------
def join_clean(cover, ss, min_area=8, close_px=1.5):
    m = cover > 0.5
    r = max(1, int(round(close_px * ss)))
    st = ndi.generate_binary_structure(2, 1)
    m = ndi.binary_closing(m, st, iterations=r)
    for inv in (False, True):
        tgt = ~m if inv else m
        lab, n = ndi.label(tgt)
        if n:
            sizes = ndi.sum(tgt, lab, range(1, n + 1))
            m[np.isin(lab, 1 + np.flatnonzero(sizes < min_area * ss * ss))] = inv
    return m

# ---------- 2. corners ----------
def corners_2scale(c, corner_deg=145):
    _, _, in4 = turning(c, 4)
    _, _, in8 = turning(c, 8)
    n = len(c)
    cand = np.flatnonzero((in4 < corner_deg) & (in8 < corner_deg + 20))
    idx = []
    for i in cand[np.argsort(in4[cand])]:
        if all(min(abs(i - j), n - abs(i - j)) > 6 for j in idx):
            idx.append(int(i))
    return sorted(idx)

# ---------- 3. fair ----------
def _diff(n, order, closed):
    """Forward difference operator of a given order (periodic when closed)."""
    if closed:
        D1 = sp.diags([-1.0, 1.0], [0, 1], shape=(n, n)).tolil()
        D1[n - 1, 0] = 1.0
        D1 = D1.tocsr()
        D = sp.eye(n, format="csr")
        for _ in range(order):
            D = D1 @ D
        return D
    D = sp.eye(n, format="csr")
    for _ in range(order):
        m = D.shape[0]
        D = sp.diags([-1.0, 1.0], [0, 1], shape=(m - 1, m)) @ D
    return D

def fair_run(p, l2, l3, closed=False):
    n = len(p)
    if n < 6:
        return p
    D2, D3 = _diff(n, 2, closed), _diff(n, 3, closed)
    A = sp.eye(n) + l2 * (D2.T @ D2) + l3 * (D3.T @ D3)
    if closed:
        return np.c_[spla.spsolve(A.tocsc(), p[:, 0]), spla.spsolve(A.tocsc(), p[:, 1])]
    # pin both ends (and their first neighbour, so the corner keeps its direction)
    fixed = np.zeros(n, bool); fixed[[0, 1, n - 2, n - 1]] = True
    free = ~fixed
    A = A.tocsr()
    Aff = A[free][:, free].tocsc()
    out = p.copy()
    for d in range(2):
        rhs = p[free, d] - A[free][:, fixed] @ p[fixed, d]
        out[free, d] = spla.spsolve(Aff, rhs)
    return out

def _area(c):
    x, y = c[:, 0], c[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)

def _normals(c):
    t = np.roll(c, -1, 0) - np.roll(c, 1, 0)
    t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-9
    return np.c_[t[:, 1], -t[:, 0]]

# ---------- 5. merge ----------
def _seg_samples(seg, n=16):
    return bez(seg, np.linspace(0, 1, n))

def merge_segments(segs, smooth, tol):
    """segs: list of cubic segments of one closed loop; smooth[i] True if anchor at segs[i][0] is smooth (G1)."""
    segs, smooth = list(segs), list(smooth)
    changed = True
    while changed and len(segs) > 2:
        changed = False
        best = None
        for i in range(len(segs)):
            j = (i + 1) % len(segs)
            if not smooth[j]:
                continue
            pts = np.vstack([_seg_samples(segs[i])[:-1], _seg_samples(segs[j])])
            t1 = _unit(segs[i][1] - segs[i][0]) if np.linalg.norm(segs[i][1] - segs[i][0]) > 1e-6 else _unit(pts[1] - pts[0])
            t2 = _unit(segs[j][2] - segs[j][3]) if np.linalg.norm(segs[j][2] - segs[j][3]) > 1e-6 else _unit(pts[-2] - pts[-1])
            fs = fit_cubic(pts, t1, t2, tol)
            if len(fs) == 1:
                e = np.max(np.linalg.norm(bez(fs[0], np.linspace(0, 1, 200))[:, None] - pts[None], axis=2).min(0))
                if best is None or e < best[0]:
                    best = (e, i, j, fs[0])
        if best is not None:
            _, i, j, seg = best
            segs[i] = seg
            del segs[j]; del smooth[j]
            changed = True
    return segs, smooth

def cap_handles(segs, k=0.45):
    out = []
    for p0, p1, p2, p3 in segs:
        ch = np.linalg.norm(p3 - p0)
        h1, h2 = p1 - p0, p2 - p3
        if np.linalg.norm(h1) > k * ch: h1 = h1 / np.linalg.norm(h1) * k * ch
        if np.linalg.norm(h2) > k * ch: h2 = h2 / np.linalg.norm(h2) * k * ch
        out.append((p0, p0 + h1, p3 + h2, p3))
    return out

def unify_corners(segs, smooth, smooth_below=35.0):
    """Illustrator's corner angle threshold, applied to anchors: a 'corner' whose two handles turn less than
    `smooth_below` degrees is a kink, not a design corner -> make it smooth (both handles on the bisector)."""
    segs = [list(s) for s in segs]
    smooth = list(smooth)
    for j in range(len(segs)):
        i = j - 1
        a = segs[i][3] - segs[i][2]
        b = segs[j][1] - segs[j][0]
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na < 1e-6 or nb < 1e-6:
            continue
        ang = np.degrees(np.arccos(np.clip(np.dot(a, b) / na / nb, -1, 1)))
        if ang < smooth_below:
            t = _unit(a / na + b / nb)
            segs[i][2] = segs[i][3] - t * na
            segs[j][1] = segs[j][0] + t * nb
            smooth[j] = True
    return [tuple(s) for s in segs], smooth

# ---------- driver ----------
def smooth_simplify(cover, ss=2, corner_deg=145, sigma=4.5, tol=0.5, merge_tol=0.9, min_area=8, close_px=1.5):
    """cover: coverage image at ss x frame resolution. Returns (paths, stats); paths are closed segment lists in frame px
    (fill even-odd); stats: anchors, corners."""
    m = join_clean(cover, ss, min_area, close_px)
    f = ndi.gaussian_filter(np.pad(m.astype(float), 2), 0.6 * ss)
    paths, n_anchor, n_corner = [], 0, 0
    l2, l3 = 0.5 * sigma**4, 0.25 * sigma**6
    for c in measure.find_contours(f, 0.5):
        c = (c[:, ::-1] - 2 + 0.5) / ss - 0.5
        if len(c) < 8:
            continue
        c = resample(c, 1.0)
        n = len(c)
        if n < 10:
            continue
        s = min(1.0, n / 60.0)  # small shards: weaker fairing
        A0 = _area(c)
        cs = corners_2scale(c, corner_deg)
        if not cs:
            q = fair_run(c, l2 * s, l3 * s, closed=True)
            runs_idx = [(0, n // 2), (n // 2, n)]
        else:
            q = c.copy()
            for a, b in zip(cs, cs[1:] + [cs[0] + n]):
                idx = np.arange(a, b + 1) % n
                q[idx] = fair_run(c[idx], l2 * s, l3 * s)
            runs_idx = list(zip(cs, cs[1:] + [cs[0] + n]))
        # give back the area lost to fairing (uniform push along normals, corners stay)
        A1 = _area(q)
        per = np.sum(np.linalg.norm(np.diff(np.vstack([q, q[:1]]), axis=0), axis=1))
        if per > 0 and abs(A1) > 1:
            nrm = _normals(q)
            if abs(_area(q + nrm)) < abs(A1):
                nrm = -nrm  # make it point outwards
            push = nrm * (abs(A0) - abs(A1)) / per
            if cs:
                push[cs] = 0
            q = q + push
        segs, smooth = [], []
        for a, b in runs_idx:
            run = q[np.arange(a, b + 1) % n]
            if len(run) < 2:
                continue
            if cs:
                t1 = _unit(run[min(2, len(run) - 1)] - run[0]); t2 = _unit(run[max(-3, -len(run))] - run[-1])
            else:
                t1 = _unit(q[(a + 1) % n] - q[(a - 1) % n]); t2 = _unit(q[(b - 1) % n] - q[(b + 1) % n])
            fs = fit_cubic(run, t1, t2, tol)
            segs += fs
            smooth += [not cs] + [True] * (len(fs) - 1)
        segs, smooth = unify_corners(segs, smooth)
        segs, smooth = merge_segments(segs, smooth, merge_tol)
        segs = cap_handles(segs)
        paths.append(segs)
        n_anchor += len(segs); n_corner += smooth.count(False)
    return paths, dict(anchors=n_anchor, corners=n_corner)
