# fxkit: hệ thống dựng hiệu ứng theo lớp

`lib-fx/_core/formulas/draw/fxkit/` là cách dựng hiệu ứng chuẩn của dự án từ 2026-11-13. Một hiệu ứng không còn là một hàm vẽ dài
viết tay, mà là **một chồng lớp (layer)**; mỗi lớp có một vai trò, một vòng đời riêng và một chỗ đặt riêng, vẽ giữa **hai điểm a → b**
do người gọi chọn, bằng một **dải màu** và một **seed** quyết định mọi biến thiên hình dạng.

Các họ cũ (`force/shock`, `impact/hit`, `melee/blade` ...) vẫn chạy như trước (module có `VARIANTS`). Họ mới khai báo `EFFECTS`.

## 1. Phong cách (bắt buộc cho mọi lớp)

Phong cách đo từ các mẫu đã duyệt 9-10/10 (`../rules/01-design-style.md`, `02-animation.md`, `05-birth-erosion-composition.md`):

| Thứ | Luật | Code |
|---|---|---|
| Hình | ít, lớn, nét cong liền có mũi nhọn thật; không ghép từ hình tròn và tam giác | `fxkit/shapes.py`: `tongue`, `lobed`, `shard`, `scrap`, `ribbon`, `spline` |
| Màu | 2-3 tông **phẳng xếp chồng** của một họ màu: `main` (màu đọc được), `deep` (mảng tối bên trong), `hot` (nóng nhất: sâu trong khối, ở gốc hoặc mép dẫn); không viền, không dải đồng tâm, không gradient | `Ink.add(tone, polygon)`, `Ink.paint([...])`, `Ramp.tone()` |
| Nét | viền **nối mịn như Smooth Tool**: góc lõm chỗ hai hình giao được bo, gờ nhỏ sau khi mòn được gọt, mép đều, mũi nhọn thật giữ nguyên; làm tự động trong `Ink.paint` trên từng tông | `smooth_mask(mask, ss, fillet, burr, tip_keep, sigma)`, `Ink(c, smooth=True\|dict\|False)`, `THIN` |
| Quầng sáng | là **bản nhoè của chính hình**, hai cỡ nhoè, màu chính của hiệu ứng; tắt trước khi hình tan (trừ vệt chém giữ tới cuối) | `Effect.glow`, `ink.paint(glow=...)` |
| Sinh | hình nhỏ ở gốc, bung trong 1-4 khung, **ngang trước, cao sau** | `ph.grow` + `out_back`, `out_cubic` |
| Tàn | **mòn và vỡ tại chỗ**: mép và phần mỏng mất trước, lỗ mở ra, mảnh sứt rồi chết khi thành đốm; khung bao giữ gần tới cuối; diện tích giảm theo tỉ lệ cố định mỗi khung; nửa sau vẽ on twos | `erode(mask, keep, ...)`, `decay_share`, `on_twos`, `drop_specks` |

Năm luật mà hệ thống ép buộc:

| # | Luật | Hệ thống ép bằng gì |
|---|---|---|
| 1 | **Hình không lặp**: thứ bậc 1 lớn, vài vừa, nhiều nhỏ; khoảng cách không đều | `vary.py`: `sizes()`, `angles()`, `delays()`, `Rand` theo seed. Đổi `seed` ra một bản anh em khác |
| 2 | **Màu hợp lý** | lớp không ghi số RGB, chỉ hỏi `c.pal.tone(...)`; đổi bảng màu là đổi mọi lớp |
| 3 | **Nhiều lớp, có chiều sâu** | `Layer(role, z, life)`: lớp sau thân (`back`) và trước thân (`front`); `Effect.lint()` đòi đủ vai trò và lệch nhịp |
| 4 | **Bắt đầu và kết thúc đúng** | `Life(start, attack, hold, release)` tính từ khung trúng đòn; hiệu ứng kết thúc khi lớp cuối tàn xong nên khung cuối luôn trống; `fxcheck` đo `end`, `cut`, `pop` |
| 5 | **Linh hoạt điểm đầu, điểm cuối** | `Space(a, b, s)`: đặt a và b ở đâu thì hiệu ứng dời, xoay, kéo dài theo; khung hình tự cắt theo cái đã vẽ |

## 2. Các tầng của hệ thống

