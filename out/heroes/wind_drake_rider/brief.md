# Wind Drake Rider (hero)

Request: `reports/brief-261029-0014-dragon-rider-master-and-idle-pose.md` (phép thử cơ chế: master + 1 pose idle; cấu trúc rig tham khảo, thiết kế nguyên bản) + design do user dán.
Class hero, tier L ({H} 84, canvas 220x196), role melee. Skills (user chốt 2026-10-29): combo_slash (liên hoàn chém, tham chiếu chuyển động từ sprite mẫu của user, chỉ nhìn, không gửi API); Gale Slash chọn nhưng chưa viết chi tiết (để sau). Drake Dive không làm.
Phạm vi hiện tại: master + 1 clip idle_loop_side theo `reports/brief-261029-0014-dragon-rider-master-and-idle-pose.md` (B); phép thử cơ chế. Report lấy từ hero KR4 có đuôi/bờm/cánh; nhân vật đã đổi thành long nhân nên khác chút (vẫn có thân, đầu, tay, đuôi, bờm, cánh).
Chi tiết user chốt: kiếm gió cong dài tới ngực, tay giơ = tay gần camera (bên phải), giơ lên trong idle. Đuôi, bờm, cánh vẽ rộng hơn thân (theo bbox brief: toàn bộ ~102 x 71 đơn vị, thân ~53 x 55).
Override mặc định: {UPRIGHT} bỏ ý "vũ khí hạ thấp" (tay giơ kiếm là dáng idle của thiết kế); vẫn thẳng đứng, hai chân một đường đất.

{design} (đổi 2026-10-29: từ 'hero + rồng nhỏ' sang long nhân): a stocky heroic dragonkin warrior, a dragon-person about 3 heads tall (draw the head big and the legs short, not a tall lean figure), with a dragon head with two swept-back horns and a short snout, a humanoid body in layered scale-plate armor built from several stacked overlapping plates on the chest, shoulders and belly, strong arms with clawed hands that grip a sword hilt with fingers, short sturdy legs ending in clawed dragon feet, one thick tail growing from the base of the spine with several curling segments, a flowing feathered mane running from the head down the back, and one large wind-swept cape-like wing trailing from the shoulders; the tail, mane and wing are drawn noticeably wider than the torso itself, spreading out behind and above the body; the near right arm is raised holding a curved wind-blade that reaches from the waist to the chest, its tip clearly below the top of the head (blade and hand fully inside the frame), the other arm relaxed at the side; deep teal-blue scales with a bright cyan accent on the mane and wing edges, dark blue-black outline.

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v05 | chốt 2026-10-29 (long nhân) |
| icon | fal-image | ảnh tĩnh | ✅ v01 | đóng gói frames/icon |
| run_side | video-sprite | loop | ⏭ | chưa cần (ngoài phạm vi brief) |
| attack_side | video-sprite | one-shot | ⏭ | chưa cần (ngoài phạm vi brief) |
| death_side | video-sprite | one-shot | ⏭ | chưa cần (ngoài phạm vi brief) |
| pose_respawn | fal-image | ảnh tĩnh | ⏭ | chưa cần (ngoài phạm vi brief) |
| respawn_side | video-sprite | one-shot | ⏭ | chưa cần (ngoài phạm vi brief) |
| fx_respawn | fx-layers | hiệu ứng | ⏭ | chưa cần (ngoài phạm vi brief) |
| fx_levelup | fx-layers | hiệu ứng | ⏭ | chưa cần (ngoài phạm vi brief) |
| levelup_side | video-sprite | one-shot | ⏭ | chưa cần (ngoài phạm vi brief) |
| pose_skill_combo_slash (p1-p3) | fal-image | ảnh tĩnh | ⏳ | 3 pha, chờ user duyệt |
| skill_combo_slash_side | video-sprite | one-shot | ❌ | 4 nhát + xoay nhảy, ~5 s |
| fx_combo_slash | fx-layers | hiệu ứng | ❌ | cung gió phẳng theo từng nhát |
| pose_skill_gale_slash, skill_gale_slash_side, fx_gale_slash | - | - | ⏭ | đã chọn, chưa viết chi tiết |
| pose_skill_drake_dive | fal-image | ảnh tĩnh | ⏭ | chưa cần (ngoài phạm vi brief) |
| skill_drake_dive_side | video-sprite | one-shot | ⏭ | chưa cần (ngoài phạm vi brief) |
| fx_drake_dive | fx-layers | hiệu ứng | ⏭ | chưa cần (ngoài phạm vi brief) |
| idle_loop_side | video-sprite | loop | ❌ | brief (B): vòng ~1 s, thở nhẹ; đuôi/bờm/cánh phấp phới lệch nhịp; không dịch chuyển |
| package | export | gói | ❌ | |
Ước tính: 4 still x ~USD 0.014 + 2 vfx + ~7 clip x ~USD 0.08.

## Why chosen (master_v05)
Vẽ lại từ design 'long nhân' bằng gpt-image-2 low sau 4 bản hero+rồng nhỏ bị loại; 2 bản long nhân, chọn v05 (đứng thẳng, cyan rõ, bờm/cánh trải rộng). ingest_image --check sạch, thân cao 83% khung.

## Skills (level 2, `format.md` §11; facing RIGHT, near arm = image left)
**combo_slash (liên hoàn chém)**: tham chiếu chuyển động: sprite mẫu của user, ~45 frame, 6 đoạn (chém ngang, gồng xoay lưng, chém chéo, xoay nhảy, quét thấp, bổ kết); chỉ lấy nhịp, không lấy thiết kế.
| Phase | Body | Effect |
|---|---|---|
| 1 Lên gồng (0-0.8 s) | hạ trọng tâm, chân sau trụ, vai cầm kiếm quay ngược ra sau, kiếm kéo về sau lưng bên trái, đầu nhìn mục tiêu; đuôi, bờm, cánh ngả ra sau | không |
| 2 Chém ngang 1 (0.8-1.5 s) | chân sau đẩy, hông xoay, vai rồi tay duỗi, kiếm vung ngang trái sang phải, thân dồn tới; đuôi và cánh vung theo sau | cung gió cong bám lưỡi kiếm |
| 3 Lên gồng 2 (1.5-2.1 s) | xoay ngược lại, kiếm qua vai lên cao sau đầu | không |
| 4 Chém chéo xuống (2.1-2.9 s) | hông xoay, kiếm chém chéo từ vai xuống thấp, thân gập nhẹ | cung gió chéo |
| 5 Xoay nhảy chém (2.9-4.0 s) | gối co, nhảy xoay ~180 độ, kiếm giơ cao rồi bổ xuống khi đáp, gối nhún; cánh dang rộng khi bay | cung bổ xuống, vòng gió nhỏ khi chạm đất |
| 6 Chém kết + giữ (4.0-5.0 s) | chân trụ dạng, kiếm quét ngang cuối, rồi về tư thế giơ của master, đuôi và bờm rơi lại | cung quạt lớn rồi tan |
Pose stills: p1 (pha 1), p2 (pha 2, đỉnh chém ngang), p3 (pha 5, xoay nhảy bổ xuống). Dài ~5 s. Rủi ro: model gộp hoặc bỏ nhát khi 5 s; xoay 180 độ làm quay lưng (ghi "xoay thân, mặt vẫn thấy"); kiếm biến dạng khi vung nhanh (`no-blur`, `weapon-shape`).
