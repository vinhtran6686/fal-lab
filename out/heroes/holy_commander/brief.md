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
| levelup_side | video-sprite | one-shot | ⏳ thân + fx đã chốt, chưa export | thân: `raw/levelup_side_extra_v2_t01` (`pose_levelup_v02`, 3 s, 46 hình). **fx: v03 "hào quang xung nhịp"** vẽ bằng Python (`fx/levelup_variants.py`, 0 USD), user chọn 2026-10-20. Chưa export 176x140; xem mục Levelup fx v03 |
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

## FX policy: vẽ bằng Python trước, gen video + cắt frame chỉ khi cần (chốt 2026-10-20)

**Quy tắc (user):** hiệu ứng (fx) của hero làm bằng **Python tự vẽ chồng lên clip thân sạch** là mặc định vì không tốn phí. Chỉ khi cần hiệu ứng phức tạp, chi tiết hơn mức Python vẽ được thì mới dùng gen video (trả phí) + cắt frame.

**Vì sao Python là mặc định**
- Miễn phí và chạy lại vô hạn: chỉnh màu, độ đậm, nhịp, kích thước là sửa tham số, không phải quay lại clip. Clip gen video tốn ~0.045 USD/take (3 s, h3-max-turbo) và mỗi lần muốn đổi là một take mới.
- Ổn định: clip thân luôn sạch (không vòng lớn, không zoom, gate `area`/`identity` không bị fx làm sai). Fx vẽ vào clip đã gây vòng lửa ở charge_v4 và zoom 2.4-2.9x ở ba skill cũ.
- Tái lập được: nguồn là clip trong `raw/` + một script; không cần `.work`.
- Khớp cách game tham chiếu làm: fx là lớp riêng, thân không đổi.

**Khi nào mới gen video + cắt frame**
- Fx có hình dạng phức tạp hoặc hoạ tiết thật sự (xoáy năng lượng có kết cấu, tia sét nhiều nhánh, lửa có hình, khói, chữ rune), mà Python tạo ra sẽ thô.
- Fx phải ăn khớp với hình dạng/chuyển động của thân hoặc vũ khí từng frame (đường chém bám lưỡi kiếm, lửa bám lưỡi) mà một lớp đặt cố định không làm được.
- Khi đó: quay một take có mô tả fx nhỏ, sát vũ khí hoặc nắm đấm, kèm câu "locked tripod", chấp nhận rủi ro model vẽ thêm vòng lớn; rồi cắt frame (bớt frame của take đã đạt, không quay lại). Báo giá và chờ user ok trước mỗi take.
- Thứ tự thử: Python trước; chỉ khi user thấy chưa đủ chi tiết mới sang gen video.

**Cách làm (Python)**
1. Quay clip thân sạch: prompt không mời hiệu ứng nào, có câu "locked tripod" (clip A của levelup: `raw/levelup_side_extra_v2_t01`).
2. Tách **toàn bộ** frame bằng `ffmpeg fps=15` và key nền bằng `sprite_pack.key_out()`. Không bỏ frame nào (lỗi đã gặp: script chỉ ghép `[:45]` trên 46 frame nên mất frame cuối).
3. Vẽ fx **theo từng frame** bằng `fx/levelup_variants.py` (numpy + PIL), thứ tự lớp: lớp sau thân, thân, lớp trước thân.
4. Ánh sáng dùng chế độ **screen** (màu sáng cộng lên nền), lớp bóng/đục dùng chế độ thường. Tất cả bằng màu + độ trong suốt.
5. Export: neo chân vào pivot (0.5, 0.88), canvas 176x140, body 111@2x như các state khác; fx rộng hơn canvas thì cắt theo canvas hoặc xuất riêng như `fx_layers`.

**Quy tắc thẩm mỹ rút ra (user + đối chiếu hero_malik)**
- Fx là các **lớp bao quanh thân**: cột/vầng sáng trong suốt (thân nhìn xuyên qua), không phải vector phẳng đặt chồng lên nhân vật. Vòng, cột, bùng nổ phẳng từ `fx_layers` (bản A1) bị chê thô và xấu.
- **Màu + độ trong suốt**, mép mềm (blur), không có viền nét đậm. Dùng gradient độ trong suốt: đậm ở chân, nhạt dần lên đầu.
- **Lớp rộng, dễ thấy.** Các chi tiết nhỏ (6 lưỡi sáng bo tròn ở đáy cột, A2 bản đầu) làm rối và không đẹp: bỏ hoặc thay bằng lớp rộng.
- Cấu trúc tham chiếu từ levelup của hero_malik: cột sáng bao thân (mọc từ chân lên), dải sáng cao trên đầu mờ dần lên trên, quầng sáng ấm dưới chân, viền sáng mảnh, rồi thân sạch giữ pose. Nhịp: hiện cùng lúc cú đấm lên đỉnh, đầy, mờ dần, kết thúc trước khi clip hết.
- Nhịp ăn khớp động tác: chớp/bùng ở frame nắm đấm lên đỉnh (frame ~22 của clip 46 frame).
- Giữ fx trong canvas; cú đấm đã sát mép trên khung nên dải sáng trên đầu mờ dần chứ không dừng gắt.

