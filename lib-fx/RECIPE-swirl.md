# Công thức: Xoáy chém lửa / Xoáy chém băng (`melee/blade/swirl_fire`, `swirl_frost`)

Dựng lại từ một GIF tham khảo user gửi ngày 2026-11-06 (1920x1080, 38 frame, 25 fps, 1,52 s; hai hiệu ứng đặt cạnh nhau trên nền tối).
Nghiên cứu bằng `_tools/study_ref.py --bg median` (nền có gradient nên tách nền theo trung vị từng điểm ảnh), lưu ở `_study/ref01/`
(không commit). Quy trình chung: [REFERENCE-GIF.md](REFERENCE-GIF.md). Code: `melee/blade/blade.py`.

```
python lib-fx/build.py melee/blade        # swirl_fire 17 frame 460x460; swirl_frost 30 frame 380x380; @2x, 30 fps, neo ở tâm
```

## 1. Phân tích bản gốc

### 1.1 Nhịp (đo trên frame)

Đầu nét quét theo chiều kim đồng hồ, bắt đầu từ bên trái:

| Frame gốc | Thời điểm | Đầu nét (độ quét) | Chuyện gì xảy ra |
|---|---|---|---|
| 1 | 0 | - | trống (không có báo trước) |
| 2 | 0,04 s | ~100° | lưỡi liềm hiện ở trên bên trái, đuôi là mũi kim |
| 3 | 0,08 s | ~205° | quét qua đỉnh xuống bên phải, thân dày |
| 4 | 0,12 s | ~282° | đầu cuộn vào tâm thành xoắn ốc |
| 5 | 0,16 s | ~330° | xoắn ốc trọn, bắt đầu nguội |
| 6-8 | 0,2-0,28 s | - | **lửa**: vỡ thành mảnh; **băng**: tan, lộ vết nứt |
| 9-13 | 0,32-0,48 s | - | lửa: móc nhỏ dần thành đốm, hết ở ~0,5 s |
| 9-27 | tới ~1,05 s | - | băng: chỉ còn vết nứt mảnh, mờ dần |

Đầu nét chạy rất nhanh (330° trong 4 drawing), đuôi gần như đứng yên: nét **dài ra** chứ không trượt đi. Bản gốc không có nhịp báo trước;
mình giữ đúng như vậy (ngoại lệ có chủ ý so với DESIGN.md §1).

### 1.2 Các lớp của bản lửa

| Lớp | Hình | Màu (lấy từ pixel) | Thay đổi theo thời gian |
|---|---|---|---|
| Quầng sáng | rộng, mềm, phủ cả lòng xoắn; thêm một viền sáng hẹp sát thân | hồng đậm, hồng | mạnh nhất khi quét, tắt dần khi vỡ |
| Thân | lưỡi liềm dày gần như ngay từ đầu, mép ngoài trơn với vài khía nhỏ, đầu tù, đuôi mũi kim thẳng theo tiếp tuyến | vàng 255,215,113 → hổ phách khi nguội | dài ra theo đầu nét, cuộn vào tâm |
| Dải hồng phía trong | ôm mép trong; hẹp ở đầu, phủ hết bề rộng ở đuôi (đuôi toàn hồng) | hồng 255,100,142 | đi theo thân |
| Lưỡi lửa hồng | gốc ở mép dải hồng, liếm ngược chiều quét vào phần vàng (răng cưa nằm TRONG thân, không thò ra ngoài) | hồng | 3 cỡ, xếp theo cụm |
| Lõi hồng đậm | dải hẹp sâu bên trong | hồng đậm 254,68,123 | |
| Mảnh vỡ | 4 lưỡi liềm khác cỡ: móc lớn ở tâm (đầu nét cũ), cung dài bên phải, hai mảnh mảnh ở trên | hồng, đầu vàng rồi hổ phách | mỏng dần, xoay tiếp theo chiều quét 10-20°, trôi ra ngoài; mỗi mảnh một kết cục |
| Đốm lửa | vụn nhỏ nơi mảnh tắt | hồng / vàng | |

### 1.3 Các lớp của bản băng

| Lớp | Hình | Màu | Thay đổi |
|---|---|---|---|
| Quầng sáng | hai cỡ như bản lửa | xanh dương, cyan | tắt dần |
| Bóng mờ (after-image) | bản sao rộng hơn của nét, trễ một nhịp, mép mềm | xanh đậm, nhìn xuyên được | thấy rõ ở frame 4-8 rồi tan |
| Thân | lưỡi liềm trắng băng, đầu nhọn móc xuống | trắng 239,255,255, viền cyan | nguội **từ đuôi về đầu**: trắng → cyan → xanh |
| Vùng cyan / xanh | các vùng hình lông vũ ở phía trong, liếm ngược vào phần trắng | cyan 105,231,255, xanh 60,170,227 → 34,119,172 | lan dần về phía đầu |
| Lỗ | lỗ dài hình thấu kính theo tiếp tuyến, mở ra trong vùng xanh | - | to dần, thân vỡ thành mảnh |
| Vết nứt | vài đoạn thẳng mảnh, 2 cụm (một dài, một vừa) và vài đoạn nhỏ, nằm trên vùng bóng mờ | xanh mờ, lõi cyan | hiện khi nét đi qua, rõ nhất 0,2-0,45 s, rồi mờ, hết ~0,9 s |
| Mảnh | lát xanh nhỏ gần vết nứt | xanh / cyan | mờ dần |

