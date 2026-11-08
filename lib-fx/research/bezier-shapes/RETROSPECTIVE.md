# Tổng kết: dựng lại hiệu ứng xoáy chém vẽ tay bằng path Bézier (2026-11-07 → 2026-11-08)

Tài liệu này ghi lại toàn bộ quá trình, từ lúc bắt đầu tới khi user chấm 9-10/10: làm gì, sai ở đâu, vì sao sai, sửa thế nào, và đúc
kết được gì. Mục đích là làm **nền cho một bộ tool dựng VFX vẽ tay bằng code** và cho animation về sau. Chi tiết số liệu nằm trong
[FINDINGS.md](FINDINGS.md); luật dùng chung đã chép vào [../../SHAPE-RULES.md](../../SHAPE-RULES.md) §7, §7b, §7c.

Trang xem lại (riêng tư, chỉ user mở được): Swirl Slash Shapes, https://claude.ai/artifact/QYf1pHQVRyrNRWtUyAdKGR.

---

## 0. Tóm tắt một trang

| Mốc | User chấm | Thay đổi quyết định | Bài học |
|---|---|---|---|
| Trước session (7 vòng cũ) | "hình sai" | trường nhiệt + ngưỡng, răng cưa tuần hoàn, hình đặt tay | chỉnh tham số khi chưa đo đúng hình thì không bao giờ tới |
| v1 | tỉ lệ, hướng, góc đúng; nét lổm chổm, thiếu gradient | đo hình bằng vector hoá, công thức "nét thon trong toạ độ cực", khớp tham số | công thức đúng, nhưng **đọc sai dữ liệu** (mặt nạ đúng mã màu) |
| v2 | ~7/10 | mặt nạ theo **đường màu** (gồm gradient mép), **tô chồng**, pen pass, gradient trong, quầng sáng đo được | bước nhảy lớn nhất đến từ **đọc đúng bản gốc**, không phải từ công thức mới |
| v3 | lửa 9/10, băng 8/10 | **Smooth & Simplify** kiểu Illustrator/Potrace + làm trơn theo độ cong biến thiên ít nhất | hết điểm gãy; độ cong đều như đường vẽ tay |
| v3 băng | 9-10/10 | bỏ "đường tối" giả giữa lưỡi trắng và lửa xanh, bỏ chấm sáng quầng gần, làm trơn mạnh hơn cho băng | lại là **một lỗi đọc dữ liệu** (khử răng cưa bị hiểu thành nét) |

**Trả lời câu hỏi "có phải nhờ nghiên cứu làm mịn vector mà đạt không?"**: một phần, và là phần cần nhưng chưa đủ.
- Từ v1 lên v2 (lên ~7/10): nhờ **đọc lại đúng bản gốc** (gradient trong lớp, lớp chồng lên nhau, quầng sáng). Làm mịn ở v2 còn đơn giản.
- Từ v2 lên v3 (lửa 9/10): nhờ **công cụ làm mịn kiểu Illustrator/Potrace + fair curve**. Đây đúng là phần user đề xuất nghiên cứu, và nó
  xoá hết điểm gãy (2-8 điểm gãy mỗi lớp → 0), độ biến thiên độ cong giảm 2-14 lần.
- Băng từ 8 lên 9-10/10: một nửa nhờ làm mịn mạnh hơn, một nửa nhờ **sửa một lỗi đọc dữ liệu nữa** (khe 2 px giữa trắng và xanh là pha
  màu, không phải nét tối).
- Kết luận: **đo đúng → dựng đúng cấu trúc → làm mịn đúng cách**. Thiếu bước nào cũng kẹt ở 7-8/10. Gợi ý của user về làm mịn
  vector là chìa khoá cho bước cuối; nhưng nếu không sửa cách đọc dữ liệu trước, làm mịn chỉ làm mịn một hình sai.

---

## 1. Bối cảnh và dữ liệu

