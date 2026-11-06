"""lib-fx / impact / ground: a slam, stomp or landing on the ground; the dust is the main element.

Sparks use the organic method of impact/hit; dust uses organic.cloud: the union of wobbly puffs, shaded in flat tones by shifting
the silhouette towards the light (light top, dark underside), curl lines on the big puffs, a hole opening in the middle and noisy
erosion breaking it into wisps (toon dust timing: fast blast on 1s, slow roll-out and dissolve). The anchor is the impact point on
the ground (y = 0 of the floor). Each design is  fn(t, P, front, back, pal=SPARK, s=1.0, d=1).
"""
import math, random
from organic import (SPARK, DUST, Shape, spark_bands, blob, thorn, shard, thorns_at, shards_at, cloud, smooth, out_back, out_cubic)

PAL_SUN = dict(light=(255, 222, 150))
HALO = 0.12
DUR = 0.8
FRAME, ANCHOR, FPS = (440, 300), (220, 236), 30
TAGS = ["impact", "ground", "one-shot", "anchor:ground"]
DUST_BACK = dict(shadow=(96, 100, 90), base=(132, 136, 122), light=(160, 164, 148), curl=(110, 114, 102))
ROCK = ((92, 80, 66), (138, 122, 100))
CATALOG = {
    "slam": dict(name="Nện bụi", status="draft", tags=["heavy", "dust"],
                 desc="a fist or weapon slams the floor: light thorns erupt out of a rolling dust bank (a dark back bank and a light front "
                      "bank, both rolling outward), pebbles arc to both sides, the middle clears first"),
    "crater": dict(name="Vòng chấn đất", status="draft", tags=["heavy", "ring"],
                   desc="a spiky ring flat on the ground races out from the impact while a short burst of light stands up in the middle; "
                        "rocks are thrown to both sides and small dust puffs rise where the ring dies"),
    "geyser": dict(name="Phun đất", status="draft", tags=["heavy", "vertical"],
                   desc="a fountain of light thorns shoots straight up from the impact over a low dust skirt, then droplets rain back down "
                        "while the skirt rolls outward"),
}


def _spark(sh, t, life, pal, s, seed, white=True):
    u = t / life
    first = white and t < 1 / 30 - 1e-6
    bands = [(1.2 * s, pal["light"]), (None, pal["white"])] if first else spark_bands(pal, s, 1 - smooth(0.04, 0.65, u))
    sh.paint(bands, 1.0, fillet=4.0, erode=10 * s * smooth(0.6, 1, u), noise=4.5 * s * smooth(0.45, 1, u), seed=seed,
             backing=(3.5 * s, pal["back"], 0.3 * (1 - smooth(0.4, 0.9, u))))


def _rocks(front, cx, cy, t, seed, n, s, spread=(0.35, 1.2), speed=(220, 380), g=900, life=0.6):
    """Pebbles thrown out of the impact in arcs to both sides, tumbling, a lit top on a dark body."""
    rng = random.Random(seed)
    for i in range(n):
        side = -1 if i % 2 else 1
        ang = -math.pi / 2 + side * rng.uniform(*spread)
        sp = rng.uniform(*speed) * s; dl = rng.uniform(0, 0.05)
        tt = t - dl
        if tt <= 0 or tt > life: continue
        x = cx + math.cos(ang) * sp * tt
        y = cy + math.sin(ang) * sp * tt + 0.5 * g * s * tt * tt
        if y > cy: continue
        r = rng.uniform(3, 6.5) * s * (1 - smooth(0.6, 1, tt / life))
        rot = rng.uniform(0, 6) + tt * rng.uniform(8, 16)
        pts = [(x + math.cos(rot + q) * r * k, y + math.sin(rot + q) * r * k) for q, k in ((0, 1.2), (1.4, 0.9), (2.6, 1.1), (3.9, 0.8), (5.0, 1.0))]
        front.poly(pts, ROCK[0], 1)
        front.poly([(px + (x - px) * 0.35, py_ + (y - py_) * 0.35 - r * 0.25) for px, py_ in pts[:3]] + [(x, y - r * 0.2)], ROCK[1], 1)


