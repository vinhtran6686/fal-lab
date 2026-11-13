"""fxkit / layers / crystals: a cluster of crystal spikes erupting from a root (the purple / blue effect of ref_trio2): a few hard
straight-edged spikes (one hero near the middle), a lit facet on each, a see-through veil of wide curved wings behind them and small
shards floating at the tips. It snaps out (wide first, tall after), then the veil is eaten from the inside out and the spikes from
the edge."""
import math
from .. import kind, sizes, angles, smooth, out_cubic, out_back, Ink, erode, drop_specks, shapes
from .flames import decay_share, on_twos


def _facet(poly, ridge):
    """The half of a shard on the lit side (towards the upper left of the screen) of its ridge line."""
    bl, pl, tip, pr, br = poly; mid = ridge[0]
    a, b = [mid, bl, pl, tip], [mid, tip, pr, br]
    sc = lambda h: sum(x + y for x, y in h) / len(h)
    return a if sc(a) <= sc(b) else b


@kind("crystals")
def crystals(c, ph, n=5, height=170.0, width=120.0, fan=95.0, dir=90.0, veil=True, linger=3.9):
    """Crystal spikes erupting from the layer's anchor. role primary. Designed for Life(0, 0.1, 0.066, 0.4).
    n: spikes; height: of the hero spike, px; width: of the foot, px; fan: spread of the spike directions, degrees; dir: where it
    erupts, degrees in the axis frame (90 = the upper side, 0 = thrown along a -> b); veil: wide see-through wings behind the
    spikes; linger: how slowly it is eaten (3.9 = short burst)."""
    rng = c.rng("design"); s = c.s
    g = ph.grow
    gy = 0.3 + 0.7 * out_cubic(g)
    gx = 0.5 + 0.5 * out_back(min(1.0, g * 1.6), 2.4)
    tilt = rng.uniform(-10, 10)
    ax = c.sp.ang(dir); nx, ny = -math.sin(ax), math.cos(ax)
    x0, y0 = c.o
    szs = sorted(sizes(rng, n, heroes=1, mid=0.72, small=0.4, jitter=0.12), reverse=True)
    degs = sorted(angles(rng, n, -fan / 2, fan / 2, jitter=0.6))
    centre = sorted(range(n), key=lambda i: abs(degs[i] + rng.uniform(-fan * 0.08, fan * 0.08)))
    hero = centre[rng.randrange(min(2, n))]
    rest = [i for i in range(n) if i != hero]; others = szs[1:]; rng.shuffle(others)
    size_of = {hero: szs[0], **dict(zip(rest, others))}
    ink = Ink(c)
    time = ph.sec
    spikes = []
    if veil:                                                                # the see-through wings, painted first
        for i, side in enumerate((-1, 1, rng.choice((-1, 1)))[:2 + (n >= 4)]):
            r = c.rng("wing", i)
            L = height * r.uniform(0.55, 0.75) * (1 if i < 2 else 0.6) * gy * s
            off = side * width * r.uniform(0.25, 0.4) * gx * s
            a = ax + side * math.radians(r.uniform(22, 42) + tilt * 0.3 * side)
            ink.add("veil", shapes.tongue((x0 + nx * off, y0 + ny * off), a, L, L * r.uniform(0.42, 0.55), -side * r.uniform(0.3, 0.6),
                                          r.uniform(0.5, 0.9) * r.sign(), belly=0.38, sharp=1.5, foot=0.12))
    for i, deg in enumerate(degs):
        r = c.rng("spike", i); sz = size_of[i]
        off = deg / max(1.0, fan / 2) * width * 0.42 * gx * s
        base = (x0 + nx * off, y0 + ny * off)
        L = height * sz * gy * s * (1 + 0.06 * ph.age)
        W = L * r.uniform(0.2, 0.3) * (gx / max(0.5, gy)) ** 0.5
        a = ax + math.radians(deg * 0.7 + tilt + r.uniform(-4, 4))
        poly, ridge = shapes.shard(base, a, L, W, skew=r.uniform(-0.25, 0.25), shoulder=r.uniform(0.25, 0.4))
        ink.add("main", poly); ink.add("hot", _facet(poly, ridge))
        spikes.append((base, a, L))
    for i in range(3 + (rng.random() < 0.6) + (n >= 6)):                      # small detached shards around the tips
        r = c.rng("float", i); base, a, L = spikes[(i * 2 + rng.randrange(n)) % n]
        dist = L * r.uniform(0.04, 0.16) + r.uniform(6, 22) * s + 8 * s * time
        side = r.sign() * r.uniform(0.2, 0.9) * L * 0.18
        p = (base[0] + math.cos(a) * (L + dist) - math.sin(a) * side, base[1] + math.sin(a) * (L + dist) + math.cos(a) * side)
        sl = height * r.uniform(0.1, 0.25) * gy * s
        poly, ridge = shapes.shard(p, a + math.radians(r.uniform(-45, 45)), sl, sl * r.uniform(0.25, 0.35), r.uniform(-0.3, 0.3))
        ink.add("main", poly)
    d = on_twos(ph, c)
    if d > 0:
        keep = decay_share(d, linger); seed = rng.randrange(1 << 16)
        if veil:
            ink.set("veil", drop_specks(erode(ink.mask("veil"), keep ** 1.3, seed + 3, ink.ss, holes=0.35, grain=height * 0.06 * s, hollow=True), ink.ss, 6 * s * s))
        body = drop_specks(erode(ink.mask("main"), keep, seed, ink.ss, holes=0.2, grain=height * 0.05 * s, stretch=1.6), ink.ss, 6 * s * s)
        ink.set("main", body)
        ink.set("hot", erode(ink.mask("hot"), keep ** 1.8, seed + 1, ink.ss, holes=0.3, grain=height * 0.05 * s) & body)
    glow = 1 - smooth(0.5, 0.85, ph.age)
    deep = c.pal.tone("deep")
    if ph.first:
        ink.paint([("veil", deep), ("main", c.pal.tone("hot")), ("hot", c.pal.tone("white"))], opacity={"veil": 0.45}, glow=1.0)
    else:
        ink.paint([("veil", deep), ("main", c.pal.tone("main")), ("hot", c.pal.tone("hot"))], opacity={"veil": 0.45}, glow=glow)
