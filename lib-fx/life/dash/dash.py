"""lib-fx / life / dash: a hero dashing forward fast (speed trails, dust, an element riding along).

Each design is  fn(t, P, front, back, pal=..., s=1.0, d=1)  drawing the dash t seconds after it starts:
  P      the dasher's chest at the start of the dash (canvas px); the dash runs along +x (d=1) or -x (d=-1)
  front  / back  layers over / behind a character
  s      size (1.0 = sized for a hero 120 px tall @2x)
The character moves with the head of the effect: head_x(t) in each design's docstring.
"""
import math, random
from fxcore import Canvas, mix, clamp, smooth, out_cubic, out_back, lens, ribbon, drag_pos
from organic import Shape, thorn, shard, blob, shade

DUR = 0.88
FRAME, ANCHOR, FPS = (800, 340), (160, 190), 30
TAGS = ["dash", "travel", "one-shot", "directional", "anchor:start"]
# layers of a flat, outline-free look: red, orange, yellow for the fire; grey and light grey for smoke, wind and dust
FLAME = dict(tip=(212, 56, 54), rim=(234, 92, 50), body=(246, 138, 54), light=(252, 188, 70), core=(255, 228, 136),
             white=(255, 250, 222), back=(118, 30, 30))
SMOKE = dict(dark=(100, 104, 112), shadow=(138, 140, 148), base=(184, 186, 192), light=(214, 216, 220))
PAL_SUN = FLAME
HALO = 0.4
CATALOG = {
    "tiger": dict(name="Hỏa hổ lướt", status="draft", tags=["fire", "heavy", "beast", "organic", "smoke"], glow=(255, 130, 60),
                  halo=(0.45, 10),
                  desc="a dash wrapped in a charging fire tiger: a white-hot beast head with an open maw, ears and a flaming mane "
                       "leads the dash; behind it flame tongues lick up and back, cooling from yellow to orange to red as they are "
                       "left behind, lift, tear and scatter red flecks; long yellow streaks trail the head while it is fast; grey "
                       "and light-grey layers (ground haze, toon smoke with swept tails, a dust kick at the start, wind shards, a "
                       "swoosh arc, dark speed lines) give it weight; at the end the head bursts forward into flame"),
}

T_RUN, RUN = 0.40, 450                                                    # the head runs RUN px in T_RUN s, fast then slowing


def _run(t):
    """How far (px, s=1) the head is at time t, and its speed factor 1 (start) -> 0 (stopped)."""
    u = clamp(t / T_RUN)
    return RUN * (1 - (1 - u) ** 2), 1 - u


def _passes(x):
    """When the head passes x (px, s=1)."""
    return T_RUN * (1 - math.sqrt(max(0.0, 1 - min(0.999, x / RUN))))


def flame_bands(pal, s=1.0, heat=1.0):
    """Edge -> centre bands; heat 1 burns white in the thick parts, 0 is red all through (an old flame)."""
    cols = [pal["tip"], pal["rim"], pal["body"], pal["light"], pal["core"], pal["white"]]
    lims = [1.1, 3.6, 6.8, 9.8, 12.8]
    top = int(round(5 * clamp(heat)))
    return [(lims[i] * s, cols[i]) for i in range(top)] + [(None, cols[top])]


def _layer(c): return Canvas(c.w, c.h, c.ss)


def spline(pts, k=6):
    """A closed Catmull-Rom curve through pts: rounds a hand-placed silhouette."""
    out, n = [], len(pts)
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        for j in range(k):
            u = j / k; u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * (2 * b + (-a + c) * u + (2 * a - 5 * b + 4 * c - e) * u2 + (-a + 3 * b - 3 * c + e) * u3)
                             for a, b, c, e in zip(p0, p1, p2, p3)))
    return out


