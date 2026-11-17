# Pose3D

Trang chỉnh tư thế 3D kiểu Cascadeur: ma-nơ-canh trơn theo thân chính của nhân vật, phân cấp khớp FK, tay chân IK hai đoạn có điểm hướng, tay cầm trên khớp + gizmo (W/E/Q), thương là đạo cụ hai tay bám theo, kiểm tra vật lý, lưu tư thế.

```bash
python tools/pose3d/bake_motion.py <params_used.json> --name "<tên>" --out tools/pose3d/motion_<id>.json \
    --mannequin out/heroes/<id>/source/rig/mannequin_master.json --master-img tools/pose3d/master_<id>.webp
python tools/pose3d/build.py tools/pose3d/motion_<id>.json      # -> tools/pose3d/index.html
```

Bản đang dùng: https://claude.ai/artifact/447LvWyAucynhJRkVuXC6G (moon_crane, quét thương lai, thân đo từ master).
Hướng dẫn đầy đủ: `docs/tools/pose3d/pose3d-guide.md`.
