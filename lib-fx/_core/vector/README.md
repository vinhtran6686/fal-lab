# lib-fx/_core/vector: bộ dựng VFX vẽ tay bằng path vector

Bộ tool chung để **đọc một hiệu ứng tham khảo** (GIF/frame) và **dựng lại nó bằng path Bézier sạch** (lớp màu phẳng, gradient mép,
quầng sáng), hoặc để **vẽ hình mới** bằng cùng một "đơn vị hình". Đóng gói từ nghiên cứu xoáy chém
([research/bezier-shapes/](../../research/bezier-shapes/RETROSPECTIVE.md), user chấm 9-10/10). Tên module chỉ phương pháp, không gắn với
hiệu ứng nào: mọi thứ riêng của một hiệu ứng nằm trong **một file profile JSON** (`profiles/<tên>.json`).

0 USD, không gọi model. Python: numpy, scipy, Pillow, opencv-python-headless, scikit-image (`pip install scikit-image opencv-python-headless`).

## 1. Lệnh

```
python lib-fx/_tools/vectorfx.py palette  PROFILE [--variant V] [--frame N]   ứng viên màu phẳng + ảnh mặt nạ từng màu
python lib-fx/_tools/vectorfx.py ingest   PROFILE                             cắt source.gif thành frame theo source.crops
python lib-fx/_tools/vectorfx.py measure  PROFILE [--frames 3-5]              đo gradient mép từng lớp + quầng sáng, ghi vào PROFILE
python lib-fx/_tools/vectorfx.py rebuild  PROFILE [--frames 2-12] [--variants a,b] [--refit]
python lib-fx/_tools/vectorfx.py review   PROFILE                             ảnh từng lớp, GIF, review/index.html
python lib-fx/_tools/vectorfx.py all      PROFILE                             rebuild + review
```

`PROFILE` là đường dẫn, hoặc tên trong `profiles/` (vd. `swirl-slash`). Kết quả ở `lib-fx/_study/<tên>/vector/` (không vào git):
`strokes/` (nét đã khớp, bước chậm, dùng lại trừ khi `--refit`), `frames/` (ảnh hoàn chỉnh), `flat/` (màu phẳng), `svg/` (mỗi lớp một
`<path id="lớp">`), `report.json`, `review/index.html` (publish bằng Artifact tool cùng thư mục `img/`).

Dùng trong code:
```python
import sys; sys.path.insert(0, "lib-fx/_core")
from vector import Profile, pipeline, review, smooth_simplify, crescent, tongue, feather, PolarFrame
```

## 2. Quy trình cho một hiệu ứng tham khảo mới (vd. GIF user gửi)

1. **Dữ liệu**: đặt GIF vào `ref/vfx/<tên>/reference.gif`; nếu có nhiều biến thể cạnh nhau, ghi khung cắt từng biến thể.
2. **Profile**: chép `profiles/swirl-slash.json` thành `profiles/<tên>.json`, sửa `name`, `source` (`gif`, `crops`, `frames_dir`, `frames`,
   `background_frame` = một frame không còn hiệu ứng nếu có), `frame.type` (`polar` cho xoáy/vòng/sóng tròn, `linear` cho đâm/tia/chém thẳng).
3. `ingest` → frame PNG.
4. `palette` trên một frame giữa → danh sách màu kèm `interior`/`compact`/`likely` và ảnh mặt nạ từng màu. **Nhìn ảnh** rồi chọn màu phẳng
   của từng lớp (GIF lượng tử hoá cả quầng sáng thành màu đúng mã, chỉ số chỉ là gợi ý).
5. Viết `variants.<v>.layers`: mỗi lớp `colours` = [màu phẳng] (thêm màu mép nếu thấy lớp ngả màu ở mép), `tol` (12-26), và `order`
   (tô từ dưới lên: lớp có mũi nhọn đâm vào lớp khác nằm **trên**).
6. `measure` → đo `gradient` (màu mép, độ dài s) cho từng lớp và `halo` cho từng biến thể, ghi thẳng vào profile. Đọc `rms` / `rms_flat`:
   gradient chỉ có nghĩa khi rms giảm rõ; s ≥ 25 px là lớp phẳng (xoá `gradient`). Quầng: thành phần có s < 1,5 px là khử răng cưa → đặt
   `near_halo: false`.
7. `all` → mở `review/index.html` (publish lên artifact), xem GIF và từng lớp từng frame, chấm OK / Needs work, chỉnh profile, chạy lại
   (`rebuild` không `--refit` chỉ làm lại bước làm mịn + tô, vài phút).

