# ref_atlas: tách atlas tham khảo thành frame và animation

`scripts/ref_atlas/` biến một atlas kiểu Cocos (một `.png` + một `.lua`) thành frame rời, gif và các animation có tên. Dùng để **đọc động tác của game tham khảo** trước khi dựng động tác cho nhân vật của mình (xem `docs/pipeline/pose-from-reference-clip-method.md`). Chỉ tách và ghép, không gọi API, 0 USD. Kết quả nằm trong `ref/<tên>/`, chỉ để đọc.

## Dữ liệu cần
| File | Vai trò |
|---|---|
| `<atlas>.png` | ảnh atlas |
| `<atlas>.lua` | mỗi sprite có `size` (canvas gốc), `trim` (lề trái, trên, phải, dưới), `f_quad` (x, y, w, h trong atlas) và `alias` (các số khung dùng chung một hình) |
| bảng animation (`.lua` hoặc `.json`) | **tên và khoảng khung của từng động tác**: `{prefix, from, to}`, động tác nhiều lớp thêm `layer_prefix`, `layer_from`, `layer_to`. Atlas KHÔNG chứa thông tin này. Với KR5 nó nằm ở `games/kr5/src/kr5/data/animations/all/<tên>.lua` (và `.json`) trong repo `reverse` |

Thiếu bảng animation thì chỉ nhóm được khung theo tiền tố tên, và các động tác nối liền nhau (idle, đi, đánh, kỹ năng) lẫn vào một nhóm.

## Lệnh (chạy ở gốc repo)
```
python scripts/ref_atlas/split_atlas.py ref/<tên> <atlas>.lua <atlas>.png
python scripts/ref_atlas/build_animations.py ref/<tên> <bảng-animation>.json
```
- `split_atlas.py` ghi `ref/<tên>/out/<nhóm>/` (`frames/NNNN.png`, `preview.gif`, `contact_sheet.png`, `frames.json`) và `out/README.md` (bảng từng khung). `out/` bị git bỏ qua (`ref/<tên>/.gitignore`), dựng lại bất cứ lúc nào.
- `build_animations.py` đọc `out/` và ghi `ref/<tên>/anim/<động-tác>/` (`frames/` giữ số khung gốc, `preview.gif` 30 fps) cộng `ref/<tên>/preview.html` xem tất cả gif. Động tác nhiều lớp được xếp chồng các lớp. Động tác trỏ tới sprite không có trong atlas này bị bỏ qua và in ra.

## Quy tắc đọc
- Khung `size` = canvas gốc; frame = ảnh cắt đặt tại (lề trái, lề trên). Script kiểm `lề trái + w + lề phải = size.w` cho mọi entry.
- Game gốc chạy "on twos": mỗi hình giữ 2 khung. Đếm hình khác nhau (so từng cặp khung), không đếm khung.
- Chân và bóng của nhân vật gốc thường đứng yên một chỗ suốt động tác. Đo vị trí bóng trước khi kết luận động tác nào có bước chân.
