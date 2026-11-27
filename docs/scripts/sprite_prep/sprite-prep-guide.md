# sprite_prep: từ clip động tác đến sheet sprite (tách, dọn, chọn khung, xuất)

Thư viện và lệnh dòng lệnh đứng sau trang Frame Tuner (`tools/frame_tuner/`, cách dùng trang: `docs/tools/frame_tuner/frame-tuner-guide.md`). Trang và lệnh dùng chung code và chung file. Không gọi model, không tốn tiền.

## Lệnh
```
python scripts/sprite_prep/prep.py list                                     workspace và bảng trạng thái
python scripts/sprite_prep/prep.py split <ws> [clip ...] [--hero H]         tách mọi khung của clip (cache .work/)
python scripts/sprite_prep/prep.py flags <ws> <clip> <hero>                 khung nghi ngờ
python scripts/sprite_prep/prep.py fit <ws> <hero>                          canvas mà mọi động tác đã chọn khung cần
python scripts/sprite_prep/prep.py export <ws> <hero> [action ...] [--asset DIR]   xuất sheet (DIR: xuất thử vào chỗ khác)
```
`<ws>` là thư mục workspace, ví dụ `out/heroes/_lineups/heroic_ref_five`.

## File trong workspace
| File | Vào git | Nội dung |
|---|---|---|
| `sprite_prep.json` | có | lưới (`cols`, `rows`, `x_margin`, `pad`, `gap`), hero (asset, tier, `cell` @1x, `body_2x`, `shadow`), clip (đường dẫn, hero có trong clip), động tác của từng hero (`sheet`, `takes`, `pick`, `loop`) |
| `prep/<hero>/<clip>.edits.json` | có | dọn khung không phá ảnh: `denoise` (mảnh lẻ, viền hồng, vệt chém) + `ops` theo **số khung gốc** của clip (24 fps): `brush`, `lasso`, `piece` (erase / keep / restore) |
| `prep/<hero>/<action>.seq.json` | có | chuỗi khung: các đoạn (clip, khung gốc giữ, ms mỗi khung, dx, dy), khung va chạm, lặp vòng |
| `.work/prep/<clip>/<hero>/raw/fNNN.png` | không | mọi khung đã cắt, xóa nền, neo chân; `info.json` (cửa sổ, neo, vùng cắt, chiều cao thân) |
| `.work/prep/<clip>/<hero>/edited/` | không | ảnh đã áp thao tác (cache theo mã của thao tác) |
Workspace một asset (`out/<class>/<id>/` có clip trong `source/video/`) không cần `sprite_prep.json`: cấu hình tự dựng từ tên clip (lưới 1 × 1; động tác = tên clip bỏ `_tNN`, sheet = phần tới `_side`), lưu ra file khi đổi thiết lập trên trang; sửa tên sheet trong file đó nếu cần.

## Các bước và quy tắc
1. **Tách** (`split.py`): cắt ô cố định như `scripts/lineup/lineup_split.py` (dùng lại hàm xóa nền và giữ thân chính của nó), nhưng giữ **mọi** khung và neo theo **bàn chân** (8% dưới cùng của hình khung 0), không theo tâm cả hình, nên vũ khí dài không kéo lệch tâm. Mọi clip của lưới bắt đầu từ cùng ảnh lưới nên mỗi hero có cùng phép dịch ở mọi take: ghép đoạn từ hai take gần như không lệch. Đổi thông số lưới thì tách lại (thao tác cũ sẽ trỏ sai điểm ảnh; trang báo khi gặp).
2. **Dọn** (`edits.py`): ảnh gốc → khử nhiễu → các thao tác theo thứ tự. "Khôi phục" lấy lại điểm ảnh của ảnh gốc đã khử nhiễu. Một cách làm duy nhất (Python), trang chỉ gửi thao tác.
3. **Cờ** (`analyze.py`): chạm mép, hồng (nhiều hơn khung 0 ít nhất max(40, số của khung 0) điểm), diện tích > 1,35 × trung vị (vệt chém, hiệu ứng), nhiều mảnh ≥ 30 px. Vòng lặp: chấm chỗ nối cuối → đầu so với bước thường, gợi ý điểm cắt.
4. **Xuất** (`export.py`): mỗi hero MỘT hệ số thu phóng `body_2x / body_px` (chiều cao đứng trong clip, đo ở khung 0) cho mọi động tác, vì `video_to_sheet.py` không tự đưa về chiều cao đích. Rồi dựng một set tạm và gọi `video_to_sheet.py --cell <cell>` (thêm `--no-shadow` khi `shadow` tắt). Lần xuất đầu của asset chốt canvas và diện tích thân: `fit()` đo trước mọi động tác; `export_order()` xuất động tác một lần (attack trước) rồi mới tới vòng lặp. `meta.json` của asset ghi `prep` (workspace, động tác, chuỗi, clip, hệ số).

## Đã kiểm
- Tách `attack_t01` (5 hero × 107 khung): ~40 s; `skill3_knight_ash_t03` (2 hero): ~14 s.
- Xuất `cinder_maul` attack vào một bản sao asset: canvas 220 × 196, thân 168 px @2x, chân đúng chỗ, bóng có.
- Trang (Playwright): tạo chuỗi, xóa mảnh, cọ xóa, tải lại vẫn còn thao tác, xem, xuất vào thư mục thử; không lỗi console.
- Trang cũ của holy_commander qua server mới: `apply_recipe.py attack` ra đúng từng điểm ảnh (18/18 khung @2x và @1x) so với bản trong repo.
