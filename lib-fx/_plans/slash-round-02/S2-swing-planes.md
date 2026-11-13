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
- [ ] `sweep`, khung trúng đòn: khung bao của vệt có cao / rộng ≤ 0,40; có điểm ảnh ở **cả** `back/` và `front/`; phần `back/` nằm ở nửa trên của khung bao, phần `front/` ở nửa dưới.
- [ ] `sweep`: bề dày nét lớn nhất ở phần gần ≥ 2 lần bề dày lớn nhất ở phần xa.
- [ ] `diag_down`: điểm đầu vệt (f = 0) cao hơn điểm cuối (f = 1) ít nhất `0.5 r`; khung bao cao / rộng trong 0,5-1,1. `diag_up`: ngược lại.
- [ ] Quay trái (`--from 300,150 --to 180,150`): hình là ảnh gương qua trục đứng của bản quay phải (so mặt nạ đã lật: IoU ≥ 0,9); phần gần vẫn ở dưới, phần xa vẫn ở trên.
- [ ] `k=1.0` cho một cung tròn không dẹt, toàn bộ ở `front` (kiểm mô hình: `--swing "k=1;roll=0;u0=110;u1=-20"`).
- [ ] Nhịp và tan như `swing`: khung trước đòn là lát mỏng; ở 15 fps `A(h+1)/A(h)` ≤ 0,75, `A(h+2)/A(h)` ≤ 0,45, `A(h+3)/A(h)` ≤ 0,2; `fxcheck` không FAIL / `pop` / `cut`.
- [ ] Ghép thử lên thân: dùng `out/heroes/azure_blade/frames/skill_crescent_puppet_side/frames/@2x` khung 1 (dáng đứng) làm nền, đặt vai bằng mắt (ghi toạ độ đã dùng),
      dựng `sweep` với `--split`, ghép `back` dưới thân và `front` trên thân: nhìn thấy vệt **vòng quanh thân** (đi sau rồi ra trước). Ảnh lưu thư mục tạm, không ghi vào `out/`.
- [ ] Không hồi quy: `crescent`, `heavy`, `thrust`, `axe`, `axe_heavy` (30 fps) và `swing --track` (lệnh của S1, 15 fps) cho khung **giống hệt** trước task này (so hash),
      trừ thay đổi có chủ ý của "Việc nhỏ" 1 và 3 trên `swing` (ghi rõ khung nào đổi).
- [ ] `python lib-fx/build.py melee/slash --check` không FAIL; `python lib-fx/_tools/fxkit_test.py` qua.
- [ ] Ba ảnh lưới (mỗi hiệu ứng: mọi khung ở 15 fps, cỡ game x3) và một ảnh so bốn loại cạnh nhau ở khung trúng đòn: bổ dọc (`swing --track` của S1), `sweep`, `diag_down`, `thrust`.

## Kết quả (người làm điền: giá trị `swing` cuối cùng của ba hiệu ứng, số đo từng tiêu chí, đường dẫn ảnh, chỗ chưa đạt, lệch so với task và lý do)
