# Gửi chuyên gia: kết quả Milestone 01

(Copy phần dưới đường kẻ gửi cho chuyên gia. Ảnh kèm: `out/heroes/holy_commander/frames/fx/slash_diag/preview_with_body.gif` (@1x),
`preview_with_body_3x.gif`, `source/vfx/slash_diag/review/gate3_contact_sheet.png`, `review/gate3_tip_trajectory.png`, `review/gate4b/variants_sheet.png`.)

---

Chào anh/chị,

Em báo kết quả Milestone 01 (Character-Synchronized Slash, Holy Commander). **Milestone đạt cả 6 tiêu chí**. Chủ dự án đã chấm tiêu chí 5 bằng mắt
ở cỡ game. Sản phẩm: một nhát chém xéo từ trên xuống, có vệt chém sinh từ quỹ đạo kiếm đánh dấu tay, tách lớp, ghép đúng frame với thân.
Tổng chi API cả ngày khoảng 1 USD; phần lớn tốn vào nhánh thử chém đôi không đạt (mục 4).

## 1. Đã làm theo 6 gate

| Gate | Kết quả |
|---|---|
| 0 Tái sử dụng | Kiểm tra `pose_skill_radiant_slash`, `attack_side`. Chủ dự án quyết tạo pose mới cho đúng đòn |
| 1 Pose | `pose_downcut_p1_v01` (kiếm giơ cao sau đầu), `pose_downcut_p2_v01` (kiếm chĩa xuống phải-dưới). Hai bàn chân căn trùng chỗ. P1 làm 2 lần (lần 1 cả hai tay mọc từ một vai) |
| 2 Video | `h3-max-turbo`, 3 s, ảnh đầu P1 → ảnh cuối P2, prompt tả từng bộ phận theo beat. **1 take đạt.** Model vẫn vẽ vệt cung dù đã cấm; xoá ở bước xử lý sau (`dearc.py` trên clip, `destrand.py` trên frame xuất). Chủ dự án chọn 16/46 frame bằng Frame Editor (1,07 s); frame chạm = hình 13 |
| 3 Quỹ đạo | Trang click tay riêng cho milestone: Root và Tip cho cả 16 hình, đều thấy rõ, đều ở trước thân. Khớp **đường tròn (k = 1, 3 bậc tự do, 6 điểm hình 8-13)**: sai số TB **0,037 H**, lớn nhất **0,078 H**, đạt ngưỡng 0,08 / 0,15. Leave-one-out điểm giữa (chỉ tham khảo): TB 0,091, lớn nhất 0,159 H |
| 4 VFX | Hai phiên bản, chi tiết ở mục 2 |
| 5 Ghép | `frames/fx/slash_diag/`: lớp front RGBA @2x/@1x, `fx.json` (pivot = chân, blend screen), preview, `criteria.json`. **Một lệnh dựng lại:** `python scripts/experiments/milestone_01/build_slash_diag.py` |

Quy ước giữ đúng như anh/chị chốt: H = 55,5 px @1x (111 px @2x), gốc ở chân, y lên, ms, 15 fps, mọi frame 67 ms.

## 2. Điểm lệch so với kế hoạch (xin anh/chị xem)

1. **Điểm bắt đầu VFX.** Quy tắc "20% đỉnh, tối thiểu 0,1 H/hình" áp nguyên văn sẽ bật VFX ở **hình 5**, vì lúc lấy đà mũi kiếm lùi khá nhanh (0,30). Em lấy
   **hình đầu tiên của đoạn nhanh liên tục chứa đỉnh**: hình 9 (536 ms); đỉnh ở hình 11, 0,83 H/hình.
2. **Đổi cách biểu diễn vệt theo yêu cầu chủ dự án.**
   - Bản đầu đúng phương án C: một dải trên cung tròn, đầu dải đặt ở mũi kiếm.
   - Chủ dự án muốn vệt **dày, phủ từ chân lưỡi tới mũi** và **nhiều tầng như showcase**. Bản cuối dùng lại bộ sinh `gen_slash_loop` (kiểu heavy:
     dải chính, dải trong, sợi tối, đầu tách ngón, răng cưa, đường tốc độ, vệt đứt, mảnh vụn), vẽ trong một khung toạ độ mới (chỉ ở thư mục thử nghiệm):
     **`SweepFrame`**, với u = thời gian theo hình và v = dọc lưỡi từ Root tới Tip. Đường gốc và đường mũi là Catmull-Rom đi qua các điểm đã đánh dấu.
   - Lần thử đầu dựng "gốc-mũi" theo bán kính của cung tròn là sai, vì tay cầm không nằm ở tâm cung (đầu vệt lệch 0,16-0,29 H); em đã bỏ.
