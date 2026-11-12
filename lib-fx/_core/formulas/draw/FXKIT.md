# fxkit: hệ thống dựng hiệu ứng theo lớp

`lib-fx/_core/formulas/draw/fxkit/` là cách dựng hiệu ứng chuẩn của dự án từ 2026-11-12. Một hiệu ứng không còn là một hàm vẽ dài
viết tay, mà là **một chồng lớp (layer)**; mỗi lớp có một vai trò, một vòng đời riêng và một chỗ đặt riêng, vẽ giữa **hai điểm a → b**
do người gọi chọn, bằng một **dải màu** và một **seed** quyết định mọi biến thiên hình dạng.

Các họ cũ (`force/shock`, `impact/hit`, `melee/blade` ...) vẫn chạy như trước (module có `VARIANTS`). Họ mới khai báo `EFFECTS`.

## 1. Năm luật mà hệ thống ép buộc

| # | Luật | Hệ thống ép bằng gì |
|---|---|---|
| 1 | **Hình không lặp**: không có hai gai, hai cụm khói, hai tia giống nhau; luôn có thứ bậc 1 lớn, vài vừa, nhiều nhỏ | `vary.py`: `sizes()`, `angles()`, `delays()`, `Rand` theo seed. Không kind nào được vẽ n vật bằng cùng một số. Đổi `seed` ra một bản anh em khác |
| 2 | **Màu hợp lý**: tối ở ngoài và cuối đời, trắng chỉ ở tâm và lúc nóng nhất; nguội dần **xuống dải màu**, không mờ dần | `ramp.py`: lớp không chọn số RGB mà hỏi `Ramp` theo vai trò và độ nóng (`bands(heat)`, `step(heat)`, `smoke()`); `Ramp.problems()` kiểm dải màu |
| 3 | **Nhiều lớp, có chiều sâu**: mỗi lớp một vai trò, sinh lệch nhau, lớp sau thân nhân vật và lớp trước thân | `effect.py`: `Layer(role, z, life)`, `Effect.lint()` đòi đủ số vai trò theo độ nặng, đòi lệch nhịp |
| 4 | **Bắt đầu và kết thúc đúng**: khung trúng đòn phải đọc được ngay; mỗi lớp tự tàn bằng **đổi hình** (mỏng, co, mòn, đứt), lớp chậm sống lâu hơn lớp nhanh; không bao giờ tắt phụt | `timing.py`: `Life(start, attack, hold, release, step)`; hiệu ứng kết thúc khi lớp cuối tàn xong nên khung cuối luôn trống; `fxcheck` đo `end`, `cut`, `pop` |
| 5 | **Linh hoạt điểm đầu, điểm cuối**: đặt a và b ở đâu thì hiệu ứng dời, xoay, kéo dài theo | `space.py`: `Space(a, b, s)`; lớp chỉ dùng `c.sp.pt()`, `c.sp.ang()`, `c.sp.path()`, `c.o`; khung hình tự cắt theo cái đã vẽ nên không bao giờ bị cụt |

## 2. Các tầng của hệ thống

```
palettes.py           16 bảng màu chuẩn (5 bậc)                         dữ liệu màu
fxcore.py organic.py  canvas siêu mẫu, mặt nạ, tô theo khoảng cách mép    vẽ pixel
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
# lib-fx/impact/burst/burst.py
from fxkit import Effect, Layer, Life
TAGS = ["impact", "one-shot", "anchor:contact"]
EFFECTS = {
  "heavy": Effect("heavy", title="Nổ trúng đòn nặng", space="aim", weight="heavy", pal="sun", tags=["heavy"], desc="...",
    layers=[
      Layer("glow",   role="glow",      z="back", life=Life(0.00, 0.05, 0.05, 0.30), r=95),
      Layer("ring",   role="secondary", z="back", life=Life(0.03, 0.10, 0.00, 0.20), r=(30, 120)),
      Layer("spikes", role="primary",             life=Life(0.00, 0.07, 0.03, 0.22), n=9, length=115),
      Layer("core",   role="core",                life=Life(0.00, 0.05, 0.02, 0.18), r=30),
      Layer("sparks", role="particles",           life=Life(0.03, 0.03, 0.00, 0.50), n=12),
      Layer("flash",  role="flash",               life=Life(0.00, 0.03, 0.00, 0.07), r=40)]),
}
EFFECTS["light"] = EFFECTS["heavy"].variant("light", weight="light", layers={"ring": False, "spikes": {"n": 6, "length": 70}})
```