```
palettes.py           16 bảng màu chuẩn (5 bậc)                         dữ liệu màu
fxcore.py             canvas siêu mẫu, GIF xem trước                    vẽ pixel
fxkit/shapes.py       hình cong liền: tongue, lobed, shard, scrap, ribbon hình
fxkit/ink.py          Ink (tông phẳng xếp chồng), erode, drop_specks, smooth_mask   tô, mòn, làm mịn nét
fxkit/vary.py         Rand, sizes, angles, delays, varied                biến thiên
fxkit/timing.py       Life, Phase, easing                                thời gian
fxkit/space.py        Space: a, b, khung trục, đường cong a → b           không gian
fxkit/ramp.py         Ramp: bậc màu theo vai trò và độ nóng, màu khói      màu
fxkit/layers/*.py     KIND: một hàm vẽ một loại lớp (bảng ở mục 5)        lớp
fxkit/effect.py       Layer, Effect (chồng lớp, lint, variant), render    hiệu ứng
<nhóm>/<họ>/<họ>.py   EFFECTS = {id: Effect(...)}: dữ liệu, gần như không có code vẽ   thư viện
build.py, _tools/     dựng, cổng chất lượng, biến thể cho nhân vật         công cụ
```

Hiệu ứng mới = **ghép các kind có sẵn bằng dữ liệu**. Chỉ viết kind mới khi không kind nào vẽ được hình cần có.

## 3. Viết một hiệu ứng

```python
# lib-fx/impact/quake/quake.py
from fxkit import Effect, Layer, Life
TAGS = ["impact", "ground", "one-shot", "anchor:ground"]
EFFECTS = {"slam": Effect("slam", title="Nện đất", space="ground", weight="heavy", pal="sun", extent=300, tags=["heavy", "dust"], desc="...",
    layers=[
        Layer("dust",   id="dust_back", role="smoke", z="back", life=Life(0.033, 0.12, 0.1, 0.6), tone="dark", reach=170, height=84),
        Layer("ring",   role="secondary", z="back", life=Life(0.033, 0.12, 0.0, 0.25), r=(30, 165), width=17, squash=0.3),
        Layer("star",   id="splash", role="primary", plane=("ground", 0.32), life=Life(0.0, 0.066, 0.033, 0.3), n=9, arc=(-180, 180), length=160, even=0.7),
        Layer("star",   id="column", role="core",    life=Life(0.0, 0.066, 0.033, 0.234), n=3, arc=(60, 120), length=110),
        Layer("scraps", role="particles",           life=Life(0.033, 0.033, 0.0, 0.55), n=9, arc=(35, 145), gravity=900, r0=40, floor=True),
        Layer("dust",   role="smoke",               life=Life(0.066, 0.1, 0.1, 0.6), tone="light", reach=150, height=60)])}
EFFECTS["stomp"] = EFFECTS["slam"].variant("stomp", weight="medium", layers={"ring": False, "dust_back": False, "splash": {"length": 80}, "column": False})
```

- `space`: `point` (chỉ a), `aim` (a + hướng tới b), `span` (kéo dài từ a tới b: vệt chém), `travel` (bay từ a tới b rồi nổ ở b), `ground` (a nằm trên mặt đất).
- `at` của lớp: `"a"`, `"b"`, `"mid"`, `("a", dx, dy)`, `("b", dx, dy)` (khung trục), `("path", f, bend)`.
- `plane` của lớp: `None` (mặc định) hoặc `("ground", k)`: mọi hình của lớp bị bóp về tỉ lệ y / x = `k` quanh điểm neo của lớp (chuẩn 0.3, bằng `squash` của `ring`), nên lớp nằm bẹt trên mặt đất; quầng sáng lấy từ hình đã bóp nên cũng dẹp. Làm một chỗ trong `Ink.add` / `Ink.cut`, kind không phải làm gì. Vụ nổ trên đất = `star` `splash` (có `plane`, `even` cao cho đều) + `star` `column` (không `plane`, đứng lên). `scraps` có `floor=True`: mảnh sinh trên ellipse dẹp bán kính `r0` và biến mất khi rơi về độ cao nơi nó sinh ra.
- `z`: `back` nằm sau thân nhân vật, `front` nằm trước. Thứ tự trong danh sách = thứ tự vẽ.
- Thời gian tính bằng giây **từ khung trúng đòn** (t = 0). `start` âm = trước khung trúng đòn (đạn đang bay, tụ lực).
- `variant()`: bản anh em: bỏ lớp (`False`), đổi tham số, đổi bảng màu, đổi độ nặng.

### Bảng nhịp chuẩn (30 fps)

