# lib-fx/_core/formulas/vector: bộ dựng VFX vẽ tay bằng path vector

**Phiên bản 1.0, chốt 2026-11-08**, sau hai bài test được user chấm 9-10/10: `swirl-slash` (2 hiệu ứng xoáy chém) và `element-trio`
(3 hiệu ứng phun từ đất: lửa, Arcane, Toxic, cả ba 10/10). Kết quả đo gốc: [../../results/bezier-research/FINDINGS.md](../../results/bezier-research/FINDINGS.md).

**Nền tảng thiết kế** (phong cách, màu, vòng đời, cách đọc bản gốc, đặc tả bộ sinh, kèm số đo): [rules/](../rules/README.md).
**Xem kết quả** các hiệu ứng đã dựng (GIF so với bản gốc, frame, SVG): [results/vector-showcase/](../../results/vector-showcase/README.md).

0 USD, không gọi model. Python: numpy, scipy, Pillow, opencv-python-headless, scikit-image (`pip install scikit-image opencv-python-headless`).
Tên module chỉ phương pháp, không gắn với hiệu ứng nào: mọi thứ riêng của một hiệu ứng nằm trong **một file profile JSON** (`profiles/<tên>.json`).

## 1. Mục đích và phạm vi

**Mục đích.** Biến một hiệu ứng VFX 2D vẽ tay (GIF/frame tham khảo) thành **dữ liệu vector sạch và đo được**: mỗi lớp màu là path Bézier
mượt như vẽ bằng pen tool, kèm gradient, glow, độ đục và nhịp thời gian của bản gốc. Từ đó (a) dựng lại hiệu ứng ở độ phân giải bất kỳ,
đổi màu, xuất SVG/PNG; (b) học **cách designer vẽ** để về sau **sinh hiệu ứng mới** (mục 9).

| Làm được (v1.0, đã kiểm chứng) | Chưa làm được |
|---|---|
| Dựng lại hiệu ứng flat-colour vẽ tay từ GIF: hình từng lớp, thứ tự tô, gradient mép, glow, độ đục theo frame | Sinh hiệu ứng mới cho loại **khác slash** (nổ / phun chưa có bộ sinh); slash theo **quỹ đạo user vẽ** (STATUS §3.1) |
| Hình dạng: xoáy / lưỡi liềm (khung cực), phun từ đất / thẳng (khung thẳng), vòng elip phối cảnh (`EllipseFrame`), phản chiếu sàn (`ReflectFrame`); **sinh slash mới** (4 kiểu, `gen-slash`) | Theo dõi **từng hình** qua các frame (mới đo tổng thể: diện tích, số mảnh) |
| Lớp đặc, lớp trong mờ (màn), lớp tối trong mờ (bóng khói), mảnh vỡ mờ dần | Gradient tô trong thân theo chiều cao / theo vùng (chỉ có gradient theo mép) |
| Làm đều nét kiểu Illustrator (0 điểm gãy), xuất SVG mỗi lớp một path | Hạt bay có quỹ đạo (tàn lửa chỉ được dựng lại như hình tĩnh từng frame) |
| Đo vòng đời: pha bùng / đỉnh / vỡ / tàn, frame giữ (vẽ "on twos") | Xuất thẳng sang chuẩn lib-fx (`sheet.png`, `meta.json`, @2x, nền trong suốt) |
| Trang review chấm từng lớp từng frame | Kết cấu (texture), vệt nhiễu, hiệu ứng 3D |

## 2. Tính năng