- Bản gốc: GIF 1920x1080, 38 frame, 25 fps, hai biến thể cạnh nhau: **lửa** (vàng, hổ phách, hồng, đỏ sẫm) và **băng** (trắng, cyan, xanh,
  xanh sẫm). Dữ liệu cắt sẵn: `ref/vfx/swirl-slash/` (frame 700x700, mặt nạ từng lớp ngưỡng < 30).
- Nhiệm vụ ([BRIEF.md](BRIEF.md)): chỉ dựng **hình tĩnh** từng lớp ở frame 3-5, bằng hàm sinh path tham số (không chép toạ độ), IoU ≥ 0,85
  lớp lớn, ≥ 0,7 lớp nhỏ, nhìn bằng mắt có cùng điểm nhọn, chỗ lồi lõm, nhịp to-nhỏ.
- Giả thuyết của user: designer vẽ từng frame bằng công cụ vector (Animate, Toon Boom), mỗi lớp màu là một path Bézier khép kín tô phẳng.
- 7 vòng trước session này (code `lib-fx/melee/blade/blade.py`, `_core/fieldfx.py`): đúng nhịp, màu, số lớp; **sai hình**. Ghép hình tham số
  thì máy móc; trường xám cắt ngưỡng với răng cưa tuần hoàn thì thành dải lặp khuôn; hình đặt tay thì tròn trịa, thiếu điểm nhọn.

---

## 2. Dòng thời gian chi tiết

### 2.1 v1: đo hình bằng vector, tìm công thức (commit `29d7997`)

**Bước 1. Vector hoá mặt nạ** (`vectorize.py`, `bezier.py`):
- Viền dưới điểm ảnh: làm mờ nhẹ mặt nạ (Gauss σ 0,7) rồi lấy đường đồng mức 0,5 (`skimage.measure.find_contours`).
- Lấy mẫu lại cách đều 1 px.
- **Phát hiện góc**: góc quay trên cửa sổ ±4 px, góc > 55° và là cực đại cục bộ thì là điểm neo góc.
- **Fit Bézier kiểu Schneider** (thuật toán "An algorithm for automatically fitting digitized curves", Graphics Gems 1990): tham số hoá
  theo chiều dài dây cung, bình phương tối thiểu cho độ dài hai tay nắm khi đã biết hướng tiếp tuyến, lặp Newton-Raphson để tham số hoá
  lại, nếu sai số vẫn > ngưỡng thì chia đôi tại điểm sai nhiều nhất (tiếp tuyến chung ở điểm chia nên nối G1).
- Kết quả: mọi lớp khớp với sai số tối đa 1,0-1,41 px, trung bình 0,3-0,46 px.

**Bước 2. Đọc cấu trúc path thật** (`analyze.py`), các số đo quan trọng nhất:
- Lớp lớn chỉ 21-34 điểm neo; trung bình **26 px viền / 1 điểm neo**.
- **Tay nắm / dây cung: trung vị 0,32** (80% trong 0,21-0,38): đúng "luật 1/3", không có tay nắm kéo dài.
- Góc nhọn: góc trong trung vị 62°; đỏ sẫm/xanh 51-52° (mũi kim), vàng 102° (lớp nóng gần như không có mũi).
- Nhịp chi tiết: hai lưỡi liền nhau chênh độ dài 2-5 lần; khoảng cách có hệ số biến thiên 0,54-1,2 (không đều).

**Bước 3. Công thức "nét thon trong toạ độ cực"** (`shapes.py`, `polar.py`, `fit.py`):
- Tâm xoáy = đường tròn khớp với viền ngoài (Kasa fit). Mở ảnh sang toạ độ cực: lưỡi liềm thành dải ngang, lưỡi lửa thành gai ngang.
- Tách mặt nạ thành **dải cực**: mỗi cột góc có các đoạn bán kính; nối các đoạn qua các cột theo độ chồng lấn lớn nhất. Nhánh sinh ra ở
  chỗ rẽ được kéo dài 4 cột vào nhánh mẹ để không có mối cắt.
