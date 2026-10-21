# Thí nghiệm (2026-10-21) cho phần cập nhật skill

Bốn clip thử, không thuộc bộ assets đã export, để kiểm các đề xuất của `docs/skill-update-proposal-from-holy-commander.md`. Mỗi clip 4 s từ `master_v07`, h3-max-turbo, ~0,06 USD (ước tính).
| File | Thử gì | Kết quả ngắn |
|---|---|---|
| `test_1080p_slash_body.mp4` | cùng prompt và ảnh đầu với take slash 480P, nhưng 1080P | 1920x1080, 24 fps, cùng chuỗi chuyển động; sắc hơn, viền bán trong suốt khi key giảm một nửa; file ~5 lần lớn hơn |
| `test_strain.mp4` | gồng, run khi nắm chặt | tư thế gồng đúng; run rất nhỏ (~0,7 px ở khổ 480P), không nhìn thấy ở cỡ game |
| `test_strain_violent.mp4` | gồng, mô tả run PHÓNG ĐẠI ("violent shake") | ~3 lần biên độ dọc của `test_strain` (p2p 5,6 px so với 2,4 px ở khổ 480P) nhưng ở cỡ game vẫn chỉ ~0,85 px @1x: tư thế gồng, áo choàng bay, run vẫn nhỏ |
| `test_offbalance.mp4` | cú vung nặng làm mất thăng bằng | cú vung quá đà đọc được, không phải vấp bước nghĩa đen; có vệt chém nhạt |
Prompt: `*.prompt.txt`; job: `*.json`.

`shake_demo.mp4` (tạo bằng `tools/frame_tuner/shake_demo.py`): 4 ô cạnh nhau ở đúng cỡ game, 15 fps: (1) run theo prompt, (2) run phóng đại, (3) run theo prompt + run hậu kỳ, (4) run phóng đại + run hậu kỳ. Biên độ thân đo trên khung @2x đã export (peak-to-peak x/y): 1.3/1.5, 1.2/2.6, 4.4/2.8, 4.3/4.1. Run hậu kỳ = trường `shake` trong công thức frame (`{"from","to","amp","seed"}`, chỉ số theo danh sách frame đã giữ), `apply_recipe.shake_offsets`; không tốn model, đọc rõ hơn nhiều ở cỡ game.
