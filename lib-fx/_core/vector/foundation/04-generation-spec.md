# 04. Đặc tả bộ sinh hiệu ứng mới (bản nháp, 2026-11-08)

Mục tiêu: sinh một hiệu ứng **chưa từng có bản gốc** nhưng đúng ngôn ngữ của các designer đã phân tích (01, 02), xuất qua cùng đường ống
`smooth_simplify` + `compose` nên nét và màu đã đạt chất lượng 9-10/10.

## 1. Đầu vào của bộ sinh

```
archetype : "eruption" (phun từ đất, khung thẳng) | "swirl" (xoáy chém, khung cực)      # mới có 2 dạng được đo
palette   : kiểu 1 thang một họ màu (3-4 tông, bước độ sáng ~50-65)
            | kiểu 2 lõi sáng + bóng tối trong mờ | kiểu 3 hai sắc cùng độ sáng + màn mờ                    # 01 §3
size      : khung kích thước (cao / rộng px), frames tổng, fps
energy    : ngắn-mạnh (va chạm: r ≈ 0,35-0,55) | cháy lâu (r ≈ 0,8)                                         # 02 §1
seed
```

## 2. Các bước sinh

1. **Khung**: khung thẳng (gốc ở chân, trục lên) hoặc khung cực (tâm, chiều quét).
2. **Hình chính theo thời gian**: diện tích A(t) và khung bao theo công thức 02 §5. Hình là các **nét thon** (`strokes.py`): thân + lưỡi + vết khoét,
   tham số trong khoảng đã đo (`research/bezier-shapes/FINDINGS.md` §4: lưỡi dài ≈ 2,4 lần rộng, cạnh lồi; lông vũ hai đầu nhọn; chi tiết liền nhau
   chênh 2-5 lần, khoảng cách không đều).
3. **Lớp màu**: lớp sáng nhất ở lõi / gốc (sâu nhất trong khối), các lớp tối hơn ra mép và đuôi; tô chồng, lớp dưới chạy dưới lớp trên 10 px.
4. **Pha tàn bằng mảnh**: từ đỉnh, mỗi hình vẽ: mỗi mảnh co ×0,3-0,85 (mòn từ mép và lỗ mở rộng, không thu về tâm); 25-50% mảnh sứt ra 1-2
   mảnh nhỏ; mảnh đứng yên (lửa: thêm tàn bay lên); mảnh < 10-30 px thì chết; khung bao sụp ở 3-4 frame cuối.
5. **Ánh sáng**: glow = làm nhoè hình × gain (1 tới ~55-60% đời, tắt trước kết thúc); lớp sáng mờ dần 1 → ~0,6 ở 30% cuối; lớp nóng tan trước.
6. **Nhịp**: on ones tới ~60-70% đời, sau đó on twos.
7. **Làm mịn và tô**: `smooth_simplify` cho mọi lớp mọi frame, `compose` (gradient mép, glow, độ đục), xuất PNG + SVG + review.

## 3. Đã đủ gì, còn thiếu gì

| Phần | Trạng thái |
|---|---|
| Đơn vị hình, khoảng tham số | có (đo trên xoáy chém) |
| Màu, lớp, glow, độ đục, gradient | có (5 hiệu ứng) |
| Đường cong vòng đời, luật mảnh (co, sứt, chết, đứng yên) | có, ở mức thống kê (5 hiệu ứng) |
| Làm mịn nét, tô, xuất, review | có (v1.0) |
| **Hình dạng ở pha bùng** (hình nhỏ đầu tiên trông thế nào, bung theo hướng nào) | chưa đo riêng: cần theo dõi hình chính qua 1-4 frame đầu |
| **Cách mép bị "ăn" khi mảnh co** (mòn đều, mòn từ một phía, lỗ mở) | mới quan sát bằng mắt; cần đo trên dữ liệu theo dõi |
| **Tính liên tục giữa các frame** (cùng một nét qua nhiều frame, không rung) | chưa làm (bộ dựng hiện khớp từng frame độc lập) |
| Dạng khác: nổ tròn, đạn bay, aura lặp, buff | chưa có mẫu: cần 2-3 GIF mỗi dạng |

## 4. Kế hoạch đề xuất

1. G1b: đo pha bùng và cách mép bị ăn trên 5 hiệu ứng (dữ liệu sẵn có).
2. G2: bộ sinh `eruption` (3 mẫu: lửa, Arcane, Toxic) → sinh 2-3 hiệu ứng mới (vd. phun băng, phun điện) đặt cạnh bản gốc, user chấm.
3. G3: bộ sinh `swirl` (2 mẫu).
4. Mỗi dạng mới: 2-3 GIF tham khảo → dựng lại (bộ tool v1.0) → `lifecycle` + `track` → cập nhật 01-04 → mở bộ sinh cho dạng đó.
