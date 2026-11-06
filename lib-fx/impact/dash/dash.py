"""lib-fx / impact / dash: the impact at the end of a dash or charge (a body or weapon arriving at speed).

Same organic method as impact/hit (DESIGN.md §8), stretched along the travel: the dash comes from -x (d=1) and hits at the anchor;
the brightest edge leads, thorns and slivers trail back along the path, droplets fly on ahead.
Each design is  fn(t, P, front, back, pal=SPARK, s=1.0, d=1).
"""
import math
from organic import (SPARK, Shape, spark_bands, blob, thorn, shard, crescent, ring_halves, thorns_at, shards_at, smooth, out_back, out_cubic)

PAL_SUN = dict(light=(255, 214, 110))
HALO = 0.3
DUR = 0.45
FRAME, ANCHOR, FPS = (340, 280), (236, 140), 30
TAGS = ["impact", "dash", "melee", "one-shot", "directional", "anchor:contact"]
LIFE = 0.4
CATALOG = {
    "wall": dict(name="Vách lưỡi liềm", status="draft", tags=["medium"],
                 desc="a tall white crescent slams up at the contact, its back edge torn into short curled thorns that trail along "
                      "the dash; droplets peel off both tips"),
    "pierce": dict(name="Xuyên vòng", status="draft", tags=["heavy", "piercing"],
                   desc="a white bulge punches through a standing ring of air while long thorns stream back along the dash like a comet"),
    "comet": dict(name="Sao chổi", status="draft", tags=["fast", "light"], frame=(400, 280), anchor=(236, 140),
                  desc="speed thorns converge from behind into a forward-pointing burst at the contact; slivers keep flying ahead"),
}


def _paint(sh, t, u, pal, s, seed, first_white=True):
    first = first_white and t < 1 / 30 - 1e-6
    bands = [(1.2 * s, pal["light"]), (None, pal["white"])] if first else spark_bands(pal, s, 1 - smooth(0.04, 0.65, u))
    sh.paint(bands, 1.0, fillet=4.0, erode=10 * s * smooth(0.62, 1, u), noise=4.5 * s * smooth(0.5, 1, u), seed=seed,
             backing=(3.5 * s, pal["back"], 0.32 * (1 - smooth(0.4, 0.9, u))))


def dash_wall(t, P, front, back, pal=SPARK, s=1.0, d=1):
    cx, cy = P
    u = t / LIFE
    if u >= 1: return
    g = 0.7 + 0.3 * out_back(min(1, t / 0.07))
    e = out_cubic(u)
    x = cx + d * 14 * s * e
    ry = (58 + 40 * e) * s * g
    rxo = (36 - 10 * e) * s * g
    sh = Shape(front)
    sh.poly(crescent(x, cy, rxo, -2 * s, ry, d=d))
    # the torn back edge: thorns rooted along the crescent's inner edge, pointing back down the dash, curling away from the middle
    for k, (ph, L, W) in enumerate([(-0.78, 30, 16), (-0.55, 48, 20), (-0.3, 26, 14), (-0.08, 56, 20), (0.14, 30, 15),
                                    (0.36, 46, 19), (0.6, 24, 13), (0.8, 34, 15)]):
        tt = t - 0.01 * k
        if tt <= 0: continue
        uu = tt / LIFE
        gg = 0.7 + 0.3 * out_back(min(1, tt / 0.07))
        off = smooth(0.4, 1, uu); thin = 1 - 0.55 * smooth(0.3, 1, uu)
        bx, by = x - d * 2 * s * math.cos(ph * math.pi / 2), cy + ry * 0.96 * math.sin(ph * math.pi / 2)
        ang = (math.pi if d > 0 else 0) - d * ph * 0.7
        sh.poly(thorn(bx - d * L * s * 0.4 * off, by, ang, L * s * gg * (1 - 0.4 * off), W * s * thin * 1.4,
                      0.35 * (1 if ph > 0 else -1) * d))
    tips = [(-math.pi / 2 - d * 0.5, 1), (math.pi / 2 + d * 0.5, -1)]
    shards_at(sh, x, cy, [(a if d > 0 else math.pi - a, ry * 0.9, 220 * s, 16 * s, 8 * s, 0.3 * sg * d, 0.05) for a, sg in
                          [(-math.pi / 2 - 0.5, 1), (math.pi / 2 + 0.5, -1), (math.pi + 0.35, 1), (math.pi - 0.35, -1)]], t, LIFE * 1.15)
    _paint(sh, t, u, pal, s, 51)


