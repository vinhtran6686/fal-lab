# lion_brawler: history

| date | sheet/still | vNN | model | score | verdict | issue | change for next version | requested by |
|---|---|---|---|---|---|---|---|---|
| 2026-11-11 | master | v01 | gpt-image-2 low | 9 | awaiting user (auto-approved by Claude) | ngực có vài nét cơ hơi chi tiết | - | user: "thú tộc ... sư tử ... ngầu" |
| 2026-11-11 | rig plate | v01 | gpt-image-2 low | 8.5 | awaiting user | còn mỏm vai gần (bị lớp tay che) | - | pipeline (Puppet Kit) |
| 2026-11-11 | pose_levelup | v01 | gpt-image-2 low | 9 | awaiting user | - | - | pipeline |
| 2026-11-11 | pose_claw_p1 | v01 | gpt-image-2 low | 9 | awaiting user | - | - | pipeline |
| 2026-11-11 | pose_claw_p2 | v01 | gpt-image-2 low | 8 | awaiting user | tay vung và tay thu khó phân biệt gần/xa | - | pipeline |
| 2026-11-11 | pose_skill_slam_p1 | v01 | gpt-image-2 low | 9 | awaiting user | vẽ nhỏ hơn master ~20%: bù bằng unit của pose rig | - | pipeline |
| 2026-11-11 | pose_skill_slam_p2 | v01 | gpt-image-2 low | 8.5 | awaiting user | chân sau bị nắm vuốt che | - | pipeline |
| 2026-11-11 | icon | v01 | gpt-image-2 low | 9 | awaiting user | - | - | pipeline |
| 2026-11-11 | idle / levelup / attack / skill_slam + fx | p01 | Puppet Kit | - | awaiting user | cỡ và điểm chân của pose căn bằng mắt + tỉ lệ diện tích, sai số vài px | thêm lệnh căn pose tự động | pipeline (Puppet Kit) |
| 2026-11-11 | pose_run_1..4 | v01 | gpt-image-2 low | 8 | awaiting user | pose 4 đứng thẳng hơn 3 pose kia; chân gần/xa ở pose 1 và 3 khó phân biệt | - | user: "implement running pose" |
| 2026-11-11 | run_side | p01 | Puppet Kit | - | awaiting user | 4 hình vẽ cho 8 frame: giật hơn vòng chạy video; đầu nhún 22 px @2x | thêm pose trung gian hoặc rig chân | user |
| 2026-11-11 | pose_run_1, pose_run_3 | v01 | gpt-image-2 low | 5 | rejected by user (kept until the profile rig replaces them) | tay trái gập sát, nhìn như tật | ghi góc khuỷu bằng số; chuyển sang run rig profile (puppet-kit-next.md P05) | user: "tay trái bị tật" |
| 2026-11-11 | layer_legs, layer_near_arm, layer_far_arm, layer_tail | v01 | gpt-image-2 low | 3 | rejected | model phóng to và dời bộ phận ra giữa ảnh: không khớp master | prompt ERASE + giữ đầu làm mỏ neo | pipeline (F1) |
| 2026-11-11 | layer_torso | v01 | gpt-image-2 low | 9 | awaiting user | - | - | pipeline (F1) |
| 2026-11-11 | layer_legs, layer_near_arm, layer_far_arm, layer_tail | v02 | gpt-image-2 low | 8.5 | awaiting user | bờm (mỏ neo) đè lên đỉnh vai gần | mỏ neo khác cho lớp tay | pipeline (F1) |
| 2026-11-11 | rig v2; idle / v2_test / levelup / attack / skill_slam | p02 | Puppet Kit | - | awaiting user | đỉnh vai gần cắt theo mép bờm; khe nhỏ ở gấu quần khi gối gập sâu | xem puppet-kit-next.md §8 | user: rig chân, háng, khuỷu |
| 2026-11-11 | hurt_side | p01 | Puppet Kit | - | awaiting user | giật nhẹ, chưa có chớp trắng (fx) | - | T5 |
| 2026-11-11 | death_side | p01 | Puppet Kit | - | awaiting user | chưa có đoạn đổ người; 3 hình cuối gần như đứng yên (giữ cố ý) | pose still nằm nếu cần | T5 |
| 2026-11-11 | skill_roar_side | p01 | Puppet Kit | - | awaiting user | 6 hình giữ gầm chỉ nhún 0,5 px (giữ cố ý) | fx_roar riêng | T5 |
| 2026-11-11 | rig v2 smooth joints; mọi state rig | p03 | Puppet Kit | - | awaiting user | gối gập sâu còn răng cưa nhỏ ở nếp gập | pose still/video cho góc gắt | user: "cắt rig làm chuyển động gãy khúc" |
