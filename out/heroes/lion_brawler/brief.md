# lion_brawler (Sư Vương)

## Request
User (2026-11-11): "tạo thử nhân vật tộc người thú (thú tộc) với động vật chính là sư tử. Mình muốn nhân vật này ngầu ngầu 1 chút để test được nhiều pose".
Chạy như `/fal-image --hero --tier M --creative` rồi áp dụng Puppet Kit. Các lựa chọn còn lại do Claude quyết (user đã uỷ quyền ở nhân vật trước), master tự duyệt (>= 8) như `--auto`.

## Concepts offered (2026-11-11)
- **A. Sư Vương đấu sĩ**: ngực trần, bờm khổng lồ, hai găng vuốt vàng, không vũ khí dài. Cận chiến. ← chosen
- B. Sư tử kiếm khách: áo giáp nhẹ, đại đao một tay vác vai.
- C. Sư tử tù trưởng: áo choàng lông, giáo dài, khiên tròn.
Lý do chọn A: hai tay tự do cho nhiều tư thế nhất (gầm, vung vuốt, dộng đất), bờm và đuôi tạo hình bóng mạnh, vuốt vàng cho vệt chém.

## Class / size
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 176x140 @1x (352x280 @2x), body 120 @2x
- Role: melee

## Slots
- `{id}`: lion_brawler
- `{body}`: biped
- `{design}`: A top-heavy lion beastman brawler about 3 heads tall (a huge spiky dark red-brown mane around the head and over the shoulders, a broad bare chest and huge forearms, a narrow waist, short strong legs), golden-tan fur with a cream muzzle and a cream chest patch, a short snout with a dark nose, a fierce brow line and two small eye slits, two small round ears in the mane; he wears only a saturated blue waist sash with one short hanging cloth end and blue trousers to the knee, big bare paw feet; on EACH fist a big bright-gold gauntlet with three short curved claws; a long thin tail with a dark tuft curving up behind him; no other weapon; golden-tan main colour, saturated blue cloth, bright gold claws.
- `{idle}` (master_v01): UPRIGHT proud stance facing right, feet apart on one ground line, both arms hanging a little away from the body, clawed fists at hip height, tail behind on the left
- `{attack}`: winds the near arm up high behind the head, then swipes the claws diagonally down to the lower right
- `{death}`: drops to his knees and falls forward in place
- `{skills}`:
  - dộng đất (slam): stretches up with both fists overhead, then drives both fists into the ground; a shockwave ring (vfx, separate asset)
  - sư tử hống (roar): chest out, head back, arms flexed; a roar cone ahead (vfx, separate asset). Hiện dùng làm level up

