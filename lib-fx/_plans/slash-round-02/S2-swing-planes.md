# S2. Mặt phẳng vung: chém ngang và chém xéo theo góc nhìn của game

Phụ thuộc: S1 (đã xong). Đọc trước: `.claude/skills/fal-image/action-planes.md` (mục 1-2: ba hướng không gian, ba mặt phẳng), nhánh `track` của
`lib-fx/_core/formulas/draw/fxkit/layers/slash.py` (hàm `swing(f)`, `at`, `strand`, sợi mũi / giữa / chuôi, dải `edge`).

## Vấn đề
Kind `slash` chỉ vẽ trong mặt phẳng màn hình, nên chỉ đúng với **bổ dọc / hất lên** và **đâm**. Từ máy quay của game (cao, chếch xuống; nhân vật quay phải):
- **chém ngang** (lưỡi quét song song mặt đất) phải là một **ellipse rất dẹt, gần thành một đường**: nửa đi trước thân thì gần (dày, sáng, vẽ ĐÈ lên thân),
  nửa đi sau thân thì xa (mảnh, tối, vẽ SAU thân), hai đầu trái phải nhọn;
- **chém xéo** là ellipse dẹt vừa, xoay nghiêng: bắt đầu cao và một phần sau thân, kết thúc thấp và trước thân (hoặc ngược lại).
Cả ba chỉ là **một mô hình**: mũi vũ khí chạy trên một đường tròn quanh vai trong không gian; hình ta thấy là hình chiếu của đường tròn đó.

## File được sửa
- `lib-fx/_core/formulas/draw/fxkit/layers/slash.py` (thêm chế độ `swing3d`; không đổi hành vi của chế độ cung và chế độ `track`)
- `lib-fx/_core/formulas/draw/fxkit/ink.py` (cho `Ink` vẽ lên canvas chỉ định), `effect.py` (chỉ hàm `lint`, mục "Việc nhỏ" 2)
- `lib-fx/melee/slash/slash.py` (3 hiệu ứng mới), `lib-fx/build.py` (cờ `--swing`)
- `lib-fx/_core/formulas/draw/fxkit/layers/scraps.py` (chỉ nếu cần cho "Việc nhỏ" 1)
- `FXKIT.md` (bảng kind, mục 6), `lib-fx/GUIDE.md` (dòng `melee/slash`), `lib-fx/_core/formulas/rules/vfx/slash/README.md` (mục mới "theo mặt phẳng vung"),
  `.claude/skills/fal-image/action-planes.md` (chỉ cột "The effect": thay "plan S2" bằng tên hiệu ứng thật và bỏ chữ *untested* cho phần vfx)

## Mô hình (làm đúng công thức, không tự chế)
Tham số mới của kind: `swing=None`. Khi là dict:
```
{"k": 0.3,        # độ dẹt của mặt phẳng vung: 1 = song song màn hình, 0.3 = nằm ngang trên đất, 0.6 = xéo
 "roll": 0.0,     # độ: góc xoay trục dài của ellipse trên màn hình (0 = nằm ngang; dương = đầu phía trước chúc XUỐNG khi nhân vật quay phải)
 "u0": 235, "u1": 430,   # độ: góc của lưỡi trong mặt phẳng vung lúc đầu và lúc cuối (xem quy ước dưới)
 "r": 120,        # px ở s = 1: bán kính mũi vũ khí tính từ vai; 0 = lấy khoảng cách a -> b
 "blade": 0.75,   # phần bán kính được quét (tính từ mũi vào): 0.75 = vệt phủ 75 % phía mũi
 "ease": 1.3}
```
- **Tâm** `O` = `c.sp.a` (vai / trục quay). Hướng mặt = dấu của `c.sp.b[0] - c.sp.a[0]` (`face` = +1 quay phải, −1 quay trái).
- **Quy ước góc `u`** (trong mặt phẳng vung, nhân vật quay phải): 0° = phía trước (phải màn hình), 90° = **gần** người xem, 180° = phía sau (trái), 270° = **xa** người xem.
  `u` tăng nghĩa là đi trước → gần → sau → xa.
