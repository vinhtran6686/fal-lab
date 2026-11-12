"""Generator v1 for the SLASH archetype, "loop" style (user brief 2026-11-09: a horizontal swing around a body, like the
axe-swing idea sheet ref/vfx/axe-swing-idea/reference.png; idea only, nothing traced).

Design language (from the idea sheet + foundation/):
  path       : an ellipse in perspective at waist height (EllipseFrame, k ~0.3): the far side (top) is a hair-thin line, the turn
               (right) is the thickest and brightest, the near side (bottom) is a thick ribbon
  strands    : main ribbon (light) + an inner ribbon (mid tone) + an innermost thin strand (dark) + hair speed lines; never one
               plain shape (user: v0 "too simple")
  head       : dry-brush split: 3-4 fingers of different lengths, needle tips; teeth notches on the inner edge
  life       : born as a small flick at the back, burst along the path, peak at the near side; after the peak the strands
               first SPREAD apart lengthwise (still continuous: fixes v0's too-early break), then break into streak segments
               of uneven length, shrink to flecks; on ones while swinging, on twos for the debris
  colour     : palette + glow measured on slash-trio blue (user: colour and motion of v0 are fine)"""
import numpy as np
from .frames import EllipseFrame
from .strokes import peak_scale
from .gen_render import render_sequence

PALETTE = {"deep": [52, 104, 168], "blue": [106, 190, 255], "ice": [227, 251, 253]}       # bottom -> top
HALO = {"model": "blur", "sigma": [8.57, 51.43], "c": [[41.7, 114.3, 142.7], [89.2, 148.9, 249.4]]}

# one row per drawing: head / tail (radians travelled along the loop), width scale, strand spread, break amount.
# The head travels past 2*pi at the peak, so the loop CLOSES (user, 2026-11-09: "khép vòng").
TIMELINE = [
    dict(head=0.50, tail=0.00, w=0.40, spread=0.0, brk=0.0, frames=[0], label="sinh: một nét nhỏ phía sau"),
    dict(head=1.70, tail=0.05, w=0.62, spread=0.0, brk=0.0, frames=[1], label="bùng: chạy dọc vòng sau"),
    dict(head=3.00, tail=0.20, w=0.90, spread=0.0, brk=0.0, frames=[2], label="quay đầu bên phải"),
    dict(head=4.60, tail=0.35, w=1.00, spread=0.0, brk=0.0, frames=[3], label="vòng trước dày"),
    dict(head=6.60, tail=0.15, w=1.00, spread=0.0, brk=0.0, frames=[4], label="đỉnh: vòng khép kín"),
    dict(head=6.85, tail=1.40, w=0.88, spread=0.55, brk=0.0, frames=[5], label="sợi tách ra theo chiều dài"),
    dict(head=7.05, tail=2.50, w=0.66, spread=1.00, brk=0.45, frames=[6], label="mỗi sợi đứt ở chỗ riêng"),
    dict(head=7.20, tail=3.60, w=0.42, spread=1.35, brk=1.00, frames=[7, 8], label="vệt co lại (giữ 2 frame)"),
    dict(head=7.30, tail=4.60, w=0.22, spread=1.60, brk=1.50, frames=[9, 10], label="mảnh vụn (giữ 2 frame)"),
    dict(head=7.35, tail=5.40, w=0.09, spread=1.80, brk=2.00, frames=[11, 12], label="tàn (giữ 2 frame)"),
]
GAIN = {0: 1.1, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.05, 6: 1.15, 7: 1.25, 8: 1.25, 9: 1.2, 10: 1.2, 11: 1.15, 12: 1.15}

