# Nghiên cứu: dựng lại hình VFX vẽ tay bằng path Bézier

Mở 2026-11-07. Đây là nhiệm vụ riêng của một session mới. Mục tiêu duy nhất là dựng **đúng hình** (shape), chưa làm hiệu ứng.

## 1. Vấn đề

User gửi một GIF xoáy chém (dữ liệu: [ref/vfx/swirl-slash/](../../../ref/vfx/swirl-slash/README.md)). Qua 7 vòng sửa trong session trước, mình đã
khớp được **nhịp, màu, số lớp và cách các lớp lồng nhau**, nhưng **hình vẫn sai**: dáng lưỡi liềm, lưỡi lửa, lông vũ, móc vỡ chưa giống bản
gốc. User đánh giá điểm xấu nhất là các chi tiết cùng một khuôn xếp thành dải.

## 2. Giả thuyết của user (hướng nghiên cứu)

- Designer vẽ VFX từng frame trong một công cụ như Adobe Animate, Toon Boom, Illustrator.
- Hình trong các công cụ đó là **vector**: path khép kín ghép từ đoạn Bézier (điểm neo + tay nắm), tô một màu phẳng; các lớp màu là các path chồng
  lên nhau (hoặc nét có độ dày thay đổi rồi tô kín).
- Vector là dữ liệu, nên code tạo lại được (SVG `path d="M… C…"`, canvas `bezierCurveTo`).
- Nếu tìm ra **công thức sinh path** (số điểm neo, vị trí điểm nhọn, độ cong, độ dày theo đường đi) cho từng loại hình đặc trưng, thì hình sẽ
  đúng và công thức dùng lại được cho các hiệu ứng khác.

## 3. Những gì đã biết (đo trên GIF ở session trước)

**Định dạng.** 1920x1080, 38 frame, 25 fps. Hai biến thể: lửa (phải), băng (trái). Không có gradient trong thân: mỗi lớp là **một mã màu
phẳng**. Chỉ quầng sáng là chuyển màu (bỏ qua quầng trong nghiên cứu này).

**Lửa: 4 lớp** (số điểm ảnh theo frame f2→f9 trong `layers/index.json`):

| Lớp | Màu | Hình |
|---|---|---|
| vàng | 255,214,112 | phần mới vẽ, phía mép ngoài, đầu tù; mép trong răng cưa |
| hổ phách | 254,172,76 | viền rất mỏng quanh vùng vàng và dọc mép ngoài |
| hồng | 255,98,140 | phía mép trong; phủ hết đuôi; lưỡi lửa dài chĩa ngược chiều quét vào vùng vàng |
| đỏ sẫm | 209,47,87 | sâu nhất phía trong và mũi kim ở đuôi; về sau thành các móc nhọn rời |

**Băng: 4 lớp:**

| Lớp | Màu | Hình |
|---|---|---|
| trắng | 239,255,255 | lưỡi trắng **phía ngoài**, đầu nhọn móc xuống |
| cyan | 105,231,254 | vài mảng lông vũ to bên trong ngọn lửa xanh |
| xanh | 59,169,226 | **ngọn lửa xanh phía trong**, cạnh lưỡi trắng (hai hình cạnh nhau, ngăn bởi đường tối mảnh) |
| xanh sẫm | 30,109,157 | viền ngoài mỏng, vệt sẫm, mảnh vỡ |

**Nhịp** (để chọn frame, không cần dựng):
- Đầu nét quét theo chiều kim đồng hồ từ trên bên trái: khoảng 100°, 205°, 282°, 330° ở frame 2-5. Đuôi gần như đứng yên.
- Lửa vỡ ở frame 6, hết khoảng frame 13. Băng tan dần, vết nứt còn tới khoảng frame 22.

**Các hướng đã thử và vì sao chưa đạt** (code: `lib-fx/melee/blade/blade.py`, `lib-fx/_core/fieldfx.py`, `organic.py`):

