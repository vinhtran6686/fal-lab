# S4: chém ngang ba pose: nhịp và rig cho thân (bớt "đơ"), vệt bám tay thật

Nguồn: người dùng duyệt vệt `sweep` ba điểm (2026-11-14) nhưng thấy **thân xoay đơ**. Người lập kế hoạch đo trên bản ghép:
1. Mỗi pose chỉ **1 khung** ở 15 fps (A khung 1, B khung 2, C từ khung 3): không có lấy đà ở A, không nảy khi trúng đòn ở C.
2. Thân nhảy giữa các pose: sau khi căn theo chân, tâm thân B lệch **45,8 px** (px ảnh 1024) sang trái so với A; C lệch thêm (-5,5, -29,6) so với B. Ba ảnh khác cỡ (B to hơn A 4,9 %, C 6,7 %).
3. Không có rig, nên thân không thở, không nén / giãn.
Cách sửa: không sinh ảnh mới. Dựng ba rig một mảnh (Puppet Kit) cùng cỡ, một animation theo **5 pha** của `docs/scripts/puppet_kit/puppet-kit-motion-recipes.md` mục 2,
dùng `shx` (nghiêng quanh chân, chân đứng yên) để thân "đi" về phía thân của pose kế tiếp, rồi dựng lại vệt từ **vị trí lưỡi thật** của rig (sockets), không từ ảnh tĩnh.

## Đọc trước
`CLAUDE.md` (mục Puppet Kit), `docs/scripts/puppet_kit/puppet-kit-motion-recipes.md` (mục 1, 2, 4, 8, 9, 10: chép bảng, không suy lại), `docs/pipeline/pose-pair-fx-method.md` mục 10.6
(số đo ba pose, lệnh ba điểm), mẫu đã chạy: `out/heroes/azure_blade/source/rig/make_rigs.py`, `make_anim.py`, `anims/crescent.json`.

## File được tạo / sửa
- Tạo mới: `out/heroes/azure_blade/source/rig/make_rigs_sweep.py` (ghi `rig_sweep_a.json`, `rig_sweep_b.json`, `rig_sweep_c.json`), `out/heroes/azure_blade/source/rig/make_anim_sweep.py` (ghi `anims/sweep.json`).
  Thư mục `out/` bị git bỏ qua: thêm bằng `git add -f` như các rig cũ.
- `puppet.py track` tự ghi `out/heroes/azure_blade/source/vfx/sweep_puppet*/` và thêm đường dẫn đó vào danh sách giữ của `out/heroes/azure_blade/meta.json`: **chỉ chấp nhận đúng thay đổi thêm vào đó** (kiểm `git diff`).
- **Không sửa** `rig_a.json`, `rig_b.json`, `anims/crescent.json`, ảnh trong `source/design/`, khung trong `frames/` (asset đã duyệt). Không `--export` ra `frames/` khi chưa được người dùng duyệt.
- Không sửa `lib-fx/` hay `scripts/` (nếu bắt buộc phải sửa, dừng lại và ghi vào "Kết quả" lý do).

## Bước
1. **Ba rig một mảnh** (`make_rigs_sweep.py`), mỗi rig: `sources.pose` = ảnh của pose; bones `root` (pivot = ground) > `body` (pivot = ground); một part `whole` (`select: {"rest": true}`, bone `body`).
   Sockets trên bone `body` (px của ảnh gốc của CHÍNH pose đó, đo ở `weapon_marks_sweep.json`):
   | rig | ảnh | `ground` (giữa hai chân) | `unit` | `blade_tip` | `blade_root` | `pivot` |
   |---|---|---|---|---|---|---|
   | `rig_sweep_a` | `pose_skill_sweep_p1_v02.png` | (541.8, 921) | 849.0 | (129, 464) | (393, 483) | (598, 464) |
   | `rig_sweep_b` | `pose_skill_sweep_p2_v03.png` | (438, 940) | 890.8 | (1007, 424) | (662, 416) | (449.0, 409.4) |
   | `rig_sweep_c` | `pose_skill_sweep_p3_v01.png` | (496.25, 952.5) | 906.0 | (502, 537) | (502, 405) | (501.5, 405) |
   `unit` = 849 x (cao của pose / 812): ba pose ra **cùng cỡ** với A (và cùng cỡ thân của các animation khác, `unit` 849). `pivot` của B, C là tâm thân ở độ cao lưỡi / nắm tay (như 10.6).
   **Kiểm**: `python scripts/puppet.py check out/heroes/azure_blade/source/rig/rig_sweep_b.json` (và a, c) không lỗi; ảnh check: chấm sockets nằm đúng mũi, chuôi, tâm thân.
