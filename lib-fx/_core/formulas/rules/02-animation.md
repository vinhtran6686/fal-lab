# 02. Hoạt hoạ: hình nhỏ → bùng → đỉnh → co và vỡ từng mảnh → mất

Số liệu: [data/lifecycle_*.json](data/) (`vectorfx.py lifecycle`: diện tích, số mảnh, mảnh lớn nhất, khung bao, frame giữ) và
[data/tracking_*.json](data/) (`vectorfx.py track`: theo dõi từng mảnh giữa hai **hình vẽ** liên tiếp, bỏ qua frame giữ; mỗi mảnh ở frame sau
thuộc về một mảnh mẹ chồng lấn nhiều nhất). Diện tích tính ở px bản gốc, GIF 25 fps.

## 1. Bốn pha

| | xoáy lửa | xoáy băng | lửa phun | Arcane | Toxic |
|---|---|---|---|---|---|
| Hình đầu tiên | 31 700 px (frame 2) | 25 600 | **357** | 3 500 | 938 |
| Bùng tới đỉnh | 2 frame | 1 | 3 | 4 | 1 |
| Diện tích đỉnh | 72 300 | 55 100 | 8 500 | 7 700 | 9 600 |
| Đỉnh → bắt đầu vỡ | 1 frame | 1 | 3 | 0 | 0 |
| Diện tích còn lại mỗi frame sau đỉnh | 0,50 | 0,36 | 0,81 | 0,55 | 0,55 |
| Đời (tới < 2% đỉnh) | 7 frame | 6 | 21 | 12 | 9 |
| Số mảnh nhiều nhất | 10 | 5 | 36 | 76 | 23 |
| Bắt đầu vẽ "on twos" | frame 10 | — | 14 | 8 | 10 |

1. **Sinh**: một hình nhỏ ở gốc hiệu ứng (chân lửa, tâm xoáy). Với hiệu ứng dài (lửa) hình đầu tiên rất nhỏ (357 px = 4% đỉnh).
2. **Bùng**: rất nhanh, 1-4 frame; mỗi mảnh to lên **×1,5 tới ×9 mỗi hình vẽ** (trung vị theo dõi: xoáy 1,5-2,2, lửa 8,6, Toxic 6,9). Hình bung tới
   đúng **khung kích thước** của loại hiệu ứng (lửa cao ~190 px, xoáy ~500 px) rồi giữ khung đó.
3. **Đỉnh**: 0-3 frame. Hiệu ứng ngắn (va chạm, xoáy) gần như không giữ đỉnh; hiệu ứng dài (lửa) giữ 2-3 frame.
4. **Tàn**: chiếm phần lớn đời hiệu ứng (lửa: 18 / 21 frame). Diện tích giảm theo **tỉ lệ cố định mỗi frame** (hàm mũ): 0,36-0,55 với hiệu ứng ngắn,
   0,81 với lửa cháy lâu.

## 2. Pha tàn nhìn từ từng mảnh (theo dõi)

| Sau đỉnh, mỗi hình vẽ | xoáy lửa | xoáy băng | lửa phun | Arcane | Toxic |
|---|---|---|---|---|---|
| Mảnh lớn (≥ 100 px) còn lại (trung vị) | 0,30 | 0,29 | 0,83 | 0,47 | 0,49 |
| Tỉ lệ mảnh tách ra | 50% | 50% | 24% | 28% | 32% |
| Số mảnh con khi tách (trung vị) | 2 | 2,5 | 2 | 3 | 3 |
| Mảnh con lớn nhất giữ (trung vị) | 75% | 98% | 85% | 82% | 67% |
| Diện tích lúc biến mất (trung vị) | 29 px | 32 | 8 | 11 | 18 |
| Dịch chuyển dọc (trung vị, px / hình) | +1,6 | +19,5 | 0 | −1,4 | −2,7 |
| Mảnh mới sinh sau đỉnh | 1 | 0 | 11 (tàn bay) | 1 | 3 |

Kết luận:
- **Mỗi mảnh co lại ở mỗi hình vẽ** (đúng như user quan sát: "giảm từng hình lại"): còn ~30% (xoáy), ~50% (Arcane, Toxic), ~83% (lửa cháy chậm).
- **Vỡ = sứt mảnh nhỏ**, không phải chẻ đôi: khi tách, mảnh lớn nhất giữ 67-98%, còn lại là 1-2 mảnh vụn nhỏ. Toxic tách đều nhất (67%).
- **Mảnh đứng tại chỗ**, gần như không bay (0-3 px / hình). Ngoại lệ: xoáy băng trôi theo hướng chém (+19 px), lửa có ~11 tàn sinh thêm và bay lên.
- **Mảnh chết khi đã thành đốm** (8-30 px), không tắt đột ngột khi còn to.
- **Khung bao giữ nguyên tới cuối**: lửa cao ~190 px từ frame 9 tới 16 trong khi diện tích giảm 4 lần; chỉ 3-4 frame cuối khung mới sụp về chân
  (190 → 97 px). Vì vậy "nhỏ dần" là **mòn và vỡ tại chỗ**, không phải thu nhỏ cả hình về tâm.

## 3. Nhịp vẽ

- Pha bùng và đỉnh: **mỗi frame một hình** ("on ones", 25 hình/giây): va chạm cần mượt.
- Phần sau của pha tàn (từ ~60-70% đời): **mỗi hình giữ 2 frame** ("on twos", 12,5 hình/giây): tan rã cho phép giật nhẹ, tiết kiệm hình vẽ.
- Xoáy băng (rất ngắn, 6 frame) không có frame giữ.

## 4. Ánh sáng theo thời gian

| Thứ | Luật | Số đo |
|---|---|---|
| Glow | là bản làm nhoè của hình; độ mạnh giữ ở đỉnh rồi **tắt trước khi hình tan hết** | lửa: 1 tới frame 12, 0,5 ở 15-16, 0,18 ở 17-18, 0 từ 19 (hình còn tới 22) |
| Độ đục | lớp mờ dần ở pha tàn | Arcane tím nhạt: 1 tới frame 8, rồi 0,89 → 0,75 → 0,64 → 0,59 |
| Màn trong mờ | độ đục cố định suốt đời | Arcane: 0,41-0,48 |
| Lớp nóng | tan trước | xoáy: vàng hết trước hồng, hồng trước đỏ sẫm; lửa: lõi vàng ở chân lại lâu nhất (nằm ở gốc) |

## 5. Công thức tóm tắt cho một hiệu ứng (dùng cho bộ sinh, xem 04)

```
t_birth = 0; t_peak = 1..4; t_break = t_peak + 0..3; t_end = t_peak + 5..18
A(t)  : A0 = 4-45 % A_peak, tăng ×1,5-×9 mỗi hình tới A_peak; sau t_break A(t+1) = r·A(t), r = 0,35-0,55 (ngắn) | 0,8 (cháy lâu)
khung : bung tới kích thước loại hiệu ứng trong pha bùng, giữ tới 3-4 frame cuối, rồi sụp về gốc
mảnh  : mỗi hình vẽ sau đỉnh, ~25-50 % mảnh sứt ra 1-2 mảnh nhỏ (mảnh chính giữ 70-85 %); mỗi mảnh co ×0,3-0,85; chết khi < ~10-30 px
nhịp  : on ones tới ~60-70 % đời, sau đó on twos
glow  : gain 1 tới ~55-60 % đời, tắt hẳn trước t_end vài frame; độ đục lớp sáng 1 → ~0,6 ở 30 % cuối
```
