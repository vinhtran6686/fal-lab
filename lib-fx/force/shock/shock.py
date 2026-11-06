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
from fxcore import (Canvas, tone, mix, clamp, smooth, out_cubic, out_back, out_expo, lin, lune, lens, ribbon, twinkle, band,
                    stepped_glow, starburst, spark, arc3d, drag_pos)
from organic import Shape, thorn, shard, blob, thorns_at
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
    "inferno": dict(name="Hỏa xung tầng", status="approved", tags=["heavy", "fire", "projectile", "burst", "organic"],
                    frame=(640, 400), anchor=(60, 200), dur=0.78, glow=(255, 120, 40), halo=(0.55, 10),
                    desc="a burning punch: rays rush into an orb at the fist, a spiky white flash fuses with a white-hot beam, a dark-red ring "
                         "stands around the fist, and four tiers of broken calligraphic fire rings fly out with a faint pressure front ahead; "
                         "the first ring travels farthest and grows widest, every ring cools, fades and breaks into hooks and chips, while "
                         "bright tracers with arrow heads, sparks and rising embers scatter forward"),
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


# ---------------------------------------------------------------- 6 inferno: a punch that fires a train of burning shock rings
# Built from many layers (back to front): far halves of the rings, a faint pressure cone, dim speed streaks, a dark-red ring around
# the fist, the white-hot beam fused with a spiky muzzle flash, the near halves of four ring tiers (broken calligraphic strokes
# with hooks and barbs), bright tracers with arrow heads, sparks off the flash, embers off the ring ends and chips when they break.
# The rings are hand-drawn silhouettes coloured by distance to their edge (organic.Shape): thick middles burn white-yellow, thin
# ends orange-red. The first ring born travels farthest and grows biggest: a shock wave widens, cools and fades as it spreads.
INFERNO = dict(tip=(172, 32, 20), rim=(226, 70, 24), body=(246, 116, 32), light=(255, 168, 60), core=(255, 224, 146),
               white=(255, 250, 234), back=(92, 18, 12))
CATALOG["inferno"]["palette"] = INFERNO                               # set here: the palette is defined after CATALOG
T_FIRE = 2 / 30                                                           # two drawings of build-up, then the burst
SQ, LEAN = 0.44, 0.32                                                      # ring seen three-quarters; its top leans forward
# tier: born (s after the burst), start x, travel, start radius, end radius, stroke width, life (s), seed; tier 0 is the oldest
INF_TIERS = [(0.00, 30, 380, 26, 138, 19, 0.74, 3), (0.04, 26, 290, 24, 114, 20, 0.69, 8),
             (0.08, 22, 200, 20, 88, 20, 0.63, 13), (0.12, 18, 118, 16, 62, 18, 0.57, 21)]


def fire_bands(pal, s=1.0, heat=1.0):
    """Edge -> centre bands; as it cools the hottest colours drop out (white first, then pale yellow, then yellow)."""
    cols = [pal["tip"], pal["rim"], pal["body"], pal["light"], pal["core"], pal["white"]]
    lims = [1.4, 3.4, 6.0, 8.6, 11.5]
    top = 2 + int(round(3 * clamp(heat)))                                # index of the hottest colour still burning
    return [(lims[i] * s, cols[i]) for i in range(top)] + [(None, cols[top])]


def dark_bands(pal, s=1.0, heat=1.0):
    """The far half of a ring, behind everything: dim and red."""
    return [(1.6 * s, pal["back"]), (3.6 * s, pal["tip"]), (6.5 * s, pal["rim"])] + ([(None, pal["body"])] if heat > 0.4 else [(None, pal["rim"])])


def _ring_pt(cx, cy, r, th, d):
    """A point on a ring standing across the axis at cx, seen three-quarters, its top leaning forward."""
    y = r * math.sin(th)
    return cx + d * (r * math.cos(th) * SQ - LEAN * y), cy + y


