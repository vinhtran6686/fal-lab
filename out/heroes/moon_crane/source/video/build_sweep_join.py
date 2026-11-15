#!/usr/bin/env python3
"""Rebuild sweep_spear_join.mp4 from the two takes using the frame ranges in sweep_spear_join.json.

    python out/heroes/moon_crane/source/video/build_sweep_join.py [--out DIR]

Needs ffmpeg on PATH. Frames are cut at the take's own 24 fps and 768x768, the dropped ranges are skipped.
"""
import argparse, json, pathlib, shutil, subprocess, tempfile

HERE = pathlib.Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "sweep_spear_join.mp4"))
    a = ap.parse_args()
    rec = json.loads((HERE / "sweep_spear_join.json").read_text())
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        cut = {}
        for k, t in rec["takes"].items():
            d = td / k
            d.mkdir()
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / t["file"]), str(d / "%03d.png")], check=True)
            cut[k] = d
        n = 0
        seq = td / "seq"
        seq.mkdir()
        for r in rec["join_frames_1_based"]:
            for i in range(r["from"], r["to"] + 1):
                n += 1
                shutil.copy(cut[r["take"]] / f"{i:03d}.png", seq / f"{n:03d}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(rec["fps"]), "-i", str(seq / "%03d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", a.out], check=True)
    print(f"{n} frames -> {a.out}")


if __name__ == "__main__":
    main()
