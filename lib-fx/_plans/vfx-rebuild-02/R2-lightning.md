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

- `compare.gif`: `lib-fx/_core/results/vector-showcase/lightning/bolt/compare.gif` (gốc | dựng lại, 127 khung); thêm `rebuilt.gif`, `frames/`, `svg/` cùng thư mục.
- `scale` cuối = 4 (không cần 6). Bước 6 (`masks.min_width_px`) **không làm**: không sửa `measure.py`.
- Nền: không có khoá `median` trong code; `background()` mặc định lấy phân vị 20 theo điểm ảnh qua mọi khung nhưng ở scale 4 hết bộ nhớ (bị kill), nên dùng `background_frame` = 40 (khung ít điểm sáng nhất, diện tích 156 trong `study_ref`).
- Hai lớp (dưới -> trên): `green` = (126,192,136), (139,208,143), (173,221,149), tol 26; `core` = (188,253,147), (199,255,147), tol 22. `halo_model` = blur. `check` không báo MISSING LAYER.
- `smooth` = `{"sigma":1.5,"corner_deg":160,"merge_tol":0.5,"min_area":6,"close_px":0.5}` (bước 4: bản mặc định làm tròn góc gãy).
- Lệch quy trình: `measure` ở scale 4 chạy > 1 giờ không xong (làm nhoè sigma tới 200 px trên 127 khung 1600x1300). Đã `measure` trên bản sao scale 1 (`/tmp`, 1 phút) rồi nhân sigma quầng và `gradient.s` với 4 để ghi vào profile thật. `lifecycle` chạy bình thường trên profile thật.
- Thời gian: `rebuild` toàn bộ ~50 s/khung (3 tiến trình song song ~35 phút), `all` (review) 26 phút, `showcase` vài phút.

Độ phủ (mặt nạ gốc vs bản dựng, ngưỡng 4 px ở scale 4 = 1 px gốc, 114 khung có nét):

| | trung bình | thấp nhất | khung >= 0.9 |
|---|---|---|---|
| gốc được phủ bởi bản dựng | 0.999 | 0.945 (khung 46) | 100% |
| bản dựng nằm trên nét gốc | 0.997 | 0.927 (khung 85) | 100% |

Số mảnh rời lệch <= 2 so với bản gốc: 89,8 % số khung (chưa đạt hết, không tính khung nào không khớp trống/có nét: 0 khung lệch).

Các tia (khung bắt đầu, kết thúc; đoạn liên tiếp, ngăn bởi khung trống hoặc IoU < 0.2): 100 tia, gần như toàn tia 1 khung: (0,0) ... (6,6), (7,9), (10,10)-(12,12), (13,14), (15,15)-(18,18), (20,20)-(30,30), (31,32), (33,33)-(37,37), (44,44), (46,46), (49,49), (51,51), (52,55), (56,57), (59,59)-(76,76), (77,78), (79,79)-(100,100), (101,103), (104,104)-(110,110), (111,112), (113,113)-(115,115), (116,117), (118,118), (119,120), (121,121)-(126,126). Nghĩa là H6 (2-5 khung, khung đầu sáng nhất) **không đúng** với mẫu này: đa số tia chỉ sống 1 khung, khung 37-59 gần trống.

3 chỗ chưa giống nhất:
1. Quầng: bản dựng trắng xanh, to, mờ đều; bản gốc xám xanh lá, nhỏ hơn quanh từng tia, có khung chớp ngả xanh lam (khung 69-71, 94-95) mà bản dựng **không** tái tạo (một màu quầng toàn cục, chỉ đổi cường độ). Nền gradient xanh đậm của gốc không có trong bản dựng (nền xám phẳng).
2. Nét mảnh xám nhạt ở đuôi và nhánh nhỏ (màu gần trùng quầng) bị mặt nạ bỏ sót; thử thêm màu (150,176,140) thì mặt nạ ăn cả quầng nên bỏ. Bộ khớp nét thon làm thân dày hơn hairline gốc và mép hơi răng cưa; góc gãy giữ được nhưng ít sắc hơn gốc.
3. Số mảnh rời lệch hơn 2 ở ~10 % khung (khung thân dày, tách mảnh khác nhau). Hệ thống không đo riêng IoU/chiều dày nhánh (H5) vì tách thân và nhánh cần theo dõi mảnh, không làm.

