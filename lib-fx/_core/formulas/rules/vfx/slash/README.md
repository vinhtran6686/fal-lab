# VFX loại "slash" (nhát chém)

Mọi thứ đã biết về nhát chém vẽ tay flat-colour: đọc bản gốc, số đo, luật, và các bộ sinh hiệu ứng mới.

| File | Nội dung |
|---|---|
| [references.md](references.md) | 5 mẫu tham khảo đã dựng lại (xoáy lửa, xoáy băng, slash-trio xanh / hồng / vàng): lớp, màu, vòng đời, bố cục, phản chiếu |
| [ARCHITECTURE.md](ARCHITECTURE.md) | kiến trúc bộ sinh (thân → khung toạ độ → nét → thời gian → dựng) và hướng **FX đi theo vũ khí** (đường đi mũi vũ khí → các nhát chém; chưa làm) |
| [generators.md](generators.md) | 4 bộ sinh (lưỡi liềm, xoay tại chỗ thường / nặng, chém trước mặt chữ C): tham số, luật rút ra, điểm user chấm, **việc còn thiếu để đạt 9-10/10** |

## Tóm tắt

**Bản gốc đã dựng lại** (bộ tool `lib-fx/_core/formulas/vector`, profile trong `profiles/`):

| Mẫu | Profile | Bản gốc | Showcase | User |
|---|---|---|---|---|
| xoáy chém lửa, băng | `swirl-slash` | `ref/vfx/swirl-slash/` | [showcase/swirl-slash](../../../../results/vector-showcase/swirl-slash/) | 9, 9-10/10 |
| nhát chém xanh, hồng, vàng + phản chiếu | `slash-trio` | `ref/vfx/slash-trio/` | [showcase/slash-trio](../../../../results/vector-showcase/slash-trio/) | đạt |

**Hiệu ứng sinh mới** (`vectorfx.py gen-slash NAME --style ...`, chi tiết [generators.md](generators.md)):

| Tên | Kiểu | User |
|---|---|---|
| `gen-slash-blue` | lưỡi liềm (v0) | 7/10 |
| `gen-slash-loop-blue` | xoay tại chỗ, vòng quanh thân, bản thường | 9-10/10 |
| `gen-slash-loop-heavy-blue` | xoay tại chỗ, vũ khí lớn (trọng kiếm, đại đao, katana) | 9-10/10 |
| `gen-slash-front-heavy-blue` | một nhát trước mặt, chữ C hở, vũ khí lớn | 9-10/10 |
| `gen-slash-x-gold` | chém đôi chữ X tuần tự, vàng (theo ảnh tham chiếu + bản mô tả) | chưa chấm |
| `gen-slash-combo-blue` | combo 2 nhát: quét ngang + bổ xuống đất có toé | chưa chấm |

User (2026-11-09): sáng tạo slash đơn bằng tool đã khá ổn. Câu hỏi mở: slash theo quỹ đạo vẽ trước cho một nhân vật (xem `generators.md`).

**Luật cốt lõi** (chi tiết và số đo trong hai file trên):
- Sinh từ một đầu nét và **dài ra theo đường quét**; bùng 1-3 frame; tàn nhanh (diện tích ×0,3 mỗi frame ở bản gốc); vẽ on ones, on twos ở tia cuối.
- Lớp sáng ở mặt ngoài / đầu nét, lớp tối ở mép trong và đuôi; nhiều sợi, đầu nét chổi khô; độ dày theo phối cảnh nếu đường chém là vòng elip.
- Tàn bằng **vết cắt và lỗ** (44-64%), không chỉ mòn mép; sau đỉnh sợi **giãn trước, đứt sau**, mỗi sợi đứt ở chỗ riêng.
- **Glow giữ sáng tới cuối** trên tia và mảnh (khác lửa phun).
- **Phản chiếu dưới sàn** = cùng nét, lật, dẹt ~1/4, tối và nhạt hơn, cùng nhịp.
- Vũ khí lớn: lưỡi rộng hơn ~2-2,7 lần, ít sợi đậm, đầu cùn, vụn to, giữ 2 frame lúc lấy đà và lúc va chạm.

