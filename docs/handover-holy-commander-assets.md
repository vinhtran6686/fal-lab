# Handover: bộ assets của holy_commander

File này mô tả bộ assets đã trích xuất của hero **holy_commander** (Thánh Kỵ Sĩ Chỉ Huy) để một repo hoặc một phiên làm việc khác nhận và dùng. Phần "Prompt để dán" ngay dưới là bản tự đứng được; phần còn lại là chi tiết để tra.
Số liệu lấy từ `out/heroes/holy_commander/export_manifest.json` (nguồn sự thật cho máy đọc) và `EXPORT_README.md` (cùng thư mục).

## Prompt để dán

```
Bạn nhận một bộ assets sprite 2D cho một hero cận chiến tên holy_commander (Thánh Kỵ Sĩ Chỉ Huy), tạo ở repo vinhtran6686/fal-lab, nhánh main,
thư mục out/heroes/holy_commander/. Hãy dùng bộ này làm nguồn, đừng tạo lại. Đọc theo thứ tự: out/heroes/holy_commander/export_manifest.json
(máy đọc), out/heroes/holy_commander/EXPORT_README.md (người đọc), rồi docs/handover-holy-commander-assets.md (file này).

Tóm tắt bộ assets:
- Hero cận chiến, giáp bạc viền vàng, thập tự vàng trên ngực, mũ có mào đỏ, áo choàng đỏ, trường kiếm dài báng đại bàng. Phong cách vector phẳng 2D, nhìn từ trên xuống nhẹ.
- 10 state, mỗi state là một chuỗi frame PNG RGBA trong suốt: idle (1 hình), run (8, lặp), attack (18), death (32), respawn (30), levelup (27),
  3 skill: Xung phong (34), Cờ hiệu thánh (39), Chém sáng (43); và icon.
- Mọi frame cùng một ô 176x140 ở @1x (352x280 ở @2x), cùng một cỡ thân, cùng pivot ở chân (x 0,5 y 0,88 của ô: (88,123) ở @1x, (176,246) ở @2x),
  nên đổi state không bị nhảy. 15 fps (mỗi hình ~67 ms). Mọi state quay mặt sang PHẢI: muốn quay trái thì lật ngang quanh pivot (cả fx).
- Bóng dưới chân (elip phẳng 35% đen) đã vẽ sẵn trong từng frame thân.
- 2 lớp hiệu ứng tách riêng (levelup, radiant_slash): mỗi lớp có back (vẽ sau thân) và front (vẽ trước thân), số hình bằng số hình thân của state,
  mỗi cái có pivot riêng trong fx.json; đặt pivot của fx trùng pivot hero; hình n của fx đi với hình n của thân; pha trộn screen hoặc additive.
- hit_frame (attack 10, levelup 13, banner 18, slash 27) tính từ 1: hình mà cú đánh trúng.
- Chưa có chỉ số nhân vật (máu, sát thương...). Chưa có âm thanh. Clip respawn chưa được chủ dự án duyệt.

Việc của bạn: ... (điền mục tiêu của repo đích, ví dụ nạp assets vào engine, dựng bảng animation, gắn sự kiện hit)
```

## Có gì trong bộ assets

Đường dẫn gốc: `out/heroes/holy_commander/` (repo `vinhtran6686/fal-lab`, nhánh `main`).

