# Công thức: Hỏa hổ lướt (`life/dash/tiger`)

Hiệu ứng lướt có một con hổ lửa lao đi trước, dựng theo ảnh tham khảo của user ngày 2026-11-06 (concept lướt lửa: đầu hổ lửa, lưỡi lửa,
khói xám, mảnh gió). Code: `life/dash/dash.py` (`dash_tiger`). Phương pháp nhiều lớp và các kỹ thuật dùng chung: [RECIPE-inferno.md](RECIPE-inferno.md).

```
python lib-fx/build.py life/dash/tiger          # 28 frame, 800x340 @2x, neo (160, 190), 0,88 s, 30 fps
```

**Neo và nhân vật.** Điểm neo là ngực nhân vật lúc bắt đầu lướt. Đầu hổ chạy `450·s` px trong 0,4 s, nhanh rồi chậm dần:
`head_x(t) = P.x + d·s·450·(1 - (1 - t/0.4)²)`. Nhân vật di chuyển theo `head_x`. Mặt đất nằm dưới neo 62 px.

## 1. Đọc ảnh tham khảo

| Trong ảnh | Thành lớp |
|---|---|
| Đầu hổ lửa trắng vàng, há miệng, nét mặt cam đỏ | đầu hổ (lớp 9), nét mặt (lớp 10), bùng khi dừng (lớp 11) |
| Lưỡi lửa uốn cong sau đầu: vàng gần đầu, cam ở giữa, đỏ ở xa | lưỡi lửa (lớp 6) |
| Mảnh lửa đỏ nhỏ rải phía sau | tàn đỏ (lớp 7) |
| Vệt lửa vàng dài nằm ngang (khung trên) | vệt vàng (lớp 8) |
| Khói xám nhạt sát đất, đuôi nhọn quét về sau; dải xám trong mờ | khói, sương đất (lớp 1, 4) |
| Mảnh gió xám nhạt hình răng cưa | mảnh gió (lớp 12) |
| Cung gió xám lớn, nét tối mảnh (khung trên) | cung gió, nét tốc độ (lớp 2, 3) |
| Móng bụi xám lớn ở chân (khung trên, bên phải) | bụi đạp (lớp 5) |

Bảng màu đúng như ảnh: **đỏ, cam, vàng** cho lửa (`FLAME`), **xám, xám nhạt** cho khói, gió, bụi (`SMOKE`). Màu phẳng, không viền.

## 2. Mười hai lớp (sau ra trước)

| # | Lớp | Cách vẽ | Ghi chú |
|---|---|---|---|
| 1 | Sương xám sát đất | dải đa giác nhọn hai đầu, alpha 0,26, trên lớp riêng | đuôi đuổi theo đầu khi tan |
| 2 | Hai cung gió xám | `ribbon` thon theo cung elip | cung mở ra rồi đuôi đuổi theo |
| 3 | Nét tốc độ xám tối | `lens` mảnh, 10 nét lần lượt | dài khi nhanh, ngắn khi chậm |
| 4 | Khói toon sát đất (8 cụm) | `Shape`: 3 `blob` + 3 đuôi `flame`, tô bằng `organic.shade` | to ra, bay lên, trôi về sau, ăn mòn |
| 5 | Bụi đạp ở chân lúc bắt đầu | 5 móng `thorn` + 4 `blob`, `shade` | bật ra trong khoảng 0,04 s, nở tiếp tới 1,3 lần, tan trong 0,5 s |
| 6 | 22 lưỡi lửa dọc đường lướt | `flame` (hình chữ S) + nhánh nhỏ, `flame_bands` | sinh khi đầu đi qua; nguội vàng → cam → đỏ |
| 7 | Tàn đỏ từ đỉnh lưỡi lửa | `shard`, bay lên và lùi lại, sống 0,5 s | dải màu nguội (`heat 0.2`) |
| 8 | 4 vệt lửa vàng sau đầu | `thorn` nằm ngang | dài theo tốc độ, ngắn lại khi chậm |
| 9 | Đầu hổ | `spline(TIGER_HEAD)` + 2 tai + 6 bờm `flame` + 3 lông má, miệng khoét `on=False` | trắng ở giữa, cam ở mép |
| 10 | Nét mặt và nanh | `lens` màu `rim` (mắt, mày, mũi, vằn), 3 nanh trắng, chấm mắt | trên lớp riêng |
| 11 | Đầu bùng lúc dừng | đầu rỗng từ giữa (`hole`), ăn mòn có nhiễu, 4 lưỡi lửa phóng về trước | vỡ thành vòng lửa rồi thành mảnh |
| 12 | Mảnh gió xám nhạt | đa giác răng cưa, bay ra sau và ra ngoài, xoay | 4 mảnh lúc đạp, 10 mảnh dọc đường |

## 3. Dòng thời gian

