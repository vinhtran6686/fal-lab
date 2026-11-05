"""lib-fx / force / shock: bursts of force released along an axis (a straight kick, a punch, a palm strike, a thrust).

Each design is  fn(t, P, front, back, pal=PAL_SUN, s=1.0, d=1)  drawing the wave t seconds after the contact:
  P      contact point (canvas px), the wave travels along +x (d=1) or -x (d=-1)
  front  / back  layers over / behind a character: the near half of every ring goes on front, the far half on back
  pal    any palette from _core/palettes.py (rim, body, light, core, white)
  s      size (1.0 = sized for a hero 120 px tall @2x)

How every design is built (game VFX practice):
  three beats   anticipation (a beat of build-up) -> burst (fast, ease-out, overshoot) -> dissipation (slow, thinning, never a pop)
  four layers   core flash (white, 2-4 frames)  > main shape (the read: rings, helix, petals; near half bright and wide, far half
                dark and thin)  > secondary (a thin shock ring, motion echoes, an axis streak, spawned BY the main shape)
                > particles (sparks, chips, motes, always emitted from a point of the shape, moving with drag, never sprinkled)
Every design is gone by DUR seconds.
"""
import math, random
from fxcore import (tone, mix, clamp, smooth, out_cubic, out_back, out_expo, lin, lune, lens, ribbon, twinkle,
                    stepped_glow, starburst, spark, arc3d, drag_pos)
from palettes import SUN as PAL_SUN

DUR = 0.6
FRAME, ANCHOR, FPS = (320, 320), (64, 160), 30   # asset canvas @2x, contact point inside it, frames per second
TAGS = ["force", "impact", "one-shot", "directional", "anchor:contact"]
CATALOG = {   # id: name (Vietnamese), description, status (draft | approved | rework), extra tags
    "tiers": dict(name="Tầng vòng", status="draft", tags=["light", "medium"],
                  desc="a hot flash at the contact, then three 3D rings born a frame apart along a bright axis streak; they shoot "
                       "forward accelerating, overshoot, leave motion echoes and shed sparks from their tips"),
    "vapor": dict(name="Nón hơi", status="draft", tags=["medium", "piercing"],
                  desc="a sonic-boom pressure cone: a hot spearpoint pierces forward while three shells of compressed air peel back from it "
                       "along flow lines; their mouths curl off into eddies and motes stream back"),
    "drill": dict(name="Khoan xoắn", status="draft", tags=["heavy", "piercing"],
                  desc="a spear of light inside a double helix that screws forward fast; the tip bites off small rings, sparks spiral off, "
                       "then the coils unwind outward and the tip flies on alone"),
    "shatter": dict(name="Vòng vỡ", status="draft", tags=["heavy"],
                    desc="a thick ring slams in, overheats and cracks at eight points (two frames of glowing cracks), then bursts: the arcs "
                         "tumble outward with hot fracture faces, chips fly from every crack and an energy ring escapes from the middle"),
    "bloom": dict(name="Hoa nổ", status="draft", tags=["heavy", "burst", "explosion"],
                  desc="an explosion shaped like a flower: rays rush in, a white flash, then three tiers of petals blast open with a shock ring, "
                       "embers fly from the petal tips and the petals tear away from the empty centre"),
}


def _x(P, d, s):
    return lambda dx: P[0] + d * dx * s


