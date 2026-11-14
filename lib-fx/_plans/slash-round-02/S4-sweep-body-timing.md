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
