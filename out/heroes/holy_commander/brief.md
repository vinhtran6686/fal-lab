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
| attack_side | video-sprite | one-shot | ✅ exported | 18 hình theo công thức user (1,20 s), hit 10, canvas 176x140 |
| death_side | video-sprite | one-shot | ✅ exported | 32 hình theo công thức user (2,13 s) |
| respawn_side | video-sprite | one-shot | ✅ exported (chờ user duyệt clip) | `rise` t01, 30 hình, 2,00 s, cỡ thân đo theo hình cuối (đứng) để khớp idle (`--rest-last`). Chưa có fx_respawn |
| levelup_side | video-sprite | one-shot | ✅ exported | 27 hình, 1,80 s, hit 13; fx `fx/levelup` (v03) xuất thành lớp riêng back/front |
| skill_holy_banner_side | video-sprite | one-shot | ✅ exported | 39 hình, 2,60 s, hit 18; take chốt `v4_t02` (ripple do model vẽ nằm trong frame) |
| skill_radiant_slash_side | video-sprite | one-shot | ✅ exported | 43 hình, 2,87 s, hit 27; thân sạch `v2_t01` + fx `fx/radiant_slash` (tia Python) lớp riêng |
| skill_charge_side | video-sprite | one-shot | ✅ exported (v4) | 34 hình theo công thức user (2,27 s); vòng lửa lớn là lỗi đã biết |
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
- Dùng làm ảnh đầu của `rise` (ảnh cuối `master_v07`, take t01): hero giữ nguyên kích thước suốt clip, màu hồi từ vàng rồi tới đỏ, đứng lên đúng tư thế master, không có vật thể lạ (đánh giá của mình khi xem frame; clip `rise` vẫn chờ user duyệt).
- User duyệt **pose** (ảnh tĩnh): "đẹp, ổn". Clip `rise` t01 chưa được user duyệt.

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

**Đã bị thay thế, đừng dùng lại**: `fx/levelup.json` + `fx/levelup/` (bản A1 qua `fx_layers`, bị chê thô) và `fx/levelup_soft_glow.py` (A2 bản đầu có lưỡi sáng nhỏ ở đáy). Entry `fx` trong `meta.json` đã gỡ vì chưa có asset fx v03 đã export; **thêm entry `fx` cho levelup khi export v03**.

**Quyết định user (2026-10-20): chưa export, chỉ review đầy đủ.** Chuyển động đấm do clip thân A (model sinh) có sẵn; Python chỉ vẽ ánh sáng lên đó và đo clip để đặt fx. Nếu sau này export, việc cần làm: quyết định cách xuất lớp trong suốt (screen trên nền tối khác nền sáng; kiểm tra trên nền sáng), kiểm tra fx vừa canvas 176x140, rồi export `levelup_side` (body 111@2x, pivot (0.5, 0.88)). Không cắt frame.

**Quy tắc cho fx của hero này về sau** (từ các góp ý của user): lớp bao quanh thân bằng màu và độ trong suốt, mép mềm; lớp rộng, dễ thấy, không chi tiết nhỏ làm rối; không viền nét, không vector phẳng chồng lên thân. Python trước; gen video + cắt frame chỉ khi fx cần chi tiết mà Python không làm được.

## Skill 2 holy_banner (chốt 2026-10-20): mô tả hành động rõ ràng là điều quyết định

**Kết quả**: sau 3 vòng quay, user chốt take do model vẽ cả ripple (`raw/skill_side_skill_holy_banner_v4_t02`); user nhận xét "quá đẹp", cả bản model lẫn bản Python (`v4_t01` + `fx/holy_banner_ripple.py`) đều đẹp, model đẹp hơn. Không cắt frame, chưa export. Take chốt vẫn có lỗi nhỏ đã ghi ở `history.md` (khối nón sáng thừa, ripple lan ra mép khung); user vẫn chọn.

