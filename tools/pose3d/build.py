"""Ghép dữ liệu chuyển động đã nướng vào trang Pose3D.

    python tools/pose3d/build.py tools/pose3d/motion_<id>.json [--out tools/pose3d/index.html]
"""
import argparse, os
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("motion")
ap.add_argument("--out", default=os.path.join(HERE, "index.html"))
a = ap.parse_args()
tpl = open(os.path.join(HERE, "pose3d.template.html"), encoding="utf-8").read()
data = open(a.motion, encoding="utf-8").read().replace("</", "<\\/")
open(a.out, "w", encoding="utf-8").write(tpl.replace("/*MOTION_DATA*/", data))
print("->", a.out, os.path.getsize(a.out), "byte")
