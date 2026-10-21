# cinderhorn history

| date | sheet/still | vNN | model | score | approved/rejected/final/awaiting user | issue | change for next version | requested by (pipeline/user: "...") |
|---|---|---|---|---|---|---|---|---|
| 2026-10-21 | master | v01 | user-supplied (manual) | 8 | approved | fills 95% of frame height, horns 23px from top edge | none | user: "từ ảnh master" |
| 2026-10-21 | pose_skill_cinder_slam | v01 | gpt-image-2 low | 7 | approved | face hidden by shoulder, horns fold to the side, flames fused into two columns | name "face and visor visible, horns upright" | user: "thiết kế 3 skill" |
| 2026-10-21 | pose_skill_horn_charge | v01 | gpt-image-2 low | 7 | approved | horns point up, not forward; face hidden by shoulder | "horns point forward-right, visor visible" | user: "thiết kế 3 skill" |
| 2026-10-21 | pose_skill_ember_armor | v01 | gpt-image-2 low | 8.5 | approved | fills 95% of height again | none | user: "thiết kế 3 skill" |
| 2026-10-21 | skill_cinder_slam_side | t01 | h3-max-turbo 480P 4s | 7 | rejected (retake) | tay giơ thẳng rồi bổ, thiếu khuỷu gập và xoay tay; chuyển động tay chưa vật lý | user: giơ tay khuỷu xuống, xoay hai tay xuống khi thân khom, tay vuông góc vai, rồi phát lực đấm cùng lúc | user: "chạy với skill đầu tiên" |
| 2026-10-21 | skill_cinder_slam_side | t02 | h3-max-turbo 480P 5s | 7.5 | awaiting user | wind-up present (arms up, crouch, arms level, punch); fists slightly above horn tips when raised; shoulders square to camera in wind-up | none yet | user: "giơ tay khuỷu xuống, xoay xuống khom, vuông góc vai, phát lực đấm" |
| 2026-10-21 | skill_horn_charge_side | t01 | h3-max-turbo 480P 5s | 8 | awaiting user | beats right, side view held, arms low; horns end up/back like the approved pose; start frame = pipeline job/input.png (body 572px) so registration will match | none | user: "gen video thử" |
| 2026-10-21 | skill_horn_charge_side | t01 | h3-max-turbo 480P 5s | 5 | rejected | crouched and froze in place, no charge: end still on the same spot as the start | end still displaced +230 px, five-phase prompt | user: "chỉ vô thế rồi ở yên, không lao tới" |
| 2026-10-21 | skill_horn_charge_side | t02 | h3-max-turbo 480P 5s | 8 | awaiting user | surge and travel present, arm flames streak during the surge; horns end up/back like the approved pose | optional: new pose_skill with horns forward | user: "tạo lại đi" |
