# Frame Tuner: tự tăng giảm frame, lưu công thức, áp dụng

Tool để bật/tắt từng frame, chỉnh thời gian mỗi frame và đặt hình va chạm cho animation của hero, xem bản gốc cạnh bản sửa, rồi lưu
"công thức" và áp dụng vào export. Không gọi model, không tốn phí. Thay cho `decimate` rải rác trong `tools/kr_compare/build_manifest.py`
(issue: `docs/issue-frame-recipe-sync.md`).

## Hai cách dùng

| | Cục bộ (`frame_tuner.bat`) | Artifact (máy khác, không cần repo) |
|---|---|---|
| Chạy | double-click `tools/frame_tuner/frame_tuner.bat` | mở link artifact |
| Lưu công thức | thẳng vào `out/heroes/holy_commander/export_recipe.json` | trong db của trang (Claude đọc lại được), kèm nút Tải JSON / Sao chép JSON |
| Cần | python (numpy, Pillow) và ffmpeg trên PATH, như các tool video khác | trình duyệt |

`frame_tuner.bat` dựng sheet frame từ clip trong `raw/` (lần đầu ~80 s, sau đó bỏ qua state đã dựng), mở `http://127.0.0.1:8767/` rồi chạy `serve.py`
(chỉ nghe 127.0.0.1). Mở thẳng `index.html` bằng `file://` sẽ không chạy (trình duyệt chặn tải dữ liệu).

## Trong tool
- **Click hình** bật/tắt (Shift+click: cả đoạn). Viền xanh = giữ, mờ = bỏ.
- **Ô số dưới hình** = thời gian (ms) của hình đó. Giữ lâu hơn = chậm lại ở hình đó (pipeline lặp frame để ra fps đều).
- **"H"** = hình va chạm (state có hit, như attack).
- Nút nhanh: Giữ tất cả, Về bản đã chốt, Giữ 1 trong N, Cắt đoạn, Thời gian đều (ms hoặc fps).
- Bên trái là bản gốc (đủ frame, 15 fps), bên phải là bản sửa; dưới mỗi bên có số hình, thời lượng và hệ số nhanh hơn.
- Phím: Space chạy/dừng, ← → đi từng hình.

## Công thức (`export_recipe.json`)
```json
{"version": 1, "hero": "holy_commander", "states": {
  "attack": {"clip": "raw/attack_side_attack_t04.mp4", "fps": 15, "loop": false,
             "keep": [0, 2, 4], "durationsMs": [67, 67, 67], "hit": 9, "savedAt": "..."}}}
```
`keep` = chỉ số các frame (15 fps) của clip được giữ, `durationsMs` = một số cho mỗi frame giữ, `hit` = **chỉ số trong danh sách giữ** (0-based) hoặc null.
`video_to_sheet.py` đọc hit là hình thứ `hit + 1` (đếm từ 1), nên attack đã chốt có `hit_frame` 10 trong `meta.json`.

## Áp dụng vào export
```
python tools/frame_tuner/apply_recipe.py                 # dry run: in kế hoạch cho mọi state đã lưu
python tools/frame_tuner/apply_recipe.py attack --write  # export attack theo công thức đã lưu
python tools/frame_tuner/apply_recipe.py --default death --write   # export theo bản đã chốt (không cần công thức)
```
Đường đi: clip trong `raw/` -> `ffmpeg fps=15` -> `key_out` -> thang `120 / 268` cho attack, death, charge (cỡ thân master trong clip cũ) hoặc
`120 / chiều cao thân hình 0` cho clip mới -> chân hình 0 tại (256, 400) trên canvas 512x512 -> set tạm -> `video_to_sheet.py` (một canvas 176x140, một cỡ thân).
Mặc định `--write` ghi đè sheet của state trong `out/heroes/holy_commander/`; thử trước bằng `--asset <thư mục khác>`.

**Đã kiểm:** chạy `--default` cho attack, death và charge vào một bản sao của asset cho ra frame **trùng từng pixel** (@1x và @2x) và cùng `hit_frame`, `body_rescale`
với bản đã export trong repo (23/23, 39/39, 67/67). Vậy công thức tái lập được bản user đã duyệt.

## Giới hạn
- Chỉ **giữ, bỏ, lặp (giữ lâu hơn)** các frame đã có; không tạo frame mới (nội suy cần công cụ khác).
- Tool xem thân sạch của clip; fx Python (levelup, banner, slash) vẽ lên sau và chưa nằm trong tool này. Hình va chạm giúp đặt fx đúng nhịp.
- Game có thể chỉ chơi fps cố định: pipeline ra fps đều bằng cách lặp frame (`even_fps`), xác nhận với engine trước khi dùng thời gian lệch nhiều.
- Chưa export gì từ công thức của session này (user chưa muốn export).

## File
`sources.json` (state, clip, bản đã chốt) · `build_states.py` (dựng sheet và `data/states.json`, thư mục `data/` không vào git) · `index.html` (tool) ·
`serve.py` (server cục bộ + API lưu) · `frame_tuner.bat` · `apply_recipe.py` · `build_artifact.py` (dựng bản đăng artifact).
Thêm state mới: thêm một dòng vào `sources.json` rồi chạy lại `build_states.py`.
