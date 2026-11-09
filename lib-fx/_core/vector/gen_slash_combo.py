"""Generator for a COMBO of slashes in one effect (user brief 2026-11-09, idea: ref/vfx/spear-combo-idea/spear-moves.png line 1 and
sword-motion-sketch.png lines 1-2; idea only, nothing traced). A spear / sword combo seen from the side, the fighter facing right:

  1. SWEEP : a horizontal swing, slightly diagonal (rising to the right), over the far side of a flat perspective ellipse: a long thin
             line that turns thick at the right and hooks down (as the idea sheet's 1st drawing)
  2. SMASH : the fighter lifts the weapon behind the head and brings it down: a tall arc in the vertical plane (no perspective) from
             behind-above, over the head, down to the ground in front; the head stops AT the ground (it never digs below), holds 2
             frames (impact), and throws up a splash of spiky shards

Every slash reuses the strand language of gen_slash_loop (main ribbon + mid ribbon + dark strand + speed lines, dry-brush head, teeth,
spread-then-break, debris), each in its OWN coordinate frame (render_sequence takes several frames). Colour follows the idea sheet:
the head is ice / cyan, the tail turns violet (a violet ribbon runs under the whole stroke, the ice ribbon starts mid-way and tapers
in, so the hue change is a flat-colour step, not a gradient)."""
import numpy as np
from .frames import EllipseFrame
from . import gen_slash_loop as L
from .gen_render import render_sequence

PALETTE = {"violet": [150, 112, 232], "deep": [52, 104, 168], "blue": [80, 200, 250], "ice": [227, 251, 253]}   # bottom -> top
HALO = {"model": "blur", "sigma": [8.57, 51.43], "c": [[41.7, 114.3, 142.7], [89.2, 148.9, 249.4]]}
REFLECTION = dict(L.REFLECTION, tint=PALETTE["blue"])

SIZE = (1100, 540)
FLOOR = 432                    # ground line (feet); the smash lands on it, the reflection mirrors about it
IMPACT = (585.0, float(FLOOR))  # where the smash hits the ground

# one row per drawing of each slash, frames are GLOBAL frame indices of the combo (25 fps)
T_SWEEP = [
    dict(head=0.50, tail=0.00, w=0.45, spread=0.0, brk=0.0, frames=[0], label="nhát 1 sinh phía sau"),
    dict(head=1.60, tail=0.05, w=0.75, spread=0.0, brk=0.0, frames=[1], label="nhát 1 quét ngang"),
    dict(head=2.80, tail=0.15, w=0.95, spread=0.0, brk=0.0, frames=[2], label="nhát 1 tới bên phải"),
    dict(head=3.75, tail=0.30, w=1.00, spread=0.0, brk=0.0, frames=[3], label="nhát 1 đỉnh: móc xuống"),
    dict(head=4.00, tail=0.90, w=0.90, spread=0.50, brk=0.0, frames=[4], label="nhát 1 sợi giãn"),
    dict(head=4.15, tail=1.70, w=0.70, spread=1.00, brk=0.45, frames=[5], label="nhát 1 đứt"),
    dict(head=4.25, tail=2.40, w=0.45, spread=1.35, brk=1.00, frames=[6, 7], label="nhát 1 co (lấy đà nhát 2)"),
    dict(head=4.30, tail=3.00, w=0.22, spread=1.60, brk=1.50, frames=[8, 9], label="nhát 1 vụn"),
    dict(head=4.33, tail=3.50, w=0.09, spread=1.80, brk=2.00, frames=[10, 11], label="nhát 1 tàn"),
]
T_SMASH = [
    dict(head=0.50, tail=0.00, w=0.45, spread=0.0, brk=0.0, frames=[8], label="nhát 2 sinh sau lưng, trên cao"),
    dict(head=1.70, tail=0.05, w=0.75, spread=0.0, brk=0.0, frames=[9], label="nhát 2 qua đỉnh đầu"),
    dict(head=3.00, tail=0.15, w=0.95, spread=0.0, brk=0.0, frames=[10], label="nhát 2 bổ xuống"),
    dict(head=3.75, tail=0.30, w=1.00, spread=0.0, brk=0.0, frames=[11, 12], label="nhát 2 chạm đất (giữ 2 frame) + toé"),
    dict(head=3.75, tail=0.95, w=0.90, spread=0.45, brk=0.0, frames=[13], label="nhát 2 sợi giãn"),
    dict(head=3.75, tail=1.65, w=0.72, spread=0.85, brk=0.45, frames=[14], label="nhát 2 đứt"),
    dict(head=3.75, tail=2.30, w=0.50, spread=1.15, brk=1.00, frames=[15, 16], label="nhát 2 co"),
    dict(head=3.75, tail=2.90, w=0.30, spread=1.35, brk=1.50, frames=[17, 18], label="nhát 2 vụn"),
    dict(head=3.75, tail=3.40, w=0.12, spread=1.50, brk=2.00, frames=[19, 20], label="nhát 2 tàn"),
]
# ground splash at the smash: per global frame, (inner radius, outer radius) as a share of each spike's length, width scale
SPLASH = {11: (0.05, 0.55, 1.0), 12: (0.05, 1.00, 1.0), 13: (0.30, 1.10, 0.80), 14: (0.55, 1.15, 0.55), 15: (0.75, 1.18, 0.35),
          16: (0.75, 1.18, 0.35), 17: (0.88, 1.20, 0.18), 18: (0.88, 1.20, 0.18)}
