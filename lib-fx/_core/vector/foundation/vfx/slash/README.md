# VFX loại "slash" (nhát chém)

Mọi thứ đã biết về nhát chém vẽ tay flat-colour: đọc bản gốc, số đo, luật, và các bộ sinh hiệu ứng mới.

| File | Nội dung |
|---|---|
| [references.md](references.md) | 5 mẫu tham khảo đã dựng lại (xoáy lửa, xoáy băng, slash-trio xanh / hồng / vàng): lớp, màu, vòng đời, bố cục, phản chiếu |
| [generators.md](generators.md) | 4 bộ sinh (lưỡi liềm, xoay tại chỗ thường / nặng, chém trước mặt chữ C): tham số, luật rút ra, điểm user chấm, **việc còn thiếu để đạt 9-10/10** |

## Tóm tắt

**Bản gốc đã dựng lại** (bộ tool `lib-fx/_core/vector`, profile trong `profiles/`):

| Mẫu | Profile | Bản gốc | Showcase | User |
|---|---|---|---|---|
| xoáy chém lửa, băng | `swirl-slash` | `ref/vfx/swirl-slash/` | [showcase/swirl-slash](../../../showcase/swirl-slash/) | 9, 9-10/10 |
| nhát chém xanh, hồng, vàng + phản chiếu | `slash-trio` | `ref/vfx/slash-trio/` | [showcase/slash-trio](../../../showcase/slash-trio/) | đạt |

**Hiệu ứng sinh mới** (`vectorfx.py gen-slash NAME --style ...`, chi tiết [generators.md](generators.md)):

| Tên | Kiểu | User |
|---|---|---|
| `gen-slash-blue` | lưỡi liềm (v0) | 7/10 |
| `gen-slash-loop-blue` | xoay tại chỗ, vòng quanh thân, bản thường | ổn |
| `gen-slash-loop-heavy-blue` | xoay tại chỗ, vũ khí lớn (trọng kiếm, đại đao, katana) | ổn |
| `gen-slash-front-heavy-blue` | một nhát trước mặt, chữ C hở, vũ khí lớn | ổn |

User (2026-11-09): sáng tạo slash đơn bằng tool đã khá ổn. Câu hỏi mở: slash theo quỹ đạo vẽ trước cho một nhân vật: [../../../STATUS.md](../../../STATUS.md) §3.1.

**Luật cốt lõi** (chi tiết và số đo trong hai file trên):
- Sinh từ một đầu nét và **dài ra theo đường quét**; bùng 1-3 frame; tàn nhanh (diện tích ×0,3 mỗi frame ở bản gốc); vẽ on ones, on twos ở tia cuối.
- Lớp sáng ở mặt ngoài / đầu nét, lớp tối ở mép trong và đuôi; nhiều sợi, đầu nét chổi khô; độ dày theo phối cảnh nếu đường chém là vòng elip.
- Tàn bằng **vết cắt và lỗ** (44-64%), không chỉ mòn mép; sau đỉnh sợi **giãn trước, đứt sau**, mỗi sợi đứt ở chỗ riêng.
- **Glow giữ sáng tới cuối** trên tia và mảnh (khác lửa phun).
- **Phản chiếu dưới sàn** = cùng nét, lật, dẹt ~1/4, tối và nhạt hơn, cùng nhịp.
- Vũ khí lớn: lưỡi rộng hơn ~2-2,7 lần, ít sợi đậm, đầu cùn, vụn to, giữ 2 frame lúc lấy đà và lúc va chạm.

Luật chung cho mọi loại VFX (lớp, nét mịn, cấp bậc màu, vòng đời, ánh sáng): [../../README.md](../../README.md) và 01-05.
