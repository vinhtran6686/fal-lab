# Tham khảo: xoáy chém (swirl slash) – dữ liệu cho nghiên cứu path Bézier

GIF tham khảo user gửi (2026-11-06 và gửi lại 2026-11-07). Chỉ dùng để **học hình**: không đồ lại làm asset, không ghi tên game.
Kết quả dựng lại: [lib-fx/_core/results/vector-showcase/swirl-slash](../../../lib-fx/_core/results/vector-showcase/swirl-slash/).

## File

| File | Nội dung |
|---|---|
| `reference.gif` | GIF gốc: 1920x1080, 38 frame, 40 ms/frame (25 fps), 1,52 s; hai biến thể cạnh nhau trên nền tối có gradient |
| `frames/{fire,frost}_NN.png` | frame 02-13 của từng biến thể, cắt 700x700 (khung cắt trong `layers/index.json`) |
| `layers/{fire,frost}_NN_<lớp>.png` | **mặt nạ đen trắng của từng lớp màu** ở từng frame (điểm ảnh gần mã màu của lớp < 30), cùng khung 700x700 |
| `layers/index.json` | số điểm ảnh từng lớp theo frame, bảng màu, khung cắt |
| `fire_layers_f3-f5.png`, `frost_layers_f3-f5.png` | các lớp tô lại bằng màu dễ phân biệt, frame 3-5, độ phân giải gốc (xem hình nhanh) |
| `fire_masks_by_colour.png` | lưới: từng màu ứng viên × từng frame (cho thấy vành tối chỉ là quầng sáng) |
| `failed_attempt_v7_compare.gif` | bản dựng gần nhất (chưa đạt) cạnh bản gốc |

Biến thể lửa: x 960-1660, y 120-820. Biến thể băng: x 200-900, y 120-820 (toạ độ trong khung 1920x1080).