- Mỗi dải = một nét:
  ```
  t ∈ [0,1] theo chiều quét, θ = θ0 + (θ1-θ0)·t
  xương sống  r_c(t) = Bernstein(b0..bn)
  bề rộng     w(t) = W·(t+e0)^a·(1-t+e1)^b·(1 + Bernstein(m1..mk))
  mép         r = r_c ± w/2 → toạ độ màn hình → fit Bézier, mũi nhọn = neo góc
  ```
  `a`, `b` = độ nhọn hai đầu (< 1 tròn, ≈ 1 nêm, > 1 kim); `e0`, `e1` = 0 mũi nhọn, > 0 đầu cụt. Bậc Bernstein và số hệ số "lượn" tăng dần
  chỉ khi cần (sai số mép > 0,6-0,8 px).
- **Thân trước, chi tiết sau** (`rebuild.py`): thân được fit bền vững (Huber IRLS cho xương sống, `soft_l1` cho bề rộng) nên gốc lưỡi lửa
  dính vào thân bị coi là ngoại lai; phần dư (thiếu / thừa) được fit thành lưỡi cộng thêm và **vết khoét** trừ đi; chỉ giữ mảnh làm IoU
  tăng ≥ 0,003. Có thêm nét theo trục bán kính cho mũi chĩa vào/ra tâm.
- Kết quả: đạt cả 24 lớp f3-f5 (vàng 0,94-0,95, trắng 0,90-0,97...) **so với mặt nạ đúng mã màu**.

**Sai lầm của v1 (phát hiện về sau):**
1. **Mặt nạ "đúng mã màu" (sai số < 12)**. Mình chọn nó vì mặt nạ < 30 của `layers/` lẫn quầng sáng. Nhưng lớp vàng và lưỡi trắng
   có **gradient trong** sát mép; mặt nạ đúng mã màu cắt mất dải đó → vàng hụt ~30% diện tích, mũi lưỡi hồng đâm vào dải cam biến mất,
   giữa các lớp có khe tối. Mình còn coi "hổ phách" là một lớp riêng, trong khi nó chính là dải mép của lớp vàng.
2. **Mỗi lớp dựng độc lập, đặt sát nhau** → khe và mối nối. Khi hợp nhiều nét lại, viền có những chỗ gãy nhỏ ở mối ghép.
3. Bỏ quầng sáng và gradient vì brief ghi "ngoài phạm vi", trong khi chúng là một phần lớn của cảm giác "mượt".

Review user (ảnh chụp điện thoại): "tỉ lệ đúng, hướng và góc đúng; nhưng shape **rác**, thiếu mềm mại, giống nhiều nét đơn lẻ ghép lại;
gấp khúc ở giữa các đường đáng lẽ cong mượt; thiếu **gradient** theo màu chính".

### 2.2 Trang xem lại + chuyển động (commit `2ddbf79`)

- Dựng thêm mọi frame còn màu (lửa 2-12, băng 2-9) để làm GIF gộp, so cạnh bản gốc ở 25 fps và 8 fps.
- Trang artifact có: chọn biến thể/frame, mỗi lớp 4 ô (mục tiêu / dựng lại / các nét / lỗi), nút Đạt-Cần sửa và ghi chú lưu trong trình duyệt,
  nút "Sao chép nhận xét". Dạng trang này giúp user review **từng shape theo từng frame**, rất hiệu quả cho vòng sửa.

### 2.3 v2: đọc lại đúng bản gốc (commit `c82921c`, user ~7/10)

**Chẩn đoán**: phóng to vùng lưỡi hồng đâm vào vàng ở frame gốc, đếm màu trong "khe" giữa hai mặt nạ: toàn `240,176,80`, `252,180,84`...
nằm trên đường thẳng từ vàng `255,214,112` sang cam `254,172,76`. Tức là **lớp vàng được tô gradient vào mép**, không phải có khe.

