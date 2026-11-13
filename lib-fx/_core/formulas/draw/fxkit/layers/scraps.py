"""fxkit / layers / scraps: the small flying pieces of an effect. In the house style sparks are not dots or straight lines: they
are small curved slivers (commas), each different, like the last frames of the references. Kinds: `scraps` (thrown pieces),
`embers` (slow glowing motes)."""
import math
import fxcore
from .. import kind, sizes, angles, smooth, clamp, Ink, THIN, shapes


def _first(c, ph, ink, glow, hot_too=True):
    """Paint one drawing (the first one overexposed)."""
    if ph.first:
        ink.paint([("main", c.pal.tone("hot")), ("hot", c.pal.tone("white"))], glow=glow)
    else:
        ink.paint([("main", c.pal.tone("main")), ("hot", c.pal.tone("hot"))], glow=glow)


@kind("scraps")
def scraps(c, ph, n=9, arc=(-180, 180), speed=(170, 430), drag=4.5, gravity=260.0, size=17.0, r0=10.0, spread=0.06):
    """Curved slivers thrown out of the anchor: they fly out fast, slow down (drag), fall (gravity), and each shortens and thins
    to nothing over the last 55 % of its own life. role particles. Designed for Life(0.033, 0.033, 0, 0.5).
    n: pieces; arc: (from, to) degrees in the axis frame (a full circle = every direction); speed: (slowest, fastest) px/s, the
    big pieces are the fast ones; drag: air drag (1/s); gravity: screen-down pull, px/s^2; size: length of the biggest, px;
    r0: how far from the anchor they are born, px; spread: longest birth delay, s."""
    rng = c.rng("design"); s = c.s
    lo, hi = float(arc[0]), float(arc[1]); span = hi - lo; mid = (lo + hi) / 2
    ax = c.sp.ang(mid); hand = c.sp.hand
    offs = angles(rng, n, lo - mid, hi - mid, jitter=0.8, gaps=1)
    if span >= 330:
        rot = rng.uniform(0, 360); offs = [o + rot for o in offs]
    szs = sizes(rng, n, heroes=1, mid=0.6, small=0.32, jitter=0.18)
    big = sorted(range(n), key=lambda i: -szs[i])[:min(3, max(2, n // 4))]
    x0, y0 = c.o; total = c.layer.life.length
    ink = Ink(c, smooth=THIN)
    for i in range(n):
        r = c.rng("scrap", i)
        ang = ax - math.radians(offs[i]) * hand
        sz = szs[i]
        v = (speed[0] + (speed[1] - speed[0]) * sz * r.uniform(0.8, 1.0)) * s
        delay = r.uniform(0.0, spread) if i else 0.0
        share = r.uniform(0.5, 1.0)
        curl = r.uniform(0.3, 0.9) * r.sign() * 1.7; L0 = size * s * sz; W0 = L0 * r.uniform(0.3, 0.42)
        t = ph.sec - delay; u = t / (total * share)
        if t < 0 or u >= 1: continue
        px0, py0 = x0 + math.cos(ang) * r0 * s * r.uniform(0.6, 1.2), y0 + math.sin(ang) * r0 * s * r.uniform(0.6, 1.2)
        x, y, vx, vy = fxcore.drag_pos(px0, py0, math.cos(ang) * v, math.sin(ang) * v, t, drag, gravity * s)
        a = math.atan2(vy, vx) if math.hypot(vx, vy) > 1e-3 else ang
        f = 1.0 if u < 0.45 else (1 - (u - 0.45) / 0.55) ** 0.85
        L, W = L0 * f, W0 * f
        if L < 1.6 * s: continue
        tone = "hot" if (i in big and u < 0.4) else "main"
        ink.add(tone, shapes.scrap((x, y), a + math.pi, L, W, curl * (1 + 0.5 * u)))
    _first(c, ph, ink, 0.8 * (1 - smooth(0.5, 0.9, ph.age)))


@kind("embers")
def embers(c, ph, n=7, area=(80, 34), rise=(34, 80), sway=8.0, size=9.0):
    """Slow glowing motes rising after fire or magic: tiny curved slivers that come one after another, drift up with a sideways
    sway, and shrink in three clear steps before they are gone. role particles. Designed for Life(0.1, 0.05, 0.3, 0.45).
    n: motes; area: (half width, half height) of the birth box around the anchor, px; rise: (slowest, fastest) px/s upwards;
    sway: sideways swing, px; size: length of the biggest, px (3 px at the smallest)."""
    rng = c.rng("design"); s = c.s
    total = c.layer.life.length; x0, y0 = c.o
    szs = sizes(rng, n, heroes=1, mid=0.6, small=0.4, jitter=0.2)
    order = list(range(n)); rng.shuffle(order)
    ink = Ink(c, smooth=THIN)
    for k, i in enumerate(order):
        r = c.rng("ember", i)
        birth = (k + r.uniform(0.05, 0.95)) / n * 0.6 * total               # one after another, inside the first 60 % of the life
        life = min(r.uniform(0.3, 0.55), total - birth - 0.03)
        t = ph.sec - birth
        if t < 0 or life < 0.1 or t >= life: continue
        u = t / life
        bx, by = x0 + r.uniform(-1, 1) * area[0] * s, y0 + r.uniform(-1, 1) * area[1] * s
        up = r.uniform(*rise) * s; fq = r.uniform(1.2, 2.4); ph0 = r.uniform(0, 6.28); sw = sway * s * r.uniform(0.6, 1.2)
        x = bx + sw * math.sin(2 * math.pi * fq * t + ph0); y = by - up * t
        vx = sw * 2 * math.pi * fq * math.cos(2 * math.pi * fq * t + ph0)
        a = math.atan2(-up, vx)
        step = 1.0 if u < 0.34 else (0.65 if u < 0.67 else 0.35)
        L = max(3.0, min(9.0, size * szs[i])) * s * step
        ink.add("hot" if u < 0.4 else "main", shapes.scrap((x, y), a + math.pi, L, L * r.uniform(0.4, 0.5), r.uniform(0.4, 1.0) * r.sign()))
    _first(c, ph, ink, 0.7)