- Đơn vị trên màn hình: `A = (cos roll, sin roll)` rồi nhân thành phần x với `face`; `P = (-sin roll, cos roll)` (vuông góc với A, y màn hình hướng xuống, **không** nhân `face`).
- Với góc `u` và bán kính `ρ`:
  - `depth(u) = sin(u) * sqrt(1 - k*k)` (dương = gần người xem);
  - phối cảnh: `ρ' = ρ * (1 + 0.16 * depth)` (gần thì to hơn);
  - điểm màn hình: `O + ρ' * (cos(u) * A + sin(u) * k * P)`.
  Với `k = 0.3, roll = 0`: điểm gần (u = 90°) nằm DƯỚI tâm `0.3 ρ`, điểm xa (270°) nằm TRÊN tâm: đúng một vòng nằm trên đất nhìn từ trên chếch xuống.
- `u(f) = u0 + (u1 - u0) * f ** ease` cho `f` trong 0..1. Mũi = bán kính `R = r * s`; chuôi (mép trong của vệt) = bán kính `R * (1 - blade)`.
- Hàm `swing(f)` của chế độ này trả về đúng bộ ba như chế độ `track`: `(điểm chuôi, điểm mũi, chiều dài)` + thêm `depth(u(f))`. **Mọi thứ sau đó dùng lại nguyên nhánh `track`**:
  ba sợi mũi đậm / giữa / chuôi nhạt, dải `edge` trắng ở lưỡi cuối, nhịp `fh` (lát mỏng trước đòn, đầy ở khung trúng đòn), nhịp tan, đuôi rút.
  Trong code: gom điều kiện `if track:` thành `tracked = bool(track or swing)` ở những chỗ chỉ phụ thuộc vào "có hàm `swing(f)`".

### Chia trước / sau thân và độ dày theo gần xa
- Mỗi sợi được vẽ thành **hai đoạn**: phần có `depth(u(f)) < 0` (xa) và phần `>= 0` (gần). Tìm điểm cắt `f*` bằng cách lấy mẫu 64 điểm.
  Đoạn xa vẽ vào một `Ink` gắn với **canvas `back`**, đoạn gần vào `Ink` gắn với **canvas `front`**, bất kể `z` của lớp.
  `Ink.__init__` thêm tham số `canvas=None` (mặc định `c.cv`); khi truyền canvas khác thì `ink.paint` phải cộng quầng sáng vào đúng nửa đó
  (`Ctx.add_glow` cộng theo `self.layer.z`: thêm tham số `z=None` cho `add_glow` và cho `Ink` nhớ `z` của canvas nó vẽ).
- Hệ số bề rộng theo gần xa (số đo của bộ sinh "xoay quanh thân" đã được chấm 9-10/10: xa 0,30, gần 2,4 khi `k` ≈ 0,25), nội suy theo độ dẹt:
  `q = (1 - k) / 0.75`; `m(u) = 1 + sin(u) * (1.4 * q)` khi `sin(u) >= 0`, `m(u) = 1 + sin(u) * (0.7 * q)` khi `sin(u) < 0`; kẹp `m` trong [0.3, 2.4].
  Nhân `m(u(f))` vào **bề dày nhìn thấy tối thiểu** của vệt: hình chiếu của bề mặt lưỡi ở chỗ gần / xa rất mỏng (`R * blade * k`), nên đặt bề dày ngang nét
  = `max(hình chiếu thật, w_min * m(u))` với `w_min = 7 px * s` (đẩy mép trong vào theo pháp tuyến màn hình của cung mũi). Nhờ vậy chém ngang là một **đường có nét dày mỏng**, không biến mất ở chỗ nhìn từ cạnh.