**Trạng thái**: 10 phiên bản Python của levelup (`fx/levelup_variants.py`, v01-v10). User chọn **v03** (mục bên dưới); v02 và v04 không đẹp (bỏ), các bản còn lại "cực đẹp" và giữ làm kho ý tưởng. Bản A1 (`fx/levelup.json` qua `fx_layers`) bị loại vì thô. **Công thức làm từng bước, bộ công cụ và các lỗi đã gặp: `docs/python-fx-recipe.md`.**

## Levelup fx v03, "hào quang xung nhịp" (chốt 2026-10-20)

**Chọn**: user xem 10 phiên bản Python và chọn v03 là đẹp nhất cho levelup của holy_commander ("cực kỳ đẹp, đẹp nhất"). Chi phí fx: 0 USD.

**Ý tưởng**: ba đợt hào quang ánh sáng lan ra từ chính hình người (không phải hình hộp hay vòng chồng lên), lúc nắm đấm lên trời; ánh sáng viền ngay mép thân, chớp trắng ở nắm đấm, quầng sáng ấm dưới chân. Hợp ý user: "ánh sáng chớp quanh người theo nhịp vung tay".

**Thân (clip A)**: `raw/levelup_side_extra_v2_t01.mp4`, 3 s, tách 15 fps = 46 hình; đứng, hạ người, đấm lên trời (đỉnh ở **frame 22**), giữ pose. Ảnh đầu master_v07, ảnh cuối `pose_levelup_v02`.

**Số đo dùng để đặt fx** (trong khung clip 832x480): chân `(370, 453)`, chiều cao thân `425 px`, nắm đấm ở đỉnh lệch `-0.08` chiều cao thân so với chân và cao `~0.93-0.95`. Canvas vẽ 700x720, chân tại `(350, 630)`.

**Các lớp, theo thứ tự** (hàm `V03` trong `fx/levelup_variants.py`; `e = env(i, 18, 24, 32, 41)`: hiện từ frame 18, đầy ở 24, giữ tới 32, tắt ở 41):
| Lớp | Vị trí so với thân | Màu | Chế độ | Độ đục | Chi tiết |
|---|---|---|---|---|---|
| Quầng sáng dưới chân `ground(e, 0.9, 0.55)` | sau | vàng (255,201,60) | screen | 0.85 x 0.9 x e | elip rộng 0.55 chiều cao thân mỗi bên, dẹt 0.1 |
| Đợt 1 hào quang | sau | vàng | screen | 0.85 x (1-t)^1.2 | bắt đầu frame 19, dài 13 frame; `aura(grow = 4 + 56 t^0.7, blur = 8 + 12 t)` |
| Đợt 2 hào quang | sau | kem (255,244,200) | screen | như trên | bắt đầu frame 23 |
| Đợt 3 hào quang | sau | hổ phách (255,158,38) | screen | như trên | bắt đầu frame 27 |
| Hào quang nền `aura(8, 12)` | sau | vàng | screen | 0.45 x e | luôn có khi `e > 0` |
| Viền sáng trong thân `rimlight(sil, 1.0)` | trước | kem | screen | 0.8 x e | mép trong của hình bóng thân |
| Chớp ở nắm đấm `flash_fist(t = 22, k = 0.7)` | trước | trắng (255,255,240) | screen | 0.7 x (1 - abs(i-22)/4) | bán kính 0.42 chiều cao thân tại nắm đấm; tắt trong ±4 frame |

`t` của mỗi đợt = `ramp(i, s, s+13)`; đợt chỉ vẽ khi `0 < t < 1`. `aura()`: blur hình bóng thân sigma `grow*0.75`, nhân 2.6 rồi cắt 0..1, blur thêm `blur` (xem lý do trong `docs/python-fx-recipe.md` mục 5: bản đầu nở bằng bộ lọc vuông ra hào quang vuông).

**Lệnh dựng lại**:
```
python out/heroes/holy_commander/fx/levelup_variants.py out/heroes/holy_commander/raw/levelup_side_extra_v2_t01.mp4 <thư_mục_ra> v03
```
Ra frame PNG đủ 46 hình, `v03.mp4` xem thử, `v03_peak.png`.

**Việc còn lại trước khi export** (chưa làm): quyết định cách xuất lớp trong suốt (screen trên nền tối khác nền sáng; kiểm tra trên nền sáng), kiểm tra fx vừa canvas 176x140, rồi export `levelup_side` (body 111@2x, pivot (0.5, 0.88)). Không cắt frame.

**Quy tắc cho fx của hero này về sau** (từ các góp ý của user): lớp bao quanh thân bằng màu và độ trong suốt, mép mềm; lớp rộng, dễ thấy, không chi tiết nhỏ làm rối; không viền nét, không vector phẳng chồng lên thân. Python trước; gen video + cắt frame chỉ khi fx cần chi tiết mà Python không làm được.
