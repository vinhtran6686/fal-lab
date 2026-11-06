"""lib-fx / impact / hit: melee hit sparks (fist, blade, blunt), the spark shown on the frame that deals damage.

Built with _core/organic.py (DESIGN.md §8): one hand-drawn silhouette (wobbly core + curved thorns, filleted), coloured by distance
to its edge (white core -> yellow -> orange -> red tips), a dark see-through backing, then noisy erosion breaks it into droplets.
Timing (30 fps): drawing 1 is pure white at 70% size, 2-3 drawings at full size (overshoot), then it keeps growing while it cools,
hollows out and breaks up. Spike rhythm: 1-3 hero thorns, 3-5 medium, a few nubs, uneven spacing, all curling one way.
Each design is  fn(t, P, front, back, pal=SPARK, s=1.0, d=1).
"""
import math
from organic import (SPARK, Shape, spark_bands, blob, thorn, shard, ring_halves, thorns_at, shards_at, smooth, out_back, out_cubic)

PAL_SUN = dict(light=(255, 214, 110))                     # tint of the soft glow build.py adds
HALO = 0.3
DUR = 0.42
FRAME, ANCHOR, FPS = (300, 300), (150, 150), 30
TAGS = ["impact", "hit", "melee", "one-shot", "anchor:contact"]
LIFE = 0.38
FAT = 1.55                                                # thorn width factor: fat, hand-painted thorns, not lines
CATALOG = {
    "star": dict(name="Nổ sao", status="draft", tags=["radial", "medium"],
                 desc="the classic hit spark: a white-hot core with two long hero thorns, four medium and three nubs curling one way, "
                      "two straight rays across it, droplets flung from the hero tips"),
    "chevron": dict(name="Mũi chéo", status="draft", tags=["directional", "medium"], frame=(320, 260), anchor=(74, 130),
                    desc="a directional spray: two wide wings open into a chevron from the contact, thorns and slivers stream away "
                         "along the hit"),
    "ring": dict(name="Vòng gai", status="draft", tags=["radial", "heavy"],
                 desc="a spiky ring: the core is punched out from the start and keeps widening, its rim stays white-hot while thorns "
                      "of three sizes spray off the outside"),
    "cross": dict(name="Chữ thập chí mạng", status="draft", tags=["crit", "heavy"],
                  desc="the critical hit: four long straight pillars in an X, four short curled thorns between them, a thin ring racing "
                       "out and droplets off the pillar tips"),
}


def burst(front, t, cx, cy, thorns, core, shards, pal, s, seed, hollow=0.0, sy=1.0, life=LIFE, wob=0.12):
    """The shared spark: core + thorns + droplets in one silhouette, white first drawing, then cooling, hollowing and breaking up."""
    u = t / life
    if u >= 1: return
    sh = Shape(front)
    g = 0.7 + 0.3 * out_back(min(1, t / 0.07)) + 0.3 * u                # keeps growing until it is gone
    rc = core * s * g * (1 - 0.35 * smooth(0.4, 1, u))
    sh.poly(blob(cx, cy, rc, sy=sy, wob=wob, freq=5, phase=seed))
    thorns_at(sh, cx, cy, [(a, L * s, W * s * FAT, b, r0 * s) + tuple(x[5:]) for x in thorns for a, L, W, b, r0 in [x[:5]]], t, life, sy=sy, thin_by=0.55)
    shards_at(sh, cx, cy, [(a, d0 * s, sp * s, L * s, W * s, b, dl) for a, d0, sp, L, W, b, dl in shards], t, life * 1.15, sy=sy)
    if hollow > 0:
        hr = rc * hollow * smooth(0.3, 0.75, u)
        if hr > 7 * s: sh.hole(cx, cy, hr, hr * sy)                   # a hole opens only once it reads as a hole, not a speck
    first = t < 1 / 30 - 1e-6
    bands = [(1.2 * s, pal["light"]), (None, pal["white"])] if first else spark_bands(pal, s, 1 - smooth(0.04, 0.6, u))
    sh.paint(bands, 1.0, fillet=4.0, erode=10 * s * smooth(0.62, 1, u), noise=4.5 * s * smooth(0.5, 1, u), seed=seed,
             backing=(3.5 * s, pal["back"], 0.32 * (1 - smooth(0.4, 0.9, u))))


def _deg(a): return math.radians(a)


def hit_star(t, P, front, back, pal=SPARK, s=1.0, d=1):
    cx, cy = P
    A = (lambda deg: _deg(deg) if d > 0 else math.pi - _deg(deg))
    B = 0.32 * d                                                          # every thorn curls the same way (a swirl)
    thorns = [  # angle, length, width, bend, base radius
        (A(-38), 108, 24, B, 8), (A(148), 96, 22, B, 8),                 # two heroes
        (A(22), 66, 17, B, 8), (A(78), 58, 16, B, 8), (A(205), 62, 17, B, 8), (A(-102), 70, 18, B, 8),   # medium
        (A(112), 26, 12, B, 6), (A(-148), 30, 13, B, 6), (A(-4), 24, 11, B, 6),                           # nubs
        (A(-12), 128, 5, 0.05 * d, 4, 0.01), (A(190), 112, 5, 0.05 * d, 4, 0.01),                        # two straight rays
    ]
    shards = [(A(-44), 70, 280, 18, 8, B, 0.05), (A(-30), 64, 220, 12, 6, B, 0.08), (A(140), 64, 260, 16, 7, B, 0.05),
              (A(158), 58, 200, 11, 5, B, 0.09), (A(70), 46, 180, 10, 5, B, 0.07)]
    burst(front, t, cx, cy, thorns, 32, shards, pal, s, seed=11, hollow=0.9)