- Đoạn xa: tông nguội hơn một bậc (`main` → `deep`, `hot` → `main`), không có dải `edge`; quầng `glow` × 0,5.
- Hai đầu trái phải của vệt (nơi `sin(u)` gần 0, tiếp tuyến chạy theo chiều sâu) phải **nhọn**: profile đuôi và đầu có sẵn đã thuôn; kiểm bằng ảnh.

## Hiệu ứng mới trong `lib-fx/melee/slash/slash.py`
Cả ba: `space="aim"`, `reach=120` (a = vai, b = điểm phía trước cách vai `reach`: chỉ dùng để lấy hướng mặt và `r` mặc định), `extent=260`,
lớp `slash` với `life=Life(-1/15, 1/15, 0.0, 0.27)`, `weapon="sword"`, `linger=1.8`, `streaks=0` (như `swing`); lớp `scraps` đặt `at` tại điểm mũi cuối
(tính sẵn toạ độ trục cho từng hiệu ứng) với `start >= 0`; một lớp `role="core"` sinh ở t = 0 **không còn cần** sau khi sửa lint (mục "Việc nhỏ" 2).

| id | title | `swing` | Mô tả |
|---|---|---|---|
| `sweep` | Chém ngang | `k=0.3, roll=0, u0=235, u1=430, r=0, blade=0.75` | bắt đầu sau lưng phía xa, vòng qua phía trước, kết thúc phía gần: đoạn đầu nằm SAU thân, đoạn cuối TRƯỚC thân |
| `diag_down` | Chém xéo xuống | `k=0.6, roll=35, u0=205, u1=400, r=0, blade=0.8` | từ cao phía sau xuống thấp phía trước |
| `diag_up` | Chém xéo lên | `k=0.6, roll=-35, u0=160, u1=-35, r=0, blade=0.8` | từ thấp phía sau lên cao phía trước (góc giảm: quét theo chiều ngược lại) |

Sau khi dựng, **nhìn ảnh rồi chỉnh `u0`, `u1`, `roll`** trong phạm vi ±25° để hình khớp mô tả ở bảng "The three planes" của `action-planes.md`; ghi giá trị cuối vào "Kết quả".
Thêm cho rìu: không làm trong task này.

## `build.py`
Cờ `--swing "k=0.3;roll=0;u0=235;u1=430;r=120;blade=0.75;ease=1.3"` (phân tích như `--track`; đặt tham số `swing` cho mọi lớp kind `slash`; `--swing` và `--track` không dùng cùng nhau: báo lỗi).
Với nhân vật thật: `--from` = toạ độ **vai** (px ô @2x), `--to` = một điểm cùng độ cao ở phía nhân vật quay mặt, `r` = khoảng cách vai → mũi vũ khí đo trên pose B.

## Việc nhỏ gộp từ lần chấm S1
1. `swing`: mảnh văng ở mũi đao rơi xuống dưới mặt đất và còn tới 6 khung sau đòn. Đặt `floor=True` (tham số có sẵn của `scraps`; nếu `c.sp.floor` không đúng với hiệu ứng `span`,
   thêm tham số `floor_y` tính từ điểm neo) và rút `life` của `scraps` còn `Life(0.033, 0.033, 0.0, 0.3)`.
2. `Effect.lint`: điều kiện "có lớp primary / core / flash trên khung trúng đòn" đổi thành: có lớp với `role` trong (`flash`, `core`, `primary`) mà
   `life.start <= 1/30` **và** `life.end > 0` (lớp sinh trước đòn và còn sống ở t = 0 cũng tính). Sau đó trả lớp `streaks` của `swing` về `role="accent"`.
3. Khung trước đòn của chế độ bám vũ khí hiện chỉ có dải `edge` trắng: thêm quanh nó một viền tông `main` rộng 3 px * s (cùng hình lát mỏng, nở ra) để có sắc màu của vệt.

