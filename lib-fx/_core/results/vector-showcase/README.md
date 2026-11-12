# Showcase: các hiệu ứng đã dựng lại bằng bộ tool vector

Xuất bằng `python lib-fx/_tools/vectorfx.py showcase PROFILE` (bộ tool không cần chạy lại để xem). Mỗi thư mục biến thể có:
`compare.gif` (bản gốc | bản dựng, đúng tốc độ gốc), `rebuilt.gif` (chỉ bản dựng), `frames/NN.png` (frame hoàn chỉnh: gradient, glow),
`svg/NN.svg` (vector sạch, mỗi lớp một `<path id="lớp">`).

| Profile | Biến thể | Thư mục | Điểm user |
|---|---|---|---|
| `swirl-slash` | xoáy lửa | [swirl-slash/fire](swirl-slash/fire/) | 9/10 |
| | xoáy băng | [swirl-slash/frost](swirl-slash/frost/) | 9-10/10 |
| `element-trio` | lửa phun | [element-trio/fire](element-trio/fire/) | 10/10 |
| | Arcane | [element-trio/arcane](element-trio/arcane/) | 10/10 |
| | Toxic | [element-trio/toxic](element-trio/toxic/) | 10/10 |
| `slash-trio` | nhát chém xanh | [slash-trio/blue](slash-trio/blue/) (+ phản chiếu `blue_refl`) | đạt (chấp nhận được) |
| | nhát chém hồng | [slash-trio/pink](slash-trio/pink/) (+ `pink_refl`) | đạt (chấp nhận được) |
| | nhát chém vàng | [slash-trio/gold](slash-trio/gold/) (+ `gold_refl`) | đạt (chấp nhận được) |

Trang review đầy đủ (từng lớp, từng frame): Swirl Slash Shapes https://claude.ai/artifact/QYf1pHQVRyrNRWtUyAdKGR,
Element Trio https://claude.ai/artifact/6Vw3supbrvPSULNoNsxCzn, Slash Trio https://claude.ai/artifact/69ermXASZKmFccapxfCYis.
Bản gốc: `ref/vfx/swirl-slash/`, `ref/vfx/element-trio/`, `ref/vfx/slash-trio/`.

## Hiệu ứng sinh mới (không có bản gốc)

| Tên | Lệnh | Thư mục | Trang |
|---|---|---|---|
| Nhát chém ngang xanh | `vectorfx.py gen-slash gen-slash-blue --variant blue --frame 7` | [generated/gen-slash-blue](generated/gen-slash-blue/) (`preview.gif`, `frames/`, `svg/`, `design.json`) | https://claude.ai/artifact/WSPsgRkzRos6fW6BfDrsNM |
| Nhát chém ngang xanh, vòng quanh thân (phản chiếu, vòng khép); user 8-9/10 trước khi thêm phản chiếu | `vectorfx.py gen-slash gen-slash-loop-blue --style loop` | [generated/gen-slash-loop-blue](generated/gen-slash-loop-blue/) | https://claude.ai/artifact/2zSWrndFyafkCGZ6a328CM |
| Như trên, vũ khí lớn (trọng kiếm, đại đao, katana) | `vectorfx.py gen-slash gen-slash-loop-heavy-blue --style loop-heavy` | [generated/gen-slash-loop-heavy-blue](generated/gen-slash-loop-heavy-blue/) | cùng trang (nút "Bản nặng") |
| Một nhát vũ khí lớn trước mặt, chữ C hở | `vectorfx.py gen-slash gen-slash-front-heavy-blue --style front-heavy` | [generated/gen-slash-front-heavy-blue](generated/gen-slash-front-heavy-blue/) | cùng trang (nút "Chém trước mặt") |
| Chém đôi chữ X tuần tự, vàng | `vectorfx.py gen-slash gen-slash-x-gold --style x` | [generated/gen-slash-x-gold](generated/gen-slash-x-gold/) (`sheet.png`, `fx_meta.json`) | https://claude.ai/artifact/JrmYvD4FCabP17GaeLUyVP |
| Combo 2 nhát: quét ngang + bổ xuống có toé | `vectorfx.py gen-slash gen-slash-combo-blue --style combo --dummy` (`preview_dummy.gif`: có hình nộm) | [generated/gen-slash-combo-blue](generated/gen-slash-combo-blue/) | https://claude.ai/artifact/6XeNBdLFJbwNAS9BwEuqYp |
