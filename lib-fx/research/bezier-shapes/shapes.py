"""Path generators: every swirl shape is a TAPERED POLAR STROKE, written as a closed cubic Bezier path.

    stroke(theta0, theta1, spine, W, a, b, e0, e1, wobble)
      t in [0,1] runs along the sweep (theta0 -> theta1)
      spine  r_c(t) = Bernstein(spine coefficients)              -- where the stroke sits (radius)
      width  w(t)   = W * (t+e0)^a * (1-t+e1)^b * (1 + Bernstein(wobble))
                       a, b : end exponents  (<1 round/blunt, ~1 straight wedge, >1 concave needle)
                       e0,e1: 0 = sharp tip at that end, >0 = blunt (cut) end of that width
      outline: hi = r_c + w/2, lo = r_c - w/2, polar -> screen, fitted with cubic Beziers, tips are corner anchors.

Type presets (the six shapes of the reference) are thin wrappers that fix the exponents and leave few free numbers:
crescent_needle, flame_tongue, feather, white_blade, broken_hook, rim. See FINDINGS.md for measured values."""
import numpy as np
from math import comb
from bezier import fit_cubic, _unit

def bern(coefs, t):
    coefs = np.atleast_1d(coefs)
    n = len(coefs) - 1
    if n < 0:
        return np.zeros_like(t)
    return sum(c * comb(n, k) * t**k * (1 - t) ** (n - k) for k, c in enumerate(coefs))

def width_profile(t, W, a, b, e0=0.0, e1=0.0, wobble=()):
    base = np.clip(t + e0, 0, None) ** a * np.clip(1 - t + e1, 0, None) ** b
    return W * base * np.clip(1 + bern(wobble, t), 0.05, None) if len(wobble) else W * base

def stroke_edges(p, n=None):
    """Polar edges of a stroke parameter dict -> (theta, lo, hi) samples."""
    span = abs(p["theta1"] - p["theta0"])
    rmean = float(np.mean(p["spine"])) if p.get("axis", "theta") == "theta" else 1.0
    n = n or int(np.clip(span * rmean / 1.5, 12, 600))
    t = np.linspace(0, 1, n)
    th = p["theta0"] + (p["theta1"] - p["theta0"]) * t
    rc = bern(p["spine"], t)
    w = width_profile(t, p["W"], p["a"], p["b"], p.get("e0", 0), p.get("e1", 0), p.get("wobble", ()))
    return th, rc - w / 2, rc + w / 2

def stroke_path(p, centre, tol=0.6):
    """Closed cubic Bezier path (list of segments) for a stroke. Sharp corners at tips / blunt-end corners."""
    th, lo, hi = stroke_edges(p)
    cx, cy = centre
    P = lambda r, a: np.c_[cx + r * np.cos(a), cy + r * np.sin(a)]
    if p.get("axis", "theta") == "theta":
        up, dn = P(hi, th), P(lo, th)[::-1]
    else:  # position = radius, edges = arc length at RS
        from polar import RS
        up, dn = P(th, hi / RS), P(th, lo / RS)[::-1]
    sharp0 = p.get("e0", 0) <= 1e-3
    sharp1 = p.get("e1", 0) <= 1e-3
    runs = [up, dn]
    segs = []
    for run in runs:
        if len(run) < 2 or np.linalg.norm(run[-1] - run[0]) < 0.3:
            continue
        t1 = _unit(run[min(2, len(run) - 1)] - run[0])
        t2 = _unit(run[max(-3, -len(run))] - run[-1])
        segs += fit_cubic(run, t1, t2, tol)
        nxt = dn[0] if run is up else up[0]
        if np.linalg.norm(run[-1] - nxt) > 0.3:  # blunt end: straight edge (cubic with 1/3 handles)
            d = nxt - run[-1]
            segs.append((run[-1], run[-1] + d / 3, run[-1] + 2 * d / 3, nxt))
    return segs

# ---------------- type presets ----------------
def crescent_needle(theta0, theta1, r0, r1, bulge, W, peak=0.35, needle=1.6, head=0.6):
    """Main crescent: spiral spine r0->r1 with outward bulge, round head (exponent <1) and needle tail (>1)."""
    a, b = head, needle * (1 - peak) / peak * head  # peak = a/(a+b)
    return dict(theta0=theta0, theta1=theta1, spine=[r0, r0 + bulge, r1 + bulge, r1], W=W, a=a, b=b)

def flame_tongue(theta_base, length, r_base, lean, W, curl=0.0, sharp=1.2):
    """Tongue grown from a parent edge against the sweep: blunt base (e0>0), straight/concave tip."""
    return dict(theta0=theta_base - length, theta1=theta_base, spine=[r_base + lean, r_base + lean * curl, r_base, r_base],
                W=W, a=sharp, b=0.0, e0=0.0, e1=0.0)

def feather(theta0, theta1, r0, r1, W, belly=0.45, fat=0.7):
    """Feather / leaf: both ends sharp, belly position = a/(a+b), fat<1 = convex sides."""
    a = fat * 2 * belly
    return dict(theta0=theta0, theta1=theta1, spine=[r0, r1], W=W, a=a, b=fat * 2 * (1 - belly))

def rim(parent, side="hi", width=3.0):
    """Thin outline along one edge of a parent stroke (same spine, offset by half the parent width)."""
    q = dict(parent)
    q["W"], q["wobble"] = width, ()
    return q
