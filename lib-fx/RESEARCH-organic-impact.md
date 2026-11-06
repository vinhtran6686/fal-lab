# Nghiên cứu: hiệu ứng impact dạng hình tự do (organic) bằng code

Tài liệu gốc cho việc làm hiệu ứng va chạm / xung chấn có hình dạng "vẽ tay" (gai cong, toé, giọt văng, khói nhiều tầng) bằng
Python, không gọi model (0 USD). Viết ngày 2026-11-06 sau khi làm 10 ví dụ trong `impact/hit`, `impact/dash`, `impact/ground`.
Phương pháp chung (ba nhịp, bốn lớp, chiều sâu) ở [DESIGN.md](DESIGN.md); tài liệu này đi sâu phần **hình dạng**.

---

## 1. Vấn đề

Bộ `force/shock` đầu tiên ghép hình học cơ bản: tròn, elip, lưỡi liềm, thấu kính, dải. Kết quả đúng hiệu ứng (6/10) nhưng
**đơn điệu**: mọi hình đều "đúng compa", nên phải bù bằng nhiều tầng.

Ảnh tham khảo của user (Melee / Dash / Ground slam impacts) đẹp vì **hình dạng tuỳ biến kiểu vector vẽ tay**: một khối liền với
gai cong độ dài khác nhau, chỗ nối giữa các gai bo mềm, màu trắng ở lõi chuyển dần ra cam ở mũi theo đúng hình, mảnh văng tách
khỏi khối, khói làm từ nhiều cụm có sáng tối và đường xoáy.

**Câu hỏi:** sinh được hình kiểu đó bằng code không, và hoạt hình nó thế nào?
**Trả lời:** được. Phương pháp ở mục 4, đã chạy được và cho ra 10 ví dụ.

## 2. Phân tích ảnh tham khảo

| Hình trong ảnh | Cấu tạo | Nhận xét |
|---|---|---|
| Melee 1 (chevron, trên trái) | khối hình "<" trắng ở điểm chạm, gai và mảnh dài phóng về một phía | hướng theo đòn; mảnh rời bay xa nhất |
| Melee 2 (nổ sao, trên giữa) | lõi tròn trắng, ~10 gai không đều: 2-3 gai rất dài, vài gai vừa, vài gai ngắn; vài mảnh rời | nhịp dài-vừa-ngắn; khoảng trống giữa gai giữ hình dễ đọc |
| Melee 3 (vòng gai, trên phải) | vòng dày, lỗ ở giữa, gai mọc ra ngoài; mép quanh lỗ trắng, mũi gai cam | lỗ không làm mép trong thành cam: màu tính từ mép NGOÀI |
| Dash 1 (vách, dưới trái) | lưỡi liềm đứng, mép trước trắng, mép sau rách thành gai ngắn | mép sáng nhất ở phía đầu đòn lao tới |
| Dash 2 (xuyên vòng, dưới giữa) | khối trắng phồng + gai dài chảy về sau + vòng elip đứng bao quanh | kết hợp hình tự do với một vòng sạch |
| Ground slam (dưới phải) | 2 khối khói (xám phía sau, kem phía trước), nhiều cụm tròn chồng nhau, đường xoáy, gai sáng phụt chéo lên qua khói, sỏi nhỏ | khói là yếu tố chính, gai là điểm nhấn |

Điểm chung về màu: **không viền tối**; trắng ở chỗ dày nhất, vàng, cam, cam đậm ở mũi. Các dải màu **đi theo hình** (như lồng
nhiều bản co nhỏ của cùng hình), không phải gradient tròn.

## 3. Nghiên cứu từ các nguồn

Có hai hướng tìm song song. Nhiều nguồn chuyên sâu (sách Elemental Magic của Joseph Gilland, video sakuga, PDF style guide của
Riot, bài của Inigo Quilez) bị chặn hoặc phải trả tiền. Những gì dưới đây lấy từ các trang đọc được, liệt kê ở mục 9. Dòng ghi
[nghề] là kinh nghiệm phổ biến, không có nguồn nào ghi thẳng ra.

### 3.1 Nguyên tắc thiết kế (VFX game / toon)

