"""fxkit / layers / slash: a weapon smear swept from a to b (rules/vfx/slash). A crescent ribbon along the path a -> b: a needle tail,
the belly near three quarters, a head; a darker tone on the inner edge, a hot tone on the outer edge. The ribbon is a bundle of
lengthwise strands in stroke coordinates (v along the arc, c across it, 0 = inner edge .. 1 = outer edge) and everything that
happens to it happens in those coordinates: the weapon sets the bundle (a sword: 3 strands that touch, one clean outer arc; an axe:
4-6 bands apart by narrow fixed gaps), and when it fades each strand thins towards its own centre line and its tail draws in, so
what is left is a few long thin strokes running the way of the swing: no holes, no noise, no pattern."""
import math
from .. import kind, angles, smooth, out_quint, out_cubic, clamp, Ink, shapes
from ..ink import _disc
from .flames import on_twos

N = 48


def _plane(sw, face):
    """The swing plane as screen vectors: k (flatness), A (the long axis, x times face), P (the short axis, y down, mirrored with the face), sqrt(1 - k^2)."""
    k = float(sw.get("k", 0.3)); ro = math.radians(float(sw.get("roll", 0.0)))
    return k, (face * math.cos(ro), math.sin(ro)), (-face * math.sin(ro), math.cos(ro)), math.sqrt(max(0.0, 1 - k * k))


def plane_point(sw, u, rho, face=1):
    """Screen offset from the shoulder of the point at angle u (deg: 0 ahead, 90 near, 180 behind, 270 far) and radius rho of the swing
    plane `sw` (the `swing` parameter of the slash kind), and its depth (+ = near the viewer). The tip of a weapon swung in that plane
    draws the circle seen from the game's camera: an ellipse k as tall as wide, turned by `roll`, a near point a little bigger."""
    k, A, P, sq = _plane(sw, face); r = math.radians(u); dep = math.sin(r) * sq; pr = rho * (1 + 0.16 * dep)
    return (pr * (math.cos(r) * A[0] + math.sin(r) * k * P[0]), pr * (math.cos(r) * A[1] + math.sin(r) * k * P[1])), dep


