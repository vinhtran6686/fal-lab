# R2. Dựng lại lightning bằng bộ vector

File được tạo / sửa: `lib-fx/_core/formulas/vector/profiles/lightning.json`, `lib-fx/_core/results/vector-showcase/lightning/`, một dòng trong
`lib-fx/_core/results/vector-showcase/README.md`. Chỉ khi bước 6 yêu cầu: `lib-fx/_core/formulas/vector/measure.py` (một tham số, ghi rõ bên dưới).

Đặc điểm của mẫu: nét **rất mảnh** (1-3 px gốc) và mỗi tia chỉ sống vài khung. Bộ đo mặc định **tự loại thành phần hẹp hơn 1,5 px gốc**, nên phải phóng to.

## Các bước
1. `python lib-fx/_tools/vectorfx.py init ref/vfx/lightning/dmitry-sarkisov-lqafinal.gif lightning`, rồi sửa profile:
   - một biến thể `bolt`; `source.crops.bolt` = `[0, 0, 400, 325]` (**kiểm**: không chứa dòng chữ phía dưới, chữ bắt đầu khoảng y = 340);
   - `source.scale` = 4; `source.frames` = `[0, 126]`;
   - nền: bản gốc có gradient xanh đậm → không dùng một màu nền; đặt nền = trung vị từng điểm ảnh qua mọi khung (khoá `background_frame` không dùng được vì
     không có khung trống chắc chắn: xem trong `measure.py` / `profile.py` có khoá nền `median` không; nếu **không có**, dùng khung có ít điểm sáng nhất:
     chạy `python lib-fx/_tools/study_ref.py ref/vfx/lightning/dmitry-sarkisov-lqafinal.gif --name lightning --bg median`, đọc `report.json`, lấy khung có diện tích nhỏ nhất làm `background_frame`);
   - `frame` = `{"type": "linear", "angle": -90}` (không có hướng chung; khung thẳng là đủ).
2. `ingest`, rồi `palette lightning --variant bolt --frame N` với N = khung có diện tích lớn nhất trong `report.json` của bước 1. Viết 2 lớp, dưới → trên `["green", "core"]`:
   - `green`: các màu xanh lá sáng bão hoà của nét (2-3 màu), `tol` 26;
   - `core`: các màu trắng xanh sáng nhất ở giữa nét, `tol` 22;
   - `halo_model` = `"blur"` (quầng nhoè rộng, có khung quầng ngả xanh lam: **không** tạo lớp cho quầng).
   **Kiểm**: `check lightning` không báo `MISSING LAYER`; mặt nạ `green ∪ core` ở 3 khung bất kỳ phủ đủ mọi nét nhìn thấy bằng mắt, kể cả nhánh mảnh nhất.
   Nhánh mảnh bị mất → tăng `source.scale` lên 6 và làm lại từ `ingest`.
3. `measure lightning`, `lifecycle lightning`.
4. Chạy thử trên 12 khung trước: `python lib-fx/_tools/vectorfx.py rebuild lightning --frames 0-11`, mở `lib-fx/_study/lightning/vector/frames/`.
   **Kiểm**: nét dựng lại vẫn **gãy khúc sắc** (góc nhọn giữ nguyên, không bị làm tròn thành sóng) và mảnh như bản gốc. Nếu góc bị tròn: trong profile đặt
   `smooth` = `{"sigma": 1.5, "corner_deg": 160, "merge_tol": 0.5, "min_area": 6, "close_px": 0.5}` rồi `rebuild` lại 12 khung (không `--refit`).
5. Đạt bước 4 → `python lib-fx/_tools/vectorfx.py all lightning` (127 khung; chạy nền), rồi `showcase lightning`, thêm dòng vào README showcase.
6. Chỉ khi ở bước 2 đã phóng `scale` = 6 mà nhánh mảnh vẫn mất: trong `lib-fx/_core/formulas/vector/measure.py` tìm chỗ loại thành phần hẹp hơn 1,5 px gốc,
   đưa ngưỡng đó thành khoá profile `masks.min_width_px` (mặc định 1.5, giữ hành vi cũ), đặt 0.6 cho profile này. Chạy `python lib-fx/_tools/vectorfx.py rebuild swirl-slash --frames 3-4`
   trước và sau để chứng minh profile cũ không đổi (so hash khung).

## Ngưỡng tự kiểm
- Với nét mảnh IoU không phải thước đo tốt: báo **độ phủ**: tỉ lệ điểm của mặt nạ gốc cách nét dựng lại ≤ 1 px gốc ≥ 0.9, và ngược lại ≥ 0.9
  (tính bằng `scipy.ndimage.distance_transform_edt` trên mặt nạ hai bên, viết đoạn tính ngay trong báo cáo, không thêm vào repo).
- Số mảnh rời mỗi khung của bản dựng lệch không quá ±2 so với bản gốc (`lifecycle`).
- `compare.gif`: mỗi tia xuất hiện và biến mất đúng khung như bản gốc; quầng đổi màu ở đúng các khung chớp.

## Báo cáo (điền dưới đây)
Đường dẫn `compare.gif`; `scale` cuối cùng; màu hai lớp; bảng độ phủ (trung bình, thấp nhất); có phải làm bước 6 không; danh sách (khung bắt đầu, khung kết thúc) của từng tia
(đọc từ `lifecycle`: một tia = một đoạn khung liên tiếp có diện tích > 0, ngăn bởi khung trống hoặc bởi khung mà IoU với khung trước < 0.2); 3 chỗ chưa giống nhất.

## Kết quả