2. **Animation** `anims/sweep.json` (`make_anim_sweep.py`), 15 fps, `loop` false, **`hit_frame` = 8**. `tx`, `ty` không dùng (sẽ làm trượt chân). Track viết theo `K((frame, value[, ease]), ...)` như `make_anim.py`:
   | shot | rig | frames | tracks |
   |---|---|---|---|
   | `wind` (lấy đà + giữ) | `rig_sweep_a` | 6 | `body.sy`: (0, 1.0), (3, 0.955, out), (5, 0.95); `body.sx`: (0, 1.0), (3, 1.022, out), (5, 1.025); `root.shx`: (0, 0), (3, -0.08, out), (5, -0.10) |
   | `cross` (ra đòn) | `rig_sweep_b` | 1 | `body.sy`: (0, 1.03); `body.sx`: (0, 0.985); `root.shx`: (0, 0.10) |
   | `hit` (trúng đòn) | `rig_sweep_c` | 6 | `body.sy`: (0, 0.90), (2, 1.03, out), (4, 1.0, inout); `body.sx`: (0, 1.08), (2, 0.985, out), (4, 1.0, inout); `root.shx`: (0, 0.12), (2, -0.02, out), (4, 0, inout) |
   | `settle` | `rig_sweep_c` | 8 | `body.sy`: `{"base": 1.0, "osc": {"amp": -0.007, "period": 8}}` |
   Tổng 21 khung. Lý do số: mục 2 và 4 của motion-recipes (lấy đà 4 + giữ 2, ra đòn 1, trúng đòn nén 0,90 rồi nảy 1,03, nghỉ thở).
   `root.shx` +0,10 ở B kéo phần trên thân sang phải, về phía thân A (B lệch trái 45,8 px ở độ cao vai ~611 px trên chân: 45,8 / 611 = 0,075), nên chỗ cắt A -> B bớt nhảy mà chân đứng yên.
3. Dựng thử: `python scripts/puppet.py render out/heroes/azure_blade source/rig/anims/sweep.json --sheet skill_sweep_puppet_side --no-export`, mở `.work/puppet/skill_sweep_puppet_side/contact.png`.
   **Kiểm** theo checklist mục 9 của motion-recipes: không chạm mép ô; chân không rời đất, không trượt; cỡ đầu A / B / C lệch ≤ 5 % (đo bề rộng băng đô); khung 8 nén mạnh nhất.
   Thấy giật ở chỗ cắt thì chỉnh theo bảng mục 10 ("Giật ở chỗ cắt pose"), mỗi lần một nấc, ghi lại.
