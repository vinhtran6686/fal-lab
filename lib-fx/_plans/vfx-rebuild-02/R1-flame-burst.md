# R1. Dựng lại flame-burst bằng bộ vector

File được tạo / sửa: `lib-fx/_core/formulas/vector/profiles/flame-burst.json`, `lib-fx/_core/results/vector-showcase/flame-burst/` (do lệnh `showcase` sinh),
một dòng trong `lib-fx/_core/results/vector-showcase/README.md`.

## Các bước (làm đúng thứ tự)
1. `python lib-fx/_tools/vectorfx.py init ref/vfx/flame-burst/dmitry-sarkisov-flame-burst.gif flame-burst`
   Mở `lib-fx/_core/formulas/vector/profiles/flame-burst.json`, sửa cho đúng các giá trị sau (ghi đè cái `init` đoán):
   - `source.gif` = đường dẫn GIF trên; một biến thể tên `jet`;
   - `source.crops.jet` = `[60, 250, 760, 500]` (x0, y0, x1, y1 px gốc). **Kiểm**: vùng cắt không chứa chữ tiêu đề (chữ nằm trên y = 120) và chứa
     toàn bộ khói ở khung 58 và 65. Nếu khói bị cắt, hạ `y0` từng 20 px (không thấp hơn 130);
   - `source.scale` = 2; `source.frames` = `[0, 80]`; `source.background_frame` = 0 (khung 0 chỉ có hộp và nền: hộp và bóng đất thuộc về nền);
   - `frame` = `{"type": "linear", "angle": 0}` (hiệu ứng phụt ngang sang phải; gốc ở miệng hộp);
   - `background` = màu nền lấy ở điểm (700, 300) của khung 0.
2. `python lib-fx/_tools/vectorfx.py ingest flame-burst` rồi `python lib-fx/_tools/vectorfx.py palette flame-burst --variant jet --frame 33`
   (khung 33 ≈ đỉnh). Mở ảnh mặt nạ từng màu. Viết 3 lớp, thứ tự dưới → trên `["smoke", "orange", "yellow"]`:
   - `smoke`: `{"darker_than_bg": true}` (khối nâu đen trong mờ; xem cách khai báo lớp bóng tối của biến thể `toxic` trong `profiles/element-trio.json` và chép đúng khoá);
   - `orange`: `colours` = 2-4 màu cam đậm nhất mà `palette` liệt kê ở vùng lửa, `tol` 22;
   - `yellow`: `colours` = 2-3 màu vàng sáng nhất, `tol` 26;
   - `halo_model` = `"blur"`.
   **Kiểm**: `python lib-fx/_tools/vectorfx.py check flame-burst` không báo `MISSING LAYER`. Nếu báo, thêm màu được báo vào lớp gần màu nhất (cam hay vàng) rồi chạy lại.
3. Xem mặt nạ bằng mắt ở 4 khung: 12 (báo trước), 33 (đỉnh), 44 (lửa rút), 60 (chỉ khói). **Kiểm**: hộp đen bên trái **không** nằm trong lớp `smoke`
   (nếu có: kiểm lại `background_frame`; nếu vẫn còn, thu `x0` của crop vào tới mép phải của hộp + 2 px và ghi lại).
4. `python lib-fx/_tools/vectorfx.py measure flame-burst` → `python lib-fx/_tools/vectorfx.py lifecycle flame-burst`.
5. `python lib-fx/_tools/vectorfx.py all flame-burst` (khớp nét: ~1 phút mỗi khung, khoảng 80 phút; chạy nền, không chạy song song lệnh khác trên cùng profile).
6. `python lib-fx/_tools/vectorfx.py showcase flame-burst`; thêm một dòng vào bảng trong `lib-fx/_core/results/vector-showcase/README.md` (cột "Điểm user": "chờ chấm").
7. Mở `lib-fx/_core/results/vector-showcase/flame-burst/jet/compare.gif` và 4 khung `frames/12, 33, 44, 60`; đọc `lib-fx/_study/flame-burst/vector/report.json`.

## Ngưỡng tự kiểm trước khi báo xong
- IoU trung bình mỗi lớp ở các khung 28-70 ≥ 0.85 (`report.json`). Lớp nào dưới ngưỡng: chạy lại `rebuild flame-burst --refit --frames <các khung kém>` **một lần**;
  vẫn kém thì ghi vào "Kết quả", không tự sửa code.
- `kinks` = 0 ở mọi khung (cột fairness trong `report.json`).
- Trong `compare.gif`: đủ 4 pha (báo trước, bùng, lửa rút, khói rách), quầng cam chỉ có khi còn lửa, khói không có quầng.
- Móc cuộn ở đầu khói còn là móc (không bị làm tròn mất): so khung 51 và 58 với bản gốc.

