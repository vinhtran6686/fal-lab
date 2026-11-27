"""Non-destructive clean-up of split frames: the raw frame + an edit list -> the edited frame (one implementation; the UI
only sends ops and shows what this returns).

edits file (prep/<hero>/<clip>.edits.json):
  {"version": 1, "grid": {...split settings...},
   "denoise": {"specks": 40, "pink": true, "trail": false},       # applied to every frame of this hero in this clip
   "ops": {"<source frame>": [op, ...]}}                           # applied in order after the denoise
ops (window pixel coordinates, the same for every frame of the clip):
  {"op": "brush", "pts": [[x, y], ...], "r": 6, "mode": "erase" | "restore"}   a stroke of radius r
  {"op": "lasso", "pts": [[x, y], ...], "mode": "erase" | "restore"}           a closed polygon
  {"op": "piece", "x": X, "y": Y, "mode": "erase" | "keep"}                    the connected piece under the point:
                                                                                erase it, or keep only it (drop the rest)
"restore" brings back the pixels of the denoised raw frame (undo of an erase in a region).
"""
from __future__ import annotations

import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

from .workspace import Workspace

ALPHA = 24


def load_raw(ws: Workspace, clip: str, hero: str, f: int) -> np.ndarray:
    return np.array(Image.open(ws.cache(clip, hero) / "raw" / f"f{f:03d}.png").convert("RGBA"))


def denoise(rgba: np.ndarray, cfg: dict) -> np.ndarray:
    out = rgba.copy()
    if not cfg:
        return out
    if cfg.get("pink"):
        # leftover magenta tint on the edges and on motion smears: fade pinkish pixels, pull the tint back to grey
        f = out.astype(np.float32)
        r, g, b, a = f[..., 0], f[..., 1], f[..., 2], f[..., 3]
        tint = np.clip((np.minimum(r, b) - g - 35.0) / 45.0, 0, 1) * (a > 0)
        pinkish = (r > 150) & (b > 120) & (r >= b - 40)
        a = np.where(pinkish, a * (1 - tint), a)
        grey = 0.3 * r + 0.59 * g + 0.11 * b
        k = tint * 0.85
        f[..., 0], f[..., 2], f[..., 3] = r * (1 - k) + grey * k, b * (1 - k) + grey * k, a
        out = f.clip(0, 255).astype(np.uint8)
    if cfg.get("trail"):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lineup"))
        from lineup_split import erase_trail
        out = erase_trail(out)
    n = int(cfg.get("specks") or 0)
    if n > 0:
        al = out[..., 3] > ALPHA
        lab, cnt = ndimage.label(al, structure=np.ones((3, 3)))
        if cnt > 1:
            areas = ndimage.sum(al, lab, range(1, cnt + 1))
            big = int(np.argmax(areas)) + 1
            small = np.zeros(cnt + 1, bool)
            small[1:] = areas < n
            small[big] = False
            out[..., 3] = np.where(small[lab], 0, out[..., 3])
    return out


def _mask(shape, op) -> np.ndarray:
    h, w = shape
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    pts = [tuple(map(float, p)) for p in op.get("pts", [])]
    if op["op"] == "brush" and pts:
        r = float(op.get("r", 6))
        if len(pts) > 1:
            d.line(pts, fill=255, width=max(1, int(round(2 * r))), joint="curve")
        for x, y in pts:
            d.ellipse((x - r, y - r, x + r, y + r), fill=255)
    elif op["op"] == "lasso" and len(pts) >= 3:
        d.polygon(pts, fill=255)
    return np.array(m) > 127


def apply_op(img: np.ndarray, base: np.ndarray, op: dict) -> np.ndarray:
    out = img.copy()
    if op["op"] in ("brush", "lasso"):
        m = _mask(img.shape[:2], op)
        if op.get("mode") == "restore":
            out[m] = base[m]
        else:
            out[..., 3][m] = 0
    elif op["op"] == "piece":
        al = out[..., 3] > ALPHA
        lab, cnt = ndimage.label(al, structure=np.ones((3, 3)))
        x, y = int(round(op["x"])), int(round(op["y"]))
        h, w = al.shape
        if not (0 <= x < w and 0 <= y < h):
            return out
        lid = lab[y, x]
        if lid == 0:   # clicked next to a piece: take the nearest piece within 6 px
            y0, y1, x0, x1 = max(0, y - 6), min(h, y + 7), max(0, x - 6), min(w, x + 7)
            sub = lab[y0:y1, x0:x1]
            if sub.any():
                ys, xs = np.nonzero(sub)
                k = np.argmin((ys + y0 - y) ** 2 + (xs + x0 - x) ** 2)
                lid = sub[ys[k], xs[k]]
        if lid == 0:
            return out
        if op.get("mode") == "keep":
            out[..., 3] = np.where(lab == lid, out[..., 3], 0)
        else:
            out[..., 3] = np.where(lab == lid, 0, out[..., 3])
    return out


def ops_key(edits: dict, f: int) -> str:
    body = json.dumps({"d": edits.get("denoise") or {}, "o": (edits.get("ops") or {}).get(str(f), [])}, sort_keys=True)
    return hashlib.sha1(body.encode()).hexdigest()[:16]


def render(ws: Workspace, clip: str, hero: str, f: int, edits: dict | None = None, use_cache: bool = True) -> np.ndarray:
    edits = edits if edits is not None else ws.edits(hero, clip)
    key = ops_key(edits, f)
    cdir = ws.cache(clip, hero) / "edited"
    cpng, ckey = cdir / f"f{f:03d}.png", cdir / f"f{f:03d}.key"
    if use_cache and cpng.exists() and ckey.exists() and ckey.read_text() == key:
        return np.array(Image.open(cpng).convert("RGBA"))
    base = denoise(load_raw(ws, clip, hero, f), edits.get("denoise") or {})
    img = base
    for op in (edits.get("ops") or {}).get(str(f), []):
        img = apply_op(img, base, op)
    cdir.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img, "RGBA").save(cpng)
    ckey.write_text(key)
    return img