# ---------------------------------------------------------------- 1 tiers: three 3D rings born a frame apart along a bright axis
def shock_tiers(t, P, front, back, pal=PAL_SUN, s=1.0, d=1):
    X, py, sq = _x(P, d, s), P[1], 0.34
    # core flash at the contact
    f = 1 - smooth(0.0, 0.13, t)
    if f > 0:
        stepped_glow(front, X(6), py, 40 * s * (0.55 + 0.45 * out_cubic(t / 0.05)), pal, f)
        starburst(front, X(6), py, 34 * s * out_back(min(1, t / 0.05 + 0.3)), 8, pal, f, rot=0.2, seed=3, sy=1.15)
    tiers = [(0.0, 64, 10, 62), (1 / 15, 50, 22, 92), (2 / 15, 36, 34, 118)]     # birth, radius, born at, travel
    pos = []
    for k, (t0, R0, x0, D) in enumerate(tiers):
        u = (t - t0) / 0.44
        pos.append((x0 + D * out_cubic(clamp(u))) if u >= 0 else None)
    # the axis streak that strings the rings together (alive while they are young)
    ax = 1 - smooth(0.12, 0.32, t)
    if ax > 0 and t > 0:
        far = max(p for p in pos if p is not None)
        for wk, col, al in ((7.5, pal["rim"], 0.8), (5.0, pal["light"], 0.9), (1.8, pal["white"], 1.0)):
            lens(front, (X(-6), py), (X(far + 14), py), wk * s, col, ax * al, n=20)
    for k in (2, 1, 0):                                                   # far and small first, the big near one on top
        t0, R0, x0, D = tiers[k]
        u = (t - t0) / 0.44
        if not 0 <= u < 1: continue
        e = out_cubic(u)
        R = R0 * s * (0.3 + 0.78 * out_back(min(1, u * 1.35)))
        w = ((10 - 2 * k) * (1 - 0.7 * u) + 1.4) * s
        a = smooth(0, 0.04, u) * (1 - smooth(0.55, 1, u))
        cx = X(pos[k])
        # pressure membrane (behind), motion echoes, then the ring itself
        back.ellipse(cx, py, R * sq, R, pal["light"], a * 0.09 * (1 - u))
        for j, lag in ((1, 0.06), (2, 0.12)):
            ue = u - lag
            if ue > 0:
                ce = X(x0 + D * out_cubic(ue)); Re = R0 * s * (0.3 + 0.78 * out_back(min(1, ue * 1.35)))
                arc3d(front, back, ce, py, Re, w * 0.35, pal, a * (0.32 if j == 1 else 0.16), sq=sq, d=d, near_only=True)
        arc3d(front, back, cx, py, R, w, pal, a, sq=sq, d=d, hot=max(0.0, 1 - u * 3))
        # tips: a glint at birth, then two sparks each shed tangentially
        if u < 0.35:
            for sy in (-1, 1):
                twinkle(front, cx, py + sy * R, 4.5 * s * (1 - u / 0.35), pal, a)
        rng = random.Random(40 + k)
        for j in range(4):
            ue = u - 0.06 - 0.03 * j
            if ue <= 0: continue
            sy = -1 if j % 2 else 1
            th = sy * rng.uniform(1.15, 1.5)
            x0p, y0p = cx + d * R * math.cos(th) * sq, py + R * math.sin(th)
            vx, vy = d * rng.uniform(60, 140) * s, sy * rng.uniform(140, 260) * s
            x, y, vx2, vy2 = drag_pos(x0p, y0p, vx, vy, ue * 0.44, k=6)
            spark(front, x, y, vx2, vy2, 10 * s * (1 - ue), 2.4 * s, pal["light"], a * (1 - ue), core=pal["white"])