| Nhóm | Tính năng | Ở đâu |
|---|---|---|
| Đọc bản gốc | cắt GIF theo khung từng biến thể, phóng to GIF nhỏ (`source.scale`) | `measure.ingest` |
| | ứng viên màu phẳng (đếm màu đúng mã, chỉ số interior/compact, ảnh mặt nạ) + gom cụm màu k-means cho bản gốc có dither | `palette` |
| | mặt nạ lớp theo **đường màu** (màu phẳng + màu mép), theo **độ đục** so với nền (`alpha`), hoặc **tối hơn nền** (`darker_than_bg`) | `measure.layer_masks` |
| | lấp khe khử răng cưa giữa các lớp; nhóm lớp chỉ khi có nét tối thật | `measure.full_targets` |
| | đo gradient mép, glow (theo khoảng cách hoặc làm nhoè hình × độ mạnh từng frame), độ đục từng frame; tự loại thành phần hẹp hơn 1,5 px gốc | `measure.measure_profile` |
| | đo vòng đời: diện tích, số mảnh, mảnh lớn nhất, chiều cao, frame giữ, các pha | `lifecycle` |
| Dựng hình | khung toạ độ của hiệu ứng: cực (xoáy, vòng) / thẳng (phun, đâm), đặt riêng từng biến thể | `frames.py` |
| | **nét thon** (xương sống Bernstein + bề rộng `W·(t+e0)^a·(1−t+e1)^b`), preset `crescent`, `tongue`, `feather`, `notch` | `strokes.py` |
| | khớp lớp = thân bền vững + lưỡi cộng + vết khoét, mỗi mảnh phải tăng IoU | `fit.fit_layer` |
| | **Smooth & Simplify** (nối khe, góc thật hai tầm, làm trơn theo độ cong ít biến thiên, nắn gãy < 35°, gộp đoạn, tay nắm ≤ 0,45) | `smooth.py` |
| Tô | tô chồng (lớp dưới chạy dưới lớp trên), gradient trong theo mép phần nhìn thấy, glow, độ đục từng frame | `compose.py` |
| Kiểm tra | IoU, điểm gãy, điểm uốn, độ biến thiên độ cong; trang review có nút Đạt / Cần sửa | `metrics.py`, `review.py` |

## 3. Hiệu ứng đã kiểm chứng

| Profile | Biến thể | Dạng | Điểm user | Điểm đáng chú ý |
|---|---|---|---|---|
| `swirl-slash` | fire, frost | xoáy chém, khung cực, 3-4 lớp | 9 / 9-10 | gradient mép vàng → cam; tô chồng; làm mịn mạnh cho băng |
| `element-trio` | fire | phun lửa, khung thẳng, 2 lớp | 10 | glow là bản làm nhoè hình, tắt dần (gain 1 → 0 từ frame 19) |
| | arcane | pha lê + cánh, 3 lớp | 10 | màn cánh trong mờ (độ đục ~0,45); tím nhạt mờ dần 1 → 0,59 |
| | toxic | khói độc + vòng sáng, 2 lớp | 10 | bóng tối trong mờ (`darker_than_bg`); không có gradient mép |
| `slash-trio` | blue, pink, gold (+ `*_refl`) | nhát chém, khung cực; phản chiếu khung thẳng ngang, 2-3 lớp | đạt, cả 3 | glow giữ sáng trên tia; phản chiếu là biến thể riêng |

Trang review: Swirl Slash Shapes https://claude.ai/artifact/QYf1pHQVRyrNRWtUyAdKGR, Element Trio https://claude.ai/artifact/6Vw3supbrvPSULNoNsxCzn.

## 4. Lệnh

```
python lib-fx/_tools/vectorfx.py gen-slash NAME [--variant blue|pink|gold] [--frame SEED] [--style crescent|loop|loop-heavy|front-heavy|combo|x] [--dummy]   SINH nhát chém mới từ luật (gen_slash.py; loop: gen_slash_loop.py)
python lib-fx/_tools/vectorfx.py init      GIF NAME                            bản nháp profile: tự tìm khung cắt (+ phản chiếu), frame, lớp màu
python lib-fx/_tools/vectorfx.py check     PROFILE                             điểm ảnh sáng không lớp nào nhận; báo "MISSING LAYER" khi một màu chiếm phần lớn
python lib-fx/_tools/vectorfx.py palette   PROFILE [--variant V] [--frame N]   màu phẳng + cụm màu + ảnh mặt nạ từng màu
python lib-fx/_tools/vectorfx.py ingest    PROFILE                             cắt source.gif thành frame (source.crops, source.scale)
python lib-fx/_tools/vectorfx.py measure   PROFILE [--frames 3-5]              đo gradient, glow, độ đục; ghi vào PROFILE
python lib-fx/_tools/vectorfx.py rebuild   PROFILE [--frames a-b] [--variants a,b] [--refit]
python lib-fx/_tools/vectorfx.py review    PROFILE                             ảnh từng lớp, GIF, review/index.html
python lib-fx/_tools/vectorfx.py all       PROFILE                             rebuild + review
python lib-fx/_tools/vectorfx.py lifecycle PROFILE                             vòng đời: pha, diện tích, số mảnh, frame giữ
python lib-fx/_tools/vectorfx.py track     PROFILE                             theo dõi từng mảnh: lớn, tách, co, trôi, chết
python lib-fx/_tools/vectorfx.py study     PROFILE                             lúc sinh, cách mép bị ăn, bố cục đỉnh (rules/05)
python lib-fx/_tools/vectorfx.py showcase  PROFILE                             xuất GIF, frame, SVG vào ../results/vector-showcase/ (có trong git)
```

