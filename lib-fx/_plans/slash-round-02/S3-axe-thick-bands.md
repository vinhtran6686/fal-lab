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