def _bank(cx, cy, t, seed, n, s, r0, r1, reach, rise, t0=0.0, life=0.7, sides=(-1, 1)):
    """Puffs of one dust bank: born near the impact, rolling outward along the floor with drag, growing, rising a little."""
    rng = random.Random(seed)
    puffs = []
    for side in sides:
        for i in range(n):
            tt = t - t0 - i * 0.012
            if tt <= 0: continue
            u = min(1.0, tt / life)
            k = (i + 1) / n
            x = cx + side * (6 + reach * k * out_cubic(min(1, tt / 0.45))) * s
            r = (r0 + (r1 - r0) * out_cubic(min(1, tt / 0.3))) * s * (1.15 - 0.45 * k) * (0.9 + 0.2 * rng.random())
            y = cy - r * 0.62 - rise * s * u * (0.5 + k)
            puffs.append((x, y, r * (1 - 0.35 * smooth(0.6, 1, u))))
    return puffs


def ground_slam(t, P, front, back, pal=SPARK, s=1.0, d=1):
    cx, cy = P
    life_d = 0.78
    ud = t / life_d
    hole = []
    if ud > 0.3:
        hr = 70 * s * smooth(0.3, 1, ud)
        hole = [(cx, cy - 22 * s, hr, hr * 0.55)]
    # back bank: darker, taller, behind everything
    cloud(front, _bank(cx, cy, t, 1, 6, s, 10, 34, 150, 28, life=life_d), DUST_BACK, 1.0, off=6, erode=12 * s * smooth(0.55, 1, ud),
          noise=6 * s * smooth(0.4, 1, ud), seed=81, curls=False, holes=hole)
    # light thorns erupting out of the dust
    sh = Shape(front)
    thorns = [(math.radians(a), L, W, b, 4, dl) for a, L, W, b, dl in
              [(-128, 104, 26, 0.2, 0.0), (-52, 112, 27, -0.2, 0.0), (-160, 70, 20, 0.25, 0.02), (-20, 76, 21, -0.25, 0.02),
               (-100, 60, 18, 0.15, 0.03), (-76, 54, 17, -0.15, 0.03), (-172, 40, 14, 0.2, 0.04), (-8, 44, 15, -0.2, 0.04)]]
    sh.poly(blob(cx, cy - 6 * s, 22 * s * (0.7 + 0.3 * out_back(min(1, t / 0.07))), sy=0.55, wob=0.12, freq=5))
    thorns_at(sh, cx, cy - 6 * s, [(a, L * s, W * s, b, r0 * s, dl) for a, L, W, b, r0, dl in thorns], t, 0.42, thin_by=0.55)
    shards_at(sh, cx, cy - 6 * s, [(math.radians(a), 60 * s, 260 * s, 16 * s, 8 * s, 0.25 if a < -90 else -0.25, 0.05) for a in (-140, -40, -110, -66)],
              t, 0.45, g=500 * s)
    if t < 0.42: _spark(sh, t, 0.42, pal, s, 82)
    _rocks(front, cx, cy - 4 * s, t, 83, 10, s)
    # front bank: light, low, rolling outward over the base of the thorns
    cloud(front, _bank(cx, cy, t, 2, 5, s, 8, 26, 175, 14, t0=0.02, life=life_d), DUST, 1.0, off=5, erode=12 * s * smooth(0.55, 1, ud),
          noise=6 * s * smooth(0.4, 1, ud), seed=84, tones=("base", "light", "high"), holes=hole)


