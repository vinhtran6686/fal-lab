"""fxkit / layers / smoke: see-through masses of smoke and ground dust in the house style. Never a heap of circles: ONE bold shape with a
few big lobes and long pointed curling ends (smoke), or two unequal low banks with lobes of different sizes and a pointed curling tip
(dust). They tear into curved rags where they stand (holes open, pieces rise or roll away), they do not shrink and do not fade."""
import math
from .. import kind, sizes, angles, smooth, out_cubic, out_back, out_expo, Ink, erode, drop_specks, shapes
from .flames import decay_share, on_twos


def _local(origin, ax, pts):
    """Points given as (u along the axis ax, v to its left-hand normal) -> canvas points."""
    ca, sa = math.cos(ax), math.sin(ax)
    return [(origin[0] + ca * u - sa * v, origin[1] + sa * u + ca * v) for u, v in pts]


@kind("smoke")
def smoke(c, ph, height=140.0, width=150.0, n=4, dir=90.0, dark=True, linger=2.8, drift=18.0):
    """A see-through mass of smoke thrown up behind an effect. role smoke, usually z="back". Designed for Life(0.033, 0.13, 0.1, 0.6).
    height: of the tallest wisp, px; width: of the low body, px; n: big wisps (pointed, curling); dir: where it rises, degrees in the
    axis frame (90 = the upper side, 0 = blown along a -> b); dark: True = tone smoke_dark at 0.62, False = tone smoke at 0.5;
    linger: how fast it is torn (3.0 = quick, 2.2 = lingers); drift: px it rises over its life."""
    rng = c.rng("design"); s = c.s; g = ph.grow
    gx = 0.55 + 0.45 * out_back(min(1.0, g * 1.4), 1.6)                       # wide first ...
    gy = 0.3 + 0.7 * out_cubic(max(0.0, g * 1.0 - 0.1) / 0.9)                 # ... tall after, slower than fire
    ax = c.sp.ang(dir)
    ux, uy = math.cos(ax), math.sin(ax)
    rise = drift * s * ph.age
    cx, cy = c.o[0] + ux * (0.25 * height * gy * s + rise), c.o[1] + uy * (0.25 * height * gy * s + rise)
    width = width * (0.5 + 0.5 * min(1.0, 1.3 * height / width))
    ink = Ink(c)
    # the low wide body: one lobed mass, uneven radii, squashed along the rise
    m = rng.randint(8, 10); sy = rng.uniform(0.5, 0.62); rot = rng.uniform(0, 6.28)
    big = rng.randrange(m)
    radii = []
    for i in range(m):
        r = rng.uniform(0.22, 0.38) * width * (1.0 if i != big else 1.25)
        radii.append(min(r, 0.55 * width))
    lob = []
    for i, r in enumerate(radii):
        th = rot + 2 * math.pi * i / m + rng.uniform(-0.12, 0.12)
        lob.append((r * math.sin(th) * sy * (0.4 + 0.6 * gy) * s, r * math.cos(th) * gx * s))
    body_pts = shapes.spline(_local((cx, cy), ax, lob), True, 8)
    ink.add("main", body_pts)
    # n big wisps: pointed lazy curls fanned around the rise, leaning outward, from points spread unevenly over the body
    szs = sizes(rng, n, heroes=1, mid=0.7, small=0.4, jitter=0.1)
    poss = angles(rng, n, -1.0, 1.0, jitter=0.7, gaps=1)
    wisps = []
    for i, (sz, pos) in enumerate(zip(szs, poss)):
        r = c.rng("wisp", i)
        deg = max(-65, min(65, (pos * 50 + r.uniform(-8, 8)) * (1.0 - 0.45 * sz)))
        v = pos * width * 0.36 * gx * s
        u = r.uniform(-0.1, 0.12) * height * gy * s + rise
        base = (c.o[0] + ux * u - uy * v, c.o[1] + uy * u + ux * v)
        L = height * 1.3 * sz * gy * s * (1.0 + 0.08 * ph.age)
        W = L * r.uniform(0.32, 0.44)
        a = ax + math.radians(deg)
        # the screen side of +deg: a + 90 deg is (-sin a, cos a); `lean` bends the wisp further the way it already points
        lean = math.copysign(r.uniform(0.05, 0.3), deg if abs(deg) > 3 else r.sign())
        curl = r.uniform(0.8, 1.3) * r.sign() + 0.25 * math.sin(ph.sec * 3 + r.uniform(0, 6.28))
        sharp = r.uniform(1.4, 1.9); belly = r.uniform(0.22, 0.34); asym = r.uniform(-0.25, 0.25)
        wisps.append((base, a, L, W, lean, curl, sharp, belly, asym, r))
        ink.add("main", shapes.tongue(base, a, L, W, lean, curl, belly=belly, sharp=sharp, asym=asym, foot=0.85))
    # 2-3 small wisps low at the sides, pointing sideways
    for i in range(rng.randint(2, 3)):
        r = c.rng("side", i)
        sd = (-1 if i % 2 == 0 else 1) * (1 if i < 2 else r.sign())
        v = sd * r.uniform(0.3, 0.48) * width * gx * s
        u = r.uniform(0.0, 0.16) * height * s + rise * 0.6
        base = (c.o[0] + ux * u - uy * v, c.o[1] + uy * u + ux * v)
        a = ax + math.radians(sd * r.uniform(72, 100))
        ink.add("main", shapes.tongue(base, a, height * r.uniform(0.3, 0.42) * gy * s, height * r.uniform(0.11, 0.16) * gx * s,
                                      math.copysign(r.uniform(0.2, 0.5), sd), r.uniform(0.5, 0.9) * r.sign() + 0.2 * math.sin(ph.sec * 3 + i),
                                      belly=0.35, sharp=1.4, foot=0.6))
    # depth: smaller copies of the biggest wisps and one inner lobe, painted lighter (dark smoke) or darker (light smoke)
    order = sorted(range(len(wisps)), key=lambda k: -wisps[k][2])[:3]
    for k in order:
        base, a, L, W, lean, curl, sharp, belly, asym, r = wisps[k]
        if L < height * 0.3 * s: continue
        sp = shapes.spine(base, a, L, lean, curl)
        p, a2 = shapes.along(sp, r.uniform(0.1, 0.26))
        ink.add("deep", shapes.tongue(p, a2, L * 0.62, W * 0.5, lean * 0.7, curl * 0.8, belly=belly, sharp=sharp, asym=asym * 0.5, foot=0.3))
    r = c.rng("inner")
    ink.add("deep", shapes.spline(_local((cx + ux * 0.05 * height * s, cy + uy * 0.05 * height * s), ax,
                                          [(rr * 0.4 * math.sin(2 * math.pi * i / 7 + 0.5) * sy * gy * s, rr * 0.4 * math.cos(2 * math.pi * i / 7 + 0.5) * gx * s)
                                           for i, rr in enumerate([r.uniform(0.3, 0.5) * width for _ in range(7)])]), True, 8))
    # torn in place: big holes open and travel along the rise, the mass breaks into curved rags that thin out
    d = on_twos(ph, c)
    if d > 0:
        keep = decay_share(d, linger); seed = rng.randrange(1 << 16)
        rs = height * 0.4 * s * d
        up = (ux * rs, uy * rs)
        body = erode(ink.mask("main"), keep, seed, ink.ss, holes=0.6, grain=height * 0.11 * s, stretch=1.3, shift=up)
        body = drop_specks(body, ink.ss, 10 * s * s)
        ink.set("main", body)
        ink.set("deep", erode(ink.mask("deep"), keep ** 1.5, seed + 1, ink.ss, holes=0.6, grain=height * 0.09 * s, stretch=1.3, shift=up) & body)
    else:
        ink.set("deep", ink.mask("deep") & ink.mask("main"))
    if dark: cm, cd, am = c.pal.tone("smoke_dark"), c.pal.tone("smoke"), 0.62
    else: cm, cd, am = c.pal.tone("smoke"), c.pal.tone("smoke_dark"), 0.5
    ink.paint([("main", cm), ("deep", cd)], glow=0, opacity={"main": am, "deep": 0.5})