GAIN = {f: g for f, g in zip(range(21), [1.1, 1.0, 1.0, 1.0, 1.05, 1.15, 1.2, 1.2, 1.1, 1.0, 1.0, 1.0, 1.0, 1.05, 1.15, 1.25, 1.25,
                                         1.2, 1.2, 1.15, 1.15])}

L.STYLES["combo-sweep"] = dict(L.STYLES["light"], timeline=T_SWEEP, width=40.0, back=0.45, front=1.9, centre=(560, 235), radius=330,
                               k=0.26, tilt=-0.10, u_start=-175, floor=FLOOR, size=SIZE)
L.STYLES["combo-smash"] = dict(L.STYLES["heavy"], timeline=T_SMASH, width=58.0, back=1.0, front=1.0, centre=(470, 282), radius=200,
                               k=0.90, tilt=0.0, u_start=-160, floor=FLOOR, size=SIZE, min_w=2.5, lines=[22, -26])


def _violet_tail(out, D, T):
    """Ice head, violet tail: the main ribbon goes to the violet layer whole; a new ice ribbon starts mid-way and tapers in over it."""
    if not out["ice"]:
        return out
    main = out["ice"][0]
    out["violet"] = [dict(main)] + out.get("violet", [])
    u0, u1 = main["pos0"], main["pos1"]
    R = main["spine"][0]
    out["ice"][0] = L._stroke(u0 + 0.42 * (u1 - u0), u1, R, D["width"] * T["w"], a=2.2, b=0.35)
    return out


