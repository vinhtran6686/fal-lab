# R2b: lightning làm lại: nét mảnh như gốc, giữ nhánh mờ, quầng đổi màu ở khung chớp

Trả về từ lần chấm R2 (2026-11-14). Đọc mục 6 của [PLAN.md](PLAN.md) trước. **Cần `lib-fx/_tools/rebuild_check.py` của R1b bước 1** (làm R1b bước 1 trước, hoặc tạo đúng như mô tả ở đó).

## Vấn đề (người lập kế hoạch đã nhìn ảnh và đo trên `compare.gif`, mặt nạ sáng `L > 170`)
| khung | diện tích gốc | diện tích dựng | bề rộng nét gốc | bề rộng nét dựng |
|---|---|---|---|---|
| 8 | 1180 | 3201 | 5,5 | 16,1 |
| 70 | 1293 | 4032 | 4,0 | 10,8 |
| 94 | 859 | 2682 | 2,6 | 8,2 |
| 110 | 942 | 4098 | 2,4 | 7,0 |
1. **Nét dày gấp ~3 lần gốc** (gốc là sợi tóc, bản dựng là dải mềm). "Độ phủ 0,999" trong báo cáo R2 không bắt được lỗi này: nét dày thì lúc nào cũng phủ nét mảnh.
2. **Nhánh mảnh, mờ bị mất** (khung 20, 46, 70, 110: các sợi xám xanh nhạt ở đuôi và nhánh). Báo cáo R2 đã ghi: thêm màu (150,176,140) thì mặt nạ ăn cả quầng.
3. Quầng một màu trắng xanh, sáng sát nét; gốc là quầng xám xanh lá rộng, mềm, và **ngả xanh lam ở khung chớp 69-71, 94-95**.

## Nguyên nhân trong code
- `lib-fx/_core/formulas/vector/measure.py` dòng 145-165 (`masks`): điểm ảnh được gán lớp chỉ theo **khoảng cách màu**. Quầng sát nét có màu gần màu nét (xanh lá sáng),
  nên `green` (`tol` 26) và `core` (`tol` 22) nhận luôn quầng trong → mặt nạ béo → nét dựng béo → quầng nhoè từ nét béo lại sáng hơn. Cùng lý do, nhánh mờ không thêm được màu.
  Cần thêm điều kiện **hình học**: nét là "đỉnh" sáng hơn vùng quanh nó, quầng thì không.
- `lib-fx/_core/formulas/vector/compose.py` hàm `halo` (dòng 30-46): màu quầng `h["c"]` là hằng số cho mọi khung; chỉ `gain` đổi theo khung.

## File được sửa
- `lib-fx/_core/formulas/vector/measure.py`: hàm gán lớp (dòng 140-165) thêm khoá tuỳ chọn `brighter_than_local`.
- `lib-fx/_core/formulas/vector/compose.py`: hàm `halo` thêm khoá tuỳ chọn `c_frames`.
- `lib-fx/_core/formulas/vector/profile.py`: thêm hai khoá vào chú thích schema (như `darker_than_bg`).
- `lib-fx/_core/formulas/vector/profiles/lightning.json`.
- Không khoá mới nào được đổi hành vi khi vắng mặt (profile cũ giữ nguyên từng điểm ảnh).

## Bước
1. **`brighter_than_local`** (khoá của lớp, dạng `{"win": 9, "d": 18}`, đơn vị px **gốc**): ngay sau khối `darker_than_bg`, với mỗi lớp có khoá này:
   - `k = source.scale`; `Ls` = độ sáng của ảnh thu nhỏ về cỡ gốc (`cv2.resize(..., INTER_AREA)`); `loc = ndi.median_filter(Ls, win)`;
   - `ridge = (Ls - loc) >= d`, phóng lại về cỡ đang làm (`cv2.resize(..., INTER_NEAREST)`) rồi nở 1 px gốc (`binary_dilation`, `iterations = k`) để giữ mép nét;
   - `D[i][~ridge] = 9e9`.
   Thêm một dòng vào docstring của hàm (cạnh dòng `darker_than_bg`).