# ---------------------------------------------------------------- 2 vapor: a sonic boom, cones of compressed air left behind a spearpoint
def shock_vapor(t, P, front, back, pal=PAL_SUN, s=1.0, d=1):
    X, py, sq = _x(P, d, s), P[1], 0.36
    tip_at = lambda tt: X(24 + 124 * out_cubic(clamp(tt / 0.34)))
    tip = tip_at(t)
    f = 1 - smooth(0.0, 0.12, t)
    if f > 0:
        stepped_glow(front, X(4), py, 34 * s, pal, f)
        starburst(front, X(4), py, 26 * s, 6, pal, f, seed=4, sy=1.2)
    # the spearpoint and the crescent of compressed air riding on its nose
    sp = smooth(0, 0.03, t) * (1 - smooth(0.34, 0.5, t))
    if sp > 0:
        tail = tip - d * min(64 * s, abs(tip - X(0)))
        for wk, col in ((12, pal["rim"]), (9, pal["body"]), (5.5, pal["light"]), (2.2, pal["white"])):
            lens(front, (tail, py), (tip + d * 4 * s, py), wk * s, col, sp, n=18)
        lune(front, tip + d * 7 * s, py, 10 * s, 1.5 * s, 16 * s, pal["rim"], sp, d=d, ryi=14 * s)
        lune(front, tip + d * 7 * s, py, 8.5 * s, 3 * s, 14.5 * s, pal["light"], sp, d=d)
        lune(front, tip + d * 7 * s, py, 7 * s, 4.5 * s, 12.5 * s, pal["white"], sp, d=d)
    # cones of compressed air, born at the tip every few drawings and left behind on its path
    for k in range(4):
        t0 = 0.02 + k * 0.05
        u = (t - t0) / 0.4
        if not 0 <= u < 1: continue
        L = (46 - 6 * k) * s * out_cubic(min(1, u * 2.2))
        M = L * 0.62
        apex = tip_at(t0) - d * 20 * s * out_cubic(u)                     # drifts back a little as it opens
        a = smooth(0, 0.04, u) * (1 - smooth(0.4, 1, u))
        def surf(v, th):                                                  # v 0 at the apex, 1 at the mouth
            r = M * v ** 0.75
            return apex - d * L * v + d * r * math.cos(th) * sq, py + r * math.sin(th)
        v0 = smooth(0.15, 0.9, u) * 0.85                                  # the air nearest the apex clears first
        vs = lin(v0, 1, 12)
        top, bot = [surf(v, -math.pi / 2) for v in vs], [surf(v, math.pi / 2) for v in vs]
        mouth = [surf(1, th) for th in lin(-math.pi / 2, math.pi / 2, 14)]
        front.poly(top + mouth + bot[::-1], pal["light"], a * 0.1)
        # flow lines: the cone is drawn by the air running along it, near lines bright, far lines faint and behind
        for j in range(12):
            th = j / 12 * 2 * math.pi + 0.3 + 1.6 * u
            z = math.cos(th); near = (z + 1) / 2
            va = (0.13 * j + 1.8 * u) % 1.0                              # each streak slides from the apex to the mouth, then again
            vb = min(1.0, va + 0.42)
            va = max(va, v0)
            if vb - va < 0.08: continue
            seg = lin(va, vb, 9)
            pts = [surf(v, th) for v in seg]
            ws = [(0.6 + 2.6 * near) * s * (0.4 + v) * math.sin(math.pi * m / 8) ** 0.7 for m, v in enumerate(seg)]
            c = front if z >= 0 else back
            ribbon(c, pts, [x + 1.3 * s * (1 if x > 0 else 0) for x in ws], pal["rim"], a * (0.3 + 0.6 * near))
            ribbon(c, pts, ws, mix(pal["body"], pal["core"], near), a * (0.3 + 0.7 * near))
        arc3d(front, back, apex - d * L, py, M, (6.5 - k) * s * (1 - 0.5 * u), pal, a, sq=sq, d=d, hot=max(0.0, 0.7 - 2 * u))
        # the rim curls off into small eddies as it slows down
        if u > 0.3:
            ue = (u - 0.3) / 0.7
            for j in range(5):
                th = j / 5 * 2 * math.pi + 0.6 + k
                bx, by = apex - d * L + d * M * math.cos(th) * sq, py + M * math.sin(th)
                ox, oy = math.cos(th) * sq * d, math.sin(th)
                pts = []
                for m in range(12):
                    q = m / 11 * ue; ang = q * 4.5; rr = (3 + 9 * q) * s
                    pts.append((bx - d * 12 * s * q + ox * rr * math.cos(ang) - d * rr * math.sin(ang) * 0.5, by + oy * (6 * s * q + rr * math.cos(ang))))
                ribbon(front if math.cos(th) >= 0 else back, pts, [2.4 * s * (1 - m / 11) + 0.3 for m in range(12)], pal["light"], a * (1 - ue))
    # motes of condensation streaming back off the spearpoint
    rng = random.Random(7)
    for j in range(16):
        te = 0.04 + rng.uniform(0, 0.28)
        u = t - te
        if u <= 0 or u > 0.28: continue
        th = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(4, 16) * s
        x0p = tip_at(te) - d * rng.uniform(6, 20) * s
        x, y, vx, vy = drag_pos(x0p, py + r0 * math.sin(th), -d * rng.uniform(150, 240) * s, math.sin(th) * 90 * s, u, k=3)
        spark(front if math.cos(th) >= 0 else back, x, y, vx, vy, 8 * s, 2.2 * s, pal["core"], 1 - u / 0.28)