**Hình**
- **Một thành phần chính đọc ra ngay:** sáng, tương phản cao, rõ hình. Các thành phần phụ (tàn lửa, bụi, mảnh) thì tối hơn, ít tương phản, hình đơn giản (Riot style guide, qua VFX Apprentice).
- **Chi tiết dày đều đặn là nhiễu:** mảnh cùng cỡ cũng là nhiễu. Phải thay đổi kích thước (RealtimeVFX).
- **Nhịp gai [nghề]:** 1-3 gai chính dài gấp 2-3 lần gai vừa, 3-5 gai vừa, vài gai ngắn. Tổng 5-9 gai; trên khoảng 12 gai là rối. Khoảng cách không đều, các gai cong cùng một chiều (xoáy).
- **Gai thẳng tắp vẫn hợp:** vài "cột" gai thẳng đâm ra trên nền lõi tròn trông rất đã mắt (RealtimeVFX, thread hit spark).
- **Cường điệu rồi giản lược:** đẩy hình thật mạnh trước, sau đó đơn giản hoá cho dễ đọc (Luis Aguas, WoW VFX, 80.lv).

**Màu**
- Trắng chỉ ở lõi cú chạm. Thân để giá trị trung bình (Riot).
- Dải màu trắng → vàng → cam → đỏ cho chiều sâu (RealtimeVFX). Tâm nhỏ sáng, ra ngoài tối dần (Game Developer, "Back with a bang").
- Phần tối nhất đặt phía sau: một hình nền tối, trong suốt đặt sau hình sáng tạo tương phản mà không cần viền (Aguas).
- Vòng phụ tương phản thấp hơn (cam, đỏ) so với hình chính.

**Nhịp (30 fps)**
- Ba giai đoạn: báo trước → bùng → tan. Đạt đỉnh sáng và độ bão hoà trong 1/4 đầu đời, sau đó giảm mượt (Riot).
- Hit spark: frame đầu bằng khoảng 70% cỡ, 2-3 frame đủ cỡ, rồi 4-6 frame vỡ ra. Đảo trắng → tối → màu ở frame đầu tạo cú giật mạnh (RealtimeVFX).
- **Không thu nhỏ khi tan:** lõi phải tiếp tục nở cho tới khi biến mất; co lại trông yếu (hai thread RealtimeVFX).
- **Vỡ [nghề]:** gai mỏng dần từ gốc, tách ra thành mảnh bay tiếp; lõi rỗng ra; màu tụt một bậc (trắng thành vàng, vàng thành cam).
- **Mờ dần trước khi hết,** không cắt ngang (VFX Apprentice).
- **Khói toon (FlashFX):**
  - Bắt đầu từ một cục nhỏ; 3 frame đầu "on 1s", nở nhanh, sau đó "on 2s", mép chậm dần.
  - Khoảng frame 4 giữa mở ra một lỗ và lan ra mép; các cụm vỡ ra, cụm nhỏ biến mất trước.
  - Nhiều nhóm cụm sinh lệch nhau 4-5 frame.
  - Tô màu: nền sáng cộng một lớp tối.
- **Khói tầng [nghề]:** trên sáng, giữa trung tính, dưới tối; đường xoáy ở mép trước.

**Theo loại đòn**
- **Melee:** tia toả tròn nhưng thiên về hướng đòn, ngắn (6-9 frame), rơi đúng frame gây sát thương, có hit-stop (cột Sakurai).
- **Dash [nghề]:** gai kéo dài theo hướng lao, lệch một phía; vệt phía sau; mảnh bay tới trước; bụi thấp kéo sau.
- **Ground slam:** vòng dẹt bám mặt đất, cột hoặc gai đứng lên, đá văng hai bên; khói là chính, cuộn ra ngang, sống lâu (15-30 frame), tan chậm (80.lv, stomp dust).

### 3.2 Thuật toán sinh hình

| Cách | Ý chính | Ưu | Nhược |
|---|---|---|---|
| A. SDF + smooth-union | mỗi phần là một hàm khoảng cách; gộp bằng smooth-min `smin(a,b,k) = min(a,b) - h²k/4` với `h = max(k-\|a-b\|,0)/k`; dải màu = ngưỡng `d < -inset` | góc bo, lỗ, dải màu, ăn mòn đều trong một mô hình | chậm (mỗi phần tính trên cả khung; 20 gai x 8 đoạn khoảng 0,5-1 s/frame nếu không cắt theo khung bao) |
| B. Bán kính cực r(θ) | `r = R0 + Σ A_i·K((θ-θ_i)/w_i)`, kernel `K(u) = max(0,1-\|u\|)^p` (p>1 cho mũi nhọn, sườn lõm); gộp bằng log-sum-exp; móc mũi bằng `θ' = θ + hook·e²` | nhanh (5-20 ms), vector | chỉ hình "hình sao" (mỗi tia cắt mép một lần): không lỗ, không móc mạnh |
| C. Nét gai + gộp | mỗi gai là một nét thon dọc đường tâm cong, gộp tất cả (union), bo góc bằng "đóng hình" (closing: nở f rồi co f), dải màu bằng co hình (buffer âm) | kiểm soát như vẽ tay, mọi kiểu hình | cần thêm bước để có dải màu đều |

