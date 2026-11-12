# Slash: các bộ sinh (hiệu ứng mới, không có bản gốc)

Kiến trúc chung của các bộ sinh và hướng "FX đi theo vũ khí": [ARCHITECTURE.md](ARCHITECTURE.md).

Mọi bản sinh ra đi qua cùng đường dựng như các bản dựng lại: nét thon (`strokes.py`) → `smooth_simplify` → tô chồng lớp + glow (`compose`)
→ PNG / SVG / GIF (`gen_render.render_sequence`). Các khung chính được viết dưới dạng **tham số nét theo từng hình vẽ** (đầu / đuôi nét, độ
dày, độ giãn sợi, độ đứt), nên các frame ở giữa liền mạch theo cấu tạo.

Lệnh chung: `python lib-fx/_tools/vectorfx.py gen-slash NAME --style STYLE [--variant blue|pink|gold] [--frame SEED]`.
Kết quả: `lib-fx/_study/NAME/` (git bỏ qua) và bản lưu trong git `lib-fx/_core/results/vector-showcase/generated/NAME/`.
Trang xem: Blue Horizontal Slash https://claude.ai/artifact/WSPsgRkzRos6fW6BfDrsNM (v0), Blue Loop Slash
https://claude.ai/artifact/2zSWrndFyafkCGZ6a328CM (3 bản dưới đây).

## 1. Danh sách

| Tên (thư mục showcase) | `--style` | Kiểu | Mã | Frame (gồm frame trống cuối) | User chấm |
|---|---|---|---|---|---|
| `gen-slash-blue` | `crescent` | lưỡi liềm một nét, 2 lớp | `gen_slash.py` | 13 | 7/10 ("nét quá đơn giản, hình đơn điệu"; màu và chuyển động ổn) |
| `gen-slash-loop-blue` | `loop` | **xoay tại chỗ**, vòng quanh thân, bản thường | `gen_slash_loop.py` (`STYLES["light"]`) | 14 | 8-9/10 (trước khi thêm phản chiếu); "khá đẹp" sau phản chiếu + khép vòng; dày hơn (v1.8): **ổn**; chốt **9-10/10** |
| `gen-slash-loop-heavy-blue` | `loop-heavy` | **xoay tại chỗ**, vũ khí lớn | `STYLES["heavy"]` | 16 | "khá đẹp"; +40% dày (v1.8): **ổn**; chốt **9-10/10** |
| `gen-slash-front-heavy-blue` | `front-heavy` | **một nhát trước mặt**, chữ C hở, vũ khí lớn | `STYLES["front-heavy"]` | 16 | **ổn**; chốt **9-10/10** |
| `gen-slash-combo-blue` | `combo` (`--dummy`) | **combo 2 nhát**: quét ngang sát thân, rồi bổ từ sau lưng xuống đất xa phía trước, có toé | `gen_slash_combo.py` | 22 | bản 1 "cũng được, chưa đúng tỷ lệ"; bản 2 chưa chấm |
| `gen-slash-x-gold` | `x` (`--scale --rotation --duration-ms --fps`) | **chém đôi chữ X tuần tự**, vàng, 550 ms, khung trên nền đen (additive) + `sheet.png`, `fx_meta.json` | `gen_slash_x.py` | 16 (+1 trống) | bản 1 sai (thiếu ảnh tham chiếu); bản 2 chưa chấm |

Ý tưởng (chỉ lấy ý, không đồ): `ref/vfx/axe-swing-idea/reference.png` (người cầm rìu vung ngang, nhát chém vòng elip phối cảnh).
Bảng màu và glow (cả 4 bản): đo trên slash-trio xanh: sâu [52,104,168], xanh [106,190,255], băng [227,251,253]; glow nhoè 2 tầng σ 8,6 / 51,4.

## 1b. Combo nhiều nhát (`gen_slash_combo.py`, 2026-11-09)

