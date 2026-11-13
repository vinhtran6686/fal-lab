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
