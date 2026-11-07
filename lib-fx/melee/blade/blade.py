"""lib-fx / melee / blade: slashes of an edged weapon.

Each design is  fn(t, P, front, back, pal=..., s=1.0, d=1)  drawing the slash t seconds after it starts; P is the centre of the
swing; d = -1 mirrors it.

swirl_fire / swirl_frost are rebuilt from a reference GIF (analysis: lib-fx/RECIPE-swirl.md; rules: lib-fx/SHAPE-RULES.md) with
the field method of _core/fieldfx.py: ONE continuous "heat" field over a spiral stroke (age since the head passed, position across
the stroke, a slanted sawtooth for licks / feathers, slow cooling, V-shaped gaps when it breaks) cut by hard thresholds into flat
colour tiers. No gradient anywhere: the glow is stepped (flat rings), the after-image is one flat see-through colour.
"""
import math
import numpy as np
from fxcore import Canvas, clamp, smooth, out_back, lens
from fieldfx import grid, saw, noise1, posterize, stepped_glow, spiral_coords
from palettes import BLAZE, FROST

FPS = 30
FRAME, ANCHOR = (380, 380), (190, 190)
DUR = 0.4
TAGS = ["melee", "blade", "slash", "swirl", "one-shot", "anchor:centre"]
PAL_SUN = BLAZE
CATALOG = {
    "swirl_fire": dict(name="Xoáy chém lửa", status="draft", tags=["fire", "medium", "field"], palette=BLAZE, halo=(0.0, 8),
                       desc="a pink-fire swirl slash in four flat tiers (yellow, amber, pink, red) cut from one heat field: it sweeps "
                            "330 degrees in four drawings with a needle tail and hooks into the centre; pink licks reach back into the "
                            "yellow; it cools tier by tier (yellow first, red last) and breaks into pointed pieces along the outer "
                            "edge; stepped flat glow"),
    "swirl_frost": dict(name="Xoáy chém băng", status="draft", tags=["ice", "water", "medium", "field"], palette=FROST, dur=0.95,
                        halo=(0.0, 8),
                        desc="a frost swirl slash in four flat tiers (white, cyan, blue, deep blue) cut from one field with feathered "
                             "streaks: a crescent sweeps and hooks over a flat see-through navy after-image, cools from the tail, opens "
                             "into pieces, and leaves thin flat crack lines that fade in steps; stepped flat glow"),
}

TH0, SPAN, T_SW = math.pi + 0.35, math.radians(330), 0.16                # starts upper left, sweeps clockwise; sweep time (measured)
T_LEAD = 0.035                         # the first drawing already shows ~100 degrees of sweep (measured): the clock starts there


def head_at(t, k=1.0): return TH0 + SPAN * k * (1 - (1 - clamp(t / T_SW)) ** 1.6)


def time_at(th, k=1.0):
    """When the head passed angle th (inverse of head_at): the age of every point of the stroke."""
    f = np.clip((th - TH0) / (SPAN * k), 0, 1)
    return T_SW * (1 - (1 - f) ** (1 / 1.6))


def rad_fn(R, curl, start=0.7):
    """Centre radius along the sweep: a slow wobble (a rounded triangle) and a steep inward curl over the last 30%."""
    def r(th):
        f = (th - TH0) / SPAN
        x = np.clip((f - start) / (1 - start), 0, 1); x = x * x * (3 - 2 * x)
        return R * (1 + 0.07 * np.sin(3 * th + 0.6)) * (1 - curl * x ** 1.3)
    return r


def _pal(pal, base):
    p = dict(base); p.update(pal); return p


# ---------------------------------------------------------------- fire
FIRE_GLOW = [(15, (96, 26, 52), 0.55), (9, (160, 36, 76), 0.6), (4, (232, 60, 112), 0.8)]     # stepped: flat rings, darkest outside


def swirl_fire(t, P, front, back, pal=BLAZE, s=1.0, d=1):
    pal = _pal(pal, BLAZE)
    t = t + T_LEAD
    R, W, curl = 110 * s, 74 * s, 0.7
    tail = TH0 + 0.35 + SPAN * 0.04 * smooth(0.04, 0.2, t)
    head = max(head_at(t), tail + 0.05)
    grow = 0.6 + 0.4 * out_back(min(1, t / 0.06))
    prof = lambda v: (v ** 0.75) * (1 - v ** 10) ** 0.3                   # a sickle: long thin tail, widest near the head
    rad = rad_fn(R, curl)
    x, y = grid(front)
    th, v, w, inside = spiral_coords(x, y, P, d, TH0, SPAN, rad, tail, head, lambda vv: W * grow * prof(vv) / 2)
    # the needle: the tail runs on thin for a while before the stroke starts
    vn = (th - tail) / max(1e-6, head - tail); nl = 0.35 / max(1e-6, head - tail)
    rn = rad(th); r = np.hypot((x - P[0]) * d, y - P[1])
    needle = (vn < 0) & (vn > -nl) & (np.abs(r - rn) < W * 0.07 * (1 + vn / nl) + 0.6 * s)
    inside = inside | needle
    w = np.where(needle, (r - rn) / (W * 0.07 + 1e-3), w); v = np.where(needle, 0.0, v)
    A = 1 - np.clip((t - time_at(th)) / 0.3, 0, 1)                        # 1 just drawn .. 0 old
    C = (w + 1) / 2                                                        # 0 inner edge .. 1 outer edge
    k = 8.5 + 2.5 * noise1(v * 2.3, 3)                                     # licks: a slanted sawtooth, jittered period and phase
    lick = saw(v * k + 1.3 * C + 0.35 * noise1(v * 5, 5)) - 0.5
    H = 0.6 * A + 0.7 * C + 0.36 * lick * (0.25 + 0.75 * C)
    cool = 1.2 * smooth(0.07, 0.46, t) ** 0.8
    brk = smooth(0.12, 0.24, t)
    gaps = (1 - np.abs(np.sin(math.pi * (v * 3.4 + 0.2 + 0.08 * noise1(v * 4, 9))))) ** 0.6   # V-shaped: pieces end in points
    H = H - cool - 0.55 * brk * gaps * (0.7 + 0.6 * (0.5 + 0.5 * noise1(v * 3, 11)))
    m = posterize(front, H, inside, [(0.12, pal["crimson"]), (0.36, pal["pink"]), (0.62, pal["amber"]), (0.67, pal["yellow"])])
    stepped_glow(back, m, [(px * s, c, a * (1 - smooth(0.2, 0.5, t))) for px, c, a in FIRE_GLOW], front.ss)