Ý tưởng: `ref/vfx/spear-combo-idea/spear-moves.png` dòng 1 (thương; kiếm, đao như nhau) và `sword-motion-sketch.png` dòng 1-2 (chuyển động).
Trang: Spear Combo Slash https://claude.ai/artifact/6XeNBdLFJbwNAS9BwEuqYp.

- **Mỗi nhát một khung toạ độ riêng** (`render_sequence` nhận danh sách khung; mỗi nét có `"frame": i`; vết cắt chỉ cắt nét cùng khung, nhát này
  không cắt nhát kia). Mỗi nhát dùng lại nguyên ngôn ngữ sợi của `gen_slash_loop.drawing` với một dòng `STYLES` riêng (`combo-sweep`,
  `combo-smash`) và một bảng thời gian riêng có **frame chung** của combo (`T_SWEEP`, `T_SMASH`).
- **Nhát 1, quét ngang**: elip dẹt (k 0,26) nghiêng −0,10 (lên về bên phải), đi qua phía xa: nét dài mảnh, dày và móc xuống ở bên phải.
- **Nhát 2, bổ xuống**: cung trong mặt phẳng đứng (k 0,90, không phối cảnh: `back = front = 1`, nét tóc tối thiểu `min_w` 2,5), từ sau lưng
  trên cao qua đầu xuống đất trước mặt; **đầu nét dừng ở mặt đất** (`head` giữ nguyên sau va chạm, đuôi đuổi theo); va chạm giữ 2 frame.
- **Toé lúc chạm đất** (`SPLASH`): 10 gai cong theo hướng bổ (nhiều về phía trước, vài cái thấp ra sau), nét toả từ điểm chạm trong khung tròn
  riêng; gai to có lõi băng; vệt loang dẹt dưới đất; sau va chạm gai **rời đất bay ra** (bán kính trong tăng) và mỏng dần.
- **Nhịp combo**: nhát 1 đỉnh ở frame 3, tàn 4-11; nhân vật lấy đà 4-7; nhát 2 sinh ở frame 8 **khi nhát 1 còn đang tàn** (gối lên nhau, không
  có khoảng trống), chạm đất 11-12, tàn tới 20.
- **Màu theo ảnh ý tưởng**: thêm lớp tím dưới cùng. Dải chính đi vào lớp tím cả dải; một dải băng mới bắt đầu từ 42% chiều dài, thon dần vào trên
  nó, nên đầu nét băng / xanh, mép và đuôi tím (bước màu phẳng, không gradient).
- Chưa tốt: tím mới ở mép và đuôi mảnh (ảnh ý tưởng tím cả nửa sau nét); gai toé hơi đều nhau, chưa có giọt nhỏ; vệt loang bị phản chiếu che.

**Bản 2 (user: "chưa đúng tỷ lệ, quẹt ngang thì gần thân, đập thì xa thân hơn"):**
- **Mọi vị trí tính từ thân nhân vật**: `H` (chiều cao thân, 170 px), `FEET` (điểm chân = điểm neo lib-fx / `fx_layers.py`), quay về +x.
  Luật tỉ lệ cho combo cận chiến:

| | Tâm | Tầm với | Ghi chú |
|---|---|---|---|
| Quét ngang | ngực: chân + (0,25 H, −0,62 H) | bán kính 1,05 H, dẹt 0,30, nghiêng −0,12 | ôm thân: phía xa đi sau vai, móc ra trước ở ~1,3 H |
| Bổ xuống | vai: chân + (0,05 H, −0,80 H) | chạm đất ở **1,75 H** trước chân; cung cao (dẹt 0,85), bắt đầu −125° (sau, trên) | xa thân hơn hẳn nhát quét; bán kính tự tính từ vai tới điểm chạm |
| Độ rộng lưỡi | | quét 0,22 H, bổ 0,32 H | nhát bổ nặng hơn |

