# Quy tắc viết mô tả động tác cho clip và bộ pose (mọi nhân vật, mọi vũ khí)

Áp dụng cho skill `video-sprite` và `fal-image` (pose của một động tác). Bản làm việc cho AI nằm trong
`.claude/skills/fal-image/action-planes.md` §9 và `.claude/skills/video-sprite/references/motion-prompts.md`
("Writing a move from a reference animation"). Doc này giải thích lý do và cho mẫu.

## Vì sao cần
Mô hình ảnh và video không biết võ thuật, không biết "trước" và "sau" của nhân vật. Chỉ cần mô tả thiếu một hướng, hoặc có hai câu
mâu thuẫn, nó tự điền theo thói quen: quay mặt về người xem, vẽ thêm một đòn, quơ vào không trung, vẽ thêm vệt. Quy tắc dưới đây
buộc người viết ghi đủ những gì mô hình không tự suy ra được, và để người xem đối chiếu được với những gì họ thấy trên màn hình.

## Quy tắc (viết cho mọi nhân vật)

1. **Xác định hệ quy chiếu và ghi vào mô tả.** Camera là camera của game: cố định, ở phía trước, hơi cao. "Phía trước" của nhân vật là
   hướng của mục tiêu mà nó tấn công; ở góc nhìn nghiêng gốc đó là **bên phải màn hình** (ảnh gốc nhìn sang phải; nhân vật nhìn trái
   là bản lật). "Phía sau" là bên trái màn hình, "phía gần" là phía người xem, "phía xa" là phía xa người xem. Trái và phải trong
   mọi câu luôn là trái và phải **của màn hình**, ghi rõ một lần ở đầu mô tả, không trộn với trái phải của cơ thể. Nhờ vậy mô hình biết
   nhân vật nhìn hướng nào và đánh hướng nào, còn người duyệt đối chiếu được với góc nhìn của mình.
2. **Mỗi bước nêu đủ năm thứ:** thân nhìn theo hướng nào so với camera (dùng tên hướng của `action-planes.md` §4b), mắt nhìn đâu,
   hai chân làm gì, hai tay làm gì, và vũ khí chỉ về đâu trên màn hình. Thiếu hướng của một bước là lỗi.
3. **Đường đi của vũ khí viết như hình học:** nó nằm trong mặt phẳng nào, ở độ cao nào, đi qua phía gần (ngang trước người) hay
   phía xa (sau lưng, bị thân che), đi từ đâu tới đâu trên màn hình. Không viết "chĩa trái rồi chĩa phải": mô hình hiểu thành hai
   cú đâm ngược nhau. Viết "quét ngang qua phía trước người từ trái sang phải". Muốn vệt chém thành một đường thẳng thì viết
   vũ khí **nằm ngang, song song mặt đất, ở độ cao cần**.
4. **Một động tác là một mô tả liền mạch.** Không tự thêm đòn thứ hai, nhịp dừng hay thế thu về. Nhịp khựng chỉ dùng để phân biệt
   hai động tác khác nhau; trong một động tác nó khiến mô hình tách thành hai.
5. **Mỗi đòn có mục tiêu:** kẻ địch ngoài khung, ghi rõ bên nào của màn hình, độ cao nào, cách bao xa (vũ khí cận chiến thì một tầm
   vũ khí). Vũ khí đi xuyên qua mục tiêu, không quơ vào không trung. **Mắt luôn nhìn mục tiêu** suốt động tác, kể cả khi thân quay
   lưng (nhìn ngoái qua vai).
6. **Xoay đến từ thân, đúng thứ tự thật:** hông trước, rồi vai, rồi tay và vũ khí. Chân chỉ xoay trên mũi chân tại chỗ, không trượt,
   và cả người không quay như con quay. Gồng thì hông và vai xoắn **ra xa** mục tiêu, nhả thì xoắn **về phía** mục tiêu.