| Vai trò | Sinh | Lớn (attack) | Giữ | Tàn (release) | Ghi chú |
|---|---|---|---|---|---|
| flash | 0 | 1 khung | 0 | 2 khung | trắng, quá sáng; chỉ 2 đến 3 khung |
| core | 0 | 1 đến 2 khung | 0 đến 1 | 4 đến 6 | co và mòn, tâm trắng khép lại |
| primary | 0 | 2 khung, vọt quá rồi về | 0 đến 2 | 5 đến 8 | hình chính: gai, lưỡi liềm, tia |
| secondary | +1 đến +2 khung | 3 | 0 | 5 đến 7 | vòng, gai phía sau, tối và mảnh hơn |
| particles | +1 | 1 | 0 | 10 đến 16 | tia lửa, mảnh vụn: sống lâu hơn hình chính |
| smoke | +1 đến +3 | 3 đến 5 | 2 đến 4 | 14 đến 22, on twos | chậm nhất, tan cuối cùng |
| glow | 0 | 1 đến 2 | 1 đến 2 | 8 đến 10 | bậc phẳng, không gradient |
| ground | 0 đến +1 | 2 | 4 đến 8 | 8 đến 12 | vết nứt, vết cháy trên đất |

## 4. Viết một kind (hợp đồng bắt buộc)

Khuôn mẫu: `fxkit/layers/flames.py`. Một kind luôn đi theo bốn bước: **thiết kế hình ở đỉnh** bằng rng có seed → **bung** theo `ph.grow` →
vẽ hình vào `Ink` theo tông → **mòn** theo phần diện tích còn lại (`decay_share`) → `ink.paint`.

1. Kích thước là px ở `s = 1`, luôn nhân `c.s`. Vị trí lấy từ `c.o` và `c.sp`. Đổi hướng trục sang góc màn hình **một lần** (`ax = c.sp.ang(độ)`),
   mọi thứ khác dựng trong toạ độ màn hình (y hướng xuống: góc trục dương là **trừ** radian nhân `c.sp.hand`). Trọng lực, khói bay, mặt đất dùng trục màn hình.
2. Ngẫu nhiên chỉ qua `c.rng("tên")`. Lắc lư, nhấp nháy là hàm của `ph.sec`.
3. Mỗi vật một cỡ, một hướng, một độ trễ: `sizes()`, `angles()`, `rng.uniform`.
4. Màu chỉ lấy từ `c.pal.tone("shade"|"deep"|"main"|"hot"|"white"|"smoke"|"smoke_dark")` (bụi đất: `c.pal.smoke(tone)`).
5. Hình chỉ lấy từ `fxkit.shapes`. Tô chỉ qua `Ink`. Tông trong luôn cắt theo tông ngoài (`& body`). Khung đầu (`ph.first`) tô quá sáng.
6. Tàn: `erode` theo `keep = decay_share(on_twos(ph, c), linger)`; `holes` nhỏ = mòn từ mép (lửa, pha lê), lớn = mở lỗ (khói, vòng),
   `hollow=True` = ăn từ trong ra, còn lại sợi dọc mép (vệt chém, màn pha lê); `shift` cho lỗ trôi (mảnh lửa bay lên). `drop_specks` sau cùng.
6b. **Làm mịn nét**: `Ink.paint` tự làm mịn từng tông (bo góc lõm 2 px, gọt gờ 1 px, làm đều sigma 0.8 px; tất cả nhân `c.s`, kẹp 0.5-2).
   Kind có hình mảnh (ring, streaks, scraps, embers, bolt) dùng `Ink(c, smooth=THIN)` (nhẹ hơn); kind hình cạnh phẳng (crystals) dùng `smooth=False`.
   Hình mảnh dài hơn `tip_keep` (6 px) bám vào hình chính được giữ nguyên như mũi nhọn. Tông trong vẫn cắt theo tông đầu sau khi mịn.
   Đừng tự làm mịn trong kind; chỉ chỉnh `smooth=dict(fillet=..., burr=..., sigma=...)` khi một hình mất nét.
7. Xem thử một mình: `python lib-fx/_tools/fxkit_sheet.py <kind> key=value ... --life s,a,h,r` (4 hàng: seed, hướng, cỡ, bảng màu khác nhau).

## 5. Bảng kind

