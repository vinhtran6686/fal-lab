"""lib-fx / melee / blade: slashes of an edged weapon.

Each design is  fn(t, P, front, back, pal=..., s=1.0, d=1)  drawing the slash t seconds after it starts; P is the centre of the
swing; d = -1 mirrors it.

swirl_fire / swirl_frost were studied from a reference GIF (lib-fx/REFERENCE-GIF.md; study not shipped; method and layer table in
lib-fx/RECIPE-swirl.md). One parametric spiral drives both: the head sweeps 330 degrees in about four drawings (measured), the
tail barely moves and ends in a straight needle, the radius has a slow wobble (a rounded triangle, never a compass circle) and
drops steeply over the last quarter so the head hooks into the centre. Colour runs ALONG the stroke by age (hot head, cool tail),
built from flat masks clipped to the body, not from distance bands. Glow: two passes from the body only (fxcore.glow_under).
"""
import math, random
from PIL import ImageFilter
from fxcore import Canvas, clamp, smooth, out_back, lens, mix, glow_under
from organic import Shape, thorn, shard
from palettes import BLAZE, FROST

FPS = 30
FRAME, ANCHOR = (380, 380), (190, 190)
DUR = 0.52
TAGS = ["melee", "blade", "slash", "swirl", "one-shot", "anchor:centre"]
PAL_SUN = BLAZE
CATALOG = {
    "swirl_fire": dict(name="Xoáy chém lửa", status="draft", tags=["fire", "medium"], palette=BLAZE, halo=(0.0, 8), frame=(460, 460), anchor=(230, 230),
                       desc="a pink-fire swirl slash: a thick yellow blade with a pink band on its inner side, pink licks reaching back "
                            "into the yellow and a needle tail sweeps 330 degrees in four drawings and hooks into the centre, then "
                            "breaks in place into four crescents of different sizes and fates (fade, split, curl tighter) that thin, "
                            "turn and drift out, cooling to amber and pink, ending in sparks; two-scale pink glow"),
    "swirl_frost": dict(name="Xoáy chém băng", status="draft", tags=["ice", "water", "medium"], palette=FROST, dur=0.95, halo=(0.0, 8),
                        desc="a frost swirl slash: an ice-white blade with feathered cyan and blue zones that cool from the tail toward "
                             "the head sweeps and hooks inward over a dark-blue see-through after-image; the blue zones open into long "
                             "holes and the blade dissolves into shards while thin, dim crack lines in two clusters stay a while"),
}


def _layer(c): return Canvas(c.w, c.h, c.ss)


# ---------------------------------------------------------------- the spiral
TH0, SPAN = math.pi, math.radians(330)                                    # starts on the left (west), sweeps clockwise


def _rad(th, R, curl, ph=0.6):
    f = (th - TH0) / SPAN
    return R * (1 + 0.07 * math.sin(3 * th + ph)) * (1 - curl * smooth(0.7, 1.0, f) ** 1.3)


def _pt(P, th, r, d): return P[0] + d * math.cos(th) * r, P[1] + math.sin(th) * r


PROFILES = {
    "fire": lambda v: (v ** 0.35) * (1 - v ** 12) ** 0.2,                 # thick at once, flat, blunt head
    "frost": lambda v: (v ** 0.4) * (1 - v ** 6) ** 0.4,                   # thick, pointed head
    "sliver": lambda v: math.sin(math.pi * v) ** 0.55,
}


def _edges(P, a, b, R, curl, W, d, prof, v0=0.0, v1=1.0, n=60, band=None, offset=0.0, bulge=None):
    """Outer and inner edge points of the stroke between sweep angles a (tail) and b (head), for v in v0..v1.
    band(v) -> fraction: instead of the whole width, the strip hugging the INNER edge that is band(v) of the width."""
    out, inn = [], []
    for i in range(n + 1):
        v = v0 + (v1 - v0) * i / n
        th = a + (b - a) * v
        w = W * PROFILES[prof](v) * (bulge(v) if bulge else 1)
        r = _rad(th, R, curl) + offset * W
        ri = max(1.0, r - w / 2)
        ro = ri + w * (band(v) if band else 1)
        out.append(_pt(P, th, ro, d)); inn.append(_pt(P, th, ri, d))
    return out, inn


