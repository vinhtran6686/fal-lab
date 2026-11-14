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

### Giá trị cuối cùng (người làm: S2b, 2026-11-14)
`sweep`: **u0 = 175, u1 = 460, w_near = 12, release = 0,33** (k = 0.3, blade = 0.75, ease = 1.3 giữ nguyên). Mới thêm: khoá `w_near` của dict `swing`; hệ số tan `(R / 120) ** 0.5` trong nhánh mặt phẳng vung; tham số `release` (mặc định 0,36) và `sparks` (cung bay của `scraps` / `streaks`, mặc định như cũ) của `_plane_effect`. `diag_down`, `diag_up` giữ `w_near` = 0 (công thức cũ), `release` 0,36, sparks cũ.

Ảnh (thư mục tạm, không ghi vào `out/`; thư mục scratchpad của session, có thể bị dọn):
- trước / sau, r = 85, 6 khung đầu, trên thân `azure_blade`: `/tmp/claude-0/-home-user-fal-lab/0d4327dc-c403-51b7-8868-48c89542b69c/scratchpad/s2b/before_after_r85.png`
- lưới 6 khung r = 85 / r = 120 (sau): `.../s2b/t8_r85.png`, `.../s2b/t8_r120.png`; khung trúng đòn phóng 300 %: `.../s2b/t8_zoom.png`; lưới trước: `.../s2b/before_r85_grid.png`, `.../s2b/before_r120_grid.png`
- khung dựng: `.../s2b/before/{r85,r120,left85}` (mốc) và `.../s2b/t8/{r85,r120,left85,solo_r85,solo_r120}` (sau).

### Số đo (15 fps, khung trúng đòn h = `hit_frame` trong `meta.json` = 2, 1-based; alpha >= 128; ghép lên khung 1 của `skill_crescent_puppet_side`, vai (140, 160))
Mốc trước khi sửa (`u0 = 215`, `u1 = 410`), r = 85: `front/` 567 điểm, `back/` 279 (tỉ lệ 2,03); `front/` dài 57 px = 0,67 r; cao / rộng 0,335; `fxcheck`: pop (khung 3 -> 4 mất 47 %); A(h+1)/A(h) = 0,98, A(h+2)/A(h) = 0,51, A(h+3)/A(h) = 0,05; cung phần gần phủ: từ u = 0 tới 50° (u1 410 -> 50°). r = 120: front 1016, back 556, `front/` dài 0,48 r, cao / rộng 0,31, tỉ lệ A 0,69 / 0,41 / 0,10.

Sau khi sửa:
| tiêu chí | r = 85 | r = 120 | quay trái r = 85 |
|---|---|---|---|
| `front/` / `back/` (điểm) | 1462 / 294 = 4,97 | 2160 / 265 = 8,15 | 1474 / 294 = 5,01 |
| `front/` dài ngang / (r * s) | 128 px = 1,51 | 164 px = 1,37 | 1,51 |
| cao / rộng khung bao | 0,392 (67 / 171) | 0,318 (77 / 242) | 0,398 (68 / 171) |
| bề dày lớn nhất phần gần (đường kính nội tiếp, nét riêng không scraps / streaks) | 16 px | 18 px | - |
| gần / xa | 3,58 | 6,36 | - |
| A(h+1) / A(h) | 0,71 | 0,69 | 0,74 |
| A(h+2) / A(h) | 0,31 | 0,28 | 0,31 |
| A(h+3) / A(h) | 0,00 | 0,00 | 0,00 |
| `fxcheck` | chỉ cảnh báo `linger` (4 khung cuối < 2 %); không pop, không cut | như vậy | như vậy |
- Cung phần gần phủ: từ u = 0 (trước mặt) tới 100° (u1 = 460), tức đi hết phần trước ngực và dừng ở phía gần hơi về sau.
- Ảnh gương: IoU mặt nạ (khung trúng đòn, quay trái lật so với quay phải, cho phép lệch 1 px) = 0,987. Mốc trước khi sửa: 0,978.
- Hai đầu: đuôi vệt nhọn như kim (xem `t8_zoom.png`); đầu vệt (bên trái, gần eo) vẫn mang bề rộng lưỡi và dải `edge` trắng nằm trong vệt như cũ (không thò ra); đầu này không nhọn hơn bản cũ (thiết kế của chế độ theo dõi: "đầu giữ bề rộng lưỡi").
- Ảnh ghép: lưới 6 khung "trước" và "sau" cạnh nhau: lưỡi quét ngang qua trước ngực từ khung 2, rồi tan thành nét mảnh ở khung 4, rỗng ở khung 5.
- Không hồi quy (hash SHA-256 của mọi png dựng, so trước / sau khi sửa, dựng hai lần giống nhau): `crescent`, `heavy`, `thrust`, `axe`, `axe_heavy` (30 fps, `--from 40,100 --to 200,140`), `swing --track` (15 fps, lệnh trong HANDOVER mục 5): **giống hệt**. `diag_down`, `diag_up` ở r = 120 giống hệt; ở r = 85 đổi (xem dưới).
- `python lib-fx/build.py melee/slash --check`: không FAIL (xong, thoát 0; thư viện có `sweep` dựng lại, `lib-fx/catalog.json` đổi theo). `python lib-fx/_tools/fxkit_test.py`: xem dòng cuối của mục này.

