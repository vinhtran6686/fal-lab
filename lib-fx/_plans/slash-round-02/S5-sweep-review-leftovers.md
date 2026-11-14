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