def _stroke(cx, cy, R, th0, th1, W, d, hook=0.0, n=30):
    """A calligraphic stroke along the ring from th0 to th1: fat middle, pointed ends, thinner on the far side; hook curls the end
    inward. Returns (outline, centre line, widths)."""
    cl, ws = [], []
    for i in range(n + 1):
        v = i / n
        th = th0 + (th1 - th0) * v
        r = R * (1 - hook * 0.24 * smooth(0.7, 1.0, v) ** 1.4)
        near = (math.cos(th) + 1) / 2
        cl.append(_ring_pt(cx, cy, r, th, d))
        ws.append(W * max(0.0, math.sin(math.pi * v)) ** 0.55 * (0.45 + 0.55 * near))
    L, Rr = [], []
    for i, (x, y) in enumerate(cl):
        p, q = cl[max(0, i - 1)], cl[min(n, i + 1)]
        dx, dy = q[0] - p[0], q[1] - p[1]; l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        L.append((x + nx * ws[i] / 2, y + ny * ws[i] / 2)); Rr.append((x - nx * ws[i] / 2, y - ny * ws[i] / 2))
    return L + Rr[::-1], cl, ws


def _segments(seed):
    """3-5 broken arcs around a ring (start, end in radians), uneven lengths and gaps, plus a hook direction per arc."""
    rng = random.Random(seed)
    segs, a = [], rng.uniform(-math.pi, -math.pi / 2)
    end = a + 2 * math.pi
    while a < end - 0.5:
        span = min(rng.uniform(1.5, 2.5), end - a - 0.15)
        if span < 0.5: break
        segs.append((a, a + span, rng.choice((-1, 1)) * rng.uniform(0.5, 1.0)))
        a += span + rng.uniform(0.22, 0.45)
    return segs


def _tier_state(k, t, s, d, P):
    """Where tier k is at time t: (u, centre x, radius, width, alpha, heat) or None."""
    tb, x0, D, R0, R1, W, life, _ = INF_TIERS[k]
    u = (t - T_FIRE - tb) / life
    if not 0 <= u < 1: return None
    e = 1 - (1 - u) ** 1.9                                                # fast out, slowing down as it spreads
    cx = P[0] + d * (x0 + D * e) * s
    R = (R0 + (R1 - R0) * out_cubic(min(1, u * 1.15)) + 0.12 * R1 * u) * s       # keeps widening until it is gone
    w = W * s * (1.15 - 0.7 * smooth(0.05, 1, u))
    fade = (0.78, 0.88, 0.96, 1.0)[k]                                     # the oldest, widest ring is the faintest
    a = fade * smooth(0, 0.04, u) * (1 - smooth(0.55, 1, u))
    heat = (1 - smooth(0.05, 0.85, u)) * (0.82 + 0.06 * k)
    return u, cx, R, w, a, heat


def _tier_arcs(k, t, s, d, P):
    """The arcs of tier k at time t: [(th0, th1, hook, near?)], spun, shrunk and drifted apart as the ring breaks."""
    st = _tier_state(k, t, s, d, P)
    if st is None: return st, []
    u = st[0]
    spin = (0.55 if k % 2 else -0.55) * out_cubic(u)
    brk = smooth(0.42, 1, u)
    out = []
    for th0, th1, hook in _segments(INF_TIERS[k][7]):
        m, h = (th0 + th1) / 2 + spin, (th1 - th0) / 2 * (1 - 0.4 * brk)
        out.append((m - h, m + h, hook, math.cos(m) >= 0))
    return st, out


def _layer(c):
    """A fresh layer the size of canvas c: translucent strokes drawn on it are then composited (drawing straight onto a canvas
    replaces the pixels underneath instead of blending with them)."""
    return Canvas(c.w, c.h, c.ss)