def hit_chevron(t, P, front, back, pal=SPARK, s=1.0, d=1):
    cx, cy = P
    A = (lambda deg: _deg(deg) if d > 0 else math.pi - _deg(deg))
    thorns = [
        (A(-42), 96, 36, 0.18 * d, 0), (A(40), 90, 34, -0.18 * d, 0),     # the two wings of the chevron
        (A(-3), 132, 19, 0.06 * d, 6),                                    # hero along the hit
        (A(-18), 74, 15, 0.12 * d, 6), (A(16), 62, 14, -0.12 * d, 6),     # medium
        (A(-64), 28, 12, 0.3 * d, 4), (A(66), 30, 12, -0.3 * d, 4),       # nubs
    ]
    shards = [(A(-24), 92, 300, 22, 9, 0.2 * d, 0.03), (A(8), 120, 340, 44, 10, 0.05 * d, 0.02), (A(26), 86, 260, 16, 7, -0.2 * d, 0.05),
              (A(-46), 70, 240, 12, 6, 0.3 * d, 0.07), (A(48), 66, 220, 12, 6, -0.3 * d, 0.08)]
    burst(front, t, cx + d * 14 * s, cy, [(a, L, W, b, r0) for a, L, W, b, r0 in thorns], 16, shards, pal, s, seed=21, hollow=0.0, wob=0.18)


def hit_ring(t, P, front, back, pal=SPARK, s=1.0, d=1):
    cx, cy = P
    u = t / LIFE
    if u >= 1: return
    sh = Shape(front)
    g = 0.7 + 0.3 * out_back(min(1, t / 0.07))
    R = (40 + 26 * out_cubic(u)) * s * g
    sh.poly(blob(cx, cy, R, wob=0.07, freq=6, phase=2))
    sh.hole(cx, cy, R * (0.45 + 0.4 * out_cubic(u)), R * (0.45 + 0.4 * out_cubic(u)))
    B = 0.25 * d
    angs = [-80, -52, -18, 8, 34, 66, 98, 128, 160, 196, 226, 252]
    sizes = [(70, 18), (24, 12), (44, 15), (22, 11), (40, 15), (26, 12), (64, 18), (22, 11), (42, 15), (26, 12), (38, 14), (20, 11)]
    thorns = [(_deg(a), L, W, B, R / s - 6) for a, (L, W) in zip(angs, sizes)]
    thorns_at(sh, cx, cy, [(a, L * s, W * s * FAT, b, r0 * s) for a, L, W, b, r0 in thorns], t, LIFE, detach=0.35, thin_by=0.55)
    shards_at(sh, cx, cy, [(_deg(a), 80 * s, 240 * s, 14 * s, 7 * s, B, 0.05) for a in (-84, 100, 30, 200)], t, LIFE * 1.15)
    first = t < 1 / 30 - 1e-6
    bands = [(1.2 * s, pal["light"]), (None, pal["white"])] if first else spark_bands(pal, s, 1 - smooth(0.04, 0.7, u))
    sh.paint(bands, 1.0, fillet=4.0, erode=9 * s * smooth(0.62, 1, u), noise=4 * s * smooth(0.5, 1, u), seed=31,
             backing=(3.5 * s, pal["back"], 0.32 * (1 - smooth(0.4, 0.9, u))))


def hit_cross(t, P, front, back, pal=SPARK, s=1.0, d=1):
    cx, cy = P
    B = 0.3 * d
    thorns = [(_deg(a), 120, 21, 0.0, 6) for a in (-45, 45, 135, 225)] + \
             [(_deg(a), 46, 16, B, 6, 0.02) for a in (-90, 0, 90, 180)]
    shards = [(_deg(a + o), 96, 300, 18, 8, 0.0, 0.05) for a in (-45, 45, 135, 225) for o in (-6,)] + \
             [(_deg(a), 60, 200, 10, 5, B, 0.08) for a in (-20, 70, 160, 250)]
    # a thin ring racing out from the core
    u = t / LIFE
    if 0.03 < t and u < 0.75:
        ur = (t - 0.03) / (0.75 * LIFE - 0.03)
        rr = (26 + 90 * out_cubic(ur)) * s
        ring = Shape(front)
        for half in ring_halves(cx, cy, rr, rr, 7 * s * (1 - ur) + 1.5 * s): ring.poly(half)
        ring.paint(spark_bands(pal, s, 1 - ur), 1 - smooth(0.6, 1, ur), fillet=0)
    burst(front, t, cx, cy, thorns, 28, shards, pal, s, seed=41, hollow=0.85)


VARIANTS = {"star": hit_star, "chevron": hit_chevron, "ring": hit_ring, "cross": hit_cross}