3. **Tiêu chí 3.**
   - Đầu vệt cách mũi kiếm 0,03-0,06 H (đo trên ảnh đã render). Đạt.
   - Về hướng: ở bản cung tròn, em đo bằng đoạn nối hình trước → hình này thì lệch 13-31°. Với bước nhảy khoảng 50° cung mỗi hình, cách đo này thực chất trễ
     nửa hình. Em chuyển sang **sai phân trung tâm**; em đổi **sau khi** thấy số liệu cách cũ, nên cả hai cột đều ghi trong báo cáo. Theo sai phân trung tâm,
     bản cung tròn lệch **18° ở hình 12** (ngưỡng 15°), dù tip hình 12 nằm đúng trên cung (0,0007 H); độ lệch đến từ hình 11 và 13 kề bên.
   - Ở bản cuối (`SweepFrame`), hướng lệch 0,1-1,7°, nhưng **đạt do cách dựng**: tiếp tuyến Catmull-Rom tại một điểm đánh dấu chính là sai phân trung tâm.
     Thực chất đây là phương án "đường cong tự do" mà anh/chị dành cho trường hợp khớp cung không đạt. Ở đây khớp cung vẫn đạt; em dùng nó vì yêu cầu phủ
     gốc-mũi của chủ dự án.
4. **Tiêu chí 4.** Ba biến thể, mỗi biến thể chỉ đổi một tham số: `width_scale` 1,0 → 0,6, `lag_frames` 2,6 → 1,4, `curvature` 0 → 0,25. Biến thể độ dày
   khác ít hơn, vì các sợi bên trong vẫn chạm phía chân lưỡi.
5. **Tiêu chí 6.** Lần đầu build hai lần ra PNG khác nhau: `gen_slash_loop.drawing` đặt vệt đứt bằng `hash(l)` của Python, giá trị này đổi theo mỗi lần
   chạy. Lệnh build của milestone đã cố định `PYTHONHASHSEED=0`, giờ hai lần ra giống hệt nhau. **Core chưa sửa**; em đề xuất sửa ở core sau.
6. **Tiêu chí 2.** Ở thân hình 11 còn một sợi vệt cung rất mảnh cạnh lưỡi kiếm, chỉ thấy khi phóng to.

## 3. Kết luận về quy trình

Quy trình **chạy được cho skill một động tác**:

ảnh đầu + ảnh cuối căn chung chỗ đặt chân → một clip, prompt tả từng bộ phận theo chuỗi lực → xoá vệt model tự vẽ → chủ dự án chọn frame →
đánh dấu tay Root/Tip → khớp cung → sinh VFX từ quỹ đạo → xuất lớp riêng, dựng lại bằng một lệnh.

**Chưa chạy được cho skill phức tạp.** Chủ dự án có thử đòn **chém đôi vuốt lên có xoay hông, xoay thân** (thành chữ X), thử cả trên hình phác lẫn trên
nhân vật. Model không giữ được hướng xoay thân, không làm đủ hai động tác trong một clip, và vệt cung dính vào lưỡi kiếm. Ghi chép đầy đủ:
`docs/milestone-01-research-rising-cuts.md`.

## 4. Xin anh/chị quyết

1. Chấp nhận các điểm lệch ở mục 2, nhất là: bản cuối bám đường gốc/mũi thật (Catmull-Rom) thay vì cung tròn, và tiêu chí 3 đạt do cách dựng.
2. Có promote `SweepFrame` và bộ sinh `slash_from_track.py` vào `lib-fx/_core/vector/` không, hay giữ ở thư mục thử nghiệm thêm một milestone nữa?
3. Có sửa `hash()` trong `gen_slash_loop` ở core không. Thay bằng hàm cố định, có thể làm đổi chút ít các slash cũ trong showcase.
4. Milestone tiếp theo: áp quy trình này cho một skill đơn khác (một nhân vật hoặc một đòn khác), hay quay lại bài toán skill phức tạp (nhiều động tác,
   xoay thân), ví dụ tách mỗi động tác thành một clip có ảnh khoá riêng?

Cảm ơn anh/chị.
