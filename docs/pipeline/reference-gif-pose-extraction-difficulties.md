# Từ gif tham chiếu đến bộ pose của nhân vật: vì sao chưa ổn

Phạm vi: quy trình xuyên nhiều công cụ (`fal-image`, `video-sprite`, Puppet Kit, `lib-fx`). Mục tiêu là lấy chuyển động từ một gif tham chiếu của nhân vật khác,
dựng cho nhân vật của mình (moon_crane, cầm thương) một **bộ pose** đủ rõ để tách khung, dựng rig pose-to-pose và ghép fx thành một skill cụ thể.
Doc này ghi: tham chiếu nào, video nào được đánh giá là ổn nhất, và những khó khăn còn lại. Các quy tắc viết mô tả đã rút ra nằm ở
`docs/skills/video-sprite/video-sprite-motion-description-rules.md` và `.claude/skills/fal-image/action-planes.md` §9.

## 1. Tham chiếu: nhân vật 1 trong `ref/king/leon-leon-yase2.gif`

Gif 900x600, 116 khung (30 ms mỗi khung), có **5 nhân vật** xếp lưới; chu kỳ lặp là 60 khung. **Nhân vật 1 = ô trên cùng bên trái**, cắt vùng (0, 0)-(300, 300) của mỗi khung.
Khung đánh số từ 0. Vệt chém trắng xám nằm ngay trong khung (khung 16-33), không tách riêng khỏi thân.

| Khung | Pha | Thân, hướng nhìn, vũ khí (trái và phải là của màn hình) |
|---|---|---|
| 0, 59 | Sẵn sàng | Chính diện 3/4, chân rộng bằng vai, kiếm tay phải màn hình chĩa lên chếch phải |
| 12-14 | Dựng kiếm | Thân xoay 3/4 sang trái, kiếm dựng thẳng bên đầu, chân trái bước trước |
| 15 | Gồng | Hông và vai xoắn, kiếm kéo ra sau đầu chếch lên trên-trái khoảng 45 độ |
| 16 | Nhả | Người hạ thấp một nấc, kiếm nằm ngang bên trái, mũi chĩa trái; vệt chém bắt đầu |
| 17-18 | Quét qua phía gần | Người cúi rất thấp, lưng cong, nhìn nghiêng mặt sang phải; kiếm đã quét qua **trước người** sang phải |
| 19-27 | Quay lưng | **Lưng về camera**, áo choàng che thân, **không thấy kiếm** (đi qua phía xa, sau lưng) |
| 28-33 | Thu | Nhổm dậy, kiếm ló ra bên trái ngang hông, mũi chĩa trái |
| 34-38 | Quay về | Xoay từ lưng sang nghiêng rồi sang mặt, kiếm hạ thấp bên trái |
| 39-58 | Thế thủ thấp | Chính diện 3/4, kiếm cầm thấp một tay, mũi chĩa xuống-phải khoảng 25 độ |

Điều rút ra: kiếm đi **một vòng tròn trọn vẹn 360 độ ngang eo** (từ trái, qua phía gần sang phải, qua phía xa bị thân che, ló ra bên trái); thân xoay một vòng đầy, mỗi pha có
hướng thân riêng. Cú xoay đọc rõ nhờ **thân che vũ khí ở nửa sau vòng**, không nhờ một pose "kiếm chĩa vào người xem".

Gif `ref/monkey/leon-leon-houzi-1.gif` (80 khung, hai nhân vật, gậy) chỉ được dùng để lấy **một khung** làm ảnh tham chiếu tư thế (khung 0-3: tấn thấp, gậy vắt vai).

## 2. Video được đánh giá là ổn nhất: `pose_library_h3_t02`

`out/heroes/moon_crane/source/video/pose_library_h3_t02.mp4`: 10 giây, 243 khung ở 24 fps, 768x768, h3-max-turbo, 0,15 USD. Một lần tạo, một khung đầu (master đặt giữa canvas 768 nền magenta,
nhân vật chiếm khoảng 63% chiều cao, chừa chỗ trên đầu cho thương: `prompts/pose_library_h3_first_frame_768.png`), prompt `prompts/pose_library_h3_t02.txt`:
11 động tác nối nhau, **không ghi giây**, cấm dừng, cấm mọi hiệu ứng, hướng thân và hướng nhìn ghi từng động tác theo màn hình.