**Sửa:**
1. **Mặt nạ theo đường màu** (`masks.family_masks`): mỗi lớp là một polyline trong không gian màu (màu phẳng → màu mép), điểm ảnh thuộc lớp
   có khoảng cách tới polyline nhỏ nhất (chia theo dung sai riêng của lớp). Lửa còn 3 lớp: vàng (gồm dải cam), hồng, đỏ sẫm.
2. **Đo gradient trong** (`out/edge_gradient_fit.json`): màu = lerp(phẳng, mép, exp(−d/s)), d = khoảng cách vào trong từ mép phần nhìn
   thấy. Vàng → `255,163,69`, s 8,1 px; trắng → `178,253,252`, s 3,4 px; hồng s 2,7; cyan s 1,5; đỏ sẫm, xanh, xanh sẫm phẳng.
3. **Đo quầng sáng** (`out/halo_fit.json`): lấy frame 13 (hiệu ứng đã tắt) làm nền, hiệu = frame − nền theo khoảng cách tới hình, fit
   tổng hai hàm mũ. Lửa đỏ `195,−8,43` s 38 px; băng xanh `1,57,91` s 27 px.
4. **Tô chồng như designer**: lửa vàng → hồng → đỏ sẫm; mỗi lớp dưới được fit với vùng của nó **cộng phần lớp trên trong 10 px**, nên chạy
   liền dưới lớp trên (hết khe, hết mối nối). Thứ tự này quan trọng: ban đầu mình đặt hồng dưới vàng thì mũi lưỡi hồng do mép vàng quyết
   định và bị tròn; đảo lại (hồng đè lên vàng) thì mũi do chính lưỡi hồng quyết định.
5. **Pen pass** (`pen.py`): hợp các nét của một lớp → bỏ vụn → viền → giữ góc thật → làm trơn Gauss dọc viền giữa hai góc (góc ghim) → fit
   Bézier G1.

**Sai lầm của v2:**
- Giữ băng thành hai nhóm để "giữ đường tối mảnh giữa lưỡi trắng và lửa xanh" (vì nhìn mặt nạ thấy có khe). Không đo, chỉ đoán. Sai (xem 2.5).
- Thành phần quầng gần của băng (s 0,5 px) thật ra là khử răng cưa, vẽ ra thành viền sáng lấm tấm.
- Làm trơn Gauss chưa đủ: vẫn còn điểm gãy 5-35° ở chỗ nối, độ cong lượn sóng.

User: "đã tốt hơn rất nhiều, ~7/10; thêm cơ chế tự làm đều nét như Illustrator (bend tool, liên kết điểm neo, mịn), tham khảo Illustrator,
Corel, image trace".

### 2.4 v3: Smooth & Simplify (commit `b62c398`, lửa 9/10, băng 8/10)

**Nghiên cứu** (nguồn ở mục 6):
- Illustrator *Object > Path > Simplify*: hai điều khiển: *curve precision* (bám đường bao nhiêu, ít/nhiều điểm neo) và *corner point angle
  threshold* (góc nào nhọn hơn ngưỡng thì giữ). Bản cũ trước 2019 được nhiều người cho là làm trơn tốt hơn.
- Potrace (lõi của nhiều tính năng image trace): `alphamax` (ngưỡng góc, nhỏ thì nhiều góc nhọn) và *curve optimization* `opttolerance`
  (gộp các đoạn Bézier liền kề khi sai số nhỏ, mặc định 0,2).
- Lý thuyết **fair curve**: Moreton (Berkeley 1993) đề xuất dùng **độ biến thiên của độ cong** làm thước đo độ đẹp, tốt hơn năng lượng uốn;
  tiêu chí thường dùng: độ cong phân bố đều nhất có thể.