## 3. Kiến trúc

```
reference frames ─► measure.layer_masks (đường màu: màu phẳng + gradient mép)  ─► full_targets (lấp khe khử răng cưa)
                                                                                     │
frames.make_frame (polar | linear) ◄─────────────────────────────────────────────────┤
                                                                                     ▼
fit.fit_layer: dải → nét thon (thân bền vững + lưỡi cộng + vết khoét)  ◄── compose.underlay_target (lớp dưới chạy dưới lớp trên)
        │
        ▼
smooth.smooth_simplify (nối khe → góc thật hai tầm → làm trơn D²/D³ → fit G1 → nắn gãy → gộp đoạn → tay nắm ≤ 0,45)
        │
        ▼
compose.composite (gradient trong theo mép phần nhìn thấy, quầng theo khoảng cách) → PNG + SVG → metrics → review
```

| File | Vai trò |
|---|---|
| `profile.py` | đọc/ghi profile, giá trị mặc định, mô tả đủ các khoá |
| `measure.py` | frame, nền, ứng viên màu, mặt nạ theo đường màu, lấp khe, đo gradient mép và quầng, `ingest` |
| `frames.py` | khung toạ độ của hiệu ứng (`PolarFrame`, `LinearFrame`), tách mặt nạ thành dải |
| `strokes.py` | **đơn vị hình**: nét thon (xương sống Bernstein + bề rộng `W·(t+e0)^a·(1−t+e1)^b`), xuất path; preset `crescent`, `tongue`, `feather`, `notch` |
| `fit.py` | đo tham số nét từ dải; `fit_layer` (thân + lưỡi + vết khoét) |
| `smooth.py` | `smooth_simplify`: làm đều nét kiểu Illustrator Simplify / Potrace / fair curve |
| `compose.py` | lớp dưới chạy dưới lớp trên, gradient trong, quầng, ảnh, SVG |
| `metrics.py` | IoU; độ mượt path: `kinks` (neo gãy 5-35°, phải = 0), `wobble` (điểm uốn / 100 px), `curv_var` (độ biến thiên độ cong / 100 px) |
| `pipeline.py` | `rebuild` từng frame, cache nét, báo cáo |
| `review.py`, `review_page.html` | ảnh từng lớp, GIF gốc / dựng lại, trang review có nút chấm và sao chép nhận xét |
| `bezier.py` | Bézier: Schneider fit, góc, viền, raster, SVG, đọc lại path |

## 4. Tham số và ý nghĩa (mặc định = giá trị đã kiểm chứng trên xoáy chém)

| Khoá | Mặc định | Ý nghĩa / khi nào chỉnh |
|---|---|---|
| `layers.<l>.tol` | 12-26 | dung sai quanh đường màu; lớp có gradient rộng cần lớn (vàng 26), lớp tối dễ lẫn quầng cần nhỏ (đỏ sẫm 12) |
| `groups` | tất cả 0 | chỉ tách nhóm khi giữa hai lớp có **nét tối thật** (đo màu dải giữa hai lớp trước; khe 1-3 px gần như luôn là khử răng cưa) |
| `fit.underlay_px` | 10 | lớp dưới chạy dưới lớp trên bao xa |
| `fit.min_gain` | 0,0008 | một lưỡi / vết khoét phải tăng IoU ít nhất bao nhiêu mới được giữ (lớn → ít mảnh, gọn hơn) |
| `smooth.sigma` | 4,5 (băng 7) | độ mạnh làm trơn (px); tăng khi nét còn lượn / nứt nẻ |
| `smooth.corner_deg` | 145 (băng 142) | góc trong nhỏ hơn mới giữ là góc; giảm → ít góc hơn, mượt hơn nhưng mũi nhọn tròn đi (130 làm tròn mũi lông vũ) |
| `smooth.merge_tol` | 0,9 (băng 1,5) | gộp hai đoạn khi sai số ≤ giá trị này; lớn → ít neo, đường dài hơn |
| `smooth.close_px` | 1,5 (băng 2,5) | khe trong cùng lớp được nối |
| `smooth.min_area` | 8 (băng 40) | vụn nhỏ hơn bị bỏ (frame tan vỡ cần nhỏ) |
| `variants.<v>.near_halo` | true | false khi thành phần quầng gần có s < 1,5 px (`measure` tự đặt) |
| `layers.<l>.darker_than_bg` | (không có) | lớp tối trong mờ (bóng khói): chỉ nhận điểm ảnh tối hơn nền tham khảo ít nhất N mức sáng, nên nền và bục không bị nhận nhầm |
| `source.scale` | 1 | `ingest` phóng to frame (GIF nhỏ: 3) để các tham số tính bằng px giữ nguyên ý nghĩa |
| `variants.<v>.frame` | theo `frame` chung | khung toạ độ riêng cho một biến thể (vd. một hiệu ứng xoáy, một hiệu ứng phun thẳng) |

