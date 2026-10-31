#!/usr/bin/env python
"""Sprite frames -> motion reference mp4 for minimax/h3-max/reference-to-video.

One fixed crop box over all frames (keeps the registration between frames), one scale, the frames
centred on a flat white square canvas, encoded so the API accepts it (>= 24 fps, 2-15 s).

  python scripts/make_ref_video.py --src "E:/.../Blaze_pibe_{i:04d}.png" --first 162 --last 204 \
      --out ref/sprite/uppercut --name ref_uppercut --seconds 5
Or from a folder of numbered pngs: --src "ref/sprite/slash/frames/f{i:02d}.png" --first 1 --last 46
"""
import argparse, pathlib, subprocess
from PIL import Image


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--src", required=True, help="path pattern with {i[:fmt]}")
    a.add_argument("--first", type=int, required=True)
    a.add_argument("--last", type=int, required=True, help="inclusive")
    a.add_argument("--out", required=True, help="folder: frames/ and <name>.mp4 go here")
    a.add_argument("--name", default="ref")
    a.add_argument("--seconds", type=float, default=5.0, help="length of the mp4; match the clip you will ask for")
    a.add_argument("--size", type=int, default=704)
    a.add_argument("--margin", type=int, default=12, help="px around the union of all frames")
    a.add_argument("--fps", type=int, default=30)
    a.add_argument("--bg", default="255,255,255")
    a = a.parse_args()

    ids = range(a.first, a.last + 1)
    frames = [Image.open(a.src.format(i=i)).convert("RGBA") for i in ids]
    W, H = frames[0].size
    x0 = y0 = 10**9
    x1 = y1 = 0
    for f in frames:
        b = f.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox()
        if b:
            x0, y0, x1, y1 = min(x0, b[0]), min(y0, b[1]), max(x1, b[2]), max(y1, b[3])
    m = a.margin
    box = (max(0, x0 - m), max(0, y0 - m), min(W, x1 + m), min(H, y1 + m))
    w, h = box[2] - box[0], box[3] - box[1]
    S = min(a.size / w, a.size / h) * 0.97
    bg = tuple(int(v) for v in a.bg.split(",")) + (255,)

    out = pathlib.Path(a.out)
    fd = out / "frames"
    fd.mkdir(parents=True, exist_ok=True)
    for k, f in enumerate(frames):
        c = f.crop(box).resize((int(w * S), int(h * S)), Image.LANCZOS)
        can = Image.new("RGBA", (a.size, a.size), bg)
        can.alpha_composite(c, ((a.size - c.width) // 2, (a.size - c.height) // 2))
        can.convert("RGB").save(fd / f"u{k:02d}.png")

    n = len(frames)
    mp4 = out / f"{a.name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", f"{n / a.seconds:.4f}",
                    "-i", str(fd / "u%02d.png"), "-vf", f"fps={a.fps}", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "18", str(mp4)], check=True)
    print(f"{n} frames, box {box}, scale {S:.2f}, {mp4} ({a.seconds}s @ {a.fps} fps)")


if __name__ == "__main__":
    main()