# a tiger's head in profile facing +x (units: px at s=1, centre of the skull at 0,0): brow, nose, upper jaw, open maw, lower jaw, ruff
TIGER_HEAD = [(-38, -2), (-32, -22), (-16, -33), (2, -35), (20, -29), (34, -20), (46, -14), (55, -9), (54, -1), (46, 3), (30, 6),
              (20, 10), (30, 15), (44, 20), (46, 26), (38, 31), (18, 33), (-4, 32), (-24, 26), (-36, 14)]
TIGER_MAW = [(22, 9), (50, 1), (47, 17), (32, 15)]
TIGER_FACE = [((10, -17), (26, -13), 4.4), ((4, -25), (26, -21), 3.0), ((44, -13), (53, -9), 3.0), ((-22, -18), (-4, -9), 3.8),
              ((-28, -2), (-8, 3), 3.8), ((-20, 14), (-4, 10), 3.2), ((-34, -12), (-24, -6), 2.6), ((20, 12), (30, 13), 2.4)]
TIGER_FANGS = [[(41, 3), (47, 2), (44, 13)], [(35, 17), (40, 16), (37, 8)], [(28, 7), (32, 7), (30, 13)]]


def flame(x, y, ang, L, W, bend=0.0, wave=0.0, p=1.15, n=22):
    """A flame tongue from its base (x, y): like organic.thorn but its spine can sway in an S (wave) as well as curl (bend)."""
    left, right = [], []
    px, py = x, y
    for i in range(n + 1):
        s = i / n
        a = ang + bend * s * s + wave * math.sin(1.6 * math.pi * s)
        if i:
            px += math.cos(a) * L / n; py += math.sin(a) * L / n
        w = W / 2 * (1 - s) ** p * (0.75 + 0.25 * math.sin(math.pi * min(1.0, s * 2.2)))
        nx, ny = -math.sin(a), math.cos(a)
        left.append((px + nx * w, py + ny * w)); right.append((px - nx * w, py - ny * w))
    return left + right[::-1]


