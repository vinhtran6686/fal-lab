# Pose3D: chỉnh tư thế 3D bằng tay để vẽ bằng fal-image

`tools/pose3d/` là một trang web: người dùng tự chỉnh tư thế của nhân vật trong 3D (kiểu Cascadeur, gọn hơn), lưu các tư thế của một động tác, rồi mỗi tư thế được vẽ bằng `fal-image` với khung khối của tư thế làm ảnh tham chiếu. Lý do: mô hình ảnh/video không tự quyết tư thế đúng; khi được cho khung khối đúng tỉ lệ nhân vật thì gpt-image-2 vẽ đúng tư thế (thử trên moon_crane 2026-11-16: 4/4 tranh đầu đạt, `out/heroes/moon_crane/history.md`).

## Người nộm đo từ master
Người nộm không phải khối chung chung: tỉ lệ khớp và độ dày từng khối lấy từ ảnh master (`out/heroes/<id>/source/rig/mannequin_master.json`, đo trên lưới 25 px: đầu, búi tóc, vai, giáp vai, ngực, eo, đai, vạt áo, cánh tay, giáp cẳng tay, nắm đấm, hông, đùi, ống, ủng, cánh hạc, thương; `px_per_unit` = chiều cao thân / 3,0). Nút **So với master** đặt người nộm vào dáng đứng của master, camera nhìn thẳng, và hiện ảnh master mờ phía sau để so từng khối (tay và thương khác vì master cầm thương một tay). Cùng file đó làm thân cho proxy (`build.py --layers` với `body_from`), nên tool và proxy dùng một nguồn tỉ lệ.

## Cách dùng
- Mở trang (artifact trên claude.ai, hoặc `tools/pose3d/index.html` trên máy có mạng tới cdn.jsdelivr.net).
- **Bắt đầu từ chuyển động**: kéo "Khung" để lấy dáng của một khung trong chuyển động đã nướng (proxy, có thể từ HY-Motion), "Phát" để xem.
- **Kéo trực tiếp trên khung 3D** (rê chuột: bộ phận sáng lên): hông/vạt áo dời cả người (Shift: xoay hông); ngực/giáp vai ngang = xoay ngực, dọc = cúi/ngả (Shift: nghiêng); đầu ngang = quay đầu; nắm đấm/cẳng tay dời chỗ hai tay nắm thương; mũi thương ngắm hướng thương; cán thương đẩy/rút; ủng đặt chân trên mặt đất (Shift: xoay bàn chân). Tay cầm nhỏ (mũi thương, nắm đấm, ủng) được ưu tiên khi bị khối to che. Kéo vùng trống để xoay camera, cuộn để thu phóng. Hoàn tác / Làm lại (Ctrl+Z, Ctrl+Shift+Z).
- **Tinh chỉnh bằng số** (mục gập): hông (vị trí, độ cao, xoay), ngực (xoay thêm, cúi/ngả, nghiêng), đầu (xoay thêm; "mắt luôn nhìn mục tiêu" bật = đầu tự quay về mục tiêu trong ±60° so với ngực), thương (hướng, nghiêng, tay cao/thấp, đẩy/rút), hai chân (vị trí mũi chân, xoay bàn chân). Tay tự bám hai điểm nắm trên thương, chân tự bám mũi chân, gót tự kiễng khi chân cần với xa (như `scripts/motion_proxy/skeleton.py`).
- **Camera**: kéo để xoay; "Camera game" = góc của game (trước, cao 15°, trực giao), "Nhìn chéo", "Nhìn từ trên".
- **Kiểm tra vật lý** (xanh/đỏ): xoắn ngực–hông ≤ 55°, chân với tới, tay nắm đúng chỗ trên thương, trọng tâm trong vùng đỡ (% về chân trước), hai chân không bắt chéo.
- **Lưu**: đặt tên rồi Lưu; tư thế vào bộ sưu tập `poses` của artifact (Claude đọc bằng công cụ dữ liệu artifact). Ngoài claude.ai: "Sao chép JSON".

## Dữ liệu một tư thế (`poses/<id>`)
`name`, `note`, `motion`, `fromFrame`, `controls` (giá trị các thanh trượt, mở lại được), `yaw` (hông, ngực, đầu, vũ khí, độ), `weaponPitch`, `heel`, `joints` (toạ độ 3D các khớp, đơn vị proxy, chiều cao nhân vật 3,0; x phải màn hình, y lên, z về camera), `savedAt`.

## Đổi nhân vật hoặc chuyển động
`bake_motion.py` đọc một `params_used.json` của motion_proxy và nướng từng khung (`--mannequin` thay thân và vũ khí bằng số đo từ master và thêm hình khối, `--master-img` nhúng ảnh master đã tách nền để so); `build.py` nhúng vào `pose3d.template.html` thành `index.html`. Xuất bản lại artifact cùng file để giữ link.

## Giới hạn
- Người nộm là khối đơn giản (để đọc tư thế, không phải hình nhân vật). Cột sống một đoạn; cổ tay không xoay riêng; vũ khí nắm cứng hai tay.
- Chưa có AutoPhysics: tool chỉ báo, không tự sửa. Khi một bộ phận bị che hoàn toàn, xoay camera để kéo được.