4. **Vị trí lưỡi thật** sau rig: `python scripts/puppet.py track out/heroes/azure_blade source/rig/anims/sweep.json --name sweep_puppet --root blade_root --tip blade_tip`,
   rồi lần hai với `--name sweep_puppet_pivot --root pivot --tip pivot`. Đọc `root_px2x` / `tip_px2x` của **khung 6, 7, 8** (khung cuối của A, khung B, khung đầu của C) trong hai `weapon_track.json`.
   Mốc để so (đổi tay từ số đo, không có shx / nén: k = 120 / 849, ô @2x 352x280, pivot (176, 246.4)):
   `tip_a=117.65,181.81;root_a=154.97,184.49;pivot=183.94,181.81;tip_b=252.64,176.89;root_b=206.16,175.81;pivot_b=177.48,174.92;tip_c=176.76,191.37;root_c=176.76,173.88;pivot_c=176.69,173.88`.
   Số track được lệch khỏi mốc vì shx / nén: dùng **số track**, ghi cả hai vào "Kết quả".
5. **Vệt** (cỡ game: s = 120 / 849 / 0,2 = **0,707** so với bản đã duyệt ở 10.6):
   `python lib-fx/build.py melee/slash/sweep --pal frost --fps 15 --split --s 0.707 --swing "tip_a=..;root_a=..;pivot=..;tip_b=..;root_b=..;pivot_b=..;tip_c=..;root_c=..;pivot_c=.." --out out/heroes/azure_blade/.work/sweep_fx`
   (số từ bước 4: `_a` = khung 6, `_b` = khung 7, `_c` = khung 8). `.work/` không vào git. Vệt có `hit_frame` 3 → **khung vệt n ghép vào khung thân n + 5** (vệt 1 = thân 6, vệt 2 = thân 7, vệt 3 = thân 8).
6. **Ghép và xem** (thư mục tạm, không ghi `frames/`): mỗi khung thân 1-21, `back/` dưới thân, `front/` trên thân, đặt tại `meta.json → origin` của vệt. Xuất `compare.gif` (15 fps) và lưới 21 khung.
   Thêm hàng so sánh: bản cũ (thân A 1 khung, B 1 khung, C giữ) cạnh bản mới.

## Tiêu chí nghiệm thu
- Animation: 21 khung, `hit_frame` 8; chân (điểm giữa hai đáy ủng) không lệch quá **2 px @2x** giữa mọi khung; cỡ đầu lệch ≤ 5 %; không khung chạm mép ô.
- Chỗ cắt: dịch chuyển tâm vai (giữa hai giáp vai) giữa khung 6 -> 7 và 7 -> 8, px @2x: **nhỏ hơn bản không có `shx`** (đo cả hai, ghi số). Bản không `shx`: dựng lại `sweep.json` với mọi `root.shx` = 0 vào thư mục tạm.
- Vệt: khung 7 đầu vệt cách `tip_b` (track) ≤ 4 px; khung 8 đầu vệt cách `tip_c` (track) ≤ 5 px; khung 6 lát mỏng nằm trên lưỡi A (≤ 6 px). `fxcheck` không FAIL, không `pop` / `cut`.
- Xem ảnh ở cỡ game (`preview_game.gif` của vệt và GIF ghép thu về 1x): lấy đà thấy được (thân lún và ngả ra sau 4 khung), cú chém nhanh, trúng đòn có nén rồi nảy, đuôi vệt rút trước.
- `git diff` trong `out/` chỉ có: file mới ở bước 1-2, `source/vfx/sweep_puppet*/`, và dòng thêm vào danh sách giữ của `meta.json`. Không đổi file nào đã có.
- Không chạy `gen_image.py` / `fal_video.py`, không đọc `.env`. Commit + push lên `ccr-38411bc5-l13uki`, đánh dấu ô S4 trong `PLAN.md`.

## Báo cáo (điền dưới đây)
Đường dẫn `contact.png`, `compare.gif`, lưới; bảng số của từng tiêu chí; sockets track ở khung 6 / 7 / 8 cạnh mốc; lệnh vệt đầy đủ; các lần chỉnh và lý do; lệch so với task.

## Kết quả
**Trạng thái: xong, 1 tiêu chí đạt sát (7 -> 8) và 2 chỗ lệch task (shx của B và C). Không xuất ra `frames/`, không chạm `lib-fx/`, `scripts/`.**