# ---------------------------------------------------------------- 3 drill: a spear of light inside a double helix screwing forward
def shock_drill(t, P, front, back, pal=PAL_SUN, s=1.0, d=1):
    X, py = _x(P, d, s), P[1]
    u = t / 0.56
    if not 0 <= u < 1: return
    grow = out_cubic(min(1, t / 0.16))
    a = smooth(0, 0.03, u) * (1 - smooth(0.62, 1, u))
    f = 1 - smooth(0.0, 0.12, t)
    if f > 0: stepped_glow(front, X(4), py, 38 * s, pal, f)
    Lx = 132 * s * grow
    unwind = 1 + 1.6 * smooth(0.48, 1, u) ** 1.3
    R0, R1 = 34 * s, 4 * s
    spin = 26 * t - 12 * t * t
    lead = smooth(0.5, 1, u) * 70 * s                                     # the tip flies on alone at the end
    # faint envelope behind: the drill reads as one solid body
    env_r = lambda v: (R0 * (1 - v) + R1 * v) * unwind * smooth(0.0, 0.18, v) ** 0.5
    env_t = [(X(4) + d * Lx * v, py - env_r(v)) for v in lin(0, 1, 24)]
    env_b = [(X(4) + d * Lx * v, py + env_r(v)) for v in lin(0, 1, 24)]
    back.poly(env_t + env_b[::-1], pal["light"], a * 0.08 * (1 - smooth(0.5, 1, u)))
    # helix samples
    M = 72; segs = []
    for h in (0, 1):
        pts = []
        for m in range(M + 1):
            v = m / M
            r = (R0 * (1 - v) + R1 * v) * unwind
            ph = 2 * math.pi * 2.4 * v - spin + h * math.pi
            z = math.cos(ph)
            pts.append((X(4) + d * (Lx * v + r * z * 0.24), py + r * math.sin(ph), z, (2.6 + 7 * (1 - v)) * s * (1 - 0.45 * smooth(0.5, 1, u)) * smooth(0.0, 0.12, v), v))
        for m in range(M):
            segs.append(((pts[m][2] + pts[m + 1][2]) / 2, h, pts[m], pts[m + 1]))
    def draw_seg(z, h, p, q, c):
        near = (z + 1) / 2
        ext = 0.35
        pa = (p[0] - (q[0] - p[0]) * ext, p[1] - (q[1] - p[1]) * ext); qa = (q[0] + (q[0] - p[0]) * ext, q[1] + (q[1] - p[1]) * ext)
        w = (p[3] + q[3]) / 2 * (0.55 + 0.45 * near)
        al = a * (0.45 + 0.55 * near)
        ribbon(c, [pa, qa], [w + 2.4 * s, w + 2.4 * s], pal["rim"], al)
        base = mix(mix(pal["rim"], pal["body"], 0.6), pal["body"] if h else pal["light"], near)
        ribbon(c, [pa, qa], [w, w], base, al)
        if near > 0.55: ribbon(c, [pa, qa], [w * 0.42, w * 0.42], mix(pal["light"], pal["core"], near), al)
        if near > 0.85: ribbon(c, [pa, qa], [w * 0.16, w * 0.16], pal["white"], al)
    for z, h, p, q in sorted(segs, key=lambda g: g[0]):                   # coils behind the spear first
        if z < 0: draw_seg(z, h, p, q, back)
    # the spear of light along the axis, between the back and the front coils
    sp_a = a * (1 - smooth(0.55, 0.95, u))
    tipx = X(4) + d * (Lx + 12 * s)
    for wk, col in ((15, pal["rim"]), (11, pal["body"]), (6.5, pal["light"]), (2.6, pal["white"])):
        lens(front, (X(-2), py), (tipx, py), wk * s * (1 - 0.4 * u), col, sp_a, n=22)
    for z, h, p, q in sorted(segs, key=lambda g: g[0]):
        if z >= 0: draw_seg(z, h, p, q, front)
    # the tip: a glint that flies on, and the rings it bites off every two drawings
    tx = tipx + d * lead
    twinkle(front, tx + d * 3 * s, py, 8 * s * (1 - 0.6 * u) * grow, pal, a)
    for j in range(4):
        tb = 0.05 + j * 2 / 30
        ub = (t - tb) / 0.22
        if not 0 <= ub < 1: continue
        xb = X(4) + d * (132 * s * out_cubic(min(1, tb / 0.16)) + 12 * s + 40 * s * out_cubic(ub))
        arc3d(front, back, xb, py, (10 + 16 * out_cubic(ub)) * s, 3.4 * s * (1 - ub), pal, (1 - ub) * a, sq=0.34, d=d, hot=1 - ub)
    # sparks spun off the outer coils
    rng = random.Random(11)
    for j in range(10):
        te = 0.06 + j * 0.022
        ue = t - te
        if ue <= 0 or ue > 0.26: continue
        v = rng.uniform(0.15, 0.7); h = j % 2
        r = (R0 * (1 - v) + R1 * v)
        ph = 2 * math.pi * 2.4 * v - (26 * te - 12 * te * te) + h * math.pi
        x0p, y0p = X(4) + d * (132 * s * out_cubic(min(1, te / 0.16)) * v), py + r * math.sin(ph)
        vx, vy = d * rng.uniform(-40, 80) * s, (math.cos(ph) * 1.0 + math.sin(ph) * 0.6) * rng.uniform(150, 240) * s * (1 if math.sin(ph) >= 0 else -1)
        x, y, vx2, vy2 = drag_pos(x0p, y0p, vx, vy, ue, k=5, g=120 * s)
        spark(front if math.cos(ph) >= 0 else back, x, y, vx2, vy2, 9 * s, 2.4 * s, pal["light"], 1 - ue / 0.26, core=pal["white"])


