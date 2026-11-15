# S5: việc nhỏ còn lại từ review chém ngang ba pose (tài liệu, `meta.json`, test, tia lửa)

Nguồn: review chém ngang A -> B -> C của người lập kế hoạch (2026-11-14) và lần chấm S4b. **Chạy song song với S3**: S5 **không được sửa**
`lib-fx/_core/formulas/draw/fxkit/layers/slash.py`, `lib-fx/melee/slash/slash.py`, `lib-fx/_core/formulas/rules/vfx/slash/README.md` (của S3). Kéo về trước khi push.

## File được sửa
`lib-fx/build.py`, `lib-fx/_tools/fxkit_test.py`, `lib-fx/_core/formulas/draw/FXKIT.md` (mục 6), `.claude/skills/fal-image/action-planes.md`,
`.claude/skills/video-sprite/references/action-planes.md` (chỉ nếu có đoạn trùng phải sửa theo), và việc 6: `out/heroes/azure_blade/frames/fx/sweep/`, `out/heroes/azure_blade/frames/skill_sweep_side/` (dựng lại bằng lệnh có sẵn), `out/heroes/azure_blade/history.md` (một dòng).

## Việc
1. **Tài liệu `action-planes.md`: tên vai trò pose theo thứ tự đi.**
   - Dòng 59, tiêu đề: `## 4. Writing the poses of a move (A = start; two stills: B = end; three stills: B = middle, C = end)`.
   - Dòng 64, cột bảng: `Pose A (start)` và `Pose B (end of a two-still move; MIDDLE of a three-still sweep)`.
   - Dòng 109, mẫu pose A: `POSE A of a two-part horizontal sweep` -> `POSE A (the START) of a three-part horizontal sweep (A start, B middle, C end)`; thêm một câu dưới mẫu: với chuỗi hai pose thì ghi `two-part` và B là cuối.
   - Kiểm: `grep -n "B = end\|Pose B (end)\|two-part" .claude/skills/fal-image/action-planes.md` chỉ còn những chỗ đã ghi rõ "two-still".
2. **Phần trăm trong prompt pose C** (dòng 78, "the tip about 12% of the image height LOWER than the fists"): trái luật 4b.6 / bài học 8.5. Giữ câu (đã chạy được một lần), thêm ngay sau prompt:
   "Exception to rule 4b.6: a percentage worked here because it sets a LENGTH relative to the figure (the wedge), not a position on the canvas; positions on the canvas (feet, boots) still never hold. Check it on the image."
   Thêm cùng ý một dòng vào mục 4b luật 6.
3. **Ghi số khớp vào `meta.json` của vệt** (`lib-fx/build.py`, hàm `kit_variant`, sau `fxkit.render`): khi `fitted`, gọi
   `fit_swing(swing, face, lambda p: p)` (import từ `fxkit.layers.slash`; `face` = `hand` nếu khác `None`, không thì `1 if B[0] - A[0] >= 0 else -1`, đúng luật của `Space`)
   và thêm vào `extra` khoá `"swing_fit"`: `k` (khoá `k` của kết quả nếu có, không thì `swing["k"]`), `u0`, `u1`, `ra`, `rb`, và khi ba điểm thêm `uc`, `rc`, `fc`; số làm tròn 2 chữ số.
   **Kiểm**: chạy lệnh ba điểm của `docs/pipeline/pose-pair-fx-method.md` mục 10.6 (cỡ 0,2): `swing_fit` ra k 0.2 (±0.01, doc ghi 0.195), u 180.0 / 367.7 / 450.0, r 93.8 / 105.1 / 109.7 (±0.2), fc 0.695. Lệch thì `world` không phải đồng nhất: ghi lại và dùng `c.sp.world` tương đương, không đoán.
   Ảnh đầu ra không đổi (hash `frames/@2x` giống trước khi sửa).
4. **Lệnh `rebuild` trong `meta.json` chạy lại được**: dòng 325 `" ".join(sys.argv[1:])` -> `shlex.join(sys.argv[1:])` (thêm `import shlex`). Kiểm: chép chuỗi `rebuild` của một bản `--swing` vào shell, chạy, hash giống hệt.
5. **Định nghĩa phép đo độ dày vệt** vào `FXKIT.md` mục 6 (dưới phần ba điểm), đúng câu:
   "Độ dày dọc vệt (đuôi -> đầu): đo trên phần ĐẶC (alpha > 0,95), đường kính nội tiếp lớn nhất theo 8-16 khoảng của tham số đường đi; bỏ 3,5 % đường đi quanh nhát cắt đầu và quanh chỗ đổi lớp trước / sau,
   và bỏ vùng quay gắt của ellipse (bán kính cong < bề dày nét: hai mép chập lại làm số đo phồng). Không giảm quá 10 % từ đuôi tới đầu. Số đo có quầng (alpha > 0,5) chỉ để tham khảo."