## Báo cáo (điền dưới đây)
Đường dẫn `compare.gif`; bảng IoU từng lớp (trung bình, thấp nhất, khung thấp nhất); crop cuối cùng; màu từng lớp; thời gian chạy; 3 chỗ chưa giống nhất.

## Kết quả

**compare.gif**: `lib-fx/_core/results/vector-showcase/flame-burst/jet/compare.gif` (640x320, 77 khung; cạnh trái bản gốc, phải bản dựng). Profile: `lib-fx/_core/formulas/vector/profiles/flame-burst.json`. Khung dựng 2-75 (profile ghi `frames` 0-80, 74 khung có nội dung).

**Crop cuối cùng**: `[60, 210, 760, 420]` (khác task: `[60, 250, 760, 500]`). Lý do: khói chạm mép trên ở khung 44-65 (đỉnh khói y = 238 px gốc) nên hạ `y0` xuống 210; bóng đất dưới hộp (y ~ 425-435) rơi vào lớp `smoke` (khác nền > 8 mức sáng) nên cắt `y1` = 420 (khói thấp nhất ~ 410). `scale` 2, `background_frame` 0, `frame` linear góc 0, `background` [49,52,56].

**Màu từng lớp** (dưới -> trên):
- `smoke`: [36,30,36] [34,34,36] [44,36,40] [70,34,26], `tol` 12, `darker_than_bg` 8. Màu gợi ý trong task ([80,34,25], [66,31,26]) là màu viền nâu, không phải thân khói (thân khói xám đen ~ (34,32,36)), nên dùng màu đo từ phần tối hơn nền. `darker_than_bg` 14 làm khói lủng lỗ ở vùng nền tối nên giữ 8.
- `orange`: [252,169,66] [254,158,60] [228,132,48] [252,192,84], `tol` 22.
- `yellow`: [253,242,113] [252,239,111] [252,224,100], `tol` 26.
- `halo_model` blur (giá trị đo bởi `measure`).

**IoU (report.json, khung 28-70)**:
| Lớp | Trung bình | Thấp nhất | Khung thấp nhất | Khung < 0.85 |
|---|---|---|---|---|
| smoke | 0.918 | 0.671 | 69 | 66-70 (mảnh khói tan, rất nhỏ) |
| orange | 0.776 | 0.565 | 50 | 40-55 (chỉ còn vài đốm lửa nhỏ) |
| yellow | 0.859 | 0.536 | 52 | 42, 43, 48-50, 52, 53 |
`kinks` = 0 ở mọi khung. Đạt ngưỡng: smoke, yellow, kinks. **Không đạt: orange (0.776 < 0.85)**. Đã chạy `rebuild --refit --frames 40-55` một lần: số không đổi (khớp nét tất định); theo luật không tự sửa code, ghi nhận ở đây. Lớp cam kém vì ở khung 40-55 diện tích cam chỉ vài trăm px (cả khung 44 chỉ ~800 px cam), mỗi đốm nhỏ lệch vài px là IoU tụt.

**Thời gian chạy**: `measure` 4 phút 56 giây, `all` (rebuild + review) ~24 phút (không phải 80 phút), refit khung 40-55 thêm 7 phút 18 giây. Lifecycle: sinh khung 2, đỉnh khung 38, vỡ khung 64, hết khung 68, tối đa 122 mảnh.

**Chỗ chưa giống nhất** (xem compare.gif, khung 33, 44, 51, 58):
1. Khói trong bản dựng là một màu phẳng tím đen, mất gradient và viền nâu đỏ ở mép khói của bản gốc (khung 33-44); lỗ tối giữa khói ở khung 33 (dưới) bị dựng thành mảng đen đậm khác bản gốc.
2. Quầng cam (halo) vẫn còn quanh khói ở khung ~44 khi lửa gần tắt (bản gốc có quầng nhạt do lửa nhỏ), tức "khói không có quầng, quầng chỉ có khi còn lửa" chưa đạt hoàn toàn; hộp bị nghiêng ở khung 33 để lại một mảnh xanh nhỏ lọt vào mặt nạ `smoke` bên trái.
3. Móc cuộn ở đầu khói (khung 51, 58) còn giữ hình móc nhưng đầu nhọn bị bo tròn, mảnh khói nhỏ cuối (khung 66-70) bị mất hay đơn giản hoá (smoke IoU thấp); đốm lửa nhỏ ở khung 40-55 lệch vị trí/hình so với gốc.
Pha: đủ 4 pha (báo trước khung ~12, bùng ~33, lửa rút ~44, khói rách ~58) hiện ra trong bản dựng.
