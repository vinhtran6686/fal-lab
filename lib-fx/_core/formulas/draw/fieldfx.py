"""lib-fx field kit: flat colour tiers cut from ONE continuous scalar field (posterised erosion). See lib-fx/_core/formulas/draw/SHAPE-RULES.md.

The method of stylised (toon) VFX, both hand-drawn and shader-based: build a grayscale "heat" field over the shape (age along the
stroke, position across it, a directional texture for flame teeth / feathers), then cut it with hard thresholds: every interval
is ONE flat colour (no gradient), the lowest threshold is the silhouette itself (alpha erosion). Animating the thresholds (and the
field) makes the effect cool down tier by tier and break apart where the field is low: the pieces, hooks and holes come out of the
field, they are not drawn one by one. Every tier boundary is a level line of a smooth field, so the shapes are seamless curves.
Glow is stepped too: flat translucent rings at fixed distances from the silhouette.

Everything works on a Canvas at its supersampled size; the canvas downsampling gives clean anti-aliased edges.
"""
import math
import numpy as np
from PIL import Image
from scipy import ndimage


def grid(canvas):
    """x, y of every supersampled pixel centre, in canvas px."""
    W, H = canvas.img.size
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    return (xs + 0.5) / canvas.ss, (ys + 0.5) / canvas.ss


def saw(x):
    """Sawtooth 0..1: a slow ramp then a sharp drop; level lines of it are teeth."""
    return x - np.floor(x)


def noise1(x, seed=0, n=64):
    """Smooth 1-D value noise in -1..1 (periodic over n)."""
    rng = np.random.default_rng(seed)
    v = rng.uniform(-1, 1, n)
    i = np.floor(x).astype(int); f = x - np.floor(x)
    f = f * f * (3 - 2 * f)
    return v[i % n] * (1 - f) + v[(i + 1) % n] * f


def posterize(canvas, field, inside, tiers, alpha=1.0, under=None):
    """Paint flat tiers: tiers = [(threshold, rgb), ...] in rising order; a pixel inside the silhouette gets the colour of the
    highest threshold its field value passes; below the first threshold it is transparent (that IS the erosion).
    Returns the painted mask (supersampled, bool)."""
    m = inside & (field > tiers[0][0])
    if not m.any(): return m
    rgb = np.zeros(m.shape + (3,), np.uint8)
    for thr, col in tiers:
        rgb[m & (field > thr)] = col
    a = (m * 255 * min(1.0, alpha)).astype(np.uint8)
    canvas.img.alpha_composite(Image.fromarray(np.dstack([rgb, a]), "RGBA"))
    return m


def stepped_glow(canvas, mask, steps, ss):
    """Flat translucent rings around a mask: steps = [(distance px, rgb, alpha), ...], widest first. No blur, no gradient."""
    if not mask.any(): return
    dist = ndimage.distance_transform_edt(~mask) / ss
    out = np.zeros(mask.shape + (4,), np.uint8)
    for px, col, a in steps:
        sel = (dist <= px) & ~mask
        out[sel] = tuple(col) + (int(255 * min(1.0, a)),)
    canvas.img.alpha_composite(Image.fromarray(out, "RGBA"))


def spiral_coords(x, y, P, d, th0, span, rad, tail, head, halfwidth):
    """Stroke coordinates of every pixel for a spiral stroke swept clockwise from angle th0 (mirrored by d):
    theta (unwrapped into th0..th0+2pi), v = 0 at the tail .. 1 at the head, w = -1 on the inner edge .. +1 on the outer edge.
    rad(theta) -> centre radius; halfwidth(v) -> half the width there. Returns theta, v, w, inside."""
    dx, dy = (x - P[0]) * d, y - P[1]
    th = np.arctan2(dy, dx)
    th = th0 + np.mod(th - th0, 2 * math.pi)
    r = np.hypot(dx, dy)
    v = (th - tail) / max(1e-6, head - tail)
    rc = rad(th)
    hw = halfwidth(np.clip(v, 0, 1))
    w = (r - rc) / np.maximum(hw, 1e-3)
    inside = (v >= 0) & (v <= 1) & (np.abs(w) <= 1) & (hw > 0.3)
    return th, v, w, inside
