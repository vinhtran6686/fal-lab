"""Frame checks: flag suspicious frames of one hero in one clip, and score the seam of a loop.

Flags per source frame (on the edited frame):
  edge   the silhouette touches the window edge (cut off, or a neighbour's part reached in)
  pink   at least max(40, frame-0 count) more magenta-tinted opaque pixels than frame 0 (the master pose, clean): key leftover, smear, a pink effect
  spike  the opaque area is > 1.35 x the clip's median: usually a slash crescent, an effect or a neighbour's weapon
  pieces more than one separate piece of >= 30 px (a loose arrow, a flying part, dust)
  empty  nothing left
"""
from __future__ import annotations

import numpy as np
from PIL import Image
from scipy import ndimage

from .edits import render
from .workspace import Workspace

ALPHA = 24


def metrics(img: np.ndarray) -> dict:
    a = img[..., 3]
    al = a > ALPHA
    area = int((a > 127).sum())
    if not al.any():
        return {"area": 0, "box": None, "pink": 0, "pieces": 0}
    ys, xs = np.nonzero(al.any(axis=1))[0], np.nonzero(al.any(axis=0))[0]
    r, g, b = (img[..., i].astype(int) for i in range(3))
    pink = int(((a > 127) & (np.minimum(r, b) - g > 45) & (r > 150)).sum())
    lab, cnt = ndimage.label(al, structure=np.ones((3, 3)))
    pieces = int((ndimage.sum(al, lab, range(1, cnt + 1)) >= 30).sum()) if cnt else 0
    return {"area": area, "box": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1], "pink": pink, "pieces": pieces}


def clip_flags(ws: Workspace, clip: str, hero: str) -> list[dict]:
    info = ws.split_info(clip, hero)
    if not info:
        return []
    edits = ws.edits(hero, clip)
    w, h = info["window"]
    ms = [metrics(render(ws, clip, hero, f, edits)) for f in range(info["frames"])]
    med = float(np.median([m["area"] for m in ms if m["area"]] or [1]))
    base_pink = ms[0]["pink"] if ms else 0
    out = []
    for f, m in enumerate(ms):
        fl = []
        if not m["box"]:
            fl.append("empty")
        else:
            x0, y0, x1, y1 = m["box"]
            if x0 <= 1 or y0 <= 1 or x1 >= w - 1 or y1 >= h - 1:
                fl.append("edge")
            if m["pink"] - base_pink >= max(40, base_pink):
                fl.append("pink")
            if m["area"] > 1.35 * med:
                fl.append("spike")
            if m["pieces"] > 1:
                fl.append("pieces")
        out.append({"f": f, "flags": fl, "area": m["area"], "ratio": round(m["area"] / med, 2) if med else 0, "box": m["box"]})
    return out


def _small(img: np.ndarray, crop) -> np.ndarray:
    x0, y0, x1, y1 = crop
    im = Image.fromarray(img[y0:y1, x0:x1], "RGBA").resize((64, 64), Image.BILINEAR)
    a = np.asarray(im).astype(np.float32) / 255.0
    return np.concatenate([a[..., :3] * a[..., 3:4], a[..., 3:4]], axis=2)


def seam(ws: Workspace, hero: str, items: list[tuple[str, int]]) -> dict:
    """items = the loop's frames in order (clip, source frame). Score the jump last -> first (0 = identical) and
    suggest the end frame (among the kept frames of the last clip after the middle) whose image is closest to the first."""
    if len(items) < 3:
        return {"score": None}
    crops = {}

    def sm(c, f):
        if c not in crops:
            crops[c] = ws.split_info(c, hero)["crop"]
        return _small(render(ws, c, hero, f), crops[c])

    first = sm(*items[0])
    d = lambda x: float(np.abs(x - first).mean())
    score = d(sm(*items[-1]))
    typical = float(np.mean([np.abs(sm(*items[i + 1]) - sm(*items[i])).mean() for i in range(min(len(items) - 1, 12))]))
    best, best_d = len(items) - 1, score
    for i in range(len(items) // 2, len(items)):
        di = d(sm(*items[i]))
        if di < best_d:
            best, best_d = i, di
    # frame `best` looks like the first one, so the loop should end just before it (the first frame takes its place)
    end = best - 1 if best_d < score and best > len(items) // 2 else len(items) - 1
    return {"score": round(score, 4), "typical_step": round(typical, 4), "ok": score <= 1.5 * typical,
            "closest_index": best, "suggest_end_index": end, "suggest_score": round(best_d, 4)}