**Lưu ý màu**: `palette.png` của công cụ là k-means trên điểm ảnh đã trộn quầng sáng và nền, nên các màu tối (27,60,84 / 71,31,41)
là quầng trên nền, không phải màu vẽ. Màu vẽ phải lấy mẫu trực tiếp ở giữa từng vùng (bảng trên). Bảng màu: `palettes.BLAZE`, `palettes.FROST`.

## 2. Cách dựng

**Một đường xoắn chung** (`_rad`, `_edges`):
- Bán kính có dao động chậm `1 + 0.07·sin(3θ)`, để hình là tam giác bo tròn chứ không phải vòng tròn compa.
- Bán kính tụt mạnh ở 30% cuối (`curl` 0,7 cho lửa, 0,3 cho băng), nên đầu nét cuộn vào tâm.
- Đầu nét: `TH0 + 330°·(1 - (1-u)^1.6)` với `u = t/0.16`, khớp số đo ở trên.
- Bề rộng theo vị trí dọc nét `v`:
  - lửa: `v^0.35·(1-v^12)^0.2`, dày ngay và đầu tù;
  - băng: `v^0.4·(1-v^6)^0.4`, đầu nhọn;
  - mảnh vỡ: `sin(πv)^0.55` nhân hệ số hình móc vuốt.
- Đuôi: một mũi kim thẳng theo tiếp tuyến (`_needle`).

**Màu chạy dọc nét theo tuổi, không theo khoảng cách tới mép**. Mỗi màu là một mặt nạ phẳng, cắt trong thân bằng `Shape.paint(clip=thân)`:
- dải phía trong rộng `band(v)` phần bề rộng, hẹp ở đầu (nóng), rộng ở đuôi (nguội);
- lưỡi lửa / lông vũ (`_licks`) mọc từ mép dải, liếm ngược chiều quét;
- bản băng có `band` lớn dần theo thời gian (nguội từ đuôi về đầu);
- lỗ cắt bằng `Shape.paint(cut=...)` với hình thấu kính dọc tiếp tuyến.

Không dùng dải theo khoảng cách cho thân (sẽ ra kiểu "sticker có viền") và không có viền tối: mép là do quầng sáng tạo ra.

**Quầng sáng hai cỡ chỉ từ thân** (`fxcore.glow_under`): một lớp rộng, mờ (blur 18-22 px) và một lớp hẹp, sáng (4-6 px), vẽ ở lớp
`back`. Độ mạnh giảm theo nhiệt. Quầng của `build.py` tắt (`halo=(0, 8)`) để vết nứt và bóng mờ không bị phát sáng như thân.

**Bóng mờ của bản băng**: vẽ nét ở `t - 0.05`, rộng 1,45 lần, màu xanh đậm, độ đậm 0,6, làm mờ (Gaussian), đặt ở lớp `back`.

**Mảnh vỡ của bản lửa** (`PIECES`): mỗi mảnh có khoảng trên nét, bề rộng, độ trôi, độ xoay, kết cục (`fade`, `split` mở khe ở giữa,
`curl` cuộn chặt hơn vào tâm) và thời gian sống riêng (0,14-0,3 s); đầu mảnh vàng rồi hổ phách, thân hồng rồi hồng đậm.

## 3. So với bản gốc

Mỗi vòng đều so frame cạnh nhau, cắt riêng từng hiệu ứng, theo cùng đồng hồ: bản gốc trên, của mình dưới.

| Vòng | Lệch | Sửa |
|---|---|---|
| 1 | Nét mảnh như vòng nhẫn; đuôi rút sớm; mảnh vỡ thành cục; vết nứt sớm, đậm như khung dây | đo nhịp từ GIF; bề rộng dày ngay; đuôi gần đứng yên |
| 2 | Màu theo khoảng cách tới mép ra kiểu sticker; gai thò ra ngoài như gai hoa hồng | màu theo tuổi dọc nét (mặt nạ cắt trong thân); lưỡi lửa nằm trong thân |
| 3 | Xoắn chưa cuộn; vòng tròn đều; mảnh vỡ hình hạt chanh | bán kính tụt ở 30% cuối; dao động bán kính; mảnh hình vuốt (dày một đầu, đuôi nhọn dài) |
| 4 | Bản băng không tan (xói mòn quá nhỏ so với độ dày); bóng mờ đè lên quá lâu | xói mòn tới 46 px, quét ngắn hơn (hình lưỡi liềm); bóng mờ ngắn và nhạt hơn; vết nứt vẽ sau quầng sáng |
| 5 | Quầng sáng chạm mép khung | khung bản lửa 460x460 |

Còn khác: lưỡi lửa hồng trong thân bản gốc nhiều và sắc hơn; vết nứt bản gốc có nhiều nhánh hơn; móc ở tâm bản lửa gốc to và vàng hơn.