## Tiêu chí nghiệm thu (đo và ghi số vào "Kết quả")
Dựng mỗi hiệu ứng mặc định (30 fps) và ở 15 fps với `--split`.
- [x] `sweep`, khung trúng đòn: khung bao của vệt có cao / rộng ≤ 0,40; có điểm ảnh ở **cả** `back/` và `front/`; phần `back/` nằm ở nửa trên của khung bao, phần `front/` ở nửa dưới.
- [x] `sweep`: bề dày nét lớn nhất ở phần gần ≥ 2 lần bề dày lớn nhất ở phần xa.
- [x] `diag_down`: điểm đầu vệt (f = 0) cao hơn điểm cuối (f = 1) ít nhất `0.5 r`; khung bao cao / rộng trong 0,5-1,1. `diag_up`: ngược lại.
- [x] Quay trái (`--from 300,150 --to 180,150`): hình là ảnh gương qua trục đứng của bản quay phải (so mặt nạ đã lật: IoU ≥ 0,9); phần gần vẫn ở dưới, phần xa vẫn ở trên.
- [x] `k=1.0` cho một cung tròn không dẹt, toàn bộ ở `front` (kiểm mô hình: `--swing "k=1;roll=0;u0=110;u1=-20"`).
- [x] Nhịp và tan như `swing`: khung trước đòn là lát mỏng; ở 15 fps `A(h+1)/A(h)` ≤ 0,75, `A(h+2)/A(h)` ≤ 0,45, `A(h+3)/A(h)` ≤ 0,2; `fxcheck` không FAIL / `pop` / `cut`.
- [x] Ghép thử lên thân: dùng `out/heroes/azure_blade/frames/skill_crescent_puppet_side/frames/@2x` khung 1 (dáng đứng) làm nền, đặt vai bằng mắt (ghi toạ độ đã dùng),
      dựng `sweep` với `--split`, ghép `back` dưới thân và `front` trên thân: nhìn thấy vệt **vòng quanh thân** (đi sau rồi ra trước). Ảnh lưu thư mục tạm, không ghi vào `out/`.
- [x] Không hồi quy: `crescent`, `heavy`, `thrust`, `axe`, `axe_heavy` (30 fps) và `swing --track` (lệnh của S1, 15 fps) cho khung **giống hệt** trước task này (so hash),
      trừ thay đổi có chủ ý của "Việc nhỏ" 1 và 3 trên `swing` (ghi rõ khung nào đổi).
- [x] `python lib-fx/build.py melee/slash --check` không FAIL; `python lib-fx/_tools/fxkit_test.py` qua.
- [x] Ba ảnh lưới (mỗi hiệu ứng: mọi khung ở 15 fps, cỡ game x3) và một ảnh so bốn loại cạnh nhau ở khung trúng đòn: bổ dọc (`swing --track` của S1), `sweep`, `diag_down`, `thrust`.

## Kết quả (người làm điền: giá trị `swing` cuối cùng của ba hiệu ứng, số đo từng tiêu chí, đường dẫn ảnh, chỗ chưa đạt, lệch so với task và lý do)

### Giá trị `swing` cuối (trong `lib-fx/melee/slash/slash.py`, hàm `_plane_effect`)
| id | k | roll | u0 | u1 | r | blade | ease | linger | release lớp slash |
|---|---|---|---|---|---|---|---|---|---|
| `sweep` | 0.3 | 0 | **215** (spec 235) | **410** (spec 430) | 0 (= 120 @ s = 1) | 0.75 | 1.3 | 3.4 | 0.36 s |
| `diag_down` | 0.6 | 35 | 205 | 400 | 0 | 0.8 | 1.3 | 2.4 | 0.36 s |
| `diag_up` | 0.6 | -35 | 160 | -35 | 0 | 0.8 | 1.3 | 2.0 | 0.36 s |
Cả ba: `Life(-1/15, 1/15, 0.0, 0.36)` (spec 0.27), `streaks=0`, `scraps` (`floor=True`, `Life(0.033, 0.033, 0.0, 0.33)`, `arc=(-10, 60)`) và `streaks` (`arc=(0, 50)`) đặt tại điểm mũi cuối tính từ chính `plane_point` (trục: `("a", x, -y)`).
`sweep` chỉnh u0 / u1 vào trong 20° (trong phạm vi ±25° cho phép) vì ở 235 / 430 khung bao cao / rộng là 0,433 (> 0,40).