def _poly(o, i): return o + i[::-1]


def _tangent(P, th, R, curl, d):
    x0, y0 = _pt(P, th, _rad(th, R, curl), d); x1, y1 = _pt(P, th + 0.01, _rad(th + 0.01, R, curl), d)
    return math.atan2(y1 - y0, x1 - x0)


def _needle(P, a, R, curl, W, d, L):
    """The straight needle the tail leaves on, along the tangent, backwards."""
    x, y = _pt(P, a, _rad(a, R, curl) - W * 0.02, d)
    return thorn(x, y, _tangent(P, a, R, curl, d) + math.pi, L, W * 0.16, 0.0, p=1.0)


def _licks(sh, P, a, b, R, curl, W, d, prof, band, spec):
    """Licks rooted on the band's outer boundary, reaching back (against the sweep) into the colour above it."""
    for v, Lk, Wk, tilt in spec:
        th = a + (b - a) * v
        w = W * PROFILES[prof](v)
        r = max(1.0, _rad(th, R, curl) - w / 2) + w * band(v)
        x, y = _pt(P, th, r, d)
        sh.poly(thorn(x, y, _tangent(P, th, R, curl, d) + math.pi - tilt * d, W * Lk, W * Wk, 0.35 * d, p=1.25))


# ---------------------------------------------------------------- fire
FIRE_LICKS = [(0.3, 0.55, 0.16, 0.25), (0.38, 0.3, 0.1, 0.4), (0.5, 0.62, 0.18, 0.2), (0.57, 0.24, 0.09, 0.5),     # long, short, ...
              (0.7, 0.5, 0.15, 0.3), (0.86, 0.34, 0.12, 0.35)]
NOTCHES = [(0.44, 0.14, 0.12), (0.66, 0.1, 0.1), (0.8, 0.16, 0.13)]       # small notches on the outer edge (v, length, width)
# break pieces: fraction range, width, drift (px), turn (rad), fate, life (s)
PIECES = [((0.05, 0.34), 0.55, 16, 0.3, "fade", 0.17), ((0.36, 0.5), 0.42, 10, 0.2, "fade", 0.14),
          ((0.52, 0.82), 0.66, 9, 0.22, "split", 0.26), ((0.84, 1.0), 0.95, 3, 0.4, "curl", 0.3)]


