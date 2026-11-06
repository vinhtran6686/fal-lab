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
from fxcore import Canvas, mix, clamp, smooth, out_cubic, out_back, ribbon, stepped_glow
from organic import Shape, thorn, shard, blob, shade, flame, noise_field, thorns_at, shards_at
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
    "soulstrike": dict(name="Xuất hồn kích", status="rework", tags=["heavy", "homing", "spirit", "organic", "ground"],
                       glow=(110, 196, 255), halo=(0.5, 10),
                       desc="spirit flames are born at the caster's chest, swell and fan out; six spirits of three sizes (the big one a "
                            "layered blue flame, the small ones flat-shaded teardrops) each take their own path and strike one after "
                            "another, every hit a bright organic splash of its own shape (a chevron on the torso, a hollow ring at the "
                            "back of the head, a star flat on the floor, the climax on the head, a fountain at the chest); a spiky "
                            "crater ring races out on the floor and independent soul flames stand in three rows (dark violet behind, "
                            "blue, bright cyan in front), each with its own sway, flicker, life and fate (sink, split, tip floats off). "
                            "The target point is 340 px ahead of the anchor; no target body is drawn"),
}


# ---------------------------------------------------------------- helpers
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
TX = TARGET_DX
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
    dict(name="hero", r=24, spawn=0.02, launch=0.12, end=0.74, tail=0.13, wig=(8, 2.0), drips=True, flicks=3, tear=0.0, tailw=0.55, strands=1, phase=0.4,
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
    # small: circles the caster once, then darts in last, into the chest, after the climax
    dict(name="orbit", r=9, spawn=0.09, launch=0.18, end=1.0, tail=0.12, wig=(3, 2.8), drips=False, flicks=1, tear=0.9, tailw=0.45, strands=1, phase=3.3,
         path=[(0, -6), (42, -38), (4, -74), (-44, -40), (-12, 12), (58, -8), (200, -62), (296, -40), (TX - 4, GROUND - 48)],
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
        for k, al in ((1.0, 0.07), (0.6, 0.1), (0.32, 0.14)):              # a faint light on the floor, not a puddle
            rx = (50 + 80 * out_cubic(min(1, u * 2.5))) * k * s
            ly.ellipse(bx, by - 2 * s, rx, rx * 0.11, pal["cyan"], a * al)
        back.paste(ly)

    # ======================================== 3. the spirits (tails behind, heads on top), each with its own fate
    for sp in SPIRITS:
        if t < sp["spawn"]: continue
        _spirit(t, sp, L, A, d, s, pal, front, back)

    # ======================================== 4. the hits: each different
    _ground(t, L, d, s, pal, front, back)
    _hits(t, L, A, d, s, pal, front, back)
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


def _spirit(t, sp, L, A, d, s, pal, front, back):
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
    pts0 = [L(*head)] * 3
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
        c.paste(ly)
        if strand == 0: pts0 = pts
    # ---- head: its own proportions (round and heavy, or a teardrop), squash and stretch from the smoothed speed, own flick count
    hx, hy = L(*head)
    vx, vy, spd = _heading(sp, t)
    ang = math.atan2(vy, vx * d) if (spd > 20 and t >= sp["launch"]) else -math.pi / 2     # pointing up while it grows
    stretch = min(0.5, spd / 1500)
    rr = r * g * shrink
    tear = sp["tear"]
    if sp["name"] == "hero":                                              # the hero is a blue flame: nested flame silhouettes
        back_dir = ang + math.pi
        bxv, byv = math.cos(back_dir) * 0.7, math.sin(back_dir) * 0.7 - 0.55       # tongues stream back AND rise (flames go up)
        flow = math.atan2(byv, bxv)
        tongues = [(-0.7, 3.8, 1.25, 0.55, 0.0), (-0.15, 3.0, 1.15, -0.45, 1.7), (0.4, 2.3, 0.95, 0.5, 3.1), (0.95, 1.5, 0.7, -0.4, 4.4)]
        layers = ((0.82, 1.0, ("deep", "blue", "cyan")), (0.5, 0.6, ("cyan", "pale", "white")))
        for li, (ks, kl, tn) in enumerate(layers):
            sh = Shape(c)
            fwd = 0.18 * rr * li                                          # the inner flame sits a little forward, hotter
            cx_, cy_ = hx + math.cos(ang) * fwd, hy + math.sin(ang) * fwd
            sh.poly(_ellipse(cx_, cy_, rr * ks * (1 + 0.3 * stretch), rr * ks * (1 - 0.15 * stretch), ang, 0.07, 9 * t + li))
            for spread, Lk, Wk, b, ph in tongues:
                base_a = back_dir + spread
                x0, y0 = cx_ + math.cos(base_a) * rr * ks * 0.55, cy_ + math.sin(base_a) * rr * ks * 0.55
                fl = 1 + 0.18 * math.sin(23 * t + ph) + 0.08 * math.sin(41 * t + 2 * ph)
                sh.poly(tongue(x0, y0, flow + spread * 0.3, rr * Lk * kl * fl, rr * Wk * ks * 1.2, b, 0.4 * math.sin(11 * t + ph)))
            if li == 0:
                for j in range(5):                                        # drips falling off the outer flame
                    tb = sp["launch"] + 0.06 + j * 0.09
                    u = (t - tb) / 0.3
                    if not 0 <= u < 1 or tb > sp["end"]: continue
                    p, _ = _pos(sp, tb - 0.05 - 0.02 * (j % 3))
                    x, y = L(p[0], p[1] + 30 * u * u + 8 * u)
                    sz = (3.4 - 0.6 * (j % 2)) * s * (1 - u)
                    if sz > 0.4: sh.poly(shard(x, y, math.pi / 2, sz * 3, sz * 1.7))
            tones = dict(shadow=pal[tn[0]], base=pal[tn[1]], light=pal[tn[2]])
            shade(sh, tones, 1.0, light=(0.15, 0.98), off=max(1.5, rr * 0.22 * ks), fillet=2.5,
                  erode=5 * s * dive if li == 0 else 0.0, noise=5 * s * dive if li == 0 else 0.0, seed=64)
        ly = _layer(c); ly.ellipse(hx + math.cos(ang) * rr * 0.3, hy + math.sin(ang) * rr * 0.3 - rr * 0.1, rr * 0.26, rr * 0.2, pal["white"], 1.0)
        c.paste(ly)
        return
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


def _tail_poly(pts, ws):
    L_, R_ = [], []
    for k, (x, y) in enumerate(pts):
        p, q = pts[max(0, k - 1)], pts[min(len(pts) - 1, k + 1)]
        dx, dy = q[0] - p[0], q[1] - p[1]; l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        L_.append((x + nx * ws[k] / 2, y + ny * ws[k] / 2)); R_.append((x - nx * ws[k] / 2, y - ny * ws[k] / 2))
    return L_ + R_[::-1]


# ---------------------------------------------------------------- hits: the impact/hit method in soul colours
# Every hit is ONE hand-drawn silhouette (wobbly core + curved thorns of three sizes, all curling the same way, droplets flung
# from the hero tips), coloured by distance to its edge (white core -> pale -> cyan -> blue -> deep -> violet tips), a dark
# see-through backing, cooling (the white shrinks), then noisy erosion breaking it into drops. Same method as impact/hit, so
# every splash in this effect speaks one shape language; they differ in size, direction and silhouette.
def soul_spark(pal, s=1.0, heat=1.0):
    """Edge -> centre bands for the splashes (like organic.spark_bands, darkest at the edge). Brighter than everything else in
    the effect on purpose: blue tips, cyan, pale, white core; cooling drops the white."""
    k = s * (0.6 + 0.4 * heat)
    return [(1.3 * s, pal["blue"]), (3.4 * k, pal["cyan"]), (7.0 * k, pal["pale"]), (None, pal["white"])] if heat > 0.25 else \
           [(1.3 * s, pal["blue"]), (3.4 * k, pal["cyan"]), (None, pal["pale"])]


def soul_burst(c, t, cx, cy, thorns, core, drops, pal, s, seed, life, A, hollow=0.0, sy=1.0, white=False, scale=1.0):
    """thorns: (deg, length, width, bend, base radius[, delay]); drops: (deg, start, speed, length, width, bend, delay)."""
    u = t / life
    if not 0 <= u < 1: return
    k = s * scale
    sh = Shape(c)
    g = 0.7 + 0.3 * out_back(min(1, t / 0.07)) + 0.3 * u                  # keeps growing until it is gone
    rc = core * k * g * (1 - 0.35 * smooth(0.4, 1, u))
    sh.poly(blob(cx, cy, rc, sy=sy, wob=0.12, freq=5, phase=seed))
    thorns_at(sh, cx, cy, [(A(math.radians(a)), L * k, W * k * 1.5, b, r0 * k) + tuple(x[5:]) for x in thorns for a, L, W, b, r0 in [x[:5]]],
              t, life, sy=sy, thin_by=0.55)
    shards_at(sh, cx, cy, [(A(math.radians(a)), d0 * k, sp * k, L * k, W * k, b, dl) for a, d0, sp, L, W, b, dl in drops], t, life * 1.15, sy=sy)
    if hollow > 0:
        hr = rc * hollow * smooth(0.3, 0.75, u)
        if hr > 7 * s: sh.hole(cx, cy, hr, hr * sy)
    first = white and t < 1 / 30 - 1e-6
    bands = [(1.2 * s, pal["cyan"]), (None, pal["white"])] if first else soul_spark(pal, k, 1 - smooth(0.04, 0.6, u))
    sh.paint(bands, 1.0, fillet=4.0, erode=10 * k * smooth(0.62, 1, u), noise=4.5 * k * smooth(0.5, 1, u), seed=seed,
             backing=(3.5 * k, pal["dark"], 0.32 * (1 - smooth(0.4, 0.9, u))))


def _hits(t, L, A, d, s, pal, front, back):
    B = 0.3 * d                                                           # one curl direction for every thorn of a hit
    # the skimming spirit hooks into the torso from behind: a small chevron spraying back the way it came (-x)
    sp = SPIRITS[1]
    soul_burst(front, t - sp["end"], *L(*TORSO), [(140, 62, 22, B, 0), (-140, 58, 21, B, 0), (180, 86, 12, B, 5), (162, 46, 10, B, 5),
                                                   (-160, 40, 10, B, 5), (112, 20, 9, B, 3), (-112, 22, 9, B, 3)],
               10, [(176, 70, 260, 18, 7, B, 0.03), (150, 56, 200, 12, 6, B, 0.05), (-150, 52, 210, 11, 5, B, 0.06)],
               pal, s, 51, 0.3, A, scale=0.7)
    # the corkscrew spirit lands on the head: a small spiky ring, hollow from the start
    sp = SPIRITS[2]
    soul_burst(front, t - sp["end"], *L(HEAD[0] - 14, HEAD[1] - 8), [(a, L_, W_, B, r0) for a, L_, W_, r0 in ((-96, 48, 14, 14), (-70, 20, 9, 12),
                                                                                        (-8, 36, 12, 14), (52, 14, 8, 10), (128, 42, 13, 15),
                                                                                        (150, 18, 9, 12), (232, 26, 10, 13))],
               22, [(-90, 60, 200, 12, 6, B, 0.03), (130, 54, 180, 10, 5, B, 0.04)], pal, s, 52, 0.17, A, hollow=0.85, scale=0.6)   # gone before the climax
    # the zigzag spirit hits the floor first: a star squashed flat on the ground
    sp = SPIRITS[3]
    soul_burst(front, t - sp["end"], *L(*sp["path"][-1]), [(-170, 70, 18, B, 4), (-10, 64, 17, B, 4), (-130, 40, 13, B, 4), (-50, 44, 14, B, 4),
                                                           (-92, 30, 12, B, 4), (160, 26, 10, B, 3), (20, 24, 10, B, 3)],
               14, [(-120, 30, 220, 12, 6, B, 0.04), (-60, 30, 200, 11, 5, B, 0.05)], pal, s, 53, 0.32, A, sy=0.4, scale=0.75)
    # the big dive: the climax. A full spark, the only white first drawing; it splashes down and out over the head
    soul_burst(front, t - T_HIT, *L(*HEAD), [(36, 112, 24, B, 8), (-156, 96, 22, B, 8),                         # two heroes
                                             (-64, 64, 17, B, 8), (122, 60, 16, B, 8), (-108, 58, 16, B, 8), (78, 50, 15, B, 8),   # medium
                                             (-18, 26, 12, B, 6), (166, 28, 13, B, 6), (-136, 24, 11, B, 6),                       # nubs
                                             (20, 134, 5, 0.05 * d, 4, 0.01), (200, 116, 5, 0.05 * d, 4, 0.01)],                  # two rays
               32, [(30, 70, 280, 18, 8, B, 0.05), (44, 64, 220, 12, 6, B, 0.08), (-150, 64, 260, 16, 7, B, 0.05),
                    (-164, 58, 200, 11, 5, B, 0.09), (-100, 46, 180, 10, 5, B, 0.07)],
               pal, s, 54, 0.4, A, hollow=0.9, white=True)
    if 0 <= t - T_HIT < 2 / 30:                                           # the flash under it (two drawings)
        ly = _layer(back); stepped_glow(ly, *L(*HEAD), 56 * s, pal, 1.0); back.paste(ly)
    # the orbiting spirit arrives last, into the chest: a fountain of thorns straight up
    sp = SPIRITS[5]
    soul_burst(front, t - sp["end"], *L(*sp["path"][-1]), [(-90, 120, 22, 0.08 * d, 4), (-70, 80, 17, -0.25 * d, 4, 0.01), (-112, 76, 17, 0.25 * d, 4, 0.01),
                                                           (-52, 40, 13, -0.3 * d, 4, 0.03), (-130, 44, 13, 0.3 * d, 4, 0.03)],
               14, [(-90 + a, 40, 300, 14, 7, 0.0, 0.03 + 0.02 * i) for i, a in enumerate((-20, 14, -6, 24))], pal, s, 55, 0.4, A, sy=0.7, scale=0.75)


# ---------------------------------------------------------------- ground: a crater ring, then independent soul flames in 3 rows
# Every flame is its own silhouette with its own height, width, lean, sway, flicker, life and fate, so they never move as one
# block. Depth is told by colour: the back row is dark violet (behind the target), the middle row blue, the front row bright
# cyan; all three use the small spirits' flat toon shading (light top, dark underside).
ROWS = {"back": ("dark", "deep", "violet"), "mid": ("deep", "blue", "cyan"), "front": ("blue", "cyan", "pale")}
# (row, offset from the target base, height, width, delay, life, fate, sway Hz, phase)
FLAMES = [("back", -18, 96, 30, 0.06, 0.62, "detach", 2.1, 0.3), ("back", 34, 70, 26, 0.10, 0.55, "sink", 2.8, 1.9),
          ("back", -70, 52, 22, 0.16, 0.5, "split", 1.7, 4.2), ("back", 88, 40, 18, 0.2, 0.42, "sink", 3.3, 2.6),
          ("mid", 4, 74, 28, 0.04, 0.55, "split", 3.0, 0.8), ("mid", -42, 50, 22, 0.1, 0.5, "detach", 2.4, 3.3),
          ("mid", 58, 46, 20, 0.12, 0.48, "sink", 3.6, 5.1), ("mid", -104, 28, 14, 0.22, 0.36, "sink", 4.2, 1.2),
          ("front", -8, 38, 24, 0.08, 0.46, "sink", 3.8, 2.2), ("front", 24, 26, 18, 0.14, 0.4, "detach", 4.4, 0.5),
          ("front", -56, 20, 16, 0.18, 0.36, "sink", 5.0, 3.9), ("front", 120, 16, 11, 0.26, 0.3, "sink", 4.6, 4.7),
          ("front", -138, 14, 10, 0.3, 0.28, "sink", 5.4, 1.6)]


def tongue(x, y, ang, L, W, bend=0.0, wave=0.0, n=26):
    """A fire tongue: a round belly in its lower third, then a long taper into a tip that curls (bend) and sways (wave).
    Unlike organic.flame (which narrows from the base), it reads as a flame, not a spike."""
    left, right = [], []
    px, py = x, y
    for i in range(n + 1):
        u = i / n
        a = ang + bend * u * u + wave * math.sin(1.6 * math.pi * u)
        if i:
            px += math.cos(a) * L / n; py += math.sin(a) * L / n
        belly = math.sin(math.pi * clamp(u / 0.75)) ** 0.5
        w = W / 2 * 1.4 * (0.45 + 0.55 * belly) * (1 - u) ** 1.2
        nx, ny = -math.sin(a), math.cos(a)
        left.append((px + nx * w, py + ny * w)); right.append((px - nx * w, py - ny * w))
    return left + right[::-1]


def _flame_one(c, x0, y0, H, W, lean, wave, tones, a, er, seed, s):
    sh = Shape(c)
    sh.poly(tongue(x0, y0, -math.pi / 2 + lean, H, W, -lean * 2.6, wave))
    sh.poly(_ellipse(x0, y0 - 1 * s, W * 0.62, 3 * s, 0.0))                 # its foot spreads on the floor
    shade(sh, tones, a, light=(0.15, 0.98), off=max(1.5, W * 0.12), fillet=2.0, erode=er * 6 * s, noise=er * 5 * s, seed=seed)


def _ground(t, L, d, s, pal, front, back):
    bx, by = L(*BASE)
    sy = 0.3
    # the flat spiky ring racing out on the floor (impact/ground crater, in the bright splash colours)
    tc = t - T_HIT - 0.02; ring_life = 0.4
    if 0 <= tc < ring_life:
        u = tc / ring_life
        sh = Shape(front)
        g = 0.7 + 0.3 * out_back(min(1, tc / 0.07))
        R = (28 + 120 * out_cubic(u)) * s * g
        sh.poly(blob(bx, by, R, sy=sy, wob=0.05, freq=7, phase=1))
        hk = 0.55 + 0.47 * smooth(0.0, 1.0, u) ** 0.8
        sh.hole(bx, by, R * hk, R * hk * sy)
        for i, a in enumerate((-170, -136, -104, -76, -48, -16, 14, 44, 76, 108, 138, 164)):
            ar = math.radians(a) if d > 0 else math.pi - math.radians(a)
            Lt, Wt = ((50, 20) if i % 3 == 0 else (30, 15) if i % 3 == 1 else (18, 12))
            sh.poly(thorn(bx + math.cos(ar) * R * 0.97, by + math.sin(ar) * R * 0.97 * sy, ar, Lt * s * g * (1 - 0.6 * smooth(0.4, 1, u)) * 1.3,
                          Wt * s * (1 - 0.9 * smooth(0.2, 1, u)) * 1.5, 0.25 * (1 if math.cos(ar) > 0 else -1), sy=sy))
        sh.paint(soul_spark(pal, s, 1 - smooth(0.04, 0.65, u)), 1.0, fillet=4.0, seed=91,
                 backing=(3.0 * s, pal["dark"], 0.3 * (1 - smooth(0.4, 0.9, u))))
    # the flames, back row first
    for row in ("back", "mid", "front"):
        tones = dict(shadow=pal[ROWS[row][0]], base=pal[ROWS[row][1]], light=pal[ROWS[row][2]])
        c = back if row == "back" else front
        for k, (rw, dx, h, w, dl, life, fate, hz, ph) in enumerate(FLAMES):
            if rw != row: continue
            tb = T_HIT + 0.03 + dl + 0.12 * (1 - (1 - min(1, abs(dx) / 160)) ** 2)    # the farther, the later
            u = (t - tb) / life
            if not 0 <= u < 1: continue
            x0 = bx + d * dx * s
            rise = out_back(min(1, u / 0.2), 2.2)
            flick = 1 + 0.16 * math.sin(2 * math.pi * hz * 2.3 * t + ph) + 0.07 * math.sin(2 * math.pi * hz * 5.1 * t + 2 * ph)
            H = h * s * rise * flick
            W = 1.35 * w * s * (0.75 + 0.25 * rise)
            side = 1 if dx >= 0 else -1
            lean = d * (side * 0.12 + 0.18 * math.sin(2 * math.pi * hz * t + ph))
            wave = d * 0.35 * math.sin(2 * math.pi * hz * 1.4 * t + ph * 1.7)
            er = smooth(0.7, 1, u)
            if fate == "sink":
                H *= 1 - smooth(0.45, 1, u); W *= 1 - 0.5 * smooth(0.5, 1, u)
            elif fate == "split" and u > 0.42:                            # splits into two thinner tongues leaning apart
                v = smooth(0.42, 0.7, u)
                for sgn, kk in ((-1, 0.75), (1, 0.55)):
                    _flame_one(c, x0 + sgn * W * 0.25 * v, by, H * kk * (1 - 0.6 * smooth(0.6, 1, u)), W * 0.6, lean + sgn * d * 0.35 * v,
                               wave * sgn, tones, 1.0, er, 300 + k, s)
                continue
            elif fate == "detach" and u > 0.45:                           # the tip breaks off and floats up as its own small flame
                v = smooth(0.45, 1, u)
                _flame_one(c, x0 + d * 6 * s * v, by - H * 0.55 - 70 * s * v, H * 0.45 * (1 - 0.7 * v), W * 0.5 * (1 - 0.5 * v), lean, wave,
                           tones, 1.0, smooth(0.6, 1, v), 400 + k, s)
                H *= 1 - 0.5 * v
            if H > 3:
                _flame_one(c, x0, by, H, W, lean, wave, tones, 1.0, er, 200 + k, s)


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