## 5. Luật đã kiểm chứng (tóm tắt; chi tiết `lib-fx/SHAPE-RULES.md` §7, §7b, §7c)

1. **Đo trước, dựng sau**; chuyển mọi nhận xét bằng lời thành một phép đo ("nứt nẻ" → đo màu dải giữa hai lớp; "gấp khúc" → đếm `kinks`).
2. Lớp = màu phẳng **+ gradient mép của nó**; một màu mỏng bao quanh lớp khác thường chỉ là gradient mép (hổ phách của lửa).
3. **Tô chồng**: lớp dưới liền khối, chạy dưới lớp trên; lớp có mũi nhọn đâm sang lớp khác nằm trên.
4. Đường của designer: ~26 px viền / neo, tay nắm ≈ 1/3 dây cung, mũi nhọn ở lớp nguội, chi tiết liền nhau chênh 2-5 lần, khoảng cách không đều.
5. Mọi viền xuất ra đi qua `smooth_simplify`; mục tiêu `kinks = 0`, `curv_var` ≈ đường vẽ tay (0,3-1 / 100 px).
6. Quầng sáng = màu chính × exp(−d/s), s 27-38 px; gradient trong 1,5-8 px.
7. IoU không phải mục tiêu duy nhất: mảnh vụn tăng IoU nhưng làm hình "rác".

## 6. Phần còn thiếu để thành tool animation (thiết kế đã chốt, làm sau khi test GIF thứ hai)

| Hạng mục | Vấn đề hiện tại | Thiết kế |
|---|---|---|
| **A. Ổn định giữa các frame** | mỗi frame khớp độc lập → nét đổi số lượng, có thể rung | (1) ghép nét giữa frame k và k+1 theo trùng lặp vùng + khoảng cách tham số (Hungarian); (2) gán ID nét xuyên suốt; (3) làm trơn theo thời gian từng tham số (xương sống, W, a, b) bằng spline, giữ khoá ở frame chính; (4) nét sinh/chết chỉ ở frame có sự kiện (đầu nét đi qua, vỡ). Thước đo: dịch chuyển viền trung bình giữa hai frame so với bản gốc. |
| **B. Sinh hình mới từ luật** | `research/.../generate.py` là bản thử | style profile = phân phối tham số đo được (dài/rộng, a/b, nhịp to-nhỏ 2-5, CV khoảng cách ≥ 0,5, góc nhọn theo lớp) + hàm sinh có seed; bố cục: thân → lưỡi theo nhịp → vết khoét → tô chồng → `smooth_simplify`. |
| **C. Lớp trong mờ phía sau** | đã có bước đầu: `darker_than_bg` (dùng cho bóng khói của element-trio/toxic) | còn thiếu: lớp sáng trong mờ (alpha < 1 trên nền) và alpha đo được thay vì màu phẳng. |
| **D. Mũi rất mảnh / móc tự do** | mũi 3-6 px và móc dưới đáy lưỡi trắng chưa nhọn bằng gốc | nét có xương sống Bézier tự do (không bám khung cực/thẳng), fit từ đường giữa (skeleton) của mảnh. |
| **E. Xuất cho game / lib-fx** | hiện xuất PNG/SVG từng frame | xuất `sheet.png`, `frames/`, `meta.json` đúng chuẩn lib-fx (`build.py`), @2x, nền trong suốt, điểm neo. |

Hiệu ứng đã có profile: `swirl-slash` (xoáy, khung cực), `element-trio` (3 hiệu ứng phun từ đất: lửa, pha lê, độc; khung thẳng đứng,
GIF nhỏ phóng 3x). Thời gian: khớp nét ~1,5 phút / frame / biến thể ở ảnh 700-840 px (cache trong `strokes/`); chạy các biến thể song
song bằng nhiều lệnh `rebuild --variants`.

Đề xuất thứ tự: test bộ này với một GIF khác dạng (nổ, đâm thẳng, vòng sóng) → sửa chỗ yếu → A → E → B → C, D.

## 7. Nhật ký test

### element-trio (2026-11-08, GIF thứ hai, 3 hiệu ứng phun từ đất)

Trang review: Element Trio, https://claude.ai/artifact/6Vw3supbrvPSULNoNsxCzn. Profile: `profiles/element-trio.json`.

