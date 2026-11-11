# Prompt gửi chuyên gia: thống nhất kế hoạch Milestone 01 trước khi test

> Đã trả lời 2026-11-10: [milestone-01-advisor-review.md](milestone-01-advisor-review.md); kế hoạch chốt: [milestone-01-plan.md](milestone-01-plan.md).
> Tên `milestone-01-plan-DRAFT.md` bên dưới là tên cũ.

(Copy toàn bộ phần dưới đường kẻ gửi cho chuyên gia, kèm `milestone-01-modules.zip`.)

---

Chào anh/chị,

Cảm ơn phản hồi về gói `project-discovery`. Bên em đồng ý chọn **Milestone 01: Character-Synchronized Slash** (Holy Commander, một nhát chém
xéo từ trên xuống, hướng Character-first). Chủ dự án muốn **thống nhất kế hoạch và checklist đầy đủ với anh/chị trước**, rồi mới bắt đầu test
(bước tạo pose và clip tốn tiền API). Em đã viết bản kế hoạch nháp (`docs/milestone-01-plan-DRAFT.md`, có trong gói kèm theo) và gom các điểm cần
anh/chị quyết dưới đây. Mỗi câu có **đề xuất của em**; anh/chị chỉ cần trả lời "đồng ý" hoặc sửa.

Gói kèm theo (`milestone-01-modules.zip`) chỉ chứa các module và dữ liệu liên quan trực tiếp tới milestone, như anh/chị đã đề nghị.

## Bối cảnh ngắn (số liệu thật)

- Holy Commander: cell 176×140 @1x, pivot (0,5; 0,88), xuất @2x; thân đo được `body_height_2x` = 111 (≈ 55,5 px @1x), bậc cỡ M ghi H = 60.
- Attack hiện có: 18 frame, 15 fps, `hit_frame` 10, retime từ clip 24 fps; model đã vẽ vệt chém dính thân ở frame 11-12, kiếm bạc cùng màu giáp.
- Tiền lệ ghép: `radiant_slash` (fx Python, 2 lớp back / front, blend screen, `fx.json` có pivot, frame n khớp frame n của thân).
- Vector Kit: nét thon trong khung toạ độ (u dọc đường, v ngang), cung elip (tâm, bán kính, dẹt k, nghiêng); đầu / đuôi nét theo bảng thời gian;
  hiện xuất RGB trên nền, chưa có alpha; hình nộm hiện suy vị trí kiếm **từ** nhát chém.

## Câu hỏi

**Q1. Pose.** Đề xuất 2 pose mới theo master v07: p1 chuẩn bị (kiếm giơ cao ra sau vai, mũi lên / ra sau, chân trước bước tới), p3 kết thúc (kiếm thấp
phía trước, chéo xuống đất, thân đổ về trước). Hướng chém: từ trên-sau xuống dưới-trước. Có đúng ý "diagonal downward slash" của anh/chị không? Có cần
pose giữa (p2, lúc chạm) không?

**Q2. Clip.** Đề xuất: h3-max-turbo, frame đầu p1, frame cuối p3, prompt chỉ cơ thể, quay 3-4 s rồi retime về **0,7 s, chạm ở 40%** (như attack hiện có),
state mới `attack_diag_side`. Tối đa **4 lần quay**; nếu cả 4 đều có vệt model vẽ hoặc không ra đòn chém rõ thì dừng và báo lại. Đồng ý chứ?

**Q3. Đánh dấu quỹ đạo.** Đề xuất: đánh dấu **mọi frame của đoạn vung** (khoảng 5-8 frame, từ lúc bắt đầu vung tới 1-2 frame sau chạm), mỗi frame
Blade Root + Blade Tip + ms. Người đánh dấu: (a) chủ dự án click trên một trang công cụ nhỏ em làm, hoặc (b) em đọc ảnh phóng to có lưới rồi ghi toạ
độ, chủ dự án duyệt trên contact sheet có vẽ điểm. Em nghiêng về (a) cho chính xác. Sai số chấp nhận: ±0,05 H (~3 px @1x). Frame kiếm bị che / mờ thì
ghi `visible: false`, không đoán. Anh/chị chọn cách nào?

**Q4. Quy ước.** Gốc = điểm neo chân, x về trước, **y lên**, đơn vị **H**, thời gian **ms**, dựng ra 15 fps. H lấy theo **bậc cỡ (60 px @1x)** hay **H đo thật
(≈ 55,5 px)**? Em đề xuất H = 60 cho đơn giản và ghi cả hai vào file dữ liệu.

