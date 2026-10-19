# thunder_sage (Lão Gù Râu Bạc, pháp sư sấm sét)

## Request
`/fal-image hero pháp sư sấm sét già, gậy gỗ cổ thụ --creative` (2026-10-19)

## Concepts offered
- **A. Lão Gù Râu Bạc**: gù, thon, râu trắng khổng lồ, mũ nhọn; gậy chạc đôi; bắn tia sét. ← chosen
- B. Lão Tăng Sấm: vai to, đầu hói, lông mày rậm; gậy thân cây khắc dấu sét; vung như côn (melee, M).
- C. Mộc Lão Sấm: người phủ vỏ cây và rễ; gậy cành sống; nện gậy gọi sét (melee, L).

## Choices
- Concept A; weapon: ancient gnarled wooden staff with a forked top, one hand; palette: deep indigo + electric yellow
- Role: ranged; skills: Chain Lightning, Thunderstorm, Thunder Step

## Class / size
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 156x140 @1x (312x280 @2x), body 120 @2x
- Role: ranged (adds `shoot_side` + `projectile`, no `attack_side`)

## Slots
- `{id}`: thunder_sage
- `{body}`: biped
- `{design}`: A hunched, thin old thunder mage about 2.5 heads tall (small head, huge flowing white beard drawn as two or three flat layered shapes, long sleeves, short legs), wearing a long deep indigo robe and a wide pointed indigo hat; one tall ancient gnarled wooden staff of dark knotted brown wood with a forked two-pronged top stands upright in his right hand, with one flat bright electric yellow lightning-bolt shape between the two prongs, the staff reaching about as high as the hat tip; saturated deep indigo main colour, bright electric yellow accent, brown wood, white beard.
- `{idle}`: UPRIGHT calm stance facing right, both feet on one horizontal ground line, staff upright in the right hand
- `{poses}`: staff held upright at rest; for shooting the staff points forward
- `{attack}`: (ranged) `shoot_side`: points the forked staff forward, a yellow bolt leaps from the fork
- `{death}`: crumples to his knees and falls forward in place, staff drops
- `{skills}`:
  - chain_lightning: points the staff forward, arm extended; a lightning chain jumps between enemies (vfx)
  - thunderstorm: raises the staff straight up over his head, looking up; a storm of bolts rains on the area ahead (vfx)
  - thunder_step: stamps the staff's foot on the ground and blinks forward in a small flat yellow burst touching the body

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v02 | chốt 2026-10-19 (user chọn v02; v01 giữ làm bản cũ) |
| icon | fal-image | ảnh tĩnh | ✅ v01 | chốt 2026-10-19 |
| projectile | fal-image | ảnh tĩnh | ✅ v01 | tia sét vàng nhỏ, bay sang phải; chốt 2026-10-19 |
| pose_skill_chain_lightning | fal-image | ảnh tĩnh | ✅ v01 | gậy chĩa trước; chốt 2026-10-19 |
| pose_skill_thunderstorm | fal-image | ảnh tĩnh | ✅ v01 | gậy giơ thẳng lên trời; chốt 2026-10-19 |
| pose_skill_thunder_step | fal-image | ảnh tĩnh | ✅ v01 | dộng gậy xuống đất; chốt 2026-10-19 |
| run_side | video-sprite | loop | ❌ | |
| shoot_side | video-sprite | one-shot | ❌ | |
| death_side | video-sprite | one-shot | ❌ | |
| respawn_side | video-sprite | one-shot | ❌ | |
| levelup_side | video-sprite | one-shot | ❌ | |
| skill_chain_lightning_side | video-sprite | one-shot | ❌ | |
| skill_thunderstorm_side | video-sprite | one-shot | ❌ | |
| skill_thunder_step_side | video-sprite | one-shot | ❌ | |
| fx_chain_lightning | fal-image vfx | hiệu ứng | ✅ v01 | chuỗi sét, asset riêng: out/vfx/chain_lightning/design/; chốt 2026-10-19 |
| fx_thunderstorm | fal-image vfx | hiệu ứng | ✅ v01 | mưa sét, asset riêng: out/vfx/thunderstorm/design/; chốt 2026-10-19 |

Estimated cost: 6 stills + 2 vfx x ~USD 0.014 (~USD 0.11) + 8 clips x ~USD 0.08 (~USD 0.64) + retakes.
