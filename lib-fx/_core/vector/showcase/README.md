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

Trang review đầy đủ (từng lớp, từng frame): Swirl Slash Shapes https://claude.ai/artifact/QYf1pHQVRyrNRWtUyAdKGR,
Element Trio https://claude.ai/artifact/6Vw3supbrvPSULNoNsxCzn. Bản gốc: `ref/vfx/swirl-slash/`, `ref/vfx/element-trio/`.
