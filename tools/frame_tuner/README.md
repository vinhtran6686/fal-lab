# Frame Tuner

Chuẩn bị sprite từ clip động tác: tách khung, dọn (tẩy, khử nhiễu), chọn khung và thời gian, xem ở cỡ game, xuất sheet vào asset. Không ghép fx.

- Mở: double-click `frame_tuner.bat` (kiểm tra Python, numpy, scipy, Pillow, ffmpeg; mở http://127.0.0.1:8767/).
- Không dùng .bat: `python tools/frame_tuner/serve.py` rồi mở http://127.0.0.1:8767/.
- Cách dùng: `docs/tools/frame_tuner/frame-tuner-guide.md`. Code các bước: `scripts/sprite_prep/` (`docs/scripts/sprite_prep/sprite-prep-guide.md`).
- Trang cũ (công thức holy_commander): nút "Trang cũ", file `legacy.html`, `sources.json`, `build_states.py`, `apply_recipe.py`.
