"""fxkit / layers / slash: a weapon smear swept from a to b (rules/vfx/slash). A crescent ribbon along the path a -> b: a needle tail,
the belly near three quarters, a head; a darker tone on the inner edge, a hot tone on the outer edge. The ribbon is a bundle of
lengthwise strands in stroke coordinates (v along the arc, c across it, 0 = inner edge .. 1 = outer edge) and everything that
happens to it happens in those coordinates: the weapon sets the bundle (a sword: 3 strands that touch, one clean outer arc; an axe:
4-6 bands apart by narrow fixed gaps), and when it fades each strand thins towards its own centre line and its tail draws in, so
what is left is a few long thin strokes running the way of the swing: no holes, no noise, no pattern."""
import math
from .. import kind, angles, smooth, out_quint, out_cubic, clamp, Ink, shapes
from .flames import on_twos

N = 48


@kind("slash")
def slash(c, ph, weapon="sword", bend=0.34, width=0.0, span=0.0, strands=0, tones=3, teeth=0, streaks=-1, linger=3.4, track=None, blade=1.0):
    """A weapon smear from a to b. role primary. Designed for Life(0, 0.1, 0.03, 0.27): the attack is the sweep.
    weapon: "sword" (also a blade or great sword: a smooth ribbon of 3 touching strands), "axe" (4-6 parallel bands apart by narrow
    gaps, shorter, thicker, blunt head), "saw" (a sword whose inner edge is toothed); bend: how far the path bows to the upper side,
    share of a-b distance (0 = straight thrust, negative = bows down); width: the widest part, px (0 = the weapon's own: sword 46,
    axe 80, a heavy weapon 70-110); span: share of the arc it covers (0 = sword 1.0, axe 0.7); strands: how many (0 = sword 3, axe 5);
    tones: 3 = main + darker inside + hot edge, 2 = no hot edge, 1 = flat; teeth: notches in the inner edge (0 = clean; saw: 6);
    streaks: hair-thin strokes beside the outer edge (-1 = sword 2, axe 0); linger: how fast it fades (3.4 = short, 2.5 = lingers).
    The belly hangs on the inside of the bow.
    track: a real weapon swing instead of the bow (dict, caller px @2x; build.py --track): {"root_a": (x, y), "root_b": (x, y), "root_up": px,
    "root_dx": px, "turn": "cw" | "ccw", "ease": 1.3}. The tip runs from a to b (the effect's own points), the hilt on a quadratic curve from
    root_a to root_b (control = (midpoint x + root_dx, the higher hilt's y - root_up), as in the approved crescent), the blade turning about the hilt (angle eased by f ** ease, length linear).
    The smear is then the SURFACE the blade swept: its outer edge is the tip's arc, the inner edge the blade's own line (blade = the share of
    the blade, from the tip inwards, that is covered: 1.0 = the whole blade, 0.6 = the tip 60 %); the head keeps the blade's width, the tail
    draws in to a needle that follows the tip's arc. bend, width and span do not apply (span still cuts the tail)."""
    axe = weapon == "axe"
    if width <= 0: width = 80.0 if axe else 46.0
    if span <= 0: span = 0.7 if axe else 1.0
    if strands <= 0: strands = 5 if axe else 3
    if streaks < 0: streaks = 0 if axe else 2
    if weapon == "saw" and teeth <= 0: teeth = 6
    rng = c.rng("design"); s = c.s
    g = ph.grow
    d = on_twos(ph, c)
    if d >= 0.985: return
    fh = min(1.0, 0.45 + 0.5 * out_quint(g) + 0.05 * out_cubic(min(1.0, ph.decay * 3)))      # the head: born 45 % out, runs on
    pre = -c.layer.life.start                                                               # s the layer is born before the hit (a swing: one frame at 15 fps)
    tt = ph.sec + c.layer.life.start                                                        # s from the hit (negative = before it)
    if track:
        if pre > 0 and tt < -1e-6: fh = 0.10 + 0.06 * (1 + tt / pre)                         # before the hit the blade is still at pose A: a thin slice on it
        elif pre > 0: fh = 1.0                                                              # from the hit the blade is at pose B: the smear is whole
        else: fh = min(1.0, 0.45 + 0.55 * out_quint(g))                                      # a real swing: the head must land on the final blade
    lo = (1 - span) * fh                                                                    # where the tail begins
    sg = c.sp.hand * (1 if bend >= 0 else -1)                                                # +1: the inside of the bow is the left of travel
    W = width * s
    OFS = 0.7                                                                              # stroke coordinate lying on the path (bow mode)
    ink = Ink(c, smooth=dict(fillet=0.6, burr=0.6, sigma=0.6) if axe else True)     # the gaps between bands must survive
    L = fh - lo
    if L < 0.06: return

    if track:
        OFS = 1.0
        ra, rb = c.sp.world(track["root_a"]), c.sp.world(track["root_b"])
        cw = str(track.get("turn", "cw")).lower() != "ccw"
        ease = float(track.get("ease", 1.3))
        ctrl = ((ra[0] + rb[0]) / 2 + float(track.get("root_dx", 0.0)), min(ra[1], rb[1]) - float(track.get("root_up", 0.0)))
        a0 = math.atan2(c.sp.a[1] - ra[1], c.sp.a[0] - ra[0]); a1 = math.atan2(c.sp.b[1] - rb[1], c.sp.b[0] - rb[0])
        if cw:
            while a1 <= a0: a1 += 2 * math.pi
        else:
            while a1 >= a0: a1 -= 2 * math.pi
        LA, LB = math.dist(ra, c.sp.a), math.dist(rb, c.sp.b)

        def swing(f):                                                                       # hilt, tip and blade length at path fraction f
            f = clamp(f)
            r = [(1 - f) ** 2 * ra[i] + 2 * (1 - f) * f * ctrl[i] + f * f * rb[i] for i in (0, 1)]
            an = a0 + (a1 - a0) * f ** ease; Lf = LA + (LB - LA) * f
            return r, (r[0] + Lf * math.cos(an), r[1] + Lf * math.sin(an)), Lf

    def prof(v):                                                                           # width along the ribbon, v 0 tail .. 1 head
        v = clamp(v)
        if track: return v ** 0.6                                          # needle tail, the head keeps the blade's full width
        if axe: return v ** 0.6 * (1 - v ** 3) ** 0.45                                       # fat tail, blunt head
        return v ** 0.75 * (1 - v ** 5) ** 0.6

    def at(f):
        if track:                                                                          # the tip, and the unit vector along the blade towards the hilt
            r, p, Lf = swing(f)
            return p, ((r[0] - p[0]) / (Lf or 1e-6), (r[1] - p[1]) / (Lf or 1e-6))
        p, a = c.sp.path(clamp(f), bend)
        return p, (-math.sin(a) * sg, math.cos(a) * sg)                                    # point, unit vector to the inside of the bow

    def pw(f):                                                                             # full ribbon width at arc position f
        if track: return blade * swing(f)[2] * prof((f - lo) / L)                          # the covered share of the blade, tip inwards
        return W * prof((f - lo) / L)

    def lat(f, cc):                                                                        # lateral offset (px, to the inside) of stroke coordinate cc
        return pw(f) * (OFS - cc)

    # ---- the bundle: strand j has the band [c0, c1], a frailty phi (1 = goes first) and its own decay law
    K = strands
    if axe:
        ws = [rng.uniform(0.55, 1.6) for _ in range(K)]
        gaps = [rng.uniform(0.06, 0.10) for _ in range(K - 1)]
        tot = (1 - sum(gaps)) / sum(ws)
        ws = [w * tot for w in ws]
    elif track and K == 3:                                                                  # tip-heavy: the bundle runs from the hilt (c 0) to the tip (c 1)
        ws = [w * rng.uniform(0.9, 1.1) for w in (0.25, 0.33, 0.42)]; t = sum(ws); ws = [w / t for w in ws]
        gaps = [0.0] * (K - 1)
    else:
        base = [0.5, 0.3, 0.2] if K == 3 else [1.0 / K] * K
        ws = [w * rng.uniform(0.85, 1.15) for w in base]; t = sum(ws); ws = [w / t for w in ws]
        gaps = [0.0] * (K - 1)
    bands, x = [], 0.0
    for j in range(K):
        bands.append((x, x + ws[j])); x += ws[j] + (gaps[j] if j < K - 1 else 0.0)
    wmax = max(ws)
    lk = linger / 3.4 * (1.3 if axe else 1.0)
    S = []
    for j in range(K):
        r = c.rng("strand", j)
        phi = (1 - ws[j] / wmax) if axe else 1 - j / max(1, K - 1)
        pj = r.uniform(0.85, 1.15)
        S.append(dict(c0=bands[j][0], c1=bands[j][1],
                      p=((1.6 + 1.6 * phi) if track else (0.8 + 1.5 * phi)) * pj * lk,
                      rut=(0.2 + 0.55 * phi) * r.uniform(0.85, 1.15),
                      lag=0.12 * phi * r.uniform(0.6, 1.0),
                      start=(r.uniform(0.0, 0.1) if axe else 0.0)))
        if track and K == 3:                                                                # the tip strand lasts longest, the hilt strand is short and goes first
            S[j].update(tone=("faint", "mid", "main")[j], lag=0.0, start=0.25 if j == 0 else 0.0)
    END = 0.14 * L                                                                          # length of a tapered end made by fading

    def strand(f0, f1, cin, cout, n=56):
        """The polygon of the band between stroke coordinates cin(f) .. cout(f) for f in f0..f1 (functions of f)."""
        Lp, Rp = [], []
        for i in range(n):
            f = f0 + (f1 - f0) * i / (n - 1)
            p, nn = at(f)
            a, b = lat(f, cin(f)), lat(f, cout(f))
            Lp.append((p[0] + nn[0] * a, p[1] + nn[1] * a)); Rp.append((p[0] + nn[0] * b, p[1] + nn[1] * b))
        return Lp + Rp[::-1]

    live = []
    for j, st in enumerate(S):
        tone = st.get("tone", "main")
        if track:                                                                           # fades from the tail early and hard; the leading edge stays on the blade
            sh = (1 - d) ** st["p"] * (1 - d) ** 0.6
            fa = lo + st["start"] * L + L * (0.55 + 0.35 * clamp((st["rut"] - 0.2) / 0.55)) * out_cubic(d * 1.6)
            fb = fh
        else:
            sh = (1 - d) ** st["p"] * min(1.0, (0.93 - d) / 0.3)                            # the last strokes go out, they do not stop
            fa = lo + st["start"] * L + d * st["rut"] * L
            fb = fh - d * st["lag"] * L
        if sh < 0.03 or fb - fa < 0.05: continue
        cm, hb = (st["c0"] + st["c1"]) / 2, (st["c1"] - st["c0"]) / 2 * sh
        a_cut = fa > lo + 1e-6                                                              # a tail made by fading is tapered
        b_cut = fb < fh - 1e-6
        def tp(f, fa=fa, fb=fb, a_cut=a_cut, b_cut=b_cut):                                  # end taper
            k = 1.0
            if a_cut: k *= clamp((f - fa) / END) ** 0.8
            if b_cut: k *= clamp((fb - f) / END) ** 0.8
            return k
        live.append((j, st, cm, hb, fa, fb, tp))
        ink.add(tone, strand(fa, fb, lambda f: cm - hb * tp(f), lambda f: cm + hb * tp(f)))
    if not live: return

    if tones >= 2:                                                                          # darker tone on the inner part of a strand
        for j, st, cm, hb, fa, fb, tp in live:
            if j != (K - 1 if track and K == 3 else 0): continue
            da, db = max(lo + 0.15 * L, fa), min(lo + 0.9 * L, fb)
            if db - da < 0.05: continue
            fr = 0.38 if not axe else 0.45
            def din(f, cm=cm, hb=hb, tp=tp): return cm - hb * tp(f)
            def dout(f, cm=cm, hb=hb, tp=tp, da=da, db=db, fr=fr):
                u = (f - da) / (db - da)
                return din(f) + 2 * hb * tp(f) * fr * math.sin(math.pi * clamp(u)) ** 0.6
            ink.add("deep", strand(da, db, din, dout))
    if tones >= 3:                                                                          # the hot edge: outer part of the outermost strand, to the head
        j, st, cm, hb, fa, fb, tp = live[-1]
        if track and K == 3 and j != K - 1: j = None
        ha = max(lo + 0.3 * L, fa)
        if j is not None and fb - ha > 0.05:
            def hout(f): return cm + hb * tp(f)
            def hin(f, ha=ha, fb=fb):
                u = (f - ha) / (fb - ha)
                return hout(f) - 2 * hb * tp(f) * 0.6 * smooth(0, 0.3, clamp(u))
            ink.add("hot", strand(ha, fb, hin, hout))

    # teeth (saw): slim wedges bitten out of the inner edge, pointing back to the tail
    for i, v in enumerate(angles(rng, teeth, 0.2, 0.88, gaps=1) if teeth > 0 and d < 0.3 else []):
        r = c.rng("tooth", i)
        v = lo + v * L
        if v > fh * 0.95 or v < lo: continue
        w = pw(v)
        TL = r.uniform(0.06, 0.16) * L; dep = r.uniform(0.3, 0.65)
        (p0, n0), (p1, n1), (pt, nt) = at(v), at(v + TL * 0.35), at(v - TL * 0.65)
        ek = OFS / 0.7
        edge = lambda p, n_, k: (p[0] + n_[0] * w * k * ek, p[1] + n_[1] * w * k * ek)
        poly = shapes.spline([edge(p0, n0, 0.95), edge(p0, n0, 0.7 - dep * 0.35), edge(pt, nt, 0.7 - dep), edge(p1, n1, 0.7 - dep * 0.2),
                              edge(p1, n1, 0.95)], True, 8, sharp=(2,))
        ink.cut("main", poly); ink.cut("deep", poly)

    # hair streaks: hair-thin ribbons running with the outer edge, lagging behind the head; they thin and draw in like the strands
    for i in range(streaks):
        r = c.rng("streak", i)
        off = r.uniform(0.14, 0.4)
        f0 = lo + r.uniform(0.04, 0.4) * L; f1 = min(f0 + r.uniform(0.35, 0.7) * L, lo + 0.88 * L, fh - r.uniform(0.04, 0.12) * L)
        f0 = f0 + d * 0.5 * (f1 - f0)
        sh = (1 - d) ** (1.3 * lk)
        if f1 - f0 < 0.1 or sh < 0.05: continue
        wd = r.uniform(3, 6) * s * sh
        pts, ws_ = [], []
        for k in range(24):
            u = k / 23; f = f0 + (f1 - f0) * u; p, n_ = at(f)
            o = -(0.3 + off) * pw(f) if not track else -(0.03 + 0.25 * off) * pw(f)
            pts.append((p[0] + n_[0] * o, p[1] + n_[1] * o)); ws_.append(wd * math.sin(math.pi * u) ** 0.7)
        ink.add("main", shapes.ribbon(pts, ws_))

    glw = 0.5 if axe else 1.0                                                                # a full glow would fill the gaps between the bands
    if track and pre > 0:                                                                    # a tracked swing: a bright edge along the blade at the head
        k = 1.0 if tt <= 0.07 else clamp(1 - d / 0.35)                                       # white to the frame after the hit, then a hot sliver that thins out
        if k > 0.02:                                                                         # a band of constant width lying on the head's blade line, on the side the tip came from
            (p0, nn), (q0, _) = at(fh), at(max(lo, fh - 0.02))
            tx, ty = q0[0] - p0[0], q0[1] - p0[1]; dot = tx * nn[0] + ty * nn[1]; ox, oy = tx - dot * nn[0], ty - dot * nn[1]
            m = math.hypot(ox, oy) or 1.0; ox, oy = ox / m * 3.6 * s * k, oy / m * 3.6 * s * k
            wb = pw(fh); e1 = (p0[0] + nn[0] * wb, p0[1] + nn[1] * wb)
            ink.add("edge", [p0, e1, (e1[0] + ox, e1[1] + oy), (p0[0] + ox, p0[1] + oy)])
        ink.paint([("faint", c.pal.tone("main"))], glow=0.0, opacity={"faint": 0.4})                  # the hilt strand: faint, it does not feed the glow
        ink.paint([("mid", c.pal.tone("main")), ("main", c.pal.tone("main")), ("deep", c.pal.tone("deep")),
                   ("hot", c.pal.tone("hot")), ("edge", c.pal.tone("white") if tt <= 0.07 else c.pal.tone("hot"))],
                  glow=glw, opacity={"mid": 0.7})
    elif ph.first:
        ink.paint([("main", c.pal.tone("hot")), ("hot", c.pal.tone("white"))], glow=glw)
    else:
        ink.paint([("main", c.pal.tone("main")), ("deep", c.pal.tone("deep")), ("hot", c.pal.tone("hot"))], glow=glw)