def fit_swing(sw, face, world):
    """Fit a plane swing to MEASURED points (keys tip_a, tip_b, pivot of the `swing` dict, caller px @2x; optional pivot_b, root_a, root_b, via).
    The tip is at tip_a at the start and at tip_b at the end; its circle of radius r round the pivot is seen as the ellipse of `plane_point`
    (k = flatness, roll). Given the pivot and k each tip fixes its own angle and radius in closed form: the offset from the pivot, in the plane's own
    axes (A along the long axis, P / k across), is pr * (cos u, sin u) with pr = r (1 + 0.16 sin(u) sqrt(1 - k^2)). Nothing is guessed:
    u0, u1, ra, rb all come from the two tips. The pivot may move from `pivot` to `pivot_b` (the body shifts between the two poses) and the
    radius runs from ra to rb with the angle. `via` = near (default: the path crosses the near half, in front of the body) or far.
    root_a / root_b (the hilt end of the VISIBLE blade, a pose that hides the hilt gives the point where the blade vanishes) set the blade line: the
    inner edge of the smear and the white edge lie on the line root -> tip in each pose. Returns the numbers the kind needs (canvas px).
    THREE tips (`tip_c`, the middle pose of the swing: the blade pointing at the viewer, the nearest point of the arc; optional `pivot_c`, `root_c`):
    the same closed form for the third tip, and when `k` is not given it is FITTED: the k in 0.10 .. 0.60 for which the radius of the middle tip equals
    the radius run from A to B at its angle, so the ellipse through the three tips is found, not assumed (`pivot_c` = the torso centre x at the hand height). The path then runs A -> C -> B: `fc` is the path fraction at
    which the tip is at C (share of the angle A -> C), and the angle, radius, pivot and hilt are piecewise linear with a knot at C."""
    k, A, P, sq = _plane(sw, face)
    ta, tb, pa = world(sw["tip_a"]), world(sw["tip_b"]), world(sw["pivot"])
    pb = world(sw["pivot_b"]) if sw.get("pivot_b") else pa
    tc = world(sw["tip_c"]) if sw.get("tip_c") else None
    pc = (world(sw["pivot_c"]) if sw.get("pivot_c") else ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2)) if tc else None

    def polar(t, o, k, A, P, sq):
        dx, dy = t[0] - o[0], t[1] - o[1]
        a_ = dx * A[0] + dy * A[1]; p_ = (dx * P[0] + dy * P[1]) / k
        u = math.degrees(math.atan2(p_, a_)) % 360.0
        return u, math.hypot(a_, p_) / (1 + 0.16 * math.sin(math.radians(u)) * sq)
    want = -1 if str(sw.get("via", "near")).lower() == "far" else 1                     # the half the path crosses: + near

    def legs(kk):                                                                       # angles and radii of the tips for the flatness kk; the path A -> (C) -> B unwrapped
        k_, A_, P_, sq_ = _plane(dict(sw, k=kk), face)
        u0, ra = polar(ta, pa, k_, A_, P_, sq_); ub, rb = polar(tb, pb, k_, A_, P_, sq_)
        cands = sorted((ub + 360.0 * m for m in (-2, -1, 0, 1, 2)), key=lambda x: abs(x - u0))
        u1 = next((x for x in cands if want * math.sin(math.radians((u0 + x) / 2)) > 0), cands[0])
        if not tc: return u0, ra, None, None, u1, rb
        uc0, rc = polar(tc, pc, k_, A_, P_, sq_)
        mid = (u0 + u1) / 2; lo_, hi_ = min(u0, u1), max(u0, u1)
        alts = [uc0 + 360.0 * m for m in (-2, -1, 0, 1, 2)]
        inside = [x for x in alts if lo_ - 1e-9 <= x <= hi_ + 1e-9]
        return u0, ra, min(inside or alts, key=lambda x: abs(x - mid)), rc, u1, rb
    kfit = None
    if tc and sw.get("kfit"):                                                           # the flatness for which the middle tip sits on the radius run from A to B
        best = None
        for i in range(0, 101):
            kk = 0.10 + 0.005 * i
            u0_, ra_k, uc_, rc_k, u1_, rb_k = legs(kk)
            t_ = (uc_ - u0_) / (u1_ - u0_) if u1_ != u0_ else 0.5
            err = abs(rc_k - (ra_k + (rb_k - ra_k) * t_)) / ((ra_k + rb_k) / 2)
            if best is None or err < best[0] - 1e-9: best = (err, kk)
        kfit = best[1]; k, A, P, sq = _plane(dict(sw, k=kfit), face)
    u0, ra, uc, rc, u1, rb = legs(kfit or k)
    ra_, rb_ = sw.get("root_a"), sw.get("root_b")
    corr = []
    for key, tip, piv, u, r, root in (("a", ta, pa, u0, ra, ra_), ("b", tb, pb, u1, rb, rb_)):
        if not root: corr.append((0.0, 0.0, float(sw.get("blade", 0.75)))); continue
        rw = world(root); bl = min(1.0, math.dist(rw, tip) / max(math.dist(piv, tip), 1e-6))
        (x, y), _ = plane_point(dict(sw, k=k), u, r * (1 - bl), face)
        corr.append((rw[0] - (piv[0] + x), rw[1] - (piv[1] + y), bl))
    out = dict(u0=u0, u1=u1, ra=ra, rb=rb, pa=pa, pb=pb, corr=corr, tip_a=ta, tip_b=tb)
    if tc:
        fc = min(0.8, max(0.2, (uc - u0) / (u1 - u0))) if u1 != u0 else 0.5
        out.update(c=True, uc=uc, rc=rc, pc=pc, tip_c=tc, fc=fc, root_c=world(sw["root_c"]) if sw.get("root_c") else None,
                   root_a=world(ra_) if ra_ else None, root_b=world(rb_) if rb_ else None)
        if kfit: out["k"] = kfit
    return out


