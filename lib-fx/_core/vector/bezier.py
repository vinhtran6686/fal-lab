"""Cubic Bezier toolkit: evaluation, Schneider fitting with corner detection, outlines, rasterising, SVG output."""
import numpy as np
import cv2
from scipy import ndimage as ndi
from skimage import measure

# ---------- evaluation ----------
def bez(seg, t):
    p0, p1, p2, p3 = seg
    t = np.asarray(t)[:, None]
    u = 1 - t
    return u**3 * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t**3 * p3

def bez_d(seg, t):
    p0, p1, p2, p3 = seg
    t = np.asarray(t)[:, None]
    u = 1 - t
    return 3 * u * u * (p1 - p0) + 6 * u * t * (p2 - p1) + 3 * t * t * (p3 - p2)

def bez_dd(seg, t):
    p0, p1, p2, p3 = seg
    t = np.asarray(t)[:, None]
    return 6 * (1 - t) * (p2 - 2 * p1 + p0) + 6 * t * (p3 - 2 * p2 + p1)

def sample_path(segs, n=24):
    pts = [bez(s, np.linspace(0, 1, n, endpoint=False)) for s in segs]
    return np.vstack(pts) if pts else np.zeros((0, 2))

# ---------- Schneider fit ----------
def _chord(pts):
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    return d / d[-1] if d[-1] > 0 else np.linspace(0, 1, len(pts))

def _fit_one(pts, u, t1, t2):
    p0, p3 = pts[0], pts[-1]
    A1 = t1[None] * (3 * (1 - u) ** 2 * u)[:, None]
    A2 = t2[None] * (3 * (1 - u) * u**2)[:, None]
    C = np.array([[np.sum(A1 * A1), np.sum(A1 * A2)], [np.sum(A1 * A2), np.sum(A2 * A2)]])
    base = bez((p0, p0, p3, p3), u)
    X = np.array([np.sum(A1 * (pts - base)), np.sum(A2 * (pts - base))])
    seg_len = np.linalg.norm(p3 - p0)
    try:
        a1, a2 = np.linalg.solve(C, X)
    except np.linalg.LinAlgError:
        a1 = a2 = seg_len / 3
    eps = 1e-6 * seg_len
    if a1 < eps or a2 < eps or a1 > 3 * seg_len + 5 or a2 > 3 * seg_len + 5:
        a1 = a2 = seg_len / 3
    return (p0, p0 + t1 * a1, p3 + t2 * a2, p3)

def _reparam(seg, pts, u):
    d = bez(seg, u) - pts
    d1, d2 = bez_d(seg, u), bez_dd(seg, u)
    num = np.sum(d * d1, 1)
    den = np.sum(d1 * d1, 1) + np.sum(d * d2, 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        nu = u - np.where(np.abs(den) > 1e-9, num / den, 0)
    return np.clip(nu, 0, 1)

def _err(seg, pts, u):
    d = np.linalg.norm(bez(seg, u) - pts, axis=1)
    i = int(np.argmax(d))
    return d[i], i

def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v

def fit_cubic(pts, t1, t2, tol):
    """Fit points (open run, ends fixed) with cubic segments; t1 leaves pts[0], t2 points back into pts[-1]."""
    if len(pts) < 3:
        d = np.linalg.norm(pts[-1] - pts[0]) / 3
        return [(pts[0], pts[0] + t1 * d, pts[-1] + t2 * d, pts[-1])]
    u = _chord(pts)
    seg = _fit_one(pts, u, t1, t2)
    e, i = _err(seg, pts, u)
    if e < tol:
        return [seg]
    if e < tol * 4:
        for _ in range(6):
            u = _reparam(seg, pts, u)
            seg = _fit_one(pts, u, t1, t2)
            e, i = _err(seg, pts, u)
            if e < tol:
                return [seg]
    i = min(max(i, 1), len(pts) - 2)
    tc = _unit(pts[i - 1] - pts[i + 1]) if len(pts) > 2 else _unit(pts[0] - pts[-1])
    return fit_cubic(pts[: i + 1], t1, tc, tol) + fit_cubic(pts[i:], -tc, t2, tol)

# ---------- contours + corners ----------
def contours(mask, sigma=0.7):
    """Sub-pixel outlines (x, y) of a binary mask: level 0.5 of a lightly blurred mask."""
    f = ndi.gaussian_filter(np.pad(mask.astype(float), 2), sigma)
    cs = measure.find_contours(f, 0.5)
    return [c[:, ::-1] - 2 for c in cs if len(c) > 8]

def resample(c, step=1.0):
    c = np.vstack([c, c[:1]]) if np.linalg.norm(c[0] - c[-1]) > 1e-6 else c
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))]
    n = max(int(d[-1] / step), 8)
    s = np.linspace(0, d[-1], n, endpoint=False)
    return np.c_[np.interp(s, d, c[:, 0]), np.interp(s, d, c[:, 1])]