2. **`c_frames`** trong `halo` (mô hình blur): `cs = h.get("c_frames", {}).get(str(frame), h["c"])` rồi dùng `cs` thay `h["c"]` trong tổng. Không có khoá → như cũ.
3. Profile `lightning.json`, biến thể `bolt`:
   - `green`: thêm màu (150,176,140); thêm `"brighter_than_local": {"win": 9, "d": 18}`; `tol` 26 giữ nguyên.
   - `core`: thêm `"brighter_than_local": {"win": 9, "d": 30}`; `tol` 22 → 18.
4. Kiểm nhanh mặt nạ: `rebuild lightning --frames 8,20,46,70,94,110`, rồi
   `python lib-fx/_tools/rebuild_check.py lightning --mode bright --frames 0-126` (chỉ đọc 6 khung trên).
   **Kiểm**: các khung đó có `area_ratio` trong 0,8-1,25 và `width_ratio` trong 0,75-1,3; mở ảnh: nhánh mờ ở khung 20, 46, 110 hiện ra, quầng không bị tô thành nét.
   Chỉnh theo thứ tự, mỗi lần một nấc, ghi lại từng lần thử: nét còn béo → `d` của `green` 18 → 24; nhánh mờ còn mất → `d` 18 → 12 hoặc `win` 9 → 13; nhiễu quầng thành chấm → `min_area` 6 → 10.
5. **Màu quầng ở khung chớp**: với mỗi khung f ∈ {69, 70, 71, 94, 95} và một khung thường n ∈ {60, 80, 100}: lấy vành quanh mặt nạ gốc (`green ∪ core`) cách 3-15 px gốc,
   `hal(f)` = trung bình (ảnh gốc − nền) trong vành. `c_frames[f] = [c × hal(f)[ch] / mean_n hal(n)[ch] cho từng màu c trong h["c"]]` (theo kênh, cắt ≥ 0).
   Viết đoạn tính ngay trong báo cáo, không thêm vào repo. Ghi vào `halo.c_frames` của profile.
6. `measure lightning` **không chạy lại ở scale 4** (quá chậm, xem R2): chạy trên bản sao scale 1 như R2 và nhân `sigma`, `gradient.s` với 4, **giữ nguyên `c_frames` vừa ghi**. Rồi `all lightning` (chạy nền), `showcase lightning`.
7. Hồi quy: `python lib-fx/_tools/vectorfx.py rebuild swirl-slash --frames 3-4` và `rebuild flame-burst --frames 33` trước và sau khi sửa code: hash khung giống nhau.

## Tiêu chí nghiệm thu
- `rebuild_check.py lightning --mode bright --frames 0-126`: trung bình `area_ratio` 0,8-1,25, trung bình `width_ratio` 0,75-1,3; khung 8, 70, 94, 110 mỗi khung trong 0,7-1,4 (cả hai cột).
- Ảnh `compare.gif`: nhánh mờ ở khung 20, 46, 110 có trong bản dựng; góc gãy còn nhọn (không thành sóng); quầng ngả xanh lam ở 69-71 và 94-95, các khung khác không.
- Số mảnh rời lệch ≤ 2 so với gốc ở ≥ 85 % số khung (`lifecycle`; R2 đạt 89,8 %, không được tụt dưới 85 %).
- Hồi quy bước 7 sạch. Nền gradient xanh của gốc **không** phải tiêu chí (hiệu ứng dùng trên nền trong suốt).

## Báo cáo (điền dưới đây)
Bảng `rebuild_check` bright (khung 8, 20, 46, 70, 94, 110 + trung bình); giá trị `win`, `d`, `tol` cuối cùng và các lần thử; `c_frames`; hash hồi quy; lệch so với task và lý do; đường dẫn `compare.gif`.

## Kết quả
