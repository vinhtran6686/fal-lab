"""Chuyển động người (motion.json từ fbx_motion.py) -> file thông số proxy của một nhân vật.

    python scripts/motion_proxy/retarget.py <motion.json> --base <proxy_x.json> --out <proxy_y.json>
        [--face 70] [--name ...] [--trim auto|none|T0,T1] [--hitstop 1]

Chuyển GÓC và NHỊP, không chuyển chiều dài xương, nên tỉ lệ nhân vật nguồn không rò sang:
  * pelvis_yaw: hướng đường nối hai hông; chest_off: vai so với hông (lag = 0, nguồn đã có trễ pha thật).
  * Vũ khí: nguồn là người tay không. Trục thương = đường nối hai bàn tay (giữ chiều liên tục),
    độ cao tay theo tỉ lệ trên đoạn vai-hông của nguồn, độ đẩy theo khoảng vươn của tay.
  * Hông: độ cao và dịch ngang nhân với tỉ lệ chân (base) / chân (nguồn).
  * Chân: tự tìm các đoạn chạm đất (thấp + gần như đứng yên), khoá mũi chân ở vị trí trung bình đoạn đó.
  * Xoay cả chuyển động để hướng thân lúc thủ thế = --face (90 = nhìn thẳng mục tiêu bên phải màn hình).
  * Khung trúng = đỉnh tốc độ đầu tay; chèn hitstop; pha và cửa sổ đo đặt theo khung trúng.
Thân, vũ khí, màu, camera lấy từ --base. Doc: docs/scripts/motion_proxy/motion-proxy-guide.md
"""
import argparse
import json
import math

import numpy as np


def unwrap_deg(a):
    return np.degrees(np.unwrap(np.radians(np.asarray(a, float))))


def yaw_of(v):
    return math.degrees(math.atan2(v[0], v[2]))