def ground_crater(t, P, front, back, pal=SPARK, s=1.0, d=1):
    cx, cy = P
    sy = 0.3
    life = 0.55
    u = t / life
    if u < 1:
        # the flat spiky ring racing out on the floor
        sh = Shape(front)
        g = 0.7 + 0.3 * out_back(min(1, t / 0.07))
        R = (30 + 108 * out_cubic(u)) * s * g
        sh.poly(blob(cx, cy, R, sy=sy, wob=0.05, freq=7, phase=1))
        sh.hole(cx, cy, R * (0.55 + 0.33 * out_cubic(u)), R * (0.55 + 0.33 * out_cubic(u)) * sy)
        angs = [-170, -140, -112, -80, -52, -24, 6, 34, 62, 96, 128, 156]
        thorns = [(math.radians(a), (52 if i % 3 == 0 else 30) * s, (20 if i % 3 == 0 else 15) * s, 0.25 * (1 if math.cos(math.radians(a)) > 0 else -1), R * 0.92)
                  for i, a in enumerate(angs)]
        for a, L, W, b, r0 in thorns:
            tt = t; uu = u
            off = smooth(0.4, 1, uu); thin = 1 - 0.55 * smooth(0.3, 1, uu)
            sh.poly(thorn(cx + math.cos(a) * r0, cy + math.sin(a) * r0 * sy, a, L * g * (1 - 0.4 * off) * 1.3, W * thin * 1.5, b, sy=sy))
        _spark(sh, t, life, pal, s, 91)
    # a short burst of light standing up in the middle
    if t < 0.32:
        up = Shape(front)
        up.poly(blob(cx, cy - 4 * s, 18 * s, sy=0.6, wob=0.15, freq=4))
        thorns_at(up, cx, cy - 4 * s, [(math.radians(a), L * s, W * s, b, 4 * s) for a, L, W, b in
                                       [(-90, 86, 24, 0.0), (-62, 58, 19, -0.2), (-118, 62, 20, 0.2), (-36, 34, 15, -0.3), (-144, 36, 15, 0.3)]], t, 0.32, thin_by=0.55)
        _spark(up, t, 0.32, pal, s, 92)
    _rocks(front, cx, cy - 2 * s, t, 93, 12, s, spread=(0.55, 1.35), speed=(240, 420))
    # small dust puffs rising where the ring slows down
    if t > 0.22:
        tt = t - 0.22
        pf = []
        for side in (-1, 1):
            for i in range(4):
                x = cx + side * (96 + 24 * i) * s * (0.85 + 0.15 * out_cubic(tt / 0.4))
                r = (8 + 6 * (i % 2)) * s * out_cubic(min(1, tt / 0.25))
                pf.append((x, cy - r * 0.6 - 10 * s * tt, r))
        ud = tt / 0.56
        cloud(front, pf, DUST, 1.0, off=4, erode=10 * s * smooth(0.45, 1, ud), noise=5 * s * smooth(0.3, 1, ud), seed=94,
              tones=("base", "light", "high"), curls=False)


def ground_geyser(t, P, front, back, pal=SPARK, s=1.0, d=1):
    cx, cy = P
    ud = t / 0.78
    # low dust skirt behind the fountain
    cloud(front, _bank(cx, cy, t, 5, 4, s, 9, 24, 110, 8, life=0.78), DUST_BACK, 1.0, off=5, erode=10 * s * smooth(0.55, 1, ud),
          noise=5 * s * smooth(0.4, 1, ud), seed=101, curls=False)
    life = 0.5
    u = t / life
    sh = Shape(front)
    if u < 1:
        g = 0.7 + 0.3 * out_back(min(1, t / 0.08))
        sh.poly(blob(cx, cy - 8 * s, 26 * s * g, sy=0.5, wob=0.12, freq=5))
        thorns = [(math.radians(a), L, W, b, 4, dl) for a, L, W, b, dl in
                  [(-90, 176, 34, 0.08, 0.0), (-72, 128, 26, -0.25, 0.01), (-110, 120, 26, 0.25, 0.01), (-54, 78, 20, -0.3, 0.03),
                   (-128, 84, 21, 0.3, 0.03), (-38, 42, 15, -0.35, 0.05), (-144, 46, 15, 0.35, 0.05)]]
        thorns_at(sh, cx, cy - 8 * s, [(a, L * s, W * s, b, r0 * s, dl) for a, L, W, b, r0, dl in thorns], t, life, t_grow=0.09, detach=0.4, thin_by=0.55)
    # droplets thrown up and raining back down
    rng = random.Random(7)
    drops = []
    for i in range(9):
        a = math.radians(-90 + rng.uniform(-38, 38))
        drops.append((a, 60 * s, rng.uniform(330, 470) * s, 18 * s, 9 * s, rng.uniform(-0.2, 0.2), 0.04 + 0.015 * i))
    shards_at(sh, cx, cy - 8 * s, drops, t, 0.62, g=1100 * s)
    _spark(sh, min(t, life * 0.999), life * 1.25, pal, s, 102)
    # front skirt rolling out
    cloud(front, _bank(cx, cy, t, 6, 4, s, 7, 20, 140, 6, t0=0.03, life=0.78), DUST, 1.0, off=4, erode=10 * s * smooth(0.55, 1, ud),
          noise=5 * s * smooth(0.4, 1, ud), seed=103, tones=("base", "light", "high"))


VARIANTS = {"slam": ground_slam, "crater": ground_crater, "geyser": ground_geyser}