**Thuật toán `fair.smooth_simplify`** (6 bước cho mỗi viền, toạ độ 1 px):
1. **Nối nét (Join)**: đóng khe < 1,5 px trong cùng một lớp (closing), bỏ vụn và lỗ < 8 px.
2. **Góc thật hai tầm** (ý tưởng alphamax): một điểm là góc khi góc trong < 145° ở cửa sổ ±4 px **và** < 165° ở ±8 px. Răng cưa nhỏ chỉ nhọn ở
   tầm sát nên bị loại; mũi nhọn thật nhọn ở cả hai tầm.
3. **Làm trơn theo độ cong biến thiên ít nhất** (fairing): giữa hai góc (ghim cả hai đầu và điểm kề), giải hệ tuyến tính thưa
   `min |q−p|² + λ₂|D²q|² + λ₃|D³q|²`, D² là sai phân bậc 2 (uốn), D³ bậc 3 (biến thiên độ cong), λ₂ = 0,5σ⁴, λ₃ = 0,25σ⁶ (σ 4,5 px; vòng
   kín thì sai phân tuần hoàn). Mảnh ngắn dùng λ nhỏ hơn. Sau đó **bù diện tích**: đẩy viền theo pháp tuyến ra ngoài một khoảng
   (A₀ − A₁)/chu vi (góc không đẩy) vì làm trơn luôn làm hình co.
4. **Fit Bézier** (Schneider, sai số 0,5 px), mọi neo trơn có tay nắm thẳng hàng (G1).
5. **Nắn điểm gãy và gộp đoạn** (Illustrator corner threshold + Potrace opticurve): neo "góc" nào hai tay nắm lệch < 35° thì nắn thành neo trơn
   (hai tay nắm về đường phân giác); rồi lặp: gộp hai đoạn liền kề qua neo trơn nếu một cubic vẫn bám mọi điểm mẫu trong 0,9 px (chọn cặp sai
   số nhỏ nhất trước).
6. **Giới hạn tay nắm** ≤ 0,45 dây cung (đường vẽ tay đo 0,21-0,38) để không sinh vòng, không phình.

**Thước đo độ mượt** (`smoothness.py`), để không chấm bằng cảm tính:
- *điểm gãy*: neo có hai tay nắm lệch 5-35° (không trơn, không phải góc thật);
- *độ biến thiên độ cong*: Σ|Δκ| trên mỗi 100 px viền (thước đo của Moreton, thấp = đều);
- *điểm uốn*: số lần độ cong đổi dấu mỗi 100 px.

Kết quả frame 3-5 (xem bảng FINDINGS §7): điểm gãy 2-8 → 0; độ biến thiên độ cong giảm 2-14 lần (hồng 10,21 → 0,71); số điểm neo bằng
hoặc ít hơn đường vẽ tay của bản gốc; IoU giữ nguyên ±0,03 ở frame 2-5. Không cần dựng lại nét công thức: v3 đọc lại `out2/params_*.json`
và chỉ thay bước viền, nên chạy rất nhanh.

### 2.5 v3 băng mượt tối đa (commit `ced4298`, 9-10/10)

User: "băng 8/10, các nét vẫn nứt nẻ, chưa mịn; làm mịn tối đa".

**Chẩn đoán bằng đo, không đoán:**
- Đo dải 2 px giữa lưỡi trắng và lửa xanh trên f3-f5: màu trung vị `91,195,236` = **pha giữa trắng và xanh** (khử răng cưa). Không có nét tối.
  Đường tối giữ từ v2 chính là "vết nứt".
- Thành phần quầng gần của băng s 0,5 px = khử răng cưa → viền sáng lấm tấm.
- Mặt nạ băng nhiễu hơn lửa (quầng xanh phủ lên lớp xanh).