**Bài học chính: phải mô tả hành động của nhân vật rõ ràng, cụ thể, không chung chung.**
Cùng một skill, cùng model, cùng giá (0.06 USD/clip), chất lượng đổi hẳn theo độ cụ thể của mô tả hành động:
| Vòng | Mô tả hành động | Kết quả |
|---|---|---|
| 1 | chung chung: "nâng kiếm, cắm xuống, giơ nắm đấm", kèm fx do model vẽ (cờ, ánh sáng) | bị chê: khối nón cam đục phủ hero, cử chỉ thừa (khoanh tay) |
| 2 | thêm mô tả thân, chân, đầu, áo choàng theo từng nhịp, nhưng ý tưởng vẫn do mình nghĩ | nhịp rõ hơn nhưng user vẫn chê "không đẹp" |
| **3** | **user tự viết hành động bằng từng bước vật lý**: đứng như idle, lùi một chân; nâng kiếm hai tay rồi găm mạnh xuống đất; kiếm chìm khoảng một nửa, người khuỵu quỳ một gối, hai tay nắm chặt cán, gồng mạnh | **quá đẹp**, cả bản model và bản Python |

**Khi đã có hành động đủ tốt thì fx Python cũng chạy tốt theo**: video thân rõ nhịp (đo được frame găm kiếm và vị trí mũi kiếm) thì fx đặt chính xác đúng khoảnh khắc va chạm. Fx đẹp chỉ khi thân đúng.

**Công thức mô tả hành động (dùng cho mọi skill còn lại và hero khác)**
1. **Khoá hướng**: "facing RIGHT the entire time and never turning around: his hips, shoulders and face stay turned to the right in every frame". Bắt buộc, nhất là khi có động tác chân ra sau (model đọc "lùi chân" thành xoay người; chỉ cho chân sau trượt lùi).
2. **Tư thế đầu**: nói rõ giống idle (chân, kiếm, tay), đứng yên một nhịp chỉ thở.
3. **Các nhịp đánh số** (Beat 1, 2, 3...): mỗi nhịp một động tác vật lý, nói **bộ phận nào làm gì**: chân (gối, hông, bàn chân, trọng tâm), thân (nghiêng, thẳng, ưỡn ngực), đầu (ngẩng, cúi), tay (từng tay, nắm ở đâu), vũ khí (thẳng đứng, mũi hướng đâu, chìm bao nhiêu), áo choàng (hất rồi rũ).
4. **Nói rõ trạng thái kết thúc** (quỳ một gối, hai tay nắm chặt cán, đầu cúi, gồng) rồi "HOLDS this pose completely still for the rest of the clip".
5. **Câu thứ tự**: "The order is always: stand, step back, lift, drive down while dropping to one knee, hold". Một lần nâng, một lần găm.
6. **Liệt kê điều không được làm**: không đi, không xoay, không đứng lên lại, không cử chỉ khác (không khoanh tay, không chào).
7. **Fx**: hoặc cấm hẳn (clip thân), hoặc cho **đúng một** hiệu ứng, kèm hình dạng, vị trí, thời điểm cụ thể ("thin concentric elliptical rings of pale gold light spreading along the ground from where the sword is buried"). Lần cho hiệu ứng hẹp và đúng mặt phẳng (mặt đất) cho kết quả đẹp hơn lần để model tự sáng tạo ánh sáng.
8. **Không ghim ảnh cuối** khi ảnh cuối chưa đúng tư thế bạn mô tả: ở vòng 3 chỉ dùng ảnh đầu (master), tư thế cuối theo mô tả đã đúng.
9. Câu "locked tripod" như mọi clip.

**Tham chiếu prompt chốt**: `raw/skill_side_skill_holy_banner_v4_t02.prompt.txt` (take chốt) và `v4_t01.prompt.txt` (thân sạch). Phần "Beat 1-5" là mẫu dùng lại.

**Điều model vẫn làm dù đã cấm** (cần dự trù): vệt trắng/hồng bắn ra ở chỗ vũ khí chạm đất; khối nón ánh sáng khi có ripple; nâng vũ khí cao hơn yêu cầu (mũi kiếm chạm mép trên khung); thân xoay nhẹ về camera khi giơ vũ khí. Python xoá được vệt (xem `fx/holy_banner_ripple.py`, hàm `clean`).

## Skill 3 radiant_slash "tia thánh xuyên" (chốt 2026-10-20)

**Kết quả**: user chốt **video 3 = thân sạch (video 1) + tia sáng vẽ bằng Python** ("hiệu ứng từ Python là đẹp nhất"). Chi phí: 2 clip x 0.06 USD (một clip thân + một clip để so với bản model vẽ tia); bản chốt chỉ cần clip thân, fx Python 0 USD. Không cắt frame, chưa export, chưa chạy gate.