# ---------------------------------------------------------------- 4 shatter: a ring that overheats, cracks, then bursts apart
def shock_shatter(t, P, front, back, pal=PAL_SUN, s=1.0, d=1):
    X, py, sq = _x(P, d, s), P[1], 0.5
    cx, R = X(30), 58 * s
    T_CRACK, T_BREAK = 0.06, 0.14
    rng = random.Random(5)
    cuts = sorted([(j + rng.uniform(-0.18, 0.18)) / 8 * 2 * math.pi + 0.3 for j in range(8)])
    W = 13 * s
    def at(th, r, dx=0.0, dy=0.0): return cx + d * r * math.cos(th) * sq + dx, py + r * math.sin(th) + dy
    # core flash when it slams in, then again when it breaks
    f1 = 1 - smooth(0, 0.1, t)
    if f1 > 0: stepped_glow(front, X(6), py, 32 * s, pal, f1)
    f2 = smooth(T_BREAK - 0.01, T_BREAK, t) * (1 - smooth(T_BREAK, T_BREAK + 0.12, t))
    if f2 > 0:                                                            # a white flicker along the ring the moment it gives way
        arc3d(front, back, cx, py, R * 1.02, W * 0.5, pal, f2, sq=sq, d=d, hot=1.0)
    if t < T_BREAK:
        # slam in (overshoot), then hold hot with growing cracks
        g = out_back(min(1, t / T_CRACK))
        Rr = R * (0.45 + 0.55 * g) * (1 + 0.025 * math.sin(t * 160) * smooth(T_CRACK, T_BREAK, t))
        heat = smooth(T_CRACK, T_BREAK, t)
        arc3d(front, back, cx, py, Rr, W, pal, 1.0, sq=sq, d=d, hot=0.3 + 0.7 * heat)
        if heat > 0:
            for th in cuts:
                c = front if math.cos(th) >= 0 else back
                zig = [at(th + (0.05 if m % 2 else -0.05) * heat, Rr + (m / 4 - 0.5) * W * 1.25) for m in range(5)]
                ribbon(c, zig, [3.2 * s * heat] * 5, pal["rim"], 1.0)
                ribbon(c, [(x + d * 1.5 * s, y) for x, y in zig], [1.3 * s * heat] * 5, pal["white"], 1.0)
        return
    u = (t - T_BREAK) / (DUR - T_BREAK)
    e = out_cubic(u)
    a = 1 - smooth(0.55, 1, u)
    # the energy that was held escapes: a thin hot ring racing out of the middle
    ue = (t - T_BREAK) / 0.22
    if ue < 1:
        arc3d(front, back, cx, py, R * (0.3 + 1.25 * out_expo(ue)), 4.5 * s * (1 - ue), pal, 1 - ue, sq=sq, d=d, hot=1 - ue)
    # the arcs between the cracks fly out, tumble, keep hot faces where they broke
    frags = []
    for j in range(8):
        th0, th1 = cuts[j], cuts[(j + 1) % 8] + (2 * math.pi if j == 7 else 0)
        frags.append((math.cos((th0 + th1) / 2), j, th0, th1))
    for z, j, th0, th1 in sorted(frags):
        r2 = random.Random(100 + j)
        thm = (th0 + th1) / 2
        gap = 0.03 + 0.06 * e                                             # the broken ends pull apart
        fly = R * (0.45 + 0.9 * r2.random()) * e
        drop = r2.uniform(30, 80) * s * u * u
        dx, dy = d * (math.cos(thm) * sq * fly + 28 * s * e), math.sin(thm) * fly + drop
        tumble = 0.6 + 0.4 * abs(math.cos(r2.uniform(5, 9) * u + r2.uniform(0, 1)))
        spin = r2.uniform(-1.1, 1.1) * e
        a_th0, a_th1 = th0 + gap + spin, th1 - gap + spin
        # a short smear behind each arc (where it was a moment ago)
        for lag, al in ((0.08, 0.28), (0.16, 0.12)):
            el = out_cubic(max(0, u - lag)); fl = R * (0.45 + 0.9 * random.Random(100 + j).random()) * el
            arc3d(front, back, cx + d * (math.cos(thm) * sq * fl + 28 * s * el), py + math.sin(thm) * fl + 40 * s * max(0, u - lag) ** 2,
                  R, W * tumble * 0.5, pal, a * al, sq=sq, d=d, th0=a_th0, th1=a_th1, near_only=True)
        arc3d(front, back, cx + dx, py + dy, R, W * tumble, pal, a, sq=sq, d=d, th0=a_th0, th1=a_th1, hot=max(0.0, 0.8 - u * 2))
        # hot fracture faces at both broken ends
        hf = 1 - smooth(0.0, 0.35, u)
        if hf > 0:
            for th in (a_th0, a_th1):
                c = front if math.cos(th) >= 0 else back
                face = [at(th, R + W * tumble * k, dx, dy) for k in (-0.62, 0.0, 0.62)]
                ribbon(c, face, [2.0 * s, 3.4 * s, 2.0 * s], pal["rim"], hf)
                ribbon(c, face, [1.0 * s, 2.0 * s, 1.0 * s], pal["white"], hf)
    # chips thrown from every crack the moment it breaks
    for j, th in enumerate(cuts):
        r3 = random.Random(200 + j)
        for m in range(3):
            uc = t - T_BREAK - m * 0.012
            if uc <= 0 or uc > 0.34: continue
            x0p, y0p = at(th, R)
            sp = r3.uniform(220, 360) * s
            vx, vy = d * (math.cos(th) * sq * sp + r3.uniform(20, 80) * s), math.sin(th) * sp + r3.uniform(-40, 40) * s
            x, y, vx2, vy2 = drag_pos(x0p, y0p, vx, vy, uc, k=4.5, g=260 * s)
            sz = r3.uniform(2.5, 4.5) * s * (1 - uc / 0.34)
            rot = r3.uniform(0, 6) + uc * r3.uniform(10, 20)
            tri = [(x + math.cos(rot + q) * sz * rr, y + math.sin(rot + q) * sz * rr) for q, rr in ((0, 1.3), (2.2, 0.9), (4.1, 1.0))]
            c = front if math.cos(th) >= 0 else back
            c.poly([(px + (px - x) * 0.4, py_ + (py_ - y) * 0.4) for px, py_ in tri], pal["rim"], 1 - uc / 0.34)
            c.poly(tri, pal["light"] if m else pal["core"], 1 - uc / 0.34)


