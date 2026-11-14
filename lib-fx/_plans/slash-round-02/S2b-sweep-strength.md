# S2b. Chém ngang (`sweep`) phải đủ mạnh; nhịp tan theo bán kính

Phụ thuộc: S2 (đã xong). Đọc trước: mục "Nhận xét khi chấm" của `PLAN.md`, hàm `_plane_effect` trong `lib-fx/melee/slash/slash.py`, nhánh `swing` (mặt phẳng vung) của `lib-fx/_core/formulas/draw/fxkit/layers/slash.py`.

## Vấn đề (chấm ngày 2026-11-14, ghép lên dáng đứng của `azure_blade`, vai (140, 160), `--to 225,160`, 15 fps)
1. `sweep` đúng hình học nhưng **yếu**: phần gần (đi TRƯỚC thân: dày, sáng) quá ngắn; nhìn chỉ thấy một đường mảnh sau đầu và một vạch trắng ở bên phải. Người xem phải thấy lưỡi **quét ngang qua trước ngực**.
   Nguyên nhân: `u0 = 215`, `u1 = 410` nên vệt kết thúc ở góc 50° (mới sang phần gần được 50°); bề dày tối thiểu phần gần nhỏ.
2. Với nhân vật cỡ game (bán kính `r` ≈ 85 px) `fxcheck` báo `pop` (khung 3 → 4 mất 47 % ở 15 fps): `linger` và `release` là hằng số, không theo cỡ vệt.

## File được sửa
- `lib-fx/melee/slash/slash.py` (giá trị của `sweep`; nếu cần, của `diag_down`, `diag_up`)
- `lib-fx/_core/formulas/draw/fxkit/layers/slash.py` (chỉ nhánh mặt phẳng vung: bề dày phần gần, nhịp tan theo bán kính)
- `lib-fx/_core/formulas/draw/FXKIT.md`, `lib-fx/_core/formulas/rules/vfx/slash/README.md` (chỉ khi giá trị ghi trong đó đổi)
Không sửa chế độ cung, chế độ `--track`, các hiệu ứng `crescent`, `heavy`, `thrust`, `axe`, `axe_heavy`, `swing`.

## Dựng mốc (trước khi sửa; giữ ảnh)
```
python lib-fx/build.py melee/slash/sweep --from 140,160 --to 225,160 --pal frost --fps 15 --split --out <tạm>/before
```
Ghép lên `out/heroes/azure_blade/frames/skill_crescent_puppet_side/frames/@2x` khung 1 (`back/` dưới thân, `front/` trên thân, dán tại `meta.json → origin`), xuất lưới 6 khung đầu. Đo và ghi:
số điểm ảnh (alpha >= 128) của `front/` và của `back/` ở khung trúng đòn; góc cung phần gần đang phủ.

## Cách làm
### Bước 1. Kéo dài phần gần của `sweep`
Quy ước góc (S2): 0° = trước mặt, 90° = gần người xem (dưới tâm trên màn hình), 180° = sau lưng, 270° = xa. Vệt đi từ `u0` tới `u1` theo chiều tăng.
- Đặt `u0 = 245`, `u1 = 460` (vệt bắt đầu ở phía xa hơi về sau, vòng qua trước mặt, **đi hết phần trước ngực và dừng ở phía gần hơi về sau**, tức góc 100°).
- Dựng, đo cao / rộng của khung bao ở khung trúng đòn (alpha >= 128). Nếu > 0,40: giảm `u1` từng 10° (không dưới 440) rồi tăng `u0` từng 5° (không quá 255) cho tới khi <= 0,40. Ghi giá trị cuối.
- **Kiểm bằng ảnh ghép**: phần `front/` phải cắt ngang qua thân nhân vật ở độ cao vai / ngực, dài ít nhất bằng bề rộng thân.

