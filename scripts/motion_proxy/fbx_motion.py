"""Đọc chuyển động từ FBX (khung xương SMPL-H của HY-Motion) ra toạ độ khớp từng khung.

    python scripts/motion_proxy/fbx_motion.py <file.fbx> [--out motion.json]

Cần Blender dạng module Python (pip install bpy). Ra motion.json:
  fps, frames, joints [tên], pos[khung][khớp] = [x, y, z] mét, hệ toạ độ y lên (đổi từ z lên của Blender),
  scale_note. Hướng mặt và chiều trái/phải để nguyên như nguồn; retarget.py lo việc xoay về mục tiêu.
"""
import argparse
import json
import pathlib

KEEP = ["Pelvis", "L_Hip", "L_Knee", "L_Ankle", "L_Foot", "R_Hip", "R_Knee", "R_Ankle", "R_Foot",
        "Spine1", "Spine2", "Spine3", "Neck", "Head", "L_Collar", "L_Shoulder", "L_Elbow", "L_Wrist",
        "R_Collar", "R_Shoulder", "R_Elbow", "R_Wrist", "L_Middle1", "R_Middle1"]


def extract(fbx):
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    act = arm.animation_data.action
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    sc = bpy.context.scene
    names = [n for n in KEEP if n in arm.pose.bones]
    pos = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        row = []
        for n in names:
            p = arm.matrix_world @ arm.pose.bones[n].head
            row.append([round(p.x, 5), round(p.z, 5), round(-p.y, 5)])   # z lên -> y lên
        pos.append(row)
    return {"fps": sc.render.fps, "frames": len(pos), "joints": names, "pos": pos,
            "source": pathlib.Path(fbx).name, "frame_range": [f0, f1],
            "axes": "x = x Blender, y = z Blender (lên), z = -y Blender"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fbx")
    ap.add_argument("--out")
    a = ap.parse_args()
    m = extract(a.fbx)
    out = pathlib.Path(a.out) if a.out else pathlib.Path(a.fbx).with_name("motion.json")
    out.write_text(json.dumps(m), encoding="utf-8")
    print(f"{m['frames']} khung @ {m['fps']} fps, {len(m['joints'])} khớp -> {out}")


if __name__ == "__main__":
    main()