- **Review ở cỡ game**: mọi slash phải được xem ở H = 60 px @1x (nhân vật game), không chỉ ở khung 600-1100 px (chuyên gia, 2026-11-10).

Hướng đi hiện tại: Milestone 01, nhát chém xéo đồng bộ kiếm nhân vật thật ([docs/pipeline/pose-pair-fx-method.md](../../../../../../docs/pipeline/pose-pair-fx-method.md)).

Luật chung cho mọi loại VFX (lớp, nét mịn, cấp bậc màu, vòng đời, ánh sáng): [../../README.md](../../README.md) và 01-05.

## Theo loại vũ khí (kind `slash`, tham số `weapon`)

Nguyên tắc: mọi chi tiết và mọi pha tàn sống trong toạ độ nét (`v` dọc cung, `c` ngang nét), không dùng nhiễu trong không gian màn hình. Vệt là một bó
sợi dọc song song với cung; khi tàn, mỗi sợi mỏng dần về đường tâm của nó và đuôi rút lên theo luật riêng (`c.rng("strand", j)`), nên chỉ còn vài nét dài,
mảnh, cùng hướng. Không lỗ, không mảnh vụn, không hoa văn.

| Vũ khí | Hình | Pha tàn |
|---|---|---|
| `sword` (kiếm, đao) | 3 sợi khít nhau (khoảng 50/30/20 %), mép ngoài là một cung sạch, không răng, 2 sợi tóc mảnh ngoài mép; rộng 46 | 3 nét dài mảnh dần, sợi ngoài (mép sáng) hết sau cùng |
| `axe` (rìu) | 4-6 dải song song cách nhau khe cố định 6-10 % bề rộng, dải rộng hẹp khác nhau; ngắn (phủ 70 % cung), dày (80), đầu tù | từng dải ngắn dần từ đuôi, dải mảnh hết trước |
| `saw` | như kiếm, mép trong có răng đều (`teeth=6`) | như kiếm |

Hiệu ứng: `crescent`, `heavy`, `thrust` là kiếm; `axe`, `axe_heavy` là rìu. Khe giữa các dải rìu bị quầng sáng lấp nếu glow đầy: kind giảm glow còn 0.5 và Ink làm mịn nhẹ.

### Luật đã được người dùng xác nhận (góp ý 2026-11-13, sau khi xem trang duyệt fxkit)

1. **Kiếm, đao = nét mịn cùng hướng.** Một cung liền, không để lại "hoa văn" ngoằn ngoèo khi tàn, không răng cưa mặc định.
2. **Rìu = dải song song.** Các vết cách nhau bởi khe, ngắn và dày hơn kiếm; từng dải tàn riêng.
3. **Vệt phải theo bề mặt lưỡi quét**, không phải một parabol giữa hai mũi đao: chuôi đi một đường, lưỡi xoay quanh chuôi, mũi vẽ cung của nó
   (`--track`, `FXKIT.md` mục 6). Mép dẫn của vệt đầy phải trùng lưỡi ở pose cuối.

## Theo mặt phẳng vung (`--swing`; `sweep`, `diag_down`, `diag_up`)

