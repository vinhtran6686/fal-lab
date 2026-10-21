# Đề xuất cập nhật skill `fal-image` và `video-sprite` (bản 2, theo phản hồi của user)

Viết 2026-10-21 từ tài liệu thiết kế holy_commander (`out/heroes/holy_commander/brief.md`, `history.md`, `docs/holy-commander-report.md`, `docs/python-fx-recipe.md`,
`docs/handover-holy-commander-assets.md`) và từ ba clip thử mới (`out/heroes/holy_commander/experiments/`).
**Chưa sửa `SKILL.md` hay file nào trong `.claude/skills/`.** Bản này thay bản 1: user góp ý rằng skill **không được đóng khuôn vào một hero**; holy_commander chỉ là
**tham khảo** để chuyển động mượt. Vì vậy mọi mục dưới đây viết thành nguyên tắc chung (chỗ trống như `{vũ khí}`), còn ví dụ cụ thể đặt vào `--example`/`references/`.
Đề xuất cũ ở `docs/holy-commander-report.md` §5 (chém, lùi, ngưỡng thời lượng) vẫn đúng nhưng nay thuộc "thư viện gợi ý" (mục V3).

## 0. Cách sắp xếp lại

| Lớp | Là gì | Đặt ở đâu |
|---|---|---|
| Nguyên tắc chung | quy tắc đúng với mọi nhân vật (mô tả hành động, thời lượng, fx, export) | `SKILL.md` và `references/` |
| Ví dụ tham khảo | hành động và prompt thật của holy_commander | `--example` của skill (`examples.md`), không đưa vào quy tắc |
| Thư viện gợi ý chuyển động | "tình huống nào model hay làm gì, nên mô tả thế nào" | chỉ dùng ở `--creative`, `--example` và lúc skill **bổ sung mô tả của user**, không ép lên nhân vật |

## 1. `video-sprite`

### V1. Mô tả chuyển động thật kỹ (nguyên tắc trung tâm)
Chuyển động càng được mô tả kỹ theo từng bộ phận cơ thể thì nhân vật càng chuyển động đúng ý. Bằng chứng: cùng model, cùng giá, vòng 1-2 (chung chung) bị chê, vòng 3 (user viết từng bước vật lý) "quá đẹp"; skill kế tiếp dùng lại cách viết này, đạt ngay lần đầu.
Công thức chung (chỗ trống thay cho chi tiết của nhân vật, để dán vào `references/motion-prompts.md`, mục "Writing the action"):
> 1. **Facing lock**: "facing {RIGHT} the entire time and never turning around: hips, shoulders and face stay turned that way in every frame". Bắt buộc khi có bước chân, chân sau, hoặc kéo vật cầm.
> 2. **Start**: "starts in the calm idle stance of the first still" kèm chân, vật cầm, tay làm gì; đứng yên một nhịp, chỉ thở.
> 3. **Beats** đánh số, mỗi nhịp một động tác, nêu **bộ phận nào làm gì**: chân (gối, hông, bàn chân nào, trọng tâm), thân (nghiêng về phía TRƯỚC, thẳng lên, ưỡn ngực), đầu (ngẩng, cúi), tay (từng tay, nắm ở đâu), vật cầm ({vũ khí/gậy/...}: hướng, độ sâu, độ cao), áo choàng hay vật mềm (hất rồi rũ).
> 4. **End state** bằng lời (đang ở tư thế nào) rồi "HOLDS that pose completely still for the rest of the clip".
> 5. **Câu thứ tự**: "The order is always: {beat 1}, {beat 2}, ... , hold".
> 6. **Số lần và điều cấm**: "{vật cầm} is {lifted} once; he does not walk, turn around or make any other gesture."
> 7. **Fx**: hoặc cấm hẳn (clip thân sạch), hoặc cho đúng MỘT fx, nêu hình, chỗ, lúc ("this is the ONLY effect").
> 8. **Ảnh cuối**: chỉ ghim ảnh cuối khi tư thế khó mô tả; khi pose cuối đã mô tả bằng lời thì không ghim (model khớp ngay).
> 9. Giữ câu "locked tripod" chống zoom.

