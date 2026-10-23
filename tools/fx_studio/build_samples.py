"""Sample effect sheets for Fx Studio's "+ Thêm hiệu ứng → Mẫu", drawn with scripts/fx_layers.py's layer painters (flat,
2-3 tones of one colour, a dark outline of the same hue: the reference game's look). No model, no cost.

Usage: python tools/fx_studio/build_samples.py [--out out/fx_studio_artifact/samples]

Every sample is a grid sheet on a transparent background, drawn at @2x of a KR1 hero (body height 64 px @1x, so 128 px
here) at 15 drawings per second, written as <id>.png, plus samples.json:
  [{id, title, file, grid: [cols, rows], frames, scale: 0.5, anchor: [x, y from the top] = the feet in the cell}]
The app uses grid and anchor as given (no detection), so a tall pillar or a faded last drawing never splits or drops a
cell. Frames with nothing visible at the start or the end are cut before the sheet is made."""
import argparse, json, math, pathlib, sys
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import fx_layers as fl   # noqa: E402

HPX = 128                 # hero body height @2x
FPS = 15
DRAW = {"ring": fl.draw_ring, "slash": fl.draw_slash, "burst": fl.draw_burst, "pillar": fl.draw_pillar, "particles": fl.draw_particles}

# canvas [w, h] in body heights, pivot = the feet in the canvas (fractions from the left and the TOP), time in seconds.
# Coordinates in body heights from the feet, y up (fx_layers' units).
SAMPLES = [
    {"id": "explosion", "title": "Nổ lửa", "canvas": [3.0, 2.8], "pivot": [0.5, 0.8], "dur": 0.8, "layers": [
        {"type": "ring", "start": 0.0, "length": 0.6, "color": "#ff7a1a", "radius": [0.3, 1.3], "width": 0.16},
        {"type": "burst", "start": 0.0, "length": 0.55, "color": "#ff8a1e", "at": [0, 0.55], "radius": 0.85, "spikes": 9, "seed": 2},
        {"type": "burst", "start": 0.05, "length": 0.4, "color": "#ffd84a", "at": [0, 0.6], "radius": 0.5, "spikes": 7, "seed": 5},
        {"type": "particles", "start": 0.05, "length": 0.75, "color": "#ff9a2e", "at": [0, 0.5], "count": 14, "speed": 2.4, "size": 0.08, "spread": 200, "gravity": 3.0}]},
    {"id": "lightning", "title": "Sét đánh", "canvas": [2.4, 4.4], "pivot": [0.5, 0.88], "dur": 0.7, "layers": [
        {"type": "bolt", "start": 0.0, "length": 0.5, "color": "#9fd8ff", "at": [0, 0], "from": [0.3, 3.6], "top": 3.6, "width": 0.09, "kinks": 7, "seed": 3},
        {"type": "burst", "start": 0.08, "length": 0.4, "color": "#c9ecff", "at": [0, 0.15], "radius": 0.55, "spikes": 8, "seed": 4},
        {"type": "ring", "start": 0.1, "length": 0.55, "color": "#7cc4ff", "radius": [0.2, 1.0], "width": 0.12}]},
    {"id": "holy_pillar", "title": "Cột sáng thánh", "canvas": [2.4, 4.2], "pivot": [0.5, 0.85], "dur": 1.1, "layers": [
        {"type": "ring", "start": 0.0, "length": 1.0, "color": "#ffe27a", "radius": [0.4, 1.1], "width": 0.14},
        {"type": "pillar", "start": 0.05, "length": 1.0, "color": "#fff0a8", "at": [0, 0], "width": 0.8, "height": 3.4},
        {"type": "particles", "start": 0.2, "length": 0.9, "color": "#ffe27a", "at": [0, 0.3], "count": 12, "speed": 1.4, "size": 0.06, "spread": 60, "gravity": -1.5}]},
    {"id": "heal", "title": "Vòng hồi máu", "canvas": [2.8, 2.6], "pivot": [0.5, 0.8], "dur": 1.1, "layers": [
        {"type": "ring", "start": 0.0, "length": 1.0, "color": "#6fe08a", "radius": [0.3, 1.2], "width": 0.13},
        {"type": "particles", "start": 0.1, "length": 1.0, "color": "#9dffb0", "at": [0, 0.1], "count": 16, "speed": 1.2, "size": 0.07, "spread": 100, "gravity": -1.8, "seed": 6}]},
    {"id": "ice_shatter", "title": "Băng vỡ", "canvas": [2.8, 2.6], "pivot": [0.5, 0.8], "dur": 0.75, "layers": [
        {"type": "burst", "start": 0.0, "length": 0.5, "color": "#9be7ff", "at": [0, 0.55], "radius": 0.75, "spikes": 6, "seed": 1},
        {"type": "particles", "start": 0.05, "length": 0.7, "color": "#cfefff", "at": [0, 0.55], "count": 12, "speed": 2.6, "size": 0.1, "spread": 220, "gravity": 3.5, "seed": 9},
        {"type": "ring", "start": 0.05, "length": 0.5, "color": "#7fd3f5", "radius": [0.2, 0.9], "width": 0.1}]},
    {"id": "poison_cloud", "title": "Mây độc", "canvas": [3.0, 2.4], "pivot": [0.5, 0.8], "dur": 1.4, "layers": [
        {"type": "ring", "start": 0.0, "length": 1.3, "color": "#6fbf3a", "radius": [0.5, 1.3], "width": 0.12, "squash": 0.3},
        {"type": "particles", "start": 0.0, "length": 1.4, "color": "#8be04e", "at": [0, 0.3], "count": 22, "speed": 0.7, "size": 0.12, "spread": 360, "gravity": -0.4, "seed": 11, "time": 1.2}]},
    {"id": "slash", "title": "Vệt chém", "canvas": [2.6, 2.4], "pivot": [0.35, 0.8], "dur": 0.4, "layers": [
        {"type": "slash", "start": 0.0, "length": 0.4, "color": "#fff3c4", "at": [0.45, 0.6], "radius": 0.85, "from": 120, "to": -50, "width": 0.24}]},
    {"id": "shockwave", "title": "Sóng xung kích", "canvas": [4.0, 2.0], "pivot": [0.5, 0.7], "dur": 0.75, "layers": [
        {"type": "ring", "start": 0.0, "length": 0.7, "color": "#ffb347", "radius": [0.2, 1.8], "width": 0.2, "squash": 0.3},
        {"type": "ring", "start": 0.12, "length": 0.6, "color": "#ffd27a", "radius": [0.1, 1.2], "width": 0.12, "squash": 0.3},
        {"type": "burst", "start": 0.0, "length": 0.3, "color": "#ffe1a0", "at": [0, 0.2], "radius": 0.5, "spikes": 10, "seed": 6}]},
    {"id": "level_up", "title": "Lên cấp", "canvas": [2.4, 3.6], "pivot": [0.5, 0.85], "dur": 1.2, "layers": [
        {"type": "ring", "start": 0.0, "length": 1.0, "color": "#ffd84a", "radius": [0.4, 1.0], "width": 0.12},
        {"type": "pillar", "start": 0.0, "length": 0.8, "color": "#ffe98a", "at": [0, 0], "width": 0.55, "height": 2.6},
        {"type": "particles", "start": 0.15, "length": 1.0, "color": "#fff3a8", "at": [0, 0.4], "count": 14, "speed": 1.8, "size": 0.07, "spread": 50, "gravity": -1.0, "seed": 4}]},
    {"id": "hit_spark", "title": "Tia trúng đòn", "canvas": [1.8, 1.8], "pivot": [0.5, 0.75], "dur": 0.35, "layers": [
        {"type": "burst", "start": 0.0, "length": 0.3, "color": "#fff3b0", "at": [0, 0.5], "radius": 0.45, "spikes": 8, "seed": 8},
        {"type": "particles", "start": 0.0, "length": 0.35, "color": "#ffe27a", "at": [0, 0.5], "count": 8, "speed": 2.0, "size": 0.06, "spread": 360, "gravity": 1.0, "seed": 2}]},
]


