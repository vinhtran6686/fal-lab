# CHANGELOG: lib-fx/_core/vector

## 1.5 (2026-11-09): bộ sinh đầu tiên

- `gen_slash.py` (lệnh `gen-slash`): sinh một nhát chém MỚI chỉ từ luật trong `foundation/` (lưỡi liềm nét thon, 2 lớp tô chồng, sinh từ đầu
  nét, bùng 2 hình, đầu nét chạy tiếp, vỡ thành mảnh cong hai đầu nhọn tại điểm cắt không đều, tia trôi theo hướng chém, glow giữ sáng,
  on twos cho tia). Bảng màu đo trên slash-trio: blue, pink, gold. Bản thử: nhát chém ngang xanh `showcase/generated/gen-slash-blue/`,
  trang https://claude.ai/artifact/WSPsgRkzRos6fW6BfDrsNM.

## 1.4 (2026-11-09): tự động hoá khâu đọc bản gốc

- `auto.py`: `propose_crops` (vùng hiệu ứng tách rời, gộp vùng cùng màu chồng nhau, tách phản chiếu dưới sàn theo khe hàng, đặt tên theo
  màu), `suggest_layers` (cụm màu trên 3 frame lớn nhất; loại glow bằng: pha với nền, độ biến thiên màu, độ sáng < 40% lớp sáng nhất; gộp màu
  gần thành đường màu), `mask_check` (điểm ảnh sáng không lớp nào nhận, gộp mọi frame; một màu chiếm > 40% = thiếu lớp), `init_profile`.
- Lệnh `init GIF NAME`, `check PROFILE`.

## 1.3 (2026-11-09)

- Profile `slash-trio` (3 nhát chém + 3 phản chiếu dưới sàn), không cần thêm tính năng mới cho bộ tool; `foundation/06-slash.md`.

## 1.2 (2026-11-08)

- `showcase/`: kết quả 5 hiệu ứng đã dựng (GIF so sánh, frame, SVG) nằm trong git; lệnh `showcase`.
- Lệnh `study` (`shape_study.py`): lúc sinh, cách mép bị ăn, bố cục lưỡi ở đỉnh; `foundation/05-birth-erosion-composition.md`.

## 1.1 (2026-11-08): nền tảng thiết kế

- Thư mục `foundation/`: phong cách (lớp, nét mịn, cấp bậc màu), hoạt hoạ (vòng đời + theo dõi từng mảnh), cách đọc bản gốc (12 bẫy đã gặp),
  đặc tả bộ sinh; số liệu trong `foundation/data/`.
- Lệnh `track` (`tracking.py`): theo dõi từng mảnh giữa các hình vẽ (lớn, tách, co, trôi, chết).

## 1.0 (2026-11-08): bản chốt sau bài test element-trio

- Glow mô hình `blur`: bản làm nhoè của hình (2 gauss, màu đo được) × độ mạnh đo từng frame (glow tắt dần ở pha tàn).
- Lớp theo độ đục (`alpha`) + độ đục từng frame (`opacity`): màn trong mờ, mảnh vỡ mờ dần.
- Lớp tối trong mờ (`darker_than_bg`).
- `source.scale` (phóng to GIF nhỏ khi ingest); khung toạ độ đặt riêng từng biến thể; khung thẳng có `edge_bias` mặc định chuẩn.
- Luật đo: gradient và glow hẹp hơn 1,5 px ảnh gốc là khử răng cưa / vệt phóng to, bị loại; gradient s ≥ 25 px là lớp phẳng.
- Khớp nét tính điểm từng mảnh tăng dần (nhanh hơn ~10 lần ở frame vỡ vụn).
- `palette` thêm gom cụm màu k-means; lệnh mới `lifecycle` (vòng đời: pha, diện tích, số mảnh, frame giữ).
- Trang review tiếng Việt. README viết lại: phạm vi, tính năng, hiệu ứng đã kiểm chứng, cách designer vẽ, lộ trình.
- Profile: `swirl-slash`, `element-trio` (fire, arcane, toxic).

## 0.1 (2026-11-08): đóng gói từ research/bezier-shapes

- Pipeline đo → khớp nét thon → Smooth & Simplify → tô chồng → review; profile JSON; CLI `vectorfx.py`; khung cực và thẳng.
- Tái hiện `swirl-slash` v3 (IoU lệch trung bình +0,002, 0 điểm gãy).