# heavy weapon (great sword, glaive, two-handed katana): a much wider blade, fewer but bolder strands, a blunt split
# head, big teeth and chunky debris; slower: wind-up held on twos and the impact (closed loop) held 2 frames.
TIMELINE_HEAVY = [
    dict(head=0.50, tail=0.00, w=0.45, spread=0.0, brk=0.0, frames=[0, 1], label="lấy đà: nét nhỏ phía sau (giữ 2 frame)"),
    dict(head=2.00, tail=0.05, w=0.70, spread=0.0, brk=0.0, frames=[2], label="bùng: chạy dọc vòng sau"),
    dict(head=3.80, tail=0.20, w=0.95, spread=0.0, brk=0.0, frames=[3], label="quay đầu bên phải"),
    dict(head=5.40, tail=0.40, w=1.00, spread=0.0, brk=0.0, frames=[4], label="vòng trước dày"),
    dict(head=6.60, tail=0.15, w=1.00, spread=0.0, brk=0.0, frames=[5, 6], label="đỉnh: vòng khép, giữ 2 frame (lực nặng)"),
    dict(head=6.80, tail=1.50, w=0.90, spread=0.45, brk=0.0, frames=[7], label="sợi tách ra theo chiều dài"),
    dict(head=7.00, tail=2.60, w=0.72, spread=0.85, brk=0.45, frames=[8], label="mỗi sợi đứt ở chỗ riêng"),
    dict(head=7.10, tail=3.60, w=0.50, spread=1.15, brk=1.00, frames=[9, 10], label="vệt co lại (giữ 2 frame)"),
    dict(head=7.20, tail=4.50, w=0.30, spread=1.35, brk=1.50, frames=[11, 12], label="mảnh vụn to (giữ 2 frame)"),
    dict(head=7.25, tail=5.30, w=0.12, spread=1.50, brk=2.00, frames=[13, 14], label="tàn (giữ 2 frame)"),
]
GAIN_HEAVY = {0: 1.1, 1: 1.1, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.05, 8: 1.15, 9: 1.25, 10: 1.25, 11: 1.2, 12: 1.2,
              13: 1.15, 14: 1.15}

STYLES = {
    "light": dict(width=47.0, timeline=TIMELINE, gain=GAIN, back=0.30, front=2.4, fingers_off=[-0.38, -0.05, 0.30, 0.55],
                  fingers_w=[0.30, 0.48, 0.30, 0.16], finger_b=1.6, n_teeth=6, teeth=(0.6, 1.6), lines=[24, 44, -30],
                  line_w=[3.2, 2.4, 2.8], debris_L=(14, 30), inner_w=0.85, deep_w=0.34, floor=338),
    "heavy": dict(width=98.0, timeline=TIMELINE_HEAVY, gain=GAIN_HEAVY, back=0.42, front=2.2, fingers_off=[-0.30, 0.05, 0.38],
                  fingers_w=[0.42, 0.62, 0.36], finger_b=0.9, n_teeth=5, teeth=(1.0, 2.0), lines=[30, -40],
                  line_w=[5.0, 4.2], debris_L=(26, 52), inner_w=0.75, deep_w=0.42, floor=360),
}
# "spin" = the two styles above: the fighter spins in place, the slash circles the body and closes at the peak.
# "front" = heavy blade, ONE swing in front of the body: an open C (about 230 deg, never closes), rounder (k 0.42), smaller,
# sitting in front of the fighter (to the right on screen, opening toward the body), as in the idea sheet's 3rd/4th drawings.
TIMELINE_FRONT = [
    dict(head=0.40, tail=0.00, w=0.45, spread=0.0, brk=0.0, frames=[0, 1], label="lấy đà: nét nhỏ phía sau (giữ 2 frame)"),
    dict(head=1.60, tail=0.05, w=0.70, spread=0.0, brk=0.0, frames=[2], label="bùng: vung qua phía trên"),
    dict(head=2.80, tail=0.15, w=0.95, spread=0.0, brk=0.0, frames=[3], label="quay đầu phía trước"),
    dict(head=3.70, tail=0.30, w=1.00, spread=0.0, brk=0.0, frames=[4], label="vòng xuống dưới, dày"),
    dict(head=4.00, tail=0.45, w=1.00, spread=0.0, brk=0.0, frames=[5, 6], label="đỉnh: chữ C hở, giữ 2 frame (va chạm)"),
    dict(head=4.25, tail=1.10, w=0.90, spread=0.45, brk=0.0, frames=[7], label="sợi tách ra theo chiều dài"),
    dict(head=4.40, tail=1.90, w=0.72, spread=0.85, brk=0.45, frames=[8], label="mỗi sợi đứt ở chỗ riêng"),
    dict(head=4.50, tail=2.60, w=0.50, spread=1.15, brk=1.00, frames=[9, 10], label="vệt co lại (giữ 2 frame)"),
    dict(head=4.55, tail=3.20, w=0.30, spread=1.35, brk=1.50, frames=[11, 12], label="mảnh vụn to (giữ 2 frame)"),
    dict(head=4.60, tail=3.70, w=0.12, spread=1.50, brk=2.00, frames=[13, 14], label="tàn (giữ 2 frame)"),
]
STYLES["front-heavy"] = dict(STYLES["heavy"], timeline=TIMELINE_FRONT, front=1.6, back=0.45, floor=392, size=(960, 480),
                             centre=(500, 205), radius=300, k=0.42, tilt=-0.06, u_start=-150, lines=[26, -34], width=86.0)
