"""fxkit / layers / slash: a sword slash smear swept from a to b (rules/vfx/slash). A crescent ribbon along the path a -> b: a needle
tail, the belly near three quarters, a pointed head; a darker tone hugging the inner edge, a hot edge on the outer edge, dry-brush
teeth bitten out of the inner edge and a few hair-thin streaks beside it. It is born at a, grows towards b in one fast sweep, then is
eaten in place and from behind (the tail retreats, thin parts and the hot edge go first, slivers and specks are what is left)."""
import math
from .. import kind, angles, smooth, out_quint, out_cubic, clamp, Ink, erode, drop_specks, shapes
from .flames import decay_share, on_twos

N = 48


@kind("slash")
def slash(c, ph, bend=0.34, width=54.0, tones=3, teeth=4, streaks=3, linger=3.4):
    """A sword slash from a to b. role primary. Designed for Life(0, 0.1, 0.03, 0.27): the attack is the sweep.
    bend: how far the path bows to the upper side, share of a-b distance (0 = straight thrust, negative = bows down); width: the
    widest part of the ribbon, px (54 = a sword, 80 = a heavy weapon); tones: 3 = main + darker inside + hot edge, 2 = no hot edge,
    1 = flat; teeth: notches bitten out of the inner edge (0 = clean); streaks: hair-thin strokes beside the ribbon (0 = none);
    linger: how fast it is eaten (3.4 = short, 2.5 = lingers). The belly hangs on the inside of the bow."""
    rng = c.rng("design"); s = c.s
    g = ph.grow
    d = on_twos(ph, c)
    fh = min(1.0, 0.45 + 0.5 * out_quint(g) + 0.05 * out_cubic(min(1.0, ph.decay * 3)))      # the head: born 45 % out, runs on
    ft = 0.55 * d                                                                           # the tail retreats while it is eaten
    sg = c.sp.hand * (1 if bend >= 0 else -1)                                                # +1: the inside of the bow is the left of travel
    W = width * s
    ink = Ink(c)

    def prof(v):                                                                           # width along the ribbon, v 0 tail .. 1 head
        v = clamp(v)
        return v ** 0.75 * (1 - v ** 5) ** 0.6

    def at(f):
        p, a = c.sp.path(clamp(f), bend)
        return p, (-math.sin(a) * sg, math.cos(a) * sg)                                    # point, unit vector to the inside of the bow

    def strip(f0, f1, wf, bias, n=N):
        pts, ws = [], []
        for i in range(n):
            u = i / (n - 1); f = f0 + (f1 - f0) * u
            pts.append(at(f)[0]); ws.append(wf(f, u))
        return shapes.ribbon(pts, ws, bias * sg)

    def wmain(f, u=0.0):
        w = W * prof(f / fh)
        if ft > 0.01: w *= min(1.0, max(0.0, (f - ft) / 0.16)) ** 0.8                         # a tapered end where the tail is eaten
        return w

    if fh - ft < 0.06: return
    # the main ribbon: 30 % of the width on the outer edge, 70 % inside
    ink.add("main", strip(ft, fh, wmain, 0.4))
    if tones >= 2:                                                                          # darker tone along the inner edge, towards the tail
        da, db = max(0.15 * fh, ft), 0.9 * fh
        if db - da > 0.05:
            ink.add("deep", strip(da, db, lambda f, u: 0.38 * wmain(f) * math.sin(math.pi * u) ** 0.6, 2.47))
    if tones >= 3:                                                                          # the hot leading edge, outer side, ending in the point
        ha = max(0.35 * fh, ft)
        if fh - ha > 0.05:
            ink.add("hot", strip(ha, fh, lambda f, u: 0.2 * wmain(f) * smooth(0, 0.3, u), -2.0))
    # teeth: slim wedges bitten out of the inner edge, pointing back to the tail
    for i, v in enumerate(angles(rng, teeth, 0.2, 0.88, gaps=1) if teeth > 0 else []):
        r = c.rng("tooth", i)
        if v > fh * 0.95 or v < ft: continue
        vl = v / fh; w = wmain(v)
        L = r.uniform(0.06, 0.16); dep = r.uniform(0.3, 0.65)
        (p0, n0), (p1, n1), (pt, nt) = at(v), at(v + L * 0.35), at(v - L * 0.65)
        edge = lambda p, n_, k: (p[0] + n_[0] * w * k, p[1] + n_[1] * w * k)
        poly = shapes.spline([edge(p0, n0, 0.95), edge(p0, n0, 0.7 - dep * 0.35), edge(pt, nt, 0.7 - dep), edge(p1, n1, 0.7 - dep * 0.2),
                              edge(p1, n1, 0.95)], True, 8, sharp=(2,))
        ink.cut("main", poly); ink.cut("deep", poly)
    # streaks: hair-thin ribbons beside the main ribbon, lagging behind the head
    for i in range(streaks):
        r = c.rng("streak", i)
        side = 1 if i % 2 == 0 else -1; off = r.uniform(0.75, 1.4) * W * 0.5 * side
        f0 = r.uniform(0.04, 0.4); f1 = min(f0 + r.uniform(0.35, 0.7), 0.88) ; f1 = min(f1, fh - r.uniform(0.04, 0.12))
        f0 = max(f0, ft)
        if f1 - f0 < 0.12: continue
        wd = r.uniform(3, 6) * s
        pts, ws = [], []
        for k in range(24):
            u = k / 23; f = f0 + (f1 - f0) * u; p, n_ = at(f)
            o = off * (0.35 + 0.65 * prof(f / fh) ** 0.5)
            pts.append((p[0] + n_[0] * o, p[1] + n_[1] * o)); ws.append(wd * math.sin(math.pi * u) ** 0.7)
        ink.add("main", shapes.ribbon(pts, ws))
    # eaten in place
    if d > 0:
        keep = decay_share(d, linger); seed = rng.randrange(1 << 16)
        body0 = ink.mask("main")
        cur = float(body0.sum()); peak = sum(W * prof(0.04 + 0.92 * i / 40) for i in range(41)) / 41 * 0.92 * c.sp.len * 0.7
        ke = min(1.0, keep * peak / max(cur / (ink.ss ** 2), 1.0)) if cur else keep
        body = erode(body0, ke, seed, ink.ss, holes=0.38, grain=width * 0.13 * s, stretch=1.0, hollow=True)   # eaten from the inside out: thin slivers stay along both edges
        body = drop_specks(body, ink.ss, 4 * s * s)
        ink.set("main", body)
        if tones >= 2: ink.set("deep", erode(ink.mask("deep"), ke ** 2.5, seed + 1, ink.ss, holes=0.4, grain=width * 0.2 * s) & body)
        if tones >= 3: ink.set("hot", drop_specks(erode(ink.mask("hot"), ke ** 1.2, seed + 2, ink.ss, holes=0.4, grain=width * 0.16 * s) & body, ink.ss, 3 * s * s))
    if ph.first:
        ink.paint([("main", c.pal.tone("hot")), ("hot", c.pal.tone("white"))], glow=1.0)
    else:
        ink.paint([("main", c.pal.tone("main")), ("deep", c.pal.tone("deep")), ("hot", c.pal.tone("hot"))], glow=1.0)
