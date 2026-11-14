# R1b: flame-burst làm lại: vỏ khói sáng, khói không có quầng, thêm bộ đo độc lập

Trả về từ lần chấm R1 (2026-11-14). Đọc mục 6 của [PLAN.md](PLAN.md) trước. Làm **trước R2b** (bước 1 tạo công cụ mà R2b dùng).

## Vấn đề (người lập kế hoạch đã nhìn ảnh và đo)
1. **Khung bùng (33-38) mất gần hết vỏ khói nâu bọc lửa**: bản dựng chỉ còn lửa trên nền xám và vài mảng đen rời. IoU phần tối giữa bản gốc và bản dựng
   (đo trên `compare.gif`, mặt nạ = khác nền > 14 và độ sáng < 110): khung 33 = **0,62**, khung 38 = **0,74**, khung 14 (báo trước) = **0,42**.
   Báo cáo R1 ghi `smoke` IoU 0,918 vì `report.json` so bản dựng với **mặt nạ của chính nó**, không so với ảnh gốc: mặt nạ thiếu thì IoU vẫn cao.
2. **Quầng cam quanh khói** khi lửa đã tắt (khung 44): quầng được nhoè từ mọi lớp, kể cả `smoke`.
3. Khói một màu phẳng, mất viền nâu đỏ.

## Nguyên nhân trong code
- `lib-fx/_core/formulas/vector/measure.py` dòng 156-161: lớp có `darker_than_bg` chỉ nhận điểm ảnh **tối hơn nền** ít nhất N mức.
  Vỏ khói sát lửa được lửa chiếu sáng, màu đo trên gốc khung 33: (83,40,29), (68,36,32), (57,39,40), mép (141,61,29). Độ sáng ~50-55 ≈ nền (~52) nên bị loại
  (`D = 9e9`) và không lớp nào nhận → thành nền. Đó là lỗ trong khói.
- `lib-fx/_core/formulas/vector/compose.py` dòng 80: quầng dùng trọng số `halo_w` của từng lớp (mặc định 1). Profile chưa đặt `halo_w` cho `smoke`.

## File được sửa
- `lib-fx/_core/formulas/vector/profiles/flame-burst.json` (chỉ biến thể `jet`).
- Tạo mới `lib-fx/_tools/rebuild_check.py` (bước 1). Thêm một dòng về nó vào `lib-fx/_core/formulas/vector/README.md` (mục công cụ) và `docs/README.md` nếu bảng đó liệt kê `lib-fx/_tools`.
- Không sửa code nào khác trong `lib-fx/_core/formulas/vector/`.

## Bước
1. **Công cụ đo độc lập** `lib-fx/_tools/rebuild_check.py PROFILE [--variant V] [--mode dark|bright] [--frames A-B]`:
   - ảnh gốc khung f: `measure.load_frame(prof, v, f)`; ảnh dựng: `prof.out_dir() / "frames" / f"{v}_{f:02d}.png"`; nền: khung `background_frame` của profile (cùng loader);
   - `L = 0.299 R + 0.587 G + 0.114 B`;
   - `--mode dark` (khói): `M = (max_kênh |ảnh - nền| > 14) & (L < 110)` trên cả hai ảnh, in `f, area_ref, area_reb, IoU`;
   - `--mode bright` (nét sáng): `M = L > 170`; in `f, area_ref, area_reb, area_ratio = reb/ref, width_ref, width_reb, width_ratio`,
     width = `2 * mean(distance_transform_edt(M)[skeletonize(M)])` (scipy + scikit-image); khung nào `area_ref` < 50 thì bỏ qua;
   - cuối bảng: trung bình, thấp nhất, khung thấp nhất; ghi CSV vào `lib-fx/_study/<profile>/check_<mode>.csv`.
   **Kiểm**: chạy `python lib-fx/_tools/rebuild_check.py flame-burst --mode dark --frames 28-60` trên bản R1 hiện có: khung 33 ra IoU ≈ 0,6 (±0,08). Lệch xa hơn → sai mặt nạ, sửa công cụ.
2. Profile: thêm lớp **`smoke_lit`** (vỏ khói được chiếu sáng), **không** có `darker_than_bg`, giữa `smoke` và `orange`. `order` = `["smoke", "smoke_lit", "orange", "yellow"]`.
   - `colours`: [57,39,40], [68,36,32], [83,40,29], [110,50,28]; `tol` 14. Lấy thêm màu bằng `palette flame-burst --variant jet --frame 33` nếu `check` báo `MISSING LAYER`.
   - Màu mép (141,61,29) không vào `smoke_lit` (nó là mép cam tối): nếu `check` báo thiếu, thêm vào **`orange`**.
3. Profile: `"halo_w": 0` cho `smoke` và `smoke_lit` (khói không phát sáng). Giữ `halo_model` blur.
4. `measure flame-burst` (đo lại `gradient` cho `smoke_lit`: viền nâu đỏ), rồi chạy thử `rebuild flame-burst --frames 12,33,38,44`.
   **Kiểm bằng mắt** 4 khung đó cạnh gốc: vỏ khói nâu bọc kín lửa ở 33, 38; không còn lỗ khói giữa thân; hộp đen bên trái không bị tô; khung 44 không có quầng cam quanh khói.
   Nếu nền xám bị nhận vào `smoke_lit` (vệt nâu quanh mọi thứ): giảm `tol` 14 → 11, bỏ màu [57,39,40]; ghi lại.
5. Đạt bước 4 → `all flame-burst`, `showcase flame-burst`.

## Tiêu chí nghiệm thu (đo bằng `rebuild_check.py`, không dùng `report.json` làm tiêu chí)
- `--mode dark --frames 28-60`: IoU khung 33 ≥ 0,80, khung 38 ≥ 0,80, trung bình 28-60 ≥ 0,80, không khung nào < 0,65.
- `report.json`: IoU `orange`, `yellow` không tụt quá 0,03 so với R1 (0,776 / 0,859); `kinks` = 0.
- Ảnh: khung 44 không quầng quanh khói; khói có ít nhất 2 tông (thân tối + vỏ nâu sáng).
- `python lib-fx/_tools/vectorfx.py rebuild swirl-slash --frames 3-4`: hash khung trước và sau giống nhau (profile cũ không đổi).

## Báo cáo (điền dưới đây)
Bảng `rebuild_check` dark (khung 14, 33, 38, 44, 51, 58 + trung bình), IoU `report.json` 3-4 lớp, màu `smoke_lit` cuối cùng, `tol`, lệch so với task và lý do, đường dẫn `compare.gif`.

## Kết quả
