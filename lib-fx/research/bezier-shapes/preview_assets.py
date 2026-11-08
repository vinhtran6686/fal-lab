"""Assets for the review page: per-shape panels (target | rebuilt | strokes | error) per frame, frame composites, GIFs."""
import json, io
from pathlib import Path
import numpy as np
from PIL import Image
import cairosvg
from masks import LAYERS, clean_mask, frame_rgb, IDX, iou
from shapes import stroke_path
from rebuild import render, raster_union

OUT = Path(__file__).parent / "preview"
SRC = Path(__file__).parent / "out"
FRAMES = {"fire": range(2, 13), "frost": range(2, 10)}
BG = np.array([20, 20, 20], np.uint8)

def crop_box(v):
    U = np.zeros((700, 700), bool)
    for f in FRAMES[v]:
        for l in LAYERS[v]:
            U |= clean_mask(v, f, l)
    ys, xs = np.nonzero(U)
    y0, y1, x0, x1 = ys.min() - 12, ys.max() + 12, xs.min() - 12, xs.max() + 12
    s = max(y1 - y0, x1 - x0)
    cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
    y0, x0 = max(cy - s // 2, 0), max(cx - s // 2, 0)
    return (x0, y0, min(x0 + s, 700), min(y0 + s, 700))

def svg_png(path):
    return np.array(Image.open(io.BytesIO(cairosvg.svg2png(url=str(path)))).convert("RGB"))

def tile(a, box, size):
    return Image.fromarray(a).crop(box).resize((size, size), Image.LANCZOS)

def main():
    OUT.mkdir(exist_ok=True)
    data = {}
    for v, layers in LAYERS.items():
        pal = {l: np.array(c, np.uint8) for l, c in IDX[v + "_palette"].items()}
        box = crop_box(v)
        frames_o, frames_r = [], []
        data[v] = {"frames": {}}
        for f in FRAMES[v]:
            P = json.loads((SRC / f"params_{v}_{f:02d}.json").read_text())
            orig = frame_rgb(v, f).astype(np.uint8)
            reb = svg_png(SRC / f"rebuild_{v}_{f:02d}.svg")
            tgt = np.zeros_like(orig) + BG
            for l in layers:
                tgt[clean_mask(v, f, l)] = pal[l]
            frames_o.append(tile(orig, box, 420)); frames_r.append(tile(reb, box, 420))
            comp = Image.new("RGB", (420 * 3, 420))
            for i, a in enumerate((orig, tgt, reb)):
                comp.paste(tile(a, box, 420), (420 * i, 0))
            comp.save(OUT / f"{v}_{f:02d}_frame.png")
            fd = {"layers": {}}
            for l in layers:
                m = clean_mask(v, f, l)
                shapes = P["layers"].get(l, [])
                if m.sum() < 12 and not shapes:
                    continue
                c = tuple(P["centre"])
                rm = render(shapes, c) if shapes else np.zeros_like(m)
                A = np.zeros_like(orig) + BG; A[m] = pal[l]
                B = np.zeros_like(orig) + BG; B[rm] = pal[l]
                # strokes: each added stroke its own shade, notches drawn dark red on top
                S = np.zeros_like(orig) + BG
                rng = np.random.default_rng(len(shapes) + f)
                for p in sorted([p for p in shapes if p["op"] == "add"], key=lambda p: -p["area"]):
                    k = rng.uniform(0.45, 1.0)
                    S[raster_union([stroke_path(p, c)])] = (pal[l] * k + 255 * (1 - k) * 0.35).astype(np.uint8)
                for p in shapes:
                    if p["op"] == "cut":
                        S[raster_union([stroke_path(p, c)])] = (150, 20, 40)
                E = np.zeros_like(orig) + BG
                E[m & rm] = (pal[l] * 0.4).astype(np.uint8); E[m & ~rm] = (40, 220, 60); E[rm & ~m] = (235, 50, 50)
                img = Image.new("RGB", (300 * 4, 300))
                for i, a in enumerate((A, B, S, E)):
                    img.paste(tile(a, box, 300), (300 * i, 0))
                name = f"{v}_{f:02d}_{l}.png"
                img.save(OUT / name)
                fd["layers"][l] = dict(img=name, iou=round(iou(rm, m), 3), strokes=sum(p["op"] == "add" for p in shapes),
                                       cuts=sum(p["op"] == "cut" for p in shapes), px=int(m.sum()))
            data[v]["frames"][f"{f:02d}"] = fd
        for tag, ms in (("", 40), ("_slow", 125)):
            seq = [Image.fromarray(np.hstack([np.array(o), np.array(r)])) for o, r in zip(frames_o, frames_r)]
            seq[0].save(OUT / f"{v}_side{tag}.gif", save_all=True, append_images=seq[1:], duration=ms, loop=0)
            frames_r[0].save(OUT / f"{v}_rebuilt{tag}.gif", save_all=True, append_images=frames_r[1:], duration=ms, loop=0)
    (OUT / "data.json").write_text(json.dumps(data, indent=1))
    print("ok")

if __name__ == "__main__":
    main()