Cú vung nằm trong một mặt phẳng; máy quay cao, chếch xuống, nên hình ta thấy là **hình chiếu** của đường tròn mũi vũ khí vẽ quanh vai (mô hình trong `layers/slash.py`, `plane_point`):
- **bổ dọc / hất lên** (mặt phẳng song song màn hình, `k = 1`): cung tròn đầy đủ, toàn bộ ở trước thân (`melee/slash/swing` + `--track`);
- **chém ngang** (`k = 0.3`, `sweep`): ellipse cao / rộng ~ 0,3, gần thành một đường; nửa đi sau thân (xa) mảnh và nguội, vẽ SAU thân; nửa đi trước (gần) dày và sáng, vẽ ĐÈ lên thân;
- **chém xéo** (`k = 0.6`, `roll = +-35`, `diag_down` / `diag_up`): ellipse dẹt vừa, xoay nghiêng; từ cao phía sau xuống thấp phía trước, hoặc ngược lại.
Luật: nét dày mỏng theo gần xa (xa 0,3 - gần 2,4 lần nét tối thiểu, nội suy theo `k`), không biến mất ở chỗ nhìn từ cạnh; nửa xa không có mép trắng; hai đầu vệt thon nhọn.
Số đo đã đạt (2026-11-14, 15 fps, S2b): `sweep` (u0 = 175, u1 = 460, `w_near` = 12, release 0,33) quét ngang qua trước ngực (phần gần dài 1,4 - 1,5 lần bán kính), cao / rộng 0,32 - 0,40, nét gần dày 16 - 18 px, gấp 3,6 - 6 lần nét xa; (S2, 2026-11-13: `sweep` cao / rộng 0,31, nét gần dày gấp 2,6 nét xa); `diag_down` 1,09, `diag_up` 1,0 (khung bao ở khung trúng đòn). Chi tiết: `lib-fx/_plans/slash-round-02/S2-swing-planes.md`.
**Khớp vào điểm đo (`--swing "tip_a=...;tip_b=...;pivot=..."`, 2026-11-14)**: thay cho u0 / u1 / r đặt tay. Mũi ở pose A, mũi ở pose B và trục quay (tâm thân ở độ cao lưỡi) đều là điểm đo trên hai ảnh; với `k` đã chọn mỗi mũi cho ra góc và bán kính của riêng nó theo công thức đóng (`fit_swing` trong `layers/slash.py`), nên mép ngoài của vệt đi đúng qua cả hai mũi. `pivot_b` cho trục dịch theo thân giữa hai pose; `root_a` / `root_b` (đầu chuôi của phần lưỡi nhìn thấy) làm mép trong và mép trắng nằm đúng trên đường lưỡi của từng pose, độ dày vệt ở hai đầu bằng chiều dài lưỡi nhìn thấy; `via=near|far` chọn nửa đi qua. Thử trên pose chém ngang đã duyệt của `azure_blade` và một cặp điểm tự nghĩ: `docs/pipeline/pose-pair-fx-method.md` mục 10.
**Ba pose, vệt đọc được hướng (`tip_c`, 2026-11-14, sửa thứ tự cùng ngày)**: luật rút ra từ lần chấm: vệt chém ngang chỉ có hai pose A, B (đầu A và đầu B là hai đầu của lưỡi bề mặt quét, nhìn gần như cạnh) mảnh dần về phía mũi nên đọc như sao chổi có đầu ở phía dày, tức phía TRÁI (ngược). Muốn đọc xuôi: (1) có pose C ở điểm gần nhất của cung (lưỡi chỉ vào người xem, rút ngắn, chúc xuống ảnh) và khớp ellipse qua ba mũi, ba khoá theo THỨ TỰ ĐI (`tip_a` đầu, `tip_b` giữa, `tip_c` cuối); pose C là pose GIỮA của cung 180 độ qua nửa gần và pose CUỐI của cung 270 độ qua nửa xa (azure_blade chọn cung 270 độ: trái -> nửa xa -> phải (B) -> vòng nửa gần về người xem (C, trúng đòn), góc 180 -> 368 -> 450, k khớp 0.195); (2) **đầu dày nhất, sáng nhất, cụt, có mép trắng chạy dọc mép ngoài của nét (không phải thanh ngang qua nét); đuôi là kim mảnh tan trước; bề dày tăng đơn điệu từ đuôi tới đầu**, nét mở theo pháp tuyến của đường mũi chứ không theo lưỡi chiếu, và 20 % cuối xoay về đường lưỡi để nhát cắt đầu không gập qua đường đi nơi ellipse dẹt rẽ gắt; (3) đầu phải DI CHUYỂN qua các khung (khung 1 lát mỏng trên lưỡi A, khung 2 đầu ở B sau khi đi qua nửa xa, khung 3 đầu ở C rồi tan đuôi trước): một vệt hiện đủ trong một khung thì không có đầu để mắt đi theo. Đoạn B -> C chạy từ phải sang trái trên màn hình nên dễ đọc ngược: đầu cụt sáng + đuôi kim mỏng nằm SAU đầu và rút trước là thứ làm nó đọc đúng. Chi tiết, số đo, lệnh: `lib-fx/_core/formulas/draw/FXKIT.md` mục 6 và `docs/pipeline/pose-pair-fx-method.md` mục 10.6.
Còn mở: rìu theo mặt phẳng (S3), thử cặp chém xéo thật.