def shock_inferno(t, P, front, back, pal=INFERNO, s=1.0, d=1):
    """Frame size scales with s: at s > 1 give it a canvas of about (640, 400) * s, anchor (60, 200) * s."""
    pal = dict(pal)
    pal.setdefault("tip", tone(pal["rim"], 0.8)); pal.setdefault("back", tone(pal["rim"], 0.45))   # any standard palette works
    X, py = _x(P, d, s), P[1]
    off = 0.0 if d > 0 else math.pi                                       # the near half of a ring faces the way the shot goes
    # ---- build-up: rays rush into a growing orb at the fist, a ring closes in around it
    if t < T_FIRE - 1e-6:
        k = t / T_FIRE + 0.5
        cx = X(10)
        stepped_glow(front, cx, py, (14 + 16 * k) * s, pal, 0.7 + 0.3 * k)
        for j in range(9):
            th = (j / 9 - 0.5) * 2.6 + 0.1 * (j % 2)
            r_out, r_in = (80 * (1 - k) + 26) * s, (50 * (1 - k) + 12) * s
            p0 = (cx + d * math.cos(th) * r_out, py + math.sin(th) * r_out * 0.8)
            p1 = (cx + d * math.cos(th) * r_in, py + math.sin(th) * r_in * 0.8)
            lens(front, p0, p1, 3.4 * s, pal["light"], 0.5 + 0.5 * k)
        band(back, cx, py, 10 * s, (64 - 30 * k) * s, 3 * s, pal["rim"], 0.6, math.pi / 2 + off, 3 * math.pi / 2 + off)
        band(front, cx, py, 10 * s, (64 - 30 * k) * s, 3 * s, pal["light"], 0.8, -math.pi / 2 + off, math.pi / 2 + off)
        front.ellipse(cx, py, (6 + 3 * k) * s, (6 + 3 * k) * s, pal["white"], 1)
        return
    tf = t - T_FIRE
    first = tf < 1 / 30 - 1e-6
    # ---- the leading pressure front: a faint, wide, dark-red ring racing ahead of everything
    ug = tf / 0.62
    if ug < 1:
        Rg, cg = (34 + 150 * out_cubic(ug)) * s, X(34 + 430 * (1 - (1 - ug) ** 2.2))
        ag = 0.55 * smooth(0, 0.05, ug) * (1 - smooth(0.3, 1, ug))
        for half, c, col, al in (((math.pi / 2, 3 * math.pi / 2), back, pal["back"], 0.6), ((-math.pi / 2, math.pi / 2), back, pal["tip"], 1.0)):
            pts = [_ring_pt(cg, py, Rg, th, d) for th in lin(half[0], half[1], 40)]
            ly = _layer(c)
            ribbon(ly, pts, [(4.5 * s * (1 - 0.5 * ug)) * max(0.0, math.sin(math.pi * i / 39)) ** 0.4 for i in range(40)], col, ag * al)
            c.paste(ly)
    # ---- pressure cone behind the rings (volume, very faint)
    lead = max((st[1] for st in (_tier_state(k, t, s, d, P) for k in range(4)) if st), default=None, key=lambda x: d * x)
    if lead is not None and tf < 0.5:
        ac = 0.07 * (1 - smooth(0.15, 0.5, tf))
        for kk in (1.0, 0.6):
            Rc = 90 * s * kk * smooth(0, 0.1, tf)
            ly = _layer(back)
            ly.poly([(X(16), py - 8 * s), (lead, py - Rc), (lead + d * 20 * s, py), (lead, py + Rc), (X(16), py + 8 * s)], pal["rim"], ac)
            back.paste(ly)
    # ---- ring tiers: far halves (behind), motion smears, then near halves (front), oldest first
    tiers = []
    for k in range(4):
        st, arcs = _tier_arcs(k, t, s, d, P)
        if st: tiers.append((k, st, arcs))
    for k, (u, cx, R, w, a, heat), arcs in tiers:
        brk = smooth(0.42, 1, u)
        Rd = R * (1 + 0.14 * brk)                                         # the pieces drift apart as the ring breaks
        sh = Shape(back)
        for th0, th1, hook, near in arcs:
            if not near: sh.poly(_stroke(cx, py, Rd, th0, th1, w * 0.8, d, hook)[0])
        sh.paint(dark_bands(pal, s, heat), a * 0.85, fillet=2.0, erode=7 * s * smooth(0.55, 1, u), noise=4 * s * smooth(0.42, 1, u), seed=50 + k)
        # smear: where the near arcs were a moment ago, thin and faint, behind
        st2, arcs2 = _tier_arcs(k, t - 0.05, s, d, P)
        if st2:
            ly = _layer(back)
            for th0, th1, hook, near in arcs2:
                if near:
                    _, cl, ws = _stroke(st2[1], py, st2[2] * (1 + 0.14 * smooth(0.42, 1, st2[0])), th0, th1, st2[3], d, hook, n=20)
                    ribbon(ly, cl, [x * 0.45 for x in ws], pal["rim"], a * 0.35)
            back.paste(ly)
    for k, (u, cx, R, w, a, heat), arcs in tiers:
        brk = smooth(0.42, 1, u)
        Rd = R * (1 + 0.14 * brk)
        sh = Shape(front)
        rng = random.Random(70 + k)
        for th0, th1, hook, near in arcs:
            if not near: continue
            poly, cl, ws = _stroke(cx, py, Rd, th0, th1, w, d, hook)
            sh.poly(poly)
            # barbs: short thorns torn off the outer edge, trailing behind the stroke's motion
            if th1 - th0 > 0.7:
                for v in (0.3, 0.62):
                    i = int(v * (len(cl) - 1))
                    (x, y), (x2, y2) = cl[i], cl[i + 1]
                    tang = math.atan2(y2 - y, x2 - x) + (math.pi if hook > 0 else 0)
                    outw = math.atan2(y - py, (x - cx) * 2.5)
                    ang = tang + 0.45 * math.sin(outw - tang)
                    sh.poly(thorn(x, y, ang, (0.16 + 0.1 * rng.random()) * R * (1 - 0.5 * brk), ws[i] * 0.75, bend=0.35 * d * (1 if hook > 0 else -1)))
            # chips thrown off the ends once it starts to break
            if brk > 0:
                for end, sgn in ((cl[2], -1), (cl[-3], 1)):
                    ang = math.atan2(end[1] - py, (end[0] - cx) * 2.0) + sgn * 0.3
                    dist = 26 * s * out_cubic(brk) + 4 * s
                    sz = 1 - smooth(0.6, 1, brk)
                    if sz > 0.05:
                        sh.poly(shard(end[0] + math.cos(ang) * dist, end[1] + math.sin(ang) * dist, ang, 13 * s * sz, 7 * s * sz, 0.3 * d))
        sh.paint(fire_bands(pal, s, heat), a, fillet=3.0, erode=8 * s * smooth(0.55, 1, u), noise=5 * s * smooth(0.42, 1, u), seed=60 + k,
                 backing=(3.0 * s, pal["back"], 0.3 * (1 - smooth(0.3, 0.9, u))))
        # a thin second line riding inside the stroke a beat behind it: the double line of a brush, it burns out first
        ac = a * (1 - smooth(0.25, 0.7, u))
        if ac > 0.01:
            ly = _layer(front)
            for th0, th1, hook, near in arcs:
                if not near or th1 - th0 < 0.8: continue
                _, cl, ws = _stroke(cx - d * 10 * s, py, Rd * 0.84, th0 + 0.2, th1 - 0.1, w, d, hook * 0.6, n=24)
                ribbon(ly, cl, [x * 0.2 + 0.6 * s for x in ws], mix(pal["light"], pal["core"], 0.6 * heat), ac)
            front.paste(ly)
    # ---- dark-red ring standing around the fist (the recoil of the shot)
    um = tf / 0.42
    if um < 1:
        am = (1 - smooth(0.3, 1, um))
        rx, ry = (8 + 6 * out_cubic(um)) * s, (40 + 22 * out_cubic(um)) * s
        lb, lf = _layer(back), _layer(front)
        band(lb, X(6), py, rx, ry, 5 * s * (1 - 0.5 * um), pal["back"], am * 0.8, math.pi / 2 + off, 3 * math.pi / 2 + off)
        band(lf, X(6), py, rx, ry, 5 * s * (1 - 0.5 * um), pal["tip"], am, -math.pi / 2 + off, math.pi / 2 + off)
        lf2 = _layer(front)
        band(lf2, X(6) + d * 1.2 * s, py, rx, ry, 1.6 * s * (1 - um), pal["light"], am, -math.pi / 2.4 + off, math.pi / 2.4 + off)
        back.paste(lb); front.paste(lf); front.paste(lf2)
    # ---- dim speed streaks behind the beam
    rng = random.Random(90)
    ly = _layer(back)
    for j in range(7):
        y0, dl, sp, w0 = rng.uniform(-30, 30) * s, rng.uniform(0, 0.06), rng.uniform(900, 1300) * s, rng.uniform(1.2, 2.2) * s
        _tracer(ly, X(20), py + y0, rng.uniform(-0.04, 0.04), sp, tf - dl, 0.42, w0, pal, 0.45, head=False, d=d)
    back.paste(ly)
    # ---- the beam fused with the muzzle flash: one silhouette, white-hot in the thick middle
    ub = tf / 0.38
    if ub < 0.3:
        ly = _layer(front); stepped_glow(ly, X(10), py, 34 * s * (1 - ub / 0.3), pal, 0.75 * (1 - ub / 0.3)); front.paste(ly)
    if ub < 1:
        sh = Shape(front)
        L = 260 * s * out_expo(min(1, ub * 3.0 + 0.4)) * (1 - 0.35 * smooth(0.4, 1, ub))
        base = X(8 + 140 * smooth(0.3, 1, ub) ** 1.3)                     # the beam leaves the fist and runs out
        Wb = 30 * s * (1 - 0.6 * smooth(0.1, 1, ub))
        ang0 = 0 if d > 0 else math.pi
        if L > 2:
            sh.poly(thorn(base, py, ang0, L, Wb, 0.0, p=1.15))
            for sy in (-1, 1):
                sh.poly(thorn(base, py + sy * 4 * s, ang0 + sy * 0.05 * d, L * 0.55, Wb * 0.55, -sy * 0.1 * d, p=2.2))
        uf = tf / 0.26
        if uf < 1:
            mx = X(10)
            sh.poly(blob(mx, py, 15 * s * (1 + 0.3 * uf) * (1 - smooth(0.5, 1, uf)) + 0.5, wob=0.15, freq=5, phase=1))
            A = (lambda deg: math.radians(deg) if d > 0 else math.pi - math.radians(deg))
            jag = [(-24, 66, 12, -0.1, 8), (22, 62, 12, 0.1, 8), (-44, 56, 11, -0.16, 8), (41, 52, 11, 0.16, 8),     # a cone of spikes
                   (-68, 40, 10, -0.22, 7), (70, 36, 10, 0.22, 7), (-96, 26, 9, -0.25, 6), (98, 24, 9, 0.25, 6),
                   (-12, 50, 10, 0.0, 8), (11, 46, 10, 0.0, 8), (-140, 18, 8, -0.2, 5), (142, 16, 8, 0.2, 5), (180, 24, 10, 0.0, 5),
                   (-33, 92, 4, -0.04, 6, 0.01), (34, 84, 4, 0.04, 6, 0.01), (-58, 70, 4, -0.06, 6, 0.017), (57, 74, 4, 0.06, 6, 0.017)]
            thorns_at(sh, mx, py, [(A(a_), L_ * s, W_ * s, b_ * d, r_ * s) + tuple(x[5:]) for x in jag for a_, L_, W_, b_, r_ in [x[:5]]],
                      tf, 0.26, thin_by=0.6, detach=0.45, start=0.85)
        heat = 1 - smooth(0.12, 1, ub)
        bands = [(1.2 * s, pal["light"]), (None, pal["white"])] if first else fire_bands(pal, s, heat)
        sh.paint(bands, 1 - smooth(0.7, 1, ub), fillet=4.0, erode=8 * s * smooth(0.55, 1, ub), noise=4 * s * smooth(0.45, 1, ub), seed=80,
                 backing=(3.5 * s, pal["back"], 0.35 * (1 - smooth(0.3, 0.8, ub))))
    # ---- tracers: the scatter of bright streaks with arrow heads, fanning out a little
    rng = random.Random(91)
    ly = _layer(front)
    for j, (yo, ang) in enumerate(((-20, -0.07), (-12, -0.04), (-5, -0.018), (4, 0.012), (11, 0.035), (19, 0.062), (0, 0.0), (-8, -0.1), (8, 0.09))):
        dl, sp = rng.uniform(0.0, 0.05), rng.uniform(1300, 1650) * s
        _tracer(ly, X(22), py + yo * s, ang, sp, tf - dl, 0.55, (3.4 if j < 6 else 4.4 if j == 6 else 2.4) * s, pal, 1.0, head=j < 7, d=d)
    front.paste(ly)
    # ---- sparks sprayed from the flash, mostly forward
    rng = random.Random(92)
    ly = _layer(front)
    for j in range(22):
        dl = rng.uniform(0, 0.05); ue = tf - dl; life = rng.uniform(0.2, 0.32)
        if not 0 < ue < life: continue
        th = rng.gauss(0, 0.9) if j < 16 else rng.uniform(-math.pi, math.pi)
        sp = rng.uniform(260, 560) * s
        x, y, vx, vy = drag_pos(X(14), py, d * math.cos(th) * sp, math.sin(th) * sp, ue, k=6, g=60 * s)
        spark(ly, x, y, vx, vy, rng.uniform(6, 13) * s, rng.uniform(1.6, 2.6) * s, pal["light"] if j % 3 else pal["core"], 1 - ue / life, core=pal["white"])
    front.paste(ly)
    # ---- embers peeling off the ring ends, rising as they cool
    lf, lb = _layer(front), _layer(back)
    for k in range(4):
        rng = random.Random(100 + k)
        for j in range(7):
            ub_ = rng.uniform(0.12, 0.55)
            tb = T_FIRE + INF_TIERS[k][0] + ub_ * INF_TIERS[k][6]
            ue = t - tb; life = rng.uniform(0.22, 0.34)
            if not 0 < ue < life: continue
            st, arcs = _tier_arcs(k, tb, s, d, P)
            if not st or not arcs: continue
            th0, th1, hook, near = arcs[j % len(arcs)]
            th = th1 if j % 2 else th0
            x0p, y0p = _ring_pt(st[1], py, st[2], th, d)
            out = math.atan2(y0p - py, (x0p - st[1]) * 2.0)
            sp = rng.uniform(90, 190) * s
            x, y, vx, vy = drag_pos(x0p, y0p, math.cos(out) * sp + d * 70 * s, math.sin(out) * sp, ue, k=3.5, g=-70 * s)
            spark(lf if near else lb, x, y, vx, vy, 7 * s, 2.2 * s, pal["light"] if j % 2 else pal["body"], (1 - ue / life) * (1 if near else 0.6), core=pal["core"])
    front.paste(lf); back.paste(lb)