### V2. Thời lượng quyết định số chuyển động
Một clip yêu cầu ngắn hay dài quyết định model sinh ra bao nhiêu chuyển động. Số liệu từ các take đã quay (cần kiểm lại ở hero khác):
| Take | Số nhịp yêu cầu | Thời lượng | Kết quả |
|---|---|---|---|
| attack t04 | 2 nhát chém + lấy đà | 3 s | đủ 2 nhát |
| attack t05, t06 | 2 nhát chém | 2 s | gộp thành 1 nhát, dù prompt ép "đúng hai nhát" |
| levelup | 3 nhịp (đứng, hạ người, đấm, giữ) | 3 s | đủ |
| banner, slash | 4-5 nhịp | 4 s | đủ |
| death | 1 hành động liền | 5 s | đọc chậm, phải bớt frame |
Quy tắc đề xuất cho skill: **ước khoảng 0,7-1 s cho mỗi nhịp riêng biệt cộng khoảng 1 s giữ pose cuối, giới hạn 3-5 s**; thêm nhịp thì phải tăng thời lượng; ngắn hơn mức cần thì model **bỏ nhịp** chứ không chạy nhanh hơn; dài quá (5 s) dễ chậm và trôi. Model còn **chia thời gian không đều** giữa các nhịp (respawn: nhịp xám chỉ ~0,5 s trên 4,5 s): muốn nhịp nào dài hơn thì nói trong prompt. Skill nên tự tính thời lượng gợi ý từ số nhịp và báo user.

### V3. Thư viện gợi ý chuyển động (theo tình huống, không theo hero)
Dùng khi `--creative`, `--example` đề xuất chuyển động, và khi skill nhận mô tả của user rồi bổ sung cho chặt chẽ. **Ghi rõ nguồn kiểm chứng: hiện chỉ có hero cầm vũ khí lớn; các class khác (ví dụ pháp sư niệm phép, nhân vật bay) chưa có dữ liệu, không khẳng định.**
Hai nhóm:
- **Chất lượng chuyển động làm hoạt ảnh sinh động** (user đề xuất): gồng và run khi nắm chặt hoặc giữ vật nặng; mất thăng bằng khi tụ lực cho chưởng hoặc tung skill (rồi lấy lại); chuẩn bị trước khi đánh; theo đà sau cú đánh; chùng gối khi va chạm; áo choàng hất rồi rũ.
- **Thói quen model theo tình huống:**
  | Tình huống | Điều hay xảy ra | Cách mô tả |
  |---|---|---|
  | bước hoặc lùi một chân | model đọc thành xoay người | khoá hướng (V1.1), chỉ cho chân đó trượt |
  | nghiêng về sau ("dồn lui") | model xoay cả người | chỉ mô tả nghiêng, dồn về TRƯỚC |
  | giơ vật cầm cao | vật vượt mép trên khung | nói "never rises above the head" hoặc kiểm `bbox.top` |
  | vật cầm chạm đất hoặc vung mạnh | model vẽ vệt hoặc tia bắn dù cấm | chấp nhận, hoặc xoá bằng hậu kỳ (Python) |
  | cho phép đúng một fx hẹp | model thêm vật thừa (khối nón, vòng sáng) | để fx làm bằng Python, hoặc chấp nhận |
  | kéo hoặc nâng vật cầm | thân xoay nhẹ về camera | chấp nhận, hoặc retake nếu user thấy rõ |
  | cần pha màu (xám sang màu) | model làm mượt | dùng nguyên "colour comes back gradually", không cần hậu kỳ |
  | thời lượng quá ngắn cho số nhịp | model bỏ nhịp | tăng thời lượng (V2) |
  | vật rung hoặc run | xem kết quả thử bên dưới | |

