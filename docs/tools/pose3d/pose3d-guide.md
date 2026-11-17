# Pose3D: chỉnh tư thế 3D bằng tay để vẽ bằng fal-image

`tools/pose3d/` là một trang web: người dùng tự chỉnh tư thế của nhân vật trong 3D (kiểu Cascadeur, gọn hơn), lưu các tư thế của một động tác, rồi mỗi tư thế được vẽ bằng `fal-image` với khung khối của tư thế làm ảnh tham chiếu. Lý do: mô hình ảnh/video không tự quyết tư thế đúng; khi được cho khung khối đúng tỉ lệ nhân vật thì gpt-image-2 vẽ đúng tư thế (thử trên moon_crane 2026-11-16: 4/4 tranh đầu đạt, `out/heroes/moon_crane/history.md`).

## Bộ khung kiểu Cascadeur (v3, 2026-11-17)
Người nộm là ma-nơ-canh trơn (không trang phục) theo **thân chính** của master: tỉ lệ khớp từ `out/heroes/<id>/source/rig/mannequin_master.json` (đo trên master_v08, 270 px một đơn vị, cao 3,0: đầu to r 0,32, vai ±0,59, hông ±0,39, cột sống 1,07, đùi 0,40, ống 0,26, cánh tay 0,48 + 0,52). Cùng file đó làm thân cho proxy (`build.py --layers` với `body_from`).
Khung là phân cấp khớp thật (FK): hông → thắt lưng → ngực → cổ → đầu; xương đòn → vai → khuỷu → cổ tay; háng → gối → cổ chân (+ mũi chân, gót). Tay và chân giải bằng IK hai đoạn tới đầu mút, mặt phẳng gập theo điểm hướng (pole). Bên phải nhân vật tô ấm, bên trái tô lạnh; mặt có dải mắt và mũi để biết đầu quay đâu.

## Cách dùng
- Mở trang (artifact trên claude.ai, hoặc `tools/pose3d/index.html` trên máy có mạng tới cdn.jsdelivr.net).
- **Bấm và rê thẳng trên khớp** (kiểu Cascadeur, không gizmo, 2026-11-17): rê chuột qua khung là chấm gần nhất sáng lên (vùng bắt 26 px), bấm vào chấm **hoặc vào thân** rồi rê. Điểm đi theo chuột trên mặt phẳng song song màn hình. Vàng: hông (dời cả người, chân giữ đất), tay, chân, mũi thương (chĩa thương quanh chỗ hai tay nắm). Xanh: bụng, ngực, đầu (gập, ngả, quay về phía chuột; rê đầu tự tắt "mắt nhìn mục tiêu"). Tím: khuỷu, gối (đổi hướng gập). Giữ **Shift** khi rê để xoay: hông quanh trục dọc, vặn bụng/ngực, nghiêng đầu, xoay bàn chân. Kéo vùng trống để xoay camera, cuộn để thu phóng; Ctrl+Z / Ctrl+Shift+Z hoàn tác / làm lại.
- **Hai tay bám thương** (bật): kéo hoặc xoay thương, hai tay tự nắm hai điểm trên cán; rê tay phải = dời cả thương, rê tay trái = xoay thương quanh tay phải. Tắt: mỗi tay đặt riêng.
- **Mắt luôn nhìn mục tiêu**: đầu tự quay về mục tiêu (cột đỏ, phải màn hình) trong ±60° so với ngực.
- **Bắt đầu từ chuyển động**: kéo "Khung" để lấy dáng của một khung trong chuyển động đã nướng (proxy, có thể từ HY-Motion): hông, xoay ngực (chia cho thắt lưng và ngực), thương, mũi chân khoá; thương tự dời về phía vai khi tay quá tầm (như `scripts/motion_proxy/skeleton.py`). "Phát" để xem. Cả 22 khung của moon_crane đạt mọi kiểm tra.
- **Camera**: "Camera game" (trước, cao 15°, trực giao), "Nhìn chéo", "Nhìn ngang", "Nhìn từ trên". **So với master**: đặt ma-nơ-canh vào dáng đứng của master (đo trên master_v08), camera nhìn thẳng, ảnh master mờ phía sau để so đầu, vai, hông, gối, mặt đất (Ctrl+Z về dáng trước).
- **Gót tự kiễng** (cả khi kéo tay): mũi chân giữ nguyên, gót nhấc vừa đủ để chân với tới, tối đa `max_heel_lift` (0,24); quá mức đó "Chân với tới" chuyển đỏ. Độ nhấc không ghi vào đích chân, nên hoàn tác và tư thế đã lưu vẫn sạch.
- **Kiểm tra vật lý** (xanh/đỏ, kèm vòng trọng tâm và đường đỡ dưới đất): xoắn ngực–hông ≤ 55°, chân với tới, tay với tới chỗ nắm, bàn chân không xuyên đất, trọng tâm trong vùng đỡ (% về chân trước), hai chân không bắt chéo.
- **Lưu**: đặt tên rồi Lưu; tư thế vào bộ sưu tập `poses` của artifact (Claude đọc bằng công cụ dữ liệu artifact). "Mở" đặt lại đúng dáng đã lưu. Ngoài claude.ai: "Sao chép JSON".

## Dữ liệu một tư thế (`poses/<id>`)
`name`, `note`, `motion`, `fromFrame`, `rig` (`pose3d-fk-ik-v3`), `state` (xoay cục bộ các khớp FK, vị trí/xoay các đích IK, điểm hướng, thương, tuỳ chọn: mở lại được), `yaw` (hông, ngực, đầu, vũ khí, độ), `weaponPitch`, `heel` (độ nhấc gót R/L), `joints` (toạ độ 3D các khớp: pelvis, chest, neck, head, hip/knee/ankle/heel/toe R/L, sh/elbow/hand R/L, butt, tip, blade_root; đơn vị proxy, chiều cao 3,0; x phải màn hình, y lên, z về camera), `savedAt`. Tư thế lưu bằng bản trước (thanh trượt, có `controls`) hiện "bản cũ" và không mở lại được.

## Đổi nhân vật hoặc chuyển động
`bake_motion.py` đọc một `params_used.json` của motion_proxy và nướng từng khung (`--mannequin` thay thân và vũ khí bằng số đo từ master và thêm hình khối, `--master-img` nhúng ảnh master đã tách nền để so); `build.py` nhúng vào `pose3d.template.html` thành `index.html`. Xuất bản lại artifact cùng file để giữ link.

## Giới hạn
- Ma-nơ-canh để đọc tư thế, không phải hình nhân vật (không giáp, vạt áo, cánh hạc).
- Cột sống hai đoạn (thắt lưng, ngực), chưa có giới hạn góc khớp và AutoPhysics: tool chỉ báo, không tự sửa. Khi một chấm bị che, xoay camera.