def dash_pierce(t, P, front, back, pal=SPARK, s=1.0, d=1):
    cx, cy = P
    u = t / LIFE
    if u >= 1: return
    g = 0.7 + 0.3 * out_back(min(1, t / 0.07))
    e = out_cubic(u)
    back_ang = math.pi if d > 0 else 0.0
    # the standing ring of air the bulge punches through (behind the bulge)
    rx, ry = (10 + 10 * e) * s * g, (52 + 46 * e) * s * g
    rg = Shape(front)
    for half in ring_halves(cx + d * (4 + 10 * e) * s, cy, rx, ry, (15 - 8 * e) * s, taper=0.55): rg.poly(half)
    rg.paint(spark_bands(pal, s, 1 - smooth(0.04, 0.7, u)), 1 - smooth(0.7, 1, u), fillet=0, erode=6 * s * smooth(0.6, 1, u),
             noise=4 * s * smooth(0.45, 1, u), seed=61, backing=(3 * s, pal["back"], 0.28 * (1 - smooth(0.4, 0.9, u))))
    sh = Shape(front)
    sh.poly(crescent(cx, cy, 26 * s * g, -12 * s * g, 34 * s * g * (1 + 0.2 * e), d=d))
    thorns = [(back_ang + d * a, L, W, 0.12 * d * (1 if a > 0 else -1), 6) for a, L, W in
              [(-0.08, 150, 20), (0.12, 128, 18), (-0.32, 96, 16), (0.38, 104, 17), (-0.62, 60, 14), (0.66, 52, 13), (0.0, 70, 12)]]
    thorns_at(sh, cx, cy, [(a, L * s, W * s * 1.4, b, r0 * s) for a, L, W, b, r0 in thorns], t, LIFE, detach=0.45, thin_by=0.55)
    shards_at(sh, cx, cy, [((0 if d > 0 else math.pi) + a, 40 * s, 300 * s, 18 * s, 8 * s, 0.1, 0.04) for a in (-0.35, 0.05, 0.4)], t, LIFE * 1.15)
    _paint(sh, t, u, pal, s, 62)


def dash_comet(t, P, front, back, pal=SPARK, s=1.0, d=1):
    cx, cy = P
    u = t / LIFE
    if u >= 1: return
    back_ang, fwd = (math.pi, 0.0) if d > 0 else (0.0, math.pi)
    sh = Shape(front)
    g = 0.7 + 0.3 * out_back(min(1, t / 0.07))
    sh.poly(blob(cx, cy, 20 * s * g, sy=0.8, wob=0.15, freq=4, phase=1))
    # speed thorns converging from behind, slightly fanned
    back_th = [(back_ang + d * a, L, W, 0.06 * d * (1 if a > 0 else -1), 4) for a, L, W in
               [(0.0, 170, 22), (-0.1, 130, 16), (0.12, 140, 17), (-0.22, 90, 13), (0.24, 84, 13)]]
    # a forward-pointing burst at the contact
    fwd_th = [(fwd + d * a, L, W, 0.3 * d, 6, 0.01) for a, L, W in
              [(0.0, 64, 22), (-0.5, 52, 18), (0.55, 48, 17), (-1.05, 34, 14), (1.1, 30, 13), (-1.6, 22, 12), (1.6, 24, 12)]]
    thorns_at(sh, cx, cy, [(a, L * s, W * s * 1.4, b, r0 * s) for a, L, W, b, r0 in back_th], t, LIFE, detach=0.25, keep=0.5, thin_by=0.6)
    thorns_at(sh, cx, cy, [(a, L * s, W * s * 1.5, b, r0 * s, dl) for a, L, W, b, r0, dl in fwd_th], t, LIFE, detach=0.5, thin_by=0.55)
    shards_at(sh, cx, cy, [(fwd + a, 56 * s, 320 * s, 20 * s, 9 * s, 0.15, dl) for a, dl in ((-0.3, 0.03), (0.0, 0.02), (0.32, 0.05), (-0.7, 0.07), (0.7, 0.06))],
              t, LIFE * 1.15)
    _paint(sh, t, u, pal, s, 71)


VARIANTS = {"wall": dash_wall, "pierce": dash_pierce, "comet": dash_comet}
