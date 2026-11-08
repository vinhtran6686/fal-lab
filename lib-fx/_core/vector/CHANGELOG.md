# CHANGELOG: lib-fx/_core/vector

## 1.8.1 (2026-11-09): docs

- `STATUS.md`: điểm nối giữa các session (đã làm, việc để dành, câu hỏi mở: slash theo quỹ đạo user vẽ cho một nhân vật, đánh giá khả thi).
- User chốt: 3 slash (xoay thường, xoay nặng, chém trước mặt) "ổn"; sáng tạo slash đơn bằng tool đã khá ổn.

## 1.8 (2026-11-09): chém trước mặt, docs theo loại VFX

- `gen_slash_loop`: kiểu `front-heavy` (`--style front-heavy`): một nhát vũ khí lớn trước mặt, chữ C hở ~230°, elip tròn hơn (k 0,42), không
  vòng qua sau lưng. Bản thường dày hơn (lưỡi 36 → 47), bản nặng +40% (70 → 98). Tham số elip, điểm bắt đầu, khung ảnh, sàn nay nằm trong `STYLES`.
  Kiểu `loop` / `loop-heavy` được gọi là "xoay tại chỗ" (spin).
- `foundation/vfx/`: docs theo từng loại VFX: `slash/` (`references.md` = 06-slash cũ, `generators.md`: 4 bộ sinh, luật, điểm chấm, việc còn
  thiếu để đạt 9-10/10), `explosion/` (nổ / phun: element-trio).

## 1.7 (2026-11-09): phản chiếu, khép vòng, bản vũ khí lớn

- `gen_render.render_sequence(..., reflection=dict(floor, squash, dim, sat, halo, opacity, tint, tint_mix))`: phản chiếu dưới sàn vẽ lại
  CÙNG các nét trong `frames.ReflectFrame` (lật qua sàn, dẹt ~1/4 như slash-trio), màu tối hơn và kéo về sắc chính (lớp sáng không hoá xám),
  glow yếu (`halo_w` theo lớp trong `compose.halo`), nét mảnh < ~2 px bị bỏ trong phản chiếu (tránh vụn chấm chấm).
- `gen_slash_loop`: vòng khép ở đỉnh (đầu nét chạy ≈ 378°), nét tóc phía sau ≥ ~2 px trên màn hình, răng khía cắn từ mép trong (không
  thành lỗ); kiểu `heavy` (`--style loop-heavy`: trọng kiếm, đại đao, katana hai tay): lưỡi ×2, ít sợi đậm, đầu nét 3 ngón cùn, vụn to,
  lấy đà và va chạm giữ 2 frame. Kết quả `showcase/generated/gen-slash-loop-blue/`, `gen-slash-loop-heavy-blue/`.

## 1.6 (2026-11-09): bộ sinh kiểu "loop"

- `gen_slash_loop.py` (lệnh `gen-slash NAME --style loop`): nhát chém ngang vòng quanh thân theo ý tưởng `ref/vfx/axe-swing-idea/reference.png`
  (chỉ lấy ý, không đồ). Elip phối cảnh, nhiều sợi (dải sáng, dải xanh, sợi tối, vệt tốc độ), đầu nét chổi khô, răng khía to ở nơi dải dày;
  sau đỉnh sợi giãn theo chiều dài rồi mới đứt, mỗi sợi đứt ở chỗ riêng. Chưa có phản chiếu.
  Kết quả `showcase/generated/gen-slash-loop-blue/`, trang https://claude.ai/artifact/2zSWrndFyafkCGZ6a328CM.
- `gen_render.py`: phần dựng chung cho bộ sinh (làm mịn, tô chồng, glow, xuất PNG / SVG / GIF / design.json).
- `frames.EllipseFrame` (elip phối cảnh: dẹt `k`, nghiêng `tilt`); `strokes.edges` thêm `wknots` (hệ số độ dày dọc nét) và `min_w`
  (nét tóc tối thiểu, đầu nét vẫn thon).

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

- Profile `slash-trio` (3 nhát chém + 3 phản chiếu dưới sàn), không cần thêm tính năng mới cho bộ tool; `foundation/06-slash.md` (nay là `foundation/vfx/slash/references.md`).

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