def turning(c, k=4):
    """Turning angle (deg) at each point of a closed resampled loop, over +-k samples."""
    a = np.roll(c, k, 0) - c
    b = np.roll(c, -k, 0) - c
    cos = np.sum(a * b, 1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-9)
    inner = np.degrees(np.arccos(np.clip(cos, -1, 1)))  # 180 = straight
    cross = a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    return 180 - inner, np.sign(cross), inner

def corners(c, k=4, thresh=55):
    turn, sgn, inner = turning(c, k)
    idx = []
    n = len(c)
    for i in np.argsort(-turn):
        if turn[i] < thresh:
            break
        if all(min(abs(i - j), n - abs(i - j)) > k for j in idx):
            idx.append(int(i))
    return sorted(idx), inner

def vectorize_loop(c, tol=1.0, k=4, thresh=55):
    """Closed loop -> list of cubic segments; anchors at detected corners are sharp (no shared tangent)."""
    c = resample(c, 1.0)
    n = len(c)
    cs, inner = corners(c, k, thresh)
    sharp = list(cs)
    if not cs:  # smooth closed loop: split at 2 far points, tangents shared
        cs = [0, n // 2]
    segs, flags = [], []
    for a, b in zip(cs, cs[1:] + [cs[0] + n]):
        run = c[np.arange(a, b + 1) % n]
        if a in sharp:
            t1 = _unit(run[min(3, len(run) - 1)] - run[0])
        else:
            t1 = _unit(c[(a + 1) % n] - c[(a - 1) % n])
        if (b % n) in sharp:
            t2 = _unit(run[max(-4, -len(run))] - run[-1])
        else:
            t2 = _unit(c[(b - 1) % n] - c[(b + 1) % n])
        fs = fit_cubic(run, t1, t2, tol)
        segs += fs
        flags += [a in sharp] + [False] * (len(fs) - 1)
    return segs, flags, [(int(i), float(inner[i])) for i in sharp], c

def max_error(segs, c):
    """Max/mean distance from loop samples to the fitted path."""
    s = sample_path(segs, 60)
    from scipy.spatial import cKDTree
    d, _ = cKDTree(s).query(c)
    return float(d.max()), float(d.mean())

# ---------- raster + svg ----------
def raster(paths, shape, ss=4):
    """Even-odd fill of closed paths (each a list of segments) -> bool mask. Supersampled ss x."""
    H, W = shape
    acc = np.zeros((H * ss, W * ss), np.uint8)
    for segs in paths:
        if not segs:
            continue
        p = sample_path(segs, 16) * ss
        m = np.zeros_like(acc)
        cv2.fillPoly(m, [np.round(p * 16).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=4)
        acc ^= m
    small = acc.reshape(H, ss, W, ss).mean((1, 3))
    return small >= 0.5

def path_d(segs):
    if not segs:
        return ""
    f = lambda p: f"{p[0]:.1f},{p[1]:.1f}"
    out = [f"M{f(segs[0][0])}"]
    out += [f"C{f(s[1])} {f(s[2])} {f(s[3])}" for s in segs]
    return " ".join(out) + "Z"

def svg_doc(w, h, body, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{b}{body}</svg>'


def raster_union(paths, shape, ss=4):
    """Non-zero union of closed paths -> float coverage (0..1) at frame resolution (supersampled ss x)."""
    H, W = shape
    acc = np.zeros((H * ss, W * ss), np.uint8)
    for segs in paths:
        if segs:
            p = sample_path(segs, 16) * ss
            cv2.fillPoly(acc, [np.round(p * 16).astype(np.int32)], 1, shift=4)
    return acc.reshape(H, ss, W, ss).mean((1, 3))


def raster_evenodd(paths, shape, ss=4):
    """Even-odd fill (holes are separate loops) -> float coverage at frame resolution."""
    H, W = shape
    acc = np.zeros((H * ss, W * ss), np.uint8)
    for segs in paths:
        if segs:
            p = sample_path(segs, 16) * ss
            m = np.zeros_like(acc)
            cv2.fillPoly(m, [np.round(p * 16).astype(np.int32)], 1, shift=4)
            acc ^= m
    return acc.reshape(H, ss, W, ss).mean((1, 3))


def trace(mask, tol=1.0):
    """Vectorise a binary mask: list of closed loops (segment lists), with fit error per loop. Used to MEASURE references."""
    out = []
    for c in contours(mask):
        segs, flags, sharp, cs = vectorize_loop(c, tol)
        emax, emean = max_error(segs, cs)
        out.append(dict(segs=segs, corner_flags=flags, corners=sharp, err_max=emax, err_mean=emean))
    return out


def parse_path_d(d):
    """Inverse of path_d for our own output: 'M x,y C ... Z ...' -> list of loops."""
    import re
    loops = []
    for part in d.split("Z"):
        nums = [tuple(map(float, xy.split(","))) for xy in re.findall(r"-?[\d.]+,-?[\d.]+", part)]
        if len(nums) < 4:
            continue
        p0, segs = np.array(nums[0]), []
        for i in range(1, len(nums) - 2, 3):
            p1, p2, p3 = map(np.array, nums[i:i + 3])
            segs.append((p0, p1, p2, p3))
            p0 = p3
        loops.append(segs)
    return loops
