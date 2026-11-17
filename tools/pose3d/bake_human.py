"""Nướng chuyển động HY-Motion (khung xương người chuẩn SMPL-H) cho Pose3D, không gắn nhân vật.

    python tools/pose3d/bake_human.py <motion.json từ fbx_motion.py> --out tools/pose3d/motion_human_<tên>.json \
        [--name "<tên>"] [--rotate 102.082] [--step 2] [--height 1.75]

Toạ độ khớp nguồn (mét, y lên) được xoay quanh trục dọc (--rotate, độ, cùng công thức retarget.py) để đòn đánh hướng về
mục tiêu bên phải màn hình, hạ cho bàn chân chạm đất, rồi đổi sang đơn vị của tool (người cao --height mét = 3,0 đơn vị).
Thân (độ dài xương) lấy trung vị trên mọi khung, nên người nộm có đúng tỉ lệ người chuẩn của mô hình.
Doc: docs/tools/pose3d/pose3d-guide.md
"""
import argparse
import json
import math

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("motion")
ap.add_argument("--out", required=True)
ap.add_argument("--name", default="HY-Motion · người chuẩn")
ap.add_argument("--rotate", type=float, default=102.082, help="độ; mặc định = retarget của seed 1 (proxy_spear_sweep_hy.json)")
ap.add_argument("--step", type=int, default=2, help="lấy 1 khung mỗi STEP khung nguồn")
ap.add_argument("--height", type=float, default=1.75)
a = ap.parse_args()

d = json.load(open(a.motion, encoding="utf-8"))
names = d["joints"]
P = np.array(d["pos"], float)                                # [khung, khớp, 3]
th = math.radians(a.rotate)
Rm = np.array([[math.cos(th), 0, math.sin(th)], [0, 1, 0], [-math.sin(th), 0, math.cos(th)]])
P = P @ Rm.T
ix = {n: i for i, n in enumerate(names)}
J = lambda n: P[:, ix[n]]
ground = float(np.percentile(np.minimum(J("L_Foot")[:, 1], J("R_Foot")[:, 1]), 5)) - 0.01
P[:, :, 1] -= ground
s = 3.0 / a.height
P *= s
med = lambda x, y: float(np.median(np.linalg.norm(J(x) - J(y), axis=1)))
hipm = (J("L_Hip") + J("R_Hip")) / 2
ank_h = float(np.median(np.concatenate([J("L_Ankle")[:, 1] - J("L_Foot")[:, 1], J("R_Ankle")[:, 1] - J("R_Foot")[:, 1]])))
af = float(np.median(np.linalg.norm((J("L_Foot") - J("L_Ankle"))[:, [0, 2]], axis=1)))
body = {
    "height": 3.0, "head_r": round(0.105 * s, 3), "head_above_neck": 0.2 * s, "neck": 0.0,
    "spine": round(med("Spine1", "Spine3") + med("Spine3", "Neck") + float(np.median(np.linalg.norm(J("Spine1") - hipm, axis=1))), 3),
    "hip_half": round(med("L_Hip", "R_Hip") / 2, 3), "shoulder_half": round(med("L_Shoulder", "R_Shoulder") / 2 + 0.02 * s, 3),
    "thigh": round((med("L_Hip", "L_Knee") + med("R_Hip", "R_Knee")) / 2, 3),
    "shin": round((med("L_Knee", "L_Ankle") + med("R_Knee", "R_Ankle")) / 2, 3),
    "ankle_h": round(ank_h + 0.01 * s, 3), "foot_len": round(af + 0.08, 3), "af": round(af, 3),
    "upper_arm": round((med("L_Shoulder", "L_Elbow") + med("R_Shoulder", "R_Elbow")) / 2, 3),
    "forearm": round((med("L_Elbow", "L_Wrist") + med("R_Elbow", "R_Wrist")) / 2, 3),
    "fist_r": round(0.05 * s, 3), "grip_center": {"right": 0.0, "forward": 0.3}, "max_heel_lift": round(0.12 * s, 3),
    "mass": {"head": 0.08, "chest": 0.36, "pelvis": 0.24, "kneeR": 0.08, "kneeL": 0.08, "ankleR": 0.03, "ankleL": 0.03,
             "elbowR": 0.025, "elbowL": 0.025, "handR": 0.025, "handL": 0.025},
    # độ dài các đoạn thân của tool (pelvis = giữa hai hông -> Spine1 -> Spine3 -> Neck -> Head)
    "L": {"spineLow": round(float(np.median(np.linalg.norm(J("Spine1") - hipm, axis=1))), 3), "spineMid": round(med("Spine1", "Spine3"), 3),
          "chestTop": round(med("Spine3", "Neck"), 3), "neck": round(med("Neck", "Head"), 3), "headC": round(0.09 * s, 3), "clavIn": 0.03 * s},
}
R = {"pelvis": [0.15 * s, 0.075 * s, 0.1 * s], "belly": [0.14 * s, 0.1 * s, 0.1 * s], "chest": [0.18 * s, 0, 0.115 * s], "neck": 0.05 * s,
     "upper": [0.05 * s, 0.042 * s], "fore": [0.043 * s, 0.032 * s], "hand": [0.045 * s, 0.09 * s, 0.022 * s],
     "thigh": [0.078 * s, 0.055 * s], "shin": [0.055 * s, 0.038 * s], "foot": [0.045 * s, 0.035 * s]}
R = {k: ([round(x, 3) for x in v] if isinstance(v, list) else round(v, 3)) for k, v in R.items()}
fps = d["fps"] / a.step
frames = []
for i in range(0, len(P), a.step):
    frames.append({"t": round(i / d["fps"], 2), "phase": f"khung nguồn {i}",
                   "J": {n: [round(float(v), 4) for v in P[i, ix[n]]] for n in names}})
out = {"name": a.name, "mode": "human", "title": "Pose3D · người chuẩn (HY-Motion)",
       "subtitle": f"Khung xương người chuẩn của HY-Motion (cao {a.height} m = 3,0 đơn vị), chuyển động gốc của mô hình, chưa gắn nhân vật. Mục tiêu ở bên phải màn hình.",
       "fps": fps, "source": d.get("source", ""), "rotate_deg": a.rotate, "body": body, "R": R,
       "weapon": {"length": round(1.9 * s, 3), "grip_rear": round(0.65 * s, 3), "grip_gap": round(0.4 * s, 3), "blade_len": round(0.32 * s, 3),
                  "blade_half_w": round(0.06 * s, 3), "crescent_r": round(0.08 * s, 3)},
       "frames": frames}
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"{len(frames)} khung @ {fps:g} fps, thân {body['thigh']}/{body['shin']} chân, tay {body['upper_arm']}/{body['forearm']} -> {a.out}")
