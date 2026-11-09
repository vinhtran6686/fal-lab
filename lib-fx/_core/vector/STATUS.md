# Trạng thái bộ tool vector (đọc file này đầu tiên khi mở session mới)

Cập nhật: 2026-11-09, bộ tool **v1.8**. File này là điểm nối giữa các session: đã làm gì, đang ở đâu, câu hỏi còn mở, việc tiếp theo.
Khi xong một bước, cập nhật file này (và `CHANGELOG.md`).

## 1. Đã làm được (user đã duyệt)

| Việc | Kết quả | Ở đâu |
|---|---|---|
| Dựng lại VFX vẽ tay từ GIF thành path Bézier sạch | xoáy chém lửa 9, băng 9-10; lửa phun, Arcane, Toxic 10/10; slash-trio (3 nhát + phản chiếu) đạt | `profiles/`, [showcase/](showcase/README.md) |
| Nền tảng thiết kế (luật + số đo) | 5 yếu tố của user đã kiểm chứng; vòng đời, mảnh, màu, ánh sáng | [foundation/](foundation/README.md) |
| Docs theo loại VFX | slash, explosion | [foundation/vfx/](foundation/vfx/README.md) |
| Tự động hoá đọc bản gốc | tự cắt vùng, gợi ý lớp màu, kiểm tra mask | `auto.py`, lệnh `init`, `check` |
| **Sinh nhát chém đơn mới từ luật** | lưỡi liềm 7/10 → xoay tại chỗ (thường, nặng) và chém trước mặt chữ C: **user: 9-10/10, sáng tạo slash đơn bằng tool đã khá ổn** | [foundation/vfx/slash/generators.md](foundation/vfx/slash/generators.md), trang https://claude.ai/artifact/2zSWrndFyafkCGZ6a328CM |

Lệnh hay dùng: `python lib-fx/_tools/vectorfx.py gen-slash NAME --style crescent|loop|loop-heavy|front-heavy`;
`vectorfx.py all PROFILE` (dựng lại); `vectorfx.py init GIF NAME` (profile mới). Đầy đủ: [README.md](README.md) §3.

## 2. Việc để dành (không làm trừ khi user cần)

- Slash 9-10/10: 3 điểm (phản chiếu sát sàn như đường kẻ; chữ C kèm vệt "(((" sau đỉnh; bản nặng chưa có bụi / tia va chạm):
  [generators.md §5](foundation/vfx/slash/generators.md).
- Bộ sinh `eruption` (nổ / phun): [foundation/vfx/explosion/](foundation/vfx/explosion/README.md) §5.
- Xuất thẳng sang chuẩn lib-fx (`sheet.png`, `meta.json`, @2x, nền trong suốt): chưa có; bản sinh hiện có nền tối + glow cộng màu.

## 3. Câu hỏi mở (concern cho các session sau)

### 3.0 Việc user định thử tiếp (2026-11-09)

Một hiệu ứng **chém liên tiếp 2-3 nhát, mỗi nhát một kiểu** (combo). Cần: nhiều đường chém trong một hiệu ứng (mỗi nhát một khung / kiểu
từ `STYLES`, lệch thời gian), nhát sau sinh khi nhát trước đang tàn; dùng chung với §3.1 (khung theo đường cong, quỹ đạo nhiều đoạn).
Trước đó user hỏi về cấu trúc thư mục `lib-fx/` (tách rõ tái tạo / sáng tạo): xem §3.2.

### 3.1 Nhát chém theo quỹ đạo user vẽ trước, khớp pose / kiểu attack của một nhân vật cụ thể (2026-11-09)

User thiết kế nhân vật theo thứ tự: **pose dáng + kiểu attack trước**, rồi mới tới hiệu ứng. Câu hỏi: với những gì đã có, có tạo được một nhát
chém đi **đúng quỹ đạo user vẽ sẵn** không? Tool chưa có tính năng này.

**Đánh giá: làm được, phần lớn đã có sẵn; thiếu 3 mảnh nhỏ.** Lý do:

