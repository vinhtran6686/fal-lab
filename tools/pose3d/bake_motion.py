"""Nướng một chuyển động proxy (params_used.json) thành dữ liệu điều khiển từng khung cho Pose3D.

    python tools/pose3d/bake_motion.py <params_used.json> --name "<tên>" --out tools/pose3d/motion_<id>.json

Mỗi khung: hông (vị trí), góc hông / ngực / đầu / thương, độ nghiêng thương, độ hạ tay, độ đẩy thương, mũi hai chân và
góc bàn chân. Kèm thân (tỉ lệ), thương, khối lượng và bảng màu của nhân vật để Pose3D dựng đúng người nộm.
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts", "motion_proxy"))
from skeleton import Proxy  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("params")
    ap.add_argument("--name", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mannequin", help="mannequin_*.json đo từ master: thay thân, vũ khí và thêm hình khối + ảnh master")
    ap.add_argument("--master-img", help="ảnh master đã tách nền (webp/png) để so trong trang")
    a = ap.parse_args()
    P = Proxy(a.params)
    seen, frames = set(), []
    for t in P.frame_times():
        if t in seen:
            continue
        seen.add(t)
        J, inf = P.pose(t)
        fy = lambda side: (P.foot_yaw(side, t, inf["yaw_pelvis"]) if P.tracks else inf["yaw_pelvis"])  # noqa: E731
        r = lambda v: [round(float(x), 4) for x in v]  # noqa: E731
        frames.append({"t": t, "phase": P.phase_of(t), "pelvis": r(J["pelvis"]),
                       "yawP": round(inf["yaw_pelvis"], 2), "yawC": round(inf["yaw_chest"], 2), "yawH": round(inf["yaw_head"], 2),
                       "wYaw": round(inf["yaw_weapon"], 2), "wPitch": round(inf["weapon_pitch"], 2),
                       "handDrop": round(P.ch["hand_drop"](t), 4), "slide": round(P.ch["weapon_slide"](t), 4),
                       "toeR": r(J["toeR"]), "toeL": r(J["toeL"]), "fyR": round(fy("R"), 2), "fyL": round(fy("L"), 2)})
    out = {"name": a.name, "fps": P.fps, "hit": P.tm["t_hit"], "body": P.b, "weapon": P.w,
           "palette": P.p["palette"], "frames": frames}
    if a.mannequin:
        man = json.load(open(a.mannequin, encoding="utf-8"))
        out["body"], out["weapon"], out["shape"] = man["body"], dict(P.w, **man["weapon"]), man["shape"]
        mp = man["measured_px"]
        out["master"] = {"px_per_unit": man["px_per_unit"], "ground_y": mp["ground_y"],
                         "center_x": (mp["hip_R"][0] + mp["hip_L"][0]) / 2, "size_px": 1024}
    if a.master_img:
        import base64
        ext = os.path.splitext(a.master_img)[1].lstrip(".").replace("jpg", "jpeg")
        out.setdefault("master", {})["img"] = f"data:image/{ext};base64," + base64.b64encode(open(a.master_img, "rb").read()).decode()
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    print(len(frames), "khung ->", a.out, os.path.getsize(a.out), "byte")


if __name__ == "__main__":
    main()
