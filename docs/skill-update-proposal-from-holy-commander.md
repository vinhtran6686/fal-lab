# Đề xuất cập nhật skill `fal-image` và `video-sprite` từ quá trình làm holy_commander

Viết 2026-10-21 từ tài liệu thiết kế của hero (`out/heroes/holy_commander/brief.md`, `history.md`, `docs/holy-commander-report.md`, `docs/python-fx-recipe.md`, `docs/handover-holy-commander-assets.md`)
và từ chính quá trình làm. **Chưa sửa `SKILL.md` hay file nào trong `.claude/skills/`** (user tự sửa, hoặc duyệt từng mục rồi mới áp dụng).
Mục tiêu: lần sau làm một hero (hoặc ally, boss) nhanh hơn, ít retake hơn, ít tốn tiền hơn.

Đề xuất cũ ở `docs/holy-commander-report.md` §5 (các thói quen của model khi chém, quay lưng, ngưỡng thời lượng) vẫn đúng và chưa áp dụng; file này bổ sung và không lặp lại chúng.

## 0. Tóm tắt: 10 điều đáng sửa nhất

| # | Điều rút ra | Skill | Mức |
|---|---|---|---|
| 1 | **Mô tả hành động cụ thể từng bước, theo bộ phận cơ thể** quyết định chất lượng clip. Cùng model, cùng giá: vòng 1-2 (chung chung) bị chê, vòng 3 (user viết từng bước) "quá đẹp" | video-sprite | cao |
| 2 | Chốt mô tả hành động **trước** khi quay clip trả phí (đề xuất 2-3 phương án có nhịp từng giây, rủi ro, giá; user chọn và chỉnh) | cả hai | cao |
| 3 | **Fx: Python trước (0 USD)**, lớp mềm, rộng, màu + độ trong suốt, bao quanh thân; không dùng vector phẳng chồng lên thân | video-sprite, fal-image | cao |
| 4 | Quy tắc style "không glow, không mềm" của `format.md` chỉ áp cho **ảnh tĩnh nhân vật**, không áp cho lớp fx | fal-image | cao |
| 5 | Xuất fx thành **lớp RGBA riêng back/front** khớp từng pixel với thân; đường biến đổi chính xác | video-sprite | cao |
| 6 | Export **từ công thức frame** (`export_recipe.json`) khi `.work` không có trong git; Frame Tuner để user tự tăng giảm frame | video-sprite | cao |
| 7 | Canvas hero tier M **156x140 không đủ** cho vũ khí dài (đòn chém, đâm); dùng 176x140 | fal-image | trung bình |
| 8 | `respawn` mặc định nên là **`rise` từ ảnh quỳ xám** (đã chạy tốt), không phải despawn đảo ngược (bị chê là pho tượng) | cả hai | trung bình |
| 9 | Danh sách thói quen model mới (xoay thân, vũ khí vượt khung, vệt trắng khi chạm đất, fx hẹp vẫn kéo theo vật thừa) | video-sprite | trung bình |
| 10 | `gen_image.py` nhận prompt từ file (`--prompt-file`): mất 0,02 USD vì shell truyền nguyên chuỗi `$(cat ...)` thành prompt | fal-image | thấp |

## 1. Số liệu quá trình (để biết nên tối ưu ở đâu)

| Mục | Con số |
|---|---|
| Ảnh tĩnh | 16 ảnh giữ lại ~0,22 USD (master 7 bản, icon, 3 pose skill cũ, pose respawn x3, pose levelup x2) + vài ảnh nháp bỏ |
| Clip | **26 clip** trong `raw/` ~**1,58 USD** (ước từ sidecar) |
| Tổng ước | **~1,8 USD** cho cả hero; bảng ước tính ban đầu của manifest ~0,75 USD |
| Take mỗi state | run 1, death 1, attack 5 (t01, t03-t06), charge 4 (v1-v4), levelup 3 (1 bị loại + 2), respawn 2 (despawn bị loại + rise), banner 7 clip (1 bị loại + 3 vòng x 2), slash 3 (1 cũ bị loại + 2) |
| Nguyên nhân tốn thêm | thiết kế lại skill sau góp ý (banner 7 clip qua 4 lần quay, charge 4 bản, attack 5 take), mỗi lần quay lại ~0,05-0,08 USD |
| Fx | 0 USD (Python); so sánh 10 phiên bản fx levelup không tốn gì |

