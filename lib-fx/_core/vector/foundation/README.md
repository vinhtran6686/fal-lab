# Nền tảng thiết kế VFX vẽ tay (foundation)

Thư mục này gom mọi thứ đã học được về **cách designer làm loại hiệu ứng flat-colour vẽ tay**, rút từ 5 hiệu ứng tham khảo đã dựng lại
được 9-10/10 bằng bộ tool `lib-fx/_core/vector` (v1.0): xoáy chém lửa và băng (`swirl-slash`), phun lửa, Arcane, Toxic (`element-trio`).
Đây là **cơ sở** cho mọi việc về sau: dựng lại hiệu ứng mới, và nhất là **sinh hiệu ứng mới** từ luật. Mỗi luật ở đây đều kèm số đo; số liệu
gốc trong [data/](data/), tạo lại bằng `python lib-fx/_tools/vectorfx.py lifecycle|track PROFILE` và các bước ghi trong từng file.

| File | Nội dung |
|---|---|
| [01-design-style.md](01-design-style.md) | phong cách: nhiều lớp, nét mịn liền, màu theo cấp bậc tạo khối |
| [02-animation.md](02-animation.md) | vòng đời: nhỏ → bùng → đỉnh → vỡ và co từng mảnh → mất; nhịp vẽ; glow và độ đục theo thời gian |
| [03-reading-references.md](03-reading-references.md) | cách đọc đúng một bản gốc (các lỗi đo đã gặp và cách tránh) |
| [04-generation-spec.md](04-generation-spec.md) | bản đặc tả cho bộ sinh hiệu ứng mới: tham số, luật, cái đã đủ và cái còn thiếu |
| [05-birth-erosion-composition.md](05-birth-erosion-composition.md) | lúc sinh (ở đâu, bung thế nào), cách mép bị ăn khi tàn, bố cục lưỡi ở đỉnh |
| [data/](data/) | `lifecycle_*.json` (từng frame), `tracking_*.json` (tóm tắt theo dõi từng mảnh), `shape_study_*.json`, `colour_hierarchy.json` |

Xem kết quả dựng lại của các hiệu ứng (GIF so với bản gốc, frame, SVG): [../showcase/](../showcase/README.md).

## Năm yếu tố quyết định một hiệu ứng đẹp (tư duy của user, đã kiểm chứng bằng số đo)

| # | Yếu tố (lời user) | Kiểm chứng | Chi tiết |
|---|---|---|---|
| 1 | **Thiết kế nhiều lớp** | đúng: mỗi hiệu ứng 2-4 lớp màu phẳng (+ màn mờ, bóng tối, glow); lớp dưới chạy liền dưới lớp trên | 01 §1 |
| 2 | **Nét vector mịn, đường cong liền, tròn** (không "rác", không rải rác, không lệch nhau) | đúng: ~26 px viền / điểm neo, tay nắm ≈ 1/3 dây cung, 0 điểm gãy; đây là bài học lớn nhất của research, đã thành `smooth.smooth_simplify` | 01 §2 |
| 3 | **Màu theo cấp bậc, ghép lại thành khối** (lửa: vàng, cam, đỏ, xám khói) | đúng: thang 2-4 tông cùng họ màu, bước độ sáng đều ~45-65; tông sáng nhất ở lõi / ở gốc, tông tối ở mép / đuôi; có thêm 2 kiểu khác (lõi sáng + bóng tối; hai sắc cùng độ sáng + màn mờ) | 01 §3 |
| 4 | **Bắt đầu từ hình nhỏ, to dần tới đỉnh, rồi từng hình nhỏ dần và mất** | đúng, và đo được chi tiết hơn: bùng rất nhanh (1-4 frame), đỉnh rất ngắn, sau đó **mỗi mảnh co lại mỗi hình vẽ và sứt ra mảnh nhỏ, đứng tại chỗ**, biến mất khi chỉ còn đốm 8-30 px; khung bao ngoài giữ nguyên tới cuối mới sụp | 02 |
| 5 | (bổ sung từ số đo) **Thời gian của ánh sáng**: glow tắt trước hình, hình mờ dần ở cuối, lớp nóng tan trước; vẽ "on twos" ở pha tàn | đo được trên lửa, Arcane, xoáy | 02 §4-5 |

## Ý kiến (2026-11-08)

Bốn yếu tố của user là đúng và là đúng thứ tự ưu tiên khi **thiết kế**. Khi **dựng lại / sinh bằng code**, kinh nghiệm cho thấy thứ tự làm
việc nên là: (a) **đọc đúng** bản gốc (03: gần hết lỗi lớn đến từ đo sai: gradient bị cắt, khử răng cưa bị coi là nét, glow cố định), (b) dựng đúng
**cấu trúc lớp và màu** (01), (c) **làm mịn nét** (01 §2), (d) đặt đúng **thời gian** (02). Bỏ bước nào cũng kẹt ở 7-8/10.

Điểm cần lưu ý nhất ở yếu tố 4: "nhỏ dần" ở pha tàn **không phải thu nhỏ cả hình về tâm**; khung kích thước của hiệu ứng được giữ, còn từng mảnh
bên trong co lại, mỏng đi và sứt ra mảnh nhỏ tại chỗ. Nếu bộ sinh thu nhỏ đều cả hình, hiệu ứng sẽ trông như bị "tua ngược".