def smooth(x, k=5):
    k = max(1, k)
    pad = np.pad(x, ((k // 2, k // 2),) + ((0, 0),) * (x.ndim - 1), mode="edge")
    ker = np.ones(k) / k
    return np.apply_along_axis(lambda c: np.convolve(c, ker, mode="valid"), 0, pad)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("motion")
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="")
    ap.add_argument("--face", type=float, default=70.0)
    ap.add_argument("--trim", default="auto")
    ap.add_argument("--hitstop", type=int, default=1)
    ap.add_argument("--after", type=float, default=8, help="số khung giữ lại sau khung trúng (trim auto)")
    a = ap.parse_args()

    m = json.load(open(a.motion, encoding="utf-8"))
    base = json.load(open(a.base, encoding="utf-8"))
    fps_src = m["fps"]
    P = np.array(m["pos"], float)                     # khung x khớp x 3
    ix = {n: i for i, n in enumerate(m["joints"])}
    J = lambda n: P[:, ix[n]]                         # noqa: E731
    n = len(P)
    step = fps_src / base.get("fps", 15)              # khung nguồn trên một khung 15 fps
    tau = np.arange(n) / step

    # ---- mặt đất, tỉ lệ
    foot = np.minimum(J("L_Foot")[:, 1], J("R_Foot")[:, 1])
    ground = float(np.percentile(foot, 5))
    P[:, :, 1] -= ground
    hipmid = (J("L_Hip") + J("R_Hip")) / 2
    b = base["body"]
    leg_t = b["thigh"] + b["shin"] + b["ankle_h"]
    s = 0.97 * leg_t / float(np.percentile(hipmid[:, 1], 95))

    def fwd_from_right(r):
        f = np.cross([0.0, 1.0, 0.0], r)
        f[1] = 0
        return f / max(np.linalg.norm(f), 1e-9)

    # ---- khung trúng và lúc nhả (không phụ thuộc phép xoay): đỉnh tốc độ đầu tay
    hm0 = (J("R_Middle1") + J("L_Middle1")) / 2
    v = smooth(np.linalg.norm(np.diff(hm0, axis=0), axis=1) * fps_src, 3)
    hit_src = int(np.argmax(v)) + 1
    t_hit = round(hit_src / step)
    d0 = J("L_Middle1") - J("R_Middle1")
    for i in range(1, n):
        if np.dot(d0[i], d0[i - 1]) < 0:
            d0[i] = -d0[i]
    wv = np.gradient(unwrap_deg([yaw_of(q) for q in smooth(d0, 5)]))
    sgn = np.sign(wv[hit_src])
    rel_src = hit_src
    while rel_src > 1 and np.sign(wv[rel_src - 1]) == sgn:
        rel_src -= 1
    t_rel = rel_src / step
    if a.trim == "auto":
        t0 = max(0.0, math.floor(t_rel - 10))
        t1 = min(tau[-1], t_hit + a.after)
    elif a.trim == "none":
        t0, t1 = 0.0, float(tau[-1])
    else:
        t0, t1 = map(float, a.trim.split(","))

    # ---- xoay: hướng hông ở đầu đoạn được cắt -> --face
    hip_f = np.array([fwd_from_right(J("R_Hip")[i] - J("L_Hip")[i]) for i in range(n)])
    i0 = int(t0 * step)
    face0 = math.degrees(math.atan2(*np.mean(hip_f[i0: i0 + max(3, int(0.2 * fps_src))], axis=0)[[0, 2]]))
    th = math.radians(a.face - face0)
    R = np.array([[math.cos(th), 0, math.sin(th)], [0, 1, 0], [-math.sin(th), 0, math.cos(th)]])
    x0 = hipmid[i0].copy()
    x0[1] = 0
    P = (P - x0) @ R.T
    J = lambda n_: P[:, ix[n_]]                       # noqa: E731
    hipmid = (J("L_Hip") + J("R_Hip")) / 2
    zmean = float(hipmid[:, 2].mean())

    # ---- góc thân
    pel = unwrap_deg([yaw_of(fwd_from_right(J("R_Hip")[i] - J("L_Hip")[i])) for i in range(n)])
    sh_r = J("R_Shoulder") - J("L_Shoulder")
    chest = unwrap_deg([yaw_of(fwd_from_right(sh_r[i])) for i in range(n)])
    chest = pel + (((chest - pel) + 180) % 360 - 180)
    pel, chest = smooth(pel, 3), smooth(chest, 3)

    # ---- vũ khí từ hai bàn tay
    hR, hL = J("R_Middle1"), J("L_Middle1")
    d = hL - hR
    d = d / np.linalg.norm(d, axis=1, keepdims=True)
    fC = np.array([[math.sin(math.radians(c)), 0, math.cos(math.radians(c))] for c in chest])
    if np.dot(d[0], fC[0]) < 0:
        d[0] = -d[0]
    for i in range(1, n):                              # giữ chiều liên tục
        if np.dot(d[i], d[i - 1]) < 0:
            d[i] = -d[i]
    d = smooth(d, 5)
    d = d / np.linalg.norm(d, axis=1, keepdims=True)
    wyaw = unwrap_deg([yaw_of(v) for v in d])
    wyaw = pel + (((wyaw - pel) + 180) % 360 - 180)
    wyaw = unwrap_deg(wyaw)
    wpitch = np.degrees(np.arcsin(np.clip(d[:, 1], -1, 1)))
    shmid = (J("L_Shoulder") + J("R_Shoulder")) / 2
    hmid = (hR + hL) / 2
    torso = np.maximum(shmid[:, 1] - hipmid[:, 1], 0.2)
    drop = np.clip((shmid[:, 1] - hmid[:, 1]) / torso * b["spine"], -0.4, 1.1)
    arm_src = float(np.median(np.linalg.norm(J("R_Shoulder") - J("R_Elbow"), axis=1)
                              + np.linalg.norm(J("R_Elbow") - J("R_Wrist"), axis=1)))
    reach = np.einsum("ij,ij->i", hmid - shmid, fC) / arm_src
    slide = np.clip((reach - np.median(reach)) * 0.5, -0.2, 0.3)

    # ---- chân: đoạn chạm đất
    tracks = {"lift": 0.14}
    for side, jn in (("R", "R_Foot"), ("L", "L_Foot")):
        p = J(jn).copy()
        sp = np.r_[0, np.linalg.norm(np.diff(p[:, [0, 2]], axis=0), axis=1)] * fps_src
        contact = (p[:, 1] < 0.08) & (smooth(sp, 3) < 0.35)
        segs, i = [], 0
        while i < n:
            if contact[i]:
                j = i
                while j + 1 < n and contact[j + 1]:
                    j += 1
                segs.append([i, j])
                i = j + 1
            else:
                i += 1
        merged = []
        for sg in segs:                                # nối đoạn hở ngắn, bỏ đoạn quá ngắn
            if merged and sg[0] - merged[-1][1] <= 3:
                merged[-1][1] = sg[1]
            else:
                merged.append(sg)
        merged = [sg for sg in merged if sg[1] - sg[0] >= 2] or [[0, n - 1]]
        out = []
        for i0, i1 in merged:
            q = p[i0:i1 + 1].mean(axis=0)
            out.append({"t0": round(i0 / step, 3), "t1": round(i1 / step, 3),
                        "pos": [round(float(q[0] * s), 4), 0.0, round(float((q[2] - zmean) * s), 4)]})
        tracks[side] = out
        an = J("R_Ankle" if side == "R" else "L_Ankle")
        fy = unwrap_deg([yaw_of(np.r_[p[i, 0] - an[i, 0], 0, p[i, 2] - an[i, 2]]) for i in range(n)])
        tracks["yaw_" + side] = {f"{tau[i]:.3f}": round(float(fy[i]), 2) for i in range(0, n, 2)}

    keep = (tau >= t0 - 1e-6) & (tau <= t1 + 1e-6)

    def ch(arr, nd=3):
        return {f"{tau[i] - t0:.3f}": round(float(arr[i]), nd) for i in np.where(keep)[0]}

    def shift_tracks(tr):
        res = {"lift": tr["lift"]}
        for side in ("R", "L"):
            segs = [{"t0": max(0.0, sg["t0"] - t0), "t1": sg["t1"] - t0, "pos": sg["pos"]}
                    for sg in tr[side] if sg["t1"] >= t0 and sg["t0"] <= t1]
            res[side] = segs or [{"t0": 0.0, "t1": t1 - t0, "pos": tr[side][0]["pos"]}]
            res["yaw_" + side] = {f"{float(k) - t0:.3f}": v_ for k, v_ in tr["yaw_" + side].items()
                                   if t0 - 1 <= float(k) <= t1 + 1}
        return res

    T_hit, T_rel, T_end = t_hit - t0, t_rel - t0, math.floor(t1 - t0)
    p = dict(base)
    p["name"] = a.name or f"{base.get('name', '').split('/')[0].strip()} / text2motion"
    p["note"] = (f"Retarget từ {m.get('source', '')} ({n} khung @ {fps_src} fps), cắt τ {t0:.1f}–{t1:.1f}, "
                 f"xoay {math.degrees(th):+.0f}°, tỉ lệ chân {s:.3f}.")
    p["chain"] = dict(base["chain"], lag_chest=0.0, lag_weapon=0.0, foot_lag=0.0)
    p["channels"] = {
        "pelvis_yaw": ch(pel, 2),
        "chest_off": ch(chest - pel, 2),
        "weapon_off": ch(wyaw - pel, 2),
        "weapon_pitch": ch(np.clip(wpitch, -60, 80), 2),
        "hand_drop": ch(drop),
        "weapon_slide": ch(slide),
        "root_x": ch(hipmid[:, 0] * s),
        "root_y": ch(hipmid[:, 1] * s),
    }
    p["feet"] = {"tracks": shift_tracks(tracks)}
    p["timing"] = {
        "t_end": T_end, "t_hit": int(round(T_hit)), "hitstop_frames": a.hitstop,
        "phases": [[0, "thủ thế"], [max(0.0, T_rel - 4), "lấy đà"], [T_rel, "ra đòn"],
                   [int(round(T_hit)), "TRÚNG"], [int(round(T_hit)) + 1, "theo đà"],
                   [int(round(T_hit)) + 6, "hồi thế"]],
        "sweep_window": [max(0.0, T_rel - 1), T_hit + 2],
        "release_window": [max(0.0, T_rel - 4), T_rel + 3],
        "spin_heel_window": [0, 0], "spin_heel_lift": 0.0,
        "lunge_heel": {"start": 0, "rise": 1, "end": 0, "fall": 1, "lift": 0.0},
        "slash_windows": [[max(0.0, T_rel), T_hit + 1.5]],
    }
    p["checks"] = ["twist", "cross", "reach", "shift", "support", "weight", "antic", "sweep_hit"]
    p.pop("reference", None)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(p, fh, ensure_ascii=False, indent=1)
    print(f"tỉ lệ {s:.3f}, xoay {math.degrees(th):+.0f}°, nhả τ {t_rel:.1f}, trúng τ {t_hit} (nguồn khung {hit_src}), "
          f"cắt {t0:.1f}–{t1:.1f} -> {a.out}")
    for side in ("R", "L"):
        print(f"  chân {side}: {len(tracks[side])} đoạn chạm đất")


if __name__ == "__main__":
    main()