**Kết quả quay thử các chất lượng chuyển động (2026-10-21, `out/heroes/holy_commander/experiments/`):**
- **Gồng run** (`test_strain`): model dựng được **tư thế gồng** (nghiêng về trước, vai khom, cúi đầu, siết tay) và có **run rất nhỏ**: dao động dọc khoảng 0,7 px (std, trên khổ clip 480P, thân ~432 px) trong nhịp gồng so với 0,01 px khi giữ yên. Ở cỡ game (thân ~65 px) nhỏ hơn 0,2 px: **không nhìn thấy**. Muốn run rõ phải **phóng đại trong prompt** ("violently", "large shaking movements") hoặc **thêm run ở hậu kỳ** (offset vài pixel mỗi frame bằng Python, trong tuner hay lúc export). Chưa thử cách phóng đại.
- **Mất thăng bằng** (`test_offbalance`): model dựng cú vung lớn với thân chồm, hai tay vung ra, một chân dài ra phía trước rồi ổn định lại ở thế thấp; **không phải "vấp bước" đúng nghĩa đen** nhưng đọc được là cú vung quá đà. Có vệt chém nhạt quen thuộc.
- **Độ phân giải** (`test_1080p_slash_body`): xem V6.

### V4. Quy trình: mô tả kỹ trước, chốt, rồi mới quay (SKILL.md "Workflow", thêm bước trước "Ask before paying")
1. **Mô tả chuyển động thật kỹ** (V1): user viết bằng lời, hoặc skill đề xuất 2-3 phương án (mỗi cái 4-6 nhịp theo bộ phận cơ thể, fx dự kiến, rủi ro, giá, khuyến nghị), có bổ sung chất lượng chuyển động (V3) cho chặt chẽ.
2. **Tính thời lượng** theo số nhịp (V2).
3. **User chốt** mô tả.
4. Mới quay (báo giá, chờ ok).
Bằng chứng: tiền tốn ở clip quay lại do mô tả chưa đúng ý (cả hero ~1,8 USD so với ước tính ban đầu ~0,75 USD).

### V5. Quy ước fx
Bản A1 (vector phẳng chồng lên thân) bị user chê thô; bản mềm bao quanh thân bằng màu và độ trong suốt được chọn; hero tham chiếu cũng làm levelup bằng cột sáng trong suốt.
- Clip thân **sạch** là mặc định; fx **Python trước** (0 USD, làm nhiều phiên bản cho user chọn); lớp mềm, rộng, bao quanh thân, tránh hạt nhỏ làm rối.
- `fx_layers.py` (vector phẳng) giữ cho vật nhỏ có hình (sprite, đạn).
- Cho phép một take fx do model vẽ khi rẻ và user muốn so (một fx hẹp, V1.7); ghi cả hai bản.
- Sửa câu "painted fx are retaken, never kept" thành "allowed when the user prefers that take".
- Xuất fx thành lớp RGBA `back`/`front` khớp từng pixel với thân (đường biến đổi chính xác của thân; IoU 0,985-0,993), kèm preview gif và sheet, vì thiếu preview thì user không thấy fx (xảy ra thật). Đo nhịp bằng chuỗi `bbox.top` và điểm phải nhất của hình bóng.