def _splash(seed, f):
    """Spiky shards thrown up and forward from the impact point: radial strokes in a circle frame centred on the impact."""
    if f not in SPLASH:
        return {}
    rng = np.random.default_rng(seed)
    n = 10
    ang = np.sort(np.concatenate([rng.uniform(-176, -150, 3), rng.uniform(-112, -78, 2), rng.uniform(-62, -6, 5)]))  # low, forward bias
    lens = rng.uniform(70, 170, n) * np.where(ang > -65, 1.15, np.where(ang < -140, 0.85, 0.7))
    bend = rng.uniform(4, 12, n)                                  # degrees: tips lean forward (the smash pushes to the right)
    r0s, r1s, ws = SPLASH[f]
    out = {"blue": [], "ice": []}
    for i, (a, Ln, bd) in enumerate(zip(ang, lens, bend)):
        r0, r1 = 6 + r0s * Ln, 6 + r1s * Ln
        if r1 - r0 < 4:
            continue
        s = 200.0                                                 # EllipseFrame.u_scale: angle -> stroke 'across' units
        spine = [np.radians(a) * s, np.radians(a + bd * 0.3) * s, np.radians(a + bd * 0.7) * s, np.radians(a + bd) * s]
        Wb = 24 * ws * (Ln / 110) * s / max(r0 + 25, 1)           # ~24 px at the base for a mid spike
        out["blue"].append(dict(axis="v", pos0=float(r0), pos1=float(r1), spine=[float(x) for x in spine], a=0.25, b=1.5, e0=0.0, e1=0.0,
                                W=float(Wb), op="add", frame=2))
        if Ln > 105 and ws > 0.3:                                  # big shards get an ice core (layered, like the slashes)
            out["ice"].append(dict(axis="v", pos0=float(r0 + 4), pos1=float(r0 + 0.75 * (r1 - r0)), spine=[float(x) for x in spine],
                                   a=0.3, b=1.6, e0=0.0, e1=0.0, W=float(Wb * 0.45), op="add", frame=2))
    if r0s < 0.6:                                                 # flat ground smear along the floor, mostly forward
        for u0, u1, w in ((np.pi / 2 + 0.25, np.pi / 2 + 0.95, 0.6), (np.pi / 2 - 1.15, np.pi / 2 - 0.2, 1.0)):
            out["blue"].append(dict(axis="u", pos0=float(u0), pos1=float(u1), spine=[170.0] * 4, a=0.7 if u0 > 1.6 else 1.4,
                                    b=1.4 if u0 > 1.6 else 0.7, e0=0.0, e1=0.0, W=float(80 * w * ws), op="add", frame=3))
    return out


def build(name="gen-slash-combo-blue", seed=11, reflection=True):
    S1, S2 = L.STYLES["combo-sweep"], L.STYLES["combo-smash"]
    D1, D2 = L.design(seed, "combo-sweep"), L.design(seed + 1, "combo-smash")
    frames = [EllipseFrame(D1["centre"], D1["k"], D1["tilt"]), EllipseFrame(D2["centre"], D2["k"], D2["tilt"]),
              EllipseFrame(IMPACT, 1.0, 0.0), EllipseFrame(IMPACT, 0.12, 0.0)]
    last = max(max(T["frames"]) for T in T_SWEEP + T_SMASH)
    # which drawing of each slash shows on each global frame
    at = {}
    for si, (Tl, D) in enumerate(((T_SWEEP, D1), (T_SMASH, D2))):
        for k, T in enumerate(Tl):
            for f in T["frames"]:
                at.setdefault(f, {})[si] = k
    drawings, prev = [], None
    for f in range(last + 1):
        key = (at.get(f, {}).get(0), at.get(f, {}).get(1), SPLASH.get(f))
        if drawings and key == prev:
            drawings[-1]["frames"].append(f)
            continue
        strokes = {l: [] for l in PALETTE}
        labels = []
        for si, (Tl, D) in enumerate(((T_SWEEP, D1), (T_SMASH, D2))):
            k = key[si]
            if k is None:
                continue
            out = _violet_tail(L.drawing(D, k, Tl), D, Tl[k])
            for l, st in out.items():
                for p in st:
                    p["frame"] = si
                strokes.setdefault(l, []).extend(st)
            labels.append(Tl[k]["label"])
        if key == (None, None, None):
            continue
        for l, st in _splash(seed + 7, f).items():
            strokes[l].extend(st)
        drawings.append(dict(strokes=strokes, frames=[f], label=" + ".join(labels) or "trống"))
        prev = key
    return render_sequence(name, drawings, frames, SIZE, PALETTE, HALO, GAIN,
                           reflection=dict(REFLECTION, floor=FLOOR) if reflection else None,
                           meta=dict(design=[D1, D2], timeline=dict(sweep=T_SWEEP, smash=T_SMASH, splash=SPLASH), gain=GAIN,
                                     style="combo-sweep-smash", idea="ref/vfx/spear-combo-idea/"))
