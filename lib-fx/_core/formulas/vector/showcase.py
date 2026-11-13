"""Export a profile's rebuilt effect into the repo (tracked), so it can be browsed without running anything:
lib-fx/_core/results/vector-showcase/<profile>/<variant>/
  compare.gif   reference | rebuilt, at the reference speed      rebuilt.gif   rebuilt only
  frames/NN.png final frames (gradient, glow)                    svg/NN.svg    clean vector layers (one <path> per layer)"""
import shutil
from pathlib import Path
import numpy as np
from PIL import Image
from . import measure


def _wide_box(prof, v, frames, pad=16):
    """Box around everything the effect draws in any frame, keeping its own aspect ratio (review._crop_box is a square capped at
    the short side of the frame, which cuts a long effect such as a flame stream)."""
    U = None
    for f in frames:
        rgb = measure.load_frame(prof, v, f)
        if rgb is None:
            continue
        for m in measure.layer_masks(prof, v, rgb).values():
            U = m.copy() if U is None else (U | m)
    ys, xs = np.nonzero(U)
    H, W = U.shape
    return (max(0, int(xs.min()) - pad), max(0, int(ys.min()) - pad), min(W, int(xs.max()) + 1 + pad), min(H, int(ys.max()) + 1 + pad))


def _fit(img, box, size):
    """Crop to box and scale so the longer side is `size` px (no distortion)."""
    c = img.crop(box)
    k = size / max(c.size)
    return c.resize((max(1, round(c.width * k)), max(1, round(c.height * k))), Image.LANCZOS)

ROOT = Path(__file__).resolve().parents[2] / "results" / "vector-showcase"


def export(prof, frames=None, size=480, fps=25):
    out_root = ROOT / prof.name
    src = prof.out_dir()
    frames = frames or prof.frames()
    written = []
    for v in prof.variants:
        d = out_root / v
        if d.exists():
            shutil.rmtree(d)
        (d / "frames").mkdir(parents=True)
        (d / "svg").mkdir()
        box = _wide_box(prof, v, frames)
        comp, reb = [], []
        for f in frames:
            fp, sp = src / "frames" / f"{v}_{f:02d}.png", src / "svg" / f"{v}_{f:02d}.svg"
            ref = measure.load_frame(prof, v, f)
            if ref is None:
                continue
            img = Image.open(fp).convert("RGB") if fp.exists() else Image.new("RGB", ref.shape[1::-1], tuple(prof.get("background")))
            if fp.exists():
                img.save(d / "frames" / f"{f:02d}.png", optimize=True)
            if sp.exists():
                shutil.copy(sp, d / "svg" / f"{f:02d}.svg")
            a = _fit(Image.fromarray(ref.astype(np.uint8)), box, size)
            b = _fit(img, box, size)
            row = Image.new("RGB", (a.width * 2, a.height))
            row.paste(a, (0, 0)); row.paste(b, (a.width, 0))
            comp.append(row); reb.append(b)
        ms = int(1000 / fps)
        if comp:
            comp[0].save(d / "compare.gif", save_all=True, append_images=comp[1:], duration=ms, loop=0, optimize=True)
            reb[0].save(d / "rebuilt.gif", save_all=True, append_images=reb[1:], duration=ms, loop=0, optimize=True)
        written.append(d)
    return written