def swirl_fire(t, P, front, back, pal=BLAZE, s=1.0, d=1):
    pal = dict(BLAZE, **pal)
    R, W, curl = 108 * s, 82 * s, 0.7
    T_SW, T_BR = 0.16, 0.175
    head = TH0 + SPAN * (1 - (1 - clamp(t / T_SW)) ** 1.6)                 # measured: 100 / 205 / 282 / 330 deg at 1-4 drawings
    tail = TH0 + SPAN * 0.08 * smooth(0.04, 0.18, t)
    head = max(head, tail + 0.05)
    Wt = W * (0.55 + 0.45 * out_back(min(1, t / 0.06)))
    heat = 1 - smooth(0.1, 0.4, t)
    ly = _layer(front)
    if t < T_BR:
        band = lambda v: clamp(0.24 + 0.76 * (1 - v) ** 2.6)              # the inner pink band: whole width at the tail, thin at the head
        body = Shape(ly)
        o, i = _edges(P, tail, head, R, curl, Wt, d, "fire")
        body.poly(_poly(o, i)); body.poly(_needle(P, tail, R, curl, Wt, d, R * 0.55 * smooth(0.02, 0.08, t)))
        for v, Lk, Wk in NOTCHES:                                         # a few small notches cut into the outer edge
            th = tail + (head - tail) * v
            x, y = _pt(P, th, _rad(th, R, curl) + Wt * PROFILES["fire"](v) / 2 + 1, d)
            body.poly(thorn(x, y, _tangent(P, th, R, curl, d) + math.pi + 0.5 * d, Wt * Lk, Wt * Wk, 0.0, p=1.0), on=False)
        body.paint([(None, mix(pal["yellow"], pal["amber"], 1 - heat))], 1.0, fillet=2.0)
        pink = Shape(ly)
        o, i = _edges(P, tail, head, R, curl, Wt, d, "fire", band=band)
        pink.poly(_poly(o, i)); pink.poly(_needle(P, tail, R, curl, Wt, d, R * 0.55 * smooth(0.02, 0.08, t)))
        _licks(pink, P, tail, head, R, curl, Wt, d, "fire", band, FIRE_LICKS)
        pink.paint([(None, pal["pink"])], 1.0, fillet=1.5, clip=body)
        deep = Shape(ly)                                                  # a hot-pink core deeper on the inner side
        o, i = _edges(P, tail, head, R, curl, Wt, d, "fire", band=lambda v: 0.4 * band(v), v0=0.15, v1=0.95)
        deep.poly(_poly(o, i))
        deep.paint([(None, pal["hotpink"])], 1.0, fillet=1.5, clip=body)
    else:
        rng = random.Random(5)
        for k, ((f0, f1), wk, drift, turn, fate, life) in enumerate(PIECES):
            b = (t - T_BR) / life
            if not 0 <= b < 1: continue
            a0, a1 = tail + (head - tail) * f0, tail + (head - tail) * f1
            rot = turn * (1 - (1 - b) ** 2)                               # keeps turning clockwise, slowing
            mid = (a0 + a1) / 2
            ln = (a1 - a0) * (1 - 0.35 * b) / 2
            Rk = R * (1 + drift * s / R * b) * ((1 - 0.25 * b) if fate == "curl" else 1)
            wv = Wt * wk * (1 - b) ** 1.5
            if wv < 1.0 * s: continue
            segs = [(mid - ln + rot, mid + ln + rot)]
            if fate == "split" and b > 0.3:                               # opens a gap in the middle
                g = ln * 0.4 * smooth(0.3, 0.8, b)
                segs = [(mid - ln + rot, mid - g + rot), (mid + g + rot, mid + ln + rot)]
            for (sa, sb) in segs:
                bul = lambda v: 0.12 + 1.3 * v ** 2.2                     # a claw: thick leading end, a long sharp trailing point
                piece = Shape(ly)
                o, i = _edges(P, sa, sb, Rk, curl * (1.2 if fate == "curl" else 1), wv, d, "sliver", offset=0.25 * b, bulge=bul)
                piece.poly(_poly(o, i))
                piece.paint([(None, pal["hotpink"] if b > 0.6 else pal["pink"])], 1.0, fillet=1.5)
                if b < 0.65:                                              # a yellow, then amber, tip at the leading end
                    tip = Shape(ly)
                    o, i = _edges(P, sa + (sb - sa) * 0.5, sb, Rk, curl * (1.2 if fate == "curl" else 1), wv * 0.6, d, "sliver", offset=0.25 * b + 0.12)
                    tip.poly(_poly(o, i))
                    tip.paint([(None, mix(pal["yellow"], pal["amber"], b / 0.65))], 1.0, fillet=1.5, clip=piece)
        # sparks where the pieces die
        for j in range(8):
            tb = T_BR + 0.08 + rng.uniform(0, 0.18)
            u = (t - tb) / 0.14
            if not 0 <= u < 1: continue
            th = tail + (head - tail) * rng.uniform(0.05, 0.98)
            x, y = _pt(P, th, _rad(th, R, curl) * rng.uniform(0.9, 1.15), d)
            r = (2.2 - 0.8 * (j % 2)) * s * (1 - u)
            ly.poly(shard(x, y - 5 * s * u, -math.pi / 2 + rng.uniform(-0.7, 0.7), r * 3, r * 1.6), pal["pink"] if j % 3 else pal["yellow"], 1 - u)
    gh = 1 - smooth(0.15, 0.45, t)
    glow_under(back, ly, [((200, 40, 90), 1.5 * gh, 22 * s), ((255, 80, 130), 1.4 * gh, 6 * s)])
    front.paste(ly)


