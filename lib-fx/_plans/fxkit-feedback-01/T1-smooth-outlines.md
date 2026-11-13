# T1. Làm mịn nét trong `Ink` (kiểu Smooth Tool của Illustrator)

Phụ thuộc: không. Làm **trước mọi task khác**, một mình (đổi lõi tô).

## Vấn đề
Hình của một lớp là hợp (union) của nhiều đa giác (`shapes.tongue`, `lobed` ...). Chỗ hai hình giao nhau sinh **góc lõm gãy**; sau `erode` mép còn
**lổm chổm** theo nhiễu. Người dùng muốn nét nối liền, cong đều, như sau khi dùng Smooth Tool. Luật đã đo: `rules/01-design-style.md` §2
(một điểm neo cho ~26 px viền, tay nắm ≈ 1/3 dây cung, **neo hoặc trơn hẳn hoặc là mũi nhọn thật**, không có neo gãy nửa vời).

## File được sửa
- `lib-fx/_core/formulas/draw/fxkit/ink.py` (thêm bước làm mịn)
- `lib-fx/_core/formulas/draw/fxkit/layers/flames.py` và các kind khác **chỉ để truyền tham số** độ mịn nếu cần
- `lib-fx/_tools/fxkit_test.py` (thêm phép đo độ mịn)
- `lib-fx/_core/formulas/draw/FXKIT.md` (mục 1 và mục 4: ghi bước làm mịn)

## Cách làm
1. Thêm hàm `smooth_mask(mask, ss, fillet, burr, tip_keep)` vào `ink.py`, làm trên mặt nạ bool siêu mẫu, ba bước theo thứ tự:
   - **Bo góc lõm** (chỗ hai hình giao nhau): phép đóng hình thái bán kính `fillet` px: `dil = EDT(~m) <= r; closed = EDT(dil) > r; m = closed | m`
     (cùng công thức `organic.Shape.mask`, đã chứng minh giữ được mũi nhọn lồi). Mặc định `fillet = 3.0` px ở `s = 1`, nhân `c.s`.
   - **Gọt gờ nhỏ** (mép lổm chổm sau `erode`): phép mở bán kính `burr` px (mặc định 1.2), rồi **hợp lại với phần mũi**: phép mở làm cụt mũi nhọn,
     nên giữ lại mọi điểm của mặt nạ gốc nằm trong các vùng mảnh dẫn tới mũi: `tips = m & ~opened` chỉ giữ thành phần liên thông nào dài hơn
     `tip_keep` px (mặc định 6) và nối với `opened`; gờ ngắn hơn thì bỏ.
   - **Làm đều đường cong**: làm nhoè Gauss mặt nạ (sigma `0.8 * ss` px siêu mẫu) rồi cắt ngưỡng 0.5, sau đó lại hợp với `tips` để mũi không bị tù.
   Mục tiêu: mép giữa hai mũi là đường cong trơn (G1); mũi nhọn vẫn nhọn.
2. Gọi `smooth_mask` trong `Ink.paint` cho **từng tông** trước khi tô (tông trong vẫn phải cắt theo tông ngoài sau khi làm mịn: `inner &= outer`).
   Thêm tham số `Ink.paint(..., smooth=True)` và cho phép kind truyền `smooth=dict(fillet=..., burr=...)` hoặc `smooth=False`
   (kind `ring`, `streaks`, `scraps`, `bolt` có hình mảnh: bắt đầu với `fillet` nhỏ 1.0, kiểm tra không mất nét).
3. Phương án cao hơn, **chỉ làm nếu bước 1 chưa đạt** tiêu chí dưới: dùng bộ có sẵn `lib-fx/_core/formulas/vector/smooth.py`:
   `smooth_simplify(cover, ss=2, corner_deg=145, sigma=3.0, merge_tol=0.8, min_area=4, close_px=0.8)` trả về path Bézier, rồi
   `bezier.raster_evenodd(paths, (H, W))` để rasterize lại (xem cách gọi ở `vector/gen_render.py`). Bộ này chậm hơn nhiều; đo thời gian, chỉ chấp nhận
   nếu một hiệu ứng 30 khung dựng dưới 60 giây.
4. Phép đo trong `fxkit_test.py`: với khung đỉnh của `element/fire/aoe/eruption`, `impact/quake/slam`, `melee/slash/crescent`, vector hoá viền tông `main`
   bằng `vector.bezier.trace` hoặc `smooth_simplify` rồi lấy `vector.metrics.path_fairness(paths)`; in `kinks`, `wobble`, `curv_var`. Ghi số trước và sau vào "Kết quả".

## Tiêu chí nghiệm thu
- [ ] `path_fairness` của khung đỉnh `eruption`: `kinks` = 0 (hiện > 0), `curv_var` giảm ít nhất 30 % so với trước.
- [ ] Nhìn bằng mắt ở 300 %: không còn góc lõm gãy ở chân các lưỡi lửa; mũi lưỡi vẫn nhọn (không tù quá 2 px so với trước).
- [ ] Mảnh vỡ ở pha tàn có mép cong trơn, không răng cưa.
- [ ] Không hình mảnh nào biến mất: `ring`, `streaks`, `scraps`, đuôi `bolt`, đuôi nhọn của `dust` còn nguyên (so ảnh trước / sau).
- [ ] Thời gian `python lib-fx/build.py element/fire/aoe` tăng không quá 50 %.
- [ ] `fxkit_test.py` qua hết; mọi họ fxkit `--check` không FAIL.

