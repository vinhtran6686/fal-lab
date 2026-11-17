# Pose3D

Trang chỉnh tư thế 3D kiểu Cascadeur: ma-nơ-canh trơn theo thân chính của nhân vật, phân cấp khớp FK, tay chân IK hai đoạn có điểm hướng, tay cầm trên khớp + gizmo (W/E/Q), thương là đạo cụ hai tay bám theo, kiểm tra vật lý, lưu tư thế.

```bash
python tools/pose3d/bake_motion.py <params_used.json> --name "<tên>" --out tools/pose3d/motion_<id>.json \
    --mannequin out/heroes/<id>/source/rig/mannequin_master.json --master-img tools/pose3d/master_<id>.webp
python tools/pose3d/build.py tools/pose3d/motion_<id>.json      # -> tools/pose3d/index.html
```

Người chuẩn (chuyển động gốc của HY-Motion, khung xương SMPL-H, không gắn nhân vật):

```bash
python scripts/motion_proxy/fbx_motion.py <hy_motion.fbx> --out .work/hy.json
python tools/pose3d/bake_human.py .work/hy.json --out tools/pose3d/motion_human_<tên>.json --rotate <độ>
python tools/pose3d/build.py tools/pose3d/motion_human_<tên>.json
```

Bản đang dùng: https://claude.ai/artifact/447LvWyAucynhJRkVuXC6G (người chuẩn, HY-Motion seed 1 quét thương; bản moon_crane build lại từ `motion_moon_crane_spear_sweep.json`).
Hướng dẫn đầy đủ: `docs/tools/pose3d/pose3d-guide.md`.
