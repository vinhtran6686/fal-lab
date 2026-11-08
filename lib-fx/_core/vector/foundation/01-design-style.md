# 01. Phong cách: nhiều lớp, nét mịn liền, màu theo cấp bậc

Nguồn: 5 hiệu ứng đã dựng lại 9-10/10. Số liệu màu: [data/colour_hierarchy.json](data/colour_hierarchy.json) (đo ở frame đỉnh: độ sáng
luma = 0,299R + 0,587G + 0,114B; `depth_px` = khoảng cách trung vị vào trong khối, px bản gốc; `height` = 0 chân → 1 đỉnh khối).

## 1. Nhiều lớp

| Hiệu ứng | Lớp (dưới → trên) | Lớp đặc biệt |
|---|---|---|
| xoáy lửa | vàng (gồm dải cam ở mép), hồng, đỏ sẫm | glow đỏ |
| xoáy băng | xanh sẫm, xanh, cyan, trắng | glow xanh |
| lửa phun | cam, vàng | glow cam (làm nhoè hình, tắt dần) |
| Arcane | màn cánh trong mờ (độ đục ~0,45), tím nhạt, cánh xanh | glow tím |
| Toxic | bóng tối trong mờ, bạc hà | vòng sáng dưới đất |

Luật:
- **2-4 lớp màu phẳng** cho phần chính; thêm tối đa 1-2 lớp "không khí" (màn trong mờ, bóng tối, glow).
- Các lớp **tô chồng**: lớp dưới là khối liền, chạy tiếp ~10 px dưới lớp trên (không ghép mép sát nhau → khe, mối nối).
- Lớp có mũi nhọn đâm sang lớp khác nằm **trên** (mũi do chính lớp đó tạo, không phải do mép lớp dưới).
- Giữa hai lớp không có nét viền tối (khe 1-3 px ở GIF là khử răng cưa); chỉ tách nhóm khi đo được nét tối thật.
- Một lớp có thể có **gradient mép** (vàng ngả cam ~8 px, trắng ngả xanh nhạt ~3 px), không có gradient tự do trong thân.

## 2. Nét mịn, đường cong liền (bài học lớn nhất của research)

Vấn đề cũ: hình ghép từ nhiều nét công thức nhìn "rác": gấp khúc ở mối nối, lổm chổm, nứt nẻ (user chấm 7/10). Đường của designer (đo bằng
vector hoá bản gốc):
- ~**26 px viền cho một điểm neo**; lớp lớn chỉ 20-35 neo.
- **Tay nắm ≈ 1/3 dây cung** (trung vị 0,32; 0,21-0,38): đường cong dài, êm, không có tay nắm kéo dài.
- **Không có neo gãy nửa vời**: neo hoặc trơn hẳn (G1), hoặc là mũi nhọn thật (góc trong ~50-100°).
- Mũi nhọn nằm ở lớp nguội / tối (51-62°), lớp nóng gần như không có mũi (~100°).
- Chi tiết liền nhau chênh nhau 2-5 lần độ dài, khoảng cách không đều: **không lặp khuôn**.

Cách đạt được bằng code (`smooth.smooth_simplify`, mô phỏng Illustrator Simplify + Potrace + fair curve của Moreton): nối khe nhỏ, chỉ giữ góc
nhọn ở cả hai tầm nhìn, làm trơn giữa hai góc sao cho độ cong biến thiên ít nhất, nắn neo gãy < 35°, gộp đoạn, tay nắm ≤ 0,45 dây cung.
Kết quả đo: 0 điểm gãy, độ biến thiên độ cong ngang đường vẽ tay. Mọi path sinh ra đều phải qua bước này. Chi tiết:
`research/bezier-shapes/RETROSPECTIVE.md` §2.4-2.5.

## 3. Màu theo cấp bậc tạo khối

| Hiệu ứng | Thang màu (sáng → tối) | Bước độ sáng | Vị trí |
|---|---|---|---|
| xoáy lửa | vàng 215 → hồng 150 → đỏ sẫm 100 | −65, −50 | vàng sâu trong khối (9,8 px vào trong) và ở đầu nét; đỏ sẫm ở đuôi / mép trong |
| xoáy băng | trắng 250 → cyan 196 → xanh 143 → xanh sẫm 91 | −54, −53, −52 | trắng sâu nhất (10,6 px); xanh sẫm là viền mỏng (2 px) |
| lửa phun | vàng 207 → cam 162 | −45 | vàng ở **chân** (cao 0,11), cam lên trên (0,48) |
| Arcane | tím nhạt 209, xanh 201 (+ màn xanh mờ) | ~0 | hai **sắc** khác nhau cùng độ sáng: tím ở giữa / trên, xanh ở dưới / hai bên |
| Toxic | bạc hà 212, bóng tối 29 | −183 | lõi sáng trên nền bóng tối trong mờ |

Ba kiểu phối màu:
1. **Thang một họ màu** (lửa, băng): 3-4 tông, **bước độ sáng đều ~50-65**, sắc trượt nhẹ khi tối đi (vàng → hồng → đỏ sẫm; trắng → cyan → xanh → xanh
   sẫm). Tông sáng nhất = phần nóng / nhiều năng lượng nhất: sâu trong khối, ở gốc phun hoặc ở đầu nét; tông tối ở mép, đuôi, phần đã nguội.
   Đây là thứ làm mắt đọc ra "khối lửa", "khối băng".
2. **Lõi sáng + bóng tối** (Toxic): một màu sáng bão hoà trên một khối tối trong mờ (khói). Tương phản độ sáng cực lớn thay cho thang.
3. **Hai sắc cùng độ sáng + màn mờ** (Arcane): tách khối bằng sắc (tím / xanh) chứ không bằng độ sáng; chiều sâu do màn trong mờ và glow.

Khói (gợi ý của user: xám cho lửa) thuộc kiểu 2: một lớp tối / xám trong mờ phía sau, không nằm trong thang sáng.

Luật glow: glow mang **màu chính** của hiệu ứng (lửa: đỏ cam, Arcane: tím, băng: xanh), là bản làm nhoè của chính hình (2 tầng nhoè ~15-30 px và
~70-90 px ở ảnh 3x), không phải viền cố định.
