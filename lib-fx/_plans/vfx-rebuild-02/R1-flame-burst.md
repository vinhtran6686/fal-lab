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