### Đo (script tạm ngoài repo: `/tmp/claude-0/-home-user-fal-lab/0d4327dc-c403-51b7-8868-48c89542b69c/scratchpad/s2/` : `base.sh`, `meas.py`, `mir2.py`, `series.py`, `cmpabs.py`, `grid.py`, `onbody.py`; kết quả thô `meas_out.txt`)
Lệnh: `--from 180,150 --to 300,150 --fps 15 --split` (quay phải), `--from 300,150 --to 180,150` (quay trái); hình = alpha >= 128, khung `h` = `hit_frame - 1` (chỉ số 0), 15 fps.
- **sweep, khung trúng đòn**: khung bao 209 x 64 px, cao / rộng **0,306** (<= 0,40; tính cả quầng alpha >= 16 là 0,378). Điểm ảnh ở cả `back/` (556 px) và `front/` (1016 px). `back/`: 98,6 % điểm nằm ở nửa trên của khung bao (trọng tâm y 330,6), `front/`: 99,8 % ở nửa dưới (trọng tâm y 365,9). Ở 235 / 430 ban đầu: 0,433 (không đạt) nên đã chỉnh.
- **sweep, bề dày**: lát cột lớn nhất (số điểm ảnh liên tục theo chiều đứng): gần 29 px, xa 11 px: **2,64 lần** (>= 2). Công thức bề dày đã lệch spec, xem dưới.
- **diag_down / diag_up**: điểm đầu - điểm cuối theo y (từ `plane_point`, r = 120): diag_down đầu cao hơn cuối **180,7 px** (>= 60); diag_up đầu thấp hơn cuối **172,2 px** (ngược lại, >= 60). Khung bao ở khung trúng đòn cao / rộng: diag_down **1,094** (170 x 186), diag_up **1,005** (199 x 200), trong 0,5-1,1 (diag_down sát trần).
- **Quay trái** (ảnh gương qua x = 240): IoU khung trúng đòn, lật thẳng: sweep **0,902**, diag_down 0,920, diag_up 0,965 (>= 0,9). Cho phép lệch 1 px (làm tròn gốc khung): 0,997 / 1,0 / 0,997. Các khung sau (nét mảnh, hạt `scraps`) lật thẳng chỉ 0,3-0,9, cho phép lệch 1 px 0,55-0,98 (khung 5 của sweep còn 0,55; mép trùng trong 2 px: 0,78-1,0): hạt văng không đối xứng hoàn toàn. Quay trái, sweep: trọng tâm `back/` y 330,6 (trên), `front/` y 366,0 (dưới): phần gần ở dưới, phần xa ở trên.
- **k = 1.0** (`--swing "k=1;roll=0;u0=110;u1=-20"`): `back/` alpha tối đa 0 ở mọi khung; toàn bộ ở `front/`; khung bao 170 x 171 (cung tròn).
- **Nhịp và tan, 15 fps** (A = tổng alpha khung `@2x`): sweep A = 129 / **2761** / 1913 / 1138 / 281 / 20: h+1 **0,693**, h+2 **0,412**, h+3 **0,102**; diag_down 517 / **7602** / 4922 / 2685 / 1200 / 224: **0,647 / 0,353 / 0,158**; diag_up 1859 / **15994** / 8898 / 3849 / 1797 / 544: **0,556 / 0,241 / 0,112** (đều <= 0,75 / 0,45 / 0,2). Khung trước đòn là lát mỏng: 129, 517, 1859 = 4,7 % / 6,8 % / 11,6 % khung trúng đòn. `fxcheck` 15 fps: không FAIL, không `pop`, không `cut`, không `linger`. Khung cuối: h+4 là 0,7 % / 2,9 % / 3,4 %, sau đó trống. diag_up: tụt h -> h+1 là 44,4 % đỉnh, dưới ngưỡng `pop` 45 % (sát).
  30 fps mặc định (thư viện): `diag_down`, `diag_up` ok; `sweep` cảnh báo `linger` (5 / 15 khung dưới 2 %), không FAIL.
