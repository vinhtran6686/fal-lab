# bezier-shapes: dựng lại hình VFX vẽ tay bằng path Bézier

Nhiệm vụ: [BRIEF.md](BRIEF.md). Kết luận: [FINDINGS.md](FINDINGS.md). Dữ liệu: [ref/vfx/swirl-slash/](../../../ref/vfx/swirl-slash/README.md).

## Chạy (theo thứ tự, ~1 phút, 0 USD)

```bash
pip install scikit-image opencv-python-headless cairosvg   # ngoài Pillow/numpy/scipy
cd lib-fx/research/bezier-shapes
python vectorize.py   # bước 1: vector hoá mặt nạ -> out/trace/*.svg, out/overlay_*.svg, out/trace_stats.json
python rebuild.py     # bước 3-4: đo tham số nét, dựng lại f3-f5 -> out/rebuild_*.svg, out/params_*.json, out/rebuild_report.json
python analyze.py     # bước 2: thống kê cấu trúc path + tham số theo loại hình -> out/analysis.json
python compare.py     # ảnh so sánh compare_fire.png, compare_frost.png
python generate.py    # demo dùng lại: hình MỚI chỉ từ công thức + luật đo được -> generated_demo.png
```

## File

| File | Vai trò |
|---|---|
| `masks.py` | mặt nạ sạch: đúng mã màu phẳng (sai số < 12), không phải mặt nạ < 30 bị lẫn quầng sáng |
| `bezier.py` | bộ công cụ Bézier bậc 3: fit kiểu Schneider, phát hiện góc nhọn, raster, SVG |
| `polar.py` | tâm xoáy, mở toạ độ cực, tách mặt nạ thành **dải cực** (mỗi góc một đoạn bán kính) |
| `shapes.py` | **hàm sinh path**: `stroke` (nét thon trong toạ độ cực) + preset theo loại hình |
| `fit.py` | đo tham số của nét từ một dải (bình phương tối thiểu, độ phức tạp tăng dần khi cần) |
| `rebuild.py` | thân trơn trước (fit bền vững) rồi thêm lưỡi / khoét vết, chỉ giữ mảnh nào tăng IoU |
| `analyze.py`, `compare.py`, `generate.py`, `diag.py` | thống kê, ảnh so sánh, demo sinh mới, ảnh lỗi một lớp |