## Skills, level 2 (format.md §11)
### dộng đất (đã làm bằng pose-to-pose: `skill_slam_side`, 20 hình, hit 9)
| Pha | Thân | Hiệu ứng |
|---|---|---|
| 1 wind-up | khuỵu gối trên rig, thân nén, đầu cúi | - |
| 2 load | `pose_skill_slam_p1`: kiễng chân, thân vươn, hai nắm vuốt giơ thẳng trên đầu | - |
| 3 release | cắt sang `pose_skill_slam_p2`: hai nắm vuốt dộng xuống đất trước chân | vệt vàng theo đường vuốt (fx `slam`) |
| 4 impact | thân nén mạnh rồi nảy, rung dọc 4 hình | vòng sốc (chưa làm) |
| 5 hold | cắt về rig, đứng dậy | tan |
### sư tử hống (chưa làm riêng; pose đang dùng cho `levelup_side`)
| Pha | Thân | Hiệu ứng |
|---|---|---|
| 1 wind-up | khuỵu, hít vào, hai tay thu | - |
| 2 load | ngực ưỡn, đầu ngửa | - |
| 3 release | `pose_levelup`: miệng há, hai tay gồng hai bên | nón sóng âm phía trước (vfx riêng) |
| 4 travel | giữ, ngực phập phồng | sóng lan |
| 5 hold | về tư thế nghỉ | tan |

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ⏳ v01 | 9/10, Claude tự duyệt theo uỷ quyền; chờ user xác nhận |
| icon | fal-image | ảnh tĩnh | ⏳ v01 | 9/10; đã pack `frames/icon` |
| pose_levelup | fal-image | ảnh tĩnh | ⏳ v01 | gầm, 9/10 |
| pose_claw_p1 | fal-image | ảnh tĩnh | ⏳ v01 | lấy đà vung vuốt, 9/10 |
| pose_claw_p2 | fal-image | ảnh tĩnh | ⏳ v01 | kết thúc vung vuốt, 8/10 |
| pose_skill_slam_p1 | fal-image | ảnh tĩnh | ⏳ v01 | hai nắm vuốt trên đầu, 9/10; model vẽ người nhỏ hơn, đã căn lại cỡ |
| pose_skill_slam_p2 | fal-image | ảnh tĩnh | ⏳ v01 | dộng đất, 8,5/10 |
| rig v1 (plate_v01 + rig_v1.json) | Puppet Kit | rig | ⏭ thay bằng rig v2 | `source/rig/`: 7 lớp, 8 xương; hai tay mỗi tay hai xương, đuôi riêng; 5 pose rig |
| layer_torso / legs / near_arm / far_arm / tail | fal-image | ảnh tĩnh (lớp rời) | ⏳ torso v01, còn lại v02 | xoá từ master, giữ đầu làm mỏ neo; v01 của 4 lớp sau lệch vị trí nên bỏ |
| rig v2 (rig.json) | Puppet Kit | rig | ⏳ v02 | 17 xương, 16 lớp, IK chân ghim đất, khớp háng và eo, tay 3 đoạn |
| v2_test_side | Puppet Kit (rig v2, $0) | one-shot | ⏳ p02 | 30 hình: bài thử khớp (ngồi xổm, xoay eo, gập khuỷu, đấm) |
| idle_side | Puppet Kit (rig v2, $0) | loop | ⏳ p02 | 24 hình, 1,60 s; gối nhún theo nhịp thở |
| levelup_side | Puppet Kit (pose-to-pose, $0) | one-shot | ⏳ p01 | 21 hình, hit 4 |
| attack_side | Puppet Kit (pose-to-pose, $0) | one-shot | ⏳ p01 | 16 hình, hit 8 |
| fx_claw_swipe | Puppet Kit + bộ sinh M01 ($0) | hiệu ứng | ⏳ p01 | vệt vuốt từ socket; tham số riêng: `source/vfx/claw_swipe/slash_params.json` |
| skill_slam_side | Puppet Kit (pose-to-pose, $0) | one-shot | ⏳ p01 | 20 hình, hit 9 |
| fx_slam | Puppet Kit + bộ sinh M01 ($0) | hiệu ứng | ⏳ p01 | vệt theo đường nắm vuốt; chưa có vòng sốc; tham số riêng: `source/vfx/claw_swipe/slash_params.json` |
| view_front | fal-image | ảnh tĩnh | ⏳ v01 | chính diện; dùng làm ảnh ghim của pose reel |
| reel turn_a / turn_b / run / squat / press | video (pose reel) | clip | ⏳ t01 | 5 clip 480p, mỗi clip một take, 16 s ~0,24 USD; `docs/puppet-kit-pose-reel.md` |
| pose_run_1..4 | fal-image | ảnh tĩnh | ⏭ thay bằng reel run | user từ chối (tay trái gập sai) |
| death_back_side | Puppet Kit (rig v2, $0) | one-shot | ⏳ p01 | 24 hình: trúng đòn, ngã ngửa ra sau, nảy một lần, nằm yên; không video |
| run_side | Puppet Kit (reel, $0) | loop | ⏳ p03 | 8 hình từ clip reel_run |
| turn_left_side | Puppet Kit (reel, $0) | one-shot | ⏳ p03 | 25 hình: quay phải → chính diện → quay trái |
| reel_test_side | Puppet Kit (reel, $0) | one-shot | ⏳ p03 | 37 hình: squat rồi đẩy tay qua đầu (bài thử khớp bằng reel) |
| death_side | Puppet Kit (rig v2, $0) | one-shot | ⏳ p01 | 12 hình: giật ra sau, khuỵu gối tại chỗ, giữ hình cuối; chưa có đoạn đổ người (rig không nằm ngang được) |
| hurt_side | Puppet Kit (rig v2, $0) | one-shot | ⏳ p01 | 6 hình, hit 1: thân giật ra sau, đầu và tay trễ 1 hình |
| pose_respawn | fal-image | ảnh tĩnh | ❌ | |
| respawn_side | video-sprite | one-shot | ❌ | |
| fx_respawn | fx-layers | hiệu ứng | ❌ | |
| fx_levelup | fx-layers | hiệu ứng | ❌ | |
| skill_roar_side | Puppet Kit (pose-to-pose, $0) | one-shot | ⏳ p01 | 22 hình, hit 4: khuỵu 3 hình, pose_levelup giữ 14 hình, về 5 hình |
| fx_roar | fx-layers | hiệu ứng | ❌ | |
| package | export | gói | ⏭ | khi asset rời repo |

Estimated cost so far: 12 ảnh gpt-image-2 low (master, plate, 5 pose, icon, 4 pose chạy) ~USD 0.172. Năm state và hai fx: 0 USD.

## Chờ user duyệt
- Thiết kế (master_v01), icon, 5 pose.
- Bốn chuyển động và hai vệt chém: `frames/<sheet>/preview.gif`, `frames/fx/<name>/preview_with_body_3x.gif`.