### V6. Clip phải thật chuẩn vì Frame Tuner chỉ chọn trong các frame đã render
Tuner (user chọn frame mượt nhất) không sửa được hình mờ, lệch cỡ hay nhấp nháy, nên chất lượng clip render quyết định giới hạn của kết quả.
- **Kiểm clip trước khi đưa vào tuner:** frame sắc nét, cỡ thân ổn định (locked tripod), không nhấp nháy, giữ hướng, không vật thừa che thân.
- **Nguồn frame 24 fps** (clip render ở 24 fps): tuner đã có công tắc "Nguồn frame 15/24 fps"; 24 fps cho khoảng 1,6 lần số hình để chọn; lựa chọn được chuyển theo thời gian khi đổi nguồn; công thức lưu `fps` của nguồn và `apply_recipe`, `export_fx` đọc `fps` đó (fx dùng thời gian 15 fps nên được ánh xạ theo 15/fps). Đã kiểm: công thức 15 fps vẫn ra đúng bản đã export (18/18 frame trùng), công thức 24 fps chạy trọn vẹn (thân và fx).
- **Độ phân giải clip** (`test_1080p_slash_body`, cùng prompt và ảnh đầu với take slash 480P): 1080P hoạt động (1920x1080, 24 fps, 107 hình như 480P); **cùng chuỗi chuyển động** với bản 480P (model gần như tất định với cùng prompt); **sắc hơn rõ** (khe mắt, viền visor), số pixel viền bán trong suốt khi key giảm còn khoảng một nửa (570 so với 1150 ở cùng cỡ thân); giá theo bảng của `fal_video.py models` là **0,015 USD/giây cho cả 480P, 768P, 1080P** (ước tính của tool; hoá đơn thực của fal chưa kiểm). Đánh đổi: tạo lâu hơn (~5,3 s so với ~3 s), file mp4 lớn hơn ~5 lần (6,9 MB so với ~1,4 MB), `key_out` bằng vòng lặp Python chậm hơn nhiều ở khổ lớn (nên tối ưu bằng numpy nếu dùng 1080P thường xuyên). Đề xuất: **dùng 1080P cho clip sẽ vào tuner/export** (hoặc ít nhất thử), 480P cho thử ý tưởng.
- Bước export: công thức frame (`export_recipe.json`) thay cho `retime --auto-oneshot`; `apply_recipe.py --write`; cờ `--rest-last` cho clip kết thúc ở tư thế master; `hit_frame` tính từ 1.

### V7. Mẫu action template (`references/motion-prompts.md`)
- `levelup`, `skill`, `rise`: thêm mẫu theo công thức V1 (prompt thật của hero nằm ở `raw/*.prompt.txt`, dùng làm ví dụ ở `--example`).
- `rise` đổi nhãn "untested alternative" thành **tested, đạt**; `despawn` đảo ngược xuống làm phương án phụ (user chê "pho tượng cứng nhắc").

### V8. Duyệt và báo cáo (sửa "Run modes")
User không có máy local: mỗi vòng quay một artifact (video raw, sheet 10-12 hình, nhận xét thẳng, giá); gate không đọc được fx vẽ trong clip nên phải xem frame thật; sau khi chốt, một trang tổng quan mọi state.

## 2. `fal-image`

### F1. Quy tắc style "không glow, không mềm" (CHỜ user giải thích)
User nói không nên cứng nhắc như mình mô tả và chưa hiểu lời giải thích. Chưa sửa mục này cho tới khi user nói rõ ý.

### F2. Canvas hero M (user đồng ý)
Hero tier M: **176x140** (@2x 352x280) thay vì 156x140, vì đòn chém và đâm của vũ khí dài không vừa 156x140 (cả asset phải đệm lại). Sửa `classes/hero.md` §3 và `format.md` §7. Fx dài hơn ô (tia) là lớp riêng, không bắt canvas thân to hơn.

### F3. Pose và manifest (user đồng ý)
- Thêm hàng ảnh `pose_respawn` (quỳ, gục đầu, xám) và `pose_levelup`; `pose_skill_*` thành **tuỳ chọn** khi user mô tả pose cuối bằng lời (ghi chú nhỏ: pose cuối mô tả bằng lời khớp ngay, không cần ảnh).
- `respawn_side`: "rise từ pose_respawn (đã chạy tốt)" thay cho "despawn đảo ngược"; `fx_*` trỏ tới fx Python.
- Thêm hàng đóng gói cuối: `ui/icon`, `export_manifest.json`, `EXPORT_README.md`.

### F4. Kích thước vũ khí và các thông số thiết kế còn thiếu: **hỏi user** (thay mục "vòng lặp master" cũ)
User chỉ ra gốc của vấn đề: ở bước mô tả nhân vật, mô tả ban đầu chưa nói kỹ kích thước vũ khí so với thân. Đề xuất: skill **phát hiện mô tả còn thiếu** và dùng `AskUserQuestion` để hỏi, thay vì đoán hay để vòng lặp master sửa dần.
- Với nhân vật cầm vật: hỏi **kích thước so với thân** (ngắn như dao găm, vừa tới eo, dài tới ngực, cao bằng người), **cầm bằng tay nào hoặc hai tay**, **khi đứng yên đặt ở đâu** (cắm đất, đeo lưng, cầm sẵn), có cần thấy báng hay mũi trong khung hay không.
- Tương tự cho các thông số hay bị bỏ sót: dáng đứng (chân giang bao nhiêu), phần được phóng đại, áo choàng hay vật mềm.
- Mỗi câu hỏi đưa 3-4 lựa chọn có khuyến nghị (như các câu hỏi class và tier hiện có). Trả lời đi thẳng vào `{design}` và `{idle}` trong `brief.md`.
Bằng chứng: master mất 7 bản vì thanh kiếm dài; v05 bị loại vì mũi kiếm tụt dưới đường chân, báng bị che, chỉ thấy một tay.