6. **Tia lửa cắt qua chân** (khung trúng đòn +1, +2 của chém ngang): `lib-fx/build.py` dòng 315, ba điểm: `streaks` `n=3, length=62.0, width=3.5, r0=22.0, arc=(75, 115)` -> `n=2, length=40.0, width=3.0, r0=16.0, arc=(80, 110)`.
   Dựng lại vệt và bản ghép bằng đúng lệnh có sẵn: lệnh vệt trong `S4b-sweep-export.md` bước 2 rồi `python out/heroes/azure_blade/source/vfx/sweep/build_sweep.py`.
   **Kiểm** (ô @2x 352x280 của `skill_sweep_side`, khung thân 9-11): số điểm `front/` của vệt có alpha > 0,3 nằm dưới y = 215 giảm ít nhất một nửa so với trước; tổng alpha khung 8 (trúng đòn) giảm ≤ 5 %. Gửi lưới khung 6-12 trước / sau.
   Ghi một dòng `history.md` (đổi tia lửa, lý do). Không đổi file nào khác trong `out/`.
7. **Test** (`lib-fx/_tools/fxkit_test.py`, thêm hàm `test_swing_fit`, gọi trong `main`): dùng lệnh ba điểm của mục 10.6 (qua `fxkit.render` với `swing` dict như `build.py` dựng, hoặc gọi `build.kit_variant` vào thư mục tạm):
   (a) chạy hai lần cùng seed: khung giống hệt; (b) `swing_fit` như việc 3; (c) `hit_frame` = 3, 9 khung; (d) ca hai điểm `lead=1` của mục 10.3 dựng được, `lint` sạch. `say(False, ...)` khi sai.
   Kiểm: `python lib-fx/_tools/fxkit_test.py` qua; cố ý đổi `k` của ca ba điểm thành 0.5 phải làm (b) báo sai (thử rồi trả lại).

## Tiêu chí nghiệm thu chung
- Mọi "Kiểm" ở trên đạt. Hồi quy: hash @2x của `crescent`, `heavy`, `thrust`, `axe`, `axe_heavy` (30 fps), `sweep`, `diag_down`, `diag_up`, `swing --track`, `sweep` ba điểm (trước việc 6) giống hệt trước khi sửa.
  **Lưu ý**: S3 có thể đổi `axe`, `axe_heavy` cùng lúc: so hash rìu với bản ngay trước commit của mình, không với bản của S3.
- `python lib-fx/build.py melee/slash --check` không FAIL; `fxkit_test.py` qua. Không công cụ tốn tiền, không đọc `.env`.
- Commit + push lên `ccr-38411bc5-l13uki`, đánh dấu ô S5 trong `PLAN.md`.

## Báo cáo (điền dưới đây)
Từng việc 1-7: đã làm gì, số kiểm; `swing_fit` in ra; lưới trước / sau việc 6; hash hồi quy; lệch so với task và lý do.

## Kết quả
**Trạng thái: 6/7 việc đạt; việc 6 làm đúng lệnh nhưng "Kiểm" của nó KHÔNG đạt được theo đúng cách đo của task (xem dưới).**
1. `action-planes.md`: tiêu đề mục 4, cột bảng, mẫu pose A đúng câu của task + một câu về chuỗi hai pose. Kiểm: `grep` chỉ còn dòng 59 và dòng 116, đều ghi rõ "two-still" / hai pose. Bản `video-sprite/references/action-planes.md` không có đoạn trùng.
2. Ghi ngoại lệ ngay sau prompt pose C và một dòng ở mục 4b luật 6.
3. `swing_fit` vào `meta.json` (`kit_variant`). `world` của `Space` chỉ là phép tịnh tiến (trừ `origin`) nên `lambda p: p` là tương đương (góc, bán kính, k không đổi). Lệnh 10.6 in ra:
   `{'k': 0.2, 'u0': 180.0, 'uc': 367.69, 'u1': 449.95, 'ra': 93.8, 'rc': 105.12, 'rb': 109.66, 'fc': 0.7}` (fc thật 0.695, làm tròn 2 chữ số ra 0.7). Hai điểm: `k 0.3, u0 180.0, u1 -13.4, ra 93.8, rb 103.6`. Ảnh giữ nguyên (hash @2x trước / sau giống hệt).
   `swing_fit` của `fx/sweep` azure_blade: k 0.18, u 180.0 / 368.54 / 450.07, r 67.9 / 73.12 / 75.84, fc 0.7.
