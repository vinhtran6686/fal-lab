# 03. Đọc đúng một bản gốc

Gần như mọi lỗi lớn trong hai bài test đến từ **đo sai bản gốc**, không phải từ công thức dựng hình. Danh sách dưới đây là các bẫy đã gặp, dấu
hiệu nhận ra và cách tránh (đã thành code trong `measure.py` / profile).

| # | Bẫy | Dấu hiệu (user thấy) | Nguyên nhân thật | Cách làm đúng |
|---|---|---|---|---|
| 1 | Chỉnh tham số khi chưa đo hình | 7 vòng sửa, "hình sai", lặp khuôn | đoán hình thay vì đo | vector hoá bản gốc trước, đọc số neo, tay nắm, góc |
| 2 | Mặt nạ đúng mã màu | thiếu mũi lửa, khe tối giữa lớp, hình "rác" | lớp có gradient mép; mã đúng chỉ là lõi | lớp = **đường màu** (màu phẳng → màu mép) |
| 3 | Mặt nạ sai số rộng | lớp tối phình to | quầng sáng trùng màu lớp tối | dung sai nhỏ cho lớp tối; quầng đo riêng |
| 4 | Một màu viền mỏng coi là lớp | lớp vụn bao quanh | đó là dải gradient của lớp kề (hổ phách = mép vàng) | xem không gian: màu chỉ nằm ở mép một lớp → là gradient của lớp đó |
| 5 | Khe 1-3 px giữa hai lớp coi là nét tối | "nứt nẻ" | khử răng cưa (màu khe = pha của hai lớp) | đo màu khe trước khi coi là nét |
| 6 | Glow có thành phần < 1,5 px | viền chấm sáng / viền xanh đậm | khử răng cưa bị fit thành glow | loại thành phần hẹp hơn 1,5 px **ảnh gốc** |
| 7 | Gradient đo trên ảnh đã phóng to | viền đậm quanh hình (Toxic) | vệt nhoè do phóng to 3x | quy mọi ngưỡng về px ảnh gốc (`source.scale`) |
| 8 | Glow cố định theo khoảng cách | đốm tàn sáng rực ở frame cuối | designer làm nhoè hình và giảm độ mạnh glow theo thời gian | `halo_model: blur` + `gain[frame]` |
| 9 | Chỉ đo ở frame đỉnh | mảnh vỡ cuối bị mất | lớp mờ dần, màu lệch khỏi màu phẳng | lớp theo **độ đục** (`alpha`) + `opacity[frame]`; đo mọi frame |
| 10 | Lớp tối trùng màu nền | bóng khói nuốt cả nền và bục | khói trong mờ, tối hơn nền chứ không có màu riêng | `darker_than_bg` |
| 11 | GIF nhỏ, dither | không màu nào "đúng mã" | màu bị lượng tử hoá / pha | gom cụm màu (k-means), xem bản đồ từng cụm |
| 12 | Tối ưu IoU | thêm mảnh vụn, hình xấu | IoU không thấy "rác" | mỗi mảnh phải tăng IoU đủ mới giữ; luôn làm mịn; chấm bằng mắt |

Quy trình đọc (tóm tắt, chi tiết `../README.md` §5): tấm tổng hợp mọi frame → khung cắt và cỡ → màu (đếm mã / gom cụm) → kiểm tra mặt nạ
bằng mắt ở 3 frame (đầu, đỉnh, tàn) → đo gradient, glow, độ đục **theo từng frame** → vòng đời và theo dõi mảnh → dựng → review.

Biến lời nhận xét thành phép đo: "rác / gấp khúc" → đếm điểm gãy và độ biến thiên độ cong; "nứt nẻ" → màu dải giữa hai lớp; "đốm sáng ở cuối"
→ độ mạnh glow theo frame; "viền đậm" → profile màu theo khoảng cách vào trong hình ở độ phân giải gốc.