Hai mẹo quan trọng từ nghiên cứu:
- **Đóng hình** (nở rồi co cùng bán kính) chỉ bo góc LÕM, giữ nguyên mũi gai nhọn. Làm ngược lại (co rồi nở) sẽ bo luôn mũi gai.
- **Ăn mòn có nhiễu** `giữ điểm có d > e(t) + nhiễu` làm phần mảnh biến mất trước, nên hình tự vỡ thành giọt. Đây chính là kỹ thuật "alpha erosion" trong shader VFX.

## 4. Phương pháp đã chọn

Kết hợp **C để dựng hình** với **bản đồ khoảng cách raster (cách A) để tô màu và ăn mòn**:

```
mặt nạ (siêu mẫu 3x)  <-  gộp các phần: thorn() gai cong thon, blob() khối méo, crescent(), shard() giọt, ring_halves()
        | đóng hình (closing) bằng 2 distance transform  -> bo góc lõm giữa các gai, mũi vẫn nhọn
        | dist = distance_transform_edt(mặt nạ)          -> khoảng cách mỗi điểm tới mép (px)
        | ăn mòn: giữ dist > e(t) + nhiễu(x,y)           -> vỡ thành giọt khi tan
        | lỗ khoét SAU khi đo khoảng cách                 -> mép quanh lỗ vẫn trắng (vòng gai)
        | nền tối trong suốt = mặt nạ nở thêm vài px      -> tương phản không cần viền
        | dải màu theo dist: tip < 1.3 < rim < 3.6 < body < 6.4 < light < 9.5 < core < 13.5/heat < white
```

Vì sao chọn cách này:
- **Dải màu tự đi theo hình:** gai mảnh không bao giờ đủ dày để vào dải trắng, nên mũi gai tự thành cam; lõi dày tự thành trắng. Đúng như ảnh tham khảo mà không cần tô tay.
- **Hoạt hình chỉ là dịch ngưỡng:** nguội = dải trắng hẹp lại (`heat` giảm); tan = `e(t)` tăng.
- **Nhanh:** khoảng 0,25 s/frame ở 300x300 siêu mẫu 3x, nhờ `scipy.ndimage.distance_transform_edt`.
- **Không thêm thư viện:** chỉ dùng Pillow, numpy, scipy, đều đã có trong `requirements.txt`.

Code ở `_core/organic.py`:

| Hàm | Làm gì |
|---|---|
| `Shape(canvas)` | mặt nạ cỡ siêu mẫu của canvas; `.poly()`, `.ellipse()`, `.line()`, `.hole()`, `.paint(bands, a, fillet, erode, noise, seed, backing)` |
| `thorn(x, y, ang, L, W, bend, p, sy)` | gai từ gốc (x,y): đường tâm cong dần `ang + bend·s²`, bề rộng `W/2·(1-s)^p` (p=1.5 cho sườn lõm, mũi nhọn); `sy` dẹt cho mặt đất |
| `shard(x, y, ang, L, W, bend)` | giọt / mảnh bay: đầu tròn, đuôi thon ngược hướng bay |
| `blob(x, y, r, sy, wob, freq)` | khối tròn méo (hai sóng sin chồng lên nhau) |
| `crescent()`, `ring_halves()` | lưỡi liềm đứng, vòng elip (vẽ hai nửa để không tự cắt) |
| `spark_bands(pal, s, heat)` | 6 dải màu theo khoảng cách; `heat` 1 → 0 làm lõi trắng co lại |
| `thorns_at(sh, cx, cy, thorns, t, life, ...)` | hoạt hình gai: frame đầu 70%, vượt đà, nở thêm 15%, rồi mỏng đi, ngắn lại, trượt khỏi thân (tách thành mảnh) |
| `shards_at(...)` | giọt bay có lực cản `d0 + v(1-e^{-kt})/k` (+ trọng lực), thu nhỏ về 0 |
| `cloud(canvas, puffs, pal, ...)` | khói: gộp các cụm méo; tô 3 tông bằng cách dịch hình về phía/ra xa nguồn sáng (mép xa sáng thành tối, mép gần sáng thành sáng); đường xoáy; lỗ giữa; ăn mòn |
| `noise_field()` | nhiễu mượt (Gaussian lọc nhiễu trắng), lưu đệm theo seed |