### Đường dẫn ảnh (`.work/` không vào git; dựng lại bằng các lệnh bên dưới)
- contact.png: `/home/user/fal-lab/out/heroes/azure_blade/.work/puppet/skill_sweep_puppet_side/contact.png` (bản sao `/home/user/fal-lab/out/heroes/azure_blade/.work/sweep_review/contact.png`)
- compare.gif (15 fps, trái = bản cũ: A giữ 5 khung rồi A, B, C một khung mỗi pose, vệt cũ; phải = bản mới 21 khung): `/home/user/fal-lab/out/heroes/azure_blade/.work/sweep_review/compare.gif`
- lưới 21 khung thân + vệt: `/home/user/fal-lab/out/heroes/azure_blade/.work/sweep_review/grid21.png`; hàng so sánh cũ / mới khung 6-11, 13: `/home/user/fal-lab/out/heroes/azure_blade/.work/sweep_review/cmp_rows.png`; chấm sockets trên 3 ảnh: `/home/user/fal-lab/out/heroes/azure_blade/.work/sweep_review/sock.png`
- vệt: `/home/user/fal-lab/out/heroes/azure_blade/.work/sweep_fx/` (`preview_game.gif`), vệt theo mốc tay (để so): `/home/user/fal-lab/out/heroes/azure_blade/.work/sweep_fx_ref/`

### Số đo từng tiêu chí (px @2x, ô 352x280; script đo nằm ở scratchpad, không vào repo)
| Tiêu chí | Kết quả | Đạt |
|---|---|---|
| 21 khung, `hit_frame` 8 | 21, 8 | có |
| chân (điểm giữa hai ủng) lệch giữa các khung | điểm `ground` qua ma trận rig: lệch 0,00 px mọi khung (176,0; 246,4). Đo trên ảnh (giữa hai đáy ủng, 5 hàng dưới cùng): x từ 175,5 tới 177,0, tối đa 1,5 px giữa hai khung. Khung 7: điểm thấp nhất 247 so với 245 ở khung khác (ủng B của chính ảnh B lệch nhau 22 px gốc) | có (<= 2) |
| cỡ đầu (bề rộng băng đô, px @2x) | đo trên ảnh gốc rồi nhân `k`, `sx` của khung: A khung 1: 94 px * 0,1413 = 13,28; B khung 7: 104 * 0,1347 * 0,985 = 13,80 (+3,9 %); C khung 13-21 (sx 1,0): 13,77 (+3,7 %); B so C 0,2 %. Đo trực tiếp trên khung dựng (số nguyên): 14 / 13 / 13. Khung 8 (nén sx 1,08) 14,87 (+12 %: là nén có chủ ý của mục 2, không phải cỡ pose) | có (<= 5 % giữa các pose) |
| không khung chạm mép | bbox nhỏ nhất x 111, lớn nhất 257 (ô 352); y 129 tới 247 (ô 280); không chạm | có |
| khung 8 nén mạnh nhất | đỉnh đầu y = 144 ở khung 8 (khung khác 129-138) | có |
| chỗ cắt, dịch tâm vai (giữa hai giáp vai, điểm đo qua rig) 6 -> 7 | **có shx cuối cùng: 6,93** (dx +1,52); không shx: **9,50** (dx -6,68) | có |
| chỗ cắt 7 -> 8 | có shx: **7,44** (dx +0,10); không shx: **7,47** (dx -0,71). Khác nhau 0,03 px: chỗ này gần như hoàn toàn là nhảy DỌC (B: vai y 157,6; C khung nén: 165,0), do nén 0,90 của pha trúng đòn và do pose C chính diện (vai thấp hơn) | đạt sát (nhỏ hơn nhưng không đáng kể) |
| bản cấu hình đúng task (shx B +0,10, shx C +0,12) | 6 -> 7: **12,40** (xấu hơn không shx 9,50), 7 -> 8: 7,44 | KHÔNG đạt: xem lệch |
| vệt khung 7: đầu cách `tip_b` track | 1,51 px (alpha > 0,5 và > 0,3) | có (<= 4) |
| vệt khung 8: đầu cách `tip_c` track | 0,71 px (> 0,5), 0,32 px (> 0,3) | có (<= 5) |
| vệt khung 6: lát mỏng so với lưỡi A (đoạn `root` - `tip` track) | trung bình 1,97, p95 4,24, lớn nhất 5,12 px | có (<= 6) |
| `fxcheck` | `qa.fail` rỗng, `qa.warn` rỗng (bản dựng theo mốc tay có cảnh báo `linger`); không `pop` / `cut`; `build.py melee/slash --check` không FAIL | có |
| tan (tổng alpha, khung vệt 3..9) | 3295, 2058, 905, 238, 12, 2, 0 (h+1 = 0,62, h+2 = 0,27, h+3 = 0,07), đuôi rút trước | có |
| cỡ game | lấy đà thấy được (thân lún 6 px @2x ở đỉnh đầu, ngả ra sau, vai trái 8 px), cú chém 1 khung, khung 8 nén rồi nảy tới khung 9-10, đuôi vệt rút trước | có (nhìn `compare.gif`, `cmp_rows.png`) |
| `git diff` trong `out/` | `meta.json`: +4 dòng (`sources.vfx`: `sweep_puppet`, `sweep_puppet_pivot`); file mới: 2 script, 3 rig, `anims/sweep.json`, `source/vfx/sweep_puppet*/` | có |