def dash_tiger(t, P, front, back, pal=FLAME, s=1.0, d=1):
    """head_x(t) = P.x + d * s * 450 * (1 - (1 - t/0.4)^2) until 0.4 s, then it stays and bursts."""
    pal = dict(pal)
    pal.setdefault("tip", mix(pal["rim"], (200, 40, 50), 0.4)); pal.setdefault("back", mix(pal["rim"], (0, 0, 0), 0.5))
    X = lambda dx: P[0] + d * dx * s
    A = lambda deg: math.radians(deg) if d > 0 else math.pi - math.radians(deg)    # angles drawn for +x, mirrored for -x
    py, gy = P[1], P[1] + 62 * s                                          # path height (chest) and the ground
    run, spd = _run(t)
    hx, hy = X(run), py - 4 * s

    # ================================================================ grey layers behind the fire
    # ground haze: a translucent grey strip the dash drags along the floor
    if t < 0.7:
        ah = 0.26 * smooth(0, 0.06, t) * (1 - smooth(0.35, 0.7, t))
        tail = X(min(run - 20, -40 + 420 * smooth(0.3, 0.7, t)))          # the back end catches up as it fades
        ly = _layer(back)
        n = 16
        xs = [tail + (hx - tail) * k / n for k in range(n + 1)]
        th = [math.sin(math.pi * k / n) ** 0.5 for k in range(n + 1)]     # pointed at both ends
        top = [(x, gy - 4 * s - 18 * s * h - 4 * s * math.sin(d * (x - P[0]) / s * 0.05)) for x, h in zip(xs, th)]
        bot = [(x, gy + 2 * s + 4 * s * h) for x, h in zip(xs, th)]
        ly.poly(top + bot[::-1], SMOKE["shadow"], ah)
        back.paste(ly)
    # swoosh arcs: a big thin wind arc above the path and a short one under it
    for k, (cx, cy, rx, ry, a0, a1, w, t0) in enumerate(((220, 70, 250, 120, 196, 330, 7, 0.04), (300, 10, 220, 52, 30, 150, 5, 0.1))):
        u = (t - t0) / 0.5
        if not 0 <= u < 1: continue
        ly = _layer(back)
        span = a0 + (a1 - a0) * out_cubic(min(1, u * 2.2))
        start = a0 + (a1 - a0) * smooth(0.3, 1, u)
        if span - start > 2:
            n = 30
            pts = [(X(cx + rx * math.cos(math.radians(start + (span - start) * i / n))), py + (cy + ry * math.sin(math.radians(start + (span - start) * i / n))) * s) for i in range(n + 1)]
            ribbon(ly, pts, [w * s * math.sin(math.pi * i / n) ** 0.7 + 0.3 for i in range(n + 1)], SMOKE["base"], 0.55 * (1 - smooth(0.6, 1, u)))
            back.paste(ly)
    # dark speed lines: thin strokes streaming past the head while it is fast
    ly = _layer(back)
    for j in range(10):
        tb = 0.02 + j * 0.035
        u = (t - tb) / 0.16
        if not 0 <= u < 1 or tb > T_RUN: continue
        rb, sp = _run(tb)
        yo = (-58, 40, -30, 54, -70, 26, -44, 62, -20, 48)[j] * s
        L = (150 + 60 * (j % 3)) * s * (0.5 + sp)
        x1 = X(rb - 10 - 60 * u); x0 = x1 - d * min(L * (1 - 0.6 * u), abs(x1 - X(-70)))
        lens(ly, (x0, py + yo + 6 * s * u), (x1, py + yo), 3.0 * s * (1 - 0.5 * u), SMOKE["dark"], 0.85 * (1 - u), n=12)
    back.paste(ly)
    # toon smoke along the floor: puffs with swept tails, left behind by the dash, rising and thinning
    for j in range(8):
        xj = 20 + j * 56 + (j % 2) * 14
        tb = _passes(xj + 30) + 0.04
        u = (t - tb) / 0.5
        if not 0 <= u < 1: continue
        rng = random.Random(300 + j)
        sh = Shape(back)
        g = 0.6 + 0.4 * out_back(min(1, u / 0.12)) + 0.5 * u
        bx, by = X(xj - 30 * u), gy - (6 + 26 * u ** 1.2) * s
        for dx, dy, r in ((0, -10, 15), (-16, -4, 10), (12, -18, 9)):
            sh.poly(blob(bx + d * dx * s * g, by + dy * s * g, r * s * g * rng.uniform(0.8, 1.25), wob=0.14, freq=4, phase=j))
        for ang, L, W, b, wv in ((180 - rng.uniform(2, 10), rng.uniform(80, 120), 18, -0.1, 0.12), (188, rng.uniform(40, 64), 12, 0.15, -0.1),
                                 (-148 + rng.uniform(-12, 12), rng.uniform(40, 62), 13, -0.3, 0.25)):
            sh.poly(flame(bx - d * 8 * s * g, by - 9 * s * g, A(ang), L * s * g * (1 - 0.3 * u), W * s * g, b * d, wv * d, p=1.5))
        shade(sh, SMOKE, 0.95 * (1 - smooth(0.55, 1, u)), off=3.5 * s, fillet=4.0, erode=8 * s * smooth(0.4, 1, u),
              noise=6 * s * smooth(0.25, 1, u), seed=40 + j, tones=("shadow", "base", "light"))
    # dust kick at the start: claws of grey thrown up and back from the feet, and a burst of smoke
    u = t / 0.5
    if u < 1:
        sh = Shape(back)
        g = 0.55 + 0.45 * out_back(min(1, u / 0.12)) + 0.3 * u
        fx, fy = X(-6 - 26 * u), gy - 4 * s
        for ang, L, W, b in ((-150, 78, 24, -0.35), (-168, 92, 22, -0.18), (-128, 56, 20, -0.4), (-176, 60, 14, 0.1), (-100, 34, 14, -0.3)):
            sh.poly(thorn(fx, fy - 6 * s, A(ang), L * s * g * (1 - 0.4 * smooth(0.4, 1, u)), W * s * g * (1 - 0.5 * u), b * d, p=1.6))
        for dx, dy, r in ((0, -10, 20), (-20, -6, 16), (14, -18, 13), (-36, -2, 11)):
            sh.poly(blob(fx + d * dx * s * g, fy + dy * s * g - 18 * s * u, r * s * g, wob=0.14, freq=4, phase=dx))
        shade(sh, SMOKE, 1 - smooth(0.55, 1, u), off=4 * s, fillet=4.0, erode=9 * s * smooth(0.45, 1, u), noise=6 * s * smooth(0.3, 1, u),
              seed=7, tones=("shadow", "base", "light"))

    # ================================================================ the fire body: flame tongues left along the path
    tongues = []
    for i in range(22):
        xi = 34 + i * 19.5
        rng = random.Random(500 + i)
        tb = _passes(xi + 24)
        life = rng.uniform(0.4, 0.5)
        up = i % 3 != 2
        if up:
            spec = (rng.uniform(-124, -96), rng.uniform(72, 120) * (0.8 + 0.4 * math.sin(i * 0.5) ** 2), rng.uniform(30, 42),
                    -rng.uniform(0.3, 0.55), rng.uniform(-8, 22))
        else:
            spec = (rng.uniform(116, 140), rng.uniform(42, 64), rng.uniform(22, 30), rng.uniform(0.2, 0.4), rng.uniform(18, 32))
        tongues.append((tb, xi, life, up, spec, rng.random()))
    for tb, xi, life, up, spec, ph in sorted(tongues, key=lambda q: q[0]):   # oldest (red, far back) first
        u = (t - tb) / life
        if not 0 <= u < 1: continue
        ang, L, W, bend, yo = spec
        g = 0.5 + 0.5 * out_back(min(1, (t - tb) / 0.07))
        fl = 1 + 0.12 * math.sin(31 * t + 7 * ph) + 0.06 * math.sin(53 * t + 3 * ph)       # flicker
        bx, by = X(xi - 16 * u), hy + yo * s - 36 * s * u ** 1.2                            # lifts and drifts back
        Lr = L * s * g * fl * (1 + 0.25 * u)
        Wr = W * s * g * (1 - 0.6 * smooth(0.3, 1, u))
        sh = Shape(front)
        wv = (0.32 if ph > 0.5 else -0.26) * (1 + 0.3 * math.sin(23 * t + 5 * ph))           # S-sway, alive
        sh.poly(flame(bx, by, A(ang), Lr, Wr, bend * (1 + 0.7 * u) * d, wv * d, p=1.1))
        if up and ph < 0.4:                                               # a small lick forking off the side
            fa = math.radians(ang)
            mx, my = bx + d * math.cos(fa) * Lr * 0.35, by + math.sin(fa) * Lr * 0.35
            sh.poly(flame(mx, my, A(ang - 42), Lr * 0.42, Wr * 0.5, -0.3 * d, 0.2 * d, p=1.3))
        sh.poly(blob(bx, by, Wr * 0.42, wob=0.2, freq=3, phase=ph * 6))
        heat = 0.9 * (1 - smooth(0.0, 0.8, u))
        sh.paint(flame_bands(pal, s, heat), 1 - smooth(0.72, 1, u), fillet=3.0, erode=9 * s * smooth(0.45, 1, u),
                 noise=6 * s * smooth(0.28, 1, u), seed=50 + int(ph * 3))                   # few seeds: the noise cache stays small
    # red flecks torn off the flame tips, drifting up and back long after
    sh = Shape(front)
    for tb, xi, life, up, spec, ph in tongues:
        ang, L, W, bend, yo = spec
        rng = random.Random(int(ph * 1e6))
        for m in range(2 if up else 1):
            te = tb + life * rng.uniform(0.3, 0.7)
            ue = (t - te) / 0.5
            if not 0 < ue < 1: continue
            fa = math.radians(ang + bend * 40)
            x0p = X(xi - 16 * (te - tb) / life) + d * math.cos(fa) * L * s * 0.8
            y0p = hy + yo * s - 36 * s * ((te - tb) / life) ** 1.2 + math.sin(fa) * L * s * 0.8
            vx, vy = -d * rng.uniform(40, 110) * s, -rng.uniform(50, 120) * s
            x, y, vx2, vy2 = drag_pos(x0p, y0p, vx, vy, ue * 0.5, k=2.0, g=-30 * s)
            sz = 1 - smooth(0.5, 1, ue)
            sh.poly(shard(x, y, math.atan2(vy2, vx2) + 0.5 * d * math.sin(9 * t + m), rng.uniform(12, 20) * s * sz, rng.uniform(6, 10) * s * sz, 0.6 * d))
    sh.paint(flame_bands(pal, s, 0.2), 0.95, fillet=2.0)

    # ================================================================ the head and what it drags
    T_END = T_RUN + 0.24
    # long yellow streaks trailing the head while it is fast (they shrink as it slows)
    if t < T_END:
        sh = Shape(front)
        fade = 1 - smooth(T_RUN - 0.04, T_END, t)
        for j, (yo, L, W, b) in enumerate(((-34, 120, 18, 0.06), (-14, 170, 22, -0.04), (10, 140, 20, 0.05), (30, 96, 16, -0.08))):
            Lr = (L * (0.25 + 0.75 * spd) * (1 + 0.1 * math.sin(40 * t + j))) * s * smooth(0, 0.05, t)
            if Lr > 4:
                sh.poly(thorn(hx - d * (26 + 4 * j) * s, hy + yo * s, A(180 + (j - 1.5) * 3), Lr, W * s, b * d, p=1.6))
        sh.paint(flame_bands(pal, s, 0.85), fade, fillet=3.0, erode=6 * s * smooth(T_RUN, T_END, t), noise=4 * s * smooth(T_RUN - 0.05, T_END, t), seed=91)
    # the tiger head: skull, muzzle, open jaws, ears, a flaming mane swept back; white-hot inside, orange at the edge
    if t < T_END:
        burst = smooth(T_RUN - 0.02, T_END, t)
        g = 1.3 * (0.55 + 0.45 * out_back(min(1, t / 0.09))) * (1 + 0.25 * burst) * s
        H = lambda dx, dy: (hx + d * dx * g, hy + dy * g)
        sh = Shape(front)
        sh.poly(spline([H(x, y) for x, y in TIGER_HEAD]))                                 # the head in profile
        for ang, x0, y0, L, W, b in ((-112, -10, -30, 30, 20, -0.4), (-138, -26, -24, 26, 18, -0.3)):     # ears
            sh.poly(thorn(*H(x0, y0), A(ang), L * g, W * g, b * d, p=1.3))
        rng = random.Random(77)
        for k in range(6):                                                # the mane: broad flames swept back off the skull
            ang = 146 + k * 15 + rng.uniform(-4, 4)
            th = math.radians(ang)
            L = rng.uniform(52, 84) * (1 + 0.15 * math.sin(36 * t + k * 1.7)) * (0.65 + 0.5 * spd)
            sh.poly(flame(*H(-6 + math.cos(th) * 22, -4 + math.sin(th) * 20), A(ang + (k - 2.5) * 4), L * g, rng.uniform(26, 34) * g,
                          (0.4 if k % 2 else -0.3) * d, (0.25 if k % 2 else -0.25) * d, p=1.2))
        for ang, x0, y0, L, W in ((150, -30, 18, 40, 22), (128, -12, 28, 34, 18), (112, 10, 30, 26, 14)):   # cheek ruff and chin
            sh.poly(flame(*H(x0, y0), A(ang), L * g * (0.8 + 0.4 * spd), W * g, 0.35 * d, 0.2 * d, p=1.2))
        sh.poly(spline([H(x, y) for x, y in TIGER_MAW], 4), on=False)                    # the open maw
        if burst > 0.15:                                                  # it hollows out from the middle as it bursts
            hr = 30 * g * smooth(0.15, 0.85, burst)
            sh.hole(*H(-4, 0), hr, hr * 0.85)
        heat = 1 - 0.65 * burst
        sh.paint(flame_bands(pal, s, heat), 1.0, fillet=3.5, erode=14 * s * smooth(0.2, 1, burst) ** 1.5,
                 noise=16 * s * smooth(0.0, 0.5, burst), seed=17, backing=(3.0 * s, pal["back"], 0.25 * (1 - burst)))
        # face: orange-red strokes on the white (eye, brow, nose, stripes) and two white fangs in the maw
        af = 1 - smooth(0.0, 0.6, burst)
        if af > 0.01:
            ly = _layer(front)
            for p0, p1, w in TIGER_FACE:
                lens(ly, H(*p0), H(*p1), w * g, pal["rim"], af, n=10)
            for f in TIGER_FANGS:
                ly.poly([H(*q) for q in f], pal["white"], af)
            ly.ellipse(*H(19, -15), 1.8 * g, 1.8 * g, pal["white"], af)
            front.paste(ly)
        # as it stops, the head bursts forward: tongues of fire thrown ahead
        if burst > 0:
            sh = Shape(front)
            ub = (t - (T_RUN - 0.02)) / (T_END - T_RUN + 0.02)
            for k, ang in enumerate((-34, -12, 10, 30)):
                r0 = (20 + 60 * out_cubic(ub)) * s
                th = A(ang)
                sh.poly(flame(hx + math.cos(th) * r0, hy + math.sin(th) * r0, th, (64 - 10 * (k % 2)) * s * (1 - 0.4 * ub), 26 * s * (1 - 0.5 * ub),
                              (0.4 if k % 2 else -0.4) * d, (0.3 if k % 2 else -0.3) * d, p=1.2))
            sh.paint(flame_bands(pal, s, 0.8 * (1 - ub)), 1.0, fillet=3.0, erode=12 * s * smooth(0.3, 1, ub), noise=6 * s * ub, seed=23)

    # ================================================================ light-grey wind shards flung off the dash
    ly = _layer(front)
    for j in range(14):
        rng = random.Random(900 + j)
        tb = 0.0 if j < 4 else _passes(40 + (j - 4) * 42)
        tb += rng.uniform(0, 0.03)
        u = (t - tb) / 0.36
        if not 0 < u < 1: continue
        rb, _ = _run(tb)
        side = -1 if j % 2 else 1
        x0p, y0p = X(rb - 70), py + side * rng.uniform(34, 70) * s
        ang = A(180 + side * rng.uniform(15, 40))
        sp = rng.uniform(160, 320) * s
        x, y, vx, vy = drag_pos(x0p, y0p, math.cos(ang) * sp, math.sin(ang) * sp, u * 0.36, k=4)
        L, Wd = rng.uniform(40, 70) * s * (1 - 0.4 * u), rng.uniform(6, 10) * s * (1 - 0.5 * u)
        rot = ang + 0.3 * d * math.sin(6 * u + j)
        ca, sa = math.cos(rot), math.sin(rot)
        zig = [(0, 0), (0.35, 0.8 * d), (0.55, -0.6 * d), (1.0, 0.0)]            # a jagged sliver: a zigzag spine, thin at both ends
        top_ = [(x + ca * L * a_ - sa * (b_ * Wd + Wd * 0.5 * math.sin(math.pi * a_)), y + sa * L * a_ + ca * (b_ * Wd + Wd * 0.5 * math.sin(math.pi * a_))) for a_, b_ in zig]
        bot_ = [(x + ca * L * a_ - sa * (b_ * Wd - Wd * 0.5 * math.sin(math.pi * a_)), y + sa * L * a_ + ca * (b_ * Wd - Wd * 0.5 * math.sin(math.pi * a_))) for a_, b_ in zig]
        ly.poly(top_ + bot_[::-1], SMOKE["light"], 0.95 * (1 - smooth(0.55, 1, u)))
    front.paste(ly)


VARIANTS = {"tiger": dash_tiger}
