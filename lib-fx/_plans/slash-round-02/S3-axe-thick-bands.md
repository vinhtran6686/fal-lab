# S3: rìu dày hơn: ít dải, dải rộng (bỏ kiểu răng lược)

Nguồn: đánh giá của người dùng ("rìu = dải song song, phải dày") và lần dựng lại của người lập kế hoạch 2026-11-14 (`axe`, `axe_heavy`, 15 fps): vệt rìu đọc như **răng lược**:
5-6 sọc mảnh xen khe, nhiều sọc chỉ vài px. Rìu phải là **ít dải và dải to**, khe hẹp nhưng nhìn rõ, đầu tù.
**Chạy song song với S5**: S3 chỉ sửa hai file dưới; S5 không đụng chúng. Không sửa file nào khác.

## Nguyên nhân trong code
`lib-fx/_core/formulas/draw/fxkit/layers/slash.py`:
- dòng 135: `strands = 5 if axe` (và `axe_heavy` đặt 6 ở `lib-fx/melee/slash/slash.py` dòng 38): quá nhiều dải cho bề rộng 80-104 px;
- dòng 299-303: bề rộng mỗi dải `rng.uniform(0.55, 1.6)` rồi chuẩn hoá: dải nhỏ nhất chỉ ~1/3 dải lớn nhất, tức 5-8 px ở `width` 80: thành sọc tóc;
- dòng 405-412: lớp `deep` (tông tối bên trong) vẽ một vạch tối trong dải đầu, thêm một "sọc" nữa cho mắt.

## File được sửa
- `lib-fx/_core/formulas/draw/fxkit/layers/slash.py`: **chỉ nhánh `axe`** (các dòng có `if axe` / `axe` trong biểu thức). Nhánh kiếm, `saw`, `track`, `swing`, `lead` không đổi một byte đầu ra.
- `lib-fx/melee/slash/slash.py`: chỉ các khai báo `axe`, `axe_heavy` (dòng 32-38) và lớp `echo` của chúng (dòng 66-67) nếu cần.
- `lib-fx/_core/formulas/rules/vfx/slash/README.md`: dòng `axe` của bảng (dòng 56) và dòng 78 ("Còn mở"): ghi số mới.
- Dựng lại thư viện cho hai hiệu ứng rìu: `lib-fx/melee/slash/axe/`, `lib-fx/melee/slash/axe_heavy/`, `lib-fx/catalog.json`, gallery của họ `melee-slash` (do `build.py` tự ghi).

## Thay đổi (giá trị cụ thể)
1. Số dải mặc định của rìu: `strands = 3 if axe` (dòng 135); `axe_heavy`: `"strands": 4` (dòng 38).
2. Bề rộng dải (dòng 300): `ws = [rng.uniform(0.85, 1.25) for _ in range(K)]` (dải nhỏ nhất ≥ 0,68 dải lớn nhất).
3. Khe (dòng 301): `gaps = [rng.uniform(0.10, 0.14) for _ in range(K - 1)]` (khe đủ rộng để quầng 0.5 không lấp).
4. Rìu không có lớp `deep` thành vạch trong dải: ở khối `tones >= 2` (dòng 403), với `axe` thì `fr = 0.25` và chỉ vẽ ở **dải rộng nhất** (thay vì dải 0). Mục đích: tông tối là mảng nền trong dải to, không thành một sọc nữa.
5. Pha tàn giữ luật "dải mảnh hết trước" (`phi = 1 - ws[j] / wmax` không đổi). Với 3 dải gần bằng nhau, thứ tự tàn vẫn theo bề rộng.
6. Nếu sau 1-5 vệt mảnh hơn trước (tổng diện tích giảm > 15 % so với bản cũ ở khung trúng đòn): tăng `width` mặc định rìu 80 -> 88 (dòng 133) và `axe` trong `slash.py` 80 -> 88. Không tăng quá 96.
Chỉnh trong khoảng: `strands` 3-4 (rìu), 4-5 (rìu lớn); `ws` từ (0.8, 1.3) đến (0.9, 1.2); `gaps` 0.09-0.15. Ghi mọi lần thử vào "Kết quả".

## Lệnh
```
python lib-fx/build.py melee/slash/axe --from 40,100 --to 200,140 --fps 15 --out <tạm>/axe
python lib-fx/build.py melee/slash/axe_heavy --from 40,100 --to 200,140 --fps 15 --out <tạm>/axe_heavy
python lib-fx/build.py melee/slash/axe          # cập nhật thư viện (30 fps mặc định), tương tự axe_heavy
```
Mốc trước khi sửa: dựng cùng các lệnh trên từ commit hiện tại (`git stash` hoặc worktree) vào `<tạm>/before/`.

