# Surya (hero)

Request: vẽ lại master từ concept của user (`source/design/concept/concept_user.png`, tỉ lệ 7 đầu, sai chuẩn).
Class hero, tier M ({H} 60, canvas 176x140), role melee, tay không. Skills (user chốt 4): Sun Fist, Whirlwind Kick, Rising Uppercut, Twin Palm Wave; chi tiết ở mục Skills.

{design}: stocky heroic bare-handed martial artist about 2.5 heads tall, top-heavy (huge shoulders, arms, fists; small head; short legs), long straight black hair down the back, sleeveless golden-yellow gi with crossed collar, baggy golden-yellow trousers, wide orange sash with one knot and one flat teal panel, plain gold wrist and ankle bands, bare feet; golden yellow main + orange accent.

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v02 | chốt 2026-10-25 (Surya được user confirm) |
| icon | fal-image | ảnh tĩnh | ❌ | |
| run_side | video-sprite | loop | ❌ | |
| attack_side | video-sprite | one-shot | ❌ | |
| death_side | video-sprite | one-shot | ❌ | |
| pose_respawn | fal-image | ảnh tĩnh | ⏳ v01 | quỳ một gối, nắm đấm chống đất |
| respawn_side | video-sprite | one-shot | ❌ | |
| fx_respawn | fx-layers | hiệu ứng | ❌ | |
| fx_levelup | fx-layers | hiệu ứng | ❌ | |
| levelup_side | video-sprite | one-shot | ❌ | |
| pose_skill_sun_fist (p1-p3) | fal-image | ảnh tĩnh | ⏳ v01 x3 | 3 pha, chờ user duyệt |
| pose_skill_whirlwind_kick (p1-p3) | fal-image | ảnh tĩnh | ✅ v01 x3 | chốt: chuỗi xoay hông, chân trụ cùng một chỗ, p3 hai tay giữ guard |
| pose_skill_rising_uppercut (p1-p3) | fal-image | ảnh tĩnh | ⏳ p1 v01, p2 v01, p3 v02 | không còn cần: clip làm từ video mẫu, không từ still (hero.md §5: tuỳ chọn) |
| pose_skill_twin_palm_wave (p1-p3) | fal-image | ảnh tĩnh | ⏳ v01 x3 | 3 pha, chờ user duyệt |
| skill_whirlwind_kick_side | video-sprite | one-shot | ⏳ t01 | clip user chốt (p1→p3, 4 s); frame đã cắt nhưng còn vệt trắng-tím của model ở mũi chân (frame 8-16), cần cắt lại |
| skill_rising_uppercut_side | video-sprite | one-shot | ⏳ t01 | clip làm từ video mẫu (`ref/sprite/uppercut/ref_uppercut.mp4`, `docs/reference-video-motion.md`), user: rất tốt. Fx dính trong thân. Chưa cắt frame. Sửa lần sau: thân bị thu nhỏ khi hạ thấp -> giữ đúng cỡ nhân vật |
| skill_sun_fist_side, skill_twin_palm_wave_side | video-sprite | one-shot | ❌ | 2 clip |
| fx_whirlwind_kick (p1-p3 stills) | fal-image | ảnh tĩnh | ⏳ v01 x3 | thử fal: chỉ hiệu ứng trên nền magenta; sẽ phủ với opacity (sprite layer), cần dời đúng vị trí |
| fx_rising_uppercut | fx-layers | hiệu ứng | ⏭ | fx nằm trong clip t01 (video mẫu), không có recipe riêng |
| fx_sun_fist, fx_twin_palm_wave | fx-layers | hiệu ứng | ❌ | |
| package | export | gói | ❌ | |

## Why chosen (master_v02)
Vẽ lại từ concept user (7 đầu) bằng gpt-image-2 low, --ref concept, 2 bản. User chốt v02 (khoảng 4 đầu, sash có đuôi dài, vòng tay chân đôi) và nói không cần chi tiết mặt (mắt nhắm là chấp nhận được). Kiểm tra: ingest_image --check không cảnh báo, thân cao 79% khung, nền magenta sạch.

