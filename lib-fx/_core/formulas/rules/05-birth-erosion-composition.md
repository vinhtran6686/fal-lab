# 05. Lúc sinh, cách mép bị ăn, bố cục ở đỉnh

Số liệu: [data/shape_study_*.json](data/) (`python lib-fx/_tools/vectorfx.py study PROFILE`). Toạ độ chuẩn hoá theo khung bao của frame đỉnh:
`cx` 0 = trái → 1 = phải, `cy` 0 = trên → 1 = dưới. Px tính ở độ phân giải bản gốc. Chỉ xét **hình vẽ** (bỏ frame giữ).

## 1. Lúc sinh

| | Hình đầu tiên (diện tích / rộng / cao so với đỉnh) | Tâm hình đầu (cx, cy) | Đường đi tới đỉnh |
|---|---|---|---|
| lửa phun | 4% / 42% / 36% | 0,43 / 0,86 | rộng ra trước (75%) khi cao 71%, rồi cả hai tới 91% ở hình thứ 3; tâm đi lên 0,86 → 0,58 |
| Arcane | 46% / 64% / 38% | 0,48 / 0,81 | rộng **vượt** đỉnh (115%) ở hình 2 rồi thu lại, chiều cao lên dần 38 → 76 → 91 → 100% |
| Toxic | 10% / 21% / 39% | 0,55 / 0,77 | một mầm hẹp, cao; hình sau là đỉnh luôn (×10) |
| xoáy lửa | 44% / 74% / 47% | 0,30 / 0,34 | hình đầu ở phía **đuôi** nét chém, tâm chạy theo chiều quét 0,30 → 0,59 → 0,67 |
| xoáy băng | 46% / 70% / 43% | 0,41 / 0,21 | như xoáy lửa, 1 hình là tới đỉnh |

Luật:
- **Phun từ đất**: sinh ở **chân, giữa** (cy ≈ 0,8-0,86), hình đầu nhỏ (4-46% diện tích đỉnh). Bung **ngang trước, cao sau** (Arcane còn bung ngang
  quá tay rồi thu lại: một nhịp "bật" rất đặc trưng); tâm khối đi lên dần.
- **Xoáy chém**: hình đầu đã lớn (~45% đỉnh) vì nét chém xuất hiện cùng lúc với cú vung; nó **dài ra theo đường quét** (đầu nét chạy, đuôi đứng),
  không phình đều từ tâm.

## 2. Cách mép bị ăn khi mảnh co

| | Mất ở mép (trong 2 px) | Mất do lỗ mở / cắt sâu | Độ sâu mất mỗi hình | Lệch một phía (0 = đều) |
|---|---|---|---|---|
| lửa phun | **84%** | 16% | 0,9 px | 0,28 |
| Arcane | **86%** | 14% | 0,9 px | 0,15 |
| Toxic | 63% | 37% | 1,4 px | 0,15 |
| xoáy lửa | 50% | 50% | 2,1 px | 0,15 |
| xoáy băng | 44% | 56% | 2,4 px | 0,17 |

Luật:
- **Lửa, pha lê**: mảnh mòn **đều từ mép**, mỏng đi khoảng 1 px (ảnh gốc) mỗi hình vẽ, ít khi mở lỗ mới. Mảnh nhọn thì mũi ngắn lại, mảnh tròn thì
  nhỏ đi tại chỗ.
- **Khói độc, xoáy**: mòn mép **và** mở lỗ / cắt ngang gần như ngang nhau, mất sâu hơn (1,4-2,4 px): hình vỡ bằng các lỗ to dần và vết cắt, rồi
  tách thành mảnh.
- **Không hiệu ứng nào bị xoá từ một phía** (độ lệch 0,15-0,28): không quét mất theo một hướng, mà ăn quanh mép. Lửa lệch nhiều nhất (0,28): chân mòn
  chậm hơn đỉnh (lõi nóng ở chân).

## 3. Bố cục ở đỉnh (nhìn từ gốc phun)

| | Số lưỡi | Hướng các lưỡi (90° = thẳng lên) | Độ xoè | Dài các lưỡi (lưỡi dài nhất = 1) | Cỡ các mảnh (lớn nhất = 1) |
|---|---|---|---|---|---|
| lửa phun | 2 | 68°, 124° | 57° | 1 · 0,69 | 1 (một khối) |
| Arcane | 4 | 16°, 52°, 92°, 122° | 105° | 1 · 0,81 · 0,71 · 0,33 | 1 · 0,77 · 0,76 · 0,26 · 0,15 |
| Toxic | 5 | 8°, 44°, 80°, 116°, 172° | 165° | 1 · 0,91 · 0,90 · 0,68 · 0,59 | 1 · 0,51 · 0,43 · 0,21 · 0,09 |

Luật (phun từ đất):
- **2-5 lưỡi chính**, xoè 57-165°, cách nhau ~36° (Arcane, Toxic: các lưỡi cách đều ~36°); thường **lệch khỏi trục đứng** (lửa nghiêng phải 68°;
  Arcane có một mũi giữa đúng 92° làm điểm nhấn).
- **Thứ bậc độ dài**: lưỡi chính 1, các lưỡi sau 0,7-0,9, lưỡi phụ ngắn 0,3-0,6. Không có hai lưỡi giống hệt nhau.
- **Thứ bậc mảnh**: một khối chính, 2 khối vừa (0,4-0,8), vài mảnh nhỏ (< 0,25): luật "to / vừa / nhỏ" (Gilland) đo được.
- Xoáy chém nhìn từ tâm chỉ có 2 "lưỡi" (đầu và đuôi nét, xoè ~230-245°): bố cục của xoáy là **một nét dài**, chi tiết nằm ở mép trong (lưỡi lửa,
  lông vũ; xem `research/bezier-shapes/FINDINGS.md` §4).