def _bank(rng, k, tipsharp=True):
    """Control points (x, y) of one dust bank in units of reach (x outwards, 0 = the centre) and height (y up, 0 = the floor), going
    along the top from the centre to the tip and back along the floor; also the lobe peaks. k lobes of clearly different sizes, the
    biggest near the centre, dips between them, an outer end drawn out to a pointed tip that curls back upward."""
    pk = []
    for i in range(k):
        f = i / max(1, k - 1)
        x = 0.1 + 0.58 * f ** 1.15 + rng.uniform(-0.03, 0.03)
        h = (1.0 - 0.68 * f ** 0.9) * rng.uniform(0.82, 1.12)
        w = 0.1 + 0.06 * (1 - f) + rng.uniform(-0.02, 0.03)
        pk.append((x, h, w))
    pts = [(-0.05, 0.0), (-0.03, pk[0][1] * 0.6)]
    for i, (x, h, w) in enumerate(pk):
        pts.append((x - 0.05, h * 0.9)); pts.append((x, h)); pts.append((x + 0.05, h * 0.9))
        if i + 1 < k:
            nx_, nh, _ = pk[i + 1]
            pts.append(((x + nx_) / 2 + rng.uniform(-0.02, 0.02), min(h, nh) * rng.uniform(0.6, 0.78)))
    last = pk[-1]
    pts.append((last[0] + 0.14, last[1] * 0.42))                       # the dip before the tip
    pts.append((0.98 + rng.uniform(-0.02, 0.02), last[1] * 0.26))       # the outer flank, still low
    pts.append((0.87 + rng.uniform(-0.03, 0.03), 0.72 + rng.uniform(0, 0.14)))   # the tip: pointed, curled back upward
    tip = len(pts) - 1
    pts.append((0.88, 0.3)); pts.append((0.8, 0.1))
    pts.append((0.62, 0.0)); pts.append((0.3, 0.0))
    return pts, tip, pk