**Sửa:** băng một nhóm (lớp xanh chạy liền dưới trắng, nét công thức băng khớp lại); bỏ quầng gần cho băng; tham số làm trơn riêng cho băng:
σ 7 px, ngưỡng góc 142° (thử 130° thì lông vũ cyan tròn đầu), gộp đoạn ≤ 1,5 px, nối khe ≤ 2,5 px, bỏ vụn < 40 px.
Kết quả: 0 điểm gãy; điểm neo 19-36 mỗi lớp (gốc 29-56); độ biến thiên độ cong 0,36-0,60. Đổi lại IoU xanh f5 0,789, f3 0,821, cyan f3 0,814;
frame vụn 6-9 giảm rõ.

---

## 3. Danh sách sai lầm và bài học

| # | Sai lầm | Hậu quả | Vì sao xảy ra | Bài học thành luật |
|---|---|---|---|---|
| 1 | 7 vòng trước chỉnh tham số trường nhiệt/răng cưa tuần hoàn | dải lặp khuôn, hình sai | chưa đo hình gốc dưới dạng path | **đo trước, dựng sau** |
| 2 | Mặt nạ đúng mã màu | mất gradient mép, mất mũi lưỡi, khe giữa lớp | sợ quầng sáng lẫn vào nên siết dung sai quá chặt | lớp = màu phẳng **+ gradient mép của nó** (polyline màu) |
| 3 | "Hổ phách" coi là lớp | thêm một lớp mỏng vụn | đếm màu mà không nhìn không gian | kiểm tra một màu có phải chỉ là mép gradient của lớp kề không |
| 4 | Lớp dựng độc lập, đặt sát nhau | khe, mối nối, viền lổm chổm | nghĩ theo "vùng nhìn thấy" thay vì "lớp tô chồng" | **tô chồng**, lớp dưới chạy liền dưới lớp trên |
| 5 | Thứ tự tô sai (hồng dưới vàng) | mũi lưỡi hồng tròn | mũi do mép lớp trên quyết định | lớp có mũi nhọn đâm vào lớp khác thì nằm **trên** |
| 6 | Bỏ gradient và quầng vì "ngoài phạm vi" | nhìn khô, "rác" | hiểu brief quá chữ | những thứ tạo cảm giác mượt phải đo và dựng, kể cả khi brief nói tập trung vào hình |
| 7 | Làm trơn Gauss đơn giản | còn điểm gãy, độ cong lượn | không có thước đo độ mượt | dùng fairing D³ + nắn gãy + gộp đoạn, và **đo** điểm gãy / độ biến thiên độ cong |
| 8 | Giữ "đường tối" giữa trắng và xanh | vết nứt ở băng | đoán từ mặt nạ, không đo màu dải đó | khe 1-3 px giữa hai lớp gần như luôn là khử răng cưa; **đo màu** trước khi coi là nét |
| 9 | Fit quầng có thành phần s < 1 px | viền sáng lấm tấm | để mô hình hấp thụ khử răng cưa | bỏ mọi thành phần có thang < 1,5 px |
| 10 | Thêm nhiều mảnh vụn để tăng IoU | "rác" | tối ưu IoU thay vì nhìn | mỗi mảnh phải trả giá (IoU tăng tối thiểu), rồi luôn qua bước làm mịn; **IoU không phải mục tiêu duy nhất** |

---

## 4. Bộ kỹ thuật đã kiểm chứng (dùng lại cho bộ tool)

### 4.1 Đo bản gốc
- Tách frame, cắt khung từng biến thể (`ref/vfx/swirl-slash/layers/index.json`).
- Đếm mã màu: màu phẳng là các đỉnh histogram với hàng nghìn điểm ảnh đúng một mã.
- **Mặt nạ theo đường màu** (`masks.FAMILY`, `family_masks`): polyline màu cho mỗi lớp, dung sai riêng, lọc trung vị 3x3, bỏ vụn/lỗ < 12 px.
- Nền = frame hiệu ứng đã tắt (f13) → đo quầng = frame − nền theo khoảng cách tới hình.
- Gradient trong: fit lerp(phẳng, mép, exp(−d/s)) theo khoảng cách vào trong.

