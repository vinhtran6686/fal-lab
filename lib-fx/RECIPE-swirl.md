# Công thức: Xoáy chém lửa / Xoáy chém băng (`melee/blade/swirl_fire`, `swirl_frost`)

Dựng lại từ một GIF tham khảo user gửi (1920x1080, 38 frame, 25 fps, 1,52 s). GIF có **hai biến thể** cạnh nhau trên nền tối:
lửa hồng-vàng bên phải, băng trắng-xanh bên trái.
- Nghiên cứu bằng `_tools/study_ref.py --bg median`, kết quả ở `_study/ref01/`, không commit.
- Phương pháp dựng và bộ luật: [SHAPE-RULES.md](SHAPE-RULES.md).
- Code: `melee/blade/blade.py` (trên `_core/fieldfx.py`).

```
python lib-fx/build.py melee/blade        # 380x380 @2x, neo ở tâm, 30 fps; swirl_fire 13 frame, swirl_frost 30 frame
```

## 1. Phân tích (2026-11-07): số lớp, màu từng lớp, hình từng lớp

**Cách đo.** GIF dùng bảng màu cố định, nên mỗi mảng tô phẳng trong bản gốc là đúng một mã màu. Mình làm ba việc:
- Đếm số điểm ảnh của từng mã màu qua từng frame: mã nào có nhiều điểm ảnh là một lớp tô phẳng.
- Dựng mặt nạ cho từng màu ứng viên trên từng frame, để thấy hình của mỗi lớp.
- Lấy mẫu màu thật ở vùng phẳng. Bảng màu k-means bị lẫn quầng sáng với nền, không dùng được.

Các vành tối mà k-means bắt được (lửa: 179,38,79 / 155,37,70 / 128,34,59 / 103,31,49) chỉ là **đường đồng mức của quầng sáng**,
không phải lớp vẽ.

### 1.1 Biến thể lửa: 4 lớp tô phẳng + quầng sáng

| Lớp | Màu | Hình | Số điểm ảnh theo frame (f2 → f9) | Vai trò |
|---|---|---|---|---|
| Vàng | 255,214,112 | phần mới vẽ, nằm phía mép ngoài, đầu nét tù; ranh giới phía trong là răng cưa | 2.0k, **15.5k**, 10.5k, 6.1k, 0, 0 | nóng nhất, mất đầu tiên (hết ở f6) |
| Hổ phách | 254,172,76 | **viền mỏng** chạy quanh vùng vàng, chỗ chuyển sang hồng | đi theo vàng | lớp chuyển, rất mỏng |
| Hồng | 255,98,140 | phía mép trong; ở đuôi phủ hết bề rộng; lưỡi liếm dài chĩa ngược chiều quét vào vùng vàng | 7.2k, 9.1k, **16.9k**, 13.2k, 10.7k, 4.1k, 0.6k | nguội vừa, hết ở f8 |
| Đỏ hồng sẫm | 209,47,87 | sâu nhất phía trong, cả đuôi mũi kim; sau đó thành **các móc nhọn rời nhau** | 11.0k, 20.2k, **30.6k**, 23.7k, 9.8k, 4.5k, 2.0k, 0.65k | nguội nhất, còn lâu nhất (tới f13) |
| Quầng sáng | hồng → đỏ sẫm | phủ quanh hình và cả lòng xoắn | mạnh nhất f3-f5 | tạo độ "phát sáng" |

Hình tổng thể:
- f2: lưỡi liềm mảnh ở trên bên trái, đuôi là mũi kim dài.
- f3: quét qua đỉnh xuống bên phải.
- f4-f5: đầu cuộn vào tâm thành xoắn ốc, đầu tù màu vàng.
- f6: vỡ thành 4 mảnh khác cỡ: một móc lớn ở tâm, một cung dài bên phải, hai mảnh mảnh ở trên.
- f7-f13: các mảnh mỏng dần thành móc nhọn rồi thành vụn.

### 1.2 Biến thể băng: 4 lớp tô phẳng + bóng mờ + vết nứt + quầng sáng

