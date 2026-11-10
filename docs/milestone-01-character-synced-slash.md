# Milestone 01: Character-Synchronized Slash

Ghi ngày 2026-11-10 từ phản hồi của chuyên gia (Technical Advisor) sau khi đọc gói khảo sát `project-discovery.zip`. Đây là **quyết định hướng đi
hiện tại**; trạng thái thực hiện ghi ở cuối file và trong `lib-fx/_core/vector/STATUS.md`.

## 1. Kết luận của chuyên gia

- Team đã đủ năng lực để làm một **skill hoàn chỉnh ở mức asset**. Thứ còn thiếu là **nối đúng các năng lực đã có** và kiểm chứng bằng một sản phẩm
  thật, không phải thêm tính năng.
- **fal-image**: đủ dùng, không phát triển thêm lúc này (giới hạn cần nhớ: độ dài vũ khí trôi giữa pose, chưa đổi vũ khí khoá ngoại hình, chuỗi pha
  chưa ổn định, chưa có kiểm tra nhất quán tự động).
- **video-sprite**: đủ để làm animation thử nghiệm; **chưa yêu cầu nó làm vũ đạo chính xác từng frame** (chỉ nhận ảnh đầu, ảnh cuối, lời tả, thời lượng;
  có thể tự vẽ vệt chém dính thân).
- **VFX**: Vector Kit là năng lực mạnh nhất (kiểm soát hình). Ba nhánh giữ đúng vai trò, **không gộp code**, **không tạo nhánh thứ tư**:
  - A. Vector Kit: tái tạo và sáng tạo slash.
  - B. Procedural Library: hiệu ứng hình học và các loại khác.
  - C. Character FX: ghép hiệu ứng vào nhân vật.

  Khi cần phối hợp thì thiết kế cách trao đổi dữ liệu.
- **Tiền lệ đáng giá**: `holy_commander` skill `radiant_slash` (thân từ video-sprite, fx tách 2 lớp back / front, khớp frame, có pivot và meta). Khoảng
  trống: fx đó viết bằng Python riêng, **chưa nối Vector Kit với quy trình ghép nhân vật đã chạy**.

## 2. Bốn điểm nghẽn (không giải quyết cùng lúc)

1. **Chưa có cầu nối chuyển động nhân vật → chuyển động VFX.** Hiện `dummy.py` suy vị trí vũ khí **từ** nhát chém (VFX điều khiển hình nộm). Mục
   tiêu: animation nhân vật → quỹ đạo vũ khí → bộ sinh VFX → nhát chém theo chuyển động thật.
2. **Hệ toạ độ và thời gian chưa đồng nhất** (sprite px cell 176×140, pivot 0,5 / 0,88, 15 fps; fx_layers theo H, y lên; Vector Kit px, y xuống; procedural
   px @2x; combo H = 170). Chưa cần hệ toàn cục; **mỗi thử nghiệm phải có quy ước chung riêng**: chuẩn hoá theo **chiều cao nhân vật H** và **thời gian ms**,
   đổi sang px / frame khi render.
3. **VFX chưa kiểm chứng ở cỡ game.** Từ nay **bắt buộc review VFX ở H = 60 px @1x** (không chỉ ở khung phóng lớn 600-1100 px).
4. **Ba nhánh VFX chưa trao đổi dữ liệu trực tiếp.** Không refactor ngay; sau này có thể dùng chung một định dạng mô tả asset / composition khi có nhu cầu thật.

## 3. Hai workflow

- **Character-first** được chọn cho thử nghiệm tích hợp quỹ đạo vũ khí đầu tiên: thấy chuyển động thật trước rồi chỉnh VFX khớp theo; video-sprite
  không nhận được quỹ đạo VFX nên VFX-first phải "hy vọng" model làm đúng.
- **VFX-first** vẫn dùng cho hiệu ứng độc lập (ma thuật, vòng năng lượng, slash phi vật lý, visual mới). Hai workflow cùng tồn tại.

## 4. Milestone 01: một nhát chém xéo có VFX riêng, đồng bộ với kiếm của nhân vật thật

Tài nguyên: `holy_commander` master v07 (không tạo master mới); fal-image (2 pose); video-sprite (1 animation); Vector Kit (slash từ quỹ đạo kiếm);
Character FX (ghép back / front như `radiant_slash`).

| Bước | Việc | Ghi chú |
|---|---|---|
| 1. Choreography | fal-image: 2 pose (chuẩn bị, kết thúc đòn chém xéo) theo master; video-sprite: **một** animation "diagonal downward slash" | nhân vật và kiếm thấy rõ; **không có vệt / hiệu ứng do model vẽ dính thân** |
| 2. Quỹ đạo vũ khí | chọn vài frame quan trọng, **đánh dấu tay** Blade Root, Blade Tip, timestamp → một chuỗi dữ liệu chuyển động đơn giản | chưa cần tự động dò |
| 3. VFX | đưa dữ liệu vào Vector Kit; **thử khớp cung elip hiện có trước**, chỉ khi không đủ chính xác mới thêm đường cong tự do; chỉnh length, width, curvature, taper, opacity, lifetime, glow | |
| 4. Ghép | ghép VFX vào animation thật; preview ở **H = 60 px @1x, 15 fps**, giữ pivot và cell của nhân vật, **VFX tách khỏi body** | |
| 5. Đánh giá | một GIF hoàn chỉnh: nhân vật chém, hiệu ứng đi theo đường kiếm | |

**Tiêu chí đạt (6):**
1. Nhân vật thực hiện một đòn chém xéo rõ ràng.
2. VFX không dính cứng vào hình nhân vật.
3. Đường chém đúng hướng và quỹ đạo vũ khí.
4. Chỉnh được độ dày, chiều dài, độ cong độc lập.
5. Hiệu ứng vẫn đọc được ở H = 60 px.
6. Xuất và tái sử dụng được VFX.

**Chưa làm:** tự động tracking, Timeline Editor tổng quát, Composition Editor hoàn chỉnh. Nếu không đạt: xác định chính xác phần nào hỏng rồi đổi cách
tiếp cận; **không xây tiếp các tầng phía trên**. Trước khi giao implementation, chuyên gia chỉ cần **các module liên quan trực tiếp** tới milestone
(không audit lại cả repo).

## 5. North Star (giữ nguyên; là năng lực cần phát triển, không phải danh sách task)

| # | Năng lực | Hiện trạng (theo chuyên gia) |
|---|---|---|
| 1 | Reference Reconstruction | đã có nền tảng |
| 2 | Parametric Shape Generator | đã có nền tảng |
| 3 | Motion-driven VFX | chưa hoàn thiện |
| 4 | Lifecycle & Impact | cần mở rộng |
| 5 | VFX Composition | prototype |
| 6 | Character Integration | đã có tích hợp riêng lẻ |
| 7 | Reusable Skill Assets | mục tiêu dài hạn |

## 6. Trạng thái

- 2026-11-10: ghi quyết định. **Chưa bắt đầu**: bước 1 tốn tiền (ảnh ~0,0135 USD/ảnh; clip h3-max-turbo ~0,062 USD/clip theo `out/costs.csv`), cần
  user đồng ý trước khi chạy clip (quy tắc chi phí trong `CLAUDE.md`).
