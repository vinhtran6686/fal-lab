# lib-fx: thư viện hiệu ứng chuẩn

Nơi lưu trữ chuẩn cho mọi hiệu ứng (fx) của dự án, dùng chung cho toàn bộ nhân vật. Mỗi hiệu ứng được vẽ bằng code
(0 USD, không gọi model) và lưu **riêng lẻ, không kèm nhân vật**. Nhân vật nào cần thì lấy từ đây ra dùng.

**Tư duy xây lib-fx (mục tiêu, các bước tái tạo → mô tả → biên độ → gắn nhân vật, tái tạo và sáng tạo, thư mục anh em): [MINDSET.md](MINDSET.md).**
**Bản đồ thư mục (mỗi nhóm, mỗi họ chứa gì): [GUIDE.md](GUIDE.md).**

**Hiệu ứng mới dựng bằng fxkit** (chồng lớp, vẽ giữa hai điểm a → b, phong cách tông phẳng xếp chồng): [_core/formulas/draw/FXKIT.md](_core/formulas/draw/FXKIT.md).
Họ dùng fxkit khai báo `EFFECTS` (vd. `impact/quake/quake.py`); họ cũ khai báo `VARIANTS` vẫn chạy như trước.

## Lệnh

```
python lib-fx/build.py                         dựng tất cả
python lib-fx/build.py force                   mọi họ trong một nhóm
python lib-fx/build.py force/shock             một họ (kèm gallery)
python lib-fx/build.py force/shock/drill       một hiệu ứng
```

```
python lib-fx/build.py --check [đường dẫn]     dựng rồi thoát mã 1 nếu có hiệu ứng FAIL cổng chất lượng
python lib-fx/_tools/fxcheck.py [đường dẫn]    chỉ đo lại khung đã có trên đĩa
python lib-fx/_tools/fxkit_sheet.py <kind|hiệu ứng> [key=value ...]   bảng duyệt một lớp: 4 seed / hướng / cỡ / bảng màu
python lib-fx/_tools/fxkit_test.py             kiểm hồi quy fxkit (tất định, có seed, tự tan, theo a → b, co giãn)
```

Biến thể cho nhân vật (không đụng thư viện):
```
python lib-fx/build.py melee/slash/crescent --from 120,60 --to 300,210 --pal blaze --seed 3 --fps 15 --split --out out/heroes/<id>/frames/fx/slash
python lib-fx/build.py melee/slash/crescent --from <mũi A> --to <mũi B> --track "root_a=X,Y;root_b=X,Y;up=35;turn=cw;ease=1.3" --pal frost --fps 15 --split --out <thư mục>
                                                vệt chém theo quỹ đạo vũ khí thật (chuôi + mũi, px ô @2x); `--set slash.weapon=axe` đổi sang vệt rìu
python lib-fx/build.py impact/hit/star --pal ice --s 0.8 --mirror --out <thư mục>          (họ cũ: --pal, --s, --mirror, --fps, --speed)
```

## Cổng chất lượng

`build.py` đo mọi hiệu ứng vừa dựng và ghi `qa` vào `meta.json` / `catalog.json`. FAIL: `clip` (chạm mép khung), `end` (khung cuối chưa trống),
`anchor`, `lint` (họ fxkit: thiếu vai trò, không lệch nhịp ...). Cảnh báo: `pop`, `cut`, `linger`, `empty0`, `flicker`, `tiny`, `speck`.
Hiệu ứng còn FAIL thì không được đổi `status` thành `approved`. Chi tiết từng phép đo: đầu file `_tools/fxcheck.py`.

Xem trước: `<nhóm>/<họ>/<id>/preview_game.gif` (cỡ game @1x phóng 3 lần, cạnh vạch cao 60 px của thân nhân vật: **duyệt bản này**), `_gallery/<nhóm>-<họ>.png` (mọi hiệu ứng, frame cách 1) và `.gif` (chạy cùng lúc, đúng tốc độ);
từng hiệu ứng: `<nhóm>/<họ>/<id>/preview.gif`.