`PROFILE` là đường dẫn hoặc tên trong `profiles/`. Kết quả ở `lib-fx/_study/<tên>/vector/` (không vào git): `strokes/` (nét đã khớp, cache;
`--refit` để khớp lại), `frames/`, `flat/`, `svg/`, `report.json`, `lifecycle.json`, `review/index.html` (publish bằng Artifact tool cùng
`img/`). Khớp nét ~1 phút / frame / biến thể ở ảnh 700-840 px; chạy song song nhiều `rebuild --variants`. Đổi màu, glow, độ đục, độ mượt
chỉ cần `rebuild` không `--refit` (vài phút).

```python
import sys; sys.path.insert(0, "lib-fx/_core")
from vector import Profile, pipeline, review, smooth_simplify, crescent, tongue, feather, PolarFrame, LinearFrame
```

## 5. Quy trình cho một bản gốc mới

**Nhanh (1.4):** `init GIF NAME` → xem `check` (và ảnh `check_<v>.png`) → chỉnh lớp nếu cần (thêm màu được báo thiếu; lớp tối trong mờ /
màn mờ vẫn phải thêm tay: `darker_than_bg`, `alpha`) → `measure` → `all`. Kiểm chứng trên `slash-trio`: tự ra đúng 6 vùng (3 nhát + 3 phản
chiếu) và đúng lớp của nhát xanh, bắt được lớp thân hồng mà lần làm tay suýt bỏ sót; trên `element-trio`: đúng 3 vùng, tự chọn phóng 3x.

**Đầy đủ (từng bước bằng tay):**

1. GIF vào `ref/vfx/<tên>/reference.gif`. Xem một tấm tổng hợp các frame để biết có mấy hiệu ứng, cạnh nhau hay nối tiếp, cỡ bao nhiêu.
2. Profile mới: `name`, `source` (`gif`, `crops` từng biến thể, `scale` = 3 nếu mỗi hiệu ứng < ~250 px, `frames`, `background_frame` nếu có
   frame không còn hiệu ứng), `frame` (`polar` cho xoáy/vòng, `linear` + `angle` cho phun/đâm; đặt riêng trong `variants.<v>.frame` khi cần).
3. `ingest`, rồi `palette` ở một frame giữa. Bản gốc màu phẳng sạch: dùng danh sách màu đúng mã. Bản gốc nhỏ / dither: dùng cụm màu, **xem ảnh**:
   cụm sáng gọn là lớp, cụm tối lan rộng là glow.
4. Viết lớp: `colours` (màu phẳng, thêm màu mép nếu có), `tol` 14-30, `order` (dưới → trên; lớp có mũi đâm sang lớp khác nằm trên). Lớp trong
   mờ / mờ dần: `alpha: [lo, hi]` (tách màn mờ và phần đặc cùng màu thành hai lớp, ngưỡng ~0,7). Bóng tối: `darker_than_bg`. Glow: `halo_model: "blur"`.
5. Kiểm tra mặt nạ bằng mắt trên 3 frame (đầu, đỉnh, tàn) trước khi khớp.
6. `measure` (ghi gradient, glow, độ đục vào profile), `lifecycle`, `all`, publish review, sửa theo nhận xét, `rebuild` lại.

## 6. Kiến trúc

```
GIF ─ ingest ─► frames ─► measure.layer_masks (đường màu | độ đục | tối hơn nền) ─► full_targets
                                                                                       │
frames.make_frame (polar | linear) ◄────────────────────────────────────────────────────┤
                                                                                       ▼
fit.fit_layer (dải → nét thon: thân + lưỡi + vết khoét) ◄── compose.underlay_target (lớp dưới chạy dưới lớp trên)
      ▼
smooth.smooth_simplify ─► compose.composite (gradient trong, glow × gain[frame], opacity[frame]) ─► PNG + SVG ─► metrics ─► review
```

