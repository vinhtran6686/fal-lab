# Quy trình lưới nhiều nhân vật trong một clip: bước làm và thông số kỹ thuật

Mục tiêu: một ảnh lưới 10 nhân vật → mỗi động tác chỉ MỘT clip → tách ra 10 bộ khung. Đã chạy thật ngày 2026-11-26 (lưới 10 quái, động tác chết và tấn công). Mọi con số dưới đây là số đã đo; lần sau dùng lại đúng các số này để kết quả nhất quán.

## Tóm tắt một dòng mỗi bước
| Bước | Việc | Công cụ | Vào → ra | Tiền |
|---|---|---|---|---|
| 1 | Vẽ lưới, mỗi con nằm giữa ô của nó | `gen_image.py` | prompt → PNG 2560×1440 | ~$0,019 |
| 2 | Đặt lại ô: thu nhỏ, đặt giữa ô, chừa khoảng trống | `lineup_regrid.py` | PNG → PNG 2560×1440 | 0 |
| 3 | Một clip cho mỗi động tác | `fal_video.py` | PNG + prompt → mp4 | $0,12 / clip |
| 4 | Tách khung từng con, xóa nền (+ công cụ tẩy từng khung, chưa làm) | `lineup_split.py` | mp4 → 10 thư mục khung | 0 |
| 5 | Chọn khung, xuất bản cuối | xem ảnh kiểm; `video_to_sheet.py` | khung → sheet | 0 |

## Bước 1. Vẽ lưới (nhân vật nằm giữa từng ô)
- **Ảnh:** gpt-image-2, `--quality low`, `--size 2560x1440` (16:9, chia hết cho 16), `--png`, nền magenta #FF00FF. Thời gian vẽ đo được 22-26 giây.
- **Lưới:** 5 cột × 2 hàng, mỗi ô 512×720 px. Con 1-5 hàng trên, con 6-10 hàng dưới, trái sang phải.
- **Prompt lưới** (~7.000 ký tự, file mẫu ghi trong git ở lịch sử phiên; viết lại từ mẫu dưới đây):
  - mở đầu: "TEN different enemy sprites in a strict grid of 5 columns by 2 rows, each in its own invisible cell";
  - mọi con SIDE VIEW quay sang PHẢI, đứng thẳng (UPRIGHT), hai chân trên một đường đất, `TWO ARMS`, `TWO LEGS`, mặt ít nét;
  - mỗi con: tên, thân (brawny / agile / slender), vũ khí cầm thấp bên trái ảnh, **bảng màu hex riêng** (bóng, nền, sáng, điểm sáng nhất); vũ khí dài cầm chéo, không dựng đứng;
  - quy cách ô: "con ở giữa ô, chừa khoảng trống hai bên và phía trên, không vũ khí nào chạm ô bên cạnh";
  - đuôi prompt: câu nền magenta, câu style chunky của `style-chunky.md` §7;
  - chạy `python scripts/prompt_lint.py <prompt> --body brawny`: không được có ERROR (đừng viết "magenta" ngoài câu nền).
- **Giới hạn đã đo:** model bỏ qua phần trăm trong prompt. Xin chiều cao 55% / 36% / 24% ô đều cho ra 50-70% ô (gấp ~2 lần số xin ở mức 24%). Vì vậy việc "nằm giữa ô và có khoảng trống" được bảo đảm ở bước 2 bằng code, không bằng prompt. Style cũng drift khỏi chunky (nhiều chi tiết, bóng mềm hơn).

## Bước 2. Đặt lại ô (thu nhỏ, giữ độ nét)
`python scripts/lineup/lineup_regrid.py lineup_vNN.png --out lineup_vNN_regrid.png --scale 0.68 --feet 0.70`

