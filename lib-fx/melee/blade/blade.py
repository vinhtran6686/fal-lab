"""lib-fx / melee / blade: slashes of an edged weapon.

Each design is  fn(t, P, front, back, pal=..., s=1.0, d=1)  drawing the slash t seconds after it starts; P is the centre of the
swing; d = -1 mirrors it.

swirl_fire / swirl_frost are rebuilt from a reference GIF; analysis in lib-fx/RECIPE-swirl.md, rules in lib-fx/SHAPE-RULES.md.
Both live in stroke space (v along the sweep, C across it) on one spiral (_core/fieldfx.spiral_coords):
  - the tiers are flat colours separated by SMOOTH boundaries across the stroke that drift with age and cooling;
  - every lick, feather, streak, hole and gap is placed by hand, each with its own size and shape (never a periodic texture:
    repeated identical teeth read as a strip and look bad);
  - frost is two shapes side by side (a white blade outside, a blue flame inside) with a thin dark seam;
  - no gradient anywhere: stepped flat glow, a flat see-through after-image.
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from fxcore import Canvas, clamp, smooth, out_back, lens
from fieldfx import grid, noise1, stepped_glow, spiral_coords
from organic import thorn
from palettes import BLAZE, FROST

FPS = 30
FRAME, ANCHOR = (380, 380), (190, 190)
DUR = 0.4
TAGS = ["melee", "blade", "slash", "swirl", "one-shot", "anchor:centre"]
PAL_SUN = BLAZE
CATALOG = {
    "swirl_fire": dict(name="Xoáy chém lửa", status="draft", tags=["fire", "medium", "field"], palette=BLAZE, halo=(0.0, 8),
                       desc="a pink-fire swirl slash: a thick yellow band outside, pink then crimson inside, an amber rim, each "
                            "boundary smooth with a few hand-placed flame licks pointing back along the sweep; a straight needle tail; "
                            "it sweeps 330 degrees in four drawings, curls into the centre, cools (yellow first) and breaks into four "
                            "claw pieces of different sizes; stepped flat glow"),
    "swirl_frost": dict(name="Xoáy chém băng", status="draft", tags=["ice", "water", "medium", "field"], palette=FROST, dur=0.95,
                        halo=(0.0, 8),
                        desc="a frost swirl slash made of two shapes side by side: a white blade on the outside and a blue flame on the "
                             "inside with a few large cyan feathers and deep streaks, split by a thin dark seam; it sweeps over a flat "
                             "see-through after-image, the white shrinks, holes open, it breaks into pieces and thin cracks fade in "
                             "steps; stepped flat glow"),
}


def _pal(pal, base):
    p = dict(base); p.update(pal); return p


TH0, SPAN, T_SW, T_LEAD = math.pi + 0.35, math.radians(330), 0.16, 0.035   # start upper left; sweep time and first-drawing lead (measured)


def head_at(t, k=1.0): return TH0 + SPAN * k * (1 - (1 - clamp(t / T_SW)) ** 1.6)


def rad_fn(R, curl, start=0.7):
    def r(th):
        f = (th - TH0) / SPAN
        x = np.clip((f - start) / (1 - start), 0, 1); x = x * x * (3 - 2 * x)
        return R * (1 + 0.07 * np.sin(3 * th + 0.6)) * (1 - curl * x ** 1.3)
    return r


def tongue_poly(pts_fn, v0, c0, length, width, lean, bend, n=24):
    """A flame tongue in stroke space: base centred at (v0, c0), running BACK along the stroke (toward smaller v) for `length`
    (in v), leaning across by `lean` (in c), curling by `bend`; width (in c) tapers to a sharp tip. pts_fn(v, c) -> canvas xy."""
    L, R = [], []
    for i in range(n + 1):
        s = i / n
        v = v0 - length * s
        c = c0 + lean * s + bend * s * s
        hw = width / 2 * (1 - s) ** 1.3 * (0.6 + 0.4 * math.sin(math.pi * min(1, s * 2 + 0.5)))
        L.append(pts_fn(v, c - hw)); R.append(pts_fn(v, c + hw))
    return L + R[::-1]


def lens_poly(pts_fn, v0, c0, length, width, lean, bend, n=24):
    """A feather: a lens lying along the stroke from v0 back to v0 - length, widest a third of the way, pointed at both ends."""
    L, R = [], []
    for i in range(n + 1):
        s = i / n
        v = v0 - length * s
        c = c0 + lean * s + bend * s * s
        hw = width / 2 * math.sin(math.pi * s ** 0.75) ** 0.8
        L.append(pts_fn(v, c - hw)); R.append(pts_fn(v, c + hw))
    return L + R[::-1]


def mask_of(polys, size, ss):
    m = Image.new('L', size, 0); dr = ImageDraw.Draw(m)
    for p in polys:
        if len(p) > 2: dr.polygon([(x * ss, y * ss) for x, y in p], fill=255)
    return np.asarray(m) > 127


def paint(canvas, mask, col, alpha=1.0):
    if not mask.any(): return
    out = np.zeros(mask.shape + (4,), np.uint8); out[mask] = tuple(col) + (int(255 * alpha),)
    canvas.img.alpha_composite(Image.fromarray(out, 'RGBA'))


# every lick hand-placed: (v of its base, length in v, width in c, lean in c, bend) -- different sizes, uneven spacing
PINK_LICKS = [(0.34, 0.13, 0.2, 0.12, 0.04), (0.41, 0.05, 0.12, 0.06, 0.0), (0.58, 0.16, 0.24, 0.14, 0.05),
              (0.68, 0.06, 0.14, 0.08, 0.02), (0.79, 0.11, 0.2, 0.12, 0.04), (0.94, 0.08, 0.16, 0.1, 0.03)]
RED_LICKS = [(0.27, 0.09, 0.16, 0.1, 0.03), (0.5, 0.13, 0.2, 0.12, 0.04), (0.64, 0.04, 0.1, 0.06, 0.0), (0.86, 0.1, 0.16, 0.1, 0.03)]
GAPS = [(0.2, 0.07), (0.44, 0.05), (0.6, 0.09), (0.83, 0.04)]          # where it breaks (v, half width): four pieces of four sizes
NOTCH = [(0.47, 0.05, 0.06), (0.71, 0.04, 0.05), (0.86, 0.06, 0.07)]   # small notches cut into the outer edge (v, length, depth)


def swirl_fire(t, P, front, back, pal=BLAZE, s=1.0, d=1):
    pal = _pal(pal, BLAZE)
    t = t + T_LEAD
    R, W, curl = 106 * s, 118 * s, 0.7
    tail = TH0 + 0.35 + SPAN * 0.04 * smooth(0.04, 0.2, t)
    head = max(head_at(t), tail + 0.05)
    grow = 0.3 + 0.7 * out_back(min(1, t / 0.1))
    prof = lambda v: (v ** 0.55) * (1 - v ** 10) ** 0.3
    rad = rad_fn(R, curl)
    hw = lambda v: W * grow * prof(np.clip(v, 0, 1)) / 2
    x, y = grid(front)
    th, v, w, inside = spiral_coords(x, y, P, d, TH0, SPAN, rad, tail, head, hw)
    C = (w + 1) / 2
    f = np.clip((th - TH0) / SPAN, 0, 1)
    age = t - T_SW * (1 - (1 - f) ** (1 / 1.6))
    old = np.clip(age / 0.3, 0, 1)                                         # 0 just drawn .. 1 old
    def pts(vv, cc):                                                       # stroke space -> canvas
        th_ = tail + (head - tail) * vv
        r = float(rad(np.array(th_))) + (cc * 2 - 1) * float(hw(np.array(vv)))
        return P[0] + d * math.cos(th_) * r, P[1] + math.sin(th_) * r
    # boundaries across the stroke: smooth curves with a slow, uneven wander (few big undulations, never a periodic comb)
    cool = smooth(0.06, 0.4, t)
    c_red = 0.1 + 0.3 * old + 0.05 * noise1(v * 2.2, 31) + 0.45 * cool                 # red below this
    c_pink = 0.3 + 0.35 * old + 0.06 * noise1(v * 1.7, 32) + 0.5 * cool                 # pink below this, yellow above
    # erosion when it breaks: from the inner edge outward, V gaps between pieces
    brk = smooth(0.1, 0.24, t)
    # gaps placed by hand, each its own width: pieces of different sizes, each eroding at its own pace
    gaps = np.zeros_like(v)
    for gv, gw in GAPS: gaps = np.maximum(gaps, np.clip(1 - np.abs(v - gv) / gw, 0, 1) ** 0.8)
    pace = 1 + 0.35 * noise1(v * 2.5, 41)
    c_alpha = -0.1 + 1.25 * smooth(0.09, 0.38, t) * pace + 0.8 * brk * gaps
    size = front.img.size
    # the needle: the tail runs on thin for a while before the stroke starts
    tx, ty = pts(0.0, 0.35)
    ax, ay = pts(0.03, 0.35)
    na = math.atan2(ty - ay, tx - ax)                                       # straight on along the tangent, backwards
    needle = mask_of([thorn(tx, ty, na, R * 0.55 * (1 - smooth(0.08, 0.2, t)), W * 0.04, 0.0, p=1.0)], front.img.size, front.ss) \
        if t < 0.25 else np.zeros_like(inside)
    body = (inside & (C > c_alpha)) | needle
    notches = mask_of([tongue_poly(pts, nv + nl, 1.02, nl, nd * 2, -nd, 0.0) for nv, nl, nd in NOTCH], size, front.ss)
    body &= ~notches
    def old_at(vv):
        th_ = tail + (head - tail) * vv
        ff = min(1, max(0, (th_ - TH0) / SPAN)); return min(1, max(0, (t - T_SW * (1 - (1 - ff) ** (1 / 1.6))) / 0.3))
    pink_t = mask_of([tongue_poly(pts, lv, 0.3 + 0.35 * old_at(lv) + 0.5 * cool, ll, lw, ln, lb) for lv, ll, lw, ln, lb in PINK_LICKS], size, front.ss)
    red_t = mask_of([tongue_poly(pts, lv, 0.1 + 0.3 * old_at(lv) + 0.45 * cool, ll, lw, ln, lb) for lv, ll, lw, ln, lb in RED_LICKS], size, front.ss)
    pink = body & ((C < c_pink) | pink_t)
    red = body & ((C < c_red) | red_t) | needle
    rim = body & (C > 0.9)                                                  # amber rim on the outer edge
    edge = body & ndimage.binary_dilation(pink, iterations=int(2.2 * front.ss)) & ~pink   # thin amber where yellow meets pink
    ly = Canvas(front.w, front.h, front.ss)
    paint(ly, body, pal['yellow']); paint(ly, rim | edge, pal['amber']); paint(ly, pink, pal['pink']); paint(ly, red, pal['crimson'])
    front.paste(ly)
    GL = [(15, (96, 26, 52), 0.55), (9, (160, 36, 76), 0.6), (4, (232, 60, 112), 0.8)]
    stepped_glow(back, body, [(px * s, c, a * (1 - smooth(0.2, 0.5, t))) for px, c, a in GL], front.ss)


# the blue flame's own shapes, hand-placed: cyan feathers (v base, length, width, lean, bend) and deep streaks
FEATHERS = [(0.27, 0.2, 0.4, 0.16, 0.06), (0.45, 0.26, 0.5, 0.2, 0.1), (0.55, 0.08, 0.24, 0.08, 0.0), (0.72, 0.22, 0.44, 0.18, 0.08),
            (0.86, 0.12, 0.3, 0.1, 0.03), (0.97, 0.08, 0.2, 0.06, 0.0)]
STREAKS = [(0.33, 0.14, 0.1, 0.04, 0.02), (0.58, 0.18, 0.12, 0.05, 0.03), (0.86, 0.1, 0.09, 0.03, 0.0)]
HOLES = [(0.3, 0.1, 0.16, 0.04, 0.0, 0.16), (0.47, 0.14, 0.2, 0.05, 0.02, 0.2), (0.62, 0.07, 0.14, 0.03, 0.0, 0.24), (0.76, 0.12, 0.18, 0.04, 0.01, 0.18)]
FGAPS = [(0.28, 0.06), (0.55, 0.08), (0.8, 0.05)]
CRACKS = [[(0.04, 1.2), (0.16, 0.96), (0.27, 1.16), (0.36, 0.98)], [(0.62, 1.12), (0.72, 0.9), (0.8, 1.04)], [(0.9, 0.74), (0.96, 0.86)]]


def swirl_frost(t, P, front, back, pal=FROST, s=1.0, d=1):
    pal = _pal(pal, FROST)
    t = t + T_LEAD
    R, W, curl, K = 104 * s, 110 * s, 0.35, 0.9
    prof = lambda v: (v ** 0.55) * (1 - v ** 8) ** 0.35
    rad = rad_fn(R, curl)
    x, y = grid(front)
    size = front.img.size

    def field(tt, wk=1.0):
        tail = TH0 + 0.35 + SPAN * 0.08 * smooth(0.05, 0.25, tt)
        head = max(head_at(tt, K), tail + 0.05)
        grow = 0.3 + 0.7 * out_back(min(1, tt / 0.1))
        hw = lambda vv: W * wk * grow * prof(np.clip(vv, 0, 1)) / 2
        th, v, w, inside = spiral_coords(x, y, P, d, TH0, SPAN, rad, tail, head, hw)
        def pts(vv, cc):
            th_ = tail + (head - tail) * vv
            r = float(rad(np.array(th_))) + (cc * 2 - 1) * float(hw(np.array(vv)))
            return P[0] + d * math.cos(th_) * r, P[1] + math.sin(th_) * r
        return th, v, w, inside, pts
    # after-image: one flat see-through navy, eroding from its edges (behind)
    te = t - 0.05
    if 0.02 < te < 0.34:
        _, va, wa, ina, _ = field(te, 1.35)
        keep = ina & ((1 - np.abs(wa) + 0.4 * (va - 0.5)) > 0.1 + 0.6 * smooth(0.1, 0.34, te))
        paint(back, keep, pal['ghost'], 0.55 * (1 - smooth(0.14, 0.34, te)))
    th, v, w, inside, pts = field(t)
    C = (w + 1) / 2
    cool = smooth(0.08, 0.36, t)
    # TWO shapes side by side: the white blade on the outer side (none at the tail), the blue flame on the inner side;
    # a thin dark seam between them. Cooling pushes the seam outward: the white shrinks first.
    seam = 0.38 + 0.7 * np.clip(1 - v, 0, 1) ** 2.2 + 0.05 * noise1(v * 2, 51) + 0.6 * cool
    brk = smooth(0.12, 0.3, t)
    gaps = np.zeros_like(v)
    for gv, gw in FGAPS: gaps = np.maximum(gaps, np.clip(1 - np.abs(v - gv) / gw, 0, 1) ** 0.8)
    c_alpha = -0.1 + 1.2 * smooth(0.08, 0.38, t) * (1 + 0.3 * noise1(v * 2.5, 52)) + 0.7 * brk * gaps
    body = inside & (C > c_alpha)
    gap_px = 1.6 * s / np.maximum(1e-3, W * prof(np.clip(v, 0, 1)) / 2) / 2  # the seam in C units
    white = body & (C > seam + gap_px)
    blue = body & (C < seam - gap_px)
    feathers = mask_of([lens_poly(pts, lv, 0.3 + 0.15 * cool, ll, lw, ln * 0.5, lb) for lv, ll, lw, ln, lb in FEATHERS], size, front.ss)
    streaks = mask_of([tongue_poly(pts, lv, 0.06, ll, lw, ln, lb) for lv, ll, lw, ln, lb in STREAKS], size, front.ss)
    holes = mask_of([tongue_poly(pts, lv, 0.3, ll * smooth(t0, t0 + 0.12, t), lw * smooth(t0, t0 + 0.12, t), ln, lb)
                     for lv, ll, lw, ln, lb, t0 in HOLES if t > t0], size, front.ss)
    blue &= ~holes
    rim = white & (C > 0.95)
    ly = Canvas(front.w, front.h, front.ss)
    paint(ly, white, pal['ice']); paint(ly, rim, pal['deep'])
    paint(ly, blue, pal['mid'] if cool < 0.7 else pal['deep'])
    paint(ly, blue & feathers, pal['cyan'] if cool < 0.75 else pal['mid'])
    paint(ly, blue & (streaks | (C < 0.08 + 0.3 * cool)), pal['deep'])
    front.paste(ly)
    # cracks: thin flat lines, fading in steps
    cr = Canvas(front.w, front.h, front.ss)
    a = 0.85 if t < 0.45 else 0.5 if t < 0.7 else 0.25 if t < 0.88 else 0.0
    for cl in CRACKS:
        for (f0, k0), (f1, k1) in zip(cl, cl[1:]):
            u = (t - 0.12 - 0.13 * f1) / 0.06
            if u <= 0 or a <= 0: continue
            a0, a1 = TH0 + 0.35 + SPAN * K * f0, TH0 + 0.35 + SPAN * K * f1
            p0 = (P[0] + d * math.cos(a0) * rad(a0) * k0, P[1] + math.sin(a0) * rad(a0) * k0)
            p1 = (P[0] + d * math.cos(a1) * rad(a1) * k1, P[1] + math.sin(a1) * rad(a1) * k1)
            g = clamp(u); pe = (p0[0] + (p1[0] - p0[0]) * g, p0[1] + (p1[1] - p0[1]) * g)
            lens(cr, p0, pe, 1.6 * s, pal['mid'], a, n=6); lens(cr, p0, pe, 0.7 * s, pal['cyan'], a, n=6)
    back.paste(cr)
    GL = [(14, (18, 52, 80), 0.6), (8, (30, 90, 140), 0.6), (3, (60, 170, 227), 0.75)]
    stepped_glow(back, white | blue, [(px * s, c, al * (1 - smooth(0.15, 0.5, t))) for px, c, al in GL], front.ss)


VARIANTS = {"swirl_fire": swirl_fire, "swirl_frost": swirl_frost}