Hệ quả: tiền không nằm ở ảnh, mà ở clip quay lại do **mô tả hành động chưa đúng ý user**. Chốt hành động trước khi quay là chỗ tiết kiệm nhất (mục 2).

## 2. `video-sprite`

### V1. Công thức mô tả hành động (thêm vào `references/motion-prompts.md`, mục mới "Writing the action", và trỏ tới từ SKILL.md "Workflow" bước 3)
Bằng chứng: skill banner. Vòng 1 (mô tả chung chung "nâng kiếm, cắm xuống, giơ nắm đấm" kèm fx do model vẽ) ra khối nón cam đục và cử chỉ khoanh tay thừa; vòng 2 (thêm mô tả thân, chân, đầu nhưng ý tưởng do mình nghĩ) vẫn bị chê; vòng 3 (user tự viết ba bước vật lý: đứng như idle và lùi một chân; nâng kiếm hai tay rồi găm mạnh xuống đất; kiếm chìm khoảng một nửa, người khuỵu quỳ một gối, hai tay nắm chặt cán, gồng) cho kết quả "quá đẹp". Skill chém sáng dùng lại công thức ngay lần đầu và đạt.

Nội dung đề xuất (tiếng Anh, để dán vào skill):
> **Writing the action (the biggest lever on quality).** Describe the motion in numbered physical beats, by body part, never in generic verbs. Template:
> 1. **Facing lock**: "facing RIGHT the entire time and never turning around: his hips, shoulders and face stay turned to the right in every frame." Required for any step, backward foot or weapon pull (the model reads "step back" as a turn; let only the back foot slide).
> 2. **Start**: "starts in the calm idle stance of the first still" and say what the feet, sword and hands do, still for a short beat with only a slow breath.
> 3. **Beats**, one action each, in order ("Beat 1, gather", "Beat 2, drive"...). For each name: legs (knees, hips, which foot, where the weight is, "the feet never leave the ground and never slide"), torso (leans FORWARD only, straightens, chest out), head (up, down toward the weapon), arms (each hand, where it grips), the weapon (vertical, level, point direction, how deep), the cape (flicks once, settles).
> 4. **End state** in words (kneeling on one knee, both hands tight on the hilt, head bowed) and "HOLDS this pose completely still for the rest of the clip".
> 5. **Order sentence**: "The order is always: stand, step back, lift, drive down while dropping to one knee, hold."
> 6. **Counts and forbidden gestures**: "the sword is lifted once and driven down once; he does not walk, turn around, stand up again or make any other gesture (no crossing of the arms, no salute)."
> 7. **Effects**: either forbid them for a clean body clip, or allow exactly ONE, with its shape, place and moment ("thin concentric elliptical rings of pale gold light spreading along the ground from where the sword is buried") and "this is the ONLY effect".
> 8. **Do not pin an end still** when the end pose is written in words and the still would be a guess: the written pose matched on the first take (kneel, lunge). Pin one only when the pose is hard to describe.
> 9. Keep the "locked tripod" sentence from the anti-zoom wording.

### V2. Quy trình thiết kế hành động với user (SKILL.md "Workflow", thêm bước 3a trước "Ask before paying")
Bằng chứng: khi mình đề xuất hai phương án có mô tả nhịp từng giây, rủi ro và giá (Cờ hiệu thánh H1-H3, Chém sáng C1-C3), user chọn nhanh và viết lại bước theo ý mình; mô tả do user viết ra kết quả tốt nhất.
Đề xuất: với skill, levelup, respawn, **trước mọi clip trả phí**: (a) hỏi user mô tả bằng lời, hoặc (b) đề xuất 2-3 phương án, mỗi phương án 4-6 nhịp theo bộ phận cơ thể (mẫu ở V1), pose cuối, fx dự kiến (Python), rủi ro với model, giá; có khuyến nghị; hỏi 3 câu (chọn hướng, chỉnh nhịp, thời lượng). Chỉ quay khi user duyệt mô tả.