- **Hình nộm xem thử** (`dummy.py`, cờ `--dummy`): người que phẳng cầm thương **dài cố định 1,35 H**; mũi thương bám theo đầu nhát chém đang
  chạy; tay trượt dọc cán (gần thì cầm giữa cán, xa thì vươn tay tới 0,6 H); giữa hai nhát mũi thương vòng qua đầu ra sau (nội suy góc quanh
  vai). Vẽ **dưới** hiệu ứng, ra thư mục riêng `lib-fx/_study/<name>/dummy/` và `showcase/.../preview_dummy*.gif`; hiệu ứng sạch không đổi.
  Dùng được cho mọi bộ sinh: `render_sequence(..., backdrop=lambda f: ảnh RGB)`.

## 1c. Chém đôi chữ X tuần tự (`gen_slash_x.py`, 2026-11-10)

Đề bài: bản mô tả của một AI khác (task "Sequential Double Slash X-shaped VFX": hướng, thứ tự, timeline 550 ms, 3 lớp, hạt, tiêu chí nghiệm thu)
+ ảnh tham chiếu `ref/vfx/x-slash-gold/reference.webp` (10 frame). Trang: X Double Slash https://claude.ai/artifact/JrmYvD4FCabP17GaeLUyVP.

- **Bài học (bản 1 bị user dừng):** làm chỉ theo lời tả thì sai hình: hai nét gần thẳng, cùng phình xuống, mảnh. **Luôn hỏi / chờ ảnh tham chiếu
  khi đề bài nhắc tới nó**, rồi đọc hình từ ảnh (chiều phình, độ cong, chỗ dày nhất) trước khi viết code. Bản mô tả còn tự mâu thuẫn (ghi phương
  "\\" cho nhát trên phải → dưới trái): theo điểm đầu / cuối và ảnh, không theo ký hiệu.
- **Hình (đọc từ ảnh):** mỗi nhát là lưỡi liềm ~1/4 vòng (116°), elip dẹt k 0,62 (rộng hơn cao). Nhát 1: tâm vòng ở trên trái điểm giao, chạy
  từ trên phải (gần dựng đứng) xuống dưới trái, phình về dưới phải. Nhát 2: tâm vòng ở dưới trái, chạy từ trên trái (gần nằm ngang) cắm xuống
  dưới phải, phình về trên phải. **Bán kính thay đổi dọc đường đi** r(s) = R·(0,70 + 0,60 s) cho nhát 1 (cuộn gắt ở đầu, duỗi dài về sau),
  R·(1,30 − 0,60 s) cho nhát 2; r(0,5) = R nên điểm giao đứng yên. Nét dày nhất ở 1/3 đầu, kim dài về phía đầu nét đang chạy. Spine của mỗi nét
  lấy theo r(s) tại chính đoạn nét phủ (`_sp`), nên đường cong không xê dịch khi nét dài ra.
- **Lớp:** viền cam, thân vàng, lõi trắng vàng nằm lệch vào phía trong lưỡi liềm; 2 cung phụ mảnh (một ngoài gần chỗ bắt đầu, một trong lùi sau
  đầu nét); viền đứt 2 chỗ ở nửa đuôi; tia lửa hình thoi (glint) để lại cạnh đường đi, trôi theo hướng chém, sống ~170 ms.
- **Thời gian theo ms** (hàm `state(ms)`), lấy mẫu theo fps; đổi `--duration-ms` là co giãn cả timeline. Nhát 1: 0-120 ms dài ra, 120-240 mờ còn
  40 %, giữ 40 %. Nhát 2: 200-340 ms; đầu nét qua giữa (~238 ms) thì nổ impact (tâm hình thoi + 4 tia dọc hai hướng chém + 2 tia ngắn + hạt).
  340-390: chữ X, nét rộng thêm 16 %. 390-550: tan (hạt, viền cam, thân vàng, lõi cuối cùng).