### Lệch so với task và lý do
1. **`u0 = 175` thay vì 245** (task: 245, tối đa 255). Với 245 / 460 cao / rộng là 0,59 (r = 85) và 0,51 (r = 120). Quy tắc của task (giảm `u1`, tăng `u0`) đi sai hướng: tăng `u0` đưa điểm bắt đầu về phía xa nhất (u = 270), làm vệt cao thêm và hẹp đi (quét lưới u0 215 / 235 / 245 / 225 x u1 430 / 445 / 460, cao / rộng 0,45 - 0,59 cho r = 85). Chỉ hạ `u0` (đuôi kéo dài ra sau lưng) đưa tỉ lệ xuống <= 0,40: u0 = 195 cho 0,399, 185 cho 0,385, 175 cho 0,392 khi có sparks bay về sau. Hệ quả: vệt bắt đầu ở sau lưng nhân vật (x ~ -r), khung trước đòn là một chấm xanh nhỏ nằm sau lưng cách thân ~ 0,9 r (xem khung 1); `u1` giữ 460 (đo: u1 = 430 cho `front/` dài 0,72 r < 0,9; u1 = 445 cho 0,95 r, sát giới hạn; 460 cho 1,2 - 1,5 r và vệt đi hết qua điểm gần nhất u = 90).
2. **`w_near = 12` thay vì 16.** Mạch task: `w_near` thay hằng `wmin` (7 px) làm bề dày nhỏ nhất, đặt 16. Nhưng `wmin` bị nhân `mfac` (tới 2,4 ở chỗ gần nhất), nên phần gần ra 38 px, và cách đo của tôi (đường kính nội tiếp mặt nạ alpha >= 128 ở khung trúng đòn) ở mốc đã cho 16,5 px (r = 85), không phải 10 - 12 như task ghi. Tôi định nghĩa `w_near` là bề dày nét ở chỗ gần nhất (px ở s = 1, trước hệ số phối cảnh 1,16) và hạ sàn `wmin * mfac` của phần gần để không làm dày thêm (phần xa không đổi: `4,5 px` ở r = 85 so với 4,5 trước đó). Với 14 thì đo ra 20 px (> 18); 12 cho 16 (r = 85) và 18 (r = 120), vào khoảng 14-18.
3. **`release = 0,33` (hạ) thay vì 0,36 -> tối đa 0,42.** Sau khi nhân `(R / 120) ** 0.5` (làm vệt nhỏ tan chậm hơn), A(h+1) / A(h) ở r = 85 là 0,76 (hơi quá 0,75); không còn `pop`. Tăng `release` làm tan chậm hơn nên sai hướng; hạ xuống 0,33 cho 0,71 / 0,69 (đo 0,30: 0,68 / 0,64 nhưng A(h+2) của r = 120 thành 0,11, quá nhanh). `release` chỉ áp cho `sweep` (tham số mới, mặc định 0,36 cho `diag_*`).
4. **Cung bay của `scraps` / `streaks` của `sweep` đổi** thành `(150, 215)` / `(160, 200)` (bay về sau, tiếp nối chiều đi của mũi lúc u = 100°). Với `u1` = 460 điểm cuối của mũi nằm cạnh eo, và cung cũ (về phía trước, lên) làm tia trắng cắt chéo qua thân ở khung 4. Không có trong task; không đụng `diag_*`.
5. **`diag_down`, `diag_up` ở r = 85 đổi nhẹ** do hệ số tan `(R / 120) ** 0.5` (bước 3 áp cho cả nhánh mặt phẳng vung, đúng như task). Tỉ lệ A (h+1 / h+2 / h+3): `diag_down` 0,76 / 0,41 / 0,16 -> 0,78 / 0,43 / 0,17; `diag_up` 0,58 / 0,25 / 0,09 -> 0,59 / 0,26 / 0,12; `fxcheck` sạch trước và sau. `diag_down` ở r = 85 đã nhỉnh quá 0,75 từ trước (0,76). Ở r = 120 cả hai giống hệt (hash).
6. Khung trúng đòn: lấy `hit_frame` của `meta.json` (1-based, = 2) làm h; chỉ số `peak@2` / `pop: frame 3 -> 4` của `fxcheck` đếm khác (khung 3 -> 4 = h+1 -> h+2).
7. `parse_swing` trong `build.py` (dòng lệnh `--swing`) không nhận `w_near`: không nằm trong danh sách file được sửa; khoá này chỉ đặt qua dict trong `slash.py`.

### Chưa đạt / cần người chấm xem
- Cao / rộng r = 85: 0,392 (bản quay trái 0,398): sát giới hạn 0,40; sparks có thể làm vượt (cung `(165, 225)` cho 0,414).
- Khung 1 (trước đòn) là một chấm xanh nằm sau lưng nhân vật (hệ quả của u0 = 175); nếu không muốn, phải đổi `k` hoặc giảm yêu cầu cao / rộng.
- "Đầu vệt nhọn" chỉ đúng cho đuôi; đầu giữ bề rộng lưỡi (theo thiết kế chế độ theo dõi).
- Chưa thử trên cặp pose thật của chém ngang (cần sinh ảnh, tốn tiền).