- **Ghép thử lên thân**: nền `azure_blade/.../skill_crescent_puppet_side` khung 1; vai đặt bằng mắt tại **(140, 160)** px ô @2x, `--to 230,160`, `--swing "k=0.3;roll=0;u0=215;u1=410;r=85;blade=0.75;ease=1.3"` (r = 85 vì thân chỉ cao 125 px), `--pal frost`, 15 fps `--split`. Nhìn thấy nửa xa đi SAU đầu và tay (dưới thân), nửa gần ra TRƯỚC thân bên phải, dày dần. Ảnh `final/on_body_sweep.png` (5 khung) và `final/on_body_sweep_zoom.png`. Cảnh báo `pop` 47 % ở khung 3 -> 4 với r = 85 (chưa chỉnh `linger` riêng cho r này).
- **Không hồi quy** (`--from 78,180 --to 288,180 --split`, 30 fps; hash toàn bộ `frames/@2x|@1x`, `back`, `front`, 97 / 121 / 97 / 97 / 121 file): `crescent`, `heavy`, `thrust`, `axe`, `axe_heavy` **giống hệt** trước (và thư viện `lib-fx/melee/slash/<id>/` của chúng không đổi trong git). `swing --track` (lệnh S1, 15 fps), so từng khung trên toạ độ tuyệt đối: khung 2 (trúng đòn) **0 điểm ảnh khác**; khung 1 đổi (viền `main` 3 px, việc nhỏ 3: alpha 577 -> 1421); khung 3-8 đổi (việc nhỏ 1: `scraps` `floor=True` và đời 0,3; đã tách riêng: dựng HEAD và bản mới đều với `--set scraps.off=true` thì khung 2-7 giống hệt từng điểm ảnh, chỉ khung 1 khác do viền `rim`: tổng alpha khung 3: 5841 -> 5815, khung 4: 3313 -> 3106, khung 5: 982 -> 782, khung 6-8: 122 / 53 / 6 -> 0). Tỉ lệ tan vẫn 0,632 / 0,337 / 0,085.
- **Công cổng**: `python lib-fx/build.py melee/slash --check` exit 0 (không FAIL; cảnh báo cũ của crescent / heavy / thrust / axe_heavy giữ nguyên; `swing` mặc định 30 fps nay cảnh báo `pop`, `cut` (khung 10 giữ 20 %), `linger`, trước đó `pop` + `linger`; `sweep` chỉ `linger`; `diag_*` ok). `python lib-fx/_tools/fxkit_test.py` (chạy lại trên mã cuối): `all checks passed`, exit 0; `build.py melee/slash --check` chạy không qua pipe: exit 0, 0 dòng FAIL.
- **Ảnh**: `final/grid_sweep.png`, `final/grid_diag_down.png`, `final/grid_diag_up.png` (mọi khung 15 fps, cỡ game x3, nền xám, vòng đỏ = vai, "HIT" = khung trúng đòn), `final/compare4_hit.png` (khung trúng đòn: `swing --track` | `sweep` | `diag_down` | `thrust`), cùng thư mục `.../scratchpad/s2/final/`. Không có GIF (không yêu cầu). Không ghi gì vào `out/`.

### Việc nhỏ từ lần chấm S1
1. `swing`: `scraps` `floor=True`, `Life(0.033, 0.033, 0.0, 0.3)`: mảnh ở mũi đao không còn rơi dưới đất; hết lúc khung 6 của bản 15 fps (alpha khung 6-8 = 0).
2. `Effect.lint`: lớp primary / core / flash đếm khi `life.start <= 1/30` và `life.end > 0`; `swing` trả `streaks` về `role` mặc định `accent`; lint của `swing` không còn lỗi.
3. Khung trước đòn của `swing --track`: viền `main` 3 px * s nở ra từ lát mỏng (tông `rim`, chỉ ở khung trước đòn, vẽ dưới `mid`).

