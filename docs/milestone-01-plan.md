# Milestone 01: kế hoạch chính thức (Character-Synchronized Diagonal Slash)

> **Trạng thái: ĐÃ CHỐT KẾ HOẠCH, chờ user duyệt chi phí.** Viết 2026-11-10 từ bản nháp v0, theo trả lời của chuyên gia
> ([milestone-01-advisor-review.md](milestone-01-advisor-review.md), nguồn quyết định; lệch nhau thì file đó đúng). Hướng đi:
> [milestone-01-character-synced-slash.md](milestone-01-character-synced-slash.md). Gate 0 đã xong (0 USD). **Chưa gọi API, chưa bắt đầu Gate 1.**

## 0. Mục tiêu và phạm vi

Sản phẩm cuối: **Holy Commander chém xéo một nhát, VFX sinh từ quỹ đạo kiếm thật, đồng bộ với chuyển động**, tách lớp, xem được ở cỡ game.

Không làm: tự động tracking, Trajectory / Timeline / Composition Editor tổng quát, refactor nhánh VFX, generator ngoài một slash thử nghiệm, sửa
`dummy.py`, sửa animation đã duyệt, ghi đè asset cũ (`attack_side`, `radiant_slash` ...), nới canvas 176×140, đăng ký vào thư viện `lib-fx/`.
Bước hiện tại chưa đạt thì không làm bước sau; mỗi lần hỏng ghi **nguyên nhân / kết quả / hướng chỉnh** vào `out/heroes/holy_commander/history.md`.

## 1. Quy ước của thử nghiệm

| Thứ | Quy ước |
|---|---|
| Gốc | pivot chân (0,5; 0,88) của cell 176×140 @1x (352×280 @2x) |
| Trục | x về trước (phải), y lên trên |
| Đơn vị | **H = 55,5 px @1x = 111 px @2x** (`body_height_2x`). Lưu cả `tier_H_px: 60`, `body_height_px: 55.5`, `coordinate_H_px: 55.5` |
| Đổi px → H | đo trên frame **đã export** `frames/attack_diag_side/frames/@2x/` (sau body_rescale + neo chân), không đo trên clip thô: `x_H = (px − 176) / 111`, `y_H = (246.4 − py) / 111` |
| Thời gian | ms tính từ frame 0 của state đã export. State này dùng **nhịp đều 67 ms / frame** (15 fps, như mọi recipe hiện có); `ms = frame × 1000 / 15`. Nếu sau này đổi nhịp từng frame thì ms lấy theo tổng `durationsMs` của recipe |
| Khoảng trống cell | trên chân 123,2 px @1x ≈ 2,22 H; trước / sau 88 px ≈ 1,59 H. **Không vừa thì dừng và hỏi user**, không nới canvas (nới là sửa lại mọi state đã duyệt, như lần 156 → 176) |

## 2. Gate 0: tái sử dụng (ĐÃ XONG, 0 USD)

Bằng chứng: [milestone-01/gate0_reuse.png](milestone-01/gate0_reuse.png).

| Pose | Kết luận | Căn cứ |
|---|---|---|
| **P3 (kết thúc)** | **Tái dùng `source/design/pose_skill_radiant_slash_v01.png`**, không tạo mới | đã duyệt 8,5/10 (history 2026-10-19); prompt chính là "the END of a two-handed downward chop: body leaning forward, both hands low in front, blade pointing forward and down diagonally to the right near the ground, front foot forward"; cùng nền magenta, cùng framing 70%, ref master_v07; độ dài kiếm khớp master bằng mắt (~210 vs ~220 px trên ảnh 1024). Đúng đủ 5 ý P3 của chuyên gia |
| **P1 (chuẩn bị)** | **Phải tạo mới (1 ảnh fal-image)**; frame `attack_side` chỉ làm tham khảo tư thế | clip thô `attack_side_attack_t04.mp4` (832×480, 24 fps) frame 8-10 có tư thế kiếm sau đầu, chưa có vệt cung; nhưng: ảnh mờ nén 480p (nhân vật cao ~270 px kể cả kiếm), lưỡi nhòe chuyển động ở f9-f10, **mặt / mũ bị tay che** (master thấy mặt), kiếm nằm ngang sau đầu chứ không "cao sau vai, mũi lên". Frame đã export của `attack_side` (frame 3-4 @1x) còn dính vệt cung. Không đủ làm frame đầu sạch cho video |
| P2 | không tạo | chỉ khi video cho thấy model không nội suy được nhát chém |

## 3. Gate 1: P1 (fal-image, TỐN TIỀN)