- Mọi nét của bộ sinh được vẽ trong một **khung toạ độ** (u = vị trí dọc đường chém, v = lệch ngang qua đường chém). `strokes.py` chỉ cần ba
  hàm của khung: `to_xy(u, v)`, `u_px`, `u_scale`. Đã có khung cực, thẳng, elip, phản chiếu. Một **khung theo đường bất kỳ** (`PathFrame`: u = độ
  dài cung dọc đường cong user vẽ, v = lệch theo pháp tuyến) chỉ là thêm một lớp nhỏ trong `frames.py` (~40-60 dòng). Mọi thứ còn lại (nhiều sợi,
  đầu chổi khô, răng khía, giãn rồi đứt, vụn, phối cảnh `wknots`, phản chiếu, làm mịn, glow, xuất PNG / SVG / GIF) dùng lại nguyên.
- **Nhịp** của nhát chém hiện là bảng `TIMELINE` (đầu / đuôi nét mỗi hình vẽ). Với nhân vật có sẵn animation, đầu nét = vị trí mũi vũ khí ở từng
  frame của clip attack, nên bảng này có thể **lấy thẳng từ animation** (frame vung bắt đầu, frame va chạm = đỉnh).

**Ba mảnh còn thiếu:**

1. `PathFrame` từ một đường cong (Bézier / polyline), xử lý chỗ cong gắt: độ lệch v không được vượt bán kính cong (nếu không mép trong tự cắt
   nhau), nên giới hạn độ dày theo độ cong hoặc làm trơn đường trước.
2. **Đầu vào quỹ đạo**, một trong ba cách: (a) user vẽ path trong Illustrator / Figma, xuất SVG `<path d>`; (b) chấm vài điểm trên frame đỉnh
   của nhân vật (một trang HTML nhỏ cho click điểm, xuất JSON); (c) bán tự động: user đánh dấu mũi vũ khí trên 3-5 frame khoá của clip attack,
   nội suy ra quỹ đạo + thời gian.
3. **Khớp với nhân vật**: cùng khung ảnh, cùng điểm neo ở chân (quy ước lib-fx / `fx_layers.py`), cùng số frame và fps với clip attack;
   xuất theo chuẩn lib-fx (nền trong suốt, @2x, `meta.json`) để ghép lên sprite.

**Rủi ro / cần user quyết:** quỹ đạo 2D trên màn hình hay elip phối cảnh (vung quanh thân thì nên giữ ý "vòng elip" để có dày / mảnh theo
phối cảnh: user có thể vẽ vòng rồi tool khớp elip); quỹ đạo nhiều đoạn (chém hai nhịp, gãy góc như nhát hồng của slash-trio) cần nhiều khung
nối nhau. Phong cách (sợi, đầu nét, màu) giữ theo `STYLES` hiện có.

**Đề xuất khi làm:** thử trên một nhân vật có clip attack sẵn trong `out/`: (1) `PathFrame` + đọc SVG path; (2) chạy kiểu `heavy` trên quỹ đạo
đó, đặt chồng lên frame nhân vật để user chấm; (3) nếu ổn, thêm cách (c) lấy nhịp từ clip và xuất chuẩn lib-fx.

### 3.2 Cấu trúc `lib-fx/`: tách tái tạo và sáng tạo (2026-11-09, đề xuất, chờ user quyết)

Hiện trạng: thư viện chuẩn là `<nhóm>/<họ>/<id>/` (hiệu ứng vẽ bằng `fxcore`, có `sheet.png` + `meta.json`); còn mọi việc của bộ vector
(bản tái tạo từ GIF bên ngoài và bản sáng tạo) nằm trong `_core/vector/showcase/` (thư mục code), tài liệu nằm rải ở gốc `lib-fx/`
(`RECIPE-*`, `RESEARCH-*`, `DESIGN.md` ...) và trong `_core/vector/foundation/`. Đề xuất: thư viện chỉ chứa hiệu ứng **có thể dùng
trong game** (procedural + sáng tạo, `meta.json` thêm `origin` / `method`); bản **tái tạo** (học từ art của người khác, không ship) tách
sang một khu riêng; code chỉ ở `_core/`; tài liệu gom về một chỗ. Chi tiết trong câu trả lời cho user cùng ngày; chưa di chuyển gì.

## 4. Ghi chú môi trường

- Code chạy trên Linux (session cloud) và Windows (máy user, xem `CLAUDE.md` mục Python).
- Output trung gian ở `lib-fx/_study/` (git bỏ qua); bản lưu trong git ở `showcase/`.
- Trang review là artifact riêng tư trên claude.ai (link trong `showcase/README.md`); ảnh trang dựng lại từ `lib-fx/_study/<name>/page/`.
