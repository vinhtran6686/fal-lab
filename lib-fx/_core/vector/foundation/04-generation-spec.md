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
| Hình ở pha bùng, cách mép bị ăn, bố cục lưỡi ở đỉnh | có (05) |
| **Vẽ chuyển tiếp giữa các khung chính** (ghép nét giữa hai khung, nội suy tham số theo đường cong thời gian, mảnh tách ra từ đâu) | **chưa có: thiếu lớn nhất** |
| Thành phần phụ (tàn bay, vòng sáng dưới đất, tia) | chưa có luật (số lượng, thời điểm, quỹ đạo) |
| Bộ kiểm tra phong cách cho hiệu ứng không có bản gốc (so với các khoảng đo trong foundation) | chưa có |
| Mẫu "đề bài thiết kế" (nguyên tố, cảm giác, cỡ, thời lượng, frame va chạm, kiểu phối màu) | nháp ở §1 |
| **Tính liên tục giữa các frame** (cùng một nét qua nhiều frame, không rung) | chưa làm (bộ dựng hiện khớp từng frame độc lập) |
| Dạng khác: nổ tròn, đạn bay, aura lặp, buff | chưa có mẫu: cần 2-3 GIF mỗi dạng |

## 3b. Bộ sinh đã có

- `gen_slash.py` v0 (2026-11-09): dạng chém. Các khung chính được viết dưới dạng **tham số nét theo hình vẽ** (đầu / đuôi nét, độ dày, độ
  rộng vết cắt, lỗ), nên các frame ở giữa liền mạch theo cấu tạo, không cần ghép nét giữa hai ảnh. Số đo của bản thử nằm trong khoảng đo
  (hình đầu 7%, bùng ×7,5, sau đỉnh còn 0,27-0,50 mỗi hình, 9 mảnh, 0 điểm gãy). Chưa tốt: tách mảnh ngay sau đỉnh hơi sớm; chưa có phản chiếu.
- `gen_slash_loop.py` v1 (2026-11-09, `--style loop`): chém ngang vòng quanh thân trên `EllipseFrame`. Luật thêm sau lần chấm v0 = 7/10 ("nét
  quá đơn giản"): một nhát chém là **nhiều sợi** (dải sáng + dải giữa + sợi tối + vệt tốc độ), đầu nét chổi khô 3-4 ngón dài ngắn khác nhau,
  độ dày theo phối cảnh (sau ×0,3, trước ×2,4, nét tóc ≥ 2 px); sau đỉnh sợi **giãn** trước khi **đứt**, mỗi sợi đứt ở chỗ riêng; răng khía chỉ
  ở nơi dải dày (trên nét tóc chúng cắt vụn nét).

## 4. Kế hoạch đề xuất

1. G1b: đo pha bùng, cách mép bị ăn, bố cục (xong: 05).
1b. Vẽ chuyển tiếp: lấy 3-4 khung chính của lửa phun, cho bộ tool tự vẽ các frame giữa, đặt cạnh bản gốc; đạt khi user chấm 8-9/10.
2. G2: bộ sinh `eruption` (3 mẫu: lửa, Arcane, Toxic) → sinh 2-3 hiệu ứng mới (vd. phun băng, phun điện) đặt cạnh bản gốc, user chấm.
3. G3: bộ sinh `swirl` (2 mẫu).
4. Mỗi dạng mới: 2-3 GIF tham khảo → dựng lại (bộ tool v1.0) → `lifecycle` + `track` → cập nhật 01-04 → mở bộ sinh cho dạng đó.