## Tiêu chí nghiệm thu (khung trúng đòn, 15 fps, alpha >= 128, px @2x)
- **Số dải đếm được**: trên 5 lát cắt vuông góc với cung ở 30, 40, 50, 60, 70 % chiều dài, số đoạn liền (dài ≥ 3 px) = `strands` (rìu 3, rìu lớn 4) ở ít nhất 4/5 lát.
- **Dải to**: đoạn nhỏ nhất trên lát 50 % ≥ **14 px** (rìu) và ≥ 15 px (rìu lớn). **Khe nhìn thấy**: mỗi khe trên lát 50 % ≥ 5 px với alpha < 128.
- Tổng diện tích không giảm quá 15 % so với mốc; hình bao (cao, rộng) lệch ≤ 10 % so với mốc.
- Pha tàn: A(h+1)/A(h), A(h+2)/A(h) không lệch quá 0,1 so với mốc; dải hẹp nhất tắt trước (ghi khung tắt của từng dải). `fxcheck` không FAIL, không cảnh báo mới (mốc `axe` đã có `cut` ở 15 fps: không được tệ hơn).
- Xem ảnh: lưới khung trúng đòn tới h+4, mốc trên / mới dưới, cả `preview_game.gif`: đọc là 3-4 dải dày song song, đầu tù, không thấy sọc tóc.
- **Không hồi quy**: hash ảnh @2x của `crescent`, `heavy`, `thrust` (30 fps, `--from 40,100 --to 200,140`), `sweep`, `diag_down`, `diag_up` (15 fps, `--from 140,160 --to 225,160 --split`),
  `swing --track` (lệnh trong `HANDOVER.md` mục 5) và `sweep` ba điểm (lệnh vệt trong `S4b-sweep-export.md` bước 2, `--out <tạm>`) giống hệt trước khi sửa.
- `python lib-fx/build.py melee/slash --check` không FAIL; `python lib-fx/_tools/fxkit_test.py` qua. Commit + push lên `ccr-38411bc5-l13uki` (kéo về trước khi push: S5 chạy cùng lúc), đánh dấu ô S3 trong `PLAN.md`.
- Không sửa `out/`, không công cụ tốn tiền, không đọc `.env`.

## Báo cáo (điền dưới đây)
Giá trị cuối cùng; bảng số dải / bề rộng dải / khe trên 5 lát cho cả hai hiệu ứng (mốc và mới); diện tích, hình bao, tỉ lệ tan; hash hồi quy; đường dẫn lưới so sánh; lệch so với task và lý do.

## Kết quả

**Giá trị cuối** (số dải, bề rộng, khe, `echo` trong `layers/slash.py` và `melee/slash/slash.py`):
- `slash.py`: `strands = 3 if axe`, `ws` 0,85-1,25, `gaps` 0,11-0,15 (task 0,10-0,14; chỉnh trong khoảng cho phép 0,09-0,15), `deep` chỉ ở dải rộng nhất với `fr = 0.25`, quầng `glw` 0,5 -> 0,3 (lệch, xem dưới), `width` mặc định rìu 80 -> 96. Phi tàn không đổi.
- `melee/slash/slash.py`: `axe` width 96, linger 4,0; `axe_heavy` width 112, **strands 3** (không phải 4), linger 4,6; lớp `echo` đổi từ `sword` thành `axe` một dải (`span` 1,0, `strands` 1): axe bend 0,55 width 44; axe_heavy bend 0,58 width 42.

**Mốc** dựng từ commit `89bc573` (trước khi sửa), 15 fps, `--from 40,100 --to 200,140`. Khung trúng đòn = khung đỉnh diện tích (axe tệp 3, axe_heavy tệp 4; `hit_frame` trong meta là khung t = 0 nên không dùng). Số đo trên alpha >= 128 @2x, 5 lát cắt vuông góc đường cung ở 30..70 % (đoạn >= 3 px).
| | mốc axe | mới axe | mốc heavy | mới heavy |
|---|---|---|---|---|
| diện tích khung đỉnh | 8462 | 7653 (-9,6 %) | 8474 | 7844 (-7,4 %) |
| hình bao (rộng x cao) | 177x135 | 161x145 (-9,0 / +7,4 %) | 192x140 | 189x153 (-1,6 / +9,3 %) |
| A(h+1)/A(h), A(h+2)/A(h) | 0,961 / 0,683 | 0,903 / 0,644 | 0,806 / 0,501 | 0,784 / 0,537 |
Số đoạn trên 5 lát (gộp cả `echo`): mốc axe 1,1,1,1,1; mới axe 4,3,3,3,2; mốc heavy 2,2,2,2,2; mới heavy 3,3,3,3,3.
Chỉ lớp `slash` (không `echo`, `--only slash`): mới axe 3,3,3,3,3 (lát 50 %: 15,2 / 17,8 / 15,2 px, khe 6,8 / 7,8 px), mới heavy 3,3,3,3,3 (lát 50 %: 14,8 / 19,5 / 15,5 px, khe 10,8 / 10,5 px); mốc axe 5,3,3,3,3 (đoạn 6-10 px, khe 0,2-3,8), mốc heavy 6,6,7,7,6 (đoạn 5-10 px).
Lát 50 % khi gộp `echo`: axe 37,5 (echo + dải ngoài) / 18,0 / 15,2, khe 6,0 / 7,8; heavy 30,0 / 19,5 / 15,8, khe 7,0 / 10,2.
Dải tắt (số mẫu bật theo từng dải, axe): khung 6 -> 7: 315/453/219 -> 60/172/57, hết ở khung 8; dải giữa (rộng nhất) giữ lâu nhất, hai dải ngoài / trong tắt trước một chút nhưng cùng khung cuối (ba dải gần bằng nhau). heavy: 383/472/278 -> 209/372/180 -> 32/119/21, hết ở khung 9.
`fxcheck`: axe còn `cut` ở khung 7 (15 % đỉnh, mốc 16 %, không tệ hơn), heavy sạch như mốc.

