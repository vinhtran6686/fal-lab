"""Review kit: per-frame and per-layer panels, motion GIFs and a self-contained review page (review/index.html).
The page lets a reviewer mark every layer of every frame OK / needs work, add a note and copy all notes back."""
import json
import numpy as np
from PIL import Image, ImageDraw
from . import measure
from .bezier import parse_path_d

PAGE = (__import__("pathlib").Path(__file__).parent / "review_page.html")


def _crop_box(prof, v, frames):
    U = None
    for f in frames:
        rgb = measure.load_frame(prof, v, f)
        if rgb is None:
            continue
        for m in measure.layer_masks(prof, v, rgb).values():
            U = m.copy() if U is None else (U | m)
    ys, xs = np.nonzero(U)
    H, W = U.shape
    s = int(min(max(ys.max() - ys.min(), xs.max() - xs.min()) + 30, min(H, W)))
    cy, cx = (ys.min() + ys.max()) // 2, (xs.min() + xs.max()) // 2
    x0, y0 = int(np.clip(cx - s // 2, 0, W - s)), int(np.clip(cy - s // 2, 0, H - s))
    return (x0, y0, x0 + s, y0 + s)


def _tile(a, box, size):
    return (Image.fromarray(a) if isinstance(a, np.ndarray) else a).crop(box).resize((size, size), Image.LANCZOS)


def _pen_view(loops, box, size, col):
    sc = size / (box[2] - box[0])
    im = Image.new("RGB", (size, size), (20, 20, 20))
    d = ImageDraw.Draw(im)
    T = lambda p: ((p[0] - box[0]) * sc, (p[1] - box[1]) * sc)
    for segs in loops:
        pts = []
        for p0, p1, p2, p3 in segs:
            t = np.linspace(0, 1, 12)[:, None]
            pts += [T(q) for q in ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3)]
        if len(pts) > 2:
            d.polygon(pts, fill=tuple(int(c * 0.35) for c in col), outline=col)
        for i, s in enumerate(segs):
            a, b = segs[i - 1][3] - segs[i - 1][2], s[1] - s[0]
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            corner = na > 1e-6 and nb > 1e-6 and np.dot(a, b) / (na * nb) < 0.97
            x, y = T(s[0]); r = 2.6 if corner else 1.8
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 70, 70) if corner else (240, 240, 240))
    return im


def build(prof, frames=None, fps=25):
    import re
    out = prof.out_dir()
    rv = out / "review"
    (rv / "img").mkdir(parents=True, exist_ok=True)
    rep = json.loads((out / "report.json").read_text())
    frames = frames or prof.frames()
    data = {"name": prof.name, "variants": {}}
    for v in prof.variants:
        box = _crop_box(prof, v, frames)
        seq_o, seq_r = [], []
        vd = {"frames": {}, "palette": {l: "#%02x%02x%02x" % prof.flat(v, l) for l in prof.order(v)}}
        for f in frames:
            orig = measure.load_frame(prof, v, f)
            if orig is None:
                continue
            orig = orig.astype(np.uint8)
            fp, lp = out / "frames" / f"{v}_{f:02d}.png", out / "flat" / f"{v}_{f:02d}.png"
            fin = np.array(Image.open(fp).convert("RGB")) if fp.exists() else np.zeros_like(orig) + 24
            flat = np.array(Image.open(lp).convert("RGB")) if lp.exists() else np.zeros_like(orig) + 20
            masks = measure.layer_masks(prof, v, orig)
            T = measure.full_targets(masks, prof.groups(v)) if any(m.any() for m in masks.values()) else masks
            tgt = np.zeros_like(orig) + 20
            for l in prof.order(v):
                tgt[T[l]] = prof.flat(v, l)
            seq_o.append(_tile(orig, box, 360)); seq_r.append(_tile(fin, box, 360))
            comp = Image.new("RGB", (360 * 4, 360))
            for i, a in enumerate((orig, tgt, flat, fin)):
                comp.paste(_tile(a, box, 360), (360 * i, 0))
            comp.save(rv / "img" / f"{v}_{f:02d}_frame.png")
            sv = out / "svg" / f"{v}_{f:02d}.svg"
            loops = {m.group(1): parse_path_d(m.group(2)) for m in re.finditer(r'<path id="(\w+)"[^>]* d="([^"]*)"', sv.read_text())} if sv.exists() else {}
            fd = {}
            for l in reversed(prof.order(v)):
                k = f"{v}_{f:02d}_{l}"
                if k not in rep:
                    continue
                A = np.zeros_like(orig) + 20; A[T[l]] = prof.flat(v, l)
                img = Image.new("RGB", (900, 300))
                img.paste(_tile(A, box, 300), (0, 0)); img.paste(_tile(flat, box, 300), (300, 0))
                img.paste(_pen_view(loops.get(l, []), box, 300, prof.flat(v, l)), (600, 0))
                name = f"{v}_{f:02d}_{l}.png"
                img.save(rv / "img" / name)
                fd[l] = dict(img=name, **rep[k])
            vd["frames"][f"{f:02d}"] = fd
        for tag, ms in (("", int(1000 / fps)), ("_slow", 125)):
            seq = [Image.fromarray(np.hstack([np.array(o), np.array(r)])) for o, r in zip(seq_o, seq_r)]
            if seq:
                seq[0].save(rv / "img" / f"{v}_side{tag}.gif", save_all=True, append_images=seq[1:], duration=ms, loop=0)
        data["variants"][v] = vd
    html = PAGE.read_text().replace("__TITLE__", prof.name).replace("__DATA__", json.dumps(data))
    (rv / "index.html").write_text(html)
    return rv / "index.html"