- `space`: `point` (chỉ a), `aim` (a + hướng tới b), `span` (kéo dài từ a tới b: vệt chém, tia), `travel` (bay từ a tới b rồi nổ ở b), `ground` (a nằm trên mặt đất).
- `at` của lớp: `"a"`, `"b"`, `"mid"`, `("a", dx, dy)`, `("b", dx, dy)` (khung trục), `("path", f, bend)`.
- `z`: `back` nằm sau thân nhân vật, `front` nằm trước. Thứ tự trong danh sách = thứ tự vẽ.
- Thời gian tính bằng giây **từ khung trúng đòn** (t = 0). `start` âm = lớp báo trước (tụ lực).

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

```python
@kind("spikes")
def spikes(c, ph, n=8, length=100.0, ...):   # c: Ctx, ph: Phase
```
1. Kích thước là px ở `s = 1`, luôn nhân `c.s`. Vị trí lấy từ `c.o` (điểm neo của lớp) và `c.sp`; hướng lấy từ `c.sp.ang(độ)`
   (0 = dọc a → b, 90 = phía trên). Trọng lực và khói bay dùng trục màn hình (y xuống / lên), không xoay theo a → b.
2. Ngẫu nhiên chỉ qua `c.rng("tên")` (ổn định mọi khung). Muốn rung theo khung thì `c.rng("flicker", số_khung)`.
3. Mỗi vật một cỡ, một hướng, một độ trễ: dùng `sizes()`, `angles()`, `delays()`.
4. Màu chỉ lấy từ `c.pal`: `bands(s, heat)` cho hình đặc tô theo khoảng cách mép, `step(heat)` cho hình nhỏ, `smoke()` cho khói.
5. `ph.grow` (0 → 1) tự áp easing vào nhanh (`out_expo`, `out_back`). `ph.decay` (0 → 1) phải **đổi hình** và ở 1 thì không còn gì.
   Giảm alpha chỉ được theo tối đa 3 bậc phẳng. Khung đầu (`ph.first`) dùng tông quá sáng.
6. Hình đặc sáng vẽ bằng `organic.Shape` + `paint(bands, erode, noise, backing)`. Không blur, không gradient.
7. Xem thử một mình: `python lib-fx/_tools/fxkit_sheet.py <kind> key=value ...` (4 hàng: seed, hướng, cỡ, bảng màu khác nhau).

## 5. Bảng kind

(cập nhật khi thêm kind; chi tiết tham số ở docstring của từng hàm)

| Kind | File | Vẽ gì | Vai trò thường dùng |
|---|---|---|---|
| `core` | `layers/basic.py` | khối nóng ở tâm, vọt ra rồi co và mòn | core |

## 6. Dùng cho nhân vật

```
python lib-fx/build.py impact/burst/heavy --from 120,200 --to 260,150 --pal ice --s 0.8 --seed 3 --fps 15 --out out/heroes/<id>/frames/fx/hit
```
`--from` / `--to` là toạ độ px @2x trong ô của nhân vật (điểm chạm, mũi vũ khí, mục tiêu). Kết quả gồm `frames/@2x`, `@1x`, hai nửa
`back/` và `front/` (vẽ thân nhân vật ở giữa), `meta.json` có `anchor_2x`, `target_2x`, `hit_frame` (đặt khung này trùng khung trúng đòn
của thân) và `origin` (góc trên trái của khung trong toạ độ đã cho). Cùng công thức, đổi `--seed` để mỗi lần đánh ra một bản khác.