| Thông số | Giá trị | Vì sao |
|---|---|---|
| Kích thước ảnh ra | 2560×1440 (giữ nguyên) | cùng tỉ lệ 16:9 để clip giữ khung hình |
| Ô | 512×720 | 2560 / 5, 1440 / 2 |
| Thu nhỏ `--scale` | 0,68 | nhỏ hơn thì clip 768P không còn đủ điểm ảnh (xem bảng cỡ), lớn hơn thì các con dính nhau |
| Đường chân `--feet` | 0,70 × cao ô = 504 px từ đỉnh ô | chừa ~30% chiều cao ô phía trên đầu cho vũ khí giơ lên |
| Tâm ngang | giữa ô (256 px) | mỗi con cách mép ô 26-30% |
| Kết quả | mỗi con cao 31-41% ô (223-295 px), rộng 40-49% ô (205-250 px), vũ khí tính vào | đo trên lưới v03 |

- **Giữ nhân vật gốc:** script chỉ cắt, thu nhỏ bằng LANCZOS và dán lại; không vẽ lại gì. Màu, nét và thiết kế của từng con giữ nguyên.
- **Độ nét:** cỡ sprite đích là `{H}` = 60 px @1x (120 px @2x). Qua chuỗi dưới đây mỗi con còn ~120-157 px cao ở clip 768P, tức xấp xỉ gốc @2x, không phải phóng lớn nên không nhòe. Xuống `--scale` ~0,5 thì chỉ còn ~95 px, phải phóng lên cho @2x và sẽ mềm.
- **Viền:** kiểm bằng cách phóng to: sạch, không viền hồng.

## Bước 3. Clip cho mỗi động tác
`python scripts/fal_video.py video --model h3-max-turbo --prompt-file <prompt> --reference lineup_vNN_regrid.png --duration 4 --resolution 720p --out-dir <thư mục>` (hỏi "yes" kèm số tiền trước khi chạy).

| Thông số | Giá trị đã đo |
|---|---|
| Model / endpoint | `minimax/h3-max-turbo/image-to-video` |
| Độ phân giải | `720p` trong CLI = 768P. Clip ra **1344×768** (không phải 1280×720), 24 fps |
| Thời lượng | xin 4 giây, ra 4,458 giây = **107 khung** |
| Khung đầu | ảnh lưới đã đặt lại ô. Tấn công và chết: KHÔNG gửi khung cuối (giữ tư thế cuối). Đi bộ: gửi `--last-frame` trùng ảnh đầu để lặp vòng |
| Giá | 768P $0,03/giây → **$0,12** cho 4 giây. 1080P: $0,06/giây → 5 giây $0,30 (clip ra 1920×1080, 124 khung) |
| Thời gian chờ | 768P 4 giây: ~4 giây; 1080P 5 giây: 7-13 giây |
| Ô sau khi cắt (768P) | 1344 / 5 × 768 / 2 = **268×384** (1080P: 384×540) |
| Cỡ mỗi con trong clip 768P | ô 384 / 720 = 0,533 so với ảnh lưới → cao ~119-157 px, rộng ~110-133 px |

**Prompt chuyển động** (theo `fal-image/action-planes.md` §9; liệt kê trong chat để duyệt trước khi chạy):
1. Hệ quy chiếu: "Left and right are the screen's"; hướng tiến = sang phải màn hình; mục tiêu ngoài khung bên phải.
2. Mỗi con **đứng tại chỗ**: "stays inside its own cell, feet never slide, never moves into another character's space". Chết: "ngã tại chỗ, không văng, không trượt".
3. Một chuỗi động tác liên tục, bắt đầu từ hông; **gắn tên vũ khí cho từng con** (mace với Knight, ...); con tay không (Wolfman, Golem) đứng riêng một câu.
4. Kết thúc và giữ tư thế cuối, không quay lại, không đòn thứ hai.
5. Giữ thiết kế, "no tail"; nền magenta cố định, không hiệu ứng, không chữ, camera cố định.

## Bước 4. Tách khung từng con
`python scripts/lineup/lineup_split.py clip.mp4 --out <thư mục> --pad 64 --names rust_knight,dune_raider,ash_wolfman,quarry_ogre,moss_troll,bog_hag,drowned_marauder,bone_reaver,gloom_monk,scrap_golem`