### Sockets của track (px @2x) ở khung 6 / 7 / 8, cạnh mốc của task
| | track (dùng) | mốc task (không shx, không nén) |
|---|---|---|
| tip A (khung 6) | 110,1 ; 185,0 | 117,65 ; 181,81 |
| root A | 148,6 ; 187,6 | 154,97 ; 184,49 |
| pivot A | 178,0 ; 185,0 | 183,94 ; 181,81 |
| tip B (khung 7) | 251,5 ; 174,8 | 252,64 ; 176,89 |
| root B | 205,7 ; 173,7 | 206,16 ; 175,81 |
| pivot B | 177,5 ; 172,8 | 177,48 ; 174,92 |
| tip C (khung 8) | 177,3 ; 196,9 | 176,76 ; 191,37 |
| root C | 177,5 ; 181,1 | 176,76 ; 173,88 |
| pivot C | 177,4 ; 181,1 | 176,69 ; 173,88 |
(Khung 6 lệch sang trái / xuống vì lấy đà ngả sau và lún; khung 8 thấp hơn 5-7 px vì nén 0,90.)

### Lệnh vệt đầy đủ (số = track khung 6 / 7 / 8)
```
python lib-fx/build.py melee/slash/sweep --pal frost --fps 15 --split --s 0.707 --swing "tip_a=110.1,185.0;root_a=148.6,187.6;pivot=178.0,185.0;tip_b=251.5,174.8;root_b=205.7,173.7;pivot_b=177.5,172.8;tip_c=177.3,196.9;root_c=177.5,181.1;pivot_c=177.4,181.1" --out out/heroes/azure_blade/.work/sweep_fx
```
Hai lệnh track: `python scripts/puppet.py track out/heroes/azure_blade <asset>/source/rig/anims/sweep.json --name sweep_puppet --root blade_root --tip blade_tip` và lần hai `--name sweep_puppet_pivot --root pivot --tip pivot`. Vệt n ghép vào thân n + 5 (`origin` (80, 106) @2x).

