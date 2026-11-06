"""lib-fx / magic / spirit: soul magic. Spirit flames that leave a body, fly, possess and burn a target.

Each design is  fn(t, P, front, back, pal=SOUL, s=1.0, d=1)  drawing the skill t seconds after the cast:
  P      the caster's chest (canvas px); the target stands TARGET_DX px ahead along +x (d=1) or -x (d=-1), on the ground
         GROUND px below the chest; the target is a generic dummy about 110 px tall
  front  / back  layers over / behind the characters
  s      size (1.0 = sized for heroes 120 px tall @2x)
Designed against DESIGN.md §10: every spirit has its own size class, path, pace, tail and fate; every layer differs from the
others in size, shape, speed, edge and opacity.
"""
import math, random
from fxcore import Canvas, mix, clamp, smooth, out_cubic, out_back, lens, ribbon, drag_pos, stepped_glow, spark
from organic import Shape, thorn, shard, blob, shade, flame, flame_point, ring_halves, noise_field
from palettes import SPIRIT
from PIL import Image, ImageDraw
import numpy as np

DUR = 1.45
FRAME, ANCHOR, FPS = (720, 420), (150, 240), 30
TARGET_DX, GROUND = 340, 62
TAGS = ["magic", "spirit", "one-shot", "directional", "anchor:caster", "target:+340,+62"]
SOUL = SPIRIT                                                             # _core/palettes.py; any palette with the same keys works
PAL_SUN = SOUL
CATALOG = {
    "soulstrike": dict(name="Xuất hồn kích", status="draft", tags=["heavy", "homing", "spirit", "organic", "ground"],
                       glow=(110, 196, 255), halo=(0.5, 10),
                       desc="spirit flames are born at the caster's chest, swell and leap out in many directions; six spirits of three "
                            "sizes each take their own path (a high arc and a steep dive, a low skim that hooks back, a corkscrew, a "
                            "zigzag that hits the ground first, a lazy one that fizzles out, one that circles the caster first) and "
                            "strike the target one after another; the big dive bursts on the head, spreads a wave of cyan ground fire "
                            "with lilac tips and covers the target in a ghost silhouette; purple wisps and motes rise as it all fades. The target "
                            "stands 340 px ahead of the anchor on the ground (+62 px); the ghost is drawn on a generic dummy mask "
                            "(no dummy body is drawn)"),
}


# ---------------------------------------------------------------- helpers
def soul_bands(pal, s=1.0, heat=1.0):
    """Edge -> centre: deep blue rim, blue, cyan, pale, white core; cooling drops the white then the pale."""
    cols = [pal["deep"], pal["blue"], pal["cyan"], pal["pale"], pal["white"]]
    lims = [1.3, 3.0, 5.8, 8.8]
    top = 2 + int(round(2 * clamp(heat)))
    return [(lims[i] * s, cols[i]) for i in range(top)] + [(None, cols[top])]


def lilac_bands(pal, s=1.0):
    return [(1.4 * s, pal["violet"]), (None, pal["lilac"])]


def _layer(c): return Canvas(c.w, c.h, c.ss)


def _cr(pts, u):
    """A point on an open Catmull-Rom path through pts, u in 0..1."""
    n = len(pts) - 1
    f = clamp(u) * n
    i = min(n - 1, int(f)); v = f - i
    p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(n, i + 2)]
    v2, v3 = v * v, v * v * v
    return tuple(0.5 * (2 * b + (-a + c) * v + (2 * a - 5 * b + 4 * c - e) * v2 + (-a + 3 * b - 3 * c + e) * v3) for a, b, c, e in zip(p0, p1, p2, p3))


def _ellipse(cx, cy, rx, ry, ang, wob=0.0, phase=0.0, n=36):
    ca, sa = math.cos(ang), math.sin(ang)
    out = []
    for k in range(n):
        th = 2 * math.pi * k / n
        r = 1 + wob * math.sin(3 * th + phase)
        x, y = rx * r * math.cos(th), ry * r * math.sin(th)
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


# ---------------------------------------------------------------- the six spirits (local px: caster chest at 0,0, y down)
TX, TH = TARGET_DX, GROUND
HEAD, TORSO, BASE = (TX, GROUND - 104), (TX, GROUND - 62), (TX, GROUND)
def hover(f, out=0.3, hold=0.14, drift=0.04, pw=1.7):
    """Time warp for a spirit: burst out to the fan-out point (path parameter f) by `out`, hang there drifting for `hold`,
    then turn and accelerate onto the target. Each spirit gets its own numbers."""
    def e(u):
        if u < out: return f * out_cubic(u / out)
        if u < out + hold: return f + drift * (u - out) / hold
        v = (u - out - hold) / (1 - out - hold)
        return f + drift + (1 - f - drift) * v ** pw
    return e


