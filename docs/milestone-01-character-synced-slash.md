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

### 1b. Đánh giá phối hợp (bảng của chuyên gia)

| Tích hợp | Hiện trạng |
|---|---|
| fal-image → video-sprite | đã kiểm chứng |
| video-sprite → quỹ đạo vũ khí | chưa có dữ liệu |
| quỹ đạo vũ khí → VFX | chưa hỗ trợ |
| VFX → xem cùng nhân vật | mới có prototype (hình nộm) / FX riêng |
| nhân vật + VFX → skill | đã làm thủ công (radiant_slash) |

Thư viện procedural: 19 hiệu ứng, 1 duyệt, 16 nháp, 2 cần làm lại; là thư viện bổ trợ, không phải nhánh tập trung.

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
| Tiêu chí | VFX-first | Character-first |
|---|---|---|
| Kiểm soát hình VFX | tốt | tốt |
| Kiểm soát vũ đạo | thấp | phụ thuộc model video |
| Biết trước đường đi vũ khí | có, từ thiết kế VFX | phải lấy từ animation |
| Đồng bộ chính xác | chưa chứng minh | chỉnh được sau khi có clip |
| Tạo lại biến thể | tốt | tốt khi đã có dữ liệu chuyển động |

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

## 6. Các tài liệu đã cập nhật theo quyết định này

| File | Cập nhật |
|---|---|
| `lib-fx/_core/vector/STATUS.md` | §0 hướng đi hiện tại; §3.1, §3.1b gộp vào Milestone 01; §3.2 không refactor, không gộp code, không nhánh thứ tư |
| `lib-fx/_core/vector/foundation/vfx/slash/ARCHITECTURE.md` | §2: cách làm trước bằng Milestone 01 (đánh dấu tay root + tip + timestamp, cung elip trước, đơn vị H + ms); dữ liệu vào thêm Blade Root |
| `lib-fx/MINDSET.md` | Phase 2-3 theo hướng Character-first; North Star 7 năng lực; §6.3 không gộp code; quy ước review ở H = 60 px |
| `lib-fx/_core/vector/foundation/vfx/slash/README.md` | luật review ở cỡ game |
| `CLAUDE.md` | trỏ tới file này và luật H = 60 px |

## 7. Trạng thái

- 2026-11-10: **Milestone 01 xuất xong** (chờ user chấm tiêu chí 5 bằng mắt). Body `attack_diag_side` (16 hình, hit 13) + fx `frames/fx/slash_diag/`
  (lớp front, RGBA @2x/@1x, `fx.json`, previews). Một lệnh dựng lại: `python scripts/experiments/milestone_01/build_slash_diag.py`. Kết quả 6 tiêu chí:
  `frames/fx/slash_diag/criteria.json`. Thay đổi so với kế hoạch: user đổi sang vệt dày phủ gốc-mũi, nhiều tầng như showcase, nên vệt bám đường đi thật
  của gốc/mũi (Catmull-Rom qua điểm đánh dấu) thay vì cung tròn; hướng tiếp tuyến vì thế đạt theo cách dựng (đã ghi). Nhánh chém đôi chữ X không đạt:
  `docs/milestone-01-research-rising-cuts.md`.

- 2026-11-10: chuyên gia trả lời 12 câu ([milestone-01-advisor-review.md](milestone-01-advisor-review.md)); **kế hoạch chốt**:
  [milestone-01-plan.md](milestone-01-plan.md) (6 gate, tiêu chí, chi phí dự kiến ~0,07-0,13 USD, trần ~0,28). Gate 0 xong: P3 tái dùng
  `pose_skill_radiant_slash_v01`, P1 phải tạo mới. **Chờ user duyệt chi phí**; chưa gọi API.
- 2026-11-10: user yêu cầu **thống nhất kế hoạch + checklist với chuyên gia trước khi test**. Kế hoạch nháp (nay là `docs/milestone-01-plan.md`);
  12 câu hỏi gửi chuyên gia: `docs/milestone-01-advisor-questions.md`. Chờ trả lời.
- 2026-11-10: ghi quyết định. **Chưa bắt đầu**: bước 1 tốn tiền (ảnh ~0,0135 USD/ảnh; clip h3-max-turbo ~0,062 USD/clip theo `out/costs.csv`), cần
  user đồng ý trước khi chạy clip (quy tắc chi phí trong `CLAUDE.md`).
