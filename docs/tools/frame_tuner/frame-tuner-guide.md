# Frame Tuner: chuẩn bị sprite (tách khung, dọn, chọn khung, xem, xuất)

Tool cục bộ để biến clip động tác (một lưới nhiều nhân vật hoặc clip của một asset) thành sheet sprite sạch trong `out/<class>/<id>/frames/<sheet>/`. Chỉ lo phần sprite; hiệu ứng (fx) ghép ở tool khác. Không gọi model, không tốn tiền. Mọi bước chạy bằng `scripts/sprite_prep/` (doc: `docs/scripts/sprite_prep/sprite-prep-guide.md`), nên làm trên trang hay bằng lệnh đều cho ra cùng file.

## Mở tool
Double-click `tools/frame_tuner/frame_tuner.bat`. File `.bat`:
1. tìm Python 3.10+ (bỏ qua bản stub của Microsoft Store nếu có bản cài thật);
2. kiểm tra numpy, scipy, Pillow (thiếu thì hỏi để `pip install -r requirements.txt`);
3. kiểm tra ffmpeg (thiếu thì báo, tool vẫn mở nhưng không tách được clip mới: `winget install Gyan.FFmpeg`);
4. chạy `serve.py` (chỉ nghe 127.0.0.1:8767) và mở trình duyệt khi server đã trả lời. Đã chạy rồi thì chỉ mở trình duyệt.
Đóng cửa sổ đen để tắt tool.

## Workspace
Chọn ở góc trên: một **lưới** (`out/<class>/_lineups/<tên>/sprite_prep.json`: lưới cột × hàng, các hero, các clip, mỗi hero × động tác có tên sheet, các take và take đang chọn) hoặc một **asset** có clip trong `source/video/` (lưới 1 × 1, cấu hình tự dựng từ tên clip).

## Bảng trạng thái (bên trái)
Mỗi hàng một hero, mỗi cột một động tác: `–` chưa tách, `tách` đã tách, `dọn` đã dọn khung, `N kh` đã chọn N khung, `xuất` đã xuất. Bấm một ô để làm động tác đó. **Tách tất cả clip** xếp mọi clip chưa tách vào hàng đợi (chạy ngầm, ~40 s mỗi clip lưới 5 con, tiến độ ở góc trên phải).

## 1 · Take
Mọi take của động tác chạy cạnh nhau cùng nhịp 24 fps để so sánh. **Tách clip này** cho take chưa tách. **Chọn take này** ghi take đó cho động tác (và tạo chuỗi khung mặc định: 1 trong 2 khung, 83 ms, nếu chưa có).

## 2 · Dọn khung
Dải hình = mọi khung gốc của take (24 fps). Chấm màu = cờ tự động: đỏ chạm mép, hồng còn màu hồng, vàng diện tích vọt (thường là vệt chém, hiệu ứng, vũ khí hàng xóm), xanh nhiều mảnh rời. **N** nhảy tới khung nghi ngờ tiếp theo.
- Công cụ: **B** cọ xóa, **L** vòng chọn xóa, **E** bấm xóa một mảnh, **G** chỉ giữ mảnh được bấm, **R** cọ khôi phục (trả lại điểm ảnh gốc), **[ ]** cỡ cọ, **O** onion skin (khung trước và sau mờ), **Ctrl+Z / Ctrl+Y**.
- **Chép thao tác sang N khung sau**: vệt thừa ở cùng chỗ trong vài khung liền nhau.
- **Khử nhiễu** (cho cả clip của hero): bỏ mảnh lẻ nhỏ hơn N px, khử viền hồng còn sót, xóa vệt chém tím nhạt. Áp cho clip này, mọi clip của hero hoặc cả workspace.
- Không sửa ảnh gốc: thao tác lưu vào `prep/<hero>/<clip>.edits.json` (theo số khung gốc), ảnh gốc đã tách nằm trong `.work/` và dựng lại được từ clip.