### F5. Ảnh trạng thái đổi màu
Câu hiệu quả (xám sạch cả 3 ảnh nháp ngay lần đầu): "THE WHOLE {subject} IS DESATURATED GREY: every part ... in flat shades of cool grey (light, mid and dark only), no {colours} anywhere; outlines stay near-black", và thay "Do not use magenta on the subject" bằng "the subject has no colour at all, only grey". Đưa vào `format.md` §3 hoặc `templates.md`.

### F6. `gen_image.py` nhận prompt từ file
Thêm `--prompt-file`; sau ảnh đầu của mỗi lệnh mở `.json` sidecar xem 60 ký tự đầu của `prompt` (đã mất ~0,02 USD vì shell truyền nguyên chuỗi `$(cat ...)` làm prompt).

### F7. Chế độ `--creative` cho skill và hành động
Sau khi nhân vật chốt, mỗi skill được đề xuất 2-3 phương án hành động theo công thức V1, có thời lượng gợi ý (V2), thư viện gợi ý (V3), rủi ro và giá.

### F8. Ghi lý do chọn
Mỗi ảnh được duyệt có mục ngắn "Cách tạo / Vì sao chọn / Vì sao ổn (đã kiểm bằng gì)" trong `brief.md`.

## 3. Công cụ nên đưa vào dự án chính thức (hiện ở `tools/frame_tuner/`)
| Công cụ | Việc | Ghi chú |
|---|---|---|
| Frame Tuner (`index.html`, `serve.py`, `.bat`, `build_artifact.py`) | chỉnh frame, lưu công thức, nguồn 15 hoặc 24 fps | tên artifact hiện là "Frame Editor" |
| `apply_recipe.py` | export thân theo công thức (đọc `fps` của công thức) | gắn `sources.json` của holy_commander, cần tổng quát hoá theo asset |
| `export_fx.py`, `preview_fx.py` | fx thành lớp riêng, preview | như trên |
| `build_export_manifest.py` | manifest và kiểm gói | mô tả state viết cứng cho holy_commander |
| `fx/*.py` | fx Python mẫu | `docs/python-fx-recipe.md` |
| `video_to_sheet.py --rest-last` | cỡ thân theo hình cuối | đã thêm |
| `gen_image.py --prompt-file` | prompt dài từ file | chưa làm |

## 4. Thứ tự áp dụng gợi ý
1. V1, V2, V4 (mô tả kỹ, thời lượng theo số nhịp, quy trình): ít code, ảnh hưởng lớn nhất tới chất lượng và chi phí.
2. F4 (hỏi user về vũ khí và thông số thiếu) cùng F2, F3 (canvas, manifest) trước hero tiếp theo.
3. V5, V6 (fx Python, clip chuẩn cho tuner, 24 fps, 1080P).
4. V3 (thư viện gợi ý) khi viết `--example` và `--creative`; V7, V8, F5-F8.
5. F1 sau khi user giải thích ý.

## 5. Cần user quyết
1. F1: ý của user về quy tắc style (mình hỏi lại ở trả lời).
2. Có chuyển 1080P thành mặc định cho clip vào tuner và export không (giá theo ước tính bằng nhau; cần kiểm hoá đơn thực).
3. Có dời công cụ vào `scripts/` không.
4. Có muốn thử một clip "run phóng đại" (~0,06 USD) và thử thêm run ở hậu kỳ bằng Python không.
