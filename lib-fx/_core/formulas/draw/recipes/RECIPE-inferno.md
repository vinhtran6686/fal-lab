# Công thức: Hỏa xung tầng (`force/shock/inferno`)

Ghi lại cách làm hiệu ứng **Hỏa xung tầng**, user duyệt ngày 2026-11-06 ("rất đẹp"), để làm lại hoặc làm các hiệu ứng nhiều lớp khác
theo cùng cách. Code: `force/shock/shock.py` (hàm `shock_inferno` và các hàm `_` đi kèm). Phương pháp chung: [lib-fx/_core/formulas/draw/DESIGN.md](../DESIGN.md);
hình tự do và tô màu theo khoảng cách tới mép: [lib-fx/_core/formulas/draw/RESEARCH-organic-impact.md](../RESEARCH-organic-impact.md).

```
python lib-fx/build.py force/shock/inferno      # 25 frame, 640x400 @2x, neo (60, 200), 0,78 s, 30 fps
```

## 1. Ảnh tham khảo và cách đọc nó

Ảnh concept "scatter gun" có 3 khung: tụ lực (quả cầu ở nắm đấm), bắn, trúng mục tiêu. Tách ra được:

| Thành phần trong ảnh | Vai trò | Thành lớp nào |
|---|---|---|
| Vòng đỏ sẫm đứng quanh nắm đấm | lực giật | lớp 6 |
| Chớp trắng nhiều gai nhọn | khoảnh khắc bắn | lớp 7 (gộp với tia lõi) |
| Tia lõi trắng nóng thon dần | lõi năng lượng | lớp 7 |
| 3-4 vòng nghiêng, nét đứt kiểu bút lông, giữa vàng, đầu nhọn cam đỏ | **hình chính**: sóng xung kích | lớp 1, 2, 8, 9 |
| Vòng ngoài cùng đỏ sẫm, mờ | sóng đã yếu | lớp 3 |
| 7 vệt mảnh có đầu mũi tên | đạn / tia | lớp 5, 10 |
| Móc rời, mảnh vụn, tàn lửa (khung 3) | vòng vỡ khi tan | lớp 8 (mảnh), 12 |

Quy luật vật lý user yêu cầu: **sóng càng lan xa càng to, càng nhạt, rồi tan**. Nên vòng **sinh trước** bay xa nhất và nở to nhất; ở
mọi frame vòng gần thì nhỏ và nóng, vòng xa thì to và nhạt.

## 2. Mười hai lớp (sau ra trước)

| # | Lớp | Nằm trên | Cách vẽ | Màu |
|---|---|---|---|---|
| 1 | Nửa xa của 4 tầng vòng | `back` | `Shape` + `dark_bands` (tô theo khoảng cách) | `back` → `tip` → `rim` |
| 2 | Vệt mờ: chỗ vòng gần vừa đi qua (trễ 0,05 s) | `back` | `ribbon` mảnh trên lớp riêng | `rim`, alpha 0,35 |
| 3 | Vòng áp suất dẫn đầu: to nhất, mảnh nhất | `back` | `ribbon` dọc `_ring_pt` | `back` / `tip` |
| 4 | Nón áp suất rất mờ từ nắm đấm tới vòng đầu | `back` | 2 đa giác lồng nhau, alpha 0,07 | `rim` |
| 5 | Vệt tốc độ mờ (7 vệt, không đầu) | `back` | `_tracer(head=False)` | `body` / `light`, alpha 0,45 |
| 6 | Vòng đỏ sẫm đứng quanh nắm đấm, nở ra rồi tan | `back` + `front` | `band` (nửa sau / nửa trước) + viền sáng | `back`, `tip`, `light` |
| 7 | Tia lõi + chớp gai: **một** hình tự do | `front` | `Shape`: `thorn` tia + 2 lưỡi lửa + `blob` + 17 gai (`thorns_at`) | `fire_bands` (trắng ở lõi) |
| 8 | Nửa gần của 4 tầng vòng | `front` | `Shape`: `_stroke` (nét bút) + gai mép ngoài + mảnh vụn khi vỡ | `fire_bands` nguội dần |
| 9 | Nét phụ mảnh chạy trong mỗi vòng, cháy hết trước | `front` | `ribbon` trên lớp riêng | `light` → `core` |
| 10 | Tia đạn có đầu mũi tên (7 sáng + 2 mảnh) | `front` | `_tracer(head=True)` | `body`, `light`, đầu `white` |
| 11 | Tia lửa bắn từ chớp (22 tia, phần lớn về trước) | `front` | `spark` + `drag_pos` | `light` / `core` |
| 12 | Tàn lửa bay lên từ đầu các cung | `front` / `back` | `spark`, trọng lực âm | `light` / `body` |