### Các lần chỉnh (mỗi lần một nấc) và lý do
1. **Vòng 1, đúng số của task** (`root.shx`: A -0,08 / -0,10, B +0,10, C +0,12 -> -0,02 -> 0). Contact đúng hình (lún, ngả sau, giãn, nén), nhưng đo chỗ cắt: 6 -> 7 = **12,40** so với 9,50 không shx: xấu hơn. Lý do: A ngả ra sau -0,10 đã dịch vai A sang TRÁI 8,2 px (tới 175,9), tức là về phía thân B (B lệch trái 6,7 px khi không shx, 177,5); rồi shx +0,10 của B đẩy B sang phải 8,9 px (186,3): hai đầu đi qua nhau. Ngoài ra 7 -> 8: shx +0,12 của khung nén C đẩy C sang phải lệch B nữa.
2. **Vòng 2**: B `root.shx` +0,10 -> 0,0 (tính nhanh: 6 -> 7 = 6,93). Nhưng 7 -> 8 xấu hơn: 11,72 (C +0,12 bay 9 px sang phải so với B).
3. **Vòng 3**: C `root.shx` đầu 0,12 -> 0,01 (giữ (2, -0,02 out), (4, 0 inout)). 7 -> 8 = 7,44. Chọn 0,01 vì cho dx = +0,10 so với B (gần 0). Mọi thử khác (b -0,01; b 0,005 + c 0,012) cho 6,79 / 7,04 và 7,44: không tốt hơn đáng kể.
4. Mỗi vòng xem `contact.png`, dải khung 1-16 (cắt 200x200), rồi ghép vệt (`grid21.png`, `cmp_rows.png`): thấy lún và ngả ở khung 1-6, nhát chém 1 khung, nén ở khung 8 rồi nảy ở khung 9-10, thở nhẹ khung 14-21; không thấy giật ngang ở chỗ cắt.
5. Dựng lại vệt theo số track (khung 6 -> 8) thay cho mốc tay: bản mốc tay có cảnh báo `linger`, bản track không có; đầu vệt cách `tip_b` / `tip_c` thật 1,5 / 0,7 px.

### Lệch so với task (làm theo code + motion-recipes, và lý do)
1. **B `root.shx` = 0,0 (task: +0,10) và C `root.shx` bắt đầu 0,01 (task: +0,12).** Dấu của `shx` đúng như task và motion-recipes (dương = ngọn ngả sang phải; code `SH`: `x' = x - shx * (y - pivot_y)`, y xuống, nên đỉnh đi sang phải). Nhưng task coi A ở nguyên chỗ cũ; thực ra lấy đà của A ngả sau (shx -0,10) đã kéo vai A tới 175,9, sát B (177,5 không shx), nên +0,10 ở B làm vượt qua (xem vòng 1). Cùng lý do với C. Nghĩa là mô tả "B -> A kéo sang phải 0,075" của task đúng cho A đứng thẳng, không đúng khi A đã ngả sau. Đã ghi trong comment của `make_anim_sweep.py`.
2. Khung 7 -> 8 chỉ nhỏ hơn bản không shx 0,03 px: chủ yếu là nhảy dọc (nén 0,90 + pose C chính diện); không chỉnh thêm vì `sy` 0,90 là số của mục 2 / 4 và đổi nó là đổi cảm giác trúng đòn.
3. Lệnh render trong task (`source/rig/anims/sweep.json` tương đối) phải viết đường dẫn đầy đủ (`<asset>/source/rig/anims/sweep.json`): `puppet.py` đọc đường dẫn theo thư mục hiện tại.
4. Bản "cũ" trong `compare.gif` được dựng lại bằng ba rig đặt `unit` = 849 cho cả ba pose (đúng cỡ cũ: B to hơn A 4,9 %, C 6,7 %), không shx, không nén, với vệt dựng từ mốc tay (không dùng bản đã duyệt từ `frames/`); A giữ 5 khung để hai bản cùng đặt `hit` ở khung 8.
5. Mép đầu ủng khung 7 thấp hơn 2 px: do B tự có hai ủng lệch (951 / 929 px gốc), `ground` đúng.
6. Không đạt / còn mở: không có.