Bảng màu `SPARK` gồm: `tip` (cam đỏ), `rim`, `body`, `light`, `core`, `white`, `back` (nền tối). Khói dùng `DUST` (sáng) và `DUST_BACK` (xám tối).

## 5. Công thức cho từng loại (đã dùng trong 10 ví dụ)

| Loại | Khung | Đời | Cấu tạo |
|---|---|---|---|
| hit (cận chiến) | 300x300, neo ở tâm | 0,38 s (14 frame) | lõi méo r 28-32 + 2 gai chính (L ~105, W ~35) + 4 gai vừa + 3 gai ngắn, cùng chiều cong; 0-2 tia thẳng mảnh; 3-5 giọt từ mũi gai chính; frame đầu trắng toàn bộ; lõi rỗng ra khi đủ lớn (> 7 px) |
| dash (lướt) | 340-400 x 280, neo ở điểm chạm, đòn tới từ -x | 0,4 s (15 frame) | hình chính bám mép trước (lưỡi liềm, khối phồng); gai chảy về sau dọc đường lao; giọt bay tới trước; có thể thêm vòng elip đứng |
| ground (nện đất) | 440x300, neo ở mặt đất | 0,8 s (25 frame) | khói 2 lớp (xám sau, kem trước) cuộn ra hai bên, lỗ giữa mở sau 0,25 s, ăn mòn từ 55% đời; gai sáng phụt lên giữa hai lớp khói; sỏi văng vòng cung có trọng lực |

Tham số tinh chỉnh chính:
- **Độ dày gai `FAT` (1,4-1,55):** mảnh quá thì gai thành nét kẻ, không ra "thịt".
- **`thin_by` (0,55):** mức mỏng đi khi tan.
- **`detach` (0,35-0,5):** gai trượt khỏi thân bao xa.
- **`fillet` (3,5-4 px):** bán kính bo góc lõm.
- **Ngưỡng ăn mòn:** `erode = 10·smooth(0.62, 1, u)`, `noise = 4.5·smooth(0.5, 1, u)`. Bắt đầu sớm hơn thì hình tan quá nhanh.
- **Nền tối:** `backing = (3.5 px, back, 0.32)`.

## 6. Nhật ký lặp (lỗi gặp và cách sửa)

| Vòng | Thấy gì | Sửa |
|---|---|---|
| Thử tĩnh 1 | Kỹ thuật đúng ngay: gai cam, lõi trắng, góc bo mềm | giữ |
| hit v1 | Gai mảnh như nét kẻ; lõi trắng nhỏ; tan quá sớm (0,27 s là hết) | gai dày x1,55, lõi to hơn, lùi ăn mòn từ 50% xuống 62% đời, `thin_by` 0,8 thành 0,55 |
| hit v2 | Lỗ ở tâm mới mở trông như chấm bẩn | chỉ khoét khi bán kính > 7 px |
| dash v1 | Vách lưỡi liềm mỏng, không có lõi trắng | độ dày 24 thành 36 px |
| ground v1 | Vòng chấn đất loang quá rộng, bị cắt mép dưới | bán kính tối đa 150 thành 108, khung 280 thành 300 |
| dash comet | Giọt bay tới trước chạm mép phải | khung riêng 400x280 cho hiệu ứng này (`frame` trong CATALOG) |

Kiểm tra bắt buộc trước khi đưa user xem (DESIGN.md §7):
- Phóng to từng hàng của gallery.
- Xem từng frame liên tiếp ở các chỗ chuyển nhịp.
- Không frame nào chạm mép khung.

## 7. Cách làm một hiệu ứng mới theo phương pháp này