## 3 · Chọn khung
Bấm hình để giữ / bỏ (Shift+bấm: cả khoảng; **K** với khung đang chọn), ô số dưới khung giữ = thời gian (ms), **H** = khung va chạm. Nút nhanh: giữ 1 trong N trong khoảng, chỉ giữ / bỏ một khoảng, thời gian đều (ms hoặc 8, 10, 12, 15 fps).
- **Ghép nhiều take**: *Thêm đoạn từ take* thêm một đoạn từ take khác, chạy tiếp đoạn trước; *Xem chỗ nối* chồng khung cuối đoạn trước lên khung đầu đoạn sau, chỉnh **dx, dy** cho khớp.
- **Lặp vòng** (run, idle): *Kiểm tra vòng lặp* chấm chỗ nối cuối → đầu và gợi ý điểm cắt cho vòng mượt.
- Lưu vào `prep/<hero>/<động tác>.seq.json`.

## 4 · Xem
Chạy chuỗi đã chọn theo đúng thời gian: cỡ nguồn, cỡ game @2x và @1x (phóng ×3), thân 60 px; nền ca-rô, tối, sáng, cỏ, magenta; lật trái phải; onion skin; tốc độ. Khung va chạm có viền vàng.

## 5 · Xuất
- Thiết lập hero: canvas @1x (theo tier, L = 220 × 196), chiều cao thân @2x (L = 168), bóng dưới chân (hero bay như `pale_seraph`: tắt, bóng là decal riêng).
- **Canvas và cỡ thân**: đo mọi động tác đã chọn khung. Lần xuất đầu tiên của một asset chốt canvas và cỡ thân cho mọi động tác (`video_to_sheet.py`), nên tool đo trước và gợi ý canvas đủ lớn; cỡ thân khung đầu của các động tác phải lệch nhau ≤ 4%.
- **Xuất**: thứ tự an toàn (động tác một lần trước, `attack` đầu tiên, vòng lặp sau). Đổi *Thư mục asset đích* sang thư mục khác để xuất thử. Kết quả: `frames/<sheet>/` (@2x, @1x, sheet, preview), `meta.json` ghi động tác lấy từ workspace và chuỗi nào.

## Không có trong tool (cố ý)
Ghép fx và điểm va chạm cho fx (tool fx riêng); nội suy khung mới.

## Trang cũ (holy_commander)
Trang tuner đầu tiên vẫn dùng được: nút **Trang cũ** (dữ liệu dựng khi cần). Nội dung dưới đây là của trang đó.

Tool để bật/tắt từng frame, chỉnh thời gian mỗi frame và đặt hình va chạm cho animation của hero, xem bản gốc cạnh bản sửa, rồi lưu
"công thức" và áp dụng vào export. Không gọi model, không tốn phí. Thay cho `decimate` rải rác (công cụ `kr_compare` cũ đã gỡ)
(issue resolved: 15 fps recipes export byte-identical).

### Hai cách dùng

| | Cục bộ (`frame_tuner.bat`) | Artifact (máy khác, không cần repo) |
|---|---|---|
| Chạy | double-click `tools/frame_tuner/frame_tuner.bat`, bấm **Trang cũ** (lần đầu dựng dữ liệu ~80 s) | mở link artifact |
| Lưu công thức | thẳng vào `out/heroes/holy_commander/frames/export_recipe.json` | trong db của trang (Claude đọc lại được), kèm nút Tải JSON / Sao chép JSON |
| Cần | python (numpy, Pillow) và ffmpeg trên PATH, như các tool video khác | trình duyệt |

Nút **Trang cũ** gọi `build_states.py` (dựng sheet frame từ clip trong `source/video/`, lần đầu ~80 s, sau đó bỏ qua state đã dựng) rồi mở `/legacy.html`.
Mở thẳng file bằng `file://` sẽ không chạy (trình duyệt chặn tải dữ liệu).

### Trong tool
- **Click hình** bật/tắt (Shift+click: cả đoạn). Viền xanh = giữ, mờ = bỏ.
- **Ô số dưới hình** = thời gian (ms) của hình đó. Giữ lâu hơn = chậm lại ở hình đó (pipeline lặp frame để ra fps đều).
- **"H"** = hình va chạm (state có hit, như attack).
- Nút nhanh: Giữ tất cả, Về bản đã chốt, Giữ 1 trong N, Cắt đoạn, Thời gian đều (ms hoặc fps).
- **Hiện fx**: state có fx Python (levelup v03, slash) có công tắc "Hiện fx": hiệu ứng được vẽ sẵn lên **từng frame nguồn** của clip, nên bỏ hoặc giữ frame thì fx theo đúng frame đó. Tắt để xem thân sạch.
- Bên trái là bản gốc (đủ frame, 15 fps), bên phải là bản sửa; dưới mỗi bên có số hình, thời lượng và hệ số nhanh hơn.
- Phím: Space chạy/dừng, ← → đi từng hình.