# ---------------------------------------------------------------- frost
# crack clusters (fraction of the sweep, radius factor): a long one over the after-image, a medium one, a tiny one
CRACKS = [[(0.04, 1.2), (0.16, 0.96), (0.27, 1.16), (0.36, 0.98)], [(0.62, 1.12), (0.72, 0.9), (0.8, 1.04)], [(0.9, 0.74), (0.96, 0.86)]]
FEATHERS = [(0.34, 0.9, 0.22, 0.3), (0.46, 0.5, 0.14, 0.45), (0.58, 1.0, 0.24, 0.25), (0.7, 0.45, 0.13, 0.4), (0.82, 0.7, 0.18, 0.3)]


def _frost_body(c, P, tail, head, R, curl, Wt, d, cool, dis, pal, s):
    """The blade: ice white, with cyan then blue zones on the inner side that grow from the tail toward the head as it cools
    (cool 0..1), feathered licks reaching back into the white; the blue zones open into long holes as it dissolves (dis)."""
    cyan_band = lambda v: clamp(0.2 + 0.6 * (1 - v) ** 1.6 + 0.85 * cool)
    blue_band = lambda v: clamp(0.08 + 0.5 * (1 - v) ** 2 + 1.0 * max(0.0, cool - 0.35))
    body = Shape(c)
    o, i = _edges(P, tail, head, R, curl, Wt, d, "frost")
    body.poly(_poly(o, i)); body.poly(_needle(P, tail, R, curl, Wt, d, R * 0.5))
    holes = None
    if dis > 0:
        holes = Shape(c)
        for k, (v, Lk, Wk, tilt) in enumerate(FEATHERS):                 # long lens-shaped holes along the tangent
            th = tail + (head - tail) * v
            x, y = _pt(P, th, _rad(th, R, curl) - Wt * PROFILES["frost"](v) * 0.12, d)
            holes.poly(thorn(x, y, _tangent(P, th, R, curl, d) + math.pi, Wt * Lk * (0.4 + 0.9 * dis), Wt * Wk * (0.6 + 1.6 * dis), 0.3 * d, p=0.9))
    er = dict(erode=46 * s * dis ** 1.3, noise=18 * s * dis, seed=17, cut=holes)
    body.paint([(1.2 * s, pal["cyan"]), (None, pal["ice"])], 1.0, fillet=2.0, **er)
    cy = Shape(c)
    o, i = _edges(P, tail, head, R, curl, Wt, d, "frost", band=cyan_band)
    cy.poly(_poly(o, i)); cy.poly(_needle(P, tail, R, curl, Wt, d, R * 0.5))
    _licks(cy, P, tail, head, R, curl, Wt, d, "frost", cyan_band, FEATHERS)
    cy.paint([(None, pal["cyan"] if cool < 0.6 else pal["mid"])], 1.0, fillet=1.5, clip=body, **er)
    bl = Shape(c)
    o, i = _edges(P, tail, head, R, curl, Wt, d, "frost", band=blue_band)
    bl.poly(_poly(o, i)); bl.poly(_needle(P, tail, R, curl, Wt, d, R * 0.5))
    _licks(bl, P, tail, head, R, curl, Wt, d, "frost", blue_band, [(v + 0.05, Lk * 0.7, Wk * 0.8, tl) for v, Lk, Wk, tl in FEATHERS[::2]])
    bl.paint([(None, pal["mid"] if cool < 0.5 else pal["blue"])], 1.0, fillet=1.5, clip=body, **er)


