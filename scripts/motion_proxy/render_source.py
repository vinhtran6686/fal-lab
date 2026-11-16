"""Dựng chuyển động nguồn (FBX) ở góc camera game, khớp từng khung với proxy đã retarget, rồi ghép cạnh nhau.

    python scripts/motion_proxy/render_source.py <proxy.json> <file.fbx> <thư mục build của proxy> [--label ...]

Đọc 'retarget' trong proxy.json (cắt, góc xoay, khung nguồn trên một khung). Kiểm tra góc hông của bản 3D sau
khi xoay khớp góc hông của proxy (in sai lệch lớn nhất). Ra trong thư mục build: source3d/fNN.png,
compare_3d.gif (15 fps), compare_3d_slow.gif, compare_3d_key.png. Cần Blender dạng module (requirements-motion.txt)
và EGL (Linux: libegl1, libegl-mesa0).
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skeleton import Proxy  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proxy")
    ap.add_argument("fbx")
    ap.add_argument("build_dir")
    ap.add_argument("--label", default="HY-Motion 3D")
    a = ap.parse_args()
    import bpy
    P = Proxy(a.proxy)
    rt = P.p["retarget"]
    ts = P.frame_times()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.abspath(a.fbx))
    sc = bpy.context.scene
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    f0 = int(arm.animation_data.action.frame_range[0])

    def src_frame(t):
        return f0 + int(round((t + rt["t0"]) * rt["src_per_frame"]))
    sc.frame_set(src_frame(0))
    hip = (arm.matrix_world @ arm.pose.bones["Pelvis"].head).copy()
    piv = bpy.data.objects.new("pivot", None)
    sc.collection.objects.link(piv)
    piv.location = (hip.x, hip.y, 0)
    bpy.context.view_layer.update()
    for o in list(bpy.data.objects):
        if o.parent is None and o is not piv:
            mw = o.matrix_world.copy()
            o.parent = piv
            o.matrix_world = mw
    piv.rotation_euler = (0, 0, math.radians(rt["rotate_deg"]))

    def hip_yaw():
        bpy.context.view_layer.update()
        R = arm.matrix_world @ arm.pose.bones["R_Hip"].head
        L = arm.matrix_world @ arm.pose.bones["L_Hip"].head
        f = np.cross([0, 1, 0], [R.x - L.x, R.z - L.z, -(R.y - L.y)])
        return math.degrees(math.atan2(f[0], f[2])) % 360
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "OBJECT"
    for o in bpy.data.objects:
        if o.type == "MESH":
            o.color = (0.62, 0.66, 0.72, 1)
    sc.render.resolution_x, sc.render.resolution_y = 390, 240
    sc.world = bpy.data.worlds.new("w")
    sc.world.color = (0.08, 0.08, 0.09)
    cam = bpy.data.cameras.new("c")
    cam.type = "ORTHO"
    cam.ortho_scale = 4.6
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    pitch = P.p.get("camera", {}).get("pitch_deg", 15)
    co.location = (hip.x + 0.6, hip.y - 8, 1.0 + 8 * math.tan(math.radians(pitch)))
    co.rotation_euler = (math.radians(90 - pitch), 0, 0)
    out3 = os.path.join(a.build_dir, "source3d")
    os.makedirs(out3, exist_ok=True)
    err = []
    for k, t in enumerate(ts):
        sc.frame_set(src_frame(t))
        err.append(abs(((hip_yaw() - P.ch["pelvis_yaw"](t) % 360) + 180) % 360 - 180))
        sc.render.filepath = os.path.join(out3, f"f{k:02d}.png")
        bpy.ops.render.render(write_still=True)
    print(f"sai lệch góc hông 3D so với proxy: tối đa {max(err):.1f}°")

    font = None
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        if os.path.exists(p):
            font = ImageFont.truetype(p, 15)
    frames = []
    for k, t in enumerate(ts):
        A = Image.open(os.path.join(out3, f"f{k:02d}.png")).convert("RGB").resize((585, 360))
        B = Image.open(os.path.join(a.build_dir, "clean", f"f{k:02d}.png")).convert("RGB")
        B = B.crop((0, 40, B.width, B.height)).resize((585, 330))
        cv = Image.new("RGB", (1170, 392), (40, 41, 44))
        cv.paste(A, (0, 32))
        cv.paste(B, (585, 47))
        d = ImageDraw.Draw(cv)
        d.text((8, 8), a.label, font=font, fill=(230, 230, 230))
        ph = P.phase_of(t)
        d.text((593, 8), f"{P.p.get('name', '')} · khung {k:02d} · {ph}", font=font,
               fill=(255, 120, 100) if "TRÚNG" in ph else (230, 230, 230))
        frames.append(cv)
    frames[0].save(os.path.join(a.build_dir, "compare_3d.gif"), save_all=True, append_images=frames[1:],
                   duration=1000 // P.fps, loop=0)
    frames[0].save(os.path.join(a.build_dir, "compare_3d_slow.gif"), save_all=True, append_images=frames[1:],
                   duration=220, loop=0)
    sel = np.linspace(0, len(frames) - 1, 8).round().astype(int)
    sh = Image.new("RGB", (1170, 196 * 4), (40, 41, 44))
    for j, k in enumerate(sel):
        sh.paste(frames[k].resize((585, 196)), ((j % 2) * 585, (j // 2) * 196))
    sh.save(os.path.join(a.build_dir, "compare_3d_key.png"))


if __name__ == "__main__":
    main()
