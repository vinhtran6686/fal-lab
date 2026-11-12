"""fxkit / shapes: the drawn shapes of the house style (lib-fx/_core/formulas/rules/01-design-style.md): few, large, smooth closed
curves with real sharp points, never a union of circles and triangles. Every function returns a polygon [(x, y), ...] in canvas px,
dense enough to be a smooth curve. Angles are screen radians (y down)."""
import math


def _cr(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return tuple(0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (3 * b - a - 3 * c + d) * t3) for a, b, c, d in zip(p0, p1, p2, p3))


def spline(pts, closed=True, k=10, sharp=()):
    """A smooth curve through pts (Catmull-Rom), k samples per span. Indices in `sharp` are real corners (the curve stops and
    starts there with no rounding): that is how a shape gets a pointed tip between two smooth flanks."""
    n = len(pts)
    if n < 3: return list(pts)
    out = []
    spans = range(n) if closed else range(n - 1)
    for i in spans:
        p1, p2 = pts[i], pts[(i + 1) % n]
        p0 = pts[(i - 1) % n] if (closed or i > 0) else p1
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        if i in sharp: p0 = p1                                           # leaving a corner: no pull from before it
        if (i + 1) % n in sharp: p3 = p2                                 # arriving at a corner: no pull from after it
        for j in range(k): out.append(_cr(p0, p1, p2, p3, j / k))
    if not closed: out.append(pts[-1])
    return out


def spine(base, ang, L, lean=0.0, curl=0.0, n=28):
    """Centre line of a tongue: from base along ang for length L; `lean` turns it steadily (radians over the length), `curl` adds
    an S (it bends one way in the lower half and back in the upper half, like a flame). Returns [(x, y, direction)]."""
    x, y = base; out = []
    for i in range(n + 1):
        t = i / n
        a = ang + lean * t + curl * math.sin(2 * math.pi * t) * 0.5
        out.append((x, y, a))
        x += math.cos(a) * L / n; y += math.sin(a) * L / n
    return out


def tongue(base, ang, L, W, lean=0.0, curl=0.0, belly=0.3, sharp=1.6, asym=0.0, foot=0.55, n=28):
    """A flame tongue / blade of energy: fat near its lower third, tapering in a long concave sweep to a real point.
    W = widest width; belly = where along the length it is widest (0..1); sharp > 1 makes the taper concave (a thorn), < 1 convex
    (a leaf); asym (-1..1) puts more of the width on one side; foot = width at the base as a share of W."""
    sp = spine(base, ang, L, lean, curl, n)
    left, right = [], []
    for i, (x, y, a) in enumerate(sp):
        t = i / n
        w = (foot + (1 - foot) * math.sin(math.pi / 2 * t / belly) ** 0.8) if t < belly else (1 - ((t - belly) / (1 - belly))) ** sharp
        w *= W / 2
        nx, ny = -math.sin(a), math.cos(a)
        left.append((x + nx * w * (1 + asym), y + ny * w * (1 + asym))); right.append((x - nx * w * (1 - asym), y - ny * w * (1 - asym)))
    return left + right[::-1]


def along(sp, t):
    """Point and direction at fraction t of a spine."""
    f = max(0.0, min(1.0, t)) * (len(sp) - 1); i = min(len(sp) - 2, int(f)); u = f - i
    return (sp[i][0] + (sp[i + 1][0] - sp[i][0]) * u, sp[i][1] + (sp[i + 1][1] - sp[i][1]) * u), sp[i][2]


def lobed(c, radii, rot=0.0, sy=1.0, sharp=(), k=10):
    """A closed smooth mass around c: control points at even angles with the given radii (a big radius = a lobe, a small one = a
    bay). sharp = indices that are pointed tips. sy squashes it (ground pools)."""
    n = len(radii)
    pts = [(c[0] + r * math.cos(rot + 2 * math.pi * i / n), c[1] + r * sy * math.sin(rot + 2 * math.pi * i / n)) for i, r in enumerate(radii)]
    return spline(pts, True, k, sharp)


def shard(base, ang, L, W, skew=0.0, shoulder=0.3):
    """A crystal spike: straight edges, a wide shoulder near the base, a hard point. Returns (polygon, ridge) where ridge is the
    line base -> tip slightly off-centre: paint one side of it lighter for a facet."""
    ca, sa = math.cos(ang), math.sin(ang); nx, ny = -sa, ca
    tip = (base[0] + ca * L, base[1] + sa * L)
    sx, sy_ = base[0] + ca * L * shoulder, base[1] + sa * L * shoulder
    pl = (sx + nx * W / 2 * (1 + skew), sy_ + ny * W / 2 * (1 + skew)); pr = (sx - nx * W / 2 * (1 - skew), sy_ - ny * W / 2 * (1 - skew))
    bl = (base[0] + nx * W * 0.28, base[1] + ny * W * 0.28); br = (base[0] - nx * W * 0.28, base[1] - ny * W * 0.28)
    mid = (base[0] + nx * W * 0.1 * (1 if skew >= 0 else -1), base[1] + ny * W * 0.1 * (1 if skew >= 0 else -1))
    return [bl, pl, tip, pr, br], [mid, tip]


def scrap(p, ang, L, W, curl=0.6, n=12):
    """A small curved sliver (a comma): what a burning shape breaks into, and what sparks look like in this style."""
    return tongue(p, ang, L, W, lean=curl, belly=0.35, sharp=1.2, foot=0.05, n=n)


def ribbon(pts, widths, bias=0.0):
    """A strip through centre points pts (x, y) with a width per point; bias (-1..1) moves the strip off its centre line
    (bias 0.4 = 70 % of the width on the left of the travel direction)."""
    L, R = [], []
    for k, (x, y) in enumerate(pts):
        p, q = pts[max(0, k - 1)], pts[min(len(pts) - 1, k + 1)]
        dx, dy = q[0] - p[0], q[1] - p[1]; l = math.hypot(dx, dy) or 1.0; nx, ny = -dy / l, dx / l
        w = widths[k]
        L.append((x + nx * w * (0.5 + bias / 2), y + ny * w * (0.5 + bias / 2))); R.append((x - nx * w * (0.5 - bias / 2), y - ny * w * (0.5 - bias / 2)))
    return L + R[::-1]
