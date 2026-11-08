"""Automation for a new reference (kit 1.4):
  propose_crops : find the separate effects in a GIF (and floor reflections) -> crop boxes
  suggest_layers: multi-frame colour clusters -> flat-colour layers (glow / translucent blends filtered out), merged into
                  colour polylines, ordered dark (bottom) -> light (top)
  mask_check    : bright pixels inside the effect that no layer claims, per frame (this is how the missing pink body
                  of slash-trio was found by hand) -> share + their colours + an image
  init_profile  : GIF -> draft profile (crops, frames, layers) ready for `ingest`, `check`, `measure`, `all`"""
import colorsys
import json
import numpy as np
from PIL import Image, ImageSequence
from scipy import ndimage as ndi
from scipy.cluster.vq import kmeans2
from . import measure

LUMA = np.array([0.299, 0.587, 0.114])


def _frames(path):
    im = Image.open(path)
    fr = [np.array(f.convert("RGB")).astype(float) for f in ImageSequence.Iterator(im)]
    durs = [f.info.get("duration", 40) for f in ImageSequence.Iterator(Image.open(path))]
    return np.stack(fr), durs


def hue_name(rgb):
    r, g, b = [c / 255 for c in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    if s < 0.18:
        return "white" if v > 0.7 else "grey"
    h *= 360
    for lim, n in ((15, "red"), (45, "orange"), (70, "gold"), (160, "green"), (195, "cyan"), (255, "blue"), (290, "purple"),
                   (340, "pink"), (361, "red")):
        if h < lim:
            return n


def propose_crops(path, thr=60, pad=24, min_area=400):
    """Effects = connected regions of pixels that clearly differ from the background in some frame. A region below
    another one, overlapping it horizontally, flatter (< 0.5 height) and dimmer is that one's floor reflection."""
    A, _ = _frames(path)
    bg = np.percentile(A, 20, axis=0)
    diff = np.abs(A - bg).max(-1)                       # per frame, per pixel
    act = (diff > thr).any(0)
    act = ndi.binary_opening(act, iterations=2)
    strong = ndi.binary_opening((diff > 2 * thr).any(0), iterations=1)
    lab, n = ndi.label(ndi.binary_dilation(act, iterations=8))
    parts = []
    for i in range(1, n + 1):
        m0 = (lab == i) & act
        rows = np.flatnonzero((m0 & strong).any(1))
        if len(rows) < 2:
            parts.append(m0); continue
        cuts = [r for r, nx in zip(rows, rows[1:]) if nx - r >= 8]   # >= 8 empty rows of strong pixels
        bounds = [rows[0]] + [c + 1 for c in cuts] + [rows[-1] + 1]
        edges = [0] + [int((c + nx) // 2) for c, nx in zip(cuts, [rows[np.searchsorted(rows, c) + 1] for c in cuts])] + [m0.shape[0]]
        for a, b in zip(edges, edges[1:]):
            mm = m0.copy(); mm[:a] = False; mm[b:] = False
            parts.append(mm)
    regions = []
    for m in parts:
        if m.sum() < min_area:
            continue
        ys, xs = np.nonzero(m)
        peak = np.argmax([(np.abs(A[f] - bg).max(-1)[m] > thr).sum() for f in range(len(A))])
        px = A[peak][m]
        bright = px[(px @ LUMA) >= np.percentile(px @ LUMA, 70)]
        sat = bright.max(1) - bright.min(1)
        col = bright[np.argsort(-sat)[: max(20, len(bright) // 10)]].mean(0)
        regions.append(dict(box=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())], area=int(m.sum()),
                            colour=[int(c) for c in col], luma=float(col @ LUMA)))
    # one effect can come out as several regions (a ground ring under a body): merge same-hue regions whose boxes overlap
    merged = True
    while merged:
        merged = False
        for r in regions:
            for o in regions:
                if o is r or hue_name(o["colour"]) != hue_name(r["colour"]):
                    continue
                x0, y0, x1, y1 = r["box"]; a0, b0, a1, b1 = o["box"]
                x0, y0, x1, y1, a0, b0, a1, b1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad, a0 - pad, b0 - pad, a1 + pad, b1 + pad
                inter = max(0, min(x1, a1) - max(x0, a0)) * max(0, min(y1, b1) - max(y0, b0))
                small = min((x1 - x0) * (y1 - y0), (a1 - a0) * (b1 - b0))
                if small and inter / small > 0.3:
                    r["box"] = [min(x0, a0) + pad, min(y0, b0) + pad, max(x1, a1) - pad, max(y1, b1) - pad]
                    big = r if r["area"] >= o["area"] else o
                    r["colour"], r["luma"] = big["colour"], big["luma"]
                    r["area"] += o["area"]
                    regions.remove(o)
                    merged = True
                    break
            if merged:
                break
    for r in regions:  # reflections
        x0, y0, x1, y1 = r["box"]
        for o in regions:
            if o is r:
                continue
            a0, b0, a1, b1 = o["box"]
            ov = max(0, min(x1, a1) - max(x0, a0)) / max(1, min(x1 - x0, a1 - a0))
            if y0 > b1 - 10 and ov > 0.5 and (y1 - y0) < 0.5 * (b1 - b0) and r["luma"] < o["luma"]:
                r["reflection_of"] = id(o)
    names, out = {}, {}
    for r in sorted(regions, key=lambda r: r["box"][0]):
        if "reflection_of" in r:
            continue
        nm = hue_name(r["colour"])
        names[nm] = names.get(nm, 0) + 1
        key = nm if names[nm] == 1 else f"{nm}{names[nm]}"
        r["name"] = key
    for r in regions:
        if "reflection_of" in r:
            parent = next(o for o in regions if id(o) == r["reflection_of"])
            r["name"] = parent.get("name", "fx") + "_refl"
    H, W = A.shape[1:3]
    for r in regions:
        x0, y0, x1, y1 = r["box"]
        out[r["name"]] = dict(crop=[max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)],
                              reflection="reflection_of" in r, colour=r["colour"])
    # frames where anything is visible (+1 margin), background frame = a frame with nothing
    vis = [int((np.abs(a - bg).max(-1) > thr).sum()) for a in A]
    on = [i for i, c in enumerate(vis) if c > 30]
    off = [i for i, c in enumerate(vis) if c <= 2]
    return out, dict(first=max(0, on[0]), last=min(len(A) - 1, on[-1] + 1), background=off[-1] if off else None)


def suggest_layers(prof, v, frames=None, k=10, min_diff=30, merge=50, min_share=0.02, ramp_max=None, debug=False):
    """Colour layers from several frames at once (the 3 biggest): k-means on effect pixels; a cluster that is a blend
    of the background and a brighter cluster (alpha < 0.8, small residual) is glow / translucency, not a fill.
    Remaining clusters closer than `merge` are joined into one layer polyline. Order: dark (bottom) -> light (top)."""
    frames = frames or prof.frames()
    bg = measure.background(prof, v)
    sizes = []
    for f in frames:
        a = measure.load_frame(prof, v, f)
        if a is not None:
            sizes.append((int((np.linalg.norm(a - bg, axis=-1) > min_diff).sum()), f))
    top = [f for _, f in sorted(sizes, reverse=True)[:3]]
    X, BG = [], []
    for f in top:
        a = measure.load_frame(prof, v, f).astype(float)
        m = np.linalg.norm(a - bg, axis=-1) > min_diff
        X.append(a[m]); BG.append(bg[m])
    X, BG = np.concatenate(X), np.concatenate(BG)
    if len(X) < k * 10:
        return {}
    C, lab = kmeans2(X, k, seed=1, minit="++")
    share = np.bincount(lab, minlength=k) / len(X)
    bgm = BG.mean(0)
    # interior share of every cluster on the biggest frame: solid fills ~0.5-0.9, glow ramps (thin bands) < 0.2
    a = measure.load_frame(prof, v, top[0]).astype(float)
    m = np.linalg.norm(a - bg, axis=-1) > min_diff
    near = np.argmin(np.linalg.norm(a[..., None, :] - C[None, None], axis=-1), -1)
    interior = []
    for i in range(k):
        mi = m & (near == i)
        interior.append(float(ndi.binary_erosion(mi, iterations=1).sum() / max(mi.sum(), 1)))
    # flat fills: almost no colour change inside; glow: a steady ramp (median gradient of luma over the cluster)
    lum = ndi.gaussian_filter(a @ LUMA, 1.0)
    gy, gx = np.gradient(lum)
    grad = np.hypot(gx, gy)
    ramp = []
    for i in range(k):
        mi = ndi.binary_erosion(m & (near == i), iterations=1)
        ramp.append(float(np.median(grad[mi])) if mi.sum() > 20 else 99.0)
    if ramp_max is None:  # relative to the flattest clusters of this effect
        ramp_max = max(2.0, 3.0 * float(np.percentile(ramp, 25)))
    if debug:
        for i in np.argsort(-(C @ LUMA)):
            print("   cluster", [int(x) for x in C[i]], "share", round(float(share[i]), 3), "interior", round(interior[i], 2),
                  "ramp", round(ramp[i], 2), "(max", round(ramp_max, 2), ")")
    order = np.argsort(-(C @ LUMA))
    fills, accepted = [], []
    for i in order:
        c = C[i]
        if share[i] < min_share:
            continue
        blend = False
        for f in fills:  # is c = bg + alpha (f - bg) ?
            d = np.array(f[0]) - bgm
            al = float((c - bgm) @ d / max(d @ d, 1))
            if 0 < al < 0.8 and np.linalg.norm(c - (bgm + al * d)) < 18:
                blend = True
                break
        # fills are at least ~40 % as bright as the brightest fill (measured: fills 48-100 %, far glow 26-32 %);
        # dark translucent layers (smoke shadows) are not found here: use `darker_than_bg` by hand
        bright_enough = (c @ LUMA) >= 0.4 * (C[order[0]] @ LUMA)
        if not blend and (c @ LUMA) > (bgm @ LUMA) + 40 and interior[i] >= 0.25 and ramp[i] < ramp_max and bright_enough:
            fills.append(([int(x) for x in c], float(share[i])))
            accepted.append(i)
    layers = []
    for c, s in fills:  # merge close colours into polylines
        for L in layers:
            if min(np.linalg.norm(np.array(c) - np.array(p)) for p in L["colours"]) < merge:
                L["colours"].append(c); L["share"] += s
                break
        else:
            layers.append(dict(colours=[c], share=s))
    out, used = {}, {}
    for L in sorted(layers, key=lambda L: np.array(L["colours"][0]) @ LUMA):
        L["colours"].sort(key=lambda c: -(np.array(c) @ LUMA) if False else 0)
        nm = hue_name(L["colours"][0])
        used[nm] = used.get(nm, 0) + 1
        out[nm if used[nm] == 1 else f"{nm}{used[nm]}"] = {"colours": L["colours"], "tol": 22}
    return out


def mask_check(prof, v, frames=None, thr=60, image=None):
    """Bright pixels inside the effect (within 6 px of a claimed layer pixel) that no layer claims.
    Returns per-frame share and the main unclaimed colours (a missing layer shows up as one big colour)."""
    frames = frames or prof.frames()
    bg = measure.background(prof, v)
    rows, worst = [], None
    for f in frames:
        a = measure.load_frame(prof, v, f)
        if a is None:
            continue
        M = measure.layer_masks(prof, v, a)
        U = np.zeros(a.shape[:2], bool)
        for m in M.values():
            U |= m
        if U.sum() < 50:
            continue
        near = ndi.binary_dilation(ndi.binary_fill_holes(ndi.binary_closing(U, iterations=6)), iterations=6)
        top = max(np.array(prof.flat(v, l), float) @ LUMA for l in prof.order(v)) if prof.order(v) else 255
        lum = a.astype(float) @ LUMA
        bright = (lum - (bg @ LUMA) > thr) & (lum >= 0.4 * top)   # glow around the shapes is darker than 40 % of the top fill
        miss = near & bright & ~U
        share = float(miss.sum() / max((near & bright).sum(), 1))
        cols = []
        if miss.sum() > 50:
            q = (a[miss] // 12 * 12).astype(int)
            u, c = np.unique(q, axis=0, return_counts=True)
            cols = [(u[i].tolist(), int(c[i])) for i in np.argsort(-c)[:5]]
        rows.append(dict(frame=f, unclaimed_share=round(share, 3), unclaimed_px=int(miss.sum()), bright_px=int((near & bright).sum()),
                         colours=cols, _miss=a[miss]))
        if worst is None or miss.sum() > worst[4].sum():
            worst = (share, f, a, U, miss)
    allmiss = np.concatenate([r.pop("_miss") for r in rows]) if rows else np.zeros((0, 3))
    total = dict(unclaimed_share=round(sum(r["unclaimed_px"] for r in rows) / max(sum(r["bright_px"] for r in rows), 1), 3),
                 unclaimed_px=int(len(allmiss)), colours=[])
    if len(allmiss):
        u, c = np.unique((allmiss // 12 * 12).astype(int), axis=0, return_counts=True)
        total["colours"] = [(u[i].tolist(), int(c[i])) for i in np.argsort(-c)[:5]]
    rows.append(dict(frame="all", **total))
    if image and worst:
        _, f, a, U, miss = worst
        t = (a * 0.35).astype(np.uint8)
        t[U] = (90, 90, 90); t[miss] = (255, 40, 200)
        Image.fromarray(np.hstack([a.astype(np.uint8), t])).save(image)
    return rows


def init_profile(gif, name, out_path):
    """GIF -> draft profile. Layers are suggested after ingest (they need the cut frames)."""
    from .profile import Profile
    crops, fr = propose_crops(gif)
    d = {"name": name, "about": f"Draft by `vectorfx.py init` from {gif}.",
         "source": {"gif": str(gif), "crops": {k: v["crop"] for k, v in crops.items()}, "scale": 1,
                    "frames_dir": f"lib-fx/_study/{name}/frames", "pattern": "{variant}_{frame:02d}.png",
                    "frames": [fr["first"], fr["last"]], "background_frame": fr["background"]},
         "frame": {"type": "polar"}, "variants": {}}
    big = max(max(c[2] - c[0], c[3] - c[1]) for c in d["source"]["crops"].values())
    d["source"]["scale"] = 3 if big < 320 else 2 if big < 500 else 1   # element-trio (~280 px crops) was run at 3x
    for k, v in crops.items():
        d["variants"][k] = {"order": [], "layers": {}, "halo_model": "blur"}
        if v["reflection"]:
            d["variants"][k]["frame"] = {"type": "linear", "angle": 0}
    with open(out_path, "w") as fh:
        json.dump(d, fh, indent=1)
    prof = Profile(out_path)
    measure.ingest(prof)
    for v in prof.variants:
        L = suggest_layers(prof, v)
        prof.var(v)["layers"] = L
        prof.var(v)["order"] = list(L)
    prof.save()
    return prof