- **Độ đục từng lớp, glow theo độ đục** (`render_sequence(layer_opacity=..., halo_weight=...)`): lớp đã mờ cũng phát sáng ít đi (chỉ bật cho
  bộ sinh, profile dựng lại giữ luật cũ).
- **Xuất cho game:** khung trên nền đen (additive: nền đen không cộng gì), `sheet.png` (1 hàng) + `fx_meta.json` (fps, số frame, cỡ, điểm neo =
  điểm giao, blend). Repo chưa có runtime game: scale / rotation / opacity áp dụng lúc vẽ, hoặc sinh lại với `--scale`, `--rotation`.

## 2. Hai cách dùng của dạng loop (user, 2026-11-09)

- **Xoay tại chỗ (spin)**: người cầm vũ khí xoay một vòng tại chỗ; nhát chém là **vòng elip quanh thân**, ngang thắt lưng, khép kín ở đỉnh.
  Sau đỉnh phần còn lại co về một bên thành hình chữ C. Dùng cho chiêu xoay, chém quét quanh mình.
- **Chém trước mặt (front)**: một nhát vung ngang **trước mặt**, không vòng qua sau lưng. Chữ C **hở hơn** (~230°, không bao giờ khép), tròn
  hơn (elip ít dẹt), nhỏ hơn, nằm phía trước người (bên phải màn hình), miệng chữ C mở về phía người. Đúng hình vẽ 3-4 của ảnh ý tưởng.

## 3. Tham số các kiểu (`gen_slash_loop.STYLES`)

| | light (spin) | heavy (spin) | front-heavy |
|---|---|---|---|
| Độ rộng lưỡi `width` (đơn vị vòng) | 47 (v1: 36; user: dày hơn) | 98 (v1: 70; user: +40%) | 86 |
| Elip: tâm, bán kính, dẹt `k`, nghiêng | (480,190), 380, 0,24, −0,04 | như light | (500,205), 300, **0,42**, −0,06 |
| Điểm bắt đầu `u_start` | −172° (sau, trái) | −172° | −150° |
| Đầu nét ở đỉnh | 6,6 rad (≈ 378°: **khép vòng**) | 6,6 rad | 4,0 rad (≈ 229°: **C hở**) |
| Phối cảnh (hệ số độ dày sau / trước) | 0,30 / 2,4 | 0,42 / 2,2 | 0,45 / 1,6 |
| Đầu nét chổi khô | 4 ngón nhọn, khác dài | 3 ngón to, cùn | như heavy |
| Răng khía | 6, cỡ 0,6-1,6 | 5, cỡ 1-2 | như heavy |
| Vệt tốc độ | 3 mảnh | 2 đậm | 2 đậm |
| Vụn | 14-30 px | 26-52 px | như heavy |
| Nhịp | on ones tới tàn; 3 hình cuối giữ 2 frame | **lấy đà giữ 2 frame, va chạm (đỉnh) giữ 2 frame** | như heavy |
| Khung ảnh, sàn phản chiếu | 960×460, y 338 | 960×460, y 360 | 960×480, y 392 |

Bảng thời gian (`TIMELINE`, `TIMELINE_HEAVY`, `TIMELINE_FRONT`): mỗi dòng một hình vẽ: `head` / `tail` (rad đã chạy dọc vòng), `w` (độ dày),
`spread` (sợi giãn), `brk` (độ đứt), `frames` (frame hiển thị: 2 frame = giữ).

## 4. Luật đã rút ra khi sinh (theo thứ tự các lần chấm)

1. **Một nhát chém là nhiều sợi**, không phải một khối (v0 = 7/10 vì "đơn giản"): dải sáng chính + dải giữa (xanh) + sợi tối trong cùng + vệt tốc
   độ mảnh trong và ngoài. Đầu nét kiểu chổi khô: 3-4 ngón dài ngắn khác nhau.