### Nguồn frame 15 hoặc 24 fps
Clip render ở 24 fps. Mỗi state có công tắc **"Nguồn frame"** (15 hoặc 24 fps): 24 fps cho khoảng 1,6 lần số hình để chọn. Đổi nguồn thì lựa chọn được chuyển theo thời gian (hình i ở nguồn cũ thành round(i x mới / cũ)).
Công thức lưu `fps` của nguồn đã chọn; `apply_recipe.py` và `export_fx.py` đọc `fps` đó (fx đếm nhịp theo 15 fps nên được nhân 15/fps). Công thức cũ (15 fps) không đổi.
`build_states.py` dựng thêm `data/<id>_24.png` (và `<id>_fx_24.jpg`); lần dựng đầu mất vài phút vì `key_out` chạy nhiều frame hơn.

### Công thức (`export_recipe.json`)
```json
{"version": 1, "hero": "holy_commander", "states": {
  "attack": {"clip": "source/video/attack_side_attack_t04.mp4", "fps": 15, "loop": false,
             "keep": [0, 2, 4], "durationsMs": [67, 67, 67], "hit": 9, "savedAt": "..."}}}
```
`keep` = chỉ số các frame của clip (ở nguồn `fps` của công thức, 15 hoặc 24) được giữ, `durationsMs` = một số cho mỗi frame giữ, `hit` = **chỉ số trong danh sách giữ** (0-based) hoặc null.
`video_to_sheet.py` đọc hit là hình thứ `hit + 1` (đếm từ 1), nên attack đã chốt có `hit_frame` 10 trong `meta.json`.

### Áp dụng vào export
```
python tools/frame_tuner/apply_recipe.py                 # dry run: in kế hoạch cho mọi state đã lưu
python tools/frame_tuner/apply_recipe.py attack --write  # export attack theo công thức đã lưu
python tools/frame_tuner/apply_recipe.py --default death --write   # export theo bản đã chốt (không cần công thức)
```
Đường đi: clip trong `source/video/` -> `ffmpeg fps=15` -> `key_out` -> thang `120 / 268` cho attack, death, charge (cỡ thân master trong clip cũ) hoặc
`120 / chiều cao thân hình 0` cho clip mới -> chân hình 0 tại (256, 400) trên canvas 512x512 -> set tạm -> `video_to_sheet.py` (một canvas 176x140, một cỡ thân).
Mặc định `--write` ghi đè sheet của state trong `out/heroes/holy_commander/`; thử trước bằng `--asset <thư mục khác>`.

**Đã kiểm:** chạy `--default` cho attack, death và charge vào một bản sao của asset cho ra frame **trùng từng pixel** (@1x và @2x) và cùng `hit_frame`, `body_rescale`
với bản đã export trong repo (23/23, 39/39, 67/67). Vậy công thức tái lập được bản user đã duyệt.

### Giới hạn
- Chỉ **giữ, bỏ, lặp (giữ lâu hơn)** các frame đã có; không tạo frame mới (nội suy cần công cụ khác).
- `apply_recipe.py` chỉ export **thân** theo công thức. Fx (levelup, slash) hiện chỉ ghép sẵn để **xem** trong tool; xuất fx thành lớp riêng cho đúng các frame đã chọn là việc tiếp theo (cần chốt cách xuất lớp trong suốt, xem lib-fx/_core/formulas/draw/recipes/RECIPE-python-fx.md mục 7).
- Game có thể chỉ chơi fps cố định: pipeline ra fps đều bằng cách lặp frame (`even_fps`), xác nhận với engine trước khi dùng thời gian lệch nhiều.
- Chưa export gì từ công thức của session này (user chưa muốn export).

### File
`sources.json` (state, clip, bản đã chốt) · `build_states.py` (dựng sheet và `data/states.json`, thư mục `data/` không vào git) · `legacy.html` (trang cũ) ·
`serve.py` (server cục bộ + API lưu) · `frame_tuner.bat` · `apply_recipe.py` · `build_artifact.py` (dựng bản đăng artifact).
Thêm state mới: thêm một dòng vào `sources.json` rồi chạy lại `build_states.py`.
