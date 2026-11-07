"""Comparison sheets: original | target masks (exact flat colours) | rebuilt from formulas | error map, frames 3-5."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cairosvg, io
from masks import LAYERS, clean_mask, frame_rgb, IDX

OUT = Path(__file__).parent / "out"

def main():
    rep = json.loads((OUT / "rebuild_report.json").read_text())
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for v, layers in LAYERS.items():
        pal = IDX[v + "_palette"]
        rows = []
        for f in (3, 4, 5):
            orig = frame_rgb(v, f).astype(np.uint8)
            tgt = np.zeros((700, 700, 3), np.uint8) + 20
            for l in layers:
                tgt[clean_mask(v, f, l)] = pal[l]
            png = cairosvg.svg2png(url=str(OUT / f"rebuild_{v}_{f:02d}.svg"))
            reb = np.array(Image.open(io.BytesIO(png)).convert("RGB"))
            err = np.zeros((700, 700, 3), np.uint8) + 20
            for l in layers:
                m = clean_mask(v, f, l)
                r = np.all(np.abs(reb.astype(int) - pal[l]) < 20, -1)
                err[m & r] = (np.array(pal[l]) * 0.45).astype(np.uint8)
                err[m & ~r] = (0, 230, 0)
                err[r & ~m] = (230, 0, 0)
            row = Image.fromarray(np.hstack([orig, tgt, reb, err]))
            d = ImageDraw.Draw(row)
            d.text((10, 8), f"{v} f{f}  original", fill="white", font=font)
            d.text((710, 8), "target: exact flat colours", fill="white", font=font)
            d.text((1410, 8), "rebuilt from stroke formulas (SVG)", fill="white", font=font)
            d.text((2110, 8), "error: green missed, red extra", fill="white", font=font)
            for i, l in enumerate(layers):
                k = rep[f"{v}_{f:02d}_{l}"]
                d.text((1420, 640 - 24 * (3 - i)), f"{l:8s} IoU {k['iou_clean']:.3f}  {k['shapes']} strokes", fill=tuple(pal[l]), font=font)
            rows.append(row)
        sheet = Image.new("RGB", (2800, 2100))
        for i, r in enumerate(rows):
            sheet.paste(r, (0, 700 * i))
        sheet.resize((1400, 1050), Image.LANCZOS).save(Path(__file__).parent / f"compare_{v}.png")
        print("wrote", f"compare_{v}.png")

if __name__ == "__main__":
    main()