def swirl_frost(t, P, front, back, pal=FROST, s=1.0, d=1):
    pal = dict(FROST, **pal)
    R, W, curl = 106 * s, 80 * s, 0.3
    T_SW = 0.16
    sweep = lambda tt: (TH0 + SPAN * 0.12 * smooth(0.06, 0.26, tt), TH0 + SPAN * 0.9 * (1 - (1 - clamp(tt / T_SW)) ** 1.6))   # a shorter sweep: a crescent
    tail, head = sweep(t); head = max(head, tail + 0.05)
    Wt = W * (0.55 + 0.45 * out_back(min(1, t / 0.06)))
    cool = smooth(0.07, 0.24, t)
    dis = smooth(0.12, 0.36, t)
    # after-image: where the blade has just been, dark blue, see-through, feathered (its own blurred layer, behind)
    te = t - 0.05
    if 0.02 < te < 0.32:
        ta, ha = sweep(te)
        ag = _layer(back)
        sh = Shape(ag)
        o, i = _edges(P, ta, max(ha, ta + 0.05), R * 1.04, curl, Wt * 1.45, d, "frost", offset=-0.08)
        sh.poly(_poly(o, i)); sh.poly(_needle(P, ta, R, curl, Wt * 1.6, d, R * 0.6))
        sh.paint([(None, pal["ghost"])], 0.6 * (1 - smooth(0.12, 0.32, te)), fillet=3.0, erode=14 * s * smooth(0.1, 0.32, te),
                 noise=12 * s * smooth(0.08, 0.32, te), seed=3)
        ag.img = ag.img.filter(ImageFilter.GaussianBlur(2.5 * ag.ss))
        back.paste(ag)
    # the blade
    if dis < 1:
        ly = _layer(front)
        _frost_body(ly, P, tail, head, R, curl, Wt, d, cool, dis, pal, s)
        gh = 1 - smooth(0.12, 0.55, t)
        glow_under(back, ly, [((34, 100, 160), 1.0 * gh, 18 * s), (pal["cyan"], 1.2 * gh, 5 * s)])
        front_blade = ly
    else:
        front_blade = None
    # cracks: thin, dim blue, two clusters, drawn in as the blade passes, peak, then stay faint
    cr = _layer(back)
    for ci, cl in enumerate(CRACKS):
        for (f0, k0), (f1, k1) in zip(cl, cl[1:]):
            tb = 0.12 + 0.13 * f1
            u = (t - tb) / 0.06
            if u <= 0: continue
            a = (0.85 * smooth(0, 1, u) * (1 - 0.6 * smooth(0.45, 0.6, t))) * (1 - smooth(0.78, 0.92, t))
            if a <= 0.01: continue
            a0, a1 = TH0 + SPAN * f0, TH0 + SPAN * f1
            p0 = _pt(P, a0, _rad(a0, R, curl) * k0, d); p1 = _pt(P, a1, _rad(a1, R, curl) * k1, d)
            g = clamp(u)
            pe = (p0[0] + (p1[0] - p0[0]) * g, p0[1] + (p1[1] - p0[1]) * g)
            lens(cr, p0, pe, (1.8 if ci == 0 else 1.4) * s, pal["mid"], a, n=6)
            lens(cr, p0, pe, 0.7 * s, pal["cyan"], a, n=6)
        f, k = cl[-1]
        if 0.14 + 0.13 * f < t < 0.6:                                     # a glint at the end of each cluster
            x, y = _pt(P, TH0 + SPAN * f, _rad(TH0 + SPAN * f, R, curl) * k, d)
            cr.ellipse(x, y, 1.6 * s, 1.6 * s, pal["ice"], 0.9 * (1 - smooth(0.4, 0.6, t)))
    glow_under(back, cr, [(pal["mid"], 0.5, 3 * s)])
    back.paste(cr)
    if front_blade is not None: front.paste(front_blade)
    # shards left where it broke: blue slivers near the cracks, fading
    ly = _layer(front)
    for k, (f, kk) in enumerate([CRACKS[0][1], CRACKS[0][3], CRACKS[1][1], CRACKS[2][0], CRACKS[1][2]]):
        tb = 0.34 + 0.04 * k
        u = (t - tb) / 0.42
        if not 0 <= u < 1: continue
        a0 = TH0 + SPAN * f
        x, y = _pt(P, a0, _rad(a0, R, curl) * kk * 0.94, d)
        L, Wd = (18 - 3 * (k % 3)) * s * (1 - 0.5 * u), (6 - (k % 2)) * s * (1 - 0.5 * u)
        a = _tangent(P, a0, R, curl, d) + math.pi + 0.3 * (k % 2 - 0.5)
        ly.poly(thorn(x, y, a, L, Wd, 0.5 * d, p=1.3), pal["blue"], 0.8 * (1 - smooth(0.4, 1, u)))
        ly.poly(thorn(x, y, a, L * 0.55, Wd * 0.4, 0.5 * d, p=1.3), pal["cyan"], 0.8 * (1 - smooth(0.4, 1, u)))
    front.paste(ly)


VARIANTS = {"swirl_fire": swirl_fire, "swirl_frost": swirl_frost}
