"""Read a reference correctly before drawing anything (the lesson of this research: most quality came from measuring
right). Frames, background, flat-colour candidates, layer masks (colour polylines: a layer = its flat fill PLUS its
edge gradient), inner edge gradients and the halo."""
import numpy as np
from PIL import Image, ImageSequence
from scipy import ndimage as ndi
from scipy.optimize import least_squares


# ---------------- frames ----------------
def frame_path(prof, v, f):
    s = prof.d["source"]
    return prof.resolve(s["frames_dir"]) / s.get("pattern", "{variant}_{frame:02d}.png").format(variant=v, frame=f)


def load_frame(prof, v, f):
    p = frame_path(prof, v, f)
    return np.array(Image.open(p).convert("RGB")).astype(int) if p.exists() else None


def ingest(prof):
    """Cut the source GIF into one PNG per frame and variant (crop boxes from the profile)."""
    s = prof.d["source"]
    out = prof.resolve(s["frames_dir"])
    out.mkdir(parents=True, exist_ok=True)
    im = Image.open(prof.resolve(s["gif"]))
    k = s.get("scale", 1)  # small references are upscaled so the px-based tool settings keep their meaning
    n = 0
    for i, fr in enumerate(ImageSequence.Iterator(im)):
        rgb = fr.convert("RGB")
        for v, box in s.get("crops", {"main": None}).items():
            c = rgb.crop(tuple(box)) if box else rgb
            if k != 1:
                c = c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS)
            c.save(out / s.get("pattern", "{variant}_{frame:02d}.png").format(variant=v, frame=i))
        n += 1
    return n


def background(prof, v):
    """The reference's backdrop: a frame where the effect is gone, else the per-pixel 20th percentile over all frames."""
    bf = prof.d["source"].get("background_frame")
    if bf is not None and load_frame(prof, v, bf) is not None:
        return load_frame(prof, v, bf).astype(float)
    st = [load_frame(prof, v, f) for f in prof.frames()]
    return np.percentile(np.stack([x for x in st if x is not None]), 20, axis=0)


# ---------------- palette ----------------
def palette_candidates(rgb, bg=None, top=14, min_count=300, merge=8):
    """Candidate flat fills: exact colours with many pixels, not background-like, not dark. GIF palettes also quantise
    glows into exact colours, so each candidate gets two shape scores:
      interior : share of its pixels with a same-colour 2 px neighbourhood (big solid fills ~0.75+)
      compact  : share of its pixels in its largest blob (one connected shape ~0.85+; glow rings and dither ~0.1-0.6)
    `likely` = interior > 0.5 or compact > 0.85. Dithered thin layers (feathers) can fail both: always check the
    candidate masks image (`palette` command) by eye before writing the profile."""
    cols, cnt = np.unique(rgb.reshape(-1, 3), axis=0, return_counts=True)
    key = rgb[..., 0] * 65536 + rgb[..., 1] * 256 + rgb[..., 2]
    bgc = np.median(bg.reshape(-1, 3), 0) if bg is not None else None
    keep = []
    for i in np.argsort(-cnt):
        c = cols[i].astype(float)
        if cnt[i] < min_count:
            break
        if c.max() < 60 or (bgc is not None and np.linalg.norm(c - bgc) < 40):
            continue
        if any(np.linalg.norm(c - np.array(k["colour"])) < merge for k in keep):
            continue
        m = key == int(c[0]) * 65536 + int(c[1]) * 256 + int(c[2])
        interior = ndi.binary_erosion(m, iterations=2).sum() / m.sum()
        lab, n = ndi.label(m)
        compact = ndi.sum(m, lab, range(1, n + 1)).max() / m.sum()
        keep.append(dict(colour=[int(x) for x in c], count=int(cnt[i]), interior=round(float(interior), 2),
                         compact=round(float(compact), 2), likely=bool(interior > 0.5 or compact > 0.85)))
        if len(keep) >= top:
            break
    return keep


