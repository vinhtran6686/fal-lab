# Puppet Studio: khái niệm và cách yêu cầu AI (dành cho bạn)

Tài liệu này giải thích các loại "điểm" và tính năng trong Studio, để bạn biết gọi tên đúng khi nhờ AI thêm hoặc sửa. AI dùng bản kỹ thuật: `docs/puppet-studio-ai-guide.md`.

## 1. Bộ xương nhìn từ ngoài

| Thứ bạn thấy | Tên | Là gì |
|---|---|---|
| Chấm tròn nhỏ có nhãn | **Khớp** (bone) | Một đoạn xương. Có **tâm xoay** (pivot) và một **khớp cha**: cha xoay thì con xoay theo (xoay vai thì cả cánh tay đi theo) |
| Hình thoi/ống nối hai chấm | **Xương** | Đoạn nối từ tâm xoay tới đầu mút (dùng để chọn nhanh) |
| Vòng tròn trắng nhấp nháy ở đầu mút | **Tay nắm đầu** | Kéo đầu mút (bàn tay…) để tay duỗi theo chuột |
| Vòng tròn hồng + chữ "đích bàn chân" | **Đích IK** | Vị trí bàn chân bám vào đất (xem §3) |
| Vùng màu mờ | **Layer** (hình) | Mảnh ảnh cắt từ hình gốc, gắn vào một khớp |
| Vùng tím/xanh có dải | **Vùng uốn** (skin) | Chỗ ảnh uốn cong liền quanh khớp thay vì cắt rời |
| Hồng đậm, vòng lớn | **Điểm bám dây chằng** | Chỗ cơ ngực dãn theo vai (xem §5) |
| Ô vuông xanh lá | **Socket** | Điểm gắn vũ khí hoặc hiệu ứng |
| Cung cam quanh khớp | **Giới hạn xoay** | Góc xoay tối thiểu/tối đa cho phép |

## 2. Các thao tác với một khớp (các "kênh")

- **Xoay (rot)**: xoay quanh tâm khớp, đơn vị độ. Dùng cho hầu hết mọi thứ: giơ tay, gập khuỷu, quay đầu. Cách làm: chọn khớp rồi bấm **T**, hoặc chế độ Xoay (E) rồi kéo ở bất kỳ đâu, hoặc gõ số ở ô "Xoay".
- **Trượt (tx, ty)**: dời **nguyên cả khớp** (và mọi thứ con của nó) sang ngang/dọc, KHÔNG xoay. Ví dụ: hông trượt xuống = nhân vật ngồi thấp; **vai trượt ra** = dây chằng cơ ngực dãn (§5); đích bàn chân trượt = bước chân. Hiếm khi cần trượt với khớp tay/chân thường, vì xoay là đủ. Phím W, hoặc mũi tên 1 px.
- **Dãn (sx, sy)**: kéo dài/ngắn bộ phận theo hai trục. Dùng để dãn xương tay khi không có dây chằng. Hình bị biến dạng, nên chỉ dùng lượng nhỏ.
- **Nghiêng (shx)**: làm méo xiên. Ít dùng.

## 3. IK và FK: hai cách điều khiển chân

- **FK** (xoay từng khớp): bạn đặt góc đùi, rồi góc gối, rồi góc bàn chân. Chính xác nhưng khó giữ bàn chân đứng đúng chỗ.
- **IK** (đặt đích): bạn đặt vị trí **bàn chân**, máy tự tính góc đùi và gối cho vừa. Đây là mặc định của chân Lion. Khi IK bật, góc xoay của đùi và cẳng chân bị bỏ qua: đó là ý nghĩa của thông báo "Khớp này do IK điều khiển".
- Muốn dời chân: kéo ô tròn hồng (đích bàn chân). Muốn đặt góc đùi/gối bằng tay: tab 2 > tắt IK của chân đó (sang FK).
- **Cẳng chân dãn theo bàn chân**: với chân gần, khi đích xa quá tầm với, cẳng chân tự dài ra (và co lại khi nhấc chân cao thay vì gập gối quá gắt). Cài đặt trong rig: `stretch: "lower"`. Muốn chân xa giống vậy, hãy nhờ AI: "bật cẳng chân dãn cho chân xa".

## 4. Giới hạn xoay