### V3. Quy ước fx (sửa mục "Body clips and effect layers")
Bằng chứng: bản A1 (fx_layers vòng/cột/bùng nổ phẳng chồng lên hero) bị user chê "thô, xấu, đè lên nhân vật"; bản mềm bao quanh thân bằng màu và độ trong suốt (v03) được chọn "đẹp nhất". Hero tham chiếu cũng làm levelup bằng cột sáng trong suốt bao thân (đã đối chiếu 23 frame). Banner: bản model vẽ ripple được user chọn dù có khối nón thừa; slash: bản Python tia sáng được chọn.
Đề xuất:
- Clip thân vẫn **sạch** là mặc định. Fx **Python trước** (`out/<class>/<id>/fx/*.py` kiểu `levelup_variants.py`, 0 USD, làm nhiều phiên bản cho user chọn), vì điều khiển được từng lớp và không làm thân bị zoom, vòng.
- Lớp fx **mềm, rộng, bao quanh thân**: màu và độ trong suốt, mép blur, đậm ở chân nhạt dần lên đầu, hào quang bám theo hình người, vòng lan trên mặt đất, tia dọc theo vũ khí. Tránh hạt nhỏ và lưỡi sáng nhỏ làm rối (bị chê ở bản A2 đầu).
- `fx_layers.py` (vector phẳng) giữ cho các vật nhỏ có hình (sprite, đạn), không dùng cho hào quang, cột sáng, tia.
- Cho phép một take có fx do model vẽ **chỉ khi rẻ và user muốn so** (một clip ~0,06 USD): mô tả đúng một fx hẹp (V1 mục 7); chấp nhận rủi ro vật thừa; ghi cả hai bản để user chọn.
- Đề xuất cho SKILL.md: sửa câu "Takes with painted glows, rings, starbursts ... are retaken, never kept" thành "painted fx are allowed when the user prefers that take".

### V4. Xuất fx thành lớp riêng, khớp thân (thêm vào "Export" hoặc mục mới "Effect layers export")
Bằng chứng: `tools/frame_tuner/export_fx.py`; thân và fx qua cùng chuỗi biến đổi (thang `120/chiều cao thân` hoặc 268 với clip cũ, đặt chân tại (256, 400) trên khung 512, nhân `body_rescale`, đặt vào pivot, kể cả làm tròn): IoU thân đặt lại so với frame đã export 0,985-0,993 (xấp xỉ bằng một hệ số chỉ cho 0,957, lệch 1 pixel).
- Lưu fx dạng RGBA: màu = màu ánh sáng, alpha = cường độ (kênh lớn nhất), alpha thẳng; hai lớp `back` (sau thân) và `front` (trước thân); số hình bằng số hình thân; `fx.json` có pivot.
- Pha trộn tốt nhất bằng screen hoặc additive; alpha-over vẫn dùng được nhưng tối hơn.
- Canvas fx cắt theo phần fx thật sự có (tia dài hơn ô hero); đừng cắt theo ô hero.
- Làm kèm `preview_fx_only.gif`, `preview_with_body.gif`, `sheet.png` và `<state>/preview_with_fx.gif`: nếu không có preview, user không thấy fx ở thư mục state (xảy ra thật, đã sửa).
- Đo nhịp từ clip: chuỗi `bbox.top` theo từng frame và vị trí điểm phải nhất của hình bóng cho biết hình va chạm, hình duỗi hết, vị trí mũi vũ khí (dùng để đặt fx đúng nhịp).