Các khung dùng được (đếm từ 1; kiểm tra bằng phân tích chuyển động, độ nét và xem từng khung; danh sách đầy đủ trong `source/video/pose_library_h3_t02_poses.json`):

| Pose trong video | Khung video | Khung king tương ứng | Khớp với king |
|---|---|---|---|
| Sẵn sàng, thương dựng | 1, 239 | 0, 59 (và 12-14 dựng kiếm) | Đúng |
| Gồng, thương kéo sau đầu | 24 | 15 | Đúng |
| Tấn thấp, thương vắt vai | 35 | 39-58 (thế thủ thấp) | Gần: tư thế khác (king cầm kiếm thấp phía trước, video vắt thương lên vai) |
| Thương nằm ngang trước ngực, thân quay về camera | 103 | 16-18 (quét qua phía gần) | **Không khớp**: king quét qua trước người, video đứng im đối mặt camera |
| Giơ thương trên đầu | 120 | không có | Pose bổ sung |
| Cúi bổ xuống, thương chếch xuống phải | 137 | không có | Pose bổ sung |
| Quay lưng về camera | 148 (142-151) | 19-27 | Đúng hướng thân; hơi mềm; thương **vẫn thấy** (king che hẳn) |
| Xoay, thấy từ phía sau bên phải | 154 | 34-38 (quay về) | Gần |
| Bước sang trái, thương nằm ngang ngang hông | 166, 169 | 28-33 (thu, kiếm ló ra trái) | Đúng hướng; gần nhất với một pose nghiêng |
| Ngồi xổm sâu | 205 | không có | Pose bổ sung |
| Giơ thương thẳng trên đầu | 229 | không có | Pose bổ sung |

Ảnh tĩnh `out/heroes/moon_crane/source/design/pose_profile_right_v01.png` (một ảnh `fal-image`, 0,0183 USD) cho **góc nghiêng thật** nhìn sang phải, thứ video không tạo được.

Cú xoay đã chốt trước đó (`skill_spin_back_v5_t01.mp4`): các khung chính 0, 24, 50, 70, 80, 90 của clip ứng với king 0, 15, 16, 17-18, (không có), 28-33. Bản dựng pose-to-pose bằng Puppet Kit từ các khung đó đã bị bỏ (không đạt).

## 3. Vì sao chưa ổn: những khó khăn

1. **Chỉ một khung của gif tới được AI qua chat.** Gif và webp gửi qua chat chỉ còn khung đầu; các lần đầu AI "đoán" chuyển động từ một khung và làm sai hoàn toàn. Chỉ khi gif nằm trong `ref/` thì mới tách khung và đọc được từng pose.
2. **Mô hình không biết kinematics.** Mô hình video không có khái niệm hông dẫn rồi vai rồi tay, chân xoay trên mũi chân, vũ khí đi qua phía gần hay phía xa. Nó vẽ chuyển động "nhẹ nhàng như múa", không dứt khoát.
3. **Từ chỉ hướng bị đọc sai.** "Chĩa trái rồi chĩa phải" thành hai cú đâm ngược nhau; "quét qua mục tiêu bên phải" thành cú đâm vào mắt người xem vì không có hướng thân và hướng nhìn; thiếu "nhìn thấy / không nhìn thấy" làm thân quay về camera.
4. **Góc nghiêng hoàn toàn không đạt được bằng chữ.** Ở bản t02, ba động tác ghi "pure side profile" đều quay về camera (đã biết: `style-chunky.md` §9). Chỉ **ảnh tĩnh nghiêng** làm được (`pose_profile_right_v01`).
5. **Không kiểm soát được thời gian.** Dù cấm dừng, pose đánh vẫn bị giữ khoảng 2,3 giây (khung 64-104); đặt "nhịp ngưng" thì nó giữ quá lâu. Chỉ chỉnh được sau khi cắt khung.
6. **Mô hình tự thêm hiệu ứng và nhòe.** Cung trắng, hồng, xanh quanh vũ khí và khung nhòe xuất hiện dù cấm (t02: khung 56, 120-123, 157-162). Có thể che bằng bộ tách nền chặt hơn, nhưng làm mất chi tiết ở đầu thương.
7. **Mất nhận dạng và đổi cỡ.** Video dài trôi dần; khung đầu và khung cuối khác cỡ thì nhân vật phình hoặc co; khung ghim cuối làm mô hình giữ khung đầu rồi nhảy cắt (clip master sang ảnh nghiêng).
8. **Ảnh ghim khác tỉ lệ thân.** Ảnh nghiêng vẽ thương dài hơn thân so với master; căn theo thương thì thân nhỏ 40%, căn theo thân thì thương tràn khung 768.
9. **Video-to-video bị rò hình ref.** LTX-2.3 `union`: nhịp theo ref khá tốt nhưng chép vệt chém trắng, đổi thương thành kiếm, nhân vật trôi sang tròn và thấp; `match_preprocessor` chép nguyên nhân vật ref. Đã bỏ.
10. **Rig 2D không xoay ra ngoài mặt phẳng.** Cú xoay phải dùng pose tĩnh cắt từ clip và nhát cắt giữa các pose; khung trúng đòn bị cắt mất mũi thương và nhòe phải vá bằng mũi thương lật gương từ khung khác. Bản dựng này không đạt và đã bị bỏ.
11. **Fx bám vũ khí, không bám thân.** Vệt chém vòng quanh người phải đo từ điểm bám của rig; khung thời gian của fx (một khung phóng đòn, một khung trúng đòn) khác hẳn nhịp của video.
12. **Tham chiếu và nhân vật khác tỉ lệ.** King cao 6 đầu cầm kiếm, moon_crane 3 đầu cầm thương dài hơn thân; copy tư thế khung theo khung làm tay chân và thương lệch; chỉ lấy được hướng và nhịp.