| File | Vai trò |
|---|---|
| `profile.py` | đọc/ghi profile, mặc định, mô tả mọi khoá |
| `measure.py` | ingest, nền, màu phẳng, cụm màu, mặt nạ, lấp khe, gradient, glow (2 mô hình), độ đục |
| `lifecycle.py` | vòng đời của bản gốc (mục 8) |
| `tracking.py` | theo dõi từng mảnh qua các hình vẽ (rules/02 §2) |
| `frames.py` | khung cực / thẳng, tách mặt nạ thành dải (`edge_bias`) |
| `strokes.py` | đơn vị hình (nét thon) + preset |
| `fit.py` | đo tham số nét, khớp lớp (tính điểm tăng dần) |
| `smooth.py` | Smooth & Simplify |
| `compose.py` | tô chồng, gradient, glow, độ đục, SVG |
| `metrics.py` | IoU, độ mượt path |
| `pipeline.py` | rebuild từng frame, cache nét, báo cáo |
| `review.py`, `review_page.html` | ảnh, GIF, trang review tiếng Việt |
| `bezier.py` | Bézier: Schneider fit, góc, viền, raster, SVG |

## 7. Khoá profile và tham số (mặc định đã kiểm chứng)

| Khoá | Mặc định | Ý nghĩa / khi nào chỉnh |
|---|---|---|
| `source.scale` | 1 | phóng to khi ingest (GIF nhỏ: 3) |
| `layers.<l>.colours`, `tol` | — / 12-30 | đường màu và dung sai; lớp có gradient rộng cần lớn, lớp tối dễ lẫn glow cần nhỏ |
| `layers.<l>.alpha` | — | nhận theo độ đục [lo, hi]; dùng cho màn mờ và lớp mờ dần; `measure` ghi `opacity` từng frame |
| `layers.<l>.darker_than_bg` | — | lớp tối trong mờ: phải tối hơn nền ít nhất N mức sáng |
| `layers.<l>.gradient` | (đo) | `{edge, s}`: chỉ giữ khi s ≥ 1,5 × scale px và < 25 px |
| `groups` | tất cả 0 | tách nhóm chỉ khi giữa hai lớp có nét tối thật (đo màu khe trước) |
| `halo_model` | distance | `blur`: glow = làm nhoè hình × `gain[frame]`; nên dùng cho mọi hiệu ứng có pha tàn |
| `near_halo` | true | `measure` tự tắt khi thành phần gần < 1,5 px gốc |
| `fit.underlay_px` | 10 | lớp dưới chạy dưới lớp trên bao xa |
| `fit.min_gain` | 0,0008 | mảnh phải tăng IoU bao nhiêu mới giữ |
| `fit.edge_bias` | [0, 0] | lệch mép dải theo mẫu; `swirl-slash` dùng [0,5, 1,5] |
| `smooth.sigma` | 4,5 (mịn tối đa 7) | độ trơn |
| `smooth.corner_deg` | 145 (142) | góc trong nhỏ hơn mới giữ là góc; thấp quá thì mũi nhọn tròn đi (130 làm tròn lông vũ) |
| `smooth.merge_tol` | 0,9 (1,5) | sai số gộp đoạn |
| `smooth.close_px`, `min_area` | 1,5 / 8 | khe được nối, vụn bị bỏ (frame tan vỡ cần nhỏ) |

## 8. Cách designer vẽ một hiệu ứng (rút ra từ 5 hiệu ứng)

Số đo: `lifecycle` trên `swirl-slash` và `element-trio` (diện tích tính ở px của bản gốc, 25 fps).

| | xoáy lửa | xoáy băng | lửa | Arcane | Toxic |
|---|---|---|---|---|---|
| Bùng tới đỉnh | 2 frame | 1 | 3 | 4 | 1 |
| Đỉnh → bắt đầu vỡ | 1 | 1 | 3 | 0 | 0 |
| Toàn bộ đời (tới < 2% diện tích đỉnh) | 7 | 6 | 21 | 12 | 9 |
| Diện tích còn lại mỗi frame sau đỉnh | 0,50 | 0,36 | 0,81 | 0,55 | 0,55 |
| Số mảnh nhiều nhất | 10 | 5 | 36 | 76 | 23 |
| Bắt đầu giữ frame ("on twos") | frame 10 | — | 14 | 8 | 10 |

1. **Một khung chuyển động, một hình chính.** Mọi hình đặt trong một khung: xoay quanh một tâm (xoáy) hoặc dọc một trục (phun lên). Hình
   chính ra đời nhỏ (lửa: 357 px ở frame 0), **bùng rất nhanh** tới đỉnh trong 1-4 frame (lửa ×22 diện tích sau 2 frame; toxic ×10 trong 1 frame).
   Hình bung tới đúng **khung kích thước** của hiệu ứng (lửa cao ~190 px) rồi giữ khung đó.
