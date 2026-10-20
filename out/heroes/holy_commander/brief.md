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
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 176x140 @1x (352x280 @2x; was 156x140 until the attack swing needed more width), body 111 @2x (area-matched)
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
| pose_respawn | fal-image | ảnh tĩnh | ✅ v02 | quỳ xám, gục đầu vào báng kiếm dựng đứng; ảnh đầu của clip `rise`. Lý do chọn: xem mục Respawn pose bên dưới |
| run_side | video-sprite | loop | ✅ t01 | export --despill --kind hero (colour gate fail là vết màu key bleed, hết sau despill); 8 hình, 15fps, canvas 176x140 (was 156x140; padded), body 111px@2x |
| attack_side | video-sprite | one-shot | ✅ exported | 23 hình (t04 bớt 1/2 frame), 1.53 s @15fps, hit frame 10, canvas 176x140, body rescale x1.094 |
| death_side | video-sprite | one-shot | ✅ exported | 39 hình (t01 bớt 1/2 frame), 2.60 s @15fps, canvas 176x140 |
| respawn_side | video-sprite | one-shot | ⏳ clip t01 quay xong, chờ user duyệt | `pose_respawn_v02` (quỳ xám) -> `master_v07`, 4.46 s raw (`raw/respawn_side_rise_t01`): xám -> hồi màu -> đứng lên. Chưa export 176x140, chưa fx_respawn. Bản đảo despawn cũ bị loại |
| levelup_side | video-sprite | one-shot | ❌ thiết kế lại | thiết kế mới (user): hero đứng, đấm một tay lên trời như vừa chiến thắng/đạt thành tựu; ánh sáng chớp quanh người theo nhịp vung tay. Clip t01 cũ (giơ kiếm chào) không dùng |
| skill_holy_banner_side | video-sprite | one-shot | ❌ thiết kế lại | t01 zoom 2.9x + tia sáng; pose cuối giơ nắm đấm đúng. Thiết kế lại hoàn toàn theo bài học charge_v4 (hiệu ứng nhỏ, sát vũ khí/nắm đấm, câu locked tripod); chờ user chốt ý tưởng |
| skill_radiant_slash_side | video-sprite | one-shot | ❌ thiết kế lại | t01 zoom + vệt chém lớn, pose cuối đúng. Thiết kế lại hoàn toàn theo bài học charge_v4; chờ user chốt ý tưởng |
| skill_charge_side | video-sprite | one-shot | ✅ exported (v4) | 67 hình, 4.47 s @15fps, giữ vòng lửa lớn frame ~46-72 theo quyết định user (user đồng ý đó là lỗi; lần sau dùng hiệu ứng vừa khung hơn, xem report §11); canvas 176x140 |
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

## Respawn pose: pose_respawn_v02 (chốt 2026-10-20)

**Yêu cầu (user)**: respawn thiết kế lại hoàn toàn. Hero quỳ, gục đầu vào thanh kiếm dựng đứng, cả người màu xám; sau đó hồi màu và đứng lên như vừa được khôi phục. Bản đảo despawn cũ bị chê giống pho tượng cứng nhắc.

**Cách tạo**
- `gen_image.py`, `gpt-image-2` edit, `--quality low`, 1024x1024, ref `master_v07`, 3 ảnh trong một lệnh (~0.042 USD). Chưa tốn thêm ảnh nào.
- Prompt lấy từ sidecar `pose_skill_charge_v01.json` (cùng khối design, cùng khối style, nền magenta, "giữ trong khung"). Chỉ thay đoạn tư thế bằng: quỳ một gối, thân cúi, đầu gục tì vào báng đại bàng, trường kiếm dựng thẳng mũi cắm đất, hai tay chồng trên báng, áo choàng rũ xuống đất.
- Thêm câu ép xám: giáp, viền vàng, chữ thập, mũ, chóp mũ, kiếm, áo choàng đều là các sắc xám lạnh (sáng, vừa, tối), không đỏ, không vàng. Câu "không dùng magenta trên nhân vật" đổi thành "nhân vật không có màu nào ngoài xám".
- Ba ảnh cùng prompt, khác nhau do model.

**Vì sao chọn v02**
- Quỳ vững và cân đối, hai tay chồng đúng trên báng đại bàng, đầu tì vào báng rõ: đọc ngay là "gục đầu vào kiếm".
- Trường kiếm dài nhất trong 3 bản (vẫn ngắn hơn master), áo choàng trải rộng sau lưng như master. Tỉ lệ sát master nhất nên đoạn đứng lên cần "bù" ít nhất.
- v01 hơi nghiêng 3/4 và kiếm ngắn nhất; v03 thân thẳng hơn, đầu tì ít, áo choàng cuộn dưới chân.
- Xám sạch hoàn toàn, không sót màu vàng hay đỏ, nên đoạn hồi màu có điểm xuất phát rõ.

**Vì sao ổn (đã kiểm bằng clip)**
- Dùng làm ảnh đầu của `rise` (ảnh cuối `master_v07`, take t01): hero giữ nguyên kích thước suốt clip, màu hồi từ vàng rồi tới đỏ, đứng lên đúng tư thế master, không có vật thể lạ.
- User xem và duyệt: "đẹp, ổn".

**Lưu ý**: kiếm trong pose ngắn hơn master; clip không bị "kiếm dài ra" đáng kể nhưng nếu thấy thì xử lý ở bước export.