def render(sp: dict) -> list:
    cw, ch = (round(v * HPX) for v in sp["canvas"])
    pivot = (cw * sp["pivot"][0], ch * sp["pivot"][1])
    n = max(1, math.ceil(sp["dur"] * FPS))
    frames = []
    for f in range(n):
        time = f / FPS
        comp = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        for ly in sp["layers"]:
            t = (time - ly["start"]) / ly["length"]
            if not 0 <= t <= 1:
                continue
            L = fl.Layer((cw, ch), pivot, HPX)
            c = fl.rgb(ly["color"])
            alpha = fl.draw_bolt(L, t, ly, c, f) if ly["type"] == "bolt" else DRAW[ly["type"]](L, t, ly, c)
            comp.alpha_composite(L.done(alpha * ly.get("alpha", 1.0)))
        frames.append(comp)
    visible = lambda im: int((np.asarray(im.getchannel("A")) > 25).sum()) > 20   # what the app keeps as a drawing
    while len(frames) > 1 and not visible(frames[-1]):
        frames.pop()
    while len(frames) > 1 and not visible(frames[0]):
        frames.pop(0)
    return frames


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default=str(ROOT / "out" / "fx_studio_artifact" / "samples"))
    main_out(pathlib.Path(p.parse_args().out))


def main_out(out: pathlib.Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for sp in SAMPLES:
        frames = render(sp)
        n, (cw, ch) = len(frames), frames[0].size
        cols = min(n, max(1, round(math.sqrt(n * ch / cw))))
        rows = -(-n // cols)
        sheet = Image.new("RGBA", (cw * cols, ch * rows), (0, 0, 0, 0))
        for i, im in enumerate(frames):
            sheet.paste(im, ((i % cols) * cw, (i // cols) * ch))
        sheet.save(out / f"{sp['id']}.png", optimize=True)
        index.append({"id": sp["id"], "title": sp["title"], "file": f"samples/{sp['id']}.png", "grid": [cols, rows], "frames": n,
                      "scale": 0.5, "anchor": sp["pivot"], "hold": round(30 / FPS)})
        print(f"{sp['id']}: {n} frames, cell {cw}x{ch} @2x, grid {cols}x{rows}")
    (out / "samples.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
