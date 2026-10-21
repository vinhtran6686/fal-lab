# cinderhorn (Hiệp sĩ giáp xám, hai tay lửa)

## Request
`/fal-image --creative từ repo fal-lab mình muốn thiết kế 3 skill cho nhân vật cinderhorn từ ảnh master` (2026-10-21)
Ảnh master do user gửi (vẽ ngoài repo), ingest làm `design/master_v01`.

## Concepts offered (bộ skill)
- **A. Lò Rèn Hung Tàn** (cận chiến nặng): Cinder Slam, Horn Charge, Ember Armor. ← chosen
- B. Hỏa Pháp Tầm Xa: Flame Lash, Meteor Rain, Ash Burst.
- C. Kẻ Thiêu Rụi: Fire Wave, Horn Charge, Inferno Pillar.

## Choices
- Bộ A, cả 3 skill; không có vũ khí cầm tay (hai tay là lửa)

## Class / size
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 176x140 @1x
- Role: melee (adds `attack_side`, smear = fx_attack)
- Ghi chú: master cao ~95% khung (sừng cách mép trên 23px), vượt mục tiêu 70%; các pose sau vẽ ở ~65%.

## Slots
- `{id}`: cinderhorn
- `{body}`: biped
- `{design}`: A tall, heavy, top-heavy fire knight about 3 heads tall (small helmeted head with two very tall curved dark-grey horns and a glowing orange flame face slit, huge spiked shoulder pauldrons, narrow waist, short plated legs with a ragged tattered tabard), made of dark charcoal-grey angular plate armour in 3 hard-edged tones; both forearms and hands are replaced by big flat layered orange and yellow flame shapes with flame-tongue edges and a few small diamond sparks; no weapon, empty flaming hands; saturated charcoal-grey main colour with bright orange-yellow flame accent.
- `{idle}`: master (đứng thẳng, hai tay lửa thả hai bên)
- `{attack}`: (melee) đấm lửa về phía trước
- `{skills}`:
  - cinder_slam: gập người, hai nắm đấm lửa dộng xuống đất trước chân; sóng lửa phẳng lan ra trước (vfx)
  - horn_charge: cúi đầu lao tới húc bằng cặp sừng, hai tay lửa hất ra sau; vệt lửa kéo sau lưng (vfx)
  - ember_armor: khoanh hai tay lửa trước ngực, lửa bùng phủ vai và giáp (buff, vfx)

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v01 | ảnh user gửi, chốt 2026-10-21 |
| icon | fal-image | ảnh tĩnh | ❌ | |
| pose_skill_cinder_slam | fal-image | ảnh tĩnh | ✅ v01 | 7/10: mặt bị vai che, sừng cụp sang bên; chốt 2026-10-21 |
| pose_skill_horn_charge | fal-image | ảnh tĩnh | ✅ v01 | 7/10: sừng hướng lên, mặt bị vai che; chốt 2026-10-21 |
| pose_skill_ember_armor | fal-image | ảnh tĩnh | ✅ v01 | 8.5/10; chốt 2026-10-21 |
| pose_respawn | fal-image | ảnh tĩnh | ❌ | |
| run_side | video-sprite | loop | ❌ | |
| attack_side | video-sprite | one-shot | ❌ | |
| death_side | video-sprite | one-shot | ❌ | |
| respawn_side | video-sprite | one-shot | ❌ | |
| levelup_side | video-sprite | one-shot | ❌ | |
| skill_cinder_slam_side | video-sprite | one-shot | ❌ | |
| skill_horn_charge_side | video-sprite | one-shot | ❌ | |
| skill_ember_armor_side | video-sprite | one-shot | ❌ | |
| fx_attack | fx-layers | hiệu ứng | ❌ | |
| fx_respawn | fx-layers | hiệu ứng | ❌ | |
| fx_levelup | fx-layers | hiệu ứng | ❌ | |
| fx_cinder_slam | fx-layers | hiệu ứng | ❌ | sóng lửa phẳng |
| fx_horn_charge | fx-layers | hiệu ứng | ❌ | vệt lửa |
| fx_ember_armor | fx-layers | hiệu ứng | ❌ | lửa phủ giáp |
| package | export | gói | ❌ | |

Estimated cost: 4 stills (~USD 0.05) đã chi 0.039 cho 3 pose; còn icon, respawn ~USD 0.03 + ~9 clips x ~USD 0.08 (~USD 0.72) + retakes.