# ---------------------------------------------------------------- frost
FROST_GLOW = [(14, (18, 52, 80), 0.6), (8, (30, 90, 140), 0.6), (3, (60, 170, 227), 0.75)]
CRACKS = [[(0.04, 1.2), (0.16, 0.96), (0.27, 1.16), (0.36, 0.98)], [(0.62, 1.12), (0.72, 0.9), (0.8, 1.04)], [(0.9, 0.74), (0.96, 0.86)]]


def swirl_frost(t, P, front, back, pal=FROST, s=1.0, d=1):
    pal = _pal(pal, FROST)
    t = t + T_LEAD
    R, W, curl, K = 106 * s, 80 * s, 0.35, 0.9                           # K: a shorter sweep, a crescent
    prof = lambda v: (v ** 0.7) * (1 - v ** 8) ** 0.35
    rad = rad_fn(R, curl)
    x, y = grid(front)

    def field(tt, wk=1.0):
        tail = TH0 + 0.35 + SPAN * 0.08 * smooth(0.05, 0.25, tt)
        head = max(head_at(tt, K), tail + 0.05)
        grow = 0.6 + 0.4 * out_back(min(1, tt / 0.06))
        return spiral_coords(x, y, P, d, TH0, SPAN, rad, tail, head, lambda vv: W * wk * grow * prof(vv) / 2)
    # after-image: where the blade just was, one flat see-through navy, eroding from its edges
    te = t - 0.05
    if 0.02 < te < 0.34:
        _, va, wa, ina = field(te, 1.5)
        posterize(back, 1 - np.abs(wa) + 0.4 * (va - 0.5), ina, [(0.1 + 0.6 * smooth(0.1, 0.34, te), pal["ghost"])],
                  alpha=0.55 * (1 - smooth(0.14, 0.34, te)))
    th, v, w, inside = field(t)
    A = 1 - np.clip((t - time_at(th, K)) / 0.3, 0, 1)
    C = 1 - np.abs(w - 0.3) ** 1.3                                         # hottest a little toward the outer side
    kf = 3.4 + 0.9 * noise1(v * 2, 21)                                     # feathers: long streaks slanted back, jittered
    feather = saw(v * kf + 1.1 * w + 0.4 * noise1(v * 6, 22)) - 0.5
    H = 0.55 * A + 0.55 * C + 0.4 * feather * (0.5 + 0.5 * C)
    cool = 0.95 * smooth(0.04, 0.5, t) ** 0.7
    brk = smooth(0.14, 0.32, t)
    gaps = (1 - np.abs(np.sin(math.pi * (v * 2.6 + 0.35 + 0.1 * noise1(v * 3, 23))))) ** 0.7
    H = H - cool - 0.45 * brk * gaps
    m = posterize(front, H, inside, [(0.06, pal["deep"]), (0.16, pal["mid"]), (0.42, pal["cyan"]), (0.6, pal["ice"])])
    # cracks: thin flat lines in two clusters, drawn in as the blade passes, fading in steps (no gradient)
    cr = Canvas(front.w, front.h, front.ss)
    a = 0.85 if t < 0.45 else 0.5 if t < 0.7 else 0.25 if t < 0.88 else 0.0
    for cl in CRACKS:
        for (f0, k0), (f1, k1) in zip(cl, cl[1:]):
            u = (t - 0.12 - 0.13 * f1) / 0.06
            if u <= 0 or a <= 0: continue
            a0, a1 = TH0 + 0.35 + SPAN * K * f0, TH0 + 0.35 + SPAN * K * f1
            p0 = (P[0] + d * math.cos(a0) * rad(a0) * k0, P[1] + math.sin(a0) * rad(a0) * k0)
            p1 = (P[0] + d * math.cos(a1) * rad(a1) * k1, P[1] + math.sin(a1) * rad(a1) * k1)
            g = clamp(u)
            pe = (p0[0] + (p1[0] - p0[0]) * g, p0[1] + (p1[1] - p0[1]) * g)
            lens(cr, p0, pe, 1.6 * s, pal["mid"], a, n=6)
            lens(cr, p0, pe, 0.7 * s, pal["cyan"], a, n=6)
    back.paste(cr)
    stepped_glow(back, m, [(px * s, c, al * (1 - smooth(0.15, 0.5, t))) for px, c, al in FROST_GLOW], front.ss)


VARIANTS = {"swirl_fire": swirl_fire, "swirl_frost": swirl_frost}