| Kind | File | Vẽ gì | Vai trò | Life thiết kế |
|---|---|---|---|---|
| `flames` | `layers/flames.py` | cụm lưỡi lửa phun từ gốc: thân, mảng tối bên trong, vũng nóng ở chân | primary | `0, 0.1, 0.1, 0.55` |
| `crystals` | `layers/crystals.py` | cụm gai pha lê cạnh thẳng có mặt sáng, màn cánh trong mờ phía sau | primary | `0, 0.1, 0.066, 0.4` |
| `slash` | `layers/slash.py` | vệt chém quét từ a tới b theo vũ khí: `weapon=sword` (3 sợi dọc liền nhau, mịn, tàn thành 2-3 nét dài), `axe` (4-6 dải song song cách nhau khe hẹp, ngắn, dày, đầu tù), `saw` (kiếm có răng mép trong); `bend=0`: đâm thẳng | primary | `0, 0.1, 0.033, 0.3` |
| `bolt` | `layers/bolt.py` | đạn bay từ a tới b: đầu giọt nước, đuôi sống, tới b đúng khung trúng đòn | primary | `-0.3, 0.3, 0, 0.1` |
| `star` | `layers/burst.py` | chớp trúng đòn: vài mũi dài chênh cỡ, ba tông chồng, tách thành kim khi tàn | primary / core | `0, 0.066, 0.033, 0.33` |
| `streaks` | `layers/burst.py` | vài tia tốc độ mảnh bay ra | accent | `0, 0.033, 0.033, 0.13` |
| `ring` | `layers/burst.py` | vòng chấn động dày mỏng không đều, vỡ thành cung (`squash` < 1: nằm trên đất) | secondary | `0.033, 0.1, 0, 0.23` |
| `smoke` | `layers/smoke.py` | khối khói trong mờ có sừng cong nhọn, rách thành mảnh | smoke | `0.033, 0.13, 0.1, 0.6` |
| `dust` | `layers/smoke.py` | bụi đất: các múi tròn chênh cỡ, đuôi nhọn chạy dọc đất, ba tông, mở từ giữa | smoke | `0.033, 0.1, 0.1, 0.55` |
| `scraps` | `layers/scraps.py` | mảnh cong (dấu phẩy) văng ra, có lực cản và trọng lực | particles | `0.033, 0.033, 0, 0.5` |
| `embers` | `layers/scraps.py` | tàn nhỏ bay lên lần lượt | particles | `0.1, 0.05, 0.3, 0.45` |

## 6. Dùng cho nhân vật

```
python lib-fx/build.py melee/slash/crescent --from 107,191 --to 240,243 --pal frost --seed 3 --fps 15 --split \
    --set slash.bend=0.85 --set slash.width=40 --out out/heroes/<id>/frames/fx/slash
```
- `--from` / `--to`: toạ độ px @2x trong ô của nhân vật (điểm chạm, mũi vũ khí, mục tiêu). Hiệu ứng `ground` và `point` luôn nằm ngang: `--to` chỉ chọn phía trái hay phải.
- `--track 'root_a=X,Y;root_b=X,Y;up=35;dx=0;turn=cw;ease=1.3'` (chỉ họ `melee/slash`, mọi lớp kind `slash`): vệt đi theo cú chém thật thay cho parabol. `--from` / `--to` là
  **mũi** đao lúc đầu / lúc cuối, `root_a` / `root_b` là **chuôi** (cùng toạ độ px @2x của người gọi; đổi từ px ảnh gốc sang ô @2x bằng `tf_of` trong `build_crescent.py`).
  Chuôi đi Bezier bậc hai (điều khiển = giữa x + `dx`, y của chuôi cao hơn - `up`), lưỡi quay quanh chuôi (`turn`, góc nội suy `f ** ease`), vệt = bề mặt lưỡi quét:
  mép ngoài là cung mũi đao, mép trong là đường lưỡi, đầu vệt rộng đúng bằng lưỡi (tham số `blade` của lớp, `--set slash.blade=0.6` = 60 % phía mũi), đuôi nhọn.
  Không có `--track` thì kind chạy như cũ. Tham số `track` có thể đặt bằng code: `Space.world((x, y))` đổi toạ độ người gọi sang canvas.
- `--pal`, `--s`, `--seed`, `--fps`, `--speed`, `--name`; `--set LỚP.THAM_SỐ=GIÁ_TRỊ` chỉnh một lớp cho riêng lần xuất này (`LỚP.off=true` bỏ lớp).
- Kết quả: `frames/@2x`, `@1x`; với `--split` thêm hai nửa `back/` và `front/` (vẽ thân nhân vật ở giữa); `meta.json` có `anchor_2x`, `target_2x`,
  `hit_frame` (đặt khung này trùng khung trúng đòn của thân; lưới khung luôn ghim vào khung trúng đòn, ở mọi fps) và `origin` (góc trên trái của khung trong
  toạ độ đã cho, luôn là số chẵn để bản @1x rơi đúng điểm ảnh).
- Cùng công thức, đổi `--seed` để mỗi lần đánh ra một bản khác. Hình vượt quá vùng làm việc (`extent` px quanh a và b) bị cắt và cổng chất lượng báo `clip`: tăng `extent` của hiệu ứng.