### V5. Export từ công thức frame và Frame Tuner (sửa mục "Tools", "Timing defaults", "Where things are")
Bằng chứng: `docs/issue-frame-recipe-sync.md`; `.work/` không có trong git nên phiên cloud phải dựng lại set; bản cũ dùng `retime --auto-oneshot` nén attack về ~0,7 s trái bản user đã duyệt (23 hình). Công thức do user chỉnh bằng Frame Tuner (bật/tắt hình, thời gian từng hình, hit) lưu trong `export_recipe.json`; `apply_recipe.py --write` export lại; **công thức mặc định tái lập đúng bản đã chốt trùng từng pixel** (attack 23/23, death 39/39, charge 67/67).
Đề xuất:
- Thêm bước "frame review" sau accept: user dùng Frame Tuner (cục bộ `.bat` hoặc artifact) để chọn frame; công thức lưu cạnh asset.
- Route export khi không có `.work`: clip trong `raw/` -> `ffmpeg fps=15` -> `key_out` -> thang -> `video_to_sheet.py`, thay vì dựng lại set bằng `sprite_set.py`.
- `hit_frame` trong `meta.json` tính từ 1; trong công thức `hit` là chỉ số 0 trong danh sách hình giữ.
- Cờ `--rest-last` (đã thêm vào `video_to_sheet.py`): đo cỡ thân theo hình **cuối** khi clip kết thúc ở tư thế master (respawn `rise`); trước đó hình đứng cuối nhỏ hơn idle 4%.
- Ghi chú: `body_height_2x` trong `meta.json` đo từ run (tư thế hơi cúi) nên thấp hơn idle (111 so với 131 px @2x với cùng thân); dùng diện tích (`body_area_2x`) để khớp, đừng so chiều cao.

### V6. Thói quen model bổ sung (mở rộng "Retake translation" điểm 6 và "Known limits", cùng với đề xuất cũ §5)
Bằng chứng ở `history.md` (dòng banner, slash, levelup):
- "Lùi chân" bị đọc thành xoay người: thêm câu khoá hướng (V1 mục 1) và chỉ cho chân sau trượt.
- Thân hơi xoay về camera khi nâng hoặc kéo vũ khí (banner, slash): xuất hiện cả khi đã khoá hướng; chấp nhận hoặc retake nếu user thấy rõ.
- Vũ khí giơ cao vượt mép trên khung (mũi kiếm chạm `bbox.top = 0` khoảng 9 hình ở banner): mô tả "never rises above his head" hoặc kiểm `bbox.top` rồi báo user.
- Kiếm chạm đất vẽ ra vệt trắng hoặc hồng bắn ra **dù cấm rõ** (banner, vòng 2 và 3): Python xoá được (vùng bên phải kiếm, dưới đường chân) hoặc chấp nhận.
- Cho phép đúng một fx hẹp vẫn kéo theo vật thừa: ripple dưới đất kéo theo khối nón sáng phủ hero; tia kiếm kéo theo vòng sáng lớn chạy ra mép khung; fx cũng làm gate `area`, `feet` đọc sai.
- Mô tả màu hồi dần (xám sang màu) model làm mượt, không cần hậu kỳ: dùng nguyên văn "the colour comes back gradually, spreading over the whole body".
- Khi không ghim ảnh cuối và mô tả pose cuối bằng lời: model khớp ngay (quỳ, đâm thẳng).
- Thời lượng đã dùng: 3 s cho levelup (đủ), 4 s cho skill nhiều nhịp; giá `h3-max-turbo` 480P: 3 s ~0,045 USD, 4 s ~0,06 USD, 5 s ~0,08 USD (SKILL.md chỉ ghi 5 s).

### V7. Mẫu action template (sửa `references/motion-prompts.md`)
- `levelup` (đấm lên trời, giữ pose) và `skill` (cắm kiếm quỳ gối; đâm thẳng) nên có bản mẫu dùng công thức V1 làm ví dụ (prompt thật nằm ở `raw/*.prompt.txt` của hero).
- `rise` đổi nhãn từ "untested alternative" thành **tested, đạt** (holy_commander, respawn quỳ xám -> đứng). Mẫu: ảnh đầu = `pose_respawn` (quỳ xám), ảnh cuối = master, nhịp "quỳ xám giữ một nhịp -> màu hồi -> ngẩng đầu -> chống kiếm đứng -> giữ".
- `despawn` (đảo ngược) vẫn chạy kỹ thuật nhưng user chê "pho tượng cứng nhắc": đưa xuống làm phương án phụ.

