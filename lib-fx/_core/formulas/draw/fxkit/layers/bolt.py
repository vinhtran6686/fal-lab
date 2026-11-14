"""fxkit / layers / bolt: a projectile flying from a to b (a fireball, a magic bolt, an arrow of light): a teardrop head, a living
ribbon trail with hair-thin streaks and a darker inner stripe. It arrives at b at t = 0 (the hit); after that the head is gone at once
and the trail is eaten in place while its far end catches up to b."""
import math
from .. import kind, smooth, clamp, Ink, THIN, erode, drop_specks, shapes
from .flames import decay_share


def _wavy(pts, angs, widths, off, ph_t, k0, amp, speed=14.0):
    """Two-edged strip along pts: each edge has its own travelling sine (amp = share of the local width)."""
    L, R = [], []
    n = len(pts)
    for k, ((x, y), a, w) in enumerate(zip(pts, angs, widths)):
        nx, ny = -math.sin(a), math.cos(a)
        wl = w * 0.5 * (1 + amp * math.sin(k * 0.9 + k0 - ph_t * speed))
        wr = w * 0.5 * (1 + amp * math.sin(k * 1.3 + k0 * 1.7 + ph_t * speed * 0.8))
        L.append((x + nx * (wl + off), y + ny * (wl + off))); R.append((x - nx * (wr - off), y - ny * (wr - off)))
    return L + R[::-1]


def _drop(p, ang, r, wob):
    """A teardrop head: round front, tapering to a point behind."""
    ca, sa = math.cos(ang), math.sin(ang); nx, ny = -sa, ca
    def q(u, v): return (p[0] + ca * u + nx * v, p[1] + sa * u + ny * v)
    pts = [q(r * 1.1, 0), q(r * 0.7, r * 0.82), q(-r * 0.2, r * 1.0), q(-r * 1.4, r * 0.45 + r * wob), q(-r * 2.4, r * 0.1 * wob),
           q(-r * 1.4, -r * 0.45 + r * wob), q(-r * 0.2, -r * 1.0), q(r * 0.7, -r * 0.82)]
    return shapes.spline(pts, True, 8, sharp=(4,))


@kind("bolt")
def bolt(c, ph, bend=0.0, r=13.0, tail=120.0, width=1.0):
    """A projectile flying from a to b at constant speed. role primary. Designed for Life(-0.3, 0.3, 0.0, 0.1).
    bend: bow of the flight path (0.28 = a lob); r: head radius, px; tail: trail length, px; width: trail width factor."""
    rng = c.rng("design"); s = c.s
    sp = c.sp; d = ph.decay
    f = ph.grow
    far0 = max(0.0, 1.0 - tail * s / sp.len) if d > 0 else max(0.0, f - tail * s / sp.len)
    f_head = 1.0 if d > 0 else f
    f_far = far0 + (1.0 - far0) * d if d > 0 else far0
    ink = Ink(c, smooth=THIN)
    N = 30
    if f_head - f_far > 1e-4:
        fs = [f_far + (f_head - f_far) * k / N for k in range(N + 1)]
        ps = [sp.path(q, bend) for q in fs]
        pts = [p for p, _ in ps]; angs = [a for _, a in ps]
        vs = [k / N for k in range(N + 1)]
        wd = 1.9 * r * s * width
        t = ph.sec; k0 = rng.uniform(0, 6.28)
        ink.add("main", _wavy(pts, angs, [wd * v ** 0.8 for v in vs], 0.0, t, k0, 0.12))
        for i in range(2):                                                  # hair-thin streaks beside the trail
            q = c.rng("streak", i)
            share = q.uniform(0.4, 0.7); side = 1 if i == 0 else -1
            off = side * q.uniform(0.55, 1.0) * r * s * width; w = q.uniform(3, 5) * s
            ks = [k for k in range(N + 1) if vs[k] >= 1 - share - 0.06 and vs[k] <= 0.94]
            if len(ks) < 3: continue
            sub = [(pts[k][0] - math.sin(angs[k]) * off, pts[k][1] + math.cos(angs[k]) * off) for k in ks]
            tt = [i2 / (len(ks) - 1) for i2 in range(len(ks))]
            ink.add("main", shapes.ribbon(sub, [w * math.sin(math.pi * x) ** 0.6 * (0.4 + 0.6 * x) for x in tt]))
        ks = [k for k in range(N + 1) if 0.05 <= vs[k] <= 0.6]
        if len(ks) >= 3:                                                    # the deep stripe: middle-rear of the trail
            ink.add("deep", _wavy([pts[k] for k in ks], [angs[k] for k in ks], [wd * 0.45 * vs[k] ** 0.8 * 1.0 for k in ks], 0.0, t, k0 + 2, 0.1))
    p, ang = sp.path(f_head, bend)
    if d <= 0:
        ink.add("hot", _drop(p, ang, r * s, 0.12 * math.sin(ph.sec * 20 + 1.0)))
    else:
        keep = decay_share(d, 3.9); seed = rng.randrange(1 << 16)
        body = erode(ink.mask("main"), keep, seed, ink.ss, holes=0.5, grain=10 * s)
        body = drop_specks(body, ink.ss, 5 * s * s)
        ink.set("main", body)
        ink.set("deep", erode(ink.mask("deep"), keep ** 1.5, seed + 1, ink.ss, holes=0.4, grain=9 * s) & body)
    ink.paint([("main", c.pal.tone("main")), ("deep", c.pal.tone("deep")), ("hot", c.pal.tone("hot"))], glow=1.0)
