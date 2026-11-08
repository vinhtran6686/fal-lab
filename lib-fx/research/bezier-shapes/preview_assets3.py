"""Review assets for v3 (rebuild3.py; v2 shown as the previous version): per-frame composites, per-layer panels with the pen-path anchors, motion GIFs."""
import json, io, re
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import cairosvg
from masks import family_masks, frame_rgb, FAMILY, iou
from rebuild2 import full_targets, ORDER

SRC, OUT = Path(__file__).parent / "out3", Path(__file__).parent / "preview3"
V1 = Path(__file__).parent / "out"
FRAMES = {"fire": range(2, 13), "frost": range(2, 10)}
HEX = lambda c: "#%02x%02x%02x" % tuple(c)

def crop_box(v):
    U = np.zeros((700, 700), bool)
    for f in FRAMES[v]:
        for m in family_masks(v, f).values():
            U |= m
    ys, xs = np.nonzero(U)
    s = max(ys.max() - ys.min(), xs.max() - xs.min()) + 30
    cy, cx = (ys.min() + ys.max()) // 2, (xs.min() + xs.max()) // 2
    x0, y0 = int(np.clip(cx - s // 2, 0, 700 - s)), int(np.clip(cy - s // 2, 0, 700 - s))
    return (x0, y0, x0 + s, y0 + s)

def parse_paths(svg_text):
    """{fill colour: [list of loops, each a list of (p0,p1,p2,p3)]} from our own SVG output."""
    out = {}
    for fill, d in re.findall(r'<path fill="(#[0-9a-f]{6})"[^>]* d="([^"]*)"', svg_text):
        loops = []
        for part in d.split("Z"):
            nums = [tuple(map(float, xy.split(","))) for xy in re.findall(r"-?[\d.]+,-?[\d.]+", part)]
            if len(nums) < 4:
                continue
            p0, segs = np.array(nums[0]), []
            for i in range(1, len(nums) - 2, 3):
                p1, p2, p3 = map(np.array, nums[i:i + 3])
                segs.append((p0, p1, p2, p3)); p0 = p3
            loops.append(segs)
        out[fill] = loops
    return out

def tile(a, box, size):
    return (Image.fromarray(a) if isinstance(a, np.ndarray) else a).crop(box).resize((size, size), Image.LANCZOS)

def anchor_view(loops, box, size, col):
    """Pen-path view: outline + anchors (white = smooth, red = corner) drawn at panel scale."""
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
        for i, (p0, p1, p2, p3) in enumerate(segs):
            prev = segs[i - 1]
            a, b = prev[3] - prev[2], p1 - p0
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            corner = na > 1e-6 and nb > 1e-6 and np.dot(a, b) / (na * nb) < 0.97
            x, y = T(p0)
            r = 2.6 if corner else 1.8
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 70, 70) if corner else (240, 240, 240))
    return im

def main():
    OUT.mkdir(exist_ok=True)
    rep = json.loads((SRC / "report.json").read_text())
    data = {}
    for v in FAMILY:
        pal = {l: FAMILY[v][l][0] for l in FAMILY[v]}
        box = crop_box(v)
        seq_o, seq_1, seq_2 = [], [], []
        data[v] = {"frames": {}}
        for f in FRAMES[v]:
            orig = frame_rgb(v, f).astype(np.uint8)
            p2 = SRC / f"{v}_{f:02d}.png"
            fin = np.array(Image.open(p2).convert("RGB")) if p2.exists() else np.zeros_like(orig) + 24
            flat = np.array(Image.open(SRC / f"{v}_{f:02d}_flat.png").convert("RGB")) if p2.exists() else np.zeros_like(orig) + 20
            v2p = Path(__file__).parent / f"out2/{v}_{f:02d}_flat.png"
            old = np.array(Image.open(v2p).convert("RGB")) if v2p.exists() else np.zeros_like(orig) + 20
            seq_o.append(tile(orig, box, 360)); seq_1.append(tile(old, box, 360)); seq_2.append(tile(fin, box, 360))
            comp = Image.new("RGB", (360 * 4, 360))
            for i, a in enumerate((orig, old, flat, fin)):
                comp.paste(tile(a, box, 360), (360 * i, 0))
            comp.save(OUT / f"{v}_{f:02d}_frame.png")
            masks = family_masks(v, f)
            T = full_targets(v, masks) if any(m.any() for m in masks.values()) else masks
            loops = parse_paths((SRC / f"{v}_{f:02d}.svg").read_text()) if p2.exists() else {}
            fd = {"layers": {}}
            for l in ORDER[v][::-1]:
                key = f"{v}_{f:02d}_{l}"
                if key not in rep:
                    continue
                A = np.zeros_like(orig) + 20; A[T[l]] = pal[l]
                lp = loops.get(HEX(pal[l]), [])
                img = Image.new("RGB", (300 * 3, 300))
                img.paste(tile(A, box, 300), (0, 0))
                img.paste(tile(flat, box, 300), (300, 0))
                img.paste(anchor_view(lp, box, 300, tuple(pal[l])), (600, 0))
                name = f"{v}_{f:02d}_{l}.png"
                img.save(OUT / name)
                r = rep[key]
                fd["layers"][l] = dict(img=name, iou=r["iou"], anchors=r["anchors"], corners=r["corners"], kinks=r["kinks"],
                                       curv_var=r["curv_var"])
            data[v]["frames"][f"{f:02d}"] = fd
        for tag, ms in (("", 40), ("_slow", 125)):
            seq = [Image.fromarray(np.hstack([np.array(o), np.array(b)])) for o, b in zip(seq_o, seq_2)]
            seq[0].save(OUT / f"{v}_side{tag}.gif", save_all=True, append_images=seq[1:], duration=ms, loop=0)
            seq = [Image.fromarray(np.hstack([np.array(o), np.array(a), np.array(b)])) for o, a, b in zip(seq_o, seq_1, seq_2)]
            seq[0].save(OUT / f"{v}_v2v3{tag}.gif", save_all=True, append_images=seq[1:], duration=ms, loop=0)
            seq_2[0].save(OUT / f"{v}_v3{tag}.gif", save_all=True, append_images=seq_2[1:], duration=ms, loop=0)
    (OUT / "data.json").write_text(json.dumps(data, indent=1))
    print("ok")

if __name__ == "__main__":
    main()
