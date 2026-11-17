# Pose3D

Trang chỉnh tư thế 3D: người nộm đúng tỉ lệ nhân vật cầm vũ khí, tay bám vũ khí và chân bám đất bằng IK, kiểm tra vật lý, lưu tư thế.

```bash
python tools/pose3d/bake_motion.py <params_used.json> --name "<tên>" --out tools/pose3d/motion_<id>.json
python tools/pose3d/build.py tools/pose3d/motion_<id>.json      # -> tools/pose3d/index.html
```

Bản đang dùng: https://claude.ai/artifact/447LvWyAucynhJRkVuXC6G (moon_crane, quét thương lai v2).
Hướng dẫn đầy đủ: `docs/tools/pose3d/pose3d-guide.md`.
