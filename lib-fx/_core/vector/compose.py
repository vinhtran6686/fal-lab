"""Stacking, inner gradients, halo, final images and SVG."""
import numpy as np
import cv2
from scipy import ndimage as ndi
from .bezier import path_d, svg_doc


def underlay_target(T, order, groups, layer, px):
    """Region a layer is fitted to: its own target PLUS the part of the layers painted above it (same group) within
    `px`: a lower layer runs on under the upper ones as one smooth shape, so there are no seams or cracks."""
    i = order.index(layer)
    above = np.zeros_like(T[layer])
    for l2 in order[i + 1:]:
        if groups.get(l2, 0) == groups.get(layer, 0):
            above |= T[l2]
    if not T[layer].any():
        return T[layer]
    return T[layer] | (above & ndi.binary_dilation(T[layer], iterations=px))


def visible(covers, order):
    vis, claimed = {}, np.zeros(next(iter(covers.values())).shape)
    for l in reversed(order):
        if l in covers:
            vis[l] = (covers[l] >= 0.5) & (claimed < 0.5)
            claimed = np.maximum(claimed, covers[l])
    return vis


def halo(covers, h, near=True, frame=None, weights=None):
    """Two models (profile `halo_model`):
    distance (default): c_near*exp(-d/s_near) + c_far*exp(-d/s_far), d = px to the silhouette; constant over time.
    blur: gain[frame] * (G(sigma0) * silhouette * c0 + G(sigma1) * silhouette * c1): a blurred copy of the shapes, so
          small specks glow weakly and holes fill with glow, with the glow opacity animated (fades out at the end)."""
    sil = np.zeros(next(iter(covers.values())).shape)
    for l, c in covers.items():
        sil = np.maximum(sil, c * (weights or {}).get(l, 1.0))
    if h.get("model") == "blur":
        g = h.get("gain", {})
        if frame is not None and g:
            keys = sorted(int(k) for k in g)
            gain = g[str(min(keys, key=lambda k: abs(k - frame)))] if str(frame) not in g else g[str(frame)]
        else:
            gain = 1.0
        out = sum(ndi.gaussian_filter(sil, s)[..., None] * np.array(c, float) for s, c in zip(h["sigma"], h["c"]))
        return np.clip(out * gain, 0, None)
    d = ndi.distance_transform_edt(sil < 0.5)
    out = np.exp(-d / h["s_far"])[..., None] * np.array(h["c_far"], float)
    if near:
        out += np.exp(-d / h["s_near"])[..., None] * np.array(h["c_near"], float)
    return np.clip(out, 0, None)


def layer_colour(vis, flat, grad):
    """Flat colour shaded toward the edge tint near the edges of the VISIBLE part (distance measured at 2x)."""
    if not grad:
        return np.broadcast_to(np.array(flat, float), vis.shape + (3,))
    H, W = vis.shape
    v2 = cv2.resize(vis.astype(np.uint8), (W * 2, H * 2), interpolation=cv2.INTER_LINEAR).astype(bool)
    d = (ndi.distance_transform_edt(v2) / 2.0).reshape(H, 2, W, 2).mean((1, 3))
    w = np.exp(-np.clip(d - 0.5, 0, None) / grad["s"])[..., None]
    return np.array(flat, float) * (1 - w) + np.array(grad["edge"], float) * w


def layer_opacity(cfg, frame):
    """Measured per-frame opacity of a layer (nearest measured frame), 1 when the layer has none."""
    op = cfg.get("opacity")
    if not op or frame is None:
        return 1.0
    if str(frame) in op:
        return float(op[str(frame)])
    k = min((int(x) for x in op), key=lambda x: abs(x - frame))
    return float(op[str(k)])


def composite(covers, order, prof, v, frame=None):
    """-> (final RGB with gradient + halo, flat RGB, visible masks)."""
    var = prof.var(v)
    shape = next(iter(covers.values())).shape
    img = np.zeros(shape + (3,)) + np.array(prof.get("background"), float)
    if var.get("halo"):
        w = {l: c["halo_w"] for l, c in prof.layers(v).items() if "halo_w" in c}
        img = img + halo(covers, var["halo"], var.get("near_halo", True), frame, w or None)
    flat = np.zeros(shape + (3,)) + 20
    vis = visible(covers, order)
    for l in order:
        if l in covers:
            a = covers[l][..., None] * layer_opacity(prof.layers(v)[l], frame)
            col = prof.flat(v, l)
            img = img * (1 - a) + layer_colour(vis[l], col, prof.layers(v)[l].get("gradient")) * a
            flat = flat * (1 - a) + np.array(col, float) * a
    return np.clip(img, 0, 255).astype(np.uint8), flat.astype(np.uint8), vis


def svg(paths_by_layer, order, prof, v, shape):
    body = []
    for l in order:
        if l in paths_by_layer:
            col = "#%02x%02x%02x" % prof.flat(v, l)
            body.append(f'<path id="{l}" fill="{col}" fill-rule="evenodd" d="{" ".join(path_d(p) for p in paths_by_layer[l])}"/>')
    return svg_doc(shape[1], shape[0], "".join(body), "#141414")