**Q5. VFX tượng trưng cho gì và khi nào bỏ cung elip.** Ba lựa chọn: (a) vệt theo **mũi kiếm** (dải hẹp quanh tip); (b) **vùng lưỡi quét** từ root tới tip
(dải rộng bằng độ dài lưỡi); (c) dải lệch về phía mũi, độ rộng là tham số riêng (không khoá vào độ dài lưỡi). Em đề xuất **(c)**: đường giữa đi theo tip
(lùi vào ~20% lưỡi), độ rộng chỉnh độc lập (tiêu chí 4). Cung elip khớp vào các điểm tip; nếu sai số trung bình > **0,08 H** hoặc lớn nhất > **0,15 H**
thì coi là không đủ và mới làm đường cong tự do. Đồng ý ngưỡng này?

**Q6. Thời gian của VFX.** Đề xuất: đầu nét **trùng** mũi kiếm ở mỗi frame; VFX sinh ở frame tốc độ mũi bắt đầu lớn (≥ 0,3 H / frame), đỉnh ở frame chạm,
sau chạm giãn 1 frame rồi đứt và tan trong **3-4 frame** (~200-270 ms ở 15 fps), on twos ở pha tàn. Có nên cho đầu nét đi trước mũi kiếm 1 frame để
nhát chém "nhanh hơn kiếm" không?

**Q7. Lớp và hoà màu.** Đề xuất chia lớp theo **vị trí so với thân**: phần cung ở phía sau vai xa / sau lưng → lớp **back**; phần trước ngực và phần chạm
đất → lớp **front**. Hoà màu **screen** như `radiant_slash`, đồng thời xuất RGBA (alpha = độ sáng) để engine nào cũng dùng được. Đồng ý chứ?

**Q8. Màu và độ đọc ở 60 px.** Đề xuất bảng màu vàng / trắng (hợp giáp vàng và `radiant_slash`), 2-3 lớp; nét mảnh nhất **≥ 1,5 px @1x** (nét tóc, tia
nhỏ hơn thì bỏ hẳn ở bản game); glow nhỏ. Có cần làm 2 mức chi tiết (bản game @1x tối giản và bản @2x đầy đủ) không?

**Q9. Nơi lưu.** Đề xuất: dữ liệu quỹ đạo và tham số ở `out/heroes/holy_commander/source/vfx/slash_diag/`, frame xuất ở
`out/heroes/holy_commander/frames/fx/slash_diag/` (asset của nhân vật, như `radiant_slash`); code bộ sinh nhỏ trong `lib-fx/_core/vector/`. **Chưa** đưa
vào thư viện `lib-fx/<nhóm>/` cho tới khi milestone đạt. Đồng ý chứ?

**Q10. Ngưỡng đạt cho 6 tiêu chí.** Đề xuất: tiêu chí 3: đầu nét cách mũi kiếm đã đánh dấu ≤ **0,1 H** ở mọi frame đoạn vung, hướng tiếp tuyến lệch
≤ **15°**; tiêu chí 5: nét mảnh nhất ≥ 1,5 px @1x và chủ dự án đọc được trên GIF @1x không phóng; tiêu chí 4: 3 biến thể (dày, dài, cong) đặt cạnh nhau,
mỗi biến thể chỉ đổi đúng một tham số; tiêu chí 6: dựng lại toàn bộ từ `weapon_track.json` + file tham số bằng một lệnh. Anh/chị có muốn ngưỡng khác?

**Q11. Hình nộm.** Có giữ hình nộm (`dummy.py`) trong milestone không, hay bỏ hẳn vì đã dùng nhân vật thật? Em đề xuất không đụng tới nó trong milestone.

**Q12. Cách làm việc.** Em đề xuất chia thành 3 điểm dừng để chủ dự án và anh/chị duyệt: (1) sau B1-B2 (pose + clip), (2) sau B3-B4 (quỹ đạo + VFX riêng ở @1x),
(3) sau B5-B6 (ghép + chấm 6 tiêu chí). Anh/chị có muốn xem thêm gì ở mỗi điểm dừng (ví dụ contact sheet có vẽ root / tip, biểu đồ sai số)?

Ngoài 12 câu trên, nếu anh/chị thấy kế hoạch nháp thiếu bước hay rủi ro nào, em xin bổ sung luôn. Sau khi anh/chị trả lời, em sẽ chốt kế hoạch và checklist
trong repo, chủ dự án duyệt, rồi mới bắt đầu bước tạo pose.

Cảm ơn anh/chị.