@kind("slash")
def slash(c, ph, weapon="sword", bend=0.34, width=0.0, span=0.0, strands=0, tones=3, teeth=0, streaks=-1, linger=3.4, track=None, blade=1.0, swing=None):
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
    draws in to a needle that follows the tip's arc. bend, width and span do not apply (span still cuts the tail).
    swing: the same smear for a swing in a PLANE seen from the game's camera (dict; build.py --swing): {"k": flatness (1 = flat to the
    screen, 0.3 = lying on the ground, 0.6 = slanted), "roll": deg, "u0", "u1": the blade's angle in its plane at the start and the end
    (0 ahead, 90 near, 180 behind, 270 far; u grows ahead -> near -> behind -> far), "r": px the tip is from the shoulder a at s = 1
    (0 = the distance a -> b), "blade": the share of the radius that is swept, "ease", "w_near": thickness of the near part, px at s = 1 (0 = from the radius)}. a is the shoulder, b only says which way it
    faces. The tip runs on a circle around a; what we see is its projection (plane_point). It is drawn in two halves: the far half
    (depth < 0) on the BACK canvas, cooler and thin, the near half on the FRONT canvas, bright and thick; everything else (fh, fade,
    three strands, white edge) is the track mode's. Overrides track.
    FITTED swing: give "tip_a", "tip_b" (the tip at the start and at the hit), "pivot" (the torso centre at the height of the blade; optional "pivot_b" if the
    torso moved, "root_a" / "root_b" the hilt end of the visible blade, "via" near | far) and u0, u1, r come from the points (`fit_swing`): the smear's
    outer edge passes through both tips, its inner edge and the white edge lie on the blade line of each pose. k and roll are still the plane's.
    LEAD swing (fitted, with "tip_c" = the tip in the middle pose, optional "pivot_c", "root_c"; or "lead": 1 for two tips): the smear must READ in its direction.
    The head (the end at the tip's present place) is the thickest, brightest, blunt end with the white edge, the tail a needle that fades first: the width
    grows from tail to head (it never exceeds the blade's own projected length behind the head), and the end cap is the head's blade line, so nothing hooks back.
    With "tip_c" the path runs A -> C -> B (`fit_swing`: k fitted when not given) and the smear is born two frames before the hit: the frame plan at 15 fps is
    frame 1 = pose A (a thin slice on blade A), frame 2 = pose C (the stroke A -> C, head at C), frame 3 = pose B and the hit (the whole stroke, head at B), then it fades tail first."""
    axe = weapon == "axe"
    if width <= 0: width = 80.0 if axe else 46.0
    if span <= 0: span = 0.7 if axe else 1.0
    if strands <= 0: strands = 5 if axe else 3
    if streaks < 0: streaks = 0 if axe else 2
    if weapon == "saw" and teeth <= 0: teeth = 6
    rng = c.rng("design"); s = c.s
    sw = swing
    if sw: track = None
    tracked = bool(track or sw)
    fit = fit_swing(sw, c.sp.hand, c.sp.world) if sw and sw.get("tip_a") and sw.get("tip_b") and sw.get("pivot") else None
    if fit and fit.get("k"): sw = dict(sw, k=fit["k"])                                      # a fitted flatness (three tips, k not given)
    lead = bool(fit and (fit.get("c") or sw.get("lead")))
    fc = fit["fc"] if fit and fit.get("c") else None
    g = ph.grow
    d = on_twos(ph, c)
    if d >= 0.985: return
    fh = min(1.0, 0.45 + 0.5 * out_quint(g) + 0.05 * out_cubic(min(1.0, ph.decay * 3)))      # the head: born 45 % out, runs on
    pre = -c.layer.life.start                                                               # s the layer is born before the hit (a swing: one frame at 15 fps)
    tt = ph.sec + c.layer.life.start                                                        # s from the hit (negative = before it)
    if tracked:
        if pre > 0 and tt < -1e-6 and fc:                                                    # three poses: the slice on blade A, then the head at C
            sv = (tt + pre) / pre                                                              # 0 at the first frame .. 1 at the hit; pose C is at 0.5
            fh = 0.07 if sv <= 0.25 else (0.07 + (fc - 0.07) * (sv - 0.25) / 0.25 if sv < 0.5 - 1e-6 else fc + (1 - fc) * (sv - 0.5) / 0.5)
        elif pre > 0 and tt < -1e-6: fh = 0.10 + 0.06 * (1 + tt / pre)                         # before the hit the blade is still at pose A: a thin slice on it
        elif pre > 0: fh = 1.0                                                              # from the hit the blade is at pose B: the smear is whole
        else: fh = min(1.0, 0.45 + 0.55 * out_quint(g))                                      # a real swing: the head must land on the final blade
    lo = (1 - span) * fh                                                                    # where the tail begins
    sg = c.sp.hand * (1 if bend >= 0 else -1)                                                # +1: the inside of the bow is the left of travel
    W = width * s
    OFS = 0.7                                                                              # stroke coordinate lying on the path (bow mode)
    sm = dict(fillet=0.6, burr=0.6, sigma=0.6) if axe else True
    ink = Ink(c, smooth=sm, canvas=c.front if sw else None)                              # swing: the near half is always in front of the character
    fink = Ink(c, smooth=sm, canvas=c.back) if sw else None                                 # and the far half behind it
    L = fh - lo
    if L < (0.03 if lead else 0.06): return

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

    if sw:
        OFS = 1.0
        face = c.sp.hand; O = c.sp.a
        k_, A_, P_, sq_ = _plane(sw, face)
        u0, u1 = float(sw.get("u0", 235)), float(sw.get("u1", 430)); ease = float(sw.get("ease", 1.3))
        R = float(sw.get("r", 0.0)) * s or c.sp.len; bl = float(sw.get("blade", 0.75)); blade = bl
        if fit: u0, u1, R = fit["u0"], fit["u1"], (fit["ra"] + fit["rb"]) / 2
        if fc: R = (fit["ra"] + fit["rc"] + fit["rb"]) / 3
        q_ = (1 - k_) / 0.75; wmin = 7.0 * s; mnear = min(2.4, 1 + 1.4 * q_)
        wnear = float(sw.get('w_near', 0) or 0) * s                                          # the near part's own thickness (px at s = 1) instead of the radius-based one; 0 = old

        def tk(f):                                                                          # three tips: which leg of A -> C -> B and how far along it (slow out of A, straight into B)
            f = clamp(f)
            return (0, (f / fc) ** ease) if f <= fc else (1, (f - fc) / (1 - fc))
        def mix3(va, vc, vb, f):                                                            # piecewise linear through A, C, B (numbers or points)
            i, t_ = tk(f); a_, b_ = (va, vc) if i == 0 else (vc, vb)
            return a_ + (b_ - a_) * t_ if isinstance(a_, float) else (a_[0] + (b_[0] - a_[0]) * t_, a_[1] + (b_[1] - a_[1]) * t_)
        def uf(f): return mix3(u0, fit["uc"], u1, f) if fc else u0 + (u1 - u0) * clamp(f) ** ease
        def lerp2(a_, b_, f): t_ = clamp(f) ** ease; return (a_[0] + (b_[0] - a_[0]) * t_, a_[1] + (b_[1] - a_[1]) * t_)
        def pt3(f, rho):
            (x, y), dep = plane_point(sw, uf(f), rho, face)
            o = (mix3(fit["pa"], fit["pc"], fit["pb"], f) if fc else lerp2(fit["pa"], fit["pb"], f)) if fit else O   # a fitted swing: the pivot moves with the body
            return (o[0] + x, o[1] + y), dep
        def Rf(f):
            if not fit: return R
            return mix3(fit["ra"], fit["rc"], fit["rb"], f) if fc else fit["ra"] + (fit["rb"] - fit["ra"]) * clamp(f) ** ease
        def hilt_old(f):
            (ca, cb) = fit["corr"]; t_ = clamp(f) ** ease; blf = ca[2] + (cb[2] - ca[2]) * t_
            h, _ = pt3(f, Rf(f) * (1 - blf)); cx, cy = lerp2(ca, cb, f)
            return (h[0] + cx, h[1] + cy)
        if fc:                                                                              # the hilt runs through the three measured hilt ends
            ca_, cb_ = fit["corr"]
            hA = fit["root_a"] or hilt_old(0.0); hB = fit["root_b"] or hilt_old(1.0)
            if fit["root_c"]: hC = fit["root_c"]
            else:
                blc = (ca_[2] + cb_[2]) / 2; h_, _ = pt3(fc, Rf(fc) * (1 - blc)); hC = (h_[0] + (ca_[0] + cb_[0]) / 2, h_[1] + (ca_[1] + cb_[1]) / 2)
        def hilt_pt(f):                                                                      # the inner end of the swept blade, screen px
            if fc: return mix3(hA, hC, hB, f)
            if not fit: return pt3(f, R * (1 - bl))[0]
            (ca, cb) = fit["corr"]; t_ = clamp(f) ** ease; blf = ca[2] + (cb[2] - ca[2]) * t_
            h, _ = pt3(f, Rf(f) * (1 - blf)); cx, cy = lerp2(ca, cb, f)
            return (h[0] + cx, h[1] + cy)
        def depth(f): return math.sin(math.radians(uf(f))) * sq_
        def mfac(f):                                                                        # how thick the stroke is allowed to be here: far thin, near fat
            sn = math.sin(math.radians(uf(f)))
            return clamp(1 + sn * (1.4 if sn >= 0 else 0.7) * q_, 0.3, 2.4)
        def swing_at(f):                                                                    # tip, unit normal of the tip's arc towards the inside, projected blade
            if fit:                                                                         # a fitted swing: the smear is the surface the blade sweeps, so the inner edge runs along the blade line
                tip, _ = pt3(f, Rf(f)); hl = hilt_pt(f); vx, vy = hl[0] - tip[0], hl[1] - tip[1]; m = math.hypot(vx, vy) or 1e-6
                return tip, (vx / m, vy / m), m
            tip, _ = pt3(f, R); hilt, _ = pt3(f, R * (1 - bl))
            r = math.radians(uf(f)); sgn = 1 if u1 >= u0 else -1
            dep = math.sin(r) * sq_
            kk = 0.16 * sq_ * math.cos(r)                                                    # d(perspective)/du
            pr = R * (1 + 0.16 * dep)
            tx = pr * (-math.sin(r) * A_[0] + math.cos(r) * k_ * P_[0]) + R * kk * (math.cos(r) * A_[0] + math.sin(r) * k_ * P_[0])
            ty = pr * (-math.sin(r) * A_[1] + math.cos(r) * k_ * P_[1]) + R * kk * (math.cos(r) * A_[1] + math.sin(r) * k_ * P_[1])
            m = math.hypot(tx, ty) or 1e-6; nx, ny = -ty / m, tx / m
            if nx * (hilt[0] - tip[0]) + ny * (hilt[1] - tip[1]) < 0: nx, ny = -nx, -ny
            return tip, (nx, ny), nx * (hilt[0] - tip[0]) + ny * (hilt[1] - tip[1])

    if lead:                                                                               # a stroke that reads in its direction: it is swept on the path's own normal (the side of the hilt) and grows towards the head
        def lead_n(f):                                                                      # the tip, and the unit normal of its path towards the hilt side
            tip, nn, _ = swing_at(f)
            if fh < 0.09: return tip, nn                                                    # the slice on blade A follows the blade
            e = 0.06; p1, p0 = swing_at(min(1.0, f + e))[0], swing_at(max(0.0, f - e))[0]
            tx, ty = p1[0] - p0[0], p1[1] - p0[1]; m_ = math.hypot(tx, ty) or 1e-6; nx, ny = -ty / m_, tx / m_
            hl = hilt_pt(f)
            if nx * (hl[0] - tip[0]) + ny * (hl[1] - tip[1]) < 0: nx, ny = -nx, -ny      # the hilt side of the path
            return tip, (nx, ny)
        LEADW = float(sw.get('lead_w', 0.26))
        sliver = fh < 0.09                                                                  # the thin slice on blade A: as wide as the blade itself
        Wh = swing_at(fh)[2] if sliver else min(swing_at(fh)[2], LEADW * R)       # the head's width: the blade's projected length, at most a fifth of the radius

    def prof(v):                                                                           # width along the ribbon, v 0 tail .. 1 head
        v = clamp(v)
        if lead: return min(1.0, v / 0.85) ** 1.15                           # a lead stroke: a needle tail, the width grows steadily, the last 15 % is the blunt head at full width
        if tracked: return v ** 0.6                                          # needle tail, the head keeps the blade's full width
        if axe: return v ** 0.6 * (1 - v ** 3) ** 0.45                                       # fat tail, blunt head
        return v ** 0.75 * (1 - v ** 5) ** 0.6

    def at(f):
        if sw and lead: return lead_n(f)
        if sw:
            p, nn, _ = swing_at(f); return p, nn
        if track:                                                                          # the tip, and the unit vector along the blade towards the hilt
            r, p, Lf = swing(f)
            return p, ((r[0] - p[0]) / (Lf or 1e-6), (r[1] - p[1]) / (Lf or 1e-6))
        p, a = c.sp.path(clamp(f), bend)
        return p, (-math.sin(a) * sg, math.cos(a) * sg)                                    # point, unit vector to the inside of the bow

    def pw(f):                                                                             # full ribbon width at arc position f
        if lead: return Wh * prof((f - lo) / L)                                             # head widest, tail a needle
        if sw and fit:                                                                      # the blade's own projected length, fatter where near (as the plain swing)
            return max(wmin * min(mfac(f), 1.0), swing_at(f)[2] * mfac(f) / mfac(1.0)) * prof((f - lo) / L)
        if sw:                                                                              # a stroke: fat where near, thin where far
            g = wnear if wnear else R * bl * k_
            fl = wmin * (min(mfac(f), 1.0) if wnear else mfac(f))                         # the floor: with w_near it does not fatten the near part
            return max(fl, g * (1 + 0.16 * depth(f)) * mfac(f) / mnear) * prof((f - lo) / L)
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
    elif tracked and K == 3:                                                                  # tip-heavy: the bundle runs from the hilt (c 0) to the tip (c 1)
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
    if sw: lk *= (R / 120.0) ** 0.5                                                         # a small swing fades slower, a 120 px one as before
    S = []
    for j in range(K):
        r = c.rng("strand", j)
        phi = (1 - ws[j] / wmax) if axe else 1 - j / max(1, K - 1)
        pj = r.uniform(0.85, 1.15)
        S.append(dict(c0=bands[j][0], c1=bands[j][1],
                      p=((1.6 + 1.6 * phi) if tracked else (0.8 + 1.5 * phi)) * pj * lk,
                      rut=(0.2 + 0.55 * phi) * r.uniform(0.85, 1.15),
                      lag=0.12 * phi * r.uniform(0.6, 1.0),
                      start=(r.uniform(0.0, 0.1) if axe else 0.0)))
        if tracked and K == 3:                                                                # the tip strand lasts longest, the hilt strand is short and goes first
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

    def parts(f0, f1):                                                                      # swing: [(fa, fb, near)]: the far part (depth < 0) and the near part
        n = 64; fs = [f0 + (f1 - f0) * i / n for i in range(n + 1)]; out = []; a = f0; cur = depth(f0) >= 0
        for x, y in zip(fs, fs[1:]):
            nx = depth(y) >= 0
            if nx != cur:
                lo_, hi_ = x, y
                for _ in range(24):
                    mid = (lo_ + hi_) / 2
                    if (depth(mid) >= 0) == cur: lo_ = mid
                    else: hi_ = mid
                out.append((a, (lo_ + hi_) / 2, cur)); a = (lo_ + hi_) / 2; cur = nx
        out.append((a, f1, cur)); return out

    def put(tone, f0, f1, cin, cout):                                                       # one band of a strand, to the right half of the effect
        if not sw: ink.add(tone, strand(f0, f1, cin, cout)); return
        for fa_, fb_, near in parts(f0, f1):
            if fb_ - fa_ < 1e-4: continue
            (ink if near else fink).add(tone, strand(fa_, fb_, cin, cout, n=max(8, int(56 * (fb_ - fa_) / max(f1 - f0, 1e-6)))))

    live = []
    for j, st in enumerate(S):
        tone = st.get("tone", "main")
        if tracked:                                                                           # fades from the tail early and hard; the leading edge stays on the blade
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
        put(tone, fa, fb, lambda f: cm - hb * tp(f), lambda f: cm + hb * tp(f))
    if not live: return

    if tones >= 2:                                                                          # darker tone on the inner part of a strand
        for j, st, cm, hb, fa, fb, tp in live:
            if j != (K - 1 if tracked and K == 3 else 0): continue
            da, db = max(lo + 0.15 * L, fa), min(lo + 0.9 * L, fb)
            if db - da < 0.05: continue
            fr = 0.38 if not axe else 0.45
            def din(f, cm=cm, hb=hb, tp=tp): return cm - hb * tp(f)
            def dout(f, cm=cm, hb=hb, tp=tp, da=da, db=db, fr=fr):
                u = (f - da) / (db - da)
                return din(f) + 2 * hb * tp(f) * fr * math.sin(math.pi * clamp(u)) ** 0.6
            put("deep", da, db, din, dout)
    if tones >= 3:                                                                          # the hot edge: outer part of the outermost strand, to the head
        j, st, cm, hb, fa, fb, tp = live[-1]
        if tracked and K == 3 and j != K - 1: j = None
        ha = max(lo + 0.3 * L, fa)
        if j is not None and fb - ha > 0.05:
            def hout(f): return cm + hb * tp(f)
            def hin(f, ha=ha, fb=fb):
                u = (f - ha) / (fb - ha)
                return hout(f) - 2 * hb * tp(f) * 0.6 * smooth(0, 0.3, clamp(u))
            put("hot", ha, fb, hin, hout)

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
            o = -(0.3 + off) * pw(f) if not tracked else -(0.03 + 0.25 * off) * pw(f)
            pts.append((p[0] + n_[0] * o, p[1] + n_[1] * o)); ws_.append(wd * math.sin(math.pi * u) ** 0.7)
        ink.add("main", shapes.ribbon(pts, ws_))

    glw = 0.5 if axe else 1.0                                                                # a full glow would fill the gaps between the bands
    if tracked and pre > 0:                                                                  # a tracked swing: a bright edge along the blade at the head
        k = 1.0 if tt <= 0.07 else clamp(1 - d / 0.35)                                       # white to the frame after the hit, then a hot sliver that thins out
        hnear = (not sw) or depth(fh) >= 0                                                   # a head on the far side is dim: no white edge there
        hink = ink if hnear else fink
        if k > 0.02:                                                                         # a band of constant width lying on the head's blade line, on the side the tip came from
            (p0, nn), (q0, _) = at(fh), at(max(lo, fh - 0.02))
            tx, ty = q0[0] - p0[0], q0[1] - p0[1]; dot = tx * nn[0] + ty * nn[1]; ox, oy = tx - dot * nn[0], ty - dot * nn[1]
            m = math.hypot(ox, oy) or 1.0; ox, oy = ox / m * 3.6 * s * k, oy / m * 3.6 * s * k
            wb = pw(fh); e1 = (p0[0] + nn[0] * wb, p0[1] + nn[1] * wb)
            if sw:                                                                           # the blade's own line in its plane: from the tip towards the shoulder, as long as the stroke is thick
                hl = hilt_pt(fh); rx, ry = hl[0] - p0[0], hl[1] - p0[1]; rm = math.hypot(rx, ry) or 1.0
                wl = rm if lead else min(wb, rm)                                        # a lead stroke: the white edge runs the whole visible blade
                e1 = (p0[0] + rx / rm * wl, p0[1] + ry / rm * wl)
            quad = [p0, e1, (e1[0] + ox, e1[1] + oy), (p0[0] + ox, p0[1] + oy)]
            if hnear: hink.add("edge", quad)
            if tt < -1e-6 and not (lead and fh >= 0.09):                                     # the frame before the hit: the white sliver gets a rim of the smear's own colour
                hink.add("rim", quad); hink.set("rim", _disc(hink.mask("rim"), 3.0 * s * hink.ss, True))
        ink.paint([("faint", c.pal.tone("main"))], glow=0.0, opacity={"faint": 0.4})                  # the hilt strand: faint, it does not feed the glow
        ink.paint(([("rim", c.pal.tone("main"))] if ink.mask("rim").any() else []) + [("mid", c.pal.tone("main")), ("main", c.pal.tone("main")), ("deep", c.pal.tone("deep")),
                   ("hot", c.pal.tone("hot")), ("edge", c.pal.tone("white") if tt <= 0.07 else c.pal.tone("hot"))],
                  glow=glw, opacity={"mid": 0.7})
    elif ph.first:
        ink.paint([("main", c.pal.tone("hot")), ("hot", c.pal.tone("white"))], glow=glw)
    else:
        ink.paint([("main", c.pal.tone("main")), ("deep", c.pal.tone("deep")), ("hot", c.pal.tone("hot"))], glow=glw)
    if sw:                                                                                   # the far half, behind the character: cooler (one step down the ramp), no white edge, half the glow
        fcol = lambda n_: c.pal.tone({"main": "deep", "mid": "deep", "faint": "deep", "rim": "deep", "deep": "shade", "hot": "main"}[n_])
        fink.paint([("faint", fcol("faint"))] + ([("rim", fcol("rim"))] if fink.mask("rim").any() else []), glow=0.0, opacity={"faint": 0.4})
        fink.paint([("mid", fcol("mid")), ("main", fcol("main")), ("deep", fcol("deep")), ("hot", fcol("hot"))], glow=glw * 0.5, opacity={"mid": 0.7})
