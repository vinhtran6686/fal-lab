"""Split a clip into one frame set per hero, EVERY native frame (no sampling), into the workspace cache.

Same cut as scripts/lineup/lineup_split.py (fixed cells, --pad window, magenta key, keep the main body), with two
differences: every source frame is kept (the tool picks frames later, by native index), and the horizontal anchor is
the FEET (bottom 8% of the silhouette in frame 0), not the centre of the whole box, so a long weapon does not pull the
pivot off the character (same rule as tools/frame_tuner/apply_recipe.py). One fixed shift per hero and clip: every
lineup clip starts from the same lineup image, so the shift is the same for every take of a hero.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from .workspace import Workspace, write_json, SPLIT_KEYS

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lineup"))
from lineup_split import key_magenta, keep_main  # noqa: E402  (one implementation of the key and the main-body rule)

ALPHA = 24


def feet_anchor(rgba: np.ndarray) -> tuple[float, float] | None:
    a = rgba[..., 3] > ALPHA
    ys = np.nonzero(a.any(axis=1))[0]
    if not len(ys):
        return None
    top, bottom = ys.min(), ys.max()
    band = a[max(top, int(round(bottom - 0.08 * (bottom - top)))):bottom + 1]
    xs = np.nonzero(band.any(axis=0))[0]
    return (xs.min() + xs.max()) / 2.0, float(bottom)


def decode(clip: Path, tmp: Path) -> list[Path]:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), str(tmp / "%04d.png")], check=True)
    return sorted(tmp.glob("*.png"))


def split_clip(ws: Workspace, clip: str, heroes: list[str] | None = None, progress=None) -> dict:
    """Cut, key and anchor every frame of `clip` for each hero; returns {hero: info}. progress(fraction, text)."""
    g = ws.grid
    heroes = [h for h in (heroes or ws.clip_heroes(clip)) if h in ws.clip_heroes(clip)]
    say = progress or (lambda f, t: None)
    say(0.0, f"{clip}: decoding")
    with tempfile.TemporaryDirectory() as td:
        files = decode(ws.clip_path(clip), Path(td))
        if not files:
            raise RuntimeError(f"{clip}: no frames decoded")
        first = np.array(Image.open(files[0]).convert("RGB"))
        H, W = first.shape[:2]
        xm = int(round(g["x_margin"] * W))
        cw0, ch0 = (W - 2 * xm) // g["cols"], H // g["rows"]
        P = g["pad"]
        cw, ch = cw0 + 2 * P, ch0 + 2 * P
        anchor = (cw // 2, P + int(round(0.88 * ch0)))
        out = {}
        n = len(files)
        for hi, hero in enumerate(heroes):
            idx = ws.cell_index(hero)
            r, c = divmod(idx, g["cols"])
            d = ws.cache(clip, hero)
            if d.exists():
                shutil.rmtree(d)
            (d / "raw").mkdir(parents=True)
            shift = None
            union = None
            for k, f in enumerate(files):
                fr = np.array(Image.open(f).convert("RGB"))
                big = np.empty((H + 2 * P, W + 2 * P, 3), np.uint8)
                big[:] = (255, 0, 255)
                big[P:P + H, P:P + W] = fr
                win = big[r * ch0:r * ch0 + ch, xm + c * cw0:xm + c * cw0 + cw]
                rgba = keep_main(key_magenta(win), cw // 2, g.get("gap", 14))
                if shift is None:
                    fa = feet_anchor(rgba)
                    if fa is None:
                        raise RuntimeError(f"{clip}/{hero}: the first frame is empty (is this hero in the clip?)")
                    shift = (int(round(anchor[0] - fa[0])), int(round(anchor[1] - fa[1])))
                    body_h = int(np.ptp(np.nonzero((rgba[..., 3] > 127).any(axis=1))[0]) + 1)
                dx, dy = shift
                canvas = np.zeros((ch, cw, 4), np.uint8)
                ys0, xs0, ys1, xs1 = max(0, dy), max(0, dx), min(ch, ch + dy), min(cw, cw + dx)
                canvas[ys0:ys1, xs0:xs1] = rgba[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
                Image.fromarray(canvas, "RGBA").save(d / "raw" / f"f{k:03d}.png")
                al = canvas[..., 3] > ALPHA
                if al.any():
                    ys, xs = np.nonzero(al.any(axis=1))[0], np.nonzero(al.any(axis=0))[0]
                    b = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
                    union = b if union is None else [min(union[0], b[0]), min(union[1], b[1]), max(union[2], b[2]), max(union[3], b[3])]
                if k % 8 == 0:
                    say((hi + k / n) / len(heroes), f"{clip}: {hero} {k + 1}/{n}")
            m = 12
            crop = [max(0, union[0] - m), max(0, union[1] - m), min(cw, union[2] + m), min(ch, union[3] + m)] if union else [0, 0, cw, ch]
            info = {"clip": clip, "hero": hero, "frames": n, "fps": 24, "window": [cw, ch], "anchor": list(anchor),
                    "shift": list(shift), "crop": crop, "body_px": body_h, "clip_size": [W, H],
                    "grid": {k: g.get(k) for k in SPLIT_KEYS}}
            write_json(d / "info.json", info)
            out[hero] = info
    say(1.0, f"{clip}: done")
    return out
