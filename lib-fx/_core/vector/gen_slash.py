"""Generator v0 for the SLASH archetype (foundation/06-slash.md): a brand-new slash drawn only from measured rules, rendered
through the same clean-vector pipeline (strokes -> smooth_simplify -> stacked layers + glow) as the rebuilt references.

What comes from where
  shape unit        : tapered stroke (strokes.py), crescent: needle tail (a > 1), round head (b < 1), length / width ~ 8-10
  layers / colours  : palette preset measured on slash-trio (blue: base blue + ice on the outer edge, 2 tones, luma step ~70)
  life (drawings)   : born tiny at the start of the swing (~6 % of peak area), peak after 2 drawings (x7-8 per drawing),
                      head keeps travelling ~1-2 drawings after the peak while the tail fades first, area x~0.4-0.6 per
                      drawing after the peak, loss by CUTS and HOLES (~50-60 %), not only the rim; pieces shrink and end as
                      sparks; on ones while slicing, on twos for the last sparks
  glow              : blurred copy of the shapes x gain per frame, gain >= 1 on the debris (slash rule: debris stays bright)
Nothing is copied from a reference frame: only the palette, glow colours and the numbers in foundation/."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from .profile import Profile, REPO
from .frames import PolarFrame
from .strokes import peak_scale
from .pipeline import strokes_cover_2x
from .smooth import smooth_simplify
from .bezier import raster_evenodd
from . import compose

PALETTES = {  # measured on slash-trio (profiles/slash-trio.json): base layer first, top layer last
    "blue": {"layers": {"blue": [106, 190, 255], "ice": [227, 251, 253]},
             "halo": {"model": "blur", "sigma": [8.57, 51.43], "c": [[41.7, 114.3, 142.7], [89.2, 148.9, 249.4]]}},
    "pink": {"layers": {"blue": [255, 95, 115], "ice": [255, 227, 231]},
             "halo": {"model": "blur", "sigma": [7.98, 48.09], "c": [[60.0, 10.0, 25.0], [240.0, 60.0, 90.0]]}},
    "gold": {"layers": {"blue": [254, 191, 52], "ice": [255, 246, 214]},
             "halo": {"model": "blur", "sigma": [20.0, 70.0], "c": [[120.0, 30.0, 10.0], [260.0, 60.0, 20.0]]}},
}

# one row per DRAWING: head / tail progress along the swing (1 = full arc), width scale, cut width (share of the arc),
# hole scale; then which frames show it (on ones, then on twos)
TIMELINE = [
    dict(head=0.20, tail=0.00, w=0.36, cut=0.000, hole=0.0, frames=[0]),     # birth: small sliver at the start of the swing
    dict(head=0.64, tail=0.02, w=0.82, cut=0.000, hole=0.0, frames=[1]),     # bursting along the path
    dict(head=1.00, tail=0.06, w=1.00, cut=0.000, hole=0.0, frames=[2]),     # peak
    dict(head=1.07, tail=0.22, w=0.70, cut=0.003, hole=0.5, frames=[3]),     # head still travels, tail fades, first cracks
    dict(head=1.10, tail=0.40, w=0.40, cut=0.020, hole=1.0, frames=[4]),     # breaks into pieces
    dict(head=1.11, tail=0.54, w=0.24, cut=0.034, hole=1.2, frames=[5]),
    dict(head=1.11, tail=0.66, w=0.12, cut=0.050, hole=0.0, frames=[6, 7]),  # on twos from here: debris and sparks
    dict(head=1.11, tail=0.76, w=0.05, cut=0.064, hole=0.0, frames=[8, 9]),
    dict(head=1.11, tail=0.86, w=0.00, cut=0.080, hole=0.0, frames=[10, 11]),
]
GAIN = {0: 1.25, 1: 1.0, 2: 1.0, 3: 1.05, 4: 1.15, 5: 1.3, 6: 1.28, 7: 1.28, 8: 1.22, 9: 1.22, 10: 1.18, 11: 1.18}


def _irregular(rng, n, lo, hi, min_gap):
    """n positions in [lo, hi] with uneven gaps (no two alike: foundation 01 §2)."""
    for _ in range(200):
        xs = np.sort(rng.uniform(lo, hi, n))
        if np.all(np.diff(xs) > min_gap):
            return xs
    return np.linspace(lo, hi, n)


def design(seed=7, size=(900, 520), arc_px=620, width=70, rise_deg=-4.0):
    """Everything that stays the same through the animation: the arc, the cut and hole positions, the sparks."""
    rng = np.random.default_rng(seed)
    W, H = size
    R = 560.0                                       # a clear swing arc, still read as horizontal
    half = np.arcsin(arc_px / 2 / R)
    centre = (W / 2, H * 0.40 + R)
    mid = -np.pi / 2 + np.radians(rise_deg)
    th0, th1 = mid - half, mid + half               # swing left -> right
    cuts = _irregular(rng, 3, 0.34, 0.90, 0.14)     # where the blade breaks (seeded, uneven: pieces 2-5x different)
    cut_len = rng.uniform(0.7, 1.6, 4)
    holes = _irregular(rng, 2, 0.45, 0.85, 0.15)
    notches = _irregular(rng, 3, 0.32, 0.88, 0.12)  # diagonal ice notches (blue shows through: reference stripes)
    notch_len = rng.uniform(0.6, 1.8, 3)
    sparks = [dict(t=float(t), born=int(b), L=float(rng.uniform(16, 34)), lift=float(rng.uniform(3, 9)),
                   speed=float(rng.uniform(10, 20))) for t, b in zip(_irregular(rng, 6, 0.35, 0.98, 0.07), [4, 4, 5, 5, 5, 6])]
    return dict(seed=seed, size=size, R=R, centre=centre, th0=th0, th1=th1, width=width, cuts=cuts.tolist(),
                cut_len=cut_len.tolist(), holes=holes.tolist(), notches=notches.tolist(), notch_len=notch_len.tolist(), sparks=sparks)


def _piece_w(D, t):
    """Width of the blade at arc position t at the peak (needle tail, fullest at ~0.7, pointed head)."""
    a, b = 1.35, 0.8
    x = np.clip(t, 0, 1)
    prof = x ** a * (1 - x) ** b
    return prof / ((a / (a + b)) ** a * (b / (a + b)) ** b)


def drawing_strokes(D, k):
    """Strokes of drawing k: {'blue': [...], 'ice': [...]}.
    Before the break: one blade (needle tail a=1.35, pointed round head b=0.8) + an ice band on its outer side with a few
    diagonal notches. After the break: the blade is a set of PIECES between uneven cut points; each piece is its own
    tapered stroke (both ends pointed), thinner and shorter every drawing (rim loss) with holes / cuts widening between
    them; sparks are born at the cuts and drift along the swing."""
    T = TIMELINE[k]
    R, th0, th1 = D["R"], D["th0"], D["th1"]
    span = th1 - th0
    at = lambda t: th0 + span * t
    Wp = D["width"] * T["w"]
    bul = 10.0
    sp = lambda r_off, w_off: [R + r_off, R + bul + r_off + w_off * 0.2, R + bul * 1.2 + r_off + w_off * 0.18, R + 2 + r_off + w_off * 0.1]
    out = {"blue": [], "ice": []}
    if Wp > 1.5:
        if T["cut"] <= 0:   # one blade
            p0, p1 = at(T["tail"]), at(T["head"])
            out["blue"].append(dict(axis="u", pos0=p0, pos1=p1, spine=sp(0, 0), a=1.35, b=0.8, e0=0.0, e1=0.0,
                                    W=peak_scale(Wp, 1.35, 0.8), op="add"))
            q0, q1 = at(T["tail"] + 0.14 * (T["head"] - T["tail"])), at(T["head"] - 0.03)
            if q1 > q0:
                out["ice"].append(dict(axis="u", pos0=q0, pos1=q1, spine=sp(Wp * 0.17, Wp), a=1.1, b=0.75, e0=0.0, e1=0.0,
                                       W=peak_scale(Wp * 0.56, 1.1, 0.75), op="add"))
            for t, L in zip(D["notches"], D["notch_len"]):      # diagonal notches in the ice: wedges, uneven sizes
                if T["tail"] + 0.1 < t < T["head"] - 0.05:
                    c = at(t)
                    out["ice"].append(dict(axis="u", pos0=c - 0.018 * span * L, pos1=c + 0.018 * span * L,
                                           spine=[R - Wp * 0.2, R + Wp * 0.15, R + Wp * 0.6], a=1.2, b=0.5, e0=0.0, e1=0.0,
                                           W=peak_scale(7.0 * L, 1.2, 0.5), op="cut"))
        else:               # pieces between the cuts
            pts = [T["tail"]] + [t for t in D["cuts"] if T["tail"] < t < T["head"]] + [T["head"]]
            for i, (u0, u1) in enumerate(zip(pts, pts[1:])):
                L = D["cut_len"][i % len(D["cut_len"])]
                g0 = T["cut"] * L * (0.6 if i == 0 else 1.0)
                g1 = T["cut"] * D["cut_len"][(i + 1) % len(D["cut_len"])]
                a0, a1 = u0 + g0, u1 - g1
                if a1 - a0 < 0.015:
                    continue
                mid = (a0 + a1) / 2
                # shards: thickness drops faster than length (rim loss): ~0.8 x the blade width scale, at most 1/5 of the shard length
                wloc = D["width"] * _piece_w(D, (mid - T["tail"]) / max(T["head"] - T["tail"], 1e-3) * 0.9 + 0.08) * T["w"] * 0.8
                wloc = min(wloc, Wp, (a1 - a0) * span * R / 5.0)
                if wloc < 1.5:
                    continue
                aa, bb = 1.3 + 0.35 * (i % 2), 1.0 + 0.4 * ((i + 1) % 2)  # needle ends, each shard its own taper
                out["blue"].append(dict(axis="u", pos0=at(a0), pos1=at(a1), spine=sp(0, 0), a=aa, b=bb, e0=0.0, e1=0.0,
                                        W=peak_scale(wloc, aa, bb), op="add"))
                if wloc > 4 and a1 - a0 > 0.04:
                    out["ice"].append(dict(axis="u", pos0=at(a0 + 0.12 * (a1 - a0)), pos1=at(a1 - 0.05 * (a1 - a0)), spine=sp(wloc * 0.17, wloc),
                                           a=aa, b=bb, e0=0.0, e1=0.0, W=peak_scale(wloc * 0.55, aa, bb), op="add"))
            for t in D["holes"]:                                    # a hole opening in the thickest piece
                if T["hole"] > 0 and T["tail"] < t < T["head"] and Wp > 8:
                    c = at(t)
                    hole = dict(axis="u", pos0=c - 0.022 * span * T["hole"], pos1=c + 0.022 * span * T["hole"],
                                spine=[R + bul + Wp * 0.02, R + bul + Wp * 0.06], a=0.7, b=0.7, e0=0.0, e1=0.0,
                                W=peak_scale(Wp * 0.22 * T["hole"], 0.7, 0.7), op="cut")
                    out["blue"].append(hole); out["ice"].append(dict(hole))
    for s in D["sparks"]:                                            # sparks: born at the cuts, drift along the swing, shrink
        age = k - s["born"]
        if age < 0:
            continue
        L = s["L"] * (0.62 ** age)
        if L < 5:
            continue
        c = at(s["t"]) + (s["speed"] * age) / R
        r = R + bul + s["lift"] * (age + 1)
        out["ice"].append(dict(axis="u", pos0=c - L / R / 2, pos1=c + L / R / 2, spine=[r, r + 1.5], a=0.9, b=0.6, e0=0.0, e1=0.0,
                               W=peak_scale(max(L / 4.5, 2.2), 0.9, 0.6), op="add"))
    return out


def build(name="gen-slash-blue", palette="blue", seed=7, out_root=None):
    D = design(seed)
    W, H = D["size"]
    pal = PALETTES[palette]
    out = Path(out_root) if out_root else REPO / f"lib-fx/_study/{name}"
    for sub in ("frames", "flat", "svg"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    halo = dict(pal["halo"]); halo["gain"] = {str(f): g for f, g in GAIN.items()}
    pd = {"name": name, "source": {"frames": [0, 12]}, "background": [18, 17, 24],
          "variants": {"slash": {"order": list(pal["layers"]), "halo_model": "blur", "near_halo": False, "halo": halo,
                                 "layers": {l: {"colours": [c]} for l, c in pal["layers"].items()}}}}
    pp = out / "profile.json"
    pp.write_text(json.dumps(pd, indent=1))
    prof = Profile(pp)
    frame = PolarFrame(D["centre"], 0.0, rmax=2000)
    stats, images = [], {}
    for k, T in enumerate(TIMELINE):
        st = drawing_strokes(D, k)
        covers, paths = {}, {}
        for l in prof.order("slash"):
            if not any(p["op"] == "add" for p in st[l]):
                continue
            pl, info = smooth_simplify(strokes_cover_2x(st[l], frame, (H, W)), ss=2, sigma=4.5, corner_deg=145, merge_tol=0.9,
                                       min_area=6, close_px=1.0)
            if pl:
                paths[l], covers[l] = pl, raster_evenodd(pl, (H, W))
        for f in T["frames"]:
            if covers:
                img, flat, vis = compose.composite(covers, prof.order("slash"), prof, "slash", f)
                svg = compose.svg(paths, prof.order("slash"), prof, "slash", (H, W))
            else:
                img = np.zeros((H, W, 3), np.uint8) + np.array(pd["background"], np.uint8)
                flat = np.zeros((H, W, 3), np.uint8) + 20
                svg = None
            Image.fromarray(img).save(out / "frames" / f"{f:02d}.png")
            Image.fromarray(flat).save(out / "flat" / f"{f:02d}.png")
            if svg:
                (out / "svg" / f"{f:02d}.svg").write_text(svg)
            images[f] = img
        sil = np.zeros((H, W), bool)
        for c in covers.values():
            sil |= c >= 0.5
        from scipy import ndimage as ndi
        lab, n = ndi.label(sil)
        stats.append(dict(drawing=k, frames=T["frames"], area=int(sil.sum()), pieces=int(n)))
    last = max(images)
    Image.fromarray(np.zeros((H, W, 3), np.uint8) + np.array(pd["background"], np.uint8)).save(out / "frames" / f"{last + 1:02d}.png")
    seq = [Image.open(out / "frames" / f"{f:02d}.png") for f in range(last + 2)]
    seq[0].save(out / "preview.gif", save_all=True, append_images=seq[1:], duration=40, loop=0)
    seq[0].save(out / "preview_slow.gif", save_all=True, append_images=seq[1:], duration=125, loop=0)
    (out / "design.json").write_text(json.dumps(dict(design=D, timeline=TIMELINE, gain=GAIN, stats=stats), indent=1, default=float))
    return out, stats