4. `shlex.join` (cả dòng `rebuild` của hiệu ứng cũ ở `main`, cùng lỗi). Kiểm: chạy lại đúng chuỗi `rebuild` của bản ba điểm trong shell: hash 1a69be42646a = bản gốc.
5. Định nghĩa độ dày vào `FXKIT.md` mục 6 (đúng câu của task) + một dòng nói về `swing_fit`.
6. Tia lửa `n=2, length=40, width=3, r0=16, arc=(80, 110)`; dựng lại `fx/sweep` và `skill_sweep_side` (chỉ khung vệt 3-5 = thân 8-10 đổi). **"Kiểm" không đạt theo cách đo của task**: ở `--s 0.707` vệt không bao giờ xuống tới y = 215 của ô thân (ở khung 9-11 chỗ thấp nhất của `front/` là y 207, chân thân ở y 246),
   nên số điểm alpha > 0,3 dưới y = 215 là 0 TRƯỚC và 0 SAU. Số thay thế (khung thân 9-11, `front/`, alpha > 0,3): y >= 200: 117 -> 102 (-13 %); y >= 190: 865 -> 829 (-4 %); riêng lớp `streaks`: 124 -> 88 (-29 %) và 91 -> 76 (-16 %) (đo bằng `--set streaks.off=true`).
   Phần còn lại ở y >= 190 là nét chính (đầu nêm C ở y ~197-203) và `scraps`, không phải tia lửa. Tổng alpha khung 8: 3295.4 -> 3288.5 (-0,2 %, đạt <= 5 %). Không giảm được một nửa chỉ bằng thay số của task; không làm thêm ngoài task.
   Lưới khung 6-12 trước / sau: `/tmp/claude-0/-home-user-fal-lab/0d4327dc-c403-51b7-8868-48c89542b69c/scratchpad/grid_6_12_before_after.png`. `history.md` một dòng. `export_meta.json` giữ nguyên (xem Lệch).
7. `test_swing_fit` trong `fxkit_test.py`: (a) hai lần cùng seed giống hệt, (b) `swing_fit`, (c) `hit_frame` 3 và 9 khung, (d) hai điểm `lead=1` dựng được, lint sạch. Thử `;k=0.5` vào ca ba điểm: (b) báo FAIL (k 0.5, rb 43.46), đã trả lại. `python lib-fx/_tools/fxkit_test.py`: all checks passed (chạy đầy đủ mất khoảng 15 phút).
**Hồi quy** (hash @2x của mọi tệp `frames/back/front`, 15 fps trừ rìu 30 fps): `crescent`, `heavy`, `thrust`, `sweep`, `diag_down`, `diag_up`, `swing --track`, `sweep` hai điểm (có và không `lead=1`) giống hệt trước khi sửa. `sweep` ba điểm đổi (hash 1a69be42646a -> 680da261cd57) CHỈ vì việc 6 (đúng dự kiến: "trước việc 6"). `axe`, `axe_heavy`: đổi do S3, nên so ngay trước commit với `build.py` cũ: giống hệt (axe c74bac9c7428, axe_heavy 5c6de6168cf9). `melee/slash --check` (chạy trên bản sao của `lib-fx` để không đè đầu ra của S3): không FAIL.
**Lệch**: (1) việc 6: xem trên. (2) `shlex.join` cũng áp cho dòng `rebuild` của hiệu ứng cũ. (3) `build_sweep.py` (ngoài danh sách) lấy chuỗi `rebuild` của vệt rồi tự thêm dấu nháy, nên với chuỗi đã có nháy `shlex` thì `export_meta.json` ra `"'tip_a=...'"`; tôi khôi phục `export_meta.json` về bản đã commit và không sửa `build_sweep.py`; lần chạy sau của nó sẽ ghi chuỗi nháy kép (nên sửa, ngoài S5). (4) `fx/sweep/meta.json` có `swing_fit` mới và `rebuild` mới do chính lệnh dựng lại sinh.