def palette_sheet(rgb, cands, path, cell=200):
    """One tile per candidate: where that exact colour sits in the frame (white), with its RGB."""
    from PIL import ImageDraw
    key = rgb[..., 0] * 65536 + rgb[..., 1] * 256 + rgb[..., 2]
    cols = 4
    rows = (len(cands) + 1 + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * (cell + 18)), (20, 20, 20))
    tiles = [Image.fromarray(rgb.astype(np.uint8))] + [Image.fromarray(((key == c["colour"][0] * 65536 + c["colour"][1] * 256 +
                                                                       c["colour"][2]) * 255).astype(np.uint8)) for c in cands]
    labels = ["frame"] + [f'{tuple(c["colour"])} {"likely" if c["likely"] else ""}' for c in cands]
    d = ImageDraw.Draw(sheet)
    for k, (t, lab) in enumerate(zip(tiles, labels)):
        x, y = (k % cols) * cell, (k // cols) * (cell + 18)
        sheet.paste(t.convert("RGB").resize((cell, cell)), (x, y + 18))
        d.text((x + 4, y + 3), lab, fill=(230, 230, 230))
    sheet.save(path)


# ---------------- layer masks ----------------
def _dist_poly(a, pts):
    pts = [np.array(p, float) for p in pts]
    if len(pts) == 1:
        return np.linalg.norm(a - pts[0], axis=-1)
    d = np.full(a.shape[:-1], 1e9)
    for p, q in zip(pts, pts[1:]):
        e = q - p
        t = np.clip(((a - p) @ e) / (e @ e), 0, 1)
        d = np.minimum(d, np.linalg.norm(a - (p + t[..., None] * e), axis=-1))
    return d


def _drop_small(m, min_area):
    for inv in (True, False):
        tgt = ~m if inv else m
        lab, n = ndi.label(tgt)
        if n:
            sizes = ndi.sum(tgt, lab, range(1, n + 1))
            m[np.isin(lab, 1 + np.flatnonzero(sizes < min_area))] = inv
    return m


_BG = {}


def _bg_cached(prof, v):
    k = (str(prof.path), v)
    if k not in _BG:
        _BG[k] = background(prof, v)
    return _BG[k]


def alpha_of(a, bg, colour):
    """Opacity of a flat colour laid over the background: a = bg + alpha * (colour - bg). Returns (alpha, residual)."""
    d = np.array(colour, float) - bg
    al = ((a - bg) * d).sum(-1) / np.maximum((d * d).sum(-1), 1.0)
    res = np.linalg.norm(a - (bg + al[..., None] * d), axis=-1)
    return al, res


def layer_masks(prof, v, rgb, tol_scale=1.0):
    """Each pixel goes to the layer whose colour polyline is closest (relative to that layer's tolerance).
    A layer with "alpha": [lo, hi] is matched by OPACITY instead: pixel = bg + alpha * (colour - bg) with alpha in
    [lo, hi] and a small residual. Use it for translucent layers (veils) and for layers that fade out over time.
    A layer with "darker_than_bg": N (a translucent dark shape, e.g. a smoke shadow) only takes pixels at least N
    luminance levels darker than the reference background at that spot, so the backdrop itself never matches."""
    L = prof.layers(v)
    names = list(L)
    a = rgb.astype(float)
    D = np.stack([_dist_poly(a, L[l]["colours"]) / (L[l].get("tol", 15) * tol_scale) for l in names])
    if any("alpha" in L[l] for l in names):
        bgf = _bg_cached(prof, v)
        for i, l in enumerate(names):
            if "alpha" in L[l]:
                al, res = alpha_of(a, bgf, L[l]["colours"][0])
                lo, hi = L[l]["alpha"]
                D[i] = np.where((al >= lo) & (al <= hi), res / L[l].get("tol", 15), 9e9)
    if any("darker_than_bg" in L[l] for l in names):
        lum = lambda x: x[..., 0] * 0.299 + x[..., 1] * 0.587 + x[..., 2] * 0.114
        dark = lum(_bg_cached(prof, v)) - lum(a)
        for i, l in enumerate(names):
            if "darker_than_bg" in L[l]:
                D[i][dark < L[l]["darker_than_bg"]] = 9e9
    best, ok = np.argmin(D, 0), np.min(D, 0) < 1
    out = {}
    for i, l in enumerate(names):
        m = ndi.median_filter((ok & (best == i)).astype(np.uint8), 3).astype(bool)
        out[l] = _drop_small(m, prof.get("masks")["min_area"])
    return out


def full_targets(masks, groups):
    """Masks leave 1-4 px anti-aliasing gaps between layers; give each gap pixel to the nearest layer of the same group.
    Gaps between DIFFERENT groups stay empty (only use groups for a real dark line: measure its colour first)."""
    names = list(masks)
    H, W = next(iter(masks.values())).shape
    U = np.zeros((H, W), bool)
    for m in masks.values():
        U |= m
    S = ndi.binary_fill_holes(ndi.binary_closing(U, iterations=6)) & ndi.binary_dilation(U, iterations=7)
    dist = np.stack([ndi.distance_transform_edt(~masks[l]) if masks[l].any() else np.full((H, W), 1e9) for l in names])
    near = np.argmin(dist, 0)
    T = {l: masks[l].copy() for l in names}
    gap = S & ~U
    for g in set(groups.values()):
        mine = [i for i, l in enumerate(names) if groups.get(l, 0) == g]
        other = [i for i, l in enumerate(names) if groups.get(l, 0) != g]
        dmine = dist[mine].min(0)
        dother = dist[other].min(0) if other else np.full((H, W), 1e9)
        ok = gap & (dmine <= dother) & (dother > 3.5)
        for i in mine:
            T[names[i]] |= ok & (near == i)
    return T


# ---------------- gradients and halo ----------------
def fit_edge_gradient(samples, flat):
    """samples: list of (distance inside the layer, colour). Model: lerp(flat, edge, exp(-(d-0.5)/s))."""
    D = np.concatenate([d for d, _ in samples])
    Y = np.concatenate([c for _, c in samples]).astype(float)
    flat = np.array(flat, float)

    def r(x):
        w = np.exp(-(D - 0.5) / x[3])[:, None]
        return ((flat * (1 - w) + x[:3] * w) - Y).ravel()
    x = least_squares(r, list(flat * 0.85) + [3], bounds=([0, 0, 0, 0.3], [255, 255, 255, 30])).x
    return dict(edge=[int(round(c)) for c in x[:3]], s=round(float(x[3]), 2),
                rms_flat=round(float(np.sqrt(np.mean((Y - flat) ** 2))), 1), rms=round(float(np.sqrt(np.mean(r(x) ** 2))), 1))


def fit_halo(samples):
    """samples: list of (distance outside the silhouette, frame - background). Model: two exponentials.
    Components narrower than 1.5 px are anti-aliasing, not glow: callers should drop them (see `near_halo`)."""
    D = np.concatenate([d for d, _ in samples])
    Y = np.concatenate([c for _, c in samples]).astype(float)

    def r(x):
        return (np.exp(-D / x[0])[:, None] * x[2:5] + np.exp(-D / x[1])[:, None] * x[5:8] - Y).ravel()
    x = least_squares(r, [4, 45, 100, 60, 40, 100, 10, 30], bounds=([0.5, 5] + [-50] * 6, [30, 200] + [400] * 6)).x
    return dict(s_near=round(float(x[0]), 2), s_far=round(float(x[1]), 2), c_near=[round(float(c), 1) for c in x[2:5]],
                c_far=[round(float(c), 1) for c in x[5:8]], rms=round(float(np.sqrt(np.mean(r(x) ** 2))), 2))


def measure_profile(prof, frames=None, write=True):
    """Fill `gradient` for every layer and `halo` for every variant from the reference frames."""
    frames = frames or prof.frames()
    k = prof.d["source"].get("scale", 1)
    report = {}
    for v in prof.variants:
        bg = background(prof, v)
        grad = {l: [] for l in prof.layers(v)}
        halo = []
        rng = np.random.default_rng(0)
        for f in frames:
            rgb = load_frame(prof, v, f)
            if rgb is None:
                continue
            M = layer_masks(prof, v, rgb)
            U = np.zeros(rgb.shape[:2], bool)
            for l, m in M.items():
                U |= m
                if m.sum() > 200:
                    d = ndi.distance_transform_edt(m)
                    grad[l].append((d[m], rgb[m]))
            if U.sum() < 500:
                continue
            S = ndi.binary_fill_holes(ndi.binary_closing(U, iterations=3)) & ndi.binary_dilation(U, iterations=4)
            d = ndi.distance_transform_edt(~S)
            sel = np.flatnonzero((d.ravel() > 0.5) & (d.ravel() < 220))
            idx = rng.choice(sel, min(20000, len(sel)), replace=False)
            halo.append((d.ravel()[idx], (rgb.astype(float) - bg).reshape(-1, 3)[idx]))
        report[v] = {}
        for l, smp in grad.items():
            if smp:
                g = fit_edge_gradient(smp, prof.layers(v)[l]["colours"][0])
                report[v][l] = g
                if write:
                    # no gradient, or only anti-aliasing / upscale blur (a real designer gradient is wider than 1.5 source px)
                    if g["s"] >= 25 or g["s"] < 1.5 * k or g["rms"] > 0.9 * g["rms_flat"]:
                        prof.layers(v)[l].pop("gradient", None)
                    else:
                        prof.layers(v)[l]["gradient"] = {"edge": g["edge"], "s": g["s"]}
        op = measure_opacity(prof, v, prof.frames())
        for l, series in op.items():
            report[v][l + "_opacity"] = series
            if write:
                prof.layers(v)[l]["opacity"] = series
        if prof.var(v).get("halo_model") == "blur":
            hb = fit_halo_blur(prof, v, prof.frames())
            report[v]["halo"] = hb
            if hb:  # a blur narrower than 1.5 source px is the reference's anti-aliasing fringe, not glow: drop it
                keep = [i for i, sg in enumerate(hb["sigma"]) if sg >= 1.5 * k]
                hb["sigma"], hb["c"] = [hb["sigma"][i] for i in keep], [hb["c"][i] for i in keep]
            if write and hb:
                prof.var(v)["halo"] = hb
                prof.var(v)["near_halo"] = False
        elif halo:
            h = fit_halo(halo)
            report[v]["halo"] = h
            if write:
                prof.var(v)["halo"] = {k: h[k] for k in ("s_near", "s_far", "c_near", "c_far")}
                prof.var(v)["near_halo"] = h["s_near"] >= 1.5 * k  # narrower than 1.5 source px: anti-aliasing, not glow
    if write:
        prof.save()
    return report


def fit_halo_blur(prof, v, frames, peak_share=0.4, rng_seed=0):
    """Glow as a BLURRED COPY of the shapes (two gaussians, global colours) times a per-frame opacity `gain`.
    Measured on element-trio: a distance-based halo needs its strength scaled from ~1.6 (peak) down to ~0.15 (last
    frames), i.e. the designer fades the glow layer out while the effect dissolves; the blur model also fills the holes
    inside a flame the way the reference does. Fit: colours and sigmas on the biggest frames (gain 1), then one
    least-squares gain per frame, clipped to [0, 2]."""
    bg = background(prof, v)
    data = []
    for f in frames:
        rgb = load_frame(prof, v, f)
        if rgb is None:
            continue
        U = np.zeros(rgb.shape[:2], bool)
        for m in layer_masks(prof, v, rgb).values():
            U |= m
        if U.sum() < 50:
            continue
        d = ndi.distance_transform_edt(~U)
        sel = np.flatnonzero((d.ravel() > 3) & (d.ravel() < 150))
        idx = np.random.default_rng(rng_seed + f).choice(sel, min(6000, len(sel)), replace=False)
        data.append((f, U, idx, (rgb.astype(float) - bg).reshape(-1, 3)[idx]))
    if not data:
        return None
    areas = np.array([U.sum() for _, U, _, _ in data])
    peak = [x for x, a in zip(data, areas) if a >= np.quantile(areas, 1 - peak_share)]
    cache = {}

    def feats(f, U, idx, s1, s2):
        key = (f, round(s1, 1), round(s2, 1))
        if key not in cache:
            u = U.astype(float)
            cache[key] = (ndi.gaussian_filter(u, s1).ravel()[idx], ndi.gaussian_filter(u, s2).ravel()[idx])
        return cache[key]

    def r(x):
        out = []
        for f, U, idx, y in peak:
            a, b = feats(f, U, idx, x[0], x[1])
            out.append((a[:, None] * x[2:5] + b[:, None] * x[5:8] - y).ravel())
        return np.concatenate(out)
    x = least_squares(r, [8, 40, 300, 200, 100, 300, 100, 100], bounds=([1, 5] + [-100] * 6, [40, 200] + [3000] * 6),
                      diff_step=0.05).x
    gain = {}
    for f, U, idx, y in data:
        a, b = feats(f, U, idx, x[0], x[1])
        p = a[:, None] * x[2:5] + b[:, None] * x[5:8]
        gain[f] = float(np.clip((p * y).sum() / max((p * p).sum(), 1e-9), 0, 2))
    return {"model": "blur", "sigma": [round(float(x[0]), 2), round(float(x[1]), 2)],
            "c": [[round(float(c), 1) for c in x[2:5]], [round(float(c), 1) for c in x[5:8]]],
            "gain": {str(f): round(g, 3) for f, g in sorted(gain.items())}}


def measure_opacity(prof, v, frames):
    """Per-frame opacity of every "alpha" layer: median alpha over its mask, capped at 1. Designers fade shapes out
    (element-trio arcane: 1.0 at the peak, 0.83, 0.62, 0.56 in the last frames) and draw veils at ~0.5-0.6."""
    bg = background(prof, v)
    out = {}
    for f in frames:
        rgb = load_frame(prof, v, f)
        if rgb is None:
            continue
        M = layer_masks(prof, v, rgb)
        for l, cfg in prof.layers(v).items():
            if "alpha" in cfg and M[l].sum() >= 30:
                al, _ = alpha_of(rgb.astype(float), bg, cfg["colours"][0])
                out.setdefault(l, {})[str(f)] = round(float(min(np.median(al[M[l]]), 1.0)), 3)
    return out
