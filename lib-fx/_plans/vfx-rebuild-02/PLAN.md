# Tái tạo hai mẫu mới (flame-burst, lightning) để rút luật cho VFX về sau

Nguồn: yêu cầu của người dùng 2026-11-13. Mẫu: `ref/vfx/flame-burst/dmitry-sarkisov-flame-burst.gif` (800x550, 81 khung, 25 fps),
`ref/vfx/lightning/dmitry-sarkisov-lqafinal.gif` (400x400, 127 khung, 25 fps).
Vai trò: người lập kế hoạch chỉ viết task và **chấm kết quả**; người thi công làm đúng từng bước, không tự đổi phương pháp; người dùng duyệt cuối; docs chỉ viết sau khi duyệt.
Thư mục này xoá khi xong (như kế hoạch `fxkit-feedback-01` trước đó, đã xoá).

**Mục tiêu thật**: hiểu **cách làm** một hiệu ứng tốt (quy trình và các quyết định), để sáng tạo độc lập, không phải học thuộc lửa hay sét.
Phương pháp tổng quát (bản nháp, có nguồn): [METHOD.md](METHOD.md). Hai mẫu dưới đây là bài kiểm tra cho phương pháp đó.

## 1. Vì sao tái tạo trước, viết luật sau
Tìm trên web không ra luật có số (sách Elemental Magic của Gilland và các khoá học chỉ nêu nguyên tắc chung: hình, năng lượng, nhịp). Nguồn đáng tin
nhất là **đo chính mẫu của hoạ sĩ**, như repo đã làm với `swirl-slash`, `element-trio` (9-10/10). Tái tạo đạt = bộ đo và bộ dựng đúng → số đo dùng được làm luật.

## 2. Đã thấy gì trong hai mẫu (xem bằng mắt, cần số đo xác nhận)
**flame-burst** (lửa phụt ngang từ một hộp, sang phải):
- khung ~7-22: **báo trước**: một nhúm lửa nhỏ và vài sợi khói ở miệng hộp rồi tắt;
- khung ~29-36: **bùng**: dải lửa dài hình chữ S, ba tông (vàng lõi, cam, **vỏ khói nâu đen bọc ngoài**), đầu mút cuộn tròn;
- khung ~44: lửa **rút về nguồn**, khói tách ra thành khối riêng trôi lên phải;
- khung ~51-73: chỉ còn khói, rách thành mảnh cong có móc; khung 80 trống.
**lightning** (nhiều tia chớp ngắn nối tiếp ở các vị trí khác nhau):
- mỗi tia sống vài khung: nét gãy khúc mảnh, một thân chính dày + nhánh mảnh + mảnh rời; lõi trắng xanh, quầng nhoè rộng;
- có khung quầng đổi màu (xanh lam) = khung chớp.

## 3. Giả thuyết cần số đo xác nhận (thành luật nếu đúng)
| # | Giả thuyết | Đo bằng |
|---|---|---|
| H1 | Có pha báo trước nhỏ (< 10 % diện tích đỉnh) trước cú bùng, cách nhau một khoảng lặng | `lifecycle` flame: diện tích theo khung |
| H2 | Khói là lớp ngoài cùng, sinh cùng lúc với lửa và sống lâu hơn lửa ≥ 2 lần | `lifecycle` từng lớp |
| H3 | Lửa tàn bằng cách rút về nguồn (tâm khối lùi về miệng hộp), khói thì trôi đi (tâm đi lên, ra xa) | `track`: dịch chuyển tâm từng lớp |
| H4 | Đầu mút của lửa và khói là móc cuộn (cung > 180°), không phải mũi thẳng | `study` + xem path |
| H5 | Tia sét: 1 thân chính + 2-4 nhánh; nhánh mảnh bằng 30-50 % thân; đoạn gãy dài không đều (tỉ lệ 2-5 lần) | đo trên path của lightning |
| H6 | Mỗi tia sét sống 2-5 khung, khung đầu sáng nhất, không có pha lớn dần | `lifecycle` lightning theo từng tia |
| H7 | Quầng của sét rộng hơn nhiều so với nét (bán kính nhoè ≥ 10 lần bề rộng nét) | `measure` halo |
| H8 | Các tia nối tiếp không lặp vị trí và hình (không có hai tia chồng nhau > 30 %) | IoU giữa các tia |

## 4. Checklist
- [x] **R1** flame-burst: profile, đo, dựng lại, so sánh: [R1-flame-burst.md](R1-flame-burst.md)
- [ ] **R2** lightning: profile, đo, dựng lại, so sánh: [R2-lightning.md](R2-lightning.md)
- [ ] **CHẤM** (người lập kế hoạch): xem `compare.gif` và số đo của R1, R2; ghi nhận xét vào mục 6. Chưa đạt → trả về đúng task đó
- [ ] **R3** xuất số đo cho luật (chỉ làm sau khi R1, R2 được chấm đạt): [R3-export-measurements.md](R3-export-measurements.md)
- [ ] **DUYỆT** (người dùng) → người lập kế hoạch viết docs **phương pháp chung** (chuyển phần đã được xác nhận của `METHOD.md` vào `rules/`: quy trình 9 bước, bảng thiết kế,
      duyệt theo tầng, phép đo mới) trước, rồi mới tới ghi chú riêng từng chất liệu và task dựng lớp fxkit tương ứng

R1 và R2 chạy song song được (khác file). Không ai sửa `fxkit/` trong kế hoạch này.

## 5. Luật chung cho người thi công
1. Đọc `lib-fx/_core/formulas/vector/README.md` mục 4-5 và `lib-fx/_core/formulas/rules/03-reading-references.md` trước.
2. Chỉ dùng bộ `vectorfx.py`. Không viết bộ dựng mới, không sửa `lib-fx/_core/formulas/vector/*.py` trừ khi task ghi rõ.
3. Kết quả trung gian ở `lib-fx/_study/` (git bỏ qua). Thứ vào git: profile JSON, showcase, số đo (R3).
4. Mỗi bước có "kiểm": không đạt thì làm lại bước đó, không đi tiếp.
5. Không công cụ tốn tiền, không đọc `.env`, không ghi tên game hay tên tác giả vào code / profile (tên file GIF gốc giữ nguyên).
6. Xong: đánh dấu ô ở mục 4, điền "Kết quả" trong file task (đường dẫn `compare.gif`, bảng IoU, thời gian chạy, chỗ chưa giống), commit + push lên `ccr-38411bc5-l13uki`.

## 6. Nhận xét khi chấm (người lập kế hoạch điền)
