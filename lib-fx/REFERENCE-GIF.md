# Vẽ lại một hiệu ứng từ GIF / video tham khảo

Quy trình khi user gửi thẳng một GIF (hoặc MP4, WEBM, thư mục frame) của một VFX và muốn dựng lại bằng lib-fx (code, 0 USD).
Ghi ngày 2026-11-06, trước khi nhận GIF đầu tiên.

## 1. Làm được gì, không làm được gì

**Làm được**
- Đọc **mọi frame** và thời lượng từng frame (ảnh tĩnh chỉ cho một khoảnh khắc; GIF cho cả nhịp: báo trước, bùng, đỉnh, tan).
- Tách hiệu ứng khỏi nền, đo từng frame: khung bao, diện tích, tâm, độ sáng, **số mảnh rời và cỡ từng mảnh** (ra nhịp to/vừa/nhỏ),
  bảng màu chính và tỉ lệ từng màu, quỹ đạo chuyển động (ảnh onion skin).
- Dựng lại bằng bộ kit có sẵn: hình tự do (`organic`: gai, giọt, khối méo, lưỡi lửa `flame`/`tongue`, viền spline, tô theo khoảng cách
  tới mép, khói toon `shade`/`cloud`, ăn mòn có nhiễu), hình học (`fxcore`: vòng 3D, lưỡi liềm, dải, tia, hạt có lực cản), đường bay
  Catmull-Rom với hàm thời gian riêng, đuôi một mặt nạ.
- Khớp **đúng số frame và nhịp** của bản gốc, rồi so từng frame cạnh nhau (`--compare`) sau mỗi vòng sửa.

**Giới hạn (nói trước với user)**
- Không phải vẽ lại từng điểm ảnh: hình là tham số hoá (gai, lưỡi lửa, khối...). Hiệu ứng 2D vẽ tay, phẳng (tia lửa, vòng xung kích,
  chém, lửa, khói, nước, sét) làm được gần; hình cụ thể phức tạp (đầu thú, chữ, nhân vật) khó và dễ xấu (bài học `life/dash/tiger`).
- Hiệu ứng 3D / particle system của engine (hàng nghìn hạt, mờ dần mượt, méo không gian, bloom) chỉ làm xấp xỉ: look của lib-fx là màu
  phẳng theo dải + quầng sáng, không có gradient hay méo hình.
- GIF 256 màu, dither, nén, nền rối hay có nhân vật đè lên sẽ làm tách nền kém; nhân vật trong khung phải loại ra (khung bỏ qua).
- Mắt mình xem ảnh ở cỡ thu nhỏ: chi tiết nhỏ hơn vài px trong GIF nhỏ sẽ bị mất.
- Thường cần **2-4 vòng**: vòng 1 khớp nhịp và bố cục, các vòng sau sửa hình.

**Bản quyền**: GIF tham khảo (thường từ game thương mại) chỉ để **học** nhịp, bố cục, cách xếp lớp. Không truy (trace) lại hình 1:1 để
dùng làm asset, không commit file tham khảo (`lib-fx/_study/` nằm trong `.gitignore`), không ghi tên game trong code hay tài liệu.
Có thể dùng chính mặt nạ của bản gốc để **thử** cách tô màu, nhưng asset cuối phải là hình mình dựng.

## 2. GIF nên gửi thế nào (càng đủ càng tốt)

- Hiệu ứng **đứng riêng**, nền trơn hoặc trong suốt; nếu có nhân vật, nói rõ nhân vật cao bao nhiêu px (để quy về hero 120 px @2x).
- Cỡ ≥ 400 px, tốc độ gốc (không tua), đủ một vòng từ đầu tới khi tan hết.
- Một câu: thích nhất phần nào (hình tóe, nhịp, màu, lớp khói...), hiệu ứng dùng cho đòn gì, hướng nào.

## 3. Quy trình

1. **Nghiên cứu** (tự động):
   ```
   python lib-fx/_tools/study_ref.py <file.gif> --name <tên> [--bg auto|R,G,B|alpha] [--thr 38] [--hero-px <cao nhân vật>]
   ```
   Ra `lib-fx/_study/<tên>/`: `contact.png` (mọi frame, số thứ tự, thời điểm), `onion.png` (quỹ đạo), `palette.png`, `curves.png`
   (diện tích, độ sáng, số mảnh theo frame), `report.json` (nhịp: frame xuất hiện, sáng nhất, to nhất, bắt đầu tan, hết; cỡ các mảnh).
2. **Đọc ra bảng lớp** (viết vào RECIPE của hiệu ứng): mỗi lớp là gì, hình gì (vẽ bằng hàm nào), màu (lấy từ `palette.png`), sinh ở
   frame nào, sống bao lâu, đi đâu, chết thế nào. Kiểm tra theo DESIGN.md §10: mỗi lớp khác nhau ≥ 3 trục, nhịp to/vừa/nhỏ, mỗi phần tử
   một số phận.
3. **Dựng key pose trước**: chọn 3-4 frame mốc (từ `report.json`: sáng nhất, to nhất, bắt đầu tan), dựng từng frame tĩnh cho giống,
   rồi mới làm chuyển tiếp.
4. **Khớp nhịp**: cùng fps và số frame; nếu GIF có frame giữ lâu (hold), giữ đúng như vậy.
5. **So từng vòng**:
   ```
   python lib-fx/_tools/study_ref.py <file.gif> --name <tên> --compare lib-fx/<nhóm>/<họ>/<id>/frames
   ```
   `compare.png`: bản gốc | của mình, cùng đồng hồ. Sửa chỗ lệch nhất trước (bố cục > nhịp > hình > màu).
6. Để `draft`, đưa user xem GIF; ghi bài học vào RECIPE và DESIGN.md.

## 4. Mẫu tham khảo đã đạt trong thư viện

- Nhiều lớp, nhịp, vòng xung kích, màu nguội dần: [RECIPE-inferno.md](RECIPE-inferno.md) (`force/shock/inferno`, approved).
- Đốm lửa / tinh linh bay có đuôi, mỗi con một tính cách: [RECIPE-soul-spirits.md](RECIPE-soul-spirits.md).
- Tóe va chạm vẽ tay: [RESEARCH-organic-impact.md](RESEARCH-organic-impact.md).
- Các lỗi phải tránh: DESIGN.md §10 (lặp lại, khô cứng, vẽ mục tiêu, sai chất liệu).