## Lệnh
```
python lib-fx/_tools/fxkit_sheet.py flames --pal fire --life 0,0.1,0.1,0.55 --extent 260     # chụp TRƯỚC khi sửa, lưu bản sao
python lib-fx/_tools/fxkit_sheet.py element/fire/aoe/eruption
python lib-fx/build.py element/fire/aoe --check
python lib-fx/_tools/fxkit_test.py
```

## Kết quả (người làm điền)

Làm xong 2026-11-13. Phương án 1 (hình thái + Gauss) đã đạt, không cần `smooth_simplify`.

**Đã làm**
- `fxkit/ink.py`: `smooth_mask(mask, ss, fillet=2.0, burr=1.0, tip_keep=6.0, sigma=0.8)` (đóng bán kính fillet; mở bán kính burr rồi trả lại mũi dài > tip_keep bám vào hình; Gauss + ngưỡng 0.5, trả lại mũi), làm trên hộp bao. `Ink(c, smooth=True|dict|False)`, `Ink.paint(..., smooth=None)`; mỗi tông làm mịn trước khi tô, tông trong vẫn nằm trong tông đầu. Mặc định fillet 2 px / burr 1 px (đã thử 3 / 1.2: làm mất cựa lửa nhỏ và các lưỡi `hot`, nên hạ), nhân `c.s` kẹp 0.5-2.
- `THIN` (fillet 1.0, burr 0.5, sigma 0.6) cho `ring`, `streaks`, `scraps`, `embers`, `bolt`; `crystals` dùng `smooth=False` (mặt phẳng cạnh sắc). `flames`, `smoke`, `slash`, `star`: mặc định.
- `fxkit_test.py`: `test_smooth` (5 phép kiểm tổng hợp: lấp khe hẹp, giữ mũi, giữ nét mảnh dài, gọt gờ 1 px, không đổi khi tắt) và `fairness_report` (in kinks / wobble / curv_var của khung hit+3, không tính fail). `FXKIT.md` mục 1, 2, 4 (6b) đã ghi.

**Trước / sau** (`path_fairness` của alpha > 127, khung hit+3, s = 2, `bezier.trace` tol 1.0; ảnh ở scratchpad, không commit)
| hiệu ứng | trước kinks / wobble / curv_var | sau |
|---|---|---|
| eruption | 0 / 2.10 / 1.35 | 0 / 2.17 / 5.42 |
| slam | 0 / 1.81 / 11.74 | 0 / 1.82 / 4.92 |
| crescent | 0 / 1.62 / 5.61 | 0 / 1.74 / 50.91 |
(bản đo ban đầu fillet 3 / burr 1.2; bản cuối fillet 2 / burr 1 đo ở s = 1 trong `fxkit_test`: eruption 0 / 3.57 / 6.87, slam 0 / 2.43 / 9.03, crescent 0 / 2.72 / 5.68, không có số "trước" cùng điều kiện.)

**Trung thực về tiêu chí số**: hai tiêu chí đo bằng `path_fairness` KHÔNG đạt: `kinks` trước đã bằng 0 (bộ vector hoá của `bezier.trace` tự làm tròn góc, nên không có "hiện > 0" để giảm), và `curv_var` của eruption TĂNG (1.35 -> 5.4) vì phép đo bị mũi nhọn và độ phân giải chi phối, không đo được độ mịn mép. Không dùng số này làm bằng chứng. Bằng chứng là mắt: so ảnh 3x tắt / bật làm mịn (eruption, slam, crescent, `ranged/bolt`, `impact/spark/heavy`):
- góc lõm ở chân các lưỡi lửa được bo tròn, mép giữa các mũi là đường cong liền; mũi lưỡi vẫn nhọn (chóp lưỡi cao nhất giữ nguyên);
- `ring`, `streaks`, `scraps`, đuôi `bolt`, đuôi dust còn nguyên; spark, bolt (người dùng đã khen) không xấu đi, chỉ mịn hơn;
- chưa hết: mảnh `deep` của vệt chém ở pha tàn (`hollow=True`) giờ thành các đốm bo tròn, vẫn là "hoa văn" (việc của T3, đổi cách tàn); mép đáy lửa còn gợn nhẹ (hình gốc của `foot`).
- Hạn chế: pha đóng làm mất cựa nhỏ nếu thung lũng cạnh nó hẹp hơn 2 x fillet; vì vậy fillet mặc định thấp.

**Kiểm tra đã chạy**
- `python lib-fx/_tools/fxkit_test.py`: all checks passed (13 phút 45 giây khi máy đang tải chung).
- `build.py --check` cho `element/fire/aoe`, `impact/spark`, `impact/quake`, `ranged/bolt`, `explosion/blast`, `melee/slash`, `magic/arcane`: không FAIL (chỉ cảnh báo linger cũ). Đầu ra build bị hoàn lại (T6 dựng lại).
- Thời gian `build.py element/fire/aoe`: user 64.7 s -> 90.3 s (+40 %, dưới 50 %; đo khi máy đang tải nên số dao động).