@kind("dust")
def dust(c, ph, reach=150.0, height=64.0, n=8, tone="light", linger=3.0):
    """Ground dust kicked out to both sides by a slam or a landing. role smoke. Designed for Life(0.033, 0.1, 0.1, 0.55).
    A cartoon dust bank, not a row of equal puffs: round lobes with a strong size hierarchy (one big, two or three medium, small
    ones far out), overlapping so the top is a scalloped line that steps down outward, a flat bottom on the floor, a thin
    pointed tail running out along the floor on each side, one side longer than the other. Three flat tones: a lit cap on the
    bigger lobes, the body, a darker band next to the floor. It opens from the middle and is eaten in place.
    Level with the screen (it never turns with a -> b).
    reach: px to the longer side; height: of the biggest lobe, px; n: lobes (both sides together); tone: "light" | "dark"
    (a dark bank goes behind, z="back"); linger: decay speed."""
    rng = c.rng("design"); s = c.s
    x0, fy = c.o[0], c.sp.floor
    g_out = 0.28 + 0.72 * out_expo(ph.grow)                                 # it shoots out along the floor ...
    g_up = (0.5 + 0.5 * out_cubic(ph.grow)) * (1 + 0.1 * ph.age)            # ... and swells more slowly, then keeps billowing
    long_side = rng.sign()
    n = int(n); szs = sorted(sizes(rng, n, heroes=1, mid=0.66, small=0.4, jitter=0.12), reverse=True)
    ink = Ink(c)
    reach_of = {long_side: reach, -long_side: reach * 0.7}
    count = {1: 0, -1: 0}; side = long_side * rng.sign()
    for i, sz in enumerate(szs):
        r = c.rng("lobe", i)
        if i: side = -side
        k = count[side]; count[side] += 1
        far = min(0.82, 0.1 + 0.2 * k + 0.05 * k * k) * r.uniform(0.88, 1.12)   # the big ones sit near the middle, the small ones far out
        R = height * 0.5 * sz * g_up * s * (1 + 0.1 * math.sin(ph.sec * 3 + i))  # each lobe breathes a little on its own
        cx = x0 + side * far * reach_of[side] * g_out * s * (1 + 0.07 * ph.age)
        cy = fy - R * r.uniform(0.62, 0.8)
        rx = R * r.uniform(1.1, 1.3)
        ink.add("main", shapes.lobed((cx, cy), [rx] * 14, sy=R / rx))
        if sz > 0.5:                                                          # a lit cap on the bigger lobes, towards the upper left
            ink.add("lit", shapes.lobed((cx - R * 0.2, cy - R * 0.22), [rx * 0.5] * 12, sy=R / rx * 0.85))
    for sd in (-1, 1):                                                        # a thin pointed tail running out along the floor
        R = reach_of[sd] * g_out * s * 1.2
        ink.add("main", shapes.tongue((x0 + sd * reach_of[sd] * 0.3 * g_out * s, fy - height * 0.1 * g_up * s), 0.0 if sd > 0 else math.pi, R * 0.75,
                                      height * 0.3 * g_up * s, lean=-0.16 * sd, curl=0.0, belly=0.2, sharp=1.5, foot=0.9))
    d = on_twos(ph, c)
    if d > 0:
        keep = decay_share(d, linger); seed = rng.randrange(1 << 16)
        hole = shapes.lobed((x0, fy - height * 0.18 * s), [reach * 0.42 * s * d * rng.uniform(0.75, 1.2) for _ in range(9)], sy=0.7)
        ink.cut("main", hole); ink.cut("lit", hole)
        body = erode(ink.mask("main"), keep, seed, ink.ss, holes=0.55, grain=height * 0.2 * s, stretch=0.8, shift=(0.0, -height * 0.3 * s * d))
        body = drop_specks(body, ink.ss, 8 * s * s)
        ink.set("main", body)
        ink.set("lit", erode(ink.mask("lit"), keep ** 1.5, seed + 1, ink.ss, holes=0.4, grain=height * 0.16 * s) & body)
    row = int(round(fy * ink.ss)) + 1                                         # nothing below the floor line
    body = ink.mask("main").copy(); body[row:] = False; ink.set("main", body)
    lit = ink.mask("lit") & body; ink.set("lit", lit)
    under = body.copy(); under[:max(0, row - int(height * 0.13 * g_up * s * ink.ss))] = False   # the darker band next to the floor
    ink.set("under", under & ~lit)
    cols = c.pal.smoke(tone)
    ink.paint([("main", cols["base"]), ("under", cols["shadow"]), ("lit", cols["light"])], glow=0,
              opacity={"main": 0.94, "under": 0.94, "lit": 0.94})
