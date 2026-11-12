"""fxkit / layers / burst: the body of a hit. `star` (a few long curved points out of a small centre), `streaks` (speed lines),
`ring` (a shock ring). Each one is designed at its peak with a seeded rng, grows, then is eaten in place (rules/05)."""
import math
from .. import kind, sizes, angles, smooth, out_back, out_quint, clamp, Ink, erode, drop_specks, shapes
from .flames import decay_share, on_twos


def _dirs(rng, c, n, arc, gaps=1):
    """n screen angles (radians) inside arc (degrees, axis frame): centre direction converted once, offsets mirrored by hand."""
    a0, a1 = arc
    degs = angles(rng, n, a0, a1, jitter=0.7, gaps=gaps)
    if a1 - a0 >= 300: degs = [d + rng.uniform(0, 360) for d in degs]
    ax = c.sp.ang(0)
    return [ax + math.radians(d) * c.sp.hand for d in degs]


def _blob(rng, centre, r, k=8):
    return shapes.lobed(centre, [r * rng.uniform(0.6, 1.2) for _ in range(k)], rot=rng.uniform(0, 6.28))


@kind("star")
def star(c, ph, n=5, length=120.0, width=44.0, arc=(-180, 180), minor=4, linger=3.0):
    """The body of a hit: a few long, slim, slightly curved points of very different lengths out of a small centre. role primary.
    Designed for Life(0, 0.066, 0.033, 0.3).
    n: main points; length: the longest, px; width: base width of the longest, px; arc: degrees in the axis frame for the point
    directions (a cone such as (-70, 70) throws them along a -> b); minor: short thin points in the gaps; linger: decay speed.
    Tones: main, hot (a smaller copy of the star: the hot heart). In the decay the centre opens and the points part into needles."""
    rng = c.rng("design"); s = c.s; x0, y0 = c.o
    n = int(n)
    dirs = _dirs(rng, c, n, arc)
    szs = sizes(rng, n, heroes=1, mid=0.74, small=0.5)
    grow = (0.55 + 0.45 * out_back(ph.grow)) * (1 + 0.08 * ph.age)
    ink = Ink(c)
    for i, (a, sz) in enumerate(zip(dirs, szs)):
        r = c.rng("point", i)
        L = length * sz * s * grow
        W = width * s * (0.45 + 0.55 * sz)
        lean, curl = r.uniform(-0.3, 0.3), r.uniform(0.2, 0.45) * r.sign()
        belly, sharp = r.uniform(0.12, 0.2), r.uniform(1.7, 2.4)
        ink.add("deep", shapes.tongue(c.o, a, L, W, lean, curl, belly=belly, sharp=sharp, foot=0.9))
        ink.add("main", shapes.tongue(c.o, a, L * r.uniform(0.66, 0.76), W * 0.62, lean, curl, belly=belly, sharp=sharp, foot=0.9))
        ink.add("hot", shapes.tongue(c.o, a, L * r.uniform(0.36, 0.46), W * 0.34, lean, curl, belly=belly, sharp=sharp, foot=0.9))
    for i, a in enumerate(_dirs(c.rng("minor"), c, int(minor), arc, gaps=0)):
        r = c.rng("minor", i)
        ink.add("deep", shapes.tongue(c.o, a, length * r.uniform(0.22, 0.42) * s * grow, width * r.uniform(0.3, 0.45) * s,
                                      r.uniform(-0.3, 0.3), r.uniform(-0.3, 0.3), belly=0.15, sharp=2.0, foot=0.8))
    rc = c.rng("centre")
    ink.add("deep", _blob(rc, c.o, length * rc.uniform(0.17, 0.22) * s * grow, rc.choice((7, 8, 9))))
    ink.add("main", _blob(rc, c.o, length * 0.13 * s * grow, 8))
    ink.add("hot", _blob(rc, c.o, length * 0.085 * s * grow, 8))
    d = on_twos(ph, c)
    if d > 0:
        keep = decay_share(d, linger); seed = rng.randrange(1 << 16)
        hole = _blob(c.rng("hole"), c.o, length * 0.3 * s * max(0.0, d - 0.25) / 0.75, 9) if d > 0.3 else []
        for tn in ("deep", "main", "hot"): ink.cut(tn, hole)
        body = erode(ink.mask("deep"), keep, seed, ink.ss, holes=0.3, grain=length * 0.07 * s, stretch=1.0)
        body = drop_specks(body, ink.ss, 5 * s * s)
        ink.set("deep", body)
        ink.set("main", erode(ink.mask("main"), keep ** 1.5, seed + 2, ink.ss, holes=0.3, grain=length * 0.06 * s) & body)
        hot = erode(ink.mask("hot"), keep ** 2.2, seed + 1, ink.ss, holes=0.3, grain=length * 0.05 * s) & body
        ink.set("hot", drop_specks(hot, ink.ss, 4 * s * s))
    glow = 1 - smooth(0.5, 0.85, ph.age)
    if ph.first: ink.paint([("deep", c.pal.tone("hot")), ("main", c.pal.tone("white")), ("hot", c.pal.tone("white"))], glow=glow)
    else: ink.paint([("deep", c.pal.tone("deep")), ("main", c.pal.tone("main")), ("hot", c.pal.tone("hot"))], glow=glow)


