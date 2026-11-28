# Showcase: các hiệu ứng đã dựng lại bằng bộ tool vector

Xuất bằng `python lib-fx/_tools/vectorfx.py showcase PROFILE` (bộ tool không cần chạy lại để xem). Mỗi thư mục biến thể có:
`compare.gif` (bản gốc | bản dựng, đúng tốc độ gốc; mỗi bên thu về 320 px), `compare_original_size.gif` (chỉ có ở `flame-burst/jet`, `lightning/bolt`, `flame-burst-trace/fire`, `lightning-trace/green`: vùng cắt của bản gốc ở **kích thước gốc** | bản dựng thu về đúng cùng tỉ lệ, cùng khung hình), `rebuilt.gif` (chỉ bản dựng), `frames/NN.png` (frame hoàn chỉnh: gradient, glow),
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
| `flame-burst` | lửa phụt ngang + khói | [flame-burst/jet](flame-burst/jet/) | chờ chấm |
| `lightning` | tia sét xanh lá, nét mảnh + quầng nhoè (127 khung, mỗi khung một tia mới) | [lightning/bolt](lightning/bolt/) | chờ chấm |
| `flame-burst-trace` | lần dựng đầu (nhánh `vfx/vector-rebuild-flame-burst-lightning`): chế độ `fit.mode = "trace"` (viền từ mặt nạ, không khớp nét), 59 khung; lửa còn thiếu nhiều | [flame-burst-trace/fire](flame-burst-trace/fire/) | chưa chấm |
| `lightning-trace` | lần dựng đầu cho sét: chế độ `trace`, 3 lớp (quầng, tia, lõi), 115 khung | [lightning-trace/green](lightning-trace/green/) | chưa chấm |
| `lightning-3` | **Prism Spark** ("Điện lăng kính"), **đạt**: tia điện ngoằn ngoèo có viền tách màu (xanh ngọc / hồng) và quầng xanh, 52 khung, mỗi khung một hình; `recipe/rebuild_check_bright.json` | [lightning-3/spark](lightning-3/spark/) | đạt |
| `lightning-2` | **đạt** · ba hiệu ứng sét từ **video** (`ref/vfx/lightning-2/lightnings.mp4`), mỗi cái một vòng lặp: cung xanh 19 hình, sét vàng đánh đất 17 hình, sét xanh lớn 20 hình; chế độ `trace`, lớp thân + chớp đất + khung mực (đảo màu); `compare.gif` giữ đúng số frame của từng hình | [lightning-2/arc](lightning-2/arc/), [lightning-2/strike](lightning-2/strike/), [lightning-2/bolt](lightning-2/bolt/) | đạt |

`lightning-2/recipe/`: `exposure.json` (bảng nhịp: frame video đầu và số frame giữ của từng hình), `rebuild_check_bright.json` (diện tích, bề rộng nét phần sáng so với ảnh gốc, ngưỡng 120), `rebuild_check_dark.json` (khung mực: diện tích, IoU phần đen), `report.json`, ảnh kiểm mặt nạ `check_*.png`; công thức và số đo: `lib-fx/_core/formulas/rules/vfx/lightning/README.md`.

Mỗi bản của `flame-burst/jet` và `lightning/bolt` còn thư mục `recipe/`: `lifecycle.json` (vòng đời từng lớp), `report.json` (IoU và độ mượt từng khung), bảng màu (`palette_*.png`), ảnh kiểm mặt nạ (`check_*.png`) và, với sét, các ảnh nghiên cứu (`study_*`). Cách dựng ra chúng: `lib-fx/_plans/vfx-rebuild-02/R1-flame-burst.md`, `R2-lightning.md`, `METHOD.md`; hồ sơ: `lib-fx/_core/formulas/vector/profiles/{flame-burst,lightning}.json` (bản `jet`, `bolt`) và `{flame-burst-trace,lightning-trace}.json` (bản `trace`).

Trang review đầy đủ (từng lớp, từng frame): Swirl Slash Shapes https://claude.ai/artifact/QYf1pHQVRyrNRWtUyAdKGR,
Element Trio https://claude.ai/artifact/6Vw3supbrvPSULNoNsxCzn, Slash Trio https://claude.ai/artifact/69ermXASZKmFccapxfCYis.
Bản gốc: `ref/vfx/swirl-slash/`, `ref/vfx/element-trio/`, `ref/vfx/slash-trio/`.

## Hiệu ứng sinh mới (không có bản gốc)

Mỗi bản `gen-lightning-*` có thêm `colours/<gold|red|purple|green>.gif` (và `_game.gif`): cùng hiệu ứng ở màu khác (`--colour ... --preview-only`).