## Skills (level 2, `format.md` §11; facing RIGHT, near arm = image left)
**A. Sun Fist (đấm thẳng)**
| Phase | Body | Effect |
|---|---|---|
| 1 Wind-up + load | khuỵ gối, chân trước gập khoảng 90 độ, chân sau thẳng, trọng tâm hạ thấp; hông xoay ra sau; vai bên tay đấm ngả ra sau, tay đó co khuỷu kéo sát hông, nắm đấm dồn lực; tay kia giơ nhẹ phía trước ngực; giữ một nhịp | nắm đấm sau hông, không hiệu ứng |
| 2 Release | chân sau đẩy, hông xoay về phía trước, vai bên đấm đẩy tới, tay đấm duỗi thẳng nhất, nắm đấm dẫn đầu; tay kia kéo về hông | vệt vàng-cam phẳng bám theo nắm đấm từ lúc nó vượt thân |
| 3 Impact | tay duỗi thẳng ngang ngực, vai đẩy tới trước, thân hơi nghiêng tới, 2 chân giữ nguyên | tại khung này sóng xung kích phẳng hình vòng cung sinh ra ở nắm đấm và đẩy ra phía trước |
| 4 Follow-through + hold | tay thu về, đứng thẳng lại về idle, tóc và đuôi sash vung ra sau rồi rơi | sóng nở rộng và nhạt dần rồi biến mất |
Pose stills: p1, p2, p3 (đã vẽ). Dài khoảng 2.5 s. Rủi ro: mô hình hay xoay thân quay mặt; ghi "vai giữ góc 30 độ".

**B. Whirlwind Kick (đá quét)**
| Phase | Body | Effect |
|---|---|---|
| 1 Wind-up + load | ngồi thấp, trọng tâm vào chân trụ, vai xoay ngược hướng đá, 2 tay co ôm ngực; giữ một nhịp | không |
| 2 Release | chân trụ đẩy, hông và vai xoay, chân kia vung ra, gối dẫn, cẳng còn gập, 2 tay vung nhẹ giữ thăng bằng | vệt cong vàng nhạt bám theo bàn chân khi nó vượt thân |
| 3 Impact | chân duỗi thẳng ngang eo về bên phải, 2 tay giữ guard sát thân (lực dồn vào chân, không vung tay), tóc và đuôi sash bay ra sau | cung quét lưỡi liềm phẳng quanh người ở mức eo, neo ở hông, hướng ra phía trước |
| 4 Follow-through + hold | chân thu về, đáp xuống, tóc rơi, về idle | cung nhạt dần |
Pose stills: p1, p2, p3 (chốt: chân trụ cố định giữa khung; p1 gối co chamber, hông cuộn ngược; p2 hông bật, gối dẫn, cẳng còn gập; p3 chân duỗi ngang eo). Dài khoảng 2.5 s. Rủi ro: xoay 360 độ làm mô hình quay lưng; chỉ ghi xoay thân, không xoay hẳn.

**C. Rising Uppercut (móc ngược)**
| Phase | Body | Effect |
|---|---|---|
| 1 Wind-up + load | ngồi thấp, gối co, trọng tâm hạ; tay đấm thả thấp cạnh hông, tay kia co trước cằm; giữ một nhịp | không |
| 2 Release | 2 chân đẩy lên, hông và vai nhấc, tay đấm vung lên theo đường chéo, khuỷu dẫn trước | vệt vàng phẳng bám nắm đấm |
| 3 Impact | cánh tay gập khoảng 100 độ, nắm đấm ngang mắt (không vượt đỉnh đầu), thân thẳng đứng, 2 chân đứng vững | cung nhô lên phẳng neo ở nắm đấm |
| 4 Follow-through + hold | thu tay, hạ gối về idle, tóc và đuôi sash rơi | cung nhạt dần |
Pose stills: p1 windup, p2 release, p3 đỉnh (v01 tay quá đầu, v02 gọn). Rủi ro: mô hình giơ tay quá đầu, ngả thân về trước; ghi "nắm đấm ngang mắt, thân xoay 30 độ".

**D. Twin Palm Wave (hai chưởng)**
| Phase | Body | Effect |
|---|---|---|
| 1 Wind-up + load | gối trước co khoảng 90 độ, chân sau thẳng; hai bàn tay mở kéo sát hông sau, vai ngả ra sau; giữ một nhịp | không |
| 2 Release | chân sau đẩy, hông và vai tiến lên, hai tay đẩy ra phía trước, lòng bàn tay mở hướng ra | vệt ánh vàng phẳng bám theo 2 bàn tay |
| 3 Impact | 2 tay duỗi ngang ngực, lòng bàn tay trước, vai đẩy tới | sóng nở hình vòng cung phẳng neo ở 2 bàn tay, đẩy ra phía trước |
| 4 Follow-through + hold | thu tay về, đứng thẳng lại về idle, tóc rơi | sóng nhạt dần |
Pose stills: p1, p2, p3. Rủi ro: 2 bàn tay dính vào nhau; ghi "2 bàn tay tách riêng, một gần một xa".