@kind("streaks")
def streaks(c, ph, n=4, arc=(-180, 180), length=130.0, width=5.0, r0=34.0, speed=420.0):
    """Speed lines around a hit: hair-thin slivers flying outward from distance r0. role secondary / accent.
    Designed for Life(0, 0.033, 0.033, 0.13).
    n: slivers; arc: directions in degrees (axis frame); length: the longest, px; width: of the longest, px; r0: start distance, px;
    speed: outward travel, px/s. They end by shortening from the tail and thinning. Tones: main, hot (the longest one)."""
    rng = c.rng("design"); s = c.s; x0, y0 = c.o
    n = int(n)
    dirs = _dirs(rng, c, n, arc)
    szs = sizes(rng, n, heroes=1, mid=0.7, small=0.4)
    hero = max(range(n), key=lambda i: szs[i]) if n else 0
    ink = Ink(c)
    d = ph.decay
    for i, (a, sz) in enumerate(zip(dirs, szs)):
        r = c.rng("line", i)
        v = speed * r.uniform(0.7, 1.15) * (0.6 + 0.4 * sz)
        head = (r0 * r.uniform(0.8, 1.3) + v * ph.sec) * s
        L = length * sz * s * (0.35 + 0.65 * out_quint(ph.grow)) * (1 - d) ** 0.9
        L = min(L, head)
        W = width * s * (0.55 + 0.45 * sz) * (1 - 0.6 * d)
        if L < 4 * s or W < 0.8 * s: continue
        p = (x0 + math.cos(a) * (head - L), y0 + math.sin(a) * (head - L))
        poly = shapes.tongue(p, a, L, W, r.uniform(-0.1, 0.1), r.uniform(0, 0.15) * r.sign(), belly=0.5, sharp=1.2, foot=0.05, n=16)
        ink.add("hot" if i == hero else "main", poly)
    if ph.first: ink.paint([("main", c.pal.tone("hot")), ("hot", c.pal.tone("white"))], glow=0.8)
    else: ink.paint([("main", c.pal.tone("main")), ("hot", c.pal.tone("hot"))], glow=0.8)


def _band(cx, cy, r, w_of, squash, k=96, outer_only=None):
    """One closed polygon: outer ellipse points, then inner ellipse points reversed. w_of(theta) = band width there.
    outer_only = share of the width (from the outer edge) to keep: the hot band."""
    out, inn = [], []
    for i in range(k):
        t = 2 * math.pi * i / k
        w = w_of(t); ro = r + w / 2; ri = max(0.0, ro - (w if outer_only is None else w * outer_only))
        out.append((cx + ro * math.cos(t), cy + ro * squash * math.sin(t)))
        inn.append((cx + ri * math.cos(t), cy + ri * squash * math.sin(t)))
    return out + [out[0]] + [inn[0]] + inn[::-1]


@kind("ring")
def ring(c, ph, r=(26.0, 120.0), width=13.0, squash=1.0, gaps=3, linger=3.4):
    """A shock ring expanding from the anchor. role secondary. Designed for Life(0.033, 0.1, 0, 0.23).
    r: (start, end) radius, px; width: band width, px; squash: y/x (0.3 = lying on the ground, axes level with the screen);
    gaps: how many arcs it breaks into (3 = 3-5); linger: decay speed. Tones: main band with a thin hot band on its outer edge.
    Eaten in place into arcs of different lengths, the band thinning; it never ends as a hairline hoop."""
    rng = c.rng("design"); s = c.s; x0, y0 = c.o
    th0 = rng.uniform(0, 6.28)
    rr = (r[0] + (r[1] - r[0]) * out_quint(ph.age)) * s
    d = on_twos(ph, c)
    w = width * s * (0.6 + 0.4 * ph.grow) * (1 - 0.45 * d)
    if w < 2 * s: return
    near = 0.4 * (1 - squash)

    def w_of(t): return w * (1 + 0.35 * math.cos(t - th0)) * (1 + near * math.sin(t))
    ink = Ink(c)
    ink.add("main", _band(x0, y0, rr, w_of, squash))
    ink.add("hot", _band(x0, y0, rr, w_of, squash, outer_only=0.25))
    if d > 0:
        keep = decay_share(d, linger); seed = rng.randrange(1 << 16)
        body = erode(ink.mask("main"), keep, seed, ink.ss, holes=0.75, grain=r[1] * 0.2 * s * 3.0 / max(1, gaps))
        body = drop_specks(body, ink.ss, 6 * s * s)
        ink.set("main", body)
        ink.set("hot", drop_specks(ink.mask("hot") & body, ink.ss, 4 * s * s))
    glow = 0.7 * (1 - smooth(0.5, 0.9, ph.age))
    if ph.first: ink.paint([("main", c.pal.tone("hot")), ("hot", c.pal.tone("white"))], glow=glow)
    else: ink.paint([("main", c.pal.tone("main")), ("hot", c.pal.tone("hot"))], glow=glow)