### V8. Duyệt và báo cáo (sửa "Run modes")
Bằng chứng: user không có máy local, chỉ xem qua artifact; mỗi take cần artifact riêng (clip, sheet key pose, nhận xét thật); gate không phát hiện được fx vẽ trong clip (đọc `qc.json` không đủ).
- Mặc định đăng một artifact cho mỗi vòng quay: video raw, sheet 10-12 hình, nhận xét thẳng (ưu, nhược, so với mô tả), giá; không chỉ dựa vào gate.
- Sau khi chốt: một trang tổng quan mọi state (pose, key pose, video, trạng thái) để user duyệt cả bộ.

## 3. `fal-image`

### F1. Quy tắc style chỉ cho ảnh tĩnh (sửa `format.md` §1, bảng "May set / Never" và đoạn "Effects")
Bằng chứng: style hiện cấm "gradient, soft glow, blur, aura" cho **mọi** tài sản; nhưng fx do game vẽ như lớp riêng (hero tham chiếu có cột sáng trong suốt khi levelup) và bản mềm được user chọn.
Đề xuất: ghi rõ "These bans apply to the character STILLS drawn by the image model. Effect layers (separate assets, drawn in code) may be soft, translucent light layers with feathered edges, in colour and opacity." Giữ nguyên cấm "aura, rim light" trong ảnh tĩnh.

### F2. Canvas hero tier M (sửa `classes/hero.md` §3 và `format.md` §7)
Bằng chứng: canvas 156x140 không chứa được đòn chém attack; toàn bộ asset phải đệm lại thành **176x140**; về sau đâm thẳng của slash dài ~2,3 lần thân. Đề xuất: hero M canvas **176x140** (@2x 352x280) mặc định cho hero cầm vũ khí dài; hoặc quy tắc "đo tầm với ngang lớn nhất của hành động trước lần export đầu và chọn canvas theo đó" (export đầu quyết định canvas cho cả hero, `meta.json`). Fx dài hơn ô (tia) là lớp riêng, không bắt canvas thân to hơn.

### F3. Ảnh pose và manifest (sửa `classes/hero.md` §5, §6)
- Thêm hàng ảnh `pose_respawn` (quỳ, gục đầu vào kiếm, xám) và `pose_levelup` (đỉnh cú đấm) khi hero dùng thiết kế đó.
- Hàng `pose_skill_<name>` đánh dấu **tuỳ chọn (⏭)** khi user mô tả pose cuối bằng lời: banner v4 và slash v2 chạy từ master không ảnh cuối và khớp mô tả; pose cũ (`pose_skill_holy_banner_v01`) từng bị thay cả thiết kế.
- Hàng `respawn_side`: "rise từ pose_respawn (đã chạy tốt)" thay cho "despawn đảo ngược" làm mặc định; `fx_respawn`, `fx_levelup`, `fx_<skill>` trỏ tới fx Python (`out/<class>/<id>/fx/`).
- Thêm hàng đóng gói cuối: `ui/icon` (`sprite_pack.py ... --state icon`), `export_manifest.json`, `EXPORT_README.md`. Hiện icon chỉ được pack khi nhớ làm.

### F4. Vòng lặp master cho hero cầm vũ khí lớn (thêm vào `classes/hero.md` §9 và `format.md` §2)
Bằng chứng: master mất 7 bản (v01-v07), mỗi bản sửa đúng một điểm; v05 bị loại vì một tay không thấy, mũi kiếm tụt dưới đường chân, báng bị che.
Đề xuất mục kiểm cho vũ khí dài: (a) nói kích thước vũ khí **so với thân** ("blade as tall as from the ground to his chest", "whole sword above the waist"); (b) hai chân giang rộng trên một đường đất, mũi kiếm trong khung ở idle và ở mọi pose; (c) báng và hai tay thấy rõ; (d) mỗi vòng dùng `--ref <bản trước>` kèm "giữ X, đổi Y"; (e) quay 3 ảnh trong một lệnh (`--n 3`, ~0,04 USD) rồi chọn, thay vì từng ảnh.