## Một hiệu ứng gồm

```
force/shock/tiers/
  sheet.png            1 hàng, nền trong suốt, mỗi ô một frame
  frames/tiers_NN.png  từng frame
  preview.gif          xem nhanh trên nền tối
  meta.json            id, tên, trạng thái, tag, fps, số frame, cỡ frame @2x, điểm neo, hướng, bảng màu, nguồn
```

Code của cả họ nằm cạnh đó: `force/shock/shock.py`. Thư viện lưu @2x; biến thể cho nhân vật (`--out`) xuất cả @2x và @1x.

## Luật nhìn (mọi hiệu ứng trong thư viện)

- Hình mịn (siêu mẫu), màu phẳng 3-4 bậc với viền tối cùng tông, thêm quầng sáng mềm. Không pixel art, không dither.
- Nhiều tầng thì mỗi tầng một vai trò, sinh cách nhau rõ ràng (thường 1 frame ở 15 fps); tầng xa/cũ mờ hơn tầng gần/mới.
- Hình khối gọn: lưỡi liềm, thấu kính nhọn hai đầu, dải. Không rải gai hay mảnh vụn lung tung.
- Một hiệu ứng tự tan hết trước khi kết thúc, không biến mất đột ngột.
- Màu lấy từ `_core/palettes.py`; đổi màu là đổi bảng màu, không nhân bản hiệu ứng.

## Thêm hiệu ứng

1. Chọn họ trong [GUIDE.md](GUIDE.md); viết hàm `fn(t, P, front, back, pal=..., s=1.0, d=1)` trong `<nhóm>/<họ>/<họ>.py`
   (khuôn: `force/shock/shock.py`), dùng hình trong `_core/fxcore.py`.
2. Module khai báo `VARIANTS`, `CATALOG` (tên, mô tả, `status`: draft / approved / rework, tag), `TAGS`, `PAL_SUN`, `DUR`,
   `FRAME`, `ANCHOR`, `FPS`. `build.py` tự tìm module, không cần đăng ký.
   Một mục `CATALOG` có thể ghi đè riêng cho hiệu ứng đó: `frame`, `anchor`, `dur`, `palette` (bảng màu ghi vào meta), `glow` (màu quầng
   sáng) và `halo` (độ đậm, độ nhòe của quầng).
3. `python lib-fx/build.py <nhóm>/<họ>`, xem gallery, duyệt rồi đổi `status` thành `approved`.
4. Họ vừa có hiệu ứng đầu tiên: xóa README "chưa có hiệu ứng" của họ đó, cập nhật cột "Hiện có" trong GUIDE.md.

## Dựng lại hiệu ứng tham khảo bằng path vector

`_core/vector/` + `_tools/vectorfx.py`: đọc một GIF tham khảo (lớp màu, gradient mép, quầng), khớp mỗi lớp bằng nét thon, làm đều nét
kiểu Illustrator Simplify, tô chồng, xuất PNG + SVG và trang review. Mỗi hiệu ứng một profile JSON trong `_core/vector/profiles/`.
Hướng dẫn: [_core/formulas/vector/README.md](_core/formulas/vector/README.md).

## Dùng cho nhân vật

Lấy `sheet.png` hoặc `frames/` của hiệu ứng, đặt điểm neo (`anchor_2x` trong `meta.json`) vào điểm chạm của nhân vật
(vd. mũi chân khi đá), bắt đầu ở frame trúng đòn, lật ngang nếu nhân vật quay trái. Muốn đổi màu hay cỡ thì gọi thẳng hàm
với `pal` / `s` khác thay vì sửa ảnh. Khi `s` > 1 thì khung và điểm neo cũng nhân theo `s` (vd. `inferno`: khoảng 640x400 nhân `s`), không thì
hiệu ứng chạm mép.