- `scripts/gen_image.py`, `gpt-image-2` edit, `--quality low`, 1024×1024, `--ref master_v07`, **1 ảnh mỗi lần**.
- Prompt: lấy nguyên sidecar `pose_skill_radiant_slash_v01.json` (cùng khối design, style, camera / góc xoay 30°, nền magenta, **"filling about 70% of the
  frame"**, "keep inside the frame") để P1 cùng tỷ lệ với P3; chỉ thay đoạn tư thế: kiếm giơ cao phía sau vai, mũi hướng lên và hơi ra sau; thân xoay nhẹ,
  nghiêng về sau lấy lực; chân trước bước lên; hai tay cầm chuôi; **mặt vẫn thấy được**; mũi kiếm trong khung có lề. Tùy chọn (hỏi user khi duyệt chi phí):
  thêm frame t04 f8 làm `--ref` thứ hai **chỉ để lấy tư thế** (CLAUDE.md cho phép khi user đồng ý).
- Kiểm tra (contact sheet P1 cạnh P3, **chồng lên nhau**: đường chân, chiều cao thân, độ dài kiếm, hướng nhìn phải, xoay 30°): chênh chiều cao thân và
  độ dài lưỡi ≤ ~5%; mũi kiếm P1 khi đặt vào cell còn trong 2,22 H phía trên chân. Chấm ≥ 8/10.
- Tối đa 3 ảnh; ảnh hỏng thì ghi nguyên nhân rồi mới tạo ảnh kế. **User duyệt P1 + P3 trước Gate 2.**
- Lưu `source/design/pose_slash_diag_p1_v01.png` (+ `.json`); dòng manifest mới trong `brief.md`.

## 4. Gate 2: clip `attack_diag_side` (video-sprite, TỐN TIỀN)

- Route **written-prompt** (`video-sprite` SKILL.md bước 5): `python scripts/fal_video.py video --prompt-file P.txt --reference p1.png --last-frame p3.png
  --duration 4 --resolution 480p`; hai ảnh keyed, đặt giữa cùng canvas magenta 1820×1024 như các clip trước của hero này. Model `h3-max-turbo`.
- **Thời lượng 4 s** (mặc định skill; hai clip thân sạch gần nhất radiant v2 t01, charge v4 đều 4 s).
- Prompt take 1 theo **công thức beat-by-beat đã cho thân sạch** (radiant v2 t01, charge v4): khoá hướng nhìn phải, các beat theo thứ tự (đứng ở P1, giữ
  ngắn → vung kiếm một lần từ trên-sau xuống dưới-trước, bước tới, chỉ thân về trước → dừng ở P3, giữ yên), câu "locked tripod", chỉ chuyển động tiến,
  danh sách cử chỉ cấm; không có từ hiệu ứng nào ngoài một câu "body motion only".
- **Đạt** khi: một nhát chém xéo rõ, kiếm luôn thấy, cùng cỡ thân (không zoom), không quay lưng, **không có bất kỳ vệt / cung / ánh sáng nào do model
  vẽ**. Khác với `attack_side` (user đã chấp nhận vệt cung ở đó, history 2026-10-20): **ở `attack_diag_side` vệt cung = KHÔNG ĐẠT**, vì VFX phải sinh từ
  quỹ đạo.
- **Hướng chỉnh take 2 (quyết trước)**, theo lỗi của take 1:
  - có vệt / cung: viết lại beat vung chỉ bằng vị trí tay, khuỷu, góc lưỡi ở đầu và cuối beat; bỏ các từ gợi hiệu ứng (slash, swing, strike, chop) và bỏ
    danh sách phủ định có gọi tên "arc / crescent" (t04 có đủ danh sách đó mà vẫn vẽ cung);
  - không ra nhát chém rõ / vung sai hướng: thêm vị trí kiếm giữa đường bằng lời ("ngang vai phải"); nếu vẫn hỏng thì đó là căn cứ để xin tạo P2;
  - zoom / đổi cỡ: kiểm tra lại P1 vs P3 (tỷ lệ, vị trí chân) trước khi quay lại.
- Một clip mỗi lần, user duyệt mỗi take. **Hai take liên tiếp không đạt: dừng**, review choreography với user / chuyên gia. Trần cứng 4 clip.
- Chọn frame: clip thô → **frame tuner** (`tools/frame_tuner/`) chọn đoạn chuẩn bị → vung → kết thúc, nhịp đều 67 ms, mục tiêu **0,8-1,2 s**
  (12-18 frame), user chọn **frame chạm** (`hit`) bằng mắt → `frames/export_recipe.json` mục mới → `apply_recipe.py` xuất `attack_diag_side`
  (176×140, cùng cỡ thân). `attack_side` không đổi. Chạy `motion_check.py`.

## 5. Gate 3: quỹ đạo kiếm (0 USD)

- Công cụ: **một trang HTML nhỏ** trong `scripts/experiments/milestone_01/annotate/`, chỉ cho milestone này: hiện từng frame @2x phóng 3-4×, click Root
  rồi Tip, vẽ đoạn Root-Tip, bật / tắt từng sample, ô `visible`, ô `side` (front / back so với thân, đánh giá bằng mắt, dùng cho Gate 5), ô note; tự đổi
  sang H theo §1 và **tự lưu** (cùng cơ chế frame tuner: artifact có db, Claude đọc lại) → `source/vfx/slash_diag/weapon_track.json`.
- Đánh dấu **mọi frame** của đoạn vung (dự kiến 5-8) + 1-2 frame sau chạm. Kiếm che / mờ: `visible: false`, không đoán. Sample nội suy (nếu có) mang
  `estimated: true`, không bao giờ dùng để chấm tiêu chí 3.
- `weapon_track.json`: `state`, `cell`, `pivot`, `fps`, `tier_H_px`, `body_height_px`, `coordinate_H_px`, `hit_frame`, `samples[{frame, ms, root, tip,
  visible, side, note}]`.
- Vận tốc mũi: sai phân trên **các sample quan sát liên tiếp**, `v_i = |tip_i − tip_{i−1}|` (H / frame). Ghi `peak_speed_frame` cạnh `hit_frame` do
  user chọn; lệch > 1 frame thì ghi chú và hỏi user.
- **Fit elip** (helper riêng trong `scripts/experiments/milestone_01/`, `EllipseFrame` chỉ dùng để vẽ): elip có 5 bậc tự do (tâm 2, bán kính, k, nghiêng)
  mà chỉ có 5-8 điểm, nên fit tự do gần như luôn "đạt". Vì vậy: nếu số điểm < 8, cố định k theo cung chém hiện có hoặc giữ tâm trong vùng vai / tay
  cầm, và **báo sai số leave-one-out** (bỏ từng điểm, fit lại, đo điểm bị bỏ). Báo cáo ghi: số điểm, số bậc tự do, mean / max (fit) và mean / max (LOO).
  Gate: **mean ≤ 0,08 H, max ≤ 0,15 H** trên sai số LOO. Không đạt → cubic Bézier / đường cong tự do, chỉ trong thư mục thử nghiệm.
- Xuất cho user duyệt: contact sheet frame + Root / Tip / đoạn kiếm / frame index / ms; biểu đồ quỹ đạo Tip (H); báo cáo fit. **User duyệt trước Gate 4.**

## 6. Gate 4: VFX riêng (0 USD)

- Code: `scripts/experiments/milestone_01/` (ví dụ `slash_from_track.py`), import Vector Kit (`gen_slash_loop`, `gen_render`, `frames`, `strokes`), không
  sửa core, không sửa generator cũ (chạy lại một slash cũ, so pixel để chắc không đổi).
- Hình: phương án C. Đầu dẫn = Tip mỗi frame (`tip_offset_ratio = 0`); đường giữa theo quỹ đạo đã fit; width độc lập; Root chỉ cho hướng lưỡi.
- Thời gian: bắt đầu ở frame đầu tiên có `v ≥ max(0,2 × v_peak, 0,1 H/frame)` (ghi frame + ms thực tế); đầu nét không đi trước kiếm; sau chạm giữ 1
  frame, giãn / phân rã, tan trong 3 frame (thử 4 nếu quá nhanh).
- Màu vàng / trắng, 2-3 lớp (core sáng, main vàng, outer vàng cam nhẹ), glow nhỏ. Dựng @2x, downsample ra @1x từ cùng geometry. Nét chính ≥ 1,5 px @1x;
  chi tiết mất ở @1x thì bỏ.
- Alpha: thêm phần xuất RGBA trong suốt (alpha theo coverage của geometry, tham khảo `tools/frame_tuner/export_fx.py`), chỉ trong thư mục thử nghiệm.
- Tham số trong `source/vfx/slash_diag/slash_params.json`. Ba biến thể, mỗi cái đổi đúng một tham số: width, length, curvature.
- Xuất: GIF chỉ VFX, PNG trong suốt, 3 biến thể cạnh nhau, preview @1x thật + phóng 3× (nearest). **User duyệt trước Gate 5.**

## 7. Gate 5: ghép và chấm (0 USD)

- Lớp theo che khuất thật (trường `side` của sample): luôn trước thân → chỉ `front`; có đoạn sau thân / cape → tách `back` + `front`.
- Xuất `frames/fx/slash_diag/` (`front/`, `back/` nếu cần; `frames/@1x`, `@2x`; preview; `fx.json` cùng dạng `radiant_slash`: pivot, blend `screen`,
  lớp, frame n ↔ frame n của thân). Dòng `fx.slash_diag` trong `meta.json`, dòng manifest trong `brief.md`.
- Preview: body + VFX GIF @1x, GIF 3×, recipe JSON; một lệnh dựng lại toàn bộ từ `weapon_track.json` + `slash_params.json`.
- Chấm 6 tiêu chí (§8), ghi kết quả + bài học vào `docs/milestone-01-character-synced-slash.md` §7, `lib-fx/_core/vector/STATUS.md`,
  `lib-fx/_core/vector/CHANGELOG.md`. Dọn `source_prune.py` (cẩn thận lỗi đã biết với tên `_p<N>`), commit, push.

## 8. Tiêu chí đạt (chốt)

| # | Tiêu chí | Đo thế nào | Đạt |
|---|---|---|---|
| 1 | Choreography | user xem GIF @1x | một nhát chém xéo rõ, không có chuyển động thừa |
| 2 | Tách VFX | lớp riêng, bật / tắt từng lớp; thân không có vệt model | VFX tách hoàn toàn |
| 3 | Đồng bộ vũ khí | đầu dẫn ↔ Tip đã đánh dấu; tiếp tuyến tại sample đủ điều kiện | ≤ 0,1 H và ≤ 15° tại mọi sample quan sát được (bỏ `visible: false`, `estimated`) |
| 4 | Tham số độc lập | 3 biến thể width / length / curvature | mỗi biến thể đổi đúng một tham số, phần còn lại giữ nguyên |
| 5 | Đọc ở cỡ thật | GIF @1x, H = 55,5 px (bậc M 60 px) | nét chính ≥ 1,5 px @1x; user nhận ra hướng và hình chém không phóng |
| 6 | Tái tạo | một lệnh từ `weapon_track.json` + `slash_params.json` | ra đúng frame, không sửa tay |
| gate fit | chọn elip hay đường tự do | sai số LOO | mean ≤ 0,08 H, max ≤ 0,15 H (không thay tiêu chí 3) |

## 9. Chi phí (giá từ `out/costs.csv`: ảnh 0,014 USD; clip `h3-max-turbo` 480P 0,015 USD/s → 4 s = 0,06 USD)

| Đợt | Nội dung | Dự kiến | Trần |
|---|---|---|---|
| Gate 1 | P1, từng ảnh một | 0,014 (1 ảnh) | 0,042 (3 ảnh) |
| Gate 2 | clip 4 s, từng clip một | 0,06 (1 clip) | 0,12 trước khi bắt buộc dừng review; trần cứng 0,24 (4 clip) |
| Gate 3-5 | code, 0 USD | 0 | 0 |
| **Tổng** | | **~0,07-0,13** | **~0,28** |
| (điều kiện) P2 | chỉ khi video không nội suy được; xin duyệt riêng | | +0,014-0,042 |

Mỗi lệnh tốn tiền vẫn hỏi user trước theo `CLAUDE.md` (duyệt đợt một lần, mỗi take vẫn review trước khi gọi take kế).

## 10. Checklist

- [x] Chuyên gia trả lời Q1-Q12; ghi vào `docs/milestone-01-advisor-review.md`; kế hoạch chốt (file này)
- [x] **Gate 0**: P3 = `pose_skill_radiant_slash_v01`; P1 thiếu; t04 f8-f10 chỉ tham khảo (`docs/milestone-01/gate0_reuse.png`)
- [ ] User duyệt kế hoạch + chi phí (Gate 1, Gate 2)
- [ ] **Gate 1**: tạo P1 (≤ 3 ảnh); contact sheet chồng P1 / P3; ghi `history.md`, manifest `brief.md`; **user duyệt**
- [ ] **Gate 2**: clip take 1 → review (thân sạch, không vệt, cỡ thân, nhát chém) → user duyệt / retry theo §4; frame tuner chọn đoạn + hit; xuất
      `attack_diag_side`; `motion_check.py`; ghi `history.md`, `meta.json`, manifest; **user duyệt**
- [ ] **Gate 3**: trang đánh dấu; `weapon_track.json`; contact sheet Root / Tip; biểu đồ Tip; vận tốc + peak; fit elip (LOO); **user duyệt**
- [ ] **Gate 4**: bộ sinh thử nghiệm; `slash_params.json`; VFX RGBA @2x / @1x; 3 biến thể; preview @1x + 3×; kiểm tra slash cũ không đổi; **user duyệt**
- [ ] **Gate 5**: lớp front (/ back); `frames/fx/slash_diag/` + `fx.json`; GIF @1x, 3×; một lệnh dựng lại; chấm 6 tiêu chí; cập nhật docs; dọn; commit, push