1. Xem ảnh tham khảo, tách ra: hình chính, cụm gai (đếm chính / vừa / ngắn), mảnh rời, lớp khói, hướng.
2. Trong `<nhóm>/<họ>/<họ>.py`:
   - tạo `Shape(front)`;
   - thêm thân (`blob` / `crescent`);
   - thêm gai bằng `thorns_at` với danh sách `(góc, dài, rộng, cong, bán kính gốc[, trễ])`, cùng một chiều cong;
   - thêm giọt bằng `shards_at`;
   - nếu có lỗ thì `hole`;
   - cuối cùng `paint(spark_bands(...), erode=..., noise=..., backing=...)`.
3. Khói: `cloud(front, puffs, DUST_BACK)` cho lớp sau, `cloud(front, puffs, DUST, tones=("base", "light", "high"))` cho lớp trước. Gai sáng vẽ giữa hai lớp.
4. Frame đầu (t < 1/30): toàn bộ trắng (`bands = [(1.2, light), (None, white)]`).
5. `python lib-fx/build.py <nhóm>/<họ>`, kiểm tra theo §6, để `draft` cho user duyệt.

## 8. Hướng mở rộng

- **Móc mũi gai mạnh hơn:** dùng đường cong Bezier bậc 3 cho đường tâm gai (hiện tại `bend·s²` chỉ là cong đều).
- **Dải màu tròn hơn ở lõi:** tô theo `mix(dist, dist_tới_tâm, 0.5)`, cho lõi trắng tròn như ảnh tham khảo.
- **SDF smooth-union thật:** gộp các phần bằng `smin`, cắt theo khung bao từng phần cho nhanh, nếu cần bo góc mềm hơn closing.
- **Bảng màu khác:** băng, độc, thánh, bóng tối. Mỗi bảng chỉ cần 7 màu theo khoá của `SPARK` (có `back`).
- **Xuất @1x** và đưa vào game.
- **Tái dùng:** gai và giọt `organic` cho lửa (gai thành lưỡi lửa), nước (giọt, vòng tóe), máu, nổ (`explosion/blast`).

## 9. Nguồn

Thiết kế / nghề:
- https://www.vfxapprentice.com/blog/10-league-of-legends-vfx-design-tips (tóm tắt style guide VFX của Riot)
- https://www.vfxapprentice.com/blog/the-soul-of-effects-what-is-timing-in-vfx
- https://realtimevfx.com/t/stylised-explosive-and-fiery-hit-spark-looking-for-feedback/11286
- https://realtimevfx.com/t/stylized-cartoon-explosion-overwatch-inspired/1767
- https://realtimevfx.com/t/stylized-explosion-in-ue4-how-to-improve/20311
- https://80.lv/articles/world-of-warcraft-vfx-overview-from-luis-aguas/
- https://80.lv/articles/impactful-anime-style-stomp-dust-vfx-created-with-unity
- https://flashfx.blogspot.com/search/label/Smoke
- https://www.gamedeveloper.com/art/2d-game-art-for-programmers-back-with-a-bang-
- https://sourcegaming.info/2015/11/11/thoughts-on-hitstop-sakurais-famitsu-column-vol-490-1/ (chỉ đọc đoạn trích)

Thuật toán:
- https://iquilezles.org/articles/smin và https://iquilezles.org/articles/distfunctions2d (bị chặn, đọc qua trích dẫn; Shadertoy: https://www.shadertoy.com/view/WtdBRS, https://www.shadertoy.com/view/4lcBWn)
- https://github.com/glslify/glsl-smooth-min
- https://ptfl.pages.dev/blog/signed-distance-fields-c/
- https://gist.github.com/munrocket/30e645d584b5300ee69295e54674b3e4
- https://vfxdoc.readthedocs.io/en/latest/shaders/alpha-erosion/
- https://realtimevfx.com/t/water-ball-explosion-using-shader-graph/6868
- https://realtimevfx.com/t/stylized-zelda-vfx/5234
- https://engineered.at/articles/stylized-vfx-in-rime
- https://mitchmcclellan.com/2D-toon-shading-for-vfx-flipbooks/
- https://shapely.readthedocs.io/en/stable/reference/shapely.buffer.html
- https://gist.github.com/Kcnarf/eb45dd635f244f9c03b88563ce44e22d
- https://openprocessing.org/sketch/2506656
- McGuire, "Real-Time Cartoon Rendering of Smoke" (SIGGRAPH 2004 poster): https://history.siggraph.org/wp-content/uploads/2023/01/2004-Poster-026-Mcguire_Real-Time-Cartoon-Rendering-of-Smoke.pdf
- https://faculty.digipen.edu/~gherron/references/References/NPR/mf-2006-toonsmoke.pdf