### Các state (thân)
| Vai trò | `sheet` | Thư mục | Hình | Thời gian | Kiểu | hit (từ 1) | fx riêng | Trạng thái |
|---|---|---|---|---|---|---|---|---|
| idle | `idle_side` | `idle/idle_side/` | 1 | - | lặp | - | - | final |
| di chuyển | `run_side` | `move/run_side/` | 8 | 0.53 s | lặp | - | - | final |
| đánh thường | `attack_side` | `attack/attack_side/` | 18 | 1.20 s | một lần | 10 | - | final |
| chết | `death_side` | `death/death_side/` | 32 | 2.13 s | một lần | - | - | final |
| hồi sinh | `respawn_side` | `spawn/respawn_side/` | 30 | 2.00 s | một lần | - | - | **chờ user duyệt clip** |
| lên cấp | `levelup_side` | `level/levelup_side/` | 27 | 1.80 s | một lần | 13 | levelup | final |
| skill 1 | `skill_charge_side` | `skill/skill_charge_side/` | 34 | 2.27 s | một lần | - | - | final |
| skill 2 | `skill_holy_banner_side` | `skill/skill_holy_banner_side/` | 39 | 2.60 s | một lần | 18 | - | final |
| skill 3 | `skill_radiant_slash_side` | `skill/skill_radiant_slash_side/` | 43 | 2.87 s | một lần | 27 | radiant_slash | final |
| icon | `icon` | `ui/icon/` | 1 | - | lặp | - | - | final |

Mỗi thư mục state có: `frames/@1x/hero_holy_commander_<sheet>_NN.png`, `frames/@2x/...` (NN từ 01), `sheet.png` (băng ngang @2x), `preview.gif`, và `check/` (kiểm tra tĩnh, không cần dùng).
Icon: 128x128 ở @1x (256x256 ở @2x), ở `ui/icon/`.

Mô tả hành động từng state:
- **idle**: đứng yên, kiếm cắm đất trước người, hai tay chồng trên báng đại bàng.
- **run**: chạy, kiếm cầm hai tay, áo choàng bay.
- **attack**: chém chéo từ trên xuống rồi chém ngang; vệt chém trắng nằm sẵn trong frame (cố ý giữ).
- **death**: khuỵu, ngã sấp, nằm yên ở hình cuối (giữ hình cuối).
- **respawn**: bắt đầu quỳ, gục đầu vào kiếm dựng đứng, cả người màu xám; màu hồi dần, ngẩng đầu, chống kiếm đứng lên, kết bằng đúng tư thế idle.
- **levelup**: hạ người lấy đà, đấm một tay thẳng lên trời, giữ pose. Ánh sáng là lớp fx `levelup`.
- **skill 1 Xung phong**: cúi người rút kiếm, vung lên, kiếm bốc lửa (lửa và vòng lửa do model vẽ nằm sẵn trong frame).
- **skill 2 Cờ hiệu thánh**: lùi một chân, nâng kiếm hai tay rồi găm xuống đất, khuỵu quỳ một gối hai tay nắm chặt cán; sóng xung kích trên đất nằm sẵn trong frame.
- **skill 3 Chém sáng (tia thánh xuyên)**: rút kiếm ngang ngực, kéo sát người, bước dài đâm thẳng, giữ pose. Tia sáng là lớp fx `radiant_slash`.

### Lớp fx tách riêng
| fx | Cho state | Hình | Kích thước @1x | Pivot (điểm đặt) |
|---|---|---|---|---|
| `levelup` | `levelup_side` | 27 | 72x99 (@2x 144x198) | [39, 88] (@2x [78, 176]) |
| `radiant_slash` | `skill_radiant_slash_side` | 43 | 209x92 (@2x 418x184) | [54, 81] (@2x [108, 162]) |

Thư mục: `fx/<tên>/back/frames/@1x|@2x/hero_holy_commander_fx_<tên>_back_NN.png`, `.../front/...`, và `fx/<tên>/fx.json`.
- Vẽ theo thứ tự: **fx back, thân, fx front**. Đặt ảnh fx sao cho `pivot` của nó nằm đúng pivot của hero, tức góc trên trái của ảnh fx = pivot hero trừ pivot fx.
- Ánh sáng lưu kiểu cộng sáng trên nền đen: màu = màu ánh sáng, alpha = độ mạnh (kênh lớn nhất), alpha thẳng. Nên pha trộn bằng **screen hoặc additive**.
  Alpha-over thường vẫn dùng được nhưng hơi tối hơn trên nền sáng.