def _tracer(c, x0, y0, ang, sp, u, life, w, pal, a, head=True, d=1):
    """A streak shot from (x0, y0) at angle ang (radians off the axis): fast with a little drag, its tail catching up as it fades."""
    if u <= 0 or u >= life: return
    k = 2.0
    dist = sp * (1 - math.exp(-k * u)) / k
    tail_len = min(dist, (300 - 230 * smooth(0.3, 1, u / life)) * w / 3.4)
    ca, sa = math.cos(ang), math.sin(ang)
    hx, hy = x0 + d * dist * ca, y0 + dist * sa
    tx, ty = x0 + d * (dist - tail_len) * ca, y0 + (dist - tail_len) * sa
    al = a * smooth(0, 0.05, u / life) * (1 - smooth(0.55, 1, u / life))
    if al <= 0.003: return
    nx, ny = -sa, d * ca
    ww = w * (1 - 0.4 * u / life)
    c.poly([(tx, ty), (hx + nx * ww / 2, hy + ny * ww / 2), (hx - nx * ww / 2, hy - ny * ww / 2)], pal["body"], al)
    c.poly([(tx + (hx - tx) * 0.3, ty + (hy - ty) * 0.3), (hx + nx * ww / 5, hy + ny * ww / 5), (hx - nx * ww / 5, hy - ny * ww / 5)], pal["light"], al)
    if head:
        L, Wh = 5.5 * ww, 2.4 * ww
        bx, by = hx - d * ca * L * 0.35, hy - sa * L * 0.35
        lens(c, (bx, by), (hx + d * ca * L * 0.65, hy + sa * L * 0.65), Wh, pal["light"], al, n=10)
        lens(c, (bx + d * ca * L * 0.15, by + sa * L * 0.15), (hx + d * ca * L * 0.55, hy + sa * L * 0.55), Wh * 0.5, pal["white"], al, n=10)


VARIANTS = {"tiers": shock_tiers, "vapor": shock_vapor, "drill": shock_drill, "shatter": shock_shatter, "bloom": shock_bloom,
            "inferno": shock_inferno}
