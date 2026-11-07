"""Measure the generator's parameters for every band of a mask (least squares on the band edges).

Complexity grows only as needed: spine Bernstein degree and width 'wobble' terms are raised until the edge error is
under ~0.7 px, so a short tongue keeps 4 spine numbers and a plain beta profile, a 200-degree crescent gets more."""
import numpy as np
from scipy.optimize import least_squares
from shapes import bern, width_profile
from polar import NT

DTH = 2 * np.pi / NT

def _bern_fit(t, y, deg, robust=False):
    B = np.stack([bern(np.eye(deg + 1)[k], t) for k in range(deg + 1)], 1)
    wts = np.ones_like(y)
    for _ in range(8 if robust else 1):  # IRLS, Huber 1.5 px: tongue bases fused into the body count as outliers
        co = np.linalg.lstsq(B * wts[:, None], y * wts, rcond=None)[0]
        e = np.abs(B @ co - y)
        wts = np.sqrt(np.where(e < 1.5, 1, 1.5 / np.maximum(e, 1e-9)))
    e = B @ co - y
    return co, float(np.sqrt(np.mean(np.minimum(np.abs(e), 3) ** 2)) if robust else np.sqrt(np.mean(e**2)))

def fit_band(band, seam, tol_spine=0.6, tol_w=0.8, robust=False, axis="theta"):
    from polar import DR, RS
    if axis == "theta":
        j, lo, hi = band["j"], band["lo"], band["hi"] + 0.5  # run end is exclusive (radius bins of 0.5 px)
        th = seam + (j + 0.5) * DTH
        step = DTH
    else:  # along the radius: position = r (px), lo/hi = arc length at RS (px)
        j, lo, hi = band["j"], band["lo"], band["hi"] + DTH * RS
        th = (j + 0.5) * DR
        step = DR
    th0, th1 = th[0] - step / 2, th[-1] + step / 2
    t = (th - th0) / (th1 - th0)
    w = np.clip(hi - lo, 0, None)
    c = (hi + lo) / 2
    span_px = (th1 - th0) * float(np.mean(c)) if axis == "theta" else (th1 - th0)
    max_deg = int(np.clip(span_px / 25, 2, 12))
    for deg in range(2, max_deg + 1):
        spine, srms = _bern_fit(t, c, deg, robust)
        if srms < tol_spine:
            break
    W0 = max(w.max(), 0.5)
    blunt0 = w[0] / W0 > 0.35 or band.get("fork0", False)
    blunt1 = w[-1] / W0 > 0.35 or band.get("fork1", False)

    best = None
    max_wob = int(np.clip(span_px / 25, 0, 12))
    for nwob in [0] + list(range(2, max_wob + 1)):
        def resid(x):
            return width_profile(t, x[0], x[1], x[2], x[3], x[4], x[5:]) - w
        x0 = [W0 * 1.5, 0.6, 0.6, 0.3 if blunt0 else 0.0, 0.3 if blunt1 else 0.0] + [0.0] * nwob
        lb = [0.1, 0.05, 0.05, 0.0, 0.0] + [-0.95] * nwob
        ub = [W0 * 40, 6, 6, 3 if blunt0 else 1e-6, 3 if blunt1 else 1e-6] + [4] * nwob
        x0 = np.clip(x0, lb, np.array(ub) - 1e-9)
        r = least_squares(resid, x0, bounds=(lb, ub), loss="soft_l1" if robust else "linear", f_scale=1.5)
        rms = float(np.sqrt(np.mean(np.minimum(np.abs(r.fun), 3) ** 2))) if robust else float(np.sqrt(np.mean(r.fun**2)))
        best = (r.x, rms, nwob)
        if rms < tol_w:
            break
    x, rms, nwob = best
    return dict(theta0=float(th0), theta1=float(th1), spine=[round(float(s), 2) for s in spine],
                W=float(x[0]), a=float(x[1]), b=float(x[2]), e0=float(x[3]), e1=float(x[4]),
                wobble=[round(float(v), 3) for v in x[5:]], rms_w=rms, rms_spine=srms,
                npar=2 + len(spine) + 5 + nwob, span_px=span_px, Wmax=float(W0), axis=axis)
