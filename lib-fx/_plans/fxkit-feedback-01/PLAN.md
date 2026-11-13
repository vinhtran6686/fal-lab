# fxkit, vòng góp ý 01: kế hoạch sửa

Nguồn: góp ý của người dùng ngày 2026-11-13 sau khi xem trang duyệt (https://claude.ai/artifact/6NN5cynqUge1CqM7tfUfoR).
Thư mục này là kế hoạch đang chạy, **xoá khi mọi task đã xong và được duyệt** (repo không giữ kế hoạch đã xong, `docs/repo-structure-rules.md` §4.5).
Người viết kế hoạch không thi công. Mỗi task do một AI khác làm theo file task, làm xong thì đánh dấu ô ở đây và điền mục "Kết quả" cuối file task.

## 1. Góp ý và đánh giá

| # | Người dùng nói | Đánh giá | Nguyên nhân trong code | Task |
|---|---|---|---|---|
| A | Đẹp, giữ: nện bụi, nổ sao, `impact/spark`, `impact/quake`, `ranged/bolt` (rất tốt) | Đồng ý. Không task nào được làm các hiệu ứng này xấu đi | - | (ràng buộc chung) |
| B | `impact/spark`: trúng đòn nặng và chí mạng chưa khác nhau rõ | Đồng ý. `crit` chỉ là `heavy` phóng to: cùng hình, cùng nhịp, khác bảng màu và vài con số | `lib-fx/impact/spark/spark.py`: `crit = _heavy.variant(...)` chỉ đổi `n`, `length`, `r`, `arc` | T5 |
| C | Vệt chém trên `azure_blade`: màu đẹp hơn nhưng quỹ đạo méo | Đồng ý. Vệt đi theo một parabol giữa hai mũi đao, không theo đường mũi đao thật quét; bề rộng là hằng số chứ không phải chiều dài lưỡi | kind `slash` chỉ biết `c.sp.path(f, bend)` (Bezier bậc hai a → b). Cú chém thật: chuôi đi một đường, lưỡi xoay quanh chuôi, mũi vẽ một cung khác hẳn (xem `sweep_samples` trong `out/heroes/azure_blade/source/vfx/crescent/build_crescent.py`) | T4 |
| D | `impact/quake/slam`: bụi nằm trên mặt phẳng (đúng) nhưng phần nổ tròn, chưa đúng phối cảnh; nên bóp thành ellipse dẹp | Đồng ý. Vòng đã dẹp (`squash=0.3`) nhưng chớp `star`, quầng sáng và quỹ đạo `scraps` vẽ trong mặt phẳng màn hình | `star`, `scraps` không có khái niệm mặt đất; glow là bản nhoè tròn của chúng | T2 |
| E | `melee/slash`: không đọc ra loại vũ khí. Kiếm, đao: vệt mịn, hướng đều, không để lại "hoa văn". Rìu: các vết song song | Đồng ý, đây là lỗi thiết kế của tôi. Pha tàn dùng mòn nhiễu từ trong ra (`hollow=True`) nên để lại hoa văn ngoằn ngoèo; răng cưa (`teeth`) bật mặc định cho mọi vũ khí | `fxkit/layers/slash.py` dòng tàn: `erode(..., holes=0.38, hollow=True)`; `teeth=4` mặc định | T3 |
| F | `element/fire/aoe`: lớp, màu, diễn đạt đúng; nhưng nét của từng lớp cần nối mịn như Smooth Tool của Illustrator | Đồng ý. Hình là hợp của nhiều lưỡi nên có góc lõm gãy ở chỗ giao; mép sau khi mòn lổm chổm. Luật `rules/01-design-style.md` §2 đã yêu cầu nhưng `Ink` chưa làm | `fxkit/ink.py`: `Ink.paint` tô thẳng mặt nạ, không có bước làm mịn. Bộ làm mịn đã có sẵn ở `lib-fx/_core/formulas/vector/smooth.py` (`smooth_simplify`) nhưng fxkit chưa dùng | T1 |

Không đồng ý điểm nào: không có.

## 2. Thứ tự và phụ thuộc

```
T1 (làm mịn nét, lõi)  ──┬─> T2 (mặt phẳng đất)
                         ├─> T3 (vệt chém theo vũ khí) ──> T4 (quỹ đạo theo vũ khí thật)
                         └─> T5 (thang nhẹ / nặng / chí mạng)
                                                   tất cả ──> T6 (dựng lại, trang duyệt, tài liệu)
```
T1 làm trước và một mình (đổi lõi tô, mọi hiệu ứng đổi khung). T2, T3, T5 chạy song song được sau T1 (khác file). T4 sau T3 (cùng file `slash.py`). T6 cuối.

## 3. Checklist

- [x] **T1** Làm mịn nét trong `Ink` (kiểu Smooth Tool): [T1-smooth-outlines.md](T1-smooth-outlines.md)
- [ ] **T2** Hiệu ứng mặt đất nằm trên mặt phẳng đất: [T2-ground-plane.md](T2-ground-plane.md)
- [ ] **T3** Vệt chém đọc ra loại vũ khí (kiếm mịn, rìu song song): [T3-slash-weapon-profiles.md](T3-slash-weapon-profiles.md)
- [ ] **T4** Vệt chém theo quỹ đạo vũ khí thật (chuôi + mũi): [T4-slash-weapon-track.md](T4-slash-weapon-track.md)
- [ ] **T5** Thang trúng đòn nhẹ / nặng / chí mạng khác nhau rõ: [T5-spark-ladder.md](T5-spark-ladder.md)
- [ ] **T6** Dựng lại, cập nhật trang duyệt và tài liệu, xoá thư mục kế hoạch: [T6-rebuild-review-docs.md](T6-rebuild-review-docs.md)

## 4. Luật chung cho mọi task (đọc trước khi làm)

1. Đọc `CLAUDE.md`, `lib-fx/_core/formulas/draw/FXKIT.md` (hợp đồng của một kind, mục 4), `lib-fx/_core/formulas/rules/01-design-style.md`, `02-animation.md`.
2. Chỉ sửa các file ghi trong mục "File được sửa" của task. Không đụng `out/` (asset đã duyệt), không đụng các họ cũ khai báo `VARIANTS`.
3. Không ghi số RGB trong kind; ngẫu nhiên chỉ qua `c.rng(...)`; hình chỉ từ `fxkit.shapes`; tô chỉ qua `Ink`.
4. Mỗi lần đổi, **mở ảnh ra xem** (`python lib-fx/_tools/fxkit_sheet.py <kind|hiệu ứng> ...` ghi `lib-fx/_gallery/kinds/<tên>.png`), so với ảnh "trước" đã chụp ở bước đầu của task. Tối thiểu 3 vòng xem và sửa.
5. Xong task phải chạy sạch: `python lib-fx/build.py <các họ bị ảnh hưởng> --check` (không FAIL) và `python lib-fx/_tools/fxkit_test.py` (all checks passed).
6. Các hiệu ứng người dùng đã khen (mục 1, dòng A) không được xấu đi: chụp trước / sau và ghi vào mục "Kết quả".
7. Không commit thay đổi dở dang lên nhánh khác; làm trên `ccr-38411bc5-l13uki`, commit theo từng task, thông điệp mô tả hành vi (không ghi mã task).
8. Không chạy công cụ tốn tiền (`scripts/gen_image.py`, `scripts/fal_video.py`), không đọc `.env`.
9. Duyệt ở cỡ game: xem `preview_game.gif` của hiệu ứng, không chỉ @2x.
