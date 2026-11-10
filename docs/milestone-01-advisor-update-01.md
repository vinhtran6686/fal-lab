# Gửi chuyên gia: Milestone 01 đổi đòn (chém đôi vuốt lên thành chữ X)

(Copy phần dưới đường kẻ gửi cho chuyên gia. Ảnh kèm: `out/heroes/holy_commander/.work/m01_poses/review_poses.png` khi pose đã chốt.)

---

Chào anh/chị,

Em đã chốt kế hoạch theo các quyết định của anh/chị (`docs/milestone-01-plan.md`; nguyên văn phản hồi lưu ở
`docs/milestone-01-advisor-review-original.md`). Sau đó chủ dự án **đổi đòn của Milestone 01**. Em báo lại để anh/chị xem phạm vi mới có ổn không.

## 1. Đòn mới (chủ dự án quyết, đã duyệt chuyển động)

Thay một nhát chém xéo từ trên xuống bằng **hai nhát vuốt lên, cắt nhau thành chữ X** ở trước ngực. Nhân vật luôn nhìn sang phải.

- **Nhát 1**, phía gần camera, kiếm thấy rõ: từ sau-dưới lên trước-cao (trên màn hình trái-dưới → phải-trên).
- **Nhát 2**, phía xa của thân, **kiếm khuất sau ngực**: từ trước-dưới lên sau-cao (phải-dưới → trái-trên).

Chuyển động đã duyệt (clip 4 s, 5 beat):

| Thời gian | Beat | Cơ thể và kiếm |
|---|---|---|
| 0-0,4 s | đứng | tư thế đầu: chân giang rộng, hai tay cầm chuôi ở hông sau, lưỡi thấp sau lưng, mũi gần đất |
| 0,4-0,9 s | lấy đà | gối khuỵu, hông hạ, tay kéo chuôi sát hông sau |
| 0,9-1,5 s | nhát 1 | chân trước bước tới, hông rồi vai xoay về trước; kiếm vuốt chéo lên tới cao phía trước, khựng ở đỉnh |
| 1,5-2,3 s | thu kiếm | khuỷu gập, tay kéo chuôi xuống sát người về hông bên kia, cổ tay xoay theo; lưỡi rơi xuống trước theo trọng lượng, mũi gần đất |
| 2,3-2,9 s | nhát 2 | hông rồi vai xoay ngược; tay từ hông bên kia lên qua vai bên kia; kiếm vuốt lên phía xa của thân, khuất sau ngực |
| 2,9-4,0 s | giữ | kiếm cao sau vai, mũi lên-ra sau, trong khung |

Beat "thu kiếm" do chủ dự án sửa: chỉ tả "xoay cổ tay" thì model giữ tay trên cao rồi vặn cổ tay và video lỗi. Phải tả chuỗi lực vật lý: khuỷu gập, tay kéo
chuôi xuống, lưỡi rơi theo trọng lượng. Nguyên văn prompt gửi model: `out/heroes/holy_commander/brief.md`, mục "Milestone 01".

## 2. Ảnh hưởng tới kế hoạch đã chốt

| Mục | Trước | Nay |
|---|---|---|
| Pose | P1 mới + P3 tái dùng `pose_skill_radiant_slash_v01` | **2 ảnh mới**: P1 kiếm thấp sau lưng, P_end kiếm cao sau vai. Chủ dự án không dùng lại pose cũ |
| Clip | 1 clip, frame đầu P1, frame cuối P3 | như cũ (P1 → P_end), 4 s; nếu mất beat thì lên 5 s, không bớt beat |
| Thời lượng animation cuối | 0,8-1,2 s | ~1,2-1,8 s (hai nhát) |
| Quỹ đạo + VFX | một nhát | **từng nhát một**: Milestone 01 làm hết 6 tiêu chí cho **nhát 1** (kiếm thấy rõ); nhát 2 làm sau với cùng bộ sinh |
| Lớp | có thể chỉ cần front | nhát 2 đi sau thân, nên đây là bài test thật cho lớp back (Q7) |
| Gate, quy ước, tiêu chí, giới hạn chi phí | | giữ nguyên |

Chi phí: hai ảnh, mỗi ảnh tối đa 3 lần (trần 0,084 USD); clip tạo từng cái một, chủ dự án duyệt từng take (0,06 USD / clip 4 s, trần 4 clip).

## 3. Rủi ro em thấy

1. **Model vẽ vệt sáng khi vung mạnh** (đã gặp ở attack t01, t04 và radiant t01). Ở state này vệt sáng tính là không đạt.
2. **Nhát 2 không khuất sau thân**: model có thể cho kiếm đi phía trước, hoặc xoay người cho thấy kiếm. Khi đó không ra chữ X.
3. **Ít điểm đo ở nhát 2**: kiếm bị che thì ghi `visible: false`, có thể không đủ điểm để khớp đường cong. Đây là lý do làm nhát 1 trước.

## 4. Xin anh/chị xác nhận

1. Đổi đòn như trên, với cách làm **VFX từng nhát** (nhát 1 trước, đủ 6 tiêu chí), có ổn không?
2. **Ràng buộc khi khớp cung** (em thêm): đòn chỉ có 5-8 điểm mà elip tự do có 5 tham số, nên khớp gần như luôn "đạt". Em đề xuất khớp **đường tròn
   (k = 1) trước**, chỉ thả độ dẹt và góc nghiêng khi có ≥ 7 điểm quan sát. Gate vẫn là sai số của phép khớp (mean ≤ 0,08 H, max ≤ 0,15 H); sai số
   leave-one-out trên các điểm giữa chỉ để tham khảo. Anh/chị đồng ý không?
3. Các điểm em thêm khác (kế hoạch §11): clip 4 s; mọi frame 67 ms; vệt do model vẽ = không đạt; không nới canvas 176×140 (không vừa thì dừng hỏi);
   trường `side` (trước / sau thân) ở mỗi điểm đánh dấu; cách sửa prompt cho take 2 quyết trước.

Cảm ơn anh/chị.