for _s in STYLES.values():                        # spin defaults: a wide flat ring around the body
    _s.setdefault("size", (960, 460)); _s.setdefault("centre", (480, 190)); _s.setdefault("radius", 380)
    _s.setdefault("k", 0.24); _s.setdefault("tilt", -0.04); _s.setdefault("u_start", -172)

REFLECTION = dict(squash=0.27, dim=0.80, sat=0.85, halo=0.4, opacity=0.9, tint=PALETTE["blue"], tint_mix=0.35)    # slash-trio: ~1/4 height, luma 0.7-0.85


def _uneven(rng, n, lo, hi, min_gap):
    for _ in range(300):
        xs = np.sort(rng.uniform(lo, hi, n))
        if np.all(np.diff(xs) > min_gap):
            return xs
    return np.linspace(lo, hi, n)


def design(seed=11, style="light"):
    S = STYLES[style]
    size, centre, radius, k, tilt = S["size"], S["centre"], S["radius"], S["k"], S["tilt"]
    rng = np.random.default_rng(seed)
    u_start = np.radians(S["u_start"])               # back-left, swinging clockwise on screen: top -> right -> bottom
    nf = len(S["fingers_off"])
    fingers = [dict(off=o, ext=float(e), w=w) for o, e, w in zip(S["fingers_off"], rng.uniform(0.0, 0.12, nf), S["fingers_w"])]
    teeth = _uneven(rng, S["n_teeth"], 0.25, 0.92, 0.07).tolist()
    teeth_size = rng.uniform(*S["teeth"], S["n_teeth"]).tolist()
    nl = len(S["lines"])
    lines = [dict(dr=dr, a=float(a), b=float(b), w=w) for dr, a, b, w in zip(S["lines"], rng.uniform(0.9, 2.0, nl),
                                                                         rng.uniform(0.1, 0.55, nl), S["line_w"])]
    breaks = _uneven(rng, 5, 0.12, 0.88, 0.09).tolist()
    break_len = rng.uniform(0.5, 1.6, 5).tolist()
    flecks = [dict(u=float(u), r=float(r), L=float(L), born=int(b)) for u, r, L, b in zip(
        rng.uniform(-0.2, 0.5, 3), rng.uniform(-30, 30, 3), rng.uniform(8, 16, 3), [0, 0, 1])]
    first_brk = next(i for i, T in enumerate(S["timeline"]) if T["brk"] > 0)
    debris = [dict(t=float(t), dr=float(dr), L=float(L), born=int(b), drift=float(df)) for t, dr, L, b, df in zip(
        _uneven(rng, 6, 0.3, 0.95, 0.06), rng.uniform(-40, 40, 6), rng.uniform(*S["debris_L"], 6),
        [first_brk] * 3 + [first_brk + 1] * 3, rng.uniform(0.02, 0.06, 6))]
    return dict(seed=seed, style=style, size=size, centre=centre, R=radius, k=k, tilt=tilt, width=S["width"], u_start=float(u_start),
                back=S["back"], front=S["front"], finger_b=S["finger_b"], inner_w=S["inner_w"], deep_w=S["deep_w"],
                fingers=fingers, teeth=teeth, teeth_size=teeth_size, lines=lines, breaks=breaks, break_len=break_len,
                flecks=flecks, debris=debris, floor=S["floor"], min_w=S.get("min_w", 9.0))