- Kích thước fx khác ô hero (tia slash dài hơn ô). Đừng cắt fx theo ô hero.
- Khi lật hero sang trái thì lật cả fx quanh pivot hero.

### Ảnh tĩnh (`design/`)
`master_v07.png` (ảnh chốt, = idle), `icon_v01.png`, `pose_respawn_v02.png`, `pose_levelup_v02.png`, `pose_skill_charge_v01.png`, hai ảnh pose cũ của skill 2 và 3 (thiết kế cũ, không dùng cho bản chốt).
Thư mục `design/` còn các bản nháp khác (v01...), chỉ để tham khảo.

## Cách ghép thân và fx (mã giả)
```
# cell = ô hero @1x 176x140; heroPivot = (88, 123)
draw(fxBack[n],  at = heroPos - heroPivot + (heroPivot - fx.pivot_1x))   # sau thân
draw(body[n],    at = heroPos - heroPivot)
draw(fxFront[n], at = heroPos - heroPivot + (heroPivot - fx.pivot_1x))   # trước thân
# heroPos = vị trí của chân hero trên màn hình
```
Chạy theo 15 fps (1000/15 ms mỗi hình). Hầu hết state chạy một lần rồi về idle; run lặp.

## Những điều phải biết
- Bóng đã vẽ sẵn trong frame thân, nên đừng vẽ thêm bóng thứ hai nếu không muốn đè.
- Frame có sẵn **fx do model vẽ** ở attack (vệt chém trắng), skill 1 (lửa), skill 2 (sóng): không tách được; chúng là một phần của frame.
- Lỗi nhỏ đã biết (chủ dự án chấp nhận): charge có vòng lửa lớn ở khoảng 2/3 clip và một hình lạ cạnh vai ở đầu; banner có khối nón sáng mờ phủ lên hero trong vài hình lúc găm kiếm và vòng sóng chạy ra mép ô; slash thân hơi xoay về camera khi kéo kiếm.
- `motion_check` báo FROZEN ở hình cuối, SPIKE khi quay về hình 1, DRIFT khi lao hoặc ngã: đều là đặc tính của hành động một lần, không phải lỗi.

## Không có trong bộ assets
- Chỉ số nhân vật (máu, sát thương, tốc độ...), âm thanh, đạn (hero cận chiến), attack thứ hai, trạng thái bị đánh, idle động (idle chỉ 1 hình), sheet riêng quay trái (chỉ cần lật), fx hồi sinh.
- Clip respawn chưa được chủ dự án duyệt (vẫn export, gắn nhãn chờ duyệt).
- Chưa chạy gate chất lượng `qc.json` cho các state mới; fx levelup và slash chưa kiểm trên nền sáng.

## Cần copy gì sang repo khác
`meta.json`, `export_manifest.json`, `EXPORT_README.md`, thư mục `idle/ move/ attack/ death/ spawn/ level/ skill/`, `fx/levelup/`, `fx/radiant_slash/`, `ui/icon/`, và (tuỳ chọn) ảnh tĩnh trong `design/`.
Không cần: `raw/` (clip nguồn), `review/`, `fx/*.py`, `brief.md`, `history.md`, `export_recipe.json`.

## Tái tạo và chỉnh sửa (chỉ trong repo fal-lab)
Công thức frame của từng state ở `out/heroes/holy_commander/export_recipe.json`. Chỉnh bằng Frame Tuner (`tools/frame_tuner/README.md`), rồi:
```
python tools/frame_tuner/apply_recipe.py --write     # xuất lại thân theo công thức
python tools/frame_tuner/export_fx.py                # xuất lại lớp fx
python tools/frame_tuner/build_export_manifest.py    # dựng lại manifest và kiểm tra gói (746 file frame)
```
Bối cảnh thiết kế, từng take và quyết định: `out/heroes/holy_commander/brief.md`, `history.md`; cách làm fx Python: `docs/python-fx-recipe.md`; trạng thái tổng: `docs/holy-commander-report.md` mục 15.
