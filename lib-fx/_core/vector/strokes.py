"""The shape unit: a TAPERED STROKE in the effect's own frame, written out as a closed cubic Bezier path.

    t in [0,1] runs along the stroke's axis:  pos = pos0 + (pos1 - pos0) * t
    spine   c(t) = Bernstein(spine coefficients)                    where the stroke sits across the axis
    width   w(t) = W * (t+e0)^a * (1-t+e1)^b * (1 + Bernstein(wobble))
              a, b  : end exponents  (< 1 round / blunt, ~1 straight wedge, > 1 concave needle)
              e0,e1 : 0 = sharp tip at that end, > 0 = blunt end (a stroke drawn into another shape)
    edges   c +- w/2

axis 'u' strokes follow the motion (crescent, flame tongue, feather, rim); axis 'v' strokes point across it (hooks,
tips aimed at / away from a swirl centre). One unit, every shape: the measured parameter ranges per shape type are in
lib-fx/research/bezier-shapes/FINDINGS.md section 4.

A stroke is a plain dict: {axis, pos0, pos1, spine[], W, a, b, e0, e1, wobble[], op: 'add'|'cut'}."""
import numpy as np
from math import comb
from .bezier import fit_cubic, _unit


def bern(coefs, t):
    coefs = np.atleast_1d(np.asarray(coefs, float))
    n = len(coefs) - 1
    t = np.asarray(t, float)
    if n < 0:
        return np.zeros_like(t)
    return sum(c * comb(n, k) * t**k * (1 - t) ** (n - k) for k, c in enumerate(coefs))


def width_profile(t, W, a, b, e0=0.0, e1=0.0, wobble=()):
    base = np.clip(t + e0, 0, None) ** a * np.clip(1 - t + e1, 0, None) ** b
    return W * base * np.clip(1 + bern(wobble, t), 0.05, None) if len(wobble) else W * base


def peak_scale(W_peak, a, b, e0=0.0, e1=0.0):
    """Turn a wanted PEAK width into the formula's W (useful when designing strokes by hand)."""
    t = np.linspace(0, 1, 401)
    return W_peak / max(width_profile(t, 1.0, a, b, e0, e1).max(), 1e-9)


def edges(p, frame, n=None):
    """(pos, lo, hi) samples of a stroke."""
    span = abs(p["pos1"] - p["pos0"])
    across = float(np.mean(p["spine"]))
    span_px = frame.u_px(span, across) if p["axis"] == "u" else span
    n = n or int(np.clip(span_px / 1.5, 12, 600))
    t = np.linspace(0, 1, n)
    pos = p["pos0"] + (p["pos1"] - p["pos0"]) * t
    c = bern(p["spine"], t)
    w = width_profile(t, p["W"], p["a"], p["b"], p.get("e0", 0), p.get("e1", 0), p.get("wobble", ()))
    return pos, c - w / 2, c + w / 2


def to_path(p, frame, tol=0.6):
    """Closed cubic Bezier path (list of segments). Tips are corner anchors; blunt ends are straight edges."""
    pos, lo, hi = edges(p, frame)
    if p["axis"] == "u":
        xy = lambda q: np.c_[frame.to_xy(pos, q)]
    else:
        s = frame.u_scale()
        xy = lambda q: np.c_[frame.to_xy(q / s, pos)]
    up, dn = xy(hi), xy(lo)[::-1]
    segs = []
    for run, nxt in ((up, dn[0]), (dn, up[0])):
        if len(run) < 2 or np.linalg.norm(run[-1] - run[0]) < 0.3:
            continue
        t1 = _unit(run[min(2, len(run) - 1)] - run[0])
        t2 = _unit(run[max(-3, -len(run))] - run[-1])
        segs += fit_cubic(run, t1, t2, tol)
        if np.linalg.norm(run[-1] - nxt) > 0.3:
            d = nxt - run[-1]
            segs.append((run[-1], run[-1] + d / 3, run[-1] + 2 * d / 3, nxt))
    return segs


# ---- design presets (hand authoring; defaults are the medians measured on the swirl-slash reference) -------------
def crescent(pos0, pos1, c0, c1, W_peak, bulge=0.0, tail=1.3, head=0.4, axis="u"):
    """Main crescent: tail exponent > 1 gives the needle, head < 1 the round front."""
    p = dict(axis=axis, pos0=pos0, pos1=pos1, spine=[c0, c0 + bulge, c1 + bulge, c1], a=tail, b=head, e0=0.0, e1=0.0, op="add")
    p["W"] = peak_scale(W_peak, tail, head)
    return p


def tongue(pos_base, length, c_base, lean, W_peak, sharp=0.6, back=True, axis="u"):
    """Flame tongue grown out of a parent: blunt base buried in the parent, tip `length` away, leaning `lean` across.
    Measured: length / width ~ 2.4, convex sides (sharp ~0.6); tips point against the sweep about half the time."""
    s = -1 if back else 1
    pos0, pos1 = sorted((pos_base, pos_base + s * length))
    sp = [c_base + lean, c_base + lean * 0.5, c_base, c_base] if back else [c_base, c_base, c_base + lean * 0.5, c_base + lean]
    a, b, e0, e1 = (sharp, 0.4, 0.0, 0.1) if back else (0.4, sharp, 0.1, 0.0)
    p = dict(axis=axis, pos0=pos0, pos1=pos1, spine=sp, a=a, b=b, e0=e0, e1=e1, op="add")
    p["W"] = peak_scale(W_peak, a, b, e0, e1)
    return p


def feather(pos0, pos1, c0, c1, W_peak, belly=0.45, fat=0.55, axis="u"):
    """Feather / leaf: both ends sharp; belly = where it is widest; fat < 1 convex sides (measured a~0.53, b~0.62)."""
    a, b = fat * 2 * belly, fat * 2 * (1 - belly)
    return dict(axis=axis, pos0=pos0, pos1=pos1, spine=[c0, c1], W=peak_scale(W_peak, a, b), a=a, b=b, e0=0.0, e1=0.0, op="add")


def notch(pos0, pos1, c, W_peak, axis="u"):
    """Bite cut out of a layer (measured: ~6 px wide, 4x as long, round ends)."""
    return dict(axis=axis, pos0=pos0, pos1=pos1, spine=[c, c], W=peak_scale(W_peak, 0.4, 0.42), a=0.4, b=0.42, e0=0.0, e1=0.0, op="cut")