### 4.2 Vector hoá và đọc cấu trúc
- Viền dưới điểm ảnh + lấy mẫu 1 px + góc theo cửa sổ + Schneider fit (`bezier.py`).
- Thống kê: điểm neo / chu vi, tay nắm / dây cung, góc trong của các neo góc, dài/rộng từng chi tiết, nhịp (`analyze.py`).

### 4.3 Sinh hình
- **Nét thon trong toạ độ của hiệu ứng** (`shapes.stroke`): xương sống Bernstein + `W·(t+e0)^a·(1−t+e1)^b·(1+lượn)`; theo trục góc hoặc
  trục bán kính. Đây là "đơn vị hình" chung cho lưỡi liềm, lưỡi lửa, lông vũ, móc, viền, vết khoét.
- Khớp tham số: tách dải cực (`polar.bands`), thân bền vững + phần dư thành lưỡi / vết khoét (`rebuild.build_layer`).
- Tô chồng với lớp dưới mở rộng 10 px dưới lớp trên (`rebuild2`).

### 4.4 Làm sạch viền (bước quyết định độ "mịn")
`fair.smooth_simplify(cover, ss, corner_deg, sigma, tol, merge_tol, min_area, close_px)`:

| Tham số | Lửa | Băng | Ý nghĩa |
|---|---|---|---|
| `close_px` | 1,5 | 2,5 | khe tối đa được nối |
| `min_area` | 8 | 40 | vụn/lỗ nhỏ hơn bị bỏ (px²) |
| `corner_deg` | 145 | 142 | góc trong nhỏ hơn mới là góc thật (tầm rộng +20°) |
| `sigma` | 4,5 | 7 | độ mạnh fairing (λ₂ = 0,5σ⁴, λ₃ = 0,25σ⁶) |
| `tol` | 0,5 | 0,5 | sai số fit Bézier ban đầu |
| `merge_tol` | 0,9 | 1,5 | sai số cho phép khi gộp hai đoạn |
| nắn gãy | 35° | 35° | neo lệch dưới ngưỡng thành neo trơn |
| tay nắm | ≤ 0,45 dây cung | | |

Thước đo đi kèm: `smoothness.path_fairness` (điểm gãy, điểm uốn, độ biến thiên độ cong).

### 4.5 Tô màu
- Lớp: màu phẳng, gradient trong theo khoảng cách tới mép **phần nhìn thấy**.
- Quầng sau hình: c·exp(−d/s) theo khoảng cách tới hình; bỏ thành phần thang < 1,5 px.
- Lửa: thứ tự vàng → hồng → đỏ sẫm. Băng: xanh sẫm → xanh → cyan → trắng.

### 4.6 Quy trình review
- Trang artifact với: GIF gốc | bản cũ | bản mới ở 25 fps và 8 fps; từng lớp theo frame với ô mục tiêu / hình phẳng / đường pen (neo trắng =
  trơn, đỏ = góc); nút Đạt / Cần sửa + ghi chú + sao chép. User chấm theo điểm, mô tả bằng lời; mình chuyển lời thành **phép đo**
  (ví dụ "nứt nẻ" → đo màu dải giữa hai lớp; "gấp khúc" → đếm điểm gãy).

---

## 5. Kiến trúc đề xuất cho bộ tool sau này

Pipeline đã chạy được, tách thành module dùng lại:

```
reference (GIF/video) ──► measure ─────────────► style profile (json)
                           · palette + edge gradients (polyline màu)
                           · halo profile
                           · shape stats (neo/chu vi, tay nắm, góc, nhịp)
                           · stacking order
design / keyframes ─────► generate strokes (shapes.stroke, theo xương sống + profile bề rộng + mũi)
                           │
                           ▼
                        stack layers (lớp dưới chạy dưới lớp trên)
                           │
                           ▼
                        smooth_simplify  ◄── tham số theo style (lửa / băng)
                           │
                           ▼
                        render: fill + inner gradient + halo  →  SVG + PNG frames
                           │
                           ▼
                        metrics (IoU nếu có gốc, điểm gãy, độ biến thiên độ cong) + review page
```