def _persp(u0, u1, back=0.30, front=2.4, n=13):
    """Thickness multipliers along a stroke: far side (top, sin<0) thin, turn 1, near side (bottom) thick; squash k is undone
    on the near side so the ribbon reads thick there, as in the idea sheet."""
    ts = np.linspace(0, 1, n)
    s = np.sin(u0 + (u1 - u0) * ts)
    m = np.where(s < 0, 1 + s * (1 - back), 1 + s * (front - 1))
    return [[float(t), float(v)] for t, v in zip(ts, m)]


PERSP = dict(back=0.30, front=2.4, w=1.0, min_w=9.0)


def _stroke(u0, u1, r, W, a, b, persp=True, op="add", r1=None):
    r1 = r if r1 is None else r1
    p = dict(axis="u", pos0=float(u0), pos1=float(u1), spine=[r, (2 * r + r1) / 3, (r + 2 * r1) / 3, r1], a=a, b=b, e0=0.0, e1=0.0,
             W=peak_scale(W, a, b), op=op)
    if op == "add" and persp:  # the far side stays a visible hair line (>= ~2 px), never vanishes
        p["min_w"] = PERSP["min_w"] * PERSP["w"]   # loop units: the far side is squashed by k (~0.24), so ~2 px on screen; fades with the stroke
    if persp:
        p["wknots"] = _persp(u0, u1, PERSP["back"], PERSP["front"])
    return p