# r: head radius; spawn/launch/end: s; path: waypoints; ease; tail: seconds of history; wig: (amplitude, cycles/s); fate
SPIRITS = [
    # the hero: bursts up, hangs high over the field, then dives steeply onto the head (the climax)
    dict(name="hero", r=24, spawn=0.02, launch=0.12, end=0.74, tail=0.13, wig=(8, 2.0), drips=True, flicks=3, tear=0.0, tailw=0.85, strands=1, phase=0.4,
         path=[(-4, -16), (26, -92), (120, -156), (236, -172), (318, -132), HEAD],
         ease=hover(0.4, out=0.32, hold=0.16, drift=0.05, pw=2.0), fate="dive"),
    # skims low past the target, hooks back and hits the torso from behind
    dict(name="skim", r=14, spawn=0.0, launch=0.06, end=0.6, tail=0.1, wig=(5, 3.2), drips=False, flicks=2, tear=0.3, tailw=0.85, strands=1, phase=2.1,
         path=[(8, -2), (92, 22), (170, 40), (296, 44), (388, 18), (394, -22), (360, -10), TORSO],
         ease=hover(2 / 7, out=0.26, hold=0.1, drift=0.03, pw=1.3), fate="split"),
    # rises, turns one corkscrew loop, then lands on the head
    dict(name="corkscrew", r=13, spawn=0.02, launch=0.1, end=0.68, tail=0.12, wig=(4, 1.6), drips=False, flicks=2, tear=0.2, tailw=0.8, strands=2, phase=4.0,
         path=[(4, -22), (64, -84), (118, -98), (150, -66), (118, -40), (98, -80), (160, -108), (268, -92), HEAD],
         ease=hover(1 / 8, out=0.22, hold=0.08, drift=0.02, pw=1.15), fate="ring"),
    # small and nervous: zigzags low and hits the ground first, ahead of the target
    dict(name="zigzag", r=9, spawn=0.05, launch=0.12, end=0.46, tail=0.09, wig=(3, 5.0), drips=False, flicks=0, tear=0.95, tailw=0.5, strands=1, phase=1.3,
         path=[(10, 8), (70, 40), (130, 20), (190, 52), (250, 32), (300, GROUND)],
         ease=lambda u: u, fate="ground"),
    # small and lazy: floats up and back over the caster and fizzles out, never arrives
    dict(name="lazy", r=8.5, spawn=0.06, launch=0.18, end=0.6, tail=0.16, wig=(7, 1.1), drips=False, flicks=0, tear=0.5, tailw=0.6, strands=1, phase=5.2,
         path=[(-4, -28), (-34, -84), (14, -134), (86, -146)],
         ease=lambda u: math.sin(u * math.pi / 2), fate="fizzle"),
    # small: circles the caster once, then darts in last, into the burning ghost
    dict(name="orbit", r=9, spawn=0.09, launch=0.18, end=0.88, tail=0.12, wig=(3, 2.8), drips=False, flicks=1, tear=0.9, tailw=0.45, strands=1, phase=3.3,
         path=[(0, -6), (42, -38), (4, -74), (-44, -40), (-12, 12), (58, -8), (200, -62), (296, -64), (TX - 4, GROUND - 92)],
         ease=lambda u: u ** 1.2, fate="flare"),
]
T_HIT = SPIRITS[0]["end"]


def _pos(sp, t):
    """Where a spirit's head is at time t (local px), and how grown it is (0..1)."""
    p0 = sp["path"][0]
    if t < sp["launch"]:
        g = out_back(clamp((t - sp["spawn"]) / (sp["launch"] - sp["spawn"])), 2.0)
        k = clamp((t - sp["spawn"]) / (sp["launch"] - sp["spawn"]))
        return (p0[0] + 3 * math.sin(40 * t), p0[1] - 6 * k), g        # grows on the body, trembling, rising a little
    u = (t - sp["launch"]) / (sp["end"] - sp["launch"])
    return _cr(sp["path"], sp["ease"](clamp(u))), 1.0


# ---------------------------------------------------------------- the effect
def spirit_soulstrike(t, P, front, back, pal=SOUL, s=1.0, d=1):
    pal = dict(pal)                                                       # a 5-step palette works too: the extra steps are derived
    for k, src in (("deep", "rim"), ("blue", "body"), ("cyan", "light"), ("pale", "core")): pal.setdefault(k, pal[src])
    pal.setdefault("violet", mix(pal["rim"], pal["body"], 0.3)); pal.setdefault("lilac", mix(pal["body"], pal["core"], 0.45))
    pal.setdefault("dark", mix(pal["rim"], (0, 0, 0), 0.5))
    L = lambda x, y: (P[0] + d * x * s, P[1] + y * s)                    # local px -> canvas
    A = lambda a: a if d > 0 else math.pi - a                           # an angle drawn for +x, mirrored
    gy = P[1] + GROUND * s

    # ======================================== 1. caster: a soft flare at the chest and short crackles (sharp, very fast)
    if t < 0.32:
        a = smooth(0, 0.04, t) * (1 - smooth(0.12, 0.32, t))
        ly = _layer(back); stepped_glow(ly, *L(2, -10), 34 * s * (0.6 + 0.4 * smooth(0, 0.1, t)), pal, a * 0.8); back.paste(ly)
        ly = _layer(front)
        rng = random.Random(3)
        for j in range(6):
            tb = rng.uniform(0.0, 0.14); u = (t - tb) / 0.07
            if not 0 <= u < 1: continue
            ang = rng.uniform(-2.6, 0.9); r0, r1 = 10 + 26 * u, 22 + 30 * u
            pts = [L(math.cos(ang) * (r0 + (r1 - r0) * k / 3) + (4 if k % 2 else -4) * math.sin(ang), math.sin(ang) * (r0 + (r1 - r0) * k / 3) - 10) for k in range(4)]
            ribbon(ly, pts, [1.8 * s] * 4, pal["pale"], 1 - u)
        front.paste(ly)

    # ======================================== 2. ground pool: a broad, slow, soft glow under the target (behind everything)
    if t > T_HIT - 0.02:
        u = (t - T_HIT + 0.02) / (DUR - T_HIT)
        a = smooth(0, 0.08, u) * (1 - smooth(0.55, 1, u))
        ly = _layer(back)
        bx, by = L(*BASE)
        for k, al in ((1.0, 0.16), (0.7, 0.22), (0.42, 0.3)):
            rx = (60 + 110 * out_cubic(min(1, u * 2.5))) * k * s
            ly.ellipse(bx, by - 2 * s, rx, rx * 0.11, pal["cyan"], a * al)
        back.paste(ly)

    # ======================================== 3. the spirits (tails behind, heads on top), each with its own fate
    events = {}
    for sp in SPIRITS:
        if t < sp["spawn"]: continue
        _spirit(t, sp, L, A, d, s, pal, front, back, events)

    # ======================================== 4. the hits: each different
    _hit_split(t, L, A, d, s, pal, front)
    _hit_ring(t, L, d, s, pal, front)
    _hit_ground(t, L, A, d, s, pal, front)
    _hit_dive(t, L, A, d, s, pal, front, back)
    _ground_fire(t, L, A, d, s, pal, front, back)
    _possession(t, L, A, d, s, pal, front, back)
    _hit_flare(t, L, A, d, s, pal, front)
    _wisps(t, L, d, s, pal, front)
    _motes(t, L, d, s, pal, front)