### Bước 2. Phần gần dày và sáng hơn
Trong nhánh mặt phẳng vung của `slash.py`, tìm chỗ tính bề dày ngang nét của vệt theo gần / xa (báo cáo S2 mục "Lệch so với task" 1 mô tả công thức đang dùng). Chỉnh sao cho:
- bề dày lớn nhất của phần gần ở khung trúng đòn = **14-18 px * s** khi `r * s` = 85-120 px (hiện ≈ 10-12 px với r = 85); bề dày phần xa giữ nguyên;
- tỉ lệ dày gần / xa >= 2,5;
- hai đầu vệt vẫn nhọn (không thành đầu tù);
- dải `edge` trắng ở lưỡi cuối dài bằng bề dày mới (không thò ra ngoài vệt).
Nếu công thức có hằng số bề dày tối thiểu, đưa nó thành một khoá của dict `swing`: `"w_near"` (px ở s = 1, mặc định bằng giá trị hiện tại để `diag_*` không đổi) và đặt `w_near = 16` cho `sweep`.

### Bước 3. Nhịp tan theo bán kính
Trong nhánh mặt phẳng vung: gọi `Rpx = r * s` (bán kính thật trên màn hình). Hệ số tan `lk` đang lấy từ `linger`; nhân thêm `(Rpx / 120) ** 0.5` (vệt nhỏ tan chậm lại tương ứng, vệt 120 px không đổi).
Kiểm ở 15 fps với `--to 225,160` (r = 85) và `--to 260,160` (r = 120): `A(h+1)/A(h)` trong 0,55-0,75; `A(h+2)/A(h)` <= 0,45; `A(h+3)/A(h)` <= 0,2 (A = tổng alpha khung xuất; h = khung trúng đòn); `fxcheck` không `pop`, không `cut`.
Nếu r = 85 vẫn `pop`: tăng `release` của lớp `slash` trong `_plane_effect` từ 0,36 lên tối đa 0,42 (ghi lại). Không đổi `linger` của `diag_down`, `diag_up` trừ khi phép kiểm trên cho thấy chúng cũng `pop` ở r = 85.

### Bước 4. Kiểm lại hai kiểu xéo
Dựng `diag_down`, `diag_up` với cùng `--from/--to` ở 15 fps trước và sau: nếu không sửa gì liên quan thì khung phải **giống hệt** (so hash); nếu bước 3 làm chúng đổi, ghi rõ và kiểm ba tỉ lệ `A` như trên.

## Tiêu chí nghiệm thu (ghi số vào "Kết quả")
- [ ] `sweep`, khung trúng đòn, r = 85 và r = 120: số điểm ảnh của `front/` >= 2,5 lần của `back/` (alpha >= 128); phần `front/` dài theo chiều ngang >= 0,9 * `r * s`.
- [ ] Khung bao cao / rộng <= 0,40 (alpha >= 128).
- [ ] Bề dày lớn nhất phần gần 14-18 px * s; gần / xa >= 2,5; hai đầu nhọn (xem ảnh phóng 300 %).
- [ ] Nhịp tan ở 15 fps đạt ba tỉ lệ của bước 3 ở cả r = 85 và r = 120; `fxcheck` không FAIL / `pop` / `cut`.
- [ ] Quay trái (`--from 300,160 --to 215,160`): ảnh gương của bản quay phải ở khung trúng đòn (IoU mặt nạ đã lật >= 0,9, cho phép lệch 1 px).
- [ ] Ảnh ghép lên thân: lưới 6 khung đầu, "trước" và "sau" cạnh nhau; nhìn thấy lưỡi quét ngang qua trước ngực rồi tan thành nét mảnh. Lưu thư mục tạm, không ghi vào `out/`.
- [ ] Không hồi quy: `crescent`, `heavy`, `thrust`, `axe`, `axe_heavy` (30 fps) và `swing --track` (lệnh trong `HANDOVER.md` mục 5, 15 fps) cho khung giống hệt trước (so hash).
- [ ] `python lib-fx/build.py melee/slash --check` không FAIL; `python lib-fx/_tools/fxkit_test.py` qua; commit + push; đánh dấu ô S2b trong `PLAN.md`.

## Kết quả (người làm điền: `u0`, `u1`, `w_near`, `release` cuối cùng; số đo từng tiêu chí; đường dẫn ảnh; lệch so với task và lý do)