def drawing(D, k, timeline=TIMELINE):
    T = timeline[k]
    PERSP.update(back=D["back"], front=D["front"], w=T["w"], min_w=D.get("min_w", 9.0))
    us = D["u_start"]
    R, Wb = D["R"], D["width"]
    h, t = us + T["head"], us + T["tail"]
    W = Wb * T["w"]
    sp = T["spread"]
    out = {"deep": [], "blue": [], "ice": []}
    if W > 1.0 and h - t > 0.05:
        L = h - t
        # main ribbon: hair-thin tail (a high), thick blunt-ish head region, ends before the fingers
        main_end = h - 0.10 * min(L, 1.2)
        out["ice"].append(_stroke(t, main_end, R, W, a=1.5, b=0.35))
        # dry-brush fingers at the head
        for f in D["fingers"]:
            f0 = main_end - 0.16 * min(L, 1.2)
            out["ice"].append(_stroke(f0, h + f["ext"] * T["w"], R + f["off"] * W * (1 + sp), W * f["w"], a=0.8, b=D["finger_b"]))
        # inner ribbon (mid tone) and innermost strand (dark): lag behind the head, drift inward as the strands spread
        if L > 0.6:
            out["blue"].append(_stroke(max(t, h - 3.0), h - 0.12, R - (0.48 + 0.55 * sp) * W, W * D["inner_w"], a=1.3, b=0.7))
            out["deep"].append(_stroke(max(t, h - 2.0), h - 0.30, R - (1.0 + 0.9 * sp) * W, W * D["deep_w"], a=1.2, b=1.0))
        # hair speed lines, outside and inside, spreading
        if L > 1.0:
            for ln in D["lines"]:
                u1 = h - ln["b"]
                u0 = max(t, u1 - ln["a"] * min(1.0, L / 2.5))
                if u1 - u0 > 0.1:
                    out["ice" if ln["dr"] > 0 else "blue"].append(
                        _stroke(u0, u1, R + ln["dr"] * (1 + sp) + (W * 0.5 if ln["dr"] > 0 else -W * 0.6), max(ln["w"] * T["w"], 1.2),
                                a=1.6, b=1.6, persp=True))
        # teeth on the inner edge of the main ribbon
        for tt, sz in zip(D["teeth"], D["teeth_size"]):
            u = t + tt * (main_end - t)
            if T["brk"] < 1.0 and np.sin(u) > -0.35:   # only where the ribbon is thick: on the far side a tooth would cut the hair line
                # a tooth bites IN FROM the inner edge (an open notch, never a hole): place it on the ribbon's local inner edge
                tn = tt * (main_end - t) / (main_end - t)
                prof = (tn ** 1.5 * (1 - tn) ** 0.35) / ((0.81 ** 1.5) * (0.19 ** 0.35))
                s_ = np.sin(u)
                m = 1 + s_ * (PERSP["front"] - 1) if s_ >= 0 else 1 + s_ * (1 - PERSP["back"])
                hw = 0.5 * W * m * prof
                cut = _stroke(u - 0.025 * sz, u + 0.025 * sz, R - 1.6 * hw, 0.55 * hw * sz, a=0.6, b=1.4, op="cut", persp=False,
                              r1=R - 0.15 * hw)
                out["ice"].append(cut)
        # break: every strand breaks at ITS OWN points (no dashes lined up across strands); gaps grow, uneven
        if T["brk"] > 0:
            sets = {"ice": [0, 2, 4], "blue": [1, 3], "deep": [2, 4]}
            radius = {"ice": R, "blue": R - (0.48 + 0.55 * sp) * W, "deep": R - (1.0 + 0.9 * sp) * W}
            for l, idx in sets.items():
                for i in idx:
                    u = t + (D["breaks"][i] + 0.07 * (hash(l) % 3 - 1)) * L
                    gap = 0.03 * T["brk"] * D["break_len"][i]
                    out[l].append(_stroke(u - gap, u + gap, radius[l] - 1.2 * W, W * 2.6, a=0.6, b=1.4, persp=False, op="cut",
                                          r1=radius[l] + 1.2 * W))
    for f in D["flecks"]:                       # little flicks around the start (as in the idea sheet's first drawings)
        age = k - f["born"]
        if 0 <= age <= 2:
            Lf = f["L"] * (0.6 ** age)
            u = us + f["u"] + 0.05 * age
            out["ice"].append(_stroke(u, u + Lf / R, R + f["r"] + 6 * age, max(Lf / 4, 1.5), a=1.0, b=1.0, persp=False))
    for d in D["debris"]:                       # debris from the breaks: drifts on along the swing, shrinks
        age = k - d["born"]
        if age >= 0:
            Ld = d["L"] * (0.62 ** age)
            if Ld > 4:
                u = us + T["tail"] + d["t"] * (T["head"] - T["tail"]) + d["drift"] * age
                out["ice"].append(_stroke(u, u + Ld / R, R + d["dr"] * (1 + 0.3 * age), max(Ld / 5, 1.5), a=1.0, b=1.3, persp=True))
    return out


def build(name="gen-slash-loop-blue", seed=11, style="light", reflection=True):
    D = design(seed, style)
    S = STYLES[style]
    frame = EllipseFrame(D["centre"], D["k"], D["tilt"])
    drawings = [dict(strokes=drawing(D, k, S["timeline"]), frames=T["frames"], label=T["label"]) for k, T in enumerate(S["timeline"])]
    refl = dict(REFLECTION, floor=D["floor"]) if reflection else None
    return render_sequence(name, drawings, frame, D["size"], PALETTE, HALO, S["gain"], reflection=refl,
                           meta=dict(design=D, timeline=S["timeline"], gain=S["gain"], style=style, reflection=refl,
                                     idea="ref/vfx/axe-swing-idea/reference.png"))
