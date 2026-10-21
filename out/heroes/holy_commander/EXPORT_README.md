# holy_commander: bộ assets đã trích xuất (cho repo khác)

Thánh Kỵ Sĩ Chỉ Huy, hero cận chiến cỡ M. Mọi frame đã export, đủ để dùng ở nơi khác. Máy đọc: `export_manifest.json`. Người đọc: file này.
Chưa có chỉ số nhân vật (stats), và clip respawn chưa được user duyệt (xem "Còn mở").

## Cần copy gì
`meta.json`, `export_manifest.json`, các thư mục state (`idle/ move/ attack/ death/ spawn/ level/ skill/`), `fx/levelup/`, `fx/radiant_slash/`, `ui/icon/`, và (tuỳ chọn) ảnh tĩnh ở `design/`.
Không cần: `raw/`, `review/`, `fx/*.py`, `brief.md`, `history.md`, `export_recipe.json` (chỉ để tái lập trong repo này).

## Định dạng
- Mỗi state là một thư mục `<loại>/<tên>/` gồm `frames/@1x/*.png` (176x140), `frames/@2x/*.png` (352x280), `sheet.png` (băng ngang @2x), `preview.gif`.
- PNG RGBA, nền trong suốt. Tên file: `hero_holy_commander_<tên>_NN.png`, NN từ 01.
- **Mọi state quay mặt sang phải.** Muốn quay trái thì lật ngang (`meta.json` "mirrored" có sẵn run_left, idle_left).
- **Pivot (điểm chân)**: x 0,5 và y 0,88 của ô: (88, 123) ở @1x, (176, 246) ở @2x. Mọi state dùng chung một ô và một cỡ thân nên đổi state không bị nhảy.
- **Bóng dưới chân** (elip phẳng 35% đen) đã **vẽ sẵn trong từng frame thân**, không nằm trong lớp fx.
- fps 15, mỗi frame 67 ms (trừ state 1 hình). Hầu hết state chạy một lần (không lặp), riêng run lặp.
- `hit_frame` (attack, levelup, banner, slash) tính từ 1: hình mà cú đánh trúng, để gắn sát thương hay hiệu ứng.

## Các state
| State (`sheet`) | Thư mục | Hình | Thời gian | hit | Ghi chú |
|---|---|---|---|---|---|
| idle_side | idle/idle_side | 1 | - | - | đứng yên (master) |
| run_side | move/run_side | 8 | 0,53 s lặp | - | |
| attack_side | attack/attack_side | 18 | 1,20 s | 10 | vệt chém trắng nằm trong frame |
| death_side | death/death_side | 32 | 2,13 s | - | nằm yên ở hình cuối |
| respawn_side | spawn/respawn_side | 30 | 2,00 s | - | quỳ xám, hồi màu, đứng lên; **chờ user duyệt** |
| levelup_side | level/levelup_side | 27 | 1,80 s | 13 | + fx `levelup` |
| skill_charge_side | skill/skill_charge_side | 34 | 2,27 s | - | skill 1; lửa nằm trong frame; vòng lửa lớn là lỗi đã biết |
| skill_holy_banner_side | skill/skill_holy_banner_side | 39 | 2,60 s | 18 | skill 2; ripple nằm trong frame |
| skill_radiant_slash_side | skill/skill_radiant_slash_side | 43 | 2,87 s | 27 | skill 3; + fx `radiant_slash` |
| icon | ui/icon | 1 | - | - | 128x128 (@2x 256x256) |

## Lớp hiệu ứng (fx) riêng
**Xem fx ở đâu:** thư mục `preview.gif` của state levelup và slash chỉ có **thân**. Hiệu ứng nằm trong mục riêng `fx/`, mỗi fx có `preview_fx_only.gif` (chỉ lớp fx), `preview_with_body.gif` (fx và thân),
`sheet.png` (8 hình fx). Cạnh `preview.gif` của state có thêm `preview_with_fx.gif` (thân + fx). Đây chỉ là bản xem (nền tối, screen); game dùng các PNG `back/` và `front/`.
Các hình đầu của fx để trống vì hiệu ứng chỉ bắt đầu khi động tác tới nhịp đó (levelup từ hình đấm lên, slash từ lúc kéo kiếm sát người).

Hai skill có lớp fx tách khỏi thân: `fx/levelup/` (hào quang xung nhịp) và `fx/radiant_slash/` (tia sáng bắn từ mũi kiếm). Mỗi fx có `back/` (vẽ **sau** thân) và `front/` (vẽ **trước** thân),
mỗi thư mục `frames/@1x` và `@2x`, số hình **bằng đúng** số hình thân của state, và `fx.json`.
- Đặt ảnh fx sao cho **pivot của nó** (`pivot_1x` hoặc `pivot_2x` trong `fx.json`) trùng pivot của hero. Hình n của fx đi với hình n của thân. Kích thước fx khác ô hero (tia slash dài hơn ô).
- Ánh sáng lưu kiểu **cộng sáng trên nền đen**: màu = màu ánh sáng, alpha = độ mạnh (kênh lớn nhất), alpha thẳng. Nên pha trộn bằng **screen hoặc additive** nếu engine có; alpha-over thường vẫn dùng được nhưng hơi tối hơn trên nền sáng.
- Skill 1, 2 và attack có fx do model vẽ **nằm sẵn trong frame thân** (không tách được).

## Còn mở và lỗi nhỏ đã biết
- **Respawn** (clip rise t01): user chưa duyệt.
- **Chưa có stats.**
- `motion_check` (kiểm tĩnh) báo FROZEN ở hình cuối (giữ pose, có chủ ý), SPIKE khi vòng về hình 1 (hành động một lần), DRIFT khi lao hoặc ngã (có chủ ý). Chưa chạy gate `qc.json` cho các state mới.
- charge: vòng lửa lớn khoảng 2/3 clip và một hình lạ cạnh vai ở đầu. banner: khối nón sáng mờ phủ lên hero vài hình, vòng sóng ra mép ô. slash: thân hơi xoay về camera khi kéo kiếm. levelup, slash: fx là bản vẽ Python, chưa kiểm trên nền sáng.

## Tái lập trong repo này
`export_recipe.json` (frame giữ, thời gian, hit của từng state) -> `python tools/frame_tuner/apply_recipe.py --write` (thân) -> `python tools/frame_tuner/export_fx.py` (fx) ->
`python tools/frame_tuner/build_export_manifest.py` (manifest và kiểm tra). Chỉnh frame bằng Frame Tuner (`tools/frame_tuner/README.md`).