| Hướng | Kết quả |
|---|---|
| ghép hình tham số (dải theo cung tròn, gai `thorn`, mảnh `shard`) | hình máy móc, compa |
| trường xám liên tục cắt bằng ngưỡng (posterize), răng cưa bằng sawtooth | ranh giới liền nhưng răng cưa lặp đều thành dải |
| ranh giới trơn + lưỡi lửa / lông vũ đặt tay (đa giác trong toạ độ nét) | không còn dải, nhưng dáng từng hình vẫn không giống: đường cong tròn trịa, thiếu điểm nhọn, thiếu chỗ "giật" của nét vẽ tay |

Kết luận: thiếu một mô hình **đúng ngôn ngữ đường nét của designer**. Bước tiếp là đo hình thật dưới dạng path.

## 4. Nhiệm vụ của session mới

1. **Vector hoá mặt nạ** (`ref/vfx/swirl-slash/layers/*.png`):
   - Tách đường viền từng lớp; nối các đoạn thành path Bézier bậc 3 khít với viền, sai số dưới 1-1,5 px.
   - Phát hiện góc nhọn (điểm neo không trơn) và chia đoạn tại đó.
   - Dùng thư viện có sẵn nếu có (potrace / `pypotrace`, `svgpathtools`, `skimage.measure.find_contours` + fitting kiểu Schneider) hoặc tự viết
     (Ramer-Douglas-Peucker + fit Bézier).
   - Xuất SVG, chồng lên frame gốc để kiểm tra.
2. **Đọc cấu trúc của path thật**, cho từng loại hình đặc trưng:
   - lưỡi liềm chính có mũi kim;
   - lưỡi lửa hồng;
   - lông vũ cyan;
   - lưỡi trắng của bản băng;
   - móc vỡ;
   - viền hổ phách.

   Với mỗi loại, đo số điểm neo, vị trí và độ nhọn của các góc, tỉ lệ tay nắm, độ dày nét dọc đường đi (nếu là nét có độ dày thay đổi), cách hai
   lớp màu chạm nhau (chung một cạnh? lớp trên đè lớp dưới?).
3. **Tìm công thức sinh path**: tham số ít (ví dụ: đường xương sống + profile độ dày + vị trí/độ nhọn các gai) sinh lại được từng loại hình. Kiểm
   tra bằng cách sinh lại hình ở frame 3, 4, 5 và so với mặt nạ gốc.
4. **Demo**: SVG (và PNG) dựng lại các lớp của frame 3, 4, 5 cho cả hai biến thể, đặt cạnh bản gốc.
5. **Lưu công thức** vào `lib-fx/research/bezier-shapes/` (code + tài liệu), để sau này dùng cho mọi hiệu ứng, bổ sung vào
   `lib-fx/SHAPE-RULES.md`.

## 5. Tiêu chí đạt

- Mỗi loại hình có một hàm sinh path với tham số đọc được (không phải toạ độ chép lại từ GIF).
- Hình sinh ra trùng mặt nạ gốc: IoU ≥ 0,85 cho lớp lớn (vàng, hồng, trắng, xanh), ≥ 0,7 cho lớp nhỏ.
- Xem bằng mắt: có cùng điểm nhọn, cùng chỗ lồi lõm, cùng nhịp to-nhỏ của lưỡi lửa như bản gốc.
- Không gradient, không lặp khuôn.
- **Ngoài phạm vi:** hiệu ứng, chuyển động giữa các frame, quầng sáng, vết nứt.

## 6. Ràng buộc

- Không gọi model trả phí (fal.ai). Không commit file tạm.
- GIF chỉ để học. Hình cuối cùng phải sinh từ công thức, không phải path chép nguyên từ GIF (path chép chỉ dùng để đo).
- Python ở repo này: Pillow, numpy, scipy có sẵn (cài thêm bằng pip nếu thiếu).
- Theo `CLAUDE.md`: hỏi advisor trước khi chốt kế hoạch và trước khi báo xong.