- **Chạy được với bộ tool, chỉ phải thêm 4 thứ** (đều đã vào code):
  - `source.scale`: GIF nhỏ (787x443, mỗi hiệu ứng cao ~150 px) được phóng 3x khi `ingest`.
  - Khung thẳng đứng (`frame: linear, angle -90`) cho hiệu ứng phun lên.
  - `darker_than_bg` cho khối bóng tối của hiệu ứng độc (trùng màu với nền và bục nếu chỉ so màu).
  - Khớp nét tính điểm từng mảnh tăng dần (frame vỡ vụn từ > 10 phút còn khoảng 1 phút).
- Kết quả frame 3-8 (IoU phần nhìn thấy so với mặt nạ, 0 điểm gãy ở mọi lớp mọi frame):
  - lửa: cam 0,80-0,91, vàng 0,87-0,92;
  - pha lê: tím nhạt 0,83-0,91, xanh 0,79-0,91;
  - độc: bạc hà 0,89-0,93, bóng tối 0,82-0,94.
- **Khác với xoáy chém**: màu không phẳng tuyệt đối (GIF nhỏ, dither, lửa chuyển vàng → cam theo chiều cao), nên `palette` (đếm màu đúng mã)
  không đánh dấu được màu nào; phải gom cụm màu (k-means) rồi xem bản đồ từng cụm bằng mắt. Nên thêm k-means vào lệnh `palette`.
- **Còn thiếu so với bản gốc**: các cánh xanh trong mờ của pha lê (lớp sáng trong mờ, hạng mục C), vòng sáng của pha lê bị gộp vào lớp xanh
  (cùng màu), lỗ trong lửa ở bản gốc được quầng sáng phủ (bản dựng thấy nền tối hơn), vòng elip mảnh dưới chân lửa.

### element-trio, vòng sửa 1 (2026-11-08): thời gian của gradient, glow và độ đục

User chấm lửa và pha lê ~9/10 ("frame cuối gradient/glow vẫn nhiều làm các đốm sáng lên"), toxic 8/10 ("viền xanh đậm quanh hình bạc hà").
Đo lại theo từng frame, cả hai nhận xét đều đúng:

1. **Glow tắt dần theo thời gian.** Quầng theo khoảng cách (cố định) phải nhân hệ số ~1,6 ở đỉnh nhưng ~0,15-0,2 ở frame cuối mới khớp
   gốc: bản dựng sáng gấp 5-8 lần ở frame tàn. Mô hình mới `halo_model: "blur"`: glow = bản làm nhoè của chính hình (2 gauss, màu đo được)
   × `gain[frame]` đo từng frame. Đốm nhỏ tự có quầng nhỏ, lỗ trong lửa được quầng phủ như gốc. Lửa: gain ≈ 1 tới frame 12, 0,5 ở 15-16,
   0,18 ở 17-18, 0 từ 19.
2. **Hình cũng mờ dần.** Lớp có `"alpha": [lo, hi]` được nhận theo độ đục so với nền và tô với `opacity[frame]` đo được. Pha lê: tím nhạt
   1,0 tới frame 8 rồi 0,89 → 0,75 → 0,64 → 0,59; các cánh xanh là **hai lớp**: cánh đặc (0,95-1) và màn trong mờ (0,41-0,48), đúng phần
   "cánh xanh trong mờ" trước đây bị thiếu. Mặt nạ theo màu phẳng đã làm rơi các mảnh vỡ mờ ở frame cuối.
3. **Viền đậm ở toxic là lỗi đo.** Ở độ phân giải gốc, màu bạc hà phẳng sát mép (chỉ 1 px khử răng cưa); "gradient mép" s 2,6 px đo trên
   ảnh đã phóng 3x chỉ là vệt nhoè của phép phóng to. Luật mới trong `measure`: gradient và quầng gần chỉ được nhận khi rộng hơn
   1,5 × `source.scale` px.

Luật rút ra (dùng cho mọi hiệu ứng có giai đoạn tan):
- Đo **theo từng frame**, không chỉ ở frame đỉnh: glow, độ đục và gradient đều có đường cong thời gian riêng.
- Glow là bản làm nhoè của hình, không phải viền theo khoảng cách; độ mạnh của nó là một đường cong (giữ ở đỉnh, tắt trước khi hình tan hết).
- Một lớp có thể có nhiều mức độ đục cố định (đặc / màn mờ): tách thành nhiều lớp cùng màu, khác dải alpha.
- Đừng đo gradient trên ảnh đã phóng to mà không quy về px gốc.