Những phần còn thiếu để thành tool animation:
1. **Ràng buộc giữa các frame**: hiện mỗi frame dựng độc lập. Cần nội suy tham số nét (xương sống, bề rộng, mũi) theo thời gian, hoặc
   khớp từng nét qua các frame (cùng ID) để không rung.
2. **Sinh hình mới từ luật** (`generate.py` mới là bản thử): bố cục lưỡi/lông vũ theo nhịp đo được, chưa đạt độ đẹp của gốc.
3. **Mảng xanh sẫm trong mờ phía sau lửa băng** (có lỗ bầu dục) chưa dựng.
4. **Mũi lưỡi lửa rất mảnh** (3-6 px) và móc dưới đáy lưỡi trắng vẫn chưa nhọn bằng gốc; cần một loại nét có xương sống tự do (không bám
   toạ độ cực) cho các mũi này.
5. Gói `fair.smooth_simplify` thành một bước chung của `lib-fx/_core/` để mọi hiệu ứng code-drawn (lib-fx) đều đi qua.

---

## 6. Nguồn tham khảo

- Adobe, *Simplify paths advanced options*:
  https://helpx.adobe.com/illustrator/desktop/draw-shapes-and-paths/modify-paths/simplify-paths-advanced-options-overview.html
- Potrace man page (alphamax, opttolerance, curve optimization): https://www.mankier.com/1/potrace ; Selinger, *Potrace: a polygon-based
  tracing algorithm* (2003): http://potrace.sourceforge.net/potrace.pdf
- Moreton, *Minimum Curvature Variation Curves, Networks, and Surfaces for Fair Free-Form Shape Design* (Berkeley 1993):
  https://www2.eecs.berkeley.edu/Pubs/TechRpts/1993/5219.html
- Schneider, *An Algorithm for Automatically Fitting Digitized Curves*, Graphics Gems (1990) (thuật toán fit trong `bezier.py`).
- Gilland, *Elemental Magic* (mảng to/vừa/nhỏ, không đều, không đối xứng) – đã dẫn trong SHAPE-RULES §2.

---

## 7. Bản đồ file

| File | Vai trò |
|---|---|
| `BRIEF.md`, `HANDOVER-PROMPT.md` | nhiệm vụ ban đầu |
| `FINDINGS.md` | kết luận và số liệu từng phiên bản (§1-5 v1, §6 v2, §7 v3, §7.1 băng) |
| `RETROSPECTIVE.md` | tài liệu này |
| `masks.py` | mặt nạ đúng mã màu (v1) và mặt nạ theo đường màu `family_masks` (v2+) |
| `bezier.py` | Schneider fit, góc, viền, raster, SVG |
| `vectorize.py`, `analyze.py` | vector hoá bản gốc và thống kê cấu trúc |
| `polar.py`, `shapes.py`, `fit.py` | toạ độ cực, công thức nét thon, khớp tham số |
| `rebuild.py` | v1: thân + lưỡi + vết khoét |
| `rebuild2.py`, `pen.py` | v2: tô chồng, gradient, quầng, pen pass |
| `fair.py`, `smoothness.py`, `rebuild3.py` | v3: Smooth & Simplify, thước đo độ mượt, tham số theo biến thể |
| `preview_assets*.py`, `build_review.py`, `review.html` | ảnh, GIF và trang xem lại |
| `out/`, `out2/`, `out3/` | tham số, SVG, báo cáo từng phiên bản (PNG không commit) |
| `preview/`, `preview2/`, `preview3/` | GIF chuyển động (PNG từng lớp không commit, tạo lại bằng script) |

Chạy lại toàn bộ (0 USD, không gọi fal): `rebuild2.py 2,...,12` (~20 phút, khớp nét) → `rebuild3.py 2,...,12` (~3 phút, làm mịn + tô) →
`preview_assets3.py` → `build_review.py`.