def _tail_paint(c, pts, ws, cols, alphas, seed=0, erode=0.0):
    """A tail as ONE mask: every segment is stamped with its index (head segments last, so they win), then the index is mapped to
    a colour and alpha; the whole tail is composited once (no seams where segments overlap, no holes where a corkscrew crosses)."""
    n = len(pts) - 1
    if n < 1: return
    ss = c.ss
    idx = Image.new("L", c.img.size, 0)
    dr = ImageDraw.Draw(idx)
    for k in range(n - 1, -1, -1):
        poly = _tail_poly([pts[k], pts[k + 1]], [ws[k], ws[k + 1]])
        dr.polygon([(x * ss, y * ss) for x, y in poly], fill=k + 1)
        r = ws[k] / 2 * ss
        if r > 0.5: dr.ellipse([pts[k][0] * ss - r, pts[k][1] * ss - r, pts[k][0] * ss + r, pts[k][1] * ss + r], fill=k + 1)
    bb = idx.getbbox()
    if bb is None: return
    a = np.asarray(idx.crop(bb))
    if erode > 0:                                                         # a tail breaking up: noisy holes, more towards its end
        nz = noise_field(idx.size[::-1], seed, 4 * ss)[bb[1]:bb[3], bb[0]:bb[2]]
        a = np.where((a > 0) & (nz * 0.5 + 0.5 < erode * (0.3 + 0.7 * a / max(1, n))), 0, a)
    lut_rgb = np.zeros((256, 3), np.uint8); lut_a = np.zeros(256, np.uint8)
    for k in range(n):
        lut_rgb[k + 1] = cols[k]; lut_a[k + 1] = int(255 * clamp(alphas[k]))
    img = Image.fromarray(np.dstack([lut_rgb[a], lut_a[a]]), "RGBA")
    c.img.alpha_composite(img, (bb[0], bb[1]))


def _heading(sp, t):
    """Smoothed direction and speed of a spirit (over 40 ms), so a hook-back or an orbit never flips the head in one frame."""
    p, _ = _pos(sp, t); q, _ = _pos(sp, t - 0.04)
    vx, vy = p[0] - q[0], p[1] - q[1]
    return vx, vy, math.hypot(vx, vy) / 0.04


TAIL_PX = {"hero": 160, "skim": 110, "corkscrew": 100, "zigzag": 46, "lazy": 96, "orbit": 58}


def _tail_time(sp, t):
    """How far back in time the tail reaches: until it is TAIL_PX long along the path (so a hovering spirit still trails a
    long tail), never less than sp["tail"] s and never before the spirit was born."""
    want, acc, tk = TAIL_PX[sp["name"]], 0.0, t
    p0, _ = _pos(sp, t)
    while tk - 0.01 > sp["spawn"] and tk > t - 0.6:
        tk -= 0.01
        p1, _ = _pos(sp, tk)
        acc += math.hypot(p1[0] - p0[0], p1[1] - p0[1]); p0 = p1
        if acc >= want: break
    return max(min(sp["tail"], t - sp["spawn"]), t - tk)


