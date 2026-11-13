"""fxkit / layers / flames: a mass of flame tongues erupting from a root (rules/vfx/explosion). The peak drawing is DESIGNED
(2-5 main tongues fanned unevenly, lengths 1 / 0.7-0.9 / 0.3-0.6, leaning off the axis), then it lives: born small at the root,
it bursts wide first and tall after, flickers at its peak, then is eaten in place (tips and thin parts first, the foot last)."""
import math
from .. import kind, sizes, angles, smooth, out_cubic, out_back, clamp, Ink, erode, drop_specks, shapes


def decay_share(d, k=3.9):
    """Share of the peak area still there at decay d (0..1): a fixed ratio per drawing (exponential), forced to 0 at the end."""
    return math.exp(-k * d) * (1 - d ** 2.5)


def on_twos(ph, c, after=0.65):
    """ph.decay held for two frames once the layer is past `after` of its life (rules/02 section 3); unchanged below 20 fps."""
    if ph.age < after or c.fps < 20: return ph.decay                  # 15 fps is already "on twos" of 30 fps: quantising again holds then drops
    n = max(1.0, c.layer.life.release * c.fps)
    return math.floor(ph.decay * n / 2) * 2 / n


@kind("flames")
def flames(c, ph, n=4, height=150.0, width=110.0, fan=80.0, dir=90.0, minor=3, pool=1.0, linger=3.2, flick=0.3):
    """Flame tongues erupting from the layer's anchor. role primary. Designed for Life(0, 0.1, 0.07, 0.5).
    n: main tongues (2-5); height: of the tallest, px; width: of the foot, px; fan: total spread of the tongue directions, degrees;
    dir: where it erupts, degrees in the axis frame (90 = the upper side: a ground eruption; 0 = along a -> b: an impact);
    minor: small tongues between the main ones; pool: size of the hot pool at the foot (0 = none); linger: how fast it is eaten
    (3.9 = short burst, 2.5 = a fire that burns on); flick: how much the tips sway while it lives."""
    rng = c.rng("design"); s = c.s
    g = ph.grow
    gy = 0.34 + 0.66 * out_cubic(g)                                        # tall comes after ...
    gx = 0.5 + 0.5 * out_back(min(1.0, g * 1.6), 2.4)                      # ... wide comes first, with an overshoot
    tilt = rng.uniform(-14, 14)
    ax = c.sp.ang(dir); nx, ny = -math.sin(ax), math.cos(ax)               # the eruption axis and the foot line across it
    x0, y0 = c.o
    szs = sizes(rng, n + minor, heroes=1, mid=0.8, small=0.42, jitter=0.14)
    main_sz, minor_sz = sorted(szs, reverse=True)[:n], sorted(szs)[:minor]
    rng.shuffle(main_sz)
    degs = angles(rng, n, -fan / 2, fan / 2, jitter=0.65)
    ink = Ink(c)
    time = ph.sec * 7.0
    tongues = []
    for i, (deg, sz) in enumerate(zip(degs, main_sz)):
        r = c.rng("tongue", i)
        off = deg / max(1.0, fan / 2) * width * 0.42 * gx * s
        base = (x0 + nx * off, y0 + ny * off)
        L = height * sz * gy * s * (1 + 0.1 * ph.age)
        W = height * 0.27 * (0.6 + 0.4 * sz) * r.uniform(0.85, 1.2) * gx * s
        a = ax + math.radians(deg + tilt) * 0.7
        lean = math.radians(deg) * 0.35 + r.uniform(-0.25, 0.25)
        curl = r.uniform(0.5, 1.0) * r.sign() + flick * math.sin(time + r.uniform(0, 6.28))
        tongues.append((base, a, L, W, lean, curl, r.uniform(1.5, 2.3), r.uniform(-0.3, 0.3), r))
        ink.add("main", shapes.tongue(base, a, L, W, lean, curl, belly=r.uniform(0.24, 0.36), sharp=tongues[-1][6], asym=tongues[-1][7]))
    for i, sz in enumerate(minor_sz):                                       # small licks between and outside the main tongues
        r = c.rng("minor", i)
        off = r.uniform(-0.55, 0.55) * width * gx * s
        base = (x0 + nx * off, y0 + ny * off)
        a = ax + math.radians(r.uniform(-fan * 0.65, fan * 0.65) + tilt)
        ink.add("main", shapes.tongue(base, a, height * sz * 0.8 * gy * s, height * 0.16 * gx * s * r.uniform(0.8, 1.3),
                                      r.uniform(-0.5, 0.5), r.uniform(-0.7, 0.7) + flick * math.sin(time * 1.3 + i), sharp=1.8))
    # the foot: one low mass joining the tongues
    foot = shapes.tongue((x0 - nx * width * 0.5 * gx * s, y0 - ny * width * 0.5 * gx * s), math.atan2(ny, nx), width * gx * s,
                         height * 0.2 * gy * s, 0, 0, belly=0.5, sharp=0.7, asym=-0.75, foot=0.2)
    ink.add("main", foot)
    # darker patches inside the mass: a shorter, thinner tongue inside each big one, starting above the foot
    for i, (base, a, L, W, lean, curl, sharp, asym, r) in enumerate(tongues):
        if L < height * 0.5 * s: continue
        sp = shapes.spine(base, a, L, lean, curl)
        p, a2 = shapes.along(sp, r.uniform(0.16, 0.26))
        ink.add("deep", shapes.tongue(p, a2, L * r.uniform(0.42, 0.58), W * r.uniform(0.34, 0.46), lean * 0.6, curl * 0.6, belly=0.35,
                                      sharp=1.4, asym=r.uniform(-0.4, 0.4), foot=0.1))
    # the hot pool at the foot with a few short licks: the brightest tone sits at the root and is the last to go
    if pool > 0:
        pw = width * 0.62 * pool * gx * s
        ink.add("hot", shapes.tongue((x0 - nx * pw * 0.5, y0 - ny * pw * 0.5), math.atan2(ny, nx), pw, height * 0.17 * pool * gy * s, 0, 0,
                                     belly=0.5, sharp=0.8, asym=-0.8, foot=0.15))
        for i in range(3):
            r = c.rng("lick", i)
            off = r.uniform(-0.3, 0.3) * pw
            ink.add("hot", shapes.tongue((x0 + nx * off, y0 + ny * off), ax + math.radians(r.uniform(-30, 30) + tilt),
                                         height * r.uniform(0.2, 0.36) * pool * gy * s, height * 0.11 * gx * s, r.uniform(-0.4, 0.4),
                                         r.uniform(-0.6, 0.6) + flick * math.sin(time * 1.7 + i * 2), sharp=1.6))
    # eaten in place
    d = on_twos(ph, c)
    if d > 0:
        keep = decay_share(d, linger); seed = rng.randrange(1 << 16)
        rise = height * 0.55 * s * d                                        # the holes travel along the eruption: the pieces seem to rise
        up = (math.cos(ax) * rise, math.sin(ax) * rise)
        body = erode(ink.mask("main"), keep, seed, ink.ss, holes=0.5, grain=height * 0.062 * s, stretch=1.8, shift=up)
        body = drop_specks(body, ink.ss, 6 * s * s)
        ink.set("main", body)
        ink.set("deep", erode(ink.mask("deep"), keep ** 1.6, seed + 1, ink.ss, holes=0.3, grain=height * 0.07 * s) & body)
        hot = erode(ink.mask("hot"), min(1.0, keep ** 0.5 * 1.05) * (1 - d ** 2), seed + 2, ink.ss, holes=0.4, grain=height * 0.05 * s,
                    root=c.o, root_bias=0.25, shift=(up[0] * 0.5, up[1] * 0.5))
        ink.set("hot", drop_specks(hot, ink.ss, 5 * s * s))
        ink.set("main", body | ink.mask("hot"))
    if ph.first:
        ink.paint([("main", c.pal.tone("hot")), ("hot", c.pal.tone("white"))], glow=1.0)
    else:
        ink.paint([("main", c.pal.tone("main")), ("deep", c.pal.tone("deep")), ("hot", c.pal.tone("hot"))], glow=1 - smooth(0.5, 0.85, ph.age))