Thêm quầng sáng cam do `build.py` vẽ dưới cả hiệu ứng (`glow=(255, 120, 40)`, `halo=(0.55, 10)` trong `CATALOG`).

## 3. Dòng thời gian (30 fps)

| Frame | Thời điểm | Chuyện gì xảy ra |
|---|---|---|
| 1-2 | 0-0,033 s | **Tụ lực**: 9 tia hút vào quả cầu ở nắm đấm, vòng nhỏ siết lại |
| 3 | 0,067 s (`T_FIRE`) | **Bùng**: chớp gai và tia lõi trắng toàn bộ (frame đầu chỉ có 2 dải: `light` mép, `white` trong) |
| 4-8 | +0,03-0,17 s | 4 tầng vòng sinh cách nhau 0,04 s; tia đạn và tia lửa bay ra; tia lõi rời khỏi nắm đấm |
| 9-15 | +0,2-0,4 s | Vòng bay chậm dần và nở; nguội từ trắng sang vàng rồi cam; nét phụ cháy hết |
| 16-22 | +0,45-0,65 s | Vòng vỡ: các cung co lại, tách xa nhau 14%, ăn mòn có nhiễu, bắn mảnh vụn |
| 23-25 | tới 0,78 s | Tan hết, không còn gì ở frame cuối |

## 4. Bốn tầng vòng: bảng tham số

`INF_TIERS` trong code, đơn vị px @2x với `s = 1`:

| Tầng | Sinh sau bùng | Đi được | Bán kính đầu → cuối | Nét | Đời | Độ đậm |
|---|---|---|---|---|---|---|
| 0 (sinh đầu) | 0,00 s | 380 | 26 → 138 (+12% khi tan) | 19 | 0,74 s | 0,78 |
| 1 | 0,04 s | 290 | 24 → 114 | 20 | 0,69 s | 0,88 |
| 2 | 0,08 s | 200 | 20 → 88 | 20 | 0,63 s | 0,96 |
| 3 (sinh cuối) | 0,12 s | 118 | 16 → 62 | 18 | 0,57 s | 1,00 |

Chuyển động của một vòng, `u` từ 0 tới 1 trong đời của nó:
- vị trí `x0 + D·(1 - (1-u)^1.9)`: ra nhanh, chậm dần nhưng không đứng hẳn;
- bán kính `R0 + (R1-R0)·out_cubic(1.15u) + 0.12·R1·u`: nở nhanh rồi **vẫn nở tiếp** tới lúc tan (co lại trông yếu);
- nét `W·(1.15 - 0.7·smooth(0.05, 1, u))`: mỏng dần;
- độ đậm `smooth(0, 0.04, u)·(1 - smooth(0.55, 1, u))`;
- độ nóng `(1 - smooth(0.05, 0.85, u))·(0.82 + 0.06k)`;
- vỡ `smooth(0.42, 1, u)`: cung co 40%, tách xa 14%, quay thêm ±0,55 rad.

## 5. Kỹ thuật chính

**Vòng 3D nghiêng.** `_ring_pt`: `x = cx + d·(r·cosθ·SQ - LEAN·r·sinθ)`, `y = cy + r·sinθ`; `SQ = 0.44` (độ dẹt góc nhìn 3/4), `LEAN = 0.32`
(đầu vòng nghiêng về phía trước). θ = 0 hướng về trước và gần người xem; cung có giữa ở `cos θ ≥ 0` là nửa gần (`front`), còn lại là nửa xa
(`back`, màu tối).

**Nét bút thư pháp.** `_stroke` vẽ một cung từ θ0 tới θ1 thành đa giác: bề rộng `W·sin(πv)^0.55` (giữa béo, hai đầu nhọn), hẹp lại ở
phía xa (`0.45 + 0.55·near`), đầu cuối **cuộn vào trong** (`hook`: bán kính giảm 24% ở 30% cuối nét). `_segments(seed)` chia vòng thành
2-3 cung dài 1,5-2,5 rad, khe 0,22-0,45 rad, mỗi cung một chiều móc. Mỗi cung dài có 2 gai ngắn ở mép ngoài (`thorn`), quay về phía sau
chuyển động.