def _spirit(t, sp, L, A, d, s, pal, front, back, events):
    r, fate = sp["r"] * s, sp["fate"]
    if t >= sp["end"]: return
    head, g = _pos(sp, t)
    shrink = 1.0
    if fate == "fizzle":                                                  # loses its shape in the last third and comes apart
        u = (t - sp["launch"]) / (sp["end"] - sp["launch"])
        shrink = 1 - smooth(0.55, 1.0, u)
        if shrink <= 0.02: return
    # the orbiting spirit passes behind the caster on the far side of its loop
    c = back if (sp["name"] == "orbit" and head[0] < -6 and t < sp["end"] * 0.6) else front
    # ---- tail: the head's past positions, a wave travelling down it, one or two strands
    N = 22
    dt = _tail_time(sp, t) / N
    amp, freq = sp["wig"]
    dive = smooth(0.55, 1.0, (t - sp["launch"]) / (sp["end"] - sp["launch"])) if fate == "dive" else 0.0
    pts0, ws0 = [L(*head)] * 3, [2 * r * g] * 3
    for strand in range(sp["strands"]):
        off = 0.0 if sp["strands"] == 1 else (strand - 0.5) * 0.9
        pts, ws = [], []
        for k in range(N + 1):
            tk = t - k * dt
            if tk < sp["spawn"]: break
            p, gk = _pos(sp, tk)
            vx, vy, _ = _heading(sp, tk)
            vl = math.hypot(vx, vy) or 1
            ph = sp["phase"] + strand * math.pi
            w = amp * math.sin(2 * math.pi * freq * tk + ph) * (k / N) ** 0.8 + off * r / s * (k / N) ** 0.6 * 1.6
            pts.append(L(p[0] - vy / vl * w, p[1] + vx / vl * w))
            ws.append(2 * r * 1.05 * gk * shrink * sp["tailw"] * (0.6 if sp["strands"] > 1 else 1) * (1 - k / N) ** 0.85)
        if len(pts) < 3: continue
        n = len(pts) - 1
        cols, als = [], []
        for k in range(n):
            v = k / N
            col = mix(pal["cyan"], pal["blue"], smooth(0.0, 0.4, v)) if v < 0.4 else mix(pal["blue"], pal["violet"], smooth(0.4, 0.7, v)) if v < 0.7 else mix(pal["violet"], pal["lilac"], smooth(0.7, 1, v))
            if dive: col = mix(col, pal["lilac"], dive * smooth(0.1, 0.5, v))
            cols.append(col); als.append((1.0 - 0.7 * v) * (0.4 + 0.6 * shrink))
        ly = _layer(c)
        _tail_paint(ly, pts, ws, cols, als, seed=11 + strand, erode=0.75 * dive + (0.35 if sp["name"] == "skim" else 0.0))
        # curls peeling off the hero's tail
        if sp["name"] == "hero" and n > 12:
            for kk, side in ((int(n * 0.35), 1), (int(n * 0.62), -1)):
                x0, y0 = pts[kk]; x1, y1 = pts[kk + 1]
                ang = math.atan2(y0 - y1, x0 - x1) + side * 0.9
                ly.poly(thorn(x0, y0, ang, 14 * s, 5.5 * s, -side * 1.4, p=1.3), pal["violet"] if kk > n // 2 else pal["blue"], 0.85)
        c.paste(ly)
        if strand == 0: pts0, ws0 = pts, ws
    # ---- head: its own proportions (round and heavy, or a teardrop), squash and stretch from the smoothed speed, own flick count
    hx, hy = L(*head)
    vx, vy, spd = _heading(sp, t)
    ang = math.atan2(vy, vx * d) if (spd > 20 and t >= sp["launch"]) else -math.pi / 2     # pointing up while it grows
    stretch = min(0.5, spd / 1500)
    rr = r * g * shrink
    tear = sp["tear"]
    sh = Shape(c)
    sh.poly(_ellipse(hx, hy, rr * (1 + stretch + 0.15 * tear), rr * (1 - 0.3 * stretch - 0.12 * tear), ang, 0.05, 7 * t))
    if tear > 0:                                                          # teardrop: the back of the head runs into a point
        sh.poly(thorn(hx - math.cos(ang) * rr * 0.4, hy - math.sin(ang) * rr * 0.4, ang + math.pi, rr * (1.2 + 1.6 * tear), rr * 1.6, 0.0, p=1.2))
    up = 1 if math.cos(ang) >= 0 else -1                                  # flicks stand on the upper back of the head
    for j in range(sp["flicks"]):                                         # flicks on the upper back of the head, each a different size
        fa = ang + math.pi + up * (0.65 + 0.55 * j)
        Lk = (1.45, 1.0, 0.6)[j]
        sh.poly(flame(hx + math.cos(fa) * rr * 0.6, hy + math.sin(fa) * rr * 0.6, fa, rr * 1.2 * Lk, rr * (0.8 - 0.1 * j), -0.9 * up, 0.25, p=1.0))
    sh.poly(thorn(hx - math.cos(ang) * rr * 0.5, hy - math.sin(ang) * rr * 0.5, math.atan2(pts0[min(3, len(pts0) - 1)][1] - hy,
                  pts0[min(3, len(pts0) - 1)][0] - hx), rr * 1.6, rr * 1.5, 0.0, p=1.0))          # the neck into the tail
    tones = dict(shadow=pal["deep"], base=pal["cyan"], light=pal["pale"])
    shade(sh, tones, 1.0, light=(0.15, 0.98), off=max(1.5, rr * 0.28), fillet=2.0)   # lit from above: pale top, deep-blue belly
    if sp["name"] in ("skim", "corkscrew"):                                # a hot point only in the two medium heads
        ly = _layer(c); ly.ellipse(hx + math.cos(ang) * rr * 0.25, hy + math.sin(ang) * rr * 0.25 - rr * 0.2, rr * 0.32, rr * 0.24, pal["white"], 0.9)
        c.paste(ly)
    # ---- drips falling off the hero's tail (only the hero: heavy and slow)
    if sp["drips"]:
        ly = _layer(front)
        for j in range(5):
            tb = sp["launch"] + 0.06 + j * 0.09
            u = (t - tb) / 0.3
            if not 0 <= u < 1 or tb > sp["end"]: continue
            p, _ = _pos(sp, tb - sp["tail"] * (0.4 + 0.12 * (j % 3)))
            x, y = L(p[0], p[1] + 30 * u * u + 8 * u)
            sz = (2.8 - 0.5 * (j % 2)) * s * (1 - u)
            ly.poly(shard(x, y, math.pi / 2, sz * 3, sz * 1.6), pal["violet"] if j % 2 else pal["blue"], 0.85 * (1 - u))
        front.paste(ly)


def _tail_poly(pts, ws):
    L_, R_ = [], []
    for k, (x, y) in enumerate(pts):
        p, q = pts[max(0, k - 1)], pts[min(len(pts) - 1, k + 1)]
        dx, dy = q[0] - p[0], q[1] - p[1]; l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        L_.append((x + nx * ws[k] / 2, y + ny * ws[k] / 2)); R_.append((x - nx * ws[k] / 2, y - ny * ws[k] / 2))
    return L_ + R_[::-1]


# ---------------------------------------------------------------- hits: liquid soul-fire, rounded, never spiky
def _drops(sh, cx, cy, drops, u, life, d, s, g=420.0):
    """Round-headed droplets flung out of a splash (angle, speed, size): drag + gravity, shrinking to nothing."""
    for ang, sp, sz in drops:
        a = ang if d > 0 else math.pi - ang
        x, y, vx, vy = drag_pos(cx, cy, math.cos(a) * sp * s, math.sin(a) * sp * s, u * life, k=3.0, g=g * s)
        k = 1 - smooth(0.45, 1, u)
        if k > 0.05:
            sh.poly(shard(x, y, math.atan2(vy, vx), sz * s * 2.4 * k, sz * s * k, 0.0))


def _hit_split(t, L, A, d, s, pal, front):
    """The skimming spirit hooks into the torso from behind: a curved sheet splashes back the way it came, drops scatter."""
    sp = SPIRITS[1]; u = (t - sp["end"]) / 0.28
    if not 0 <= u < 1: return
    cx, cy = L(*TORSO)
    sh = Shape(front)
    e = out_cubic(min(1, u * 1.6))
    for deg, Ln, W, b in ((-150, 34, 18, -0.9), (160, 26, 14, 0.8)):        # the sheet: two rounded licks curling back
        a0 = A(math.radians(deg))
        sh.poly(flame(cx + math.cos(a0) * 6 * s, cy + math.sin(a0) * 6 * s, a0, Ln * s * (0.5 + 0.6 * e), W * s * (1 - 0.5 * u), b * d, 0.2 * d, p=0.85))
    _drops(sh, cx, cy, [(math.radians(-150), 260, 4.5), (math.radians(-125), 200, 3.5), (math.radians(175), 230, 3.0),
                        (math.radians(-100), 150, 2.6), (math.radians(150), 120, 4.0)], u, 0.28, d, s)
    sh.paint(soul_bands(pal, s, 0.9 - 0.7 * u), 1.0, fillet=2.5, erode=6 * s * smooth(0.5, 1, u), noise=4 * s * smooth(0.3, 1, u), seed=5)


def _hit_ring(t, L, d, s, pal, front):
    """The corkscrew spirit lands on the head: a thin tilted ring flies out and three specks."""
    sp = SPIRITS[2]; u = (t - sp["end"]) / 0.26
    if not 0 <= u < 1: return
    cx, cy = L(*HEAD)
    sh = Shape(front)
    rr = (12 + 40 * out_cubic(u)) * s
    for half in ring_halves(cx, cy, rr * 0.42, rr, 5 * s * (1 - u) + 1 * s, taper=0.5): sh.poly(half)
    sh.paint([(1.4 * s, pal["blue"]), (None, pal["pale"])], 1 - smooth(0.5, 1, u), fillet=0)
    ly = _layer(front)
    for k, ang in enumerate((-1.2, -0.3, 0.6)):
        x, y, vx, vy = drag_pos(cx, cy, math.cos(ang) * 220 * s * d, math.sin(ang) * 220 * s, u * 0.26, k=5)
        ly.ellipse(x, y, 2.6 * s * (1 - u), 2.6 * s * (1 - u), pal["white"], 1 - u)
    front.paste(ly)


def _hit_ground(t, L, A, d, s, pal, front):
    """The zigzag spirit hits the floor ahead of the target: two low waves roll apart along the ground, a few drops hop up."""
    sp = SPIRITS[3]; u = (t - sp["end"]) / 0.34
    if not 0 <= u < 1: return
    cx, cy = L(*sp["path"][-1])
    sh = Shape(front)
    e = out_cubic(min(1, u * 1.5))
    for side, Ln in ((1, 40), (-1, 30)):
        x0 = cx + side * d * 26 * s * e
        a0 = A(math.radians(-14)) if side > 0 else A(math.radians(-166))
        sh.poly(flame(x0 - side * d * 12 * s, cy + 2 * s, a0, Ln * s * (0.5 + 0.5 * e), 14 * s * (1 - 0.5 * u), -side * d * 2.2, 0.0, p=0.9))
    _drops(sh, cx, cy - 4 * s, [(math.radians(-110), 200, 3.2), (math.radians(-70), 170, 2.6), (math.radians(-90), 240, 2.2)], u, 0.34, d, s, g=900)
    sh.paint(soul_bands(pal, s, 0.8 - 0.8 * u), 1.0, fillet=2.5, erode=6 * s * smooth(0.5, 1, u), noise=4 * s * u, seed=8)


def _hit_dive(t, L, A, d, s, pal, front, back):
    """The big dive: the only white flash (two drawings), a crown of rounded flames bursting off the head and breaking into drops,
    a flat ring on the floor, sparks thrown up and falling."""
    u = (t - T_HIT) / 0.4
    if not 0 <= u < 1: return
    cx, cy = L(*HEAD)
    if t - T_HIT < 2 / 30:
        ly = _layer(front); stepped_glow(ly, cx, cy, 60 * s, pal, 1.0 - 0.4 * (t - T_HIT) * 15); front.paste(ly)
    sh = Shape(front)
    crown = [(-168, 34, 16, -0.6), (-118, 22, 12, -0.4), (-24, 40, 18, 0.6), (28, 30, 14, 0.8), (150, 26, 13, -0.8)]   # wraps the head
    for k, (deg, Ln, W, b) in enumerate(crown):                         # big stretched drops: round heads out, tails to the centre
        a0 = A(math.radians(deg))
        e = out_cubic(min(1, u * 2.2))
        r0 = (14 + Ln * 0.9 * e) * s
        sz = 1 - smooth(0.45, 1, u)
        hx_, hy_ = cx + math.cos(a0) * r0, cy + math.sin(a0) * r0 + 60 * s * smooth(0.3, 1, u) ** 2
        sh.poly(shard(hx_, hy_, a0 + b * d * 0.3 * u, (r0 - 8 * s) * (0.5 + 0.5 * (1 - e * 0.6)) * sz + 4 * s, W * s * (0.45 + 0.55 * sz), b * d * 0.4))
    sh.poly(_ellipse(cx, cy - 6 * s, 20 * s * (1 + 0.5 * u), 12 * s * (1 - 0.4 * u), 0.0, 0.1, 2))     # the spirit flattens over the head
    _drops(sh, cx, cy, [(math.radians(a), sp, sz) for a, sp, sz in ((-160, 300, 5), (-135, 240, 4), (-100, 330, 3.5), (-70, 280, 4.5),
                                                                      (-40, 250, 3), (-12, 200, 4), (20, 160, 3), (190, 180, 3.5))], u, 0.4, d, s, g=520)
    bands = soul_bands(pal, s, 1 - u)
    sh.paint(bands, 1.0, fillet=3.0, erode=8 * s * smooth(0.55, 1, u), noise=6 * s * smooth(0.3, 1, u), seed=13,
             backing=(2.5 * s, pal["dark"], 0.25 * (1 - u)))
    # a flat ring racing out on the floor
    ur = (t - T_HIT - 0.03) / 0.3
    if 0 <= ur < 1:
        bx, by = L(*BASE)
        ly = _layer(back)
        rx = (20 + 150 * out_cubic(ur)) * s
        for half in ring_halves(bx, by, rx, rx * 0.1, 3.5 * s * (1 - ur) + 0.8 * s):
            ly.poly(half, pal["pale"], 0.9 * (1 - ur))
        back.paste(ly)
    # sparks thrown up and falling (fast, ballistic: unlike the floating motes)
    ly = _layer(front)
    rng = random.Random(21)
    for j in range(12):
        tb = T_HIT + rng.uniform(0, 0.04); life = rng.uniform(0.3, 0.55)
        ue = t - tb
        if not 0 < ue < life: continue
        ang = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
        sp_ = rng.uniform(180, 420) * s
        x, y, vx, vy = drag_pos(cx, cy, math.cos(ang) * sp_ * d, math.sin(ang) * sp_, ue, k=2.5, g=700 * s)
        spark(ly, x, y, vx, vy, rng.uniform(5, 11) * s, rng.uniform(1.4, 2.4) * s, pal["pale"] if j % 3 else pal["cyan"], 1 - ue / life, core=pal["white"])
    front.paste(ly)


# ---------------------------------------------------------------- ground fire: soul flame rolling out from the target's feet
# Hand-placed, clustered (a tall centre, two side clusters, strays, gaps) and of three kinds:
#   tall   a standing tongue that curls outward, cyan with a lilac tip
#   crest  a low rolling wave: long, flat, its front curling up and over like water
#   flick  a small quick flame that flickers on and off
# (offset from the target base, kind, height, width, lean outward, fate, life)
FIRE = [(-8, "tall", 92, 36, 0.10, "detach", 0.62), (18, "tall", 66, 28, 0.30, "curl", 0.56), (-38, "crest", 34, 66, 0.0, "sink", 0.6),
        (44, "crest", 30, 60, 0.0, "detach", 0.66), (2, "flick", 24, 14, 0.2, "sink", 0.4),
        (-84, "tall", 54, 26, 0.55, "curl", 0.5), (-102, "flick", 20, 12, 0.4, "sink", 0.36), (-122, "crest", 22, 50, 0.0, "sink", 0.5),
        (86, "tall", 46, 24, 0.6, "detach", 0.58), (106, "crest", 26, 54, 0.0, "curl", 0.52),
        (-158, "flick", 16, 10, 0.5, "sink", 0.32), (150, "flick", 14, 9, 0.6, "sink", 0.3)]
EARLY = [(-36, "tall", 34, 18, 0.5, "sink", 0.42, SPIRITS[3]["end"] + 0.04), (-62, "crest", 20, 40, 0.0, "sink", 0.44, SPIRITS[3]["end"] + 0.06),
         (-8, "flick", 16, 10, 0.4, "sink", 0.32, SPIRITS[1]["end"] + 0.12), (18, "tall", 22, 13, 0.6, "curl", 0.34, SPIRITS[1]["end"] + 0.14)]
FIRE_R, FIRE_T = 160, 0.32                                                # the front reaches FIRE_R px in FIRE_T s, slowing down


def _ground_fire(t, L, A, d, s, pal, front, back):
    def arrive(dx): return FIRE_T * (1 - (1 - min(0.999, abs(dx) / FIRE_R)) ** (1 / 3))     # inverse of out_cubic
    tongues = [(dx, kind, h, w, lean, fate, life, T_HIT + 0.03 + arrive(dx)) for dx, kind, h, w, lean, fate, life in FIRE] + list(EARLY)
    # the bed: one continuous low strip of flame along the floor, its top rolling in waves that run outward; it grows with the
    # front, then sinks and breaks up. It ties every tongue together (the tongues are separate silhouettes on top of it).
    ub = (t - T_HIT - 0.02) / (DUR - T_HIT - 0.02)
    if 0 <= ub < 1:
        R = (FIRE_R * out_cubic(min(1, ub / (FIRE_T / (DUR - T_HIT)))) + 8) * (1 - 0.7 * smooth(0.5, 1, ub))   # the bed pulls in to the feet
        n = 48
        xs = [-R + 2 * R * i / n for i in range(n + 1)]
        def hgt(x):
            env = math.sin(math.pi * clamp((x + R) / (2 * R))) ** 0.6
            wav = abs(math.sin(abs(x) * 0.07 - 22 * t)) * (0.6 + 0.4 * math.sin(abs(x) * 0.03 + 1.3))
            return (5 + 24 * wav ** 1.5) * env * (1 - smooth(0.45, 1, ub))
        top = [L(TX + x, GROUND - hgt(x)) for x in xs]
        bot = [L(TX + x, GROUND + 3) for x in xs[::-1]]
        sh = Shape(front)
        sh.poly(top + bot)
        sh.paint(soul_bands(pal, s, 0.45 * (1 - ub)), 0.95, fillet=2.5, erode=3 * s * smooth(0.7, 1, ub), noise=3 * s * smooth(0.6, 1, ub), seed=29)
    for k, (dx, kind, h, w, lean, fate, life, tb) in enumerate(tongues):
        u = (t - tb) / life
        if not 0 <= u < 1: continue
        side = 1 if dx >= 0 else -1
        bx, by = L(TX + dx, GROUND)
        c = back if (kind == "crest" and k % 2) else front                 # some crests roll behind the target's feet
        if kind == "crest":
            # a low wave: the body runs along the floor outward, its front lifts and curls back over
            ext = out_cubic(min(1, u / 0.35))
            Lw = w * s * (0.4 + 0.6 * ext)
            Hh = h * s * (0.5 + 0.5 * out_back(min(1, u / 0.3), 2)) * (1 - (smooth(0.5, 1, u) if fate == "sink" else 0.3 * smooth(0.6, 1, u)))
            if Hh < 2: continue
            ang = A(math.radians(-18)) if side > 0 else A(math.radians(-162))
            sh = Shape(c)
            sh.poly(flame(bx - side * d * Lw * 0.3, by + 2 * s, ang, Lw, Hh, -side * d * 2.4 * (0.6 + 0.4 * ext), 0.0, p=0.9))
            sh.poly(_ellipse(bx, by, Lw * 0.6, 3 * s, 0.0))
            sh.paint(soul_bands(pal, s, 0.55 * (1 - u)), 1.0, fillet=2.5, erode=7 * s * smooth(0.4, 1, u), noise=9 * s * smooth(0.25, 1, u), seed=31 + k % 3)   # crests foam apart
            continue
        rise = out_back(min(1, u / (0.22 if kind == "tall" else 0.1)), 2.4)
        sway = 0.12 * math.sin(14 * t + k * 1.9)
        H = h * s * rise
        if kind == "flick": H *= 0.35 + 0.65 * abs(math.sin(31 * t + k * 2.3))   # flickers on and off
        if fate == "sink": H *= 1 - smooth(0.45, 1, u)
        if H < 2: continue
        ang = -math.pi / 2 + side * d * (lean * 0.6 + sway)                      # leans away from the target
        bend = side * d * (lean * (1.6 if fate == "curl" else 0.8)) * (1 + (1.2 * smooth(0.3, 1, u) if fate == "curl" else 0))
        W = 1.3 * w * s * (1 - 0.4 * smooth(0.5, 1, u))
        sh = Shape(c)
        sh.poly(flame(bx, by + 2 * s, ang, H, W, bend, 0.25 * side * d, p=0.85))
        sh.poly(_ellipse(bx, by, W * 0.8, 3 * s, 0.0))                  # the foot spreads on the floor
        if kind == "flick":                                               # flicks just blink out, no erosion
            sh.paint(soul_bands(pal, s, 0.8), 1.0, fillet=2.0)
        else:
            sh.paint(soul_bands(pal, s, 0.7 * (1 - u)), 1.0, fillet=2.5, erode=6 * s * smooth(0.6, 1, u), noise=4 * s * smooth(0.4, 1, u), seed=30 + k % 4)
        if kind == "flick": continue
        # lilac tip: the upper part of a tall tongue, its own colour; it leaves when the fate says so
        tip_from = 0.5
        lift = 46 * s * smooth(0.45, 1, u) ** 1.2 if fate == "detach" else 0.0
        tx, ty = flame_point(bx, by + 2 * s, ang, H, bend, 0.25 * side * d, tip_from)
        ta = ang + bend * tip_from ** 2
        sh2 = Shape(c)
        sh2.poly(flame(tx, ty - lift, ta, H * (1 - tip_from) * (1.1 if fate == "detach" else 1), W * 0.7, bend * 0.6, 0.3 * side * d, p=1.0))
        al = 0.9 * (1 - smooth(0.6, 1, u)) if fate == "detach" else 0.9
        sh2.paint(lilac_bands(pal, s), al, fillet=2.0, erode=4 * s * smooth(0.6, 1, u), noise=3 * s * smooth(0.4, 1, u), seed=40 + k % 3)
        if fate == "curl" and u > 0.55:                                  # the curled crest breaks into two drops
            ue = (u - 0.55) * life
            ly = _layer(front)
            for m in range(2):
                x, y, _, _ = drag_pos(tx, ty, side * d * (40 + 30 * m) * s, -40 * s, ue, k=2, g=500 * s)
                if y < gy_of(L): ly.poly(shard(x, y, math.pi / 2, 7 * s, 4.5 * s), pal["cyan"] if m else pal["violet"], 1 - smooth(0.7, 1, u))
            front.paste(ly)


def gy_of(L): return L(0, GROUND)[1]


# ---------------------------------------------------------------- possession: the target becomes a ghost
def _dummy(sh, L, s, d, wipe=None, grow=1.0):
    """A generic target mask (head and body only; a character would pass its own alpha mask instead)."""
    hx, hy = L(*HEAD)
    sh.poly(_ellipse(hx, hy, 16 * s * grow, 15 * s * grow, 0.0))
    sh.poly(_ellipse(hx, hy + 30 * s, 20 * s * grow, 26 * s * grow, 0.0))
    sh.poly([(hx - 7 * s * d, hy - 12 * s), (hx - 2 * s * d, hy - 24 * s), (hx + 2 * s * d, hy - 13 * s)])          # a tuft on top
    if wipe is not None:
        sh.poly([(hx - 60 * s, wipe), (hx + 60 * s, wipe), (hx + 60 * s, hy + 140 * s), (hx - 60 * s, hy + 140 * s)], on=False)


def _possession(t, L, A, d, s, pal, front, back):
    u = (t - T_HIT - 0.04) / (DUR - T_HIT - 0.04)
    if not 0 <= u < 1: return
    hx, hy = L(*HEAD)
    wipe = hy - 20 * s + 140 * s * out_cubic(min(1, u / 0.25))          # the ghost runs down the body from the head ...
    wipe = min(wipe, hy + 70 * s - 100 * s * smooth(0.55, 1, u) ** 0.8)     # ... and drains back up out of it at the end
    a = smooth(0, 0.05, u) * (1 - smooth(0.85, 1, u))
    sh = Shape(front)
    _dummy(sh, L, s, d, wipe, 1.0 + 0.04 * math.sin(30 * t))
    sh.paint([(2.6 * s, pal["cyan"]), (4.4 * s, pal["blue"]), (None, pal["deep"])], 0.8 * a, fillet=3.0,
             erode=3 * s * smooth(0.55, 1, u), noise=4 * s * smooth(0.4, 1, u), seed=61)
    # lilac flames rising off the head and shoulders: tall, thin, slow, see-through (unlike the ground fire)
    for k, (dx, dy, Ln, W, ph) in enumerate(((-6, -12, 58, 14, 0.0), (14, 14, 40, 11, 1.7), (-16, 22, 34, 10, 3.1))):
        uk = (u - 0.08 * k) / 0.8
        if not 0 <= uk < 1: continue
        sh2 = Shape(front)
        Lr = Ln * s * smooth(0, 0.2, uk) * (1 + 0.15 * math.sin(9 * t + ph))
        sh2.poly(flame(hx + d * dx * s, hy + dy * s, A(-math.pi / 2 - 0.25) - 0.15 * math.sin(6 * t + ph), Lr, W * s, -0.6 * d, 0.45 * d * math.sin(4 * t + ph), p=1.4))
        sh2.paint(lilac_bands(pal, s), 0.55 * a * (1 - smooth(0.6, 1, uk)), fillet=2.0, erode=3 * s * smooth(0.5, 1, uk), noise=3 * s * uk, seed=70 + k)


def _hit_flare(t, L, A, d, s, pal, front):
    """The orbiting spirit arrives last, into the burning ghost: a tall thin flare shoots up out of it."""
    sp = SPIRITS[5]; u = (t - sp["end"]) / 0.3
    if not 0 <= u < 1: return
    cx, cy = L(*sp["path"][-1])
    sh = Shape(front)
    sh.poly(flame(cx, cy + 10 * s, A(-math.pi / 2), (40 + 70 * out_cubic(u)) * s, 16 * s * (1 - 0.5 * u), -0.4 * d, 0.3 * d, p=1.6))
    sh.poly(flame(cx, cy + 10 * s, A(-math.pi / 2 + 0.5), (20 + 30 * out_cubic(u)) * s, 10 * s * (1 - 0.5 * u), 0.5 * d, 0.0, p=1.5))
    sh.paint(soul_bands(pal, s, 1 - u), 1 - smooth(0.6, 1, u), fillet=2.0, erode=5 * s * smooth(0.5, 1, u), noise=3 * s * u, seed=77)


# ---------------------------------------------------------------- slow purple wisps and floating motes
def _wisps(t, L, d, s, pal, front):
    rng = random.Random(55)
    ly = _layer(front)
    for j in range(7):
        tb = T_HIT + 0.12 + rng.uniform(0, 0.35); life = rng.uniform(0.35, 0.55)
        u = (t - tb) / life
        if not 0 <= u < 1: continue
        x0 = TX + rng.choice((-1, 1)) * rng.uniform(10, 120)
        h = rng.uniform(50, 110); w0 = rng.uniform(3, 7); ph = rng.uniform(0, 6)
        n = 14
        top = h * out_cubic(u)
        bot = h * smooth(0.3, 1, u)
        pts, ws = [], []
        for m in range(n + 1):
            v = m / n
            yy = GROUND - 10 - (bot + (top - bot) * v)
            xx = x0 + 10 * math.sin(3 * v + ph + 4 * t) * (0.4 + v)
            pts.append(L(xx, yy)); ws.append(w0 * s * math.sin(math.pi * v) ** 0.8 + 0.3)
        ribbon(ly, pts, ws, pal["lilac"] if j % 2 else pal["violet"], 0.5 * (1 - smooth(0.6, 1, u)))
    front.paste(ly)


def _motes(t, L, d, s, pal, front):
    """Small glowing specks of three sizes that float and twinkle: shed by the spirits, then by the fire."""
    ly = _layer(front)
    rng = random.Random(77)
    for j in range(34):
        if j < 14:                                                        # shed by a spirit along its way
            sp = SPIRITS[j % 6]
            tb = sp["launch"] + rng.uniform(0.05, 0.9) * (sp["end"] - sp["launch"])
            if sp["fate"] == "fizzle" and j >= 6: tb = sp["end"] - 0.12 + rng.uniform(0, 0.12)
            p, _ = _pos(sp, tb)
            vx, vy = rng.uniform(-30, 30), rng.uniform(-50, -10)
        else:                                                             # rising off the ground fire
            tb = T_HIT + rng.uniform(0.0, 0.45)
            p = (TX + rng.uniform(-140, 140), GROUND - rng.uniform(4, 30))
            vx, vy = rng.uniform(-20, 20), rng.uniform(-70, -30)
        life = rng.uniform(0.3, 0.6)
        u = (t - tb) / life
        if not 0 <= u < 1: continue
        size = (1.2, 2.0, 3.2)[j % 3]
        x, y = L(p[0] + vx * u * life + 6 * math.sin(7 * t + j), p[1] + vy * u * life)
        r = size * s * (0.7 + 0.3 * math.sin(22 * t + j * 2.1)) * (1 - smooth(0.7, 1, u))
        ly.ellipse(x, y, r * 1.8, r * 1.8, pal["cyan"], 0.35 * (1 - u))
        ly.ellipse(x, y, r, r, pal["white"], 0.95 * (1 - smooth(0.6, 1, u)))
    front.paste(ly)


VARIANTS = {"soulstrike": spirit_soulstrike}