Mỗi khớp có thể có góc nhỏ nhất/lớn nhất (khuỷu không gập ngược, bàn chân không xoay 360°). Hiển thị là **cung cam**. **Kéo hai chấm cam** ở đầu cung để đổi (giữ Shift để làm tròn 5°), hoặc sửa số ở tab 2. Nhớ **Lưu rig**. Giới hạn chỉ chặn khi bạn thao tác trong Studio; mở pose đã lưu thì giữ nguyên giá trị của nó.

## 5. Dây chằng (muscle link)

Khi bạn kéo bàn tay ra quá tầm với, một người thật sẽ nghiêng vai và ngực dãn theo. Dây chằng làm điều đó:
- **Vai trượt ra** theo tay (dùng kênh Trượt của khớp vai), và
- **ảnh ngực quanh các điểm bám dãn theo** (da dãn, không rách).
- Hai kiểu: **dãn cơ** (`stretch`: cho nhân vật có cơ như Lion) và **cả thân đi theo** (`carry`: nhân vật không có cơ).
- Cách thêm: tab 3 > chọn một cánh tay > phím A > bấm 1–3 điểm lên ngực. Bán kính 100–160 là hợp lý; điểm sát vai làm lộ khe. Hoặc nhờ AI: "thêm dây chằng ngực cho tay xa, 2 điểm bám".

## 6. Mối nối tròn (bo tròn chỗ cắt)

Mỗi layer được cắt bằng đa giác nên chỗ nối có thể là mép thẳng. Khi khớp xoay, mép thẳng hở ra thành khe nứt. **Mối nối tròn** thêm một hình tròn của ảnh vào layer, đặt tâm ở khớp: layer xoay quanh đúng tâm hình tròn nên không thấy mép cắt.
- Cách làm: tab Layer bên trái > "Sửa vùng cắt" của layer > tab 4 > "Mối nối tròn" > "Thêm mối tròn tại khớp đang chọn". Chỉnh x, y và r (40–80 px thường đủ). Hình tròn hiện nét hồng.
- Khớp **uốn liền** (khuỷu, đầu gối, thân: vùng tím) thì đã mượt, không cần.

## 7. Chọn khớp: chế độ "nhóm đang chọn"

Chọn một khớp thì Studio chỉ hiện khớp cùng nhóm (khớp cha lên tới gốc và mọi khớp con), ẩn nốt các khớp khác để khỏi bấm nhầm khi hai khớp gần nhau. Bấm ra ngoài hoặc Esc để bỏ chọn thì mọi khớp hiện lại. Tắt hẳn bằng ô "Chỉ hiện nhóm đang chọn". Tab, danh sách khớp ở bên trái dùng để nhảy sang nhóm khác.

## 8. Phím tắt

| Phím | Việc |
|---|---|
| bấm | chọn khớp/hình |
| giữ + kéo | di chuyển (tay duỗi, chân dời đích, hông trượt) |
| **T** (hoặc Ctrl+T) | xoay bằng cách di chuột; bấm hoặc Enter = giữ, Esc/chuột phải = hủy, Shift = tròn số |
| V / E / W / P / A | tạo dáng / xoay / trượt / sửa rig / điểm bám |
| ←/→, ↑/↓ | chỉnh nhẹ 1° hoặc 1 px (Shift = 5) |
| **Ctrl+Z**, Ctrl+Shift+Z hoặc Ctrl+Y | hoàn tác nhiều bước, làm lại |
| Ctrl+S | lưu rig (có backup) |
| Esc, Tab, F, H | thoát chế độ hoặc bỏ chọn, khớp kế, vừa khung, hướng dẫn |

(Một số trình duyệt giữ Ctrl+T để mở tab mới; khi đó dùng T.)

## 9. Cách nói với AI

Dùng tên khớp, tên layer, tên tính năng ở trên. Ví dụ:
- "Thêm khớp `near_ear` con của `head`, tâm ở (300,150), giới hạn -30…30."
- "Bật cẳng chân dãn cho chân xa như chân gần."
- "Thêm mối nối tròn bán kính 55 ở cổ tay layer near_arm."
- "Thêm dây chằng ngực cho tay xa, 2 điểm bám ở ngực, mode stretch."
- "Đổi giới hạn khuỷu gần thành -5…140."

AI sẽ sửa rig của Studio (có backup), chạy test và vẽ thử ảnh cho bạn xem trước khi báo xong.
