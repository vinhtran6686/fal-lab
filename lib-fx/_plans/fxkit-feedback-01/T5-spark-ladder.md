# T5. Thang trúng đòn: nhẹ, nặng, chí mạng khác nhau rõ

Phụ thuộc: T1. Độc lập với T2, T3.

## Vấn đề
`impact/spark/crit` là `heavy` phóng to (cùng hình, cùng nhịp). Người chơi phải phân biệt được ba mức **trong một khung hình ở cỡ game**, kể cả khi
không thấy màu.

## File được sửa
- `lib-fx/impact/spark/spark.py`
- `lib-fx/_core/formulas/draw/fxkit/layers/burst.py` (chỉ khi cần tham số mới cho `star`; không đổi mặc định)
- `lib-fx/GUIDE.md` (dòng `impact/spark`)

## Cách làm
Mỗi mức khác nhau ở **bốn trục** cùng lúc: hình bóng, số lớp, nhịp, màu.

| | light | heavy | crit |
|---|---|---|---|
| Hình bóng | chớp nhỏ 3-4 mũi lệch một phía theo hướng đòn | chớp 5 mũi + vòng tròn | **chữ thập / X**: 4 mũi rất dài, mảnh, gần vuông góc nhau (`star` với `n=4`, `gaps=0`, `jitter` nhỏ, `minor=0`) chồng lên một chớp 5 mũi ngắn; đường viền nhọn hơn hẳn |
| Vòng | không | 1 vòng | **2 vòng lệch nhịp** (vòng 2 sinh sau 3 khung, nhỏ hơn) |
| Tia tốc độ | không | 4, theo hướng đòn | 6-8, mọi hướng, dài |
| Mảnh văng | 5 | 10, phía trước | 14-16, mọi hướng, to hơn (`size` 22) |
| Khung trúng đòn | 1 khung quá sáng | 1 khung | **2 khung quá sáng** (giữ hình đỉnh trắng thêm 1 khung: thêm một lớp `star` id `flash` sống 2 khung, tông `white`, hoặc tham số `flash_frames` cho `star`) |
| Thời gian | ~0.3 s | ~0.55 s | ~0.7 s (mảnh và vòng 2 kéo dài) |
| Diện tích đỉnh (so với light) | 1 | ≥ 2.5 | ≥ 4.5 |
| Bảng màu mặc định | `sun` | `sun` | `holy` với **lõi trắng lớn** và tông `hot` chiếm nhiều hơn; cân nhắc thêm tia `accent` |

1. `crit` không còn là `_heavy.variant(...)` chỉ đổi số: viết chồng lớp riêng (có thể dùng lại `_heavy` rồi thêm lớp `cross`, `ring2`, `flash`).
2. Nếu `star` cần mũi "chữ thập" (4 mũi đều, dài, mảnh): thêm tham số `even=False` vào `star` (khi `True`: hướng chia đều, không jitter, mọi mũi cùng cỡ).
   Đây là ngoại lệ có chủ ý của luật "không đều": chữ thập là ký hiệu, không phải hình tự nhiên; các lớp khác của `crit` vẫn không đều.
3. Kiểm ở cỡ game: xuất ba `preview_game.gif`, đặt cạnh nhau; chuyển ảnh sang **xám** và kiểm lại (phải phân biệt được không cần màu).

## Tiêu chí nghiệm thu
- [ ] Ở khung đỉnh, cỡ game, ảnh xám: ba hình bóng khác nhau rõ (nhỏ lệch / sao + vòng / chữ thập dài + 2 vòng).
- [ ] Diện tích đỉnh (tổng alpha khung đỉnh, in từ `fxcheck`): heavy ≥ 2.5 × light, crit ≥ 4.5 × light.
- [ ] Số khung: light < heavy < crit.
- [ ] `light` và `heavy` không xấu đi so với hiện tại (người dùng đã khen `impact/spark`): so ảnh trước / sau.
- [ ] `impact/spark --check` không FAIL; lint sạch.

## Lệnh
```
python lib-fx/_tools/fxkit_sheet.py impact/spark/heavy && python lib-fx/_tools/fxkit_sheet.py impact/spark/crit     # chụp TRƯỚC
python lib-fx/build.py impact/spark --check
```

## Kết quả (người làm điền)

Làm xong 2026-11-13.
- `burst.py`: `star` có tham số mới `even` (mặc định False, không đổi gì cho nơi khác): hướng chia đều, lệch vài độ, mọi mũi cùng cỡ.
- `spark.py`: `crit` viết lại thành chồng lớp riêng: `ring` + `ring2` (sinh sau 4 khung, nhỏ hơn), `flash` (star trắng lớn, sống 2 khung), `cross` (star `even`, n=4, dài 210, mảnh), `star` 5 mũi ngắn, `streaks` 7 mọi hướng, `scraps` 15 to (size 22). Bảng màu `holy`. `light`: sao giới hạn `arc=(-80, 80)` để lệch về một phía; `heavy` không đổi.
- Số đo (1x, tổng alpha khung đỉnh): light 1025, heavy 6075 (5.9x), crit 10664 (10.4x). Số khung: 14 / 18 / 21. Thời gian crit ~0.67 s.
- Xem ảnh xám khung đỉnh: ba hình bóng khác rõ (chớp nhỏ lệch / sao + vòng / chữ thập dài + vòng).
- `build.py impact/spark --check`: không FAIL, chỉ warn `linger` (cuối đuôi mảnh vụn, cả ba mức; heavy cũ cũng có). `fxkit_test.py`: all checks passed. Lint sạch.
- Chưa so sánh ảnh trước/sau của `light` theo từng pixel: light đổi hướng sao (một phía) nên khung đỉnh khác chút, diện tích 1066 -> 1025.
- Lưu ý: commit WIP f03efe7 của điều phối đã gồm cả file dựng lại của `impact/spark`; T6 sẽ dựng lại lại.
