# diablo (hero, quỷ lửa sừng dài)

## Request
`/fal-image` tạo lại master từ ảnh tham chiếu `design/concept_ref.png` (2026-10-22), sau khi xoá nhân vật cinderhorn.

## Class / size
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 176x140 @1x (352x280 @2x), body 120 @2x
- Role: melee (adds `attack_side`)
- Skills: flame_slam, horn_charge, ember_armor

## Overrides of the default style (user chose to keep the reference)
- Flat flame layers as the arms (big orange + yellow shapes), allowed by the user.
- Two huge horns and shoulder spikes allowed (the `{SIMPLE}` ban on spikes lifted for these shapes only).
- Palette: charcoal grey armour + orange main flame + bright yellow accent (a dark hero; the reference's look wins).

## Slots
- `{id}`: diablo
- `{body}`: biped
- `{design}`: A tall menacing horned fire demon, top-heavy, with a small dark helmet head, two huge long curved dark horns, huge spiked shoulder pauldrons, a narrow dark torso with a ragged hanging cloth, dark armoured greaves, and two long arms made of flat layered orange and yellow flame ending in big flame hands; dark charcoal-grey armour, orange main flame colour, bright yellow accent; hands empty, no weapon.
- `{idle}`: UPRIGHT calm stance facing right, both flame arms hanging relaxed along the body
- `{poses}`: no weapon; the flame arms move for each action
- `{attack}`: swings a flame arm forward in a short strike
- `{death}`: collapses to his knees and falls in place, flames die down
- `{skills}`:
  - flame_slam: raises both flame arms, then smashes them into the ground; a fire shockwave spreads (vfx)
  - horn_charge: lowers the head, horns forward, lunges ahead; a flame trail behind
  - ember_armor: crosses the arms over the chest; flame coats the armour (buff)

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v04 | chốt 2026-10-22 (user chọn v04; v01-v03 quay thẳng mặt, giữ làm bản cũ) |
| icon | fal-image | ảnh tĩnh | ✅ v01 | chốt 2026-10-22 |
| pose_respawn | fal-image | ảnh tĩnh | ✅ v01 | chốt 2026-10-22; ngồi xổm hơn là quỳ |
| pose_skill_flame_slam_start | fal-image | ảnh tĩnh | ⏳ v01 | tư thế gồng: chân trước chân sau, hai tay ngang vai; chờ user duyệt |
| pose_skill_flame_slam | fal-image | ảnh tĩnh | ⏳ v04 | ảnh cuối: quỳ 1 chân, hai tay thẳng vuông góc đất, vòng lửa rộng ~4x thân; chờ user duyệt (v01-v03 bị loại) |
| pose_skill_horn_charge | fal-image | ảnh tĩnh | ✅ v01 | chốt 2026-10-22; sừng chĩa trước, thân thấp (ảnh cuối) |
| pose_skill_horn_charge_windup / _load / _lunge | fal-image | ảnh tĩnh | ⏳ v01 | 3 ảnh trung gian (gồng, nén, lao); chờ user duyệt |
| pose_skill_ember_armor | fal-image | ảnh tĩnh | ✅ v01 | chốt 2026-10-22; hai tay lửa khoanh trước ngực |
| run_side | video-sprite | loop | ✅ t04 | đã cắt 2026-10-22 (move/run_side, 19 hình @15 fps, vòng 2 bước chọn tay nguồn 52-88, mối nối sạch theo số đo); chưa xem chuyển động trong Motion Lab |
| attack_side | video-sprite | one-shot | ✅ t02 | đã cắt 2026-10-22 (attack/attack_side, 20 hình @15 fps, hit 12); thay bản t01 |
| death_side | video-sprite | one-shot | ✅ t01 | đã cắt 2026-10-22 (death/death_side, 25 hình @15 fps); giáp đổ thành đống |
| respawn_side | video-sprite | one-shot | ⏳ t01 | đã cắt (spawn/respawn_side, 39 hình @15 fps, --rest-last); lỗi: hình 15-33 to hơn ~10-18% (model zoom giữa lúc đứng dậy) |
| levelup_side | fx (python) | hiệu ứng | ⏳ v01 | user chốt v01; không quay clip: pose master + hào quang lửa xung nhịp, fx/levelup_v01; chưa xuất lớp RGBA |
| skill_flame_slam_side | video-sprite | one-shot | ✅ t02 | đã cắt 2026-10-22 (skill/skill_flame_slam_side, 38 hình @15 fps, hit 15); vòng lửa nằm trong clip |
| skill_fire_breath_side (thay horn_charge) | video-sprite | one-shot | ⏳ t01 | đã cắt cho Fx Studio (skill/skill_fire_breath_side, 33 hình @15 fps, hit 20), chờ user duyệt chính thức; ảnh: _crouch (đầu), pose_skill_fire_breath v02 (cuối, không lửa) |
| fx_fire_breath | fx (python) | hiệu ứng | ⏸ v04 | tạm dừng, user tách topic riêng làm fx sau (lửa là một phần); fx/fire_breath.py, luồng lửa từ miệng; chờ user duyệt, chưa gắn vị trí miệng thật |
| skill_ember_armor_side | video-sprite | one-shot | ⏳ t01 | clip xong, chưa cắt; chỉ thân (không lửa); chờ user duyệt; ảnh cuối pose_skill_ember_armor_v01 |
| fx_ember_armor | fx (python) | hiệu ứng | ❌ | vòng lửa bao quanh nhân vật lúc khoanh tay (buff tăng thủ + tăng dame); làm ở topic fx riêng |
| fx_flame_slam | fx-layers | hiệu ứng | ⏭ | không cần: vòng lửa nằm trong clip |
| fx_respawn, fx_levelup | fx-layers | hiệu ứng | ❌ | |
| package | export | gói | ❌ | |

Estimated cost: 5 stills (~USD 0.07) + 7 clips (~USD 0.56) + retakes. Spent so far: 4 masters ~USD 0.06.

## Why chosen
- master v04: made from the user's concept (`design/concept_ref.png`, `--ref`, prompts/master_p02.txt); the only version of four turned to face right with the far arm hidden; style anchor not compared.
- icon, pose_respawn and the three pose_skill stills: `--ref master_v04`, prompts/<name>_p01.txt, reviewed by eye against the master (same horns, spikes and flame arms, nothing added, inside the frame).
Spent on stills so far: 9 images ~USD 0.12.