## 4. Những yếu tố đã làm bản t02 tốt hơn các bản trước

Thứ tự đã thử: 8 động tác (bản đầu, đòn bị quay về camera, bỏ), Google Flow (không đạt, không lưu), t02 (11 động tác, bản được chọn), LTX (2/10, bỏ).

| Yếu tố | Trước | Sau (t02) |
|---|---|---|
| Hệ quy chiếu | không ghi | camera cố định, trái phải là của màn hình, ghi ở đầu prompt |
| Từng động tác | chỉ ghi vị trí vũ khí | ghi hướng thân, mắt, chân, tay, thương, kèm "parallel to the picture plane" |
| Số động tác | 8, có giây | 11, không giây, nối liền, "không dừng" |
| Khung đầu | master vuông, sát mép trên | master 0,70 giữa canvas 768, chừa 31% phía trên cho thương |
| Hiệu ứng | cấm "no effects" | cấm liệt kê từng loại (cung, vệt, bóng mờ, quầng, nhòe, viền xanh hồng) |
| Cỡ thân | không nhắc | "boots stay on the same spots, body keeps the same size" |
| Kiểm tra | xem lưới 10 khung | phân tích chuyển động, độ nét, viền; xem từng khung đã chọn |

## 5. Trăn trở chưa giải quyết

- Một bộ pose đủ dùng cho **mọi skill** cần cả góc nghiêng, chính diện, lưng, 3/4, mỗi góc đủ độ nét; video chỉ cho 3/4, chính diện và lưng. Góc nghiêng cần ảnh tĩnh: bao nhiêu ảnh là đủ?
- Pose copy từ khung tham chiếu (ảnh tĩnh, một khung) làm tốt tay, chân, hướng thương nhưng **bỏ qua góc xoay, lề và kích thước**; mỗi pose một ảnh thì nhịp giữa các pose phải tự dựng.
- Cú quét "thương đi sau lưng bị che" của king khó tái hiện: thương trong video vẫn lộ ra khi quay lưng.
- Chất lượng ổn định giữa các lần tạo: cùng prompt, hai lần cho hai kết quả khác; không có cách chấm tự động ngoài xem tay.
- Cắt khung từ video cho kết quả mềm hơn ảnh tĩnh (độ nét 700-2800 trên thang đo của repo); chưa có bước làm nét hoặc dựng lại khung.
- Giữa "đúng hướng nhưng ngập ngừng" và "dứt khoát nhưng sai hướng", hiện chưa có cách ép cả hai.