| Frame | Thời điểm | Chuyện gì xảy ra |
|---|---|---|
| 1-3 | 0-0,07 s | Đầu hổ bật ra (vượt đà), bụi đạp tung ở chân, mảnh gió bay ra |
| 4-12 | 0,1-0,37 s | Đầu lao đi; lưỡi lửa mọc lên sau đầu, lửa gần đầu vàng, xa đầu đỏ; khói phủ sát đất |
| 13-20 | 0,4-0,63 s | Đầu dừng, bùng (từ 0,38 tới 0,64 s): rỗng giữa, vỡ thành vòng lửa, 4 lưỡi lửa phóng tới trước |
| 21-28 | 0,67-0,9 s | Lưỡi lửa cuối bốc lên và tan, tàn đỏ trôi, khói cuối cùng tan hết |

## 4. Kỹ thuật mới (so với Hỏa xung tầng)

**Lưỡi lửa hình chữ S** (`flame`): như `organic.thorn` nhưng xương sống vừa cong (`bend·s²`) vừa uốn sóng (`wave·sin(1.6πs)`), thân phình ở
một phần ba dưới. Sóng thay đổi theo thời gian, nên lửa "sống". Lưỡi lửa rộng (30-42 px), đuôi `p = 1.1`; lưỡi mảnh trông như gai hay que.

**Nguội theo tuổi, không theo vị trí.** Mỗi lưỡi lửa có tuổi riêng: `heat = 0.9·(1 - smooth(0, 0.8, u))`. Vì lửa sinh khi đầu đi qua, lửa
gần đầu luôn trẻ (vàng), lửa xa luôn già (đỏ), đúng như ảnh mà không cần tô theo vị trí. `flame_bands` bỏ màu nóng trước; `heat = 0` là đỏ hết.

**Hình nhân vật dựng tay bằng spline.** `TIGER_HEAD` là 20 điểm vẽ đầu hổ nhìn nghiêng (trán, sống mũi, hàm trên, hàm dưới, lông má),
nối bằng đường cong Catmull-Rom (`spline`). Miệng là một hình khoét (`poly(..., on=False)`): mép miệng được tô như mép ngoài nên tự có
viền cam. Nét mặt là các `lens` màu `rim` vẽ đè lên. Tọa độ nhân `g` (to dần, vượt đà) và lật theo `d` qua hàm `H`.

**Khói toon cho hình bất kỳ** (`organic.shade`, mới): như `cloud()` nhưng nhận một `Shape` có sẵn (cụm tròn + đuôi nhọn). Tô 3 tông bằng cách
dịch bóng hình về phía/ra xa nguồn sáng (`shadow`, `base`, `light`). Chỉ xử lý trong khung bao của hình.

**Tan đầu to mà không "bụp".** Hình rất dày thì ăn mòn chỉ gọt mép thành một cục phẳng. Cách làm: khoét lỗ ở giữa (`hole`, lớn dần) +
nhiễu mạnh (16 px), để đầu thành vòng lửa rồi vỡ thành các cung; kéo dài 0,26 s.

## 5. Nhật ký lặp

| Vòng | Thấy gì | Sửa |
|---|---|---|
| 1 | Lưỡi lửa mảnh, có nhánh, trông như gạc hươu | lưỡi lửa chữ S rộng 30-42, nhánh chỉ ở khoảng 1/4 số lưỡi |
| 1 | Khói thành một dải liền như khúc gỗ | 8 cụm thưa (cách 56 px), đuôi dài, ăn mòn sớm hơn |
| 1 | Đầu là quả cầu gai, không ra hổ | dựng đầu bằng 20 điểm spline, miệng khoét, 3 nanh, 6 bờm rộng thay 9 gai |
| 1 | Hình chạm mép trái (móng bụi, nét tốc độ) | neo 130, móng ngắn hơn, nét tốc độ không vượt quá 70 px sau neo |
| 4 (review) | Mảnh gió lúc đạp chỉ cách mép trái 2 px; 34 trường nhiễu (khoảng 330 MB) | neo 160; lưỡi lửa dùng 3 seed nhiễu chung |
| 2 | Dải sương thành tấm xám chữ nhật | dải nhọn hai đầu, mờ hơn, tan trước 0,7 s |
| 2 | Đầu tan thành một khối vàng trong mờ | vẽ đầu luôn đậm (alpha 1), chỉ tan bằng ăn mòn |
| 3 | Đầu tan thành cục cam phẳng rồi mất trong 1 frame | lỗ rỗng giữa + nhiễu mạnh, bùng kéo dài 0,24 s |

## 6. Biến thể

- Đổi màu: `pal=` bảng màu khác (thiếu `tip`, `back` thì tự suy); khói giữ màu xám.
- Không phải hổ: thay `TIGER_HEAD` / `TIGER_FACE` / `TIGER_FANGS` bằng điểm của con khác (rồng, sói), giữ nguyên thân lửa.
- Lướt ngắn hơn: đổi `T_RUN`, `RUN`, và **sửa tay** các vị trí đang ghi cứng theo quãng 450 px: lưỡi lửa (tới 443 px), khói (tới 426), mảnh gió (tới 418),
  đuôi sương (420), cung gió, docstring. `_passes(x)` chỉ tính lúc đầu đi qua x; x vượt `RUN` sẽ sinh ngay chỗ đầu dừng.
