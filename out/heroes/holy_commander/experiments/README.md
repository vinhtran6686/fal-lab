# Thí nghiệm (2026-10-21) cho phần cập nhật skill

Ba clip thử, không thuộc bộ assets đã export, để kiểm các đề xuất của `docs/skill-update-proposal-from-holy-commander.md`. Mỗi clip 4 s từ `master_v07`, h3-max-turbo, ~0,06 USD (ước tính).
| File | Thử gì | Kết quả ngắn |
|---|---|---|
| `test_1080p_slash_body.mp4` | cùng prompt và ảnh đầu với take slash 480P, nhưng 1080P | 1920x1080, 24 fps, cùng chuỗi chuyển động; sắc hơn, viền bán trong suốt khi key giảm một nửa; file ~5 lần lớn hơn |
| `test_strain.mp4` | gồng, run khi nắm chặt | tư thế gồng đúng; run rất nhỏ (~0,7 px ở khổ 480P), không nhìn thấy ở cỡ game |
| `test_offbalance.mp4` | cú vung nặng làm mất thăng bằng | cú vung quá đà đọc được, không phải vấp bước nghĩa đen; có vệt chém nhạt |
Prompt: `*.prompt.txt`; job: `*.json`.