2. **Độ dày theo phối cảnh**: phía sau mảnh như sợi tóc (nhưng ≥ ~2 px trên màn hình, nếu không vòng bị đứt), chỗ quay đầu dày và sáng nhất,
   phía trước là dải dày. Vì elip dẹt `k`, độ dày phía trước phải nhân ×1,6-2,4 mới đọc được là dày.
3. **Sau đỉnh: giãn trước, đứt sau**. Các sợi tách nhau theo chiều dài và vẫn liền 1 hình, rồi mới đứt (v0 tách mảnh quá sớm).
4. **Mỗi sợi đứt ở chỗ riêng**, dài ngắn không đều; vết đứt thẳng hàng qua các sợi trông như mã Morse.
5. **Răng khía cắn từ mép trong** (khía hở), đặt theo độ dày tại chỗ; nằm giữa dải thì thành lỗ tròn. Không khía trên phần nét tóc (cắt vụn nét).
6. **Phản chiếu** = vẽ lại **cùng các nét** trong khung lật qua sàn, dẹt ~1/4 (đo trên slash-trio), nên giữ đủ sợi, đứt, nhịp. Màu tối hơn (×0,8),
   bớt bão hoà và kéo 35% về sắc chính (lớp trắng không hoá xám), glow 40%, độ đục 0,9. Nét < ~2 px bị bỏ trong phản chiếu (khi dẹt chúng thành
   chuỗi chấm). Mã: `gen_render.render_sequence(reflection=...)`, `frames.ReflectFrame`.
7. **Khép vòng** (kiểu spin): đầu nét chạy hơn 2π ở đỉnh, đuôi bắt đầu ngay chỗ đầu nét quay về.
8. **Vũ khí lớn** = cùng ngôn ngữ, khác ở: lưỡi rộng ~2-2,7 lần, phía sau dày hơn, ít sợi nhưng đậm, đầu nét cùn, răng và vụn to, **nhịp chậm**
   (lấy đà và va chạm giữ 2 frame).

Kết luận của user (2026-11-09): **sáng tạo một nhát chém đơn bằng tool hiện tại đã khá ổn**; các bản sinh mới được chấm **9-10/10**. Câu hỏi mở tiếp theo (nhát chém theo quỹ đạo
user vẽ trước cho một nhân vật cụ thể): ghi chú trong file này.

## 5. Còn thiếu để đạt 9-10/10 (chưa làm: chỉ làm khi cần đẹp hoàn hảo)

Ghi theo nhận xét của user 2026-11-09 ("khá đẹp, 3 điểm này để làm thêm khi cần"):

1. **Phản chiếu sát sàn đọc như một đường kẻ dài**: phía trước của phản chiếu là dải dẹt dài liền. Hướng sửa: rút ngắn / làm đứt phản chiếu phía
   xa người xem, hoặc giảm độ đục dần theo khoảng cách tới điểm va chạm (slash-trio: phản chiếu ngắn hơn nhát chính).
2. **Sau đỉnh, phần còn lại co về một bên thành chữ C kèm vài vệt cong "(((" ngoài rìa** (kiểu spin): có thể rối. Hướng sửa: bớt vệt tốc độ ở pha
   tàn hoặc cho chúng tan trước thân; xem lại tốc độ đuôi đuổi theo đầu.
3. **Bản nặng chưa có thành phần va chạm**: chỉ khác bản thường ở độ dày và nhịp; chưa có bụi, mảnh đất hay tia lửa lúc va chạm. Hướng sửa: thêm
   lớp phụ (bụi bung ở sàn tại frame đỉnh, 3-6 tia bắn theo hướng chém), luật số lượng / thời điểm cần đo trên 2-3 GIF tham khảo.

Khác (nhỏ): ở bản front-heavy vài răng khía đọc như vạch nhỏ trên lớp xanh; đầu nét ở bản spin chạy sát mép trái khung.
