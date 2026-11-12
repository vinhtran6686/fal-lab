"""Measure stroke parameters from a mask (least squares on band edges), and decompose a layer into strokes:
body first (robust fit: tongue bases fused to the body are outliers), then tongues ADDED and notches CUT from the
residual, a piece kept only if it raises IoU by `min_gain`. Mirrors how a designer draws: smooth shape, then details."""
import numpy as np
from scipy import ndimage as ndi
from scipy.optimize import least_squares
from .strokes import bern, width_profile, to_path
from .frames import bands, band_area
from .bezier import raster_union


def _bern_fit(t, y, deg, robust=False):
    B = np.stack([bern(np.eye(deg + 1)[k], t) for k in range(deg + 1)], 1)
    w = np.ones_like(y)
    for _ in range(8 if robust else 1):  # IRLS with a Huber weight of 1.5 px
        co = np.linalg.lstsq(B * w[:, None], y * w, rcond=None)[0]
        e = np.abs(B @ co - y)
        w = np.sqrt(np.where(e < 1.5, 1, 1.5 / np.maximum(e, 1e-9)))
    e = B @ co - y
    rms = np.sqrt(np.mean(np.minimum(np.abs(e), 3) ** 2)) if robust else np.sqrt(np.mean(e**2))
    return co, float(rms)


def fit_band(band, frame, tol_spine=0.6, tol_w=0.8, robust=False):
    """One band -> one stroke dict. Spine degree and width 'wobble' terms grow (one per ~25 px) only while needed."""
    pos, lo, hi, step = band["pos"], band["lo"], band["hi"], band["step"]
    p0, p1 = pos[0] - step / 2, pos[-1] + step / 2
    t = (pos - p0) / (p1 - p0)
    w = np.clip(hi - lo, 0, None)
    c = (hi + lo) / 2
    span_px = frame.u_px(p1 - p0, float(np.mean(c))) if band["axis"] == "u" else (p1 - p0)
    for deg in range(2, int(np.clip(span_px / 25, 2, 12)) + 1):
        spine, srms = _bern_fit(t, c, deg, robust)
        if srms < tol_spine:
            break
    W0 = max(w.max(), 0.5)
    blunt0 = w[0] / W0 > 0.35 or band.get("fork0", False)
    blunt1 = w[-1] / W0 > 0.35 or band.get("fork1", False)
    best = None
    for nwob in [0] + list(range(2, int(np.clip(span_px / 25, 0, 12)) + 1)):
        x0 = [W0 * 1.5, 0.6, 0.6, 0.3 if blunt0 else 0.0, 0.3 if blunt1 else 0.0] + [0.0] * nwob
        lb = [0.1, 0.05, 0.05, 0.0, 0.0] + [-0.95] * nwob
        ub = [W0 * 40, 6, 6, 3 if blunt0 else 1e-6, 3 if blunt1 else 1e-6] + [4] * nwob
        x0 = np.clip(x0, lb, np.array(ub) - 1e-9)
        r = least_squares(lambda x: width_profile(t, x[0], x[1], x[2], x[3], x[4], x[5:]) - w, x0, bounds=(lb, ub),
                          loss="soft_l1" if robust else "linear", f_scale=1.5)
        rms = float(np.sqrt(np.mean(np.minimum(np.abs(r.fun), 3) ** 2)))
        best = r.x
        if rms < tol_w:
            break
    x = best
    return dict(axis=band["axis"], pos0=float(p0), pos1=float(p1), spine=[round(float(s), 3) for s in spine],
                W=float(x[0]), a=float(x[1]), b=float(x[2]), e0=float(x[3]), e1=float(x[4]),
                wobble=[round(float(v), 4) for v in x[5:]], span_px=float(span_px), Wmax=float(W0))


def render_strokes(strokes, frame, shape, ss=4):
    """Coverage of add-strokes minus cut-strokes."""
    add = raster_union([to_path(p, frame) for p in strokes if p["op"] == "add"], shape, ss)
    cut = raster_union([to_path(p, frame) for p in strokes if p["op"] == "cut"], shape, ss)
    return np.clip(add - cut, 0, 1)


def _iou(a, b):
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else 1.0


def _fit_all(mask, frame, robust, min_area, op, axes, edge_bias=(0.0, 0.0)):
    out = []
    P = frame.sample(mask)
    for ax in axes:
        for bd in bands(frame, P, ax, edge_bias=edge_bias):
            area = band_area(frame, bd)
            if area < min_area:
                continue
            p = fit_band(bd, frame, robust=robust)
            p["op"], p["area"] = op, area
            out.append(p)
    return out


def fit_layer(mask, frame, passes=4, min_area=6, min_gain=0.0008, axes=("u", "v"), edge_bias=(0.0, 0.0)):
    """mask -> list of strokes (body + tongues + notches).
    Each candidate is scored incrementally: (adds | candidate) & ~cuts, instead of re-rendering the whole layer
    (same result up to anti-aliased edge pixels, and linear instead of quadratic in the number of pieces)."""
    shape = mask.shape
    strokes = _fit_all(mask, frame, True, min_area, "add", ("u",), edge_bias)
    A = render_strokes(strokes, frame, shape) >= 0.5 if strokes else np.zeros(shape, bool)
    C = np.zeros(shape, bool)
    cur = A & ~C
    st = ndi.generate_binary_structure(2, 1)
    for _ in range(passes):
        add = ndi.binary_opening(mask & ~cur, st)
        cut = ndi.binary_opening(cur & ~mask, st)
        new = _fit_all(add, frame, False, min_area, "add", axes, edge_bias) + _fit_all(cut, frame, False, min_area, "cut", axes, edge_bias)
        new.sort(key=lambda p: -p["area"])
        base, took = _iou(cur, mask), False
        for p in new:
            r = raster_union([to_path(p, frame)], shape) >= 0.5
            A2, C2 = (A | r, C) if p["op"] == "add" else (A, C | r)
            trial = A2 & ~C2
            g = _iou(trial, mask)
            if g - base >= min_gain:
                strokes.append(p)
                A, C, cur, base, took = A2, C2, trial, g, True
        if not took:
            break
    return strokes