### F5. Ảnh trạng thái đổi màu (thêm vào `format.md` §3 hoặc `templates.md`, ví dụ pose xám)
Bằng chứng: `pose_respawn` ra xám sạch ở cả 3 ảnh nháp ngay lần đầu. Câu hiệu quả: "THE WHOLE HERO IS DESATURATED GREY: every part ... is drawn in flat shades of cool grey (light, mid and dark grey only), with no red, no gold and no colour anywhere on the subject; outlines stay near-black", và thay "Do not use magenta or pink on the subject" bằng "the subject has no colour at all, only grey".

### F6. Chạy generator với prompt dài (sửa "Running the generator")
Bằng chứng: 2 ảnh hỏng (~0,02 USD): lệnh `gen_image.py "\$(cat file)"` gửi nguyên chuỗi lệnh làm prompt, model vẽ một thẻ nhân vật. Đề xuất: thêm `--prompt-file`; và bước "mở `.json` sidecar, xem 60 ký tự đầu của `prompt` sau ảnh đầu tiên của mỗi lệnh mới".

### F7. Chế độ `--creative` cho skill và hành động (thêm vào "Creative mode")
Bằng chứng: kiểu "đề xuất 3 phương án, mỗi phương án nhịp + rủi ro + giá, khuyến nghị, hỏi 3 câu" hoạt động tốt cho skill 2 và 3. Đề xuất bước 6 cho `--creative`: sau khi nhân vật chốt, mỗi skill được đề xuất 2-3 phương án hành động theo mẫu V1/V2.

### F8. Ghi lý do chọn (sửa `format.md` §4 hoặc `brief.md` mẫu)
Bằng chứng: user yêu cầu ghi "vì sao chọn v02 và vì sao ổn" vào tài liệu thiết kế. Đề xuất: mỗi ảnh được duyệt có mục ngắn "Cách tạo", "Vì sao chọn", "Vì sao ổn (đã kiểm bằng gì)" trong `brief.md`, kèm lệnh hoặc prompt dựng lại.

## 4. Công cụ nên đưa vào dự án chính thức (hiện nằm ở `tools/frame_tuner/`)
| Công cụ | Việc | Đề xuất |
|---|---|---|
| `frame_tuner` (`index.html`, `serve.py`, `.bat`, `build_artifact.py`) | chỉnh frame, lưu công thức | dời hoặc trỏ từ `scripts/`; ghi vào SKILL.md "Tools" |
| `apply_recipe.py` | export thân từ công thức | như trên; hiện gắn `sources.json` của holy_commander, cần tổng quát hoá theo asset |
| `export_fx.py`, `preview_fx.py` | fx thành lớp riêng và preview | như trên |
| `build_export_manifest.py` | manifest và kiểm gói | như trên; mô tả các state đang viết cứng cho holy_commander |
| `fx/*.py` (levelup_variants, holy_banner_ripple, radiant_slash_beam) | fx Python | mẫu để copy cho hero khác (`docs/python-fx-recipe.md`) |
| `scripts/video_to_sheet.py --rest-last` | cỡ thân theo hình cuối | đã thêm; ghi vào bảng "Tools" |

## 5. Gợi ý thứ tự áp dụng
1. V1 và V2 (công thức mô tả hành động, thiết kế hành động trước khi quay): tiết kiệm nhiều tiền nhất, sửa văn bản, không cần code.
2. F1, V3 (quy ước fx) vì hai chỗ đang mâu thuẫn nhau trong skill.
3. F2, F3 (canvas và manifest) trước khi làm hero tiếp theo, để khỏi làm lại canvas.
4. V5 và V4 cùng Frame Tuner: đưa công cụ vào `scripts/` rồi sửa SKILL.md.
5. V6 và đề xuất cũ §5, F4 đến F8: làm sau, cùng một lượt sửa tài liệu.

Việc cần user quyết trước khi sửa skill: (1) blend của fx khi xuất (alpha thường hay cộng sáng, dùng để viết chuẩn mục V4); (2) có chuyển công cụ vào `scripts/` không; (3) canvas M mặc định 176x140 hay giữ 156x140 kèm quy tắc đo.