2. **Giữ đỉnh rất ngắn** (0-3 frame), rồi **vỡ chứ không thu nhỏ đều**: chiều cao bao ngoài gần như giữ nguyên (lửa 190 px từ frame 9 tới 16) trong
   khi diện tích giảm đều (≈ ×0,8 mỗi frame với lửa, ×0,35-0,55 với xoáy và Arcane). Hình chính tách thành nhiều mảnh (1 → 30-76 mảnh), từng mảnh
   mỏng dần và nhỏ dần **tại chỗ** (mép bị ăn vào, lỗ mở rộng), mảnh lớn nhất co nhanh hơn tổng.
3. **Cuối cùng khung mới sụp**: ở vài frame cuối, các mảnh còn lại co về chân / về điểm gốc (chiều cao lửa 190 → 97 px), chỉ còn đốm.
   Phần nóng (lõi vàng của lửa) ở lại lâu nhất ở chân hiệu ứng; tàn bay lên.
4. **Lớp nóng / sáng tan trước** (xoáy: vàng hết trước hồng, hồng trước đỏ sẫm); **độ đục giảm ở giai đoạn tàn** (Arcane: 1 → 0,59); **glow tắt
   trước hình** (lửa: glow 0 từ frame 19, đốm còn tới 22).
5. **Vẽ "on ones" khi bùng, "on twos" khi tàn**: từ khoảng 60-70% đời hiệu ứng (phần sau của pha tàn), mỗi hình vẽ được giữ 2 frame
   (12,5 hình/giây). Pha va chạm
   cần mượt, pha tan cho phép giật nhẹ và tiết kiệm số hình vẽ.
6. **Mỗi hình là vài đường cong dài** (~26 px viền / điểm neo, tay nắm ≈ 1/3 dây cung), mũi nhọn ở lớp nguội; chi tiết liền nhau chênh 2-5 lần;
   các lớp tô chồng; glow là bản làm nhoè của hình, màu chính của hiệu ứng.

## 9. Lộ trình: từ dựng lại tới sinh hiệu ứng mới

| Bước | Nội dung | Cần gì |
|---|---|---|
| G1. Theo dõi từng hình | ghép mảnh giữa các frame (trùng vùng + khoảng cách tham số nét), đo quỹ đạo từng hình: sinh từ đâu, lớn bao nhanh, vỡ ra mấy mảnh, mảnh co theo luật nào | dữ liệu đã có (5 hiệu ứng) |
| G2. Bộ sinh "phun từ đất" | khung thẳng + hình chính theo đường cong vòng đời mục 8 + vỡ mảnh + glow/độ đục theo thời gian, tham số có seed, xuất qua `smooth_simplify` + `compose` | G1; 3 mẫu đã có |
| G3. Bộ sinh "xoáy chém" | như G2 với khung cực | G1; 2 mẫu đã có |
| G4. Kiểm chứng | sinh hiệu ứng mới, đặt cạnh bản gốc cùng dạng, user chấm | — |
| G5. Mở rộng dạng | va chạm / nổ tròn, đạn bay, aura lặp, buff | **bản gốc mới cho mỗi dạng** (2-3 GIF mỗi dạng) |
| E. Xuất lib-fx | `sheet.png`, `frames/`, `meta.json`, @2x, nền trong suốt | — |

## 10. Nhật ký test

**swirl-slash** (2026-11-07/08): Bài học chính: đo đúng bản gốc (gradient mép, tô chồng) quan trọng hơn công thức;
làm đều nét kiểu Illustrator xoá điểm gãy; khe 2 px giữa hai lớp là khử răng cưa, không phải nét tối.

**element-trio** (2026-11-08):
- Bộ tool chạy được, chỉ cần thêm: `source.scale`, khung thẳng theo biến thể, `darker_than_bg`, khớp nét tính điểm tăng dần (frame vỡ vụn từ
  > 10 phút còn ~1 phút), gom cụm màu.
- Vòng 1 (user: lửa/Arcane ~9, toxic 8): glow cố định theo khoảng cách làm đốm tàn sáng gấp 5-8 lần bản gốc → glow = làm nhoè hình ×
  `gain[frame]`; mảnh Arcane mờ dần bị rơi khỏi mặt nạ → lớp theo độ đục + `opacity[frame]`, tách màn cánh trong mờ; viền xanh đậm của toxic
  là vệt phóng to 3x bị đo thành gradient → luật 1,5 px gốc cho gradient và glow.
- Vòng 2: user chấm cả ba 10/10.