7. **Không ghi giây.** Chỉ liệt kê các bước theo thứ tự, mô hình tự dàn nhịp. Độ dài động tác chọn bằng độ dài clip.
8. **Kết thúc ở bước cuối và giữ nguyên.** Không về thế gốc, vì game tự reset nhân vật.
9. **Một động tác thì không có điểm dừng; hai động tác giống nhau mà ngược hướng thì cần một nhịp dừng nhìn thấy được giữa chúng.**
10. **Khi người dùng góp ý, viết lại toàn bộ mô tả từ đầu**, không vá. Sau một kết quả hỏng, nêu câu nào của prompt gây lỗi
    (từ chỉ hướng mơ hồ, câu mâu thuẫn, chi tiết mô hình không vẽ được) rồi mới trả tiền chạy lại.
11. **Đọc hết tham chiếu trước khi viết:** tách animation thành khung, xác nhận với người dùng đúng nhân vật và ô, đọc khung chính ở độ
    phóng đại lớn, ghi hướng thân, mắt và vũ khí từng khung, rồi kiểm tra đường đi của vũ khí từng khung (phía gần, phía xa, bị che).
    Gif hoặc webp gửi qua chat chỉ tới AI **một khung**: phải có file trong `ref/`; thiếu thì dừng, không đoán.

## Mẫu bảng mô tả (điền trước khi viết prompt)

| Bước | Thân và hướng so với camera | Mắt | Chân | Tay | Vũ khí (hướng trên màn hình, độ cao, đi phía gần hay xa) |
|---|---|---|---|---|---|
| 1 Sẵn sàng | | | | | |
| 2 Gồng | | | | | |
| 3 Quét qua mục tiêu | | | | | |
| 4 Quét tiếp (đà) | | | | | |
| 5 Giữ thế cuối | | | | | |

Mở đầu mô tả luôn có câu hệ quy chiếu (quy tắc 1) và câu mục tiêu (quy tắc 5).

## Quy tắc khi tạo clip

- Khung đầu và khung cuối **cùng kích thước thân và cùng đường chân**; nếu không, nhân vật to rồi nhỏ trong clip.
- Chỉ ghim khung cuối khi có ảnh đã duyệt cho tư thế cuối.
- Một vòng xoay trọn thân cần khoảng 5 giây; mỗi vòng thử 2 clip; báo giá trước (0,015 USD mỗi giây ở 768P).
- Mỗi prompt có: khoá nhận dạng nhân vật, vũ khí cứng giữ nguyên hình, camera cố định, chân không trượt và thân giữ một kích thước,
  cấm mọi hiệu ứng và cung, vệt, bóng mờ, quầng sáng, nhòe, nền magenta phẳng.

## Mô hình hay làm sai và cách xử lý

| Thói quen | Xử lý |
|---|---|
| Vẫn vẽ vệt trắng hoặc hồng dù đã cấm | Siết bộ tách nền (alpha từ `min(R,B) - G` = 8 đến 53): vệt biến mất, nhân vật không đổi, không cắt khung |
| Giữ thế cuối rất lâu, chạy động tác chậm | Cắt khung tĩnh khi dựng gif |
| Bỏ qua góc bằng số, lề, độ dài giữ | Không dùng chữ cho những thứ này; xử lý ở khâu cắt và thu khung |
| Hai nửa ngược hướng bị hiểu thành hai động tác | Một câu quét liền mạch theo một chiều |
| Gồng ngược hướng | Xem khung, ghi nhận trong review, chỉ chạy lại khi ảnh hưởng đến kết quả |
| Vũ khí đáng lẽ bị che lại lộ ra | Chấp nhận; lớp hiệu ứng che |

## Quy trình

Mô tả → người dùng duyệt → mới chạy. Sửa nhỏ thì nêu đúng một thay đổi rồi chạy. Xem từng khung trước khi báo cáo, đối chiếu với bảng
mô tả, nói rõ phần chưa kiểm tra được. Một tư thế lấy từ một khung mẫu: gửi ảnh gốc của nhân vật trước, khung mẫu sau, nói rõ chỉ lấy
tư thế, không lấy thiết kế, màu hay vệt.