| Thông số | Giá trị |
|---|---|
| Lưới cắt | 5 cột × 2 hàng, cắt cố định (rộng clip / 5, cao clip / 2) |
| Nới ô `--pad` | 64 px mỗi phía ở 768P (ô 268×384 → cửa sổ **396×512**). Ở 1080P dùng 96 (576×732) |
| Số khung `--frames` | 13 khung mỗi con, lấy đều trên cả clip (cách nhau ~8,8 khung = 0,37 giây ở 24 fps). Muốn dày hơn: `--step 3` (≈ 36 khung, 8 khung/giây) |
| Phát xem trước | `--fps 12` (13 khung ≈ 1,1 giây) |
| Neo | chân (đáy hình bóng khung đầu) tại y = 64 + 0,88 × 384 = **402 px**, tâm ngang tại x = 198 px của cửa sổ; một phép dịch cố định cho cả bộ khung, không căn lại từng khung |
| Xóa nền | điểm magenta = min(R,B) − G; viền mềm, khử hồng ở rìa |
| Bỏ mảnh lạ | giữ mảnh lớn nhất qua cột giữa cửa sổ + mảnh cách nó ≤ `--gap` 14 px |
| Ra | `<tên>/frames/f01..f13.png` (RGBA 396×512), `sheet.png` (5148×512), `preview.gif` |

**Công cụ tẩy từng khung (CHƯA làm, ghi để làm sau):** khi vũ khí hoặc thân của con bên cạnh đã dính liền vào con chính (khung giơ lên của clip tấn công: Wolfman cầm búa, Monk cầm rìu), script tự động không tách được. Tool cần: một trang xem tất cả khung của 10 con trên một màn hình, bấm chọn vùng hoặc mảnh liên thông để xóa trên từng khung, bỏ cả khung, lưu lại. Một trang như vậy cũng giúp tiết kiệm token vì không phải đọc nhiều ảnh lớn.

## Bước 5. Bản cuối
1. Mở ảnh kiểm (6-8 khung mỗi con, thu nhỏ 1/3); bỏ khung sai vũ khí, dính hàng xóm hoặc viền hồng, và khung cuối của clip tấn công (nó quay về dáng đứng).
2. Con nào giữ: nhập vào asset thật (`scripts/ingest_image.py`, `brief.md` có manifest), rồi `scripts/video_to_sheet.py` đưa khung vào canvas chuẩn của class (enemy tier M: 136×120 @1x, `{H}` 60 px). Rồi `video_prune.py`, `motion_check.py`.
3. Dọn bằng `scripts/source_prune.py`; không để bản thử trong repo; chi phí chỉ ghi ở `out/costs.csv`.

## Tổng chi phí và thời gian một lưới
| Hạng mục | Tiền | Thời gian đo |
|---|---|---|
| Lưới (1 ảnh) | $0,019 | 22-26 giây |
| Đặt lại ô | 0 | vài giây |
| Mỗi động tác (clip 768P 4 giây) | $0,12 | ~4 giây chờ fal |
| Tách khung | 0 | vài giây mỗi clip |
Ví dụ 10 con × 2 động tác: $0,019 + 2 × $0,12 ≈ **$0,26**, khoảng $0,013 mỗi con mỗi động tác (làm từng con riêng: ~$0,12 mỗi con mỗi động tác).

## Kết quả đã đo và việc còn lại
- **Chết:** sạch, 10/10 không dính nhau (lưới đã đặt lại ô, h3-max-turbo 768P 4 giây).
- **Tấn công:** đòn chém và tư thế giữ sạch; nhịp giơ lên (khung 3-5) có vũ khí lạ (Wolfman cầm búa, Monk cầm rìu). Cần công cụ tẩy từng khung hoặc chạy lại.
- **Đi bộ:** chưa chạy với lưới đã đặt lại ô. Clip đi bộ trên lưới khít (ô 1080P) đã trôi khỏi ô và không dùng được.