**Hành động** (mô tả từng bước, theo công thức ở mục "Skill 2 holy_banner"): khoá hướng nhìn sang phải; đứng idle kiếm cắm đất; rút kiếm bằng hai tay, đưa ngang ngực, mũi chỉ sang phải; gối chùng, hông sụp, hai tay kéo cán sát người, lưỡi vẫn ngang ngực; một bước dài về phía trước bên phải, chân sau thẳng, hai tay đẩy kiếm thẳng ra; giữ pose lao tới. Cấm: xoay, nhảy, vung, cử chỉ khác; chỉ rút một lần, đâm một lần. Không ghim ảnh cuối. Prompt: `raw/skill_side_skill_radiant_slash_v2_t01.prompt.txt` (thân) và `_t02.prompt.txt` (kèm tia).

**Kết quả quay**: mọi nhịp đọc rõ, kích thước ổn định, mũi kiếm trong khung (cách mép phải ~30 px), không có vệt splash. Lỗi nhỏ còn lại: thân hơi xoay về camera khi kéo kiếm sát người; lúc rút kiếm, kiếm vung chéo lên cao hơn mức "ngang ngực".

**Số đo clip** (15 fps, 67 hình, 832x480): rút kiếm hình 6-18; kéo sát người 21-38; đâm 39-43; **duỗi hết ở hình 43**, mũi kiếm tại **(803, 202.5)**; giữ pose tới hết.

**Fx Python (`fx/radiant_slash_beam.py`, canvas 1500x600, khung clip đặt tại (100, 60))**, màu + độ trong suốt, screen blend, `t = i - 43`:
| Lớp | Thời điểm | Chi tiết |
|---|---|---|
| Ánh sáng gom ở mũi kiếm | hình 21-38, tắt 38-41 | vàng, `radial` bán kính 70 + 40 g, độ đục 0.75 g, bám mũi kiếm đo từng hình (điểm phải nhất của hình bóng) |
| Tia sáng ngang | t 0-22 | đi tới mép phải trong 4 hình (`reach`), lõi trắng (sigma 7 px, 1.0), thân vàng (sigma 20 px, 0.85), quầng ngoài hổ phách (sigma 52 px, 0.35), mờ dần theo khoảng cách (^0.5), nhịp phồng +-12%; vào 0-2, ra 12-22 |
| 2 vòng sóng ở mũi kiếm | trễ 0 và 3 hình, dài 14 | vòng tròn (hướng về người xem), bán kính (0.10 + 0.60 u^0.8) x 425, kem rồi vàng |
| Chớp ở mũi kiếm | 6 hình | trắng 110 px + vàng 220x160 |
| 2 đợt hào quang quanh hình bóng (cả kiếm) | trễ 0 và 4, dài 14 | vàng rồi kem, phía sau thân, `aura(grow 4 + 50 u^0.7)` |
Kết thúc sạch (không còn fx) để game về idle.

**Rút ra**
1. Công thức mô tả hành động của holy_banner dùng lại ngay lần đầu cho skill khác và đạt: thân đọc rõ nhịp, không cần quay lại.
2. Mũi kiếm đo **từng hình** từ clip, nên fx bám đúng vũ khí; tia không bắt đầu từ chỗ đoán.
3. Với tia sáng (hình dạng đơn giản, cần mềm và nhiều lớp), Python cho kết quả đẹp hơn model: model thêm vòng không yêu cầu chạy ra mép khung, Python điều khiển được từng lớp. Với ripple trên mặt đất của banner thì user chọn bản model. Cả hai đều dùng được; mỗi skill nên thử cả hai (Python đã miễn phí).
4. Canvas fx phải rộng về phía hướng tia bắn (ở đây sang phải): khung clip đặt lệch trái canvas.

## Bộ assets đã trích xuất (2026-10-21)
Trích xuất hoàn chỉnh theo yêu cầu (repo khác sẽ dùng, không liên quan game ở session này): `EXPORT_README.md` (cho người) và `export_manifest.json` (cho máy) trong thư mục này.
Đủ 10 state (idle, run, attack, death, respawn, levelup, 3 skill, icon), 2 lớp fx tách (levelup, radiant_slash), 7 ảnh tĩnh. Frame theo `export_recipe.json` (công thức user lưu trong Frame Tuner).
Kiểm: `python tools/frame_tuner/build_export_manifest.py` (746 file frame, đúng số lượng, kích thước, alpha, fx khớp thân).