| Lớp | Màu | Hình | Số điểm ảnh (f2 → f8) | Vai trò |
|---|---|---|---|---|
| Trắng băng | 239,255,255 | lõi lưỡi liềm, lệch về mép ngoài và phần đầu; đầu nhọn móc xuống | 10.8k, **24.3k**, 13.9k, 4.0k, 0.4k, 0.2k, 0 | nóng nhất, mất đầu tiên |
| Cyan nhạt | 105,231,254 | các mảng hình **lông vũ** dài nằm trong vùng trắng, chĩa ngược chiều quét | nhỏ, f3-f6 | vân bên trong |
| Xanh | 59,169,226 | bao quanh vùng trắng, dày ở đuôi và mép trong | 4.7k, 11.5k, **15.9k**, 9.5k, 3.7k, 1.2k, 0.4k | nguội vừa |
| Xanh sẫm | 30,109,157 | viền mỏng ngoài cùng, các mảnh vỡ cuối | mỏng | nguội nhất |
| Bóng mờ | xanh đậm trong mờ | bản sao to hơn của nét, trễ một nhịp | rõ ở f4-f8 | dấu vết vệt chém |
| Vết nứt | xanh, lõi cyan | vài đoạn thẳng mảnh, 2 cụm, có chấm ở đầu | f5 → ~f22 | lớp còn lại lâu nhất |

### 1.3 Có vẽ lại được bằng code không?

**Được**, và theo một cách chung, không phải vẽ tay từng hình (SHAPE-RULES.md):
- Vì các lớp **lồng nhau**, **ranh giới liền mạch** và **tầng nóng mất trước**, cả hiệu ứng là một trường nhiệt duy nhất được cắt
  bằng 4 ngưỡng.
- Răng cưa, lông vũ, mảnh vỡ hình móc và lỗ thủng đều sinh ra từ trường đó (kết cấu sawtooth nghiêng + khe vỡ chữ V), không phải
  vẽ từng mảnh.

## 2. Thông số đã dùng

**Chung cho cả hai:**
- Đầu nét: `TH0 + 330°·k·(1-(1-t/0,16)^1.6)`, bắt đầu ở trên bên trái (`TH0 = 180° + 20°`).
- Tuổi từng điểm: `time_at(θ)`, phép đảo ngược của hàm quét.
- Bán kính: dao động `1 + 0,07·sin(3θ)`, cuộn vào tâm ở 30% cuối.

| | Lửa | Băng |
|---|---|---|
| Bán kính, bề rộng, độ cuộn | 110, 74, 0,7 | 106, 80, 0,35; quét 90% (lưỡi liềm) |
| Profile bề rộng | `v^0.75·(1-v^10)^0.3` + mũi kim ở đuôi | `v^0.7·(1-v^8)^0.35` |
| Trường | `0.6·tuổi + 0.7·ngang + 0.36·lưỡi liếm` | `0.55·tuổi + 0.55·ngang + 0.4·lông vũ` |
| Kết cấu | `saw(v·(8.5±2.5) + 1.3·C)`, nghiêng ngược chiều quét | `saw(v·(3.4±0.9) + 1.1·w)` |
| Ngưỡng → màu | 0,12 đỏ sẫm · 0,36 hồng · 0,62 hổ phách · 0,67 vàng | 0,06 xanh sẫm · 0,16 xanh · 0,42 cyan · 0,6 trắng |
| Nguội | `1.2·smooth(0.1, 0.46)` | `0.95·smooth(0.06, 0.5)` |
| Vỡ | khe chữ V, 3,4 khe dọc nét, từ 0,12 s | 2,6 khe, từ 0,14 s |
| Quầng bậc thang | 15 / 9 / 4 px | 14 / 8 / 3 px |

Bản gốc không có nhịp báo trước; mình giữ đúng như vậy (ngoại lệ có chủ ý so với DESIGN.md §1).

## 3. Nhật ký

| Vòng | Cách làm | Kết quả |
|---|---|---|
| 1-5 (2026-11-06) | vẽ từng lớp bằng hình riêng (dải, lưỡi liếm, mảnh vỡ) + quầng mờ Gaussian | user: chưa mượt, chưa rõ, nét chưa liền như bản gốc; có gradient |
| 6 (2026-11-07) | phân tích lớp bằng đếm mã màu; chuyển sang trường nhiệt cắt tầng; quầng bậc thang; bóng mờ phẳng | các tầng liền mạch, không gradient, vỡ thành mảnh nhọn tự nhiên |

**Còn khác bản gốc:**
- Phần móc ở tâm bản lửa gốc to và vàng hơn.
- Răng cưa bản gốc ít mà dài hơn ở cung trên.
- Bản băng gốc hình gọn hơn, đầu móc sắc hơn.
- Vết nứt bản gốc có nhiều nhánh hơn.