| Tên | Lệnh | Thư mục | Trang |
|---|---|---|---|
| Nhát chém ngang xanh | `vectorfx.py gen-slash gen-slash-blue --variant blue --frame 7` | [generated/gen-slash-blue](generated/gen-slash-blue/) (`preview.gif`, `frames/`, `svg/`, `design.json`) | https://claude.ai/artifact/WSPsgRkzRos6fW6BfDrsNM |
| Nhát chém ngang xanh, vòng quanh thân (phản chiếu, vòng khép); user 8-9/10 trước khi thêm phản chiếu | `vectorfx.py gen-slash gen-slash-loop-blue --style loop` | [generated/gen-slash-loop-blue](generated/gen-slash-loop-blue/) | https://claude.ai/artifact/2zSWrndFyafkCGZ6a328CM |
| Như trên, vũ khí lớn (trọng kiếm, đại đao, katana) | `vectorfx.py gen-slash gen-slash-loop-heavy-blue --style loop-heavy` | [generated/gen-slash-loop-heavy-blue](generated/gen-slash-loop-heavy-blue/) | cùng trang (nút "Bản nặng") |
| Một nhát vũ khí lớn trước mặt, chữ C hở | `vectorfx.py gen-slash gen-slash-front-heavy-blue --style front-heavy` | [generated/gen-slash-front-heavy-blue](generated/gen-slash-front-heavy-blue/) | cùng trang (nút "Chém trước mặt") |
| Chém đôi chữ X tuần tự, vàng | `vectorfx.py gen-slash gen-slash-x-gold --style x` | [generated/gen-slash-x-gold](generated/gen-slash-x-gold/) (`sheet.png`, `fx_meta.json`) | https://claude.ai/artifact/JrmYvD4FCabP17GaeLUyVP |
| **Đã duyệt (user 2026-11-28, phong cách sét chuẩn).** Sét quanh nhân vật, dùng chính hình vector của bản remake `lightning-2`: hai tia `bolt` đánh xuống hai bên (một sau, một trước thân), một cung `arc` quấn quanh thân (nửa sau bị che) | `vectorfx.py gen-lightning gen-lightning-wrap-blue` | [generated/gen-lightning-wrap-blue](generated/gen-lightning-wrap-blue/) (`preview.gif` có khối thân thay nhân vật, `preview_game.gif` thân cao 60 px, `back/` `front/` RGBA chỉ có hiệu ứng, `design.json`) | https://claude.ai/artifact/4cbfa2MD123GvG3iVK3ubb |
| **Đã duyệt (2026-11-28).** Sét quanh cánh tay giơ ngang: 2 cung remake xoắn quanh tay (lò xo, mặt sau bị tay che) + 1 tia remake phóng từ bàn tay | `vectorfx.py gen-lightning gen-lightning-arm-blue --style arm` | [generated/gen-lightning-arm-blue](generated/gen-lightning-arm-blue/) | https://claude.ai/artifact/4cbfa2MD123GvG3iVK3ubb |
| Gọi sét: tay giơ thẳng lên, tia từ trời đánh vào bàn tay, cung xoắn quanh tay + quanh thân (**đã duyệt** 2026-11-28) | `vectorfx.py gen-lightning gen-lightning-raise-blue --style raise` | [generated/gen-lightning-raise-blue](generated/gen-lightning-raise-blue/) | https://claude.ai/artifact/4cbfa2MD123GvG3iVK3ubb |
| Dang hai tay: cung xoắn quanh mỗi tay, tia phóng ra hai phía (**đã duyệt** 2026-11-28) | `vectorfx.py gen-lightning gen-lightning-dual-blue --style dual` | [generated/gen-lightning-dual-blue](generated/gen-lightning-dual-blue/) | https://claude.ai/artifact/4cbfa2MD123GvG3iVK3ubb |
| Đập đất: tay chéo xuống, tia từ bàn tay đánh xuống đất phía trước, tia trời đánh sau lưng (**đã duyệt** 2026-11-28) | `vectorfx.py gen-lightning gen-lightning-slam-blue --style slam` | [generated/gen-lightning-slam-blue](generated/gen-lightning-slam-blue/) | https://claude.ai/artifact/4cbfa2MD123GvG3iVK3ubb |
| Phóng chéo lên: cung xoắn quanh tay, tia phóng theo hướng tay (**đã duyệt** 2026-11-28) | `vectorfx.py gen-lightning gen-lightning-thrust-blue --style thrust` | [generated/gen-lightning-thrust-blue](generated/gen-lightning-thrust-blue/) | https://claude.ai/artifact/4cbfa2MD123GvG3iVK3ubb |
| **Charge v2 (đã duyệt 2026-11-28)**: Prism Spark quấn quanh thân nhân vật (3 lớp quấn lệch nhịp, viền tách màu tính sau khi quấn), 5 màu | `vectorfx.py gen-lightning gen-lightning-prism-blue --style prism` | [generated/gen-lightning-prism-blue](generated/gen-lightning-prism-blue/) | https://claude.ai/artifact/4cbfa2MD123GvG3iVK3ubb |
| Combo 2 nhát: quét ngang + bổ xuống có toé | `vectorfx.py gen-slash gen-slash-combo-blue --style combo --dummy` (`preview_dummy.gif`: có hình nộm) | [generated/gen-slash-combo-blue](generated/gen-slash-combo-blue/) | https://claude.ai/artifact/6XeNBdLFJbwNAS9BwEuqYp |