### Lệch so với task (và lý do)
1. **Bề dày nét**: không dùng `max(hình chiếu thật, w_min * m)`. Hình chiếu thật (`(hilt - tip) . n`) là 23-31 px ở cả gần và xa (R = 120, blade 0,75, k = 0,3) nên tỉ lệ gần / xa chỉ 1,35 (< 2) và ở hai đầu ellipse (nơi pháp tuyến nằm ngang) là cả 90 px, thành một khối tròn bè, không "nhọn" (ảnh đầu tiên). Dùng `max(w_min * m, R * blade * k * (1 + 0,16 * depth) * m / m_gần)`: gần ~ `R*blade*k`, xa mỏng theo `m`. Pháp tuyến dùng là pháp tuyến của cung mũi (hướng vào trong) như spec.
2. **Vector P** của mặt phẳng: spec ghi `P = (-sin roll, cos roll)` không nhân `face`; thế thì `diag_*` quay trái không phải ảnh gương. Dùng `P = (-face * sin roll, cos roll)`.
3. **Dải `edge` trắng** của chế độ `swing3d`: đặt dọc đường lưỡi trong mặt phẳng (từ mũi hướng về vai, dài `min(bề dày, |hilt - tip|)`) thay vì dọc pháp tuyến, vì dọc pháp tuyến thành một que đứng thẳng như lá cờ. Chỉ ở nửa gần.
4. `release` lớp slash 0,36 s (spec 0,27) và `linger` riêng từng hiệu ứng (3,4 / 2,4 / 2,0): với 0,27 và 1,8 cả ba dính `pop` hoặc `cut` ở 15 fps (đuôi sợi tắt hẳn ở h+4). `scraps` `Life(.., 0.33)` để lint "nothing outlives the primary" qua và số khung vẫn là 8 ở 15 fps.
5. `sweep` u0 / u1 = 215 / 410 (xem bảng).
6. Quầng `glow` nửa xa nhân 0,5 như spec; tông nửa xa: `main` -> `deep`, `deep` -> `shade`, `hot` -> `main` (spec chỉ nêu hai cặp đầu).
7. `.claude/skills/fal-image/action-planes.md`: ngoài cột "The effect" còn sửa dòng Status (bỏ *untested* cho phần vfx, giữ cho phần pose) và câu ở mục 6 ("plan S2" -> `--swing`), vì "plan S2" nằm ở đó.
8. Thêm `from ..ink import _disc` (hàm riêng của `ink.py`) vào `slash.py` cho viền `rim`.

### Chưa đạt / còn mở
- Mirror IoU các khung SAU khung trúng đòn thấp (0,3-0,9 lật thẳng): chỉ khung trúng đòn và khung trước đòn đạt >= 0,9 với lệch 1 px; thực tế là hạt `scraps` / nét mảnh lệch 1-2 px, không phải hình học sai.
- `diag_down` khung bao cao / rộng 1,094 sát trần 1,1; `diag_up` sát ngưỡng `pop` (h+1 = 0,556 so với 0,55 cần); ghép thân với r = 85 cho `pop` 47 % (cần `linger` theo r).
- `swing` thư viện 30 fps có thêm cảnh báo `cut` (xem trên).
- Chưa thử trên pose pair thật của chém ngang / xéo; mới ghép lên một khung đứng.
- Nửa xa chưa được "chấm" bằng mắt người trên nhiều thân khác nhau; vệt `sweep` nhìn nghiêng khá mảnh ở nửa xa (11 px).
- Sửa sau khi chấm thử: nửa xa của `--swing` trên lớp slash không có `pre > 0` (ví dụ `crescent --swing`) từng bị bỏ; nay luôn vẽ (kiểm: `crescent --swing ... --split` có `back/` alpha ở 6 / 16 khung).