# ---------------------------------------------------------------- 5 bloom: an explosion in the shape of a flower
def shock_bloom(t, P, front, back, pal=PAL_SUN, s=1.0, d=1):
    X, py, sq = _x(P, d, s), P[1], 0.42
    cx = X(34)
    T_POP = 0.05
    # anticipation: rays rush into the centre
    if t < T_POP:
        k = t / T_POP
        for j in range(8):
            th = j / 8 * 2 * math.pi + 0.2
            r_out, r_in = 70 * s * (1 - k) + 10 * s, 50 * s * (1 - k) + 4 * s
            p0 = (cx + d * math.cos(th) * sq * r_out, py + math.sin(th) * r_out)
            p1 = (cx + d * math.cos(th) * sq * r_in, py + math.sin(th) * r_in)
            lens(front, p0, p1, 4 * s, pal["light"], 0.4 + 0.6 * k)
        front.ellipse(cx, py, (8 - 4 * k) * s, (8 - 4 * k) * s, pal["white"], 1)
        stepped_glow(front, cx, py, 22 * s * k, pal, k)
        return
    u = (t - T_POP) / (DUR - T_POP)
    # the flash
    fl = 1 - smooth(0.0, 0.2, u)
    if fl > 0:
        stepped_glow(front, cx, py, 70 * s * (0.6 + 0.4 * out_cubic(u / 0.08)), pal, fl, sy=1.3)
        starburst(front, cx, py, 64 * s * out_back(min(1, u / 0.08)), 12, pal, fl, rot=0.1, seed=12, sy=1.5, thin=0.7)
    # the shock ring in the flower's plane
    if u < 0.5:
        ur = u / 0.5
        arc3d(front, back, cx, py, (24 + 100 * out_expo(ur)) * s, 5 * s * (1 - ur), pal, 1 - ur, sq=sq, d=d, hot=1 - ur)
    # three tiers of petals blasting open, then tearing away from the centre
    tiers = [  # count, length, width, turn, delay, colours, alpha
        (10, 80, 17, 0.0, 0.00, ("body", "light"), 0.95),
        (8, 58, 14, math.pi / 8, 0.02, ("light", "core"), 1.0),
        (6, 30, 10, math.pi / 6, 0.04, ("core", "white"), 1.0),
    ]
    blades = []
    for ti, (n, Lb, Wb, off, dl, cols, al) in enumerate(tiers):
        ut = (t - T_POP - dl) / (DUR - T_POP - dl)
        if ut < 0: continue
        for j in range(n):
            th = j / n * 2 * math.pi + off + (0.9 if ti % 2 else -0.9) * ut
            blades.append((math.cos(th) + 0.01 * ti, ti, j, th, Lb, Wb, cols, al, ut))
    for z, ti, j, th, Lb, Wb, cols, al, ut in sorted(blades):
        r2 = random.Random(ti * 31 + j)
        burst = out_back(min(1, ut / 0.16), 2.2)                          # blast open with an overshoot
        tear = smooth(0.28, 1, ut)                                        # then let go of the centre
        r1 = (6 + Lb * r2.uniform(0.85, 1.12) * burst + 30 * s * tear) * s
        r0 = (4 + (Lb * 0.75 + 30) * tear ** 1.2) * s
        if r1 - r0 < 1: continue
        curl = (0.25 if j % 2 else -0.25) * tear
        near = (math.cos(th) + 1) / 2
        def pt(r, bend=0.0):
            tt = th + bend
            return cx + d * r * math.cos(tt) * sq, py + r * math.sin(tt)
        w = Wb * s * (1 - 0.65 * tear) * (0.6 + 0.4 * near)
        a = al * (1 - smooth(0.6, 1, ut)) * (0.5 + 0.5 * near)
        c = front if math.cos(th) >= 0 else back
        lens(c, pt(r0 - 1.5), pt(r1 + 2, curl), w + 3 * s, pal["rim"], a)
        lens(c, pt(r0), pt(r1, curl), w, mix(pal[cols[0]], pal[cols[1]], near), a)
        lens(c, pt(r0 + (r1 - r0) * 0.1), pt(r1 - (r1 - r0) * 0.15, curl * 0.9), w * 0.4, pal["white"] if near > 0.5 else pal["core"], a * (0.4 + 0.6 * near))
        # embers leave the tips of the outer petals as they open
        if ti == 0 and ut > 0.08:
            ue = (ut - 0.08) * (DUR - T_POP)
            if ue < 0.3:
                tipx, tipy = pt(6 * s + Lb * s)
                sp = r2.uniform(170, 260) * s
                vx, vy = d * math.cos(th) * sq * sp, math.sin(th) * sp
                x, y, vx2, vy2 = drag_pos(tipx, tipy, vx, vy, ue, k=4, g=150 * s)
                spark(c, x, y, vx2, vy2, 12 * s, 2.8 * s, pal["light"], 1 - ue / 0.3, core=pal["white"])
    # the hot core shrinks into the empty middle
    if u < 0.35:
        k = 1 - u / 0.35
        front.ellipse(cx, py, 10 * s * k + 1, 10 * s * k + 1, pal["white"], k)


VARIANTS = {"tiers": shock_tiers, "vapor": shock_vapor, "drill": shock_drill, "shatter": shock_shatter, "bloom": shock_bloom}
