# holy_commander (Thánh Kỵ Sĩ Chỉ Huy)

## Request
`/fal-image --hero --tier M hiệp sĩ thánh giáp bạc viền vàng, khiên thập tự tay trái, kiếm dài tay phải, áo choàng đỏ --creative`

## Concepts offered (2026-10-19)
- A. Paladin Tường Thành: đô con, vai giáp to, khiên thập tự lớn, tank.
- B. Kiếm Sĩ Thập Tự: thon, kiếm rất dài, khiên nhỏ, lướt chém.
- **C. Thánh Kỵ Sĩ Chỉ Huy**: mũ trụ có mào đỏ, áo choàng dài, hỗ trợ. ← chosen

## Choices
- Concept C; weapon: medium shield + sword raised diagonally; palette: silver + gold accent, red cape; role: melee
- Skills: Cờ hiệu thánh, Chém sáng, Xung phong

## Class / size
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 156x140 @1x (312x280 @2x), body 120 @2x
- Role: melee

## Slots
- `{id}`: holy_commander
- `{body}`: biped
- `{design}`: A top-heavy holy knight commander about 2.5 heads tall (huge rounded silver shoulder plates, small head, short legs), wearing sleek silver plate armour with a gold cross emblem on the chest and a simple engraved gold swirl pattern (a few big flat swooping lines) on each shoulder plate and the hip armour, and a tall silver helmet with an angular T-shaped visor and one tall swept-back red plume crest; a big broad heavy VERY LONG longsword (blade as tall as from the ground to his chest) with a wide silver blade, a gold crossguard, a long grip and a gold EAGLE-HEAD pommel, held in both mitten-shaped hands; no shield; a long plain red cape behind him; saturated silver main colour, bright gold accent, red cape.
- `{idle}` (master_v07): UPRIGHT calm stance facing right, feet planted wide apart on one horizontal ground line, the sword point stuck into the ground in front of the body, blade vertical, both hands stacked on the eagle pommel
- `{attack}`: raise the sword, then chop down in front of him
- `{death}`: falls to his knees and forward in place, sword drops
- `{skills}`:
  - cờ hiệu thánh: pulls the sword upright beside him, point on the ground, and thrusts his free fist high in command; a small gold banner rises above him (vfx, separate asset). Peak differs from the idle (raised fist)
  - chém sáng: two-handed chop from top to bottom; the pose is the END of the chop (leaning forward, blade low and forward, tip inside the frame); a flat gold slash arc forward (vfx, separate asset)
  - xung phong: leans forward into a dash, sword carried low in both hands behind the hip, tip pointing back-down, cape streaming back

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v07 | chốt 2026-10-19: trường kiếm dài cắm đất, hai chân giang rộng, báng đại bàng |
| icon | fal-image | ảnh tĩnh | ✅ v01 | |
| pose_skill_holy_banner | fal-image | ảnh tĩnh | ✅ v01 | kiếm cắm đất, cờ vàng |
| pose_skill_radiant_slash | fal-image | ảnh tĩnh | ✅ v01 | đỉnh nhát chém từ trên xuống |
| pose_skill_charge | fal-image | ảnh tĩnh | ✅ v01 | cúi người, kiếm đưa ngang người |
| run_side | video-sprite | loop | ✅ t01 | export --despill --kind hero (colour gate fail là vết màu key bleed, hết sau despill); 8 hình, 15fps, canvas 156x140, body 111px@2x |
| attack_side | video-sprite | one-shot | ⏳ t04 accepted, chốt bản bớt frame | combo 2 chém (chéo xuống + ngang, 3s, dồn người về trước); accepted bỏ qua gate area/feet/turn (vệt lưỡi liềm làm méo silhouette, user đã xem frame thật và duyệt). Quay 2s (t05) và prompt chặt hơn vẫn 2s (t06) đều làm model gộp mất 1 nhát — không quay thêm. User chốt: giữ frame của t04, bớt 1/2 số frame (xen kẽ) để animation tự nhanh hơn (46→23 hình, 3.07s→1.53s); CHƯA export sang canvas 156x140 (cần `video_to_sheet.py`, chọn đúng tập frame đã bớt khi retime) |
| death_side | video-sprite | one-shot | ❌ | |
| respawn_side | video-sprite | one-shot | ❌ | |
| levelup_side | video-sprite | one-shot | ❌ | |
| skill_holy_banner_side | video-sprite | one-shot | ❌ | |
| skill_radiant_slash_side | video-sprite | one-shot | ❌ | |
| skill_charge_side | video-sprite | one-shot | ❌ | |
| fx_holy_banner | fal-image vfx | hiệu ứng | ✅ v01 | cờ hiệu, asset riêng |
| fx_radiant_slash | fal-image vfx | hiệu ứng | ✅ v01 | vệt chém vàng, asset riêng |

Estimated cost: 5 stills + 2 vfx x ~USD 0.014 (~USD 0.10) + 8 clips x ~USD 0.08 (~USD 0.64) + retakes.

## Update 2026-10-19: weapon changed (shield + sword -> two-handed longsword)
  - xung phong: leans forward into a dash, sword carried low in both hands behind the hip, tip pointing back-down, cape streaming back

## Update 2026-10-19 (2): upright master with sword planted
Design v04: shield removed; `{design}` and `{idle}` above replaced. Master prompt uses the new `{UPRIGHT}` (format.md §3), `--ref master_v03`.

## Update 2026-10-19 (3): longer sword, wide stance (v06, v07; ref master_v04)
`{design}` unchanged except the sword is longer (blade from the ground to the chest, whole sword above the waist) and the stance is wide: feet planted shoulder-width and a half apart on one ground line. When approved, fold this into `{design}`/`{idle}` above.

## Approved 2026-10-19
master_v07 approved by user ("v07 đẹp nhất, chốt"). `{design}` and `{idle}` above now describe it.