**Tô màu theo khoảng cách tới mép, nguội bằng cách bỏ màu nóng.** `fire_bands(pal, s, heat)`: các dải 1,4 / 3,4 / 6 / 8,6 / 11,5 px từ mép vào
là `tip`, `rim`, `body`, `light`, `core`, phần còn lại `white`. Khi `heat` giảm, màu nóng nhất bị bỏ trước (trắng, rồi vàng nhạt, rồi vàng),
nên phần dày của nét chuyển dần từ trắng sang cam. Nửa xa dùng `dark_bands` (đỏ sẫm).

**Tan bằng ăn mòn có nhiễu.** `paint(erode=8·smooth(0.55,1,u), noise=5·smooth(0.42,1,u))`: phần mảnh mất trước, nét tự vỡ thành móc và giọt.

**Một hình cho tia lõi + chớp.** Tia (`thorn`, p = 1,15), hai lưỡi lửa sát bên (p = 2,2, ngắn 55%), lõi `blob` và 17 gai hình nón cùng nằm
trong **một** mặt nạ, bo góc lõm (`fillet` 4): chớp và tia liền khối như vẽ tay. Gai mảnh (W 4) dài hơn gai béo, tạo nhịp.

**Lớp riêng cho mọi nét mờ.** `fxcore.Canvas` vẽ bằng ImageDraw nên **ghi đè** điểm ảnh, kể cả kênh alpha. Một nét alpha 0,3 vẽ thẳng lên
một vòng sáng sẽ đục thủng vòng. Mọi nét mờ (vệt, vòng áp suất, tia đạn, tia lửa, tàn lửa, quầng) được vẽ lên `_layer(c)` rồi `c.paste(...)`.
Hình tự do (`Shape.paint`) thì đã tự trộn alpha.

**Hướng và cỡ.** Mọi khoảng cách nhân `s`; `d = -1` lật hướng (nửa gần của vòng quanh nắm đấm cộng π, gai và mảnh cong theo `d`).
Với `s > 1` khung phải lớn theo: khoảng `(640, 400)·s`, neo `(60, 200)·s`. Bảng màu nào cũng dùng được: thiếu `tip`, `back` thì tự suy ra
từ `rim`.

## 6. Nhật ký lặp (lỗi gặp và cách sửa)

| Vòng | Thấy gì | Sửa |
|---|---|---|
| 1 | Vòng thành các mảnh hình lá rời, không đọc ra vòng; vòng quá hẹp | cung dài 1,5-2,5 rad thay vì 0,9-1,7; `SQ` 0,3 → 0,44 |
| 1 | Frame bùng nhỏ, gần như trống | tia lõi đã dài ngay frame đầu (`out_expo(3u + 0.4)`) |
| 1 | Vòng mới sinh trắng toàn bộ thành đốm trắng lạ | vòng dùng dải màu thật ngay từ đầu, chỉ chớp + tia được trắng toàn bộ |
| 1 | Tan quá sớm: 8 frame cuối gần trống | đời vòng dài hơn, `DUR` 0,9 → 0,78 s cho khớp |
| 2 | Lõi trắng ở nắm đấm biến mất | quầng `stepped_glow` vẽ SAU đã ghi đè lên hình: vẽ quầng trước, trên lớp riêng |
| 2 | Vòng tới cuối đứng yên rồi mờ | vị trí mũ 1,9 thay vì 2,4; bán kính cộng thêm `0.12·R1·u` |
| 3 | Chớp gai bị nuốt vào tia | 17 gai mảnh xòe hình nón (±24° tới ±142°), 4 gai rất mảnh và dài, `start` 0,85 |
| 4 (review) | Lật hướng `d = -1` sai nửa vòng; bảng màu chuẩn thiếu `tip` / `back` | cộng π cho nửa vòng, `bend·d`; tự suy màu thiếu |

## 7. Làm biến thể

- **Đổi màu**: `pal=ICE`, `pal=ARCANE`... (`_core/palettes.py`), không cần sửa code.
- **Mạnh hơn / yếu hơn**: thêm hoặc bớt dòng trong `INF_TIERS` (giữ luật: sinh trước thì đi xa, to và nhạt hơn), đổi số tia đạn.
- **Không phải lửa**: bỏ lớp 12 (tàn lửa), giữ vòng + tia, dùng bảng `LIGHTNING` hay `WIND`.
- **Áp cho đòn khác**: `_stroke` + `_segments` + `fire_bands` dùng được cho mọi vòng xung chấn (đá, chưởng, nện đất nhìn từ trên).