**Không đạt / lệch so với task**
1. `axe_heavy` dùng 3 dải, không phải 4: với 4 dải, khe 0,09-0,15 và width <= 120 cho dải nhỏ nhất chỉ 7-13 px, không thể >= 15 px (thử 4 dải width 112 và 120, 5 dải width 120). 3 dải width 112 cho 14,8 px khi chỉ tính lớp `slash` và 15,5 khi gộp `echo`.
2. Lớp `echo` kiểu kiếm (bend 0,46 width 40, đục) phủ kín khe ở mọi lát nên bị đổi thành một dải rìu cong hơn. Hệ quả: khi đếm cả `echo`, axe chỉ có 3 đoạn ở 3/5 lát (30 % tách riêng ra 4 đoạn, 70 % `echo` lấp khe đầu nên còn 2): không đạt "4/5". Đường `echo` và đường dải gặp nhau ở đầu vệt nên không thể tách đều ở cả 5 lát (đã quét bend 0,50-0,62 và width 26-46). axe_heavy đạt 5/5 nhưng khe đầu ở lát 60-70 % chỉ 2,8 và 0,2 px. Số đo "đúng" cho yêu cầu dải là số của lớp `slash` riêng (5/5, đều đạt).
3. `width` axe 96 (task: 88, tối đa 96) và quầng 0,5 -> 0,3: cần để dải nhỏ nhất >= 14 px và để khe >= 5 px (alpha < 128; quầng 0,35-0,5 lấp khe ở khung đỉnh). Quầng yếu hơn là nhìn thấy rõ ở `preview_game.gif`.
4. Khoảng khe 0,11-0,15 thay 0,10-0,14; thêm `linger` (axe 4,0; heavy 4,6) để tỉ lệ tan không lệch quá 0,1 và `cut` không tệ hơn mốc.
5. `sweep` ba điểm khác hash so với mốc: do `build.py` của S5 (đổi `streaks` của ba pose: n=2, length 40...), đã kiểm: dựng bằng mã `slash.py` cũ + `build.py` hiện tại cho đúng hash của bản mới. Bảy lệnh còn lại (crescent, heavy, thrust, sweep, diag_down, diag_up, swing --track) giống hệt từng byte ảnh @2x.
6. "Dải hẹp nhất tắt trước" chỉ đạt một phần: ba dải gần bằng nhau (phi <= 0,21) nên cả ba cùng hết ở một khung (axe khung 7, heavy khung 8); dải giữa (rộng nhất) giữ lâu hơn một chút, hai dải còn lại mỏng nhanh hơn.
7. `fxcheck` ở 30 fps trong thư viện: `axe` mốc và mới đều không cảnh báo; `axe_heavy` mốc có `cut` (khung 16 còn 8 %), mới `cut` (còn 7 %): không có cảnh báo mới. Ở 15 fps `axe` có `cut` ở cả mốc (16 %) và mới (15 %).
8. Lưới so sánh (mốc trên, mới dưới, khung đỉnh tới đỉnh + 4, @2x) và số đo là tệp / script tạm, không đưa vào repo: `/tmp/claude-0/-home-user-fal-lab/0d4327dc-c403-51b7-8868-48c89542b69c/scratchpad/grid_axe_hit_h4.png`, `/tmp/claude-0/-home-user-fal-lab/0d4327dc-c403-51b7-8868-48c89542b69c/scratchpad/grid_axe_heavy_hit_h4.png`; gif cỡ game: `/tmp/claude-0/-home-user-fal-lab/0d4327dc-c403-51b7-8868-48c89542b69c/scratchpad/final3/axe/preview_game.gif`, `/tmp/claude-0/-home-user-fal-lab/0d4327dc-c403-51b7-8868-48c89542b69c/scratchpad/final3/axe_heavy/preview_game.gif` (mốc ở `/tmp/claude-0/-home-user-fal-lab/0d4327dc-c403-51b7-8868-48c89542b69c/scratchpad/before/...`). Gallery `lib-fx/_gallery/` bị git bỏ qua nên không commit.
