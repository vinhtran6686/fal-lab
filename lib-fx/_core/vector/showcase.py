"""Export a profile's rebuilt effect into the repo (tracked), so it can be browsed without running anything:
lib-fx/_core/vector/showcase/<profile>/<variant>/
  compare.gif   reference | rebuilt, at the reference speed      rebuilt.gif   rebuilt only
  frames/NN.png final frames (gradient, glow)                    svg/NN.svg    clean vector layers (one <path> per layer)"""
import shutil
from pathlib import Path
import numpy as np
from PIL import Image
from . import measure
from .review import _crop_box

ROOT = Path(__file__).parent / "showcase"


def export(prof, frames=None, size=320, fps=25):
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
        box = _crop_box(prof, v, frames)
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
            a = Image.fromarray(ref.astype(np.uint8)).crop(box).resize((size, size), Image.LANCZOS)
            b = img.crop(box).resize((size, size), Image.LANCZOS)
            row = Image.new("RGB", (size * 2, size))
            row.paste(a, (0, 0)); row.paste(b, (size, 0))
            comp.append(row); reb.append(b)
        ms = int(1000 / fps)
        if comp:
            comp[0].save(d / "compare.gif", save_all=True, append_images=comp[1:], duration=ms, loop=0, optimize=True)
            reb[0].save(d / "rebuilt.gif", save_all=True, append_images=reb[1:], duration=ms, loop=0, optimize=True)
        written.append(d)
    return written
