# Skill bằng cặp pose A/B + vfx + rig studio (phương pháp "alien")

Ghi ngày 2026-11-12. Nhân vật thử: `out/heroes/azure_blade` (hero, cỡ M), skill 1 "Trảm Trăng Khuyết". Kết quả: người dùng đánh giá hai pose "đúng ý 100%".
Phân tích gốc của phương pháp (đo trên `ref/alien`): phụ lục §8 cuối file này. Hướng dẫn công cụ: `docs/scripts/puppet_kit/puppet-kit-guide.md`, `docs/tools/studio/puppet-studio-guide.md`, `lib-fx/README.md`.

## 1. Ý tưởng

Một skill chuyển động kiểu "trước khung, sau khung" (A rồi B, mô tả 4 bước vươn, rút, co, đâm) làm video rất hay sai và phải làm lại cả clip.
Game tham khảo (`ref/alien`: 177 khung nhưng chỉ 81 hình khác nhau, chân đứng yên ở một hàng pixel, mỗi đòn khoảng 3 hình thân) **không vẽ chuyển động giữa hai tư thế**:

- Họ vẽ kỹ **hai tư thế chính**: A (chuẩn bị) và B (kết thúc).
- Một **vệt chém lớn** vẽ đúng đường quét của lưỡi từ A tới B, đặt vào khung đổi tư thế, che chỗ nhảy hình. Mắt người tự thấy "đã chém".
- Phần còn lại là sự sống nhỏ: thở, nhún, áo choàng vẩy.

Mình làm theo đúng cấu trúc đó, nhưng mỗi phần dùng công cụ phù hợp:

| Phần | Công cụ | Chi phí |
|---|---|---|
| Hai pose A, B | `fal-image` (gpt-image-2 low), mỗi pose một ảnh, A làm ảnh tham chiếu cho B | ~0,015 USD/ảnh |
| Sự sống của thân, tay, vai, áo choàng | Puppet Kit + dây chằng của Studio, pose-to-pose, hai pose đã duyệt | 0 USD |
| Vệt chém | bộ sinh slash của `lib-fx` (`scripts/slash_fx/`) + lớp bề mặt lưỡi quét, theo quỹ đạo gốc/mũi đao | 0 USD |

## 2. Ưu điểm và khuyết điểm

**Ưu điểm**
1. **Làm lại (retry) rẻ hơn video.** Sai một pose: làm lại đúng ảnh đó, ~0,015 USD (thực tế `costs.csv`: 0,0154 đến 0,0159). Một clip video `h3-max-turbo` 4 s: 0,06 USD (~4 lần), và sai thì mất cả clip cùng mọi thứ trong đó. Hai pose của azure_blade (A một lần, B ba lần thử) tốn 0,063 USD.
2. **Chủ động hoàn toàn với vfx.** Vệt chém tự host trong `lib-fx` và `source/vfx/`: sinh bằng code, đổi màu, độ dày, độ sáng, nhịp, vị trí chỉ bằng sửa tham số JSON. Không phụ thuộc model tự vẽ vệt (video hay vẽ vệt hồng, nhoè, sai hướng). Chạy lại ra đúng kết quả cũ (`PYTHONHASHSEED=0`).
3. **Tích hợp Studio và rig, nhân vật sống hơn.** Hai pose chỉ là ảnh tĩnh, rig tách thân, tay, đao và dây chằng vai-ngực cho nhịp thở, nhún theo quán tính, tay nảy, áo choàng vẩy, mà không đổi tư thế đã duyệt.
4. **Tất định và sửa được từng phần**: sửa nhịp là sửa số trong `make_anim.py`, sửa vệt là sửa `slash_params.json`, không gọi API.

**Khuyết điểm**
1. **Phụ thuộc 100% vào pose gốc phải chuẩn.** Rig 2D chỉ biến đổi nhẹ ảnh đã có (nhấc vài px, nghiêng vài độ). Không sửa được pose sai tay, sai chân, sai hướng đao hay sai cỡ. Pose sai là phải vẽ lại pose (mục 4, bước 2 và 3).
2. Không có chuyển động trung gian giữa A và B: cú vung dài một khung, do vệt chém che. Hợp đòn mạnh, ngắn; không hợp động tác cần thấy rõ từng bước (chạy, quay người).
3. Cần người duyệt bằng mắt từng pose; mô hình ảnh hay nhầm tay trái phải, hướng đao, độ nghiêng.
4. Cắt rig (đa giác cho tay, đao) vẫn do người hoặc AI đặt tay trên ảnh, sai số vài chục px; phải xem overlay.
5. Vị trí chân giữa hai pose không tự khớp: phải đo chân trước thủ công (`foot_marks.json`).

## 3. Cấu trúc thư mục của một skill (ví dụ azure_blade)

```
out/heroes/azure_blade/
  brief.md, history.md, meta.json
  source/design/
    master_v06.png                  master đã duyệt (cỡ chuẩn)
    pose_skill_crescent_p1_v01.png  pose A
    pose_skill_crescent_p2_v03.png  pose B
    prompts/pose_skill_crescent_p{1,2}_*.txt   prompt đầy đủ (ghi lại để chạy lại)
  source/rig/
    foot_marks.json                 x chân trước của từng ảnh (px ảnh gốc)
    make_rigs.py  -> rig_a.json, rig_b.json   (torso / blade / arms + dây chằng)
    make_anim.py  -> anims/crescent.json      (nhịp)
  source/vfx/crescent/
    weapon_marks.json               gốc/mũi đao của A và B (px ảnh gốc) + đường quét
    slash_params.json               màu, độ dày, trắng, mũi đậm/cán nhạt, quầng
    build_crescent.py               ghép thân puppet + vệt, ra GIF
  frames/skill_crescent_puppet_side/   thân (chưa vệt), xuất bởi puppet.py
  frames/skill_crescent_side/          thành phẩm có vệt: frames @2x @1x, preview_2x.gif, preview_game_1x_x3.gif, contact.png
```

## 4. Quy trình

### Bước 0: chuẩn bị
- Master đã duyệt (hero: `fal-image`; **không chibi, không dễ thương**, 3,5 đến 4,5 đầu; hai tay và hai chân cùng cỡ; áo choàng nằm sau thân; cả vũ khí trong khung. Xem `fal-image/format.md` "No chibi, no cute").
- Viết **mô tả skill** từng pha, theo vật lý (cầm, giơ, chém, tiếp đất), cho **hai pose duy nhất**. Không mô tả các khung giữa.

### Bước 1: viết prompt hai pose (chưa tốn tiền)
Lấy `{design}` nguyên văn từ master (script mẫu `out/heroes/azure_blade/source/design/prompts/mk_poses.py` ghép: `{design}` + vũ khí + mô tả pose + câu cấm + `{BG}` + `{STYLE}`). Mỗi pose gồm:

| Phần | Pose A (chuẩn bị) | Pose B (kết thúc) |
|---|---|---|
| Hướng nhìn | nghiêng hẳn, nhìn một phía | nghiêng hẳn, cùng phía |
| Tay | hai tay cùng nắm cán, nêu vị trí | như A, nêu vị trí mới |
| Vũ khí | nêu hướng lưỡi bằng **vị trí trên ảnh** (trái/phải của ảnh), không nói trái/phải của nhân vật | nêu rõ: nằm ngang song song đất, áp lên đất, **không cắm**; thấy đủ lưỡi |
| Áo choàng, lưng | rủ sau lưng | bị hất lên phủ lưng, thấy lưng |
| Thân | ngả nhẹ, chân vững | khom thấp, chân trước khuỵu, chân sau duỗi |
| Khung | vừa trong khung, ~75% | **chừa lề ≥ 8% mọi phía**, vẽ nhỏ hơn một chút |
| Cấm | không vệt, không bụi, không chuyển động, không bóng đất | như A |
| Ảnh tham chiếu | master | master **và pose A** (dặn: giữ nhân vật và cỡ, **không chép dáng**) |

### Bước 2: sinh và duyệt từng pose
```
python scripts/gen_image.py --prompt-file <prompt A> --size 1024x1024 --png --ref master_v06.png --name pose_skill_x_p1 --versioned --out <asset>/source/design
python scripts/gen_image.py --prompt-file <prompt B> ... --ref master_v06.png --ref pose_A.png --name pose_skill_x_p2 ...
```
- Mỗi lần một ảnh, xem bằng mắt, chấm theo checklist mục 5. Sai thì **chỉ làm lại pose sai**, sửa đúng một câu trong prompt (ví dụ lần đầu pose B cắm đao xuống đất thì sửa thành "lưỡi nằm ngang, áp lên đất").
- Người dùng duyệt; các bản không chọn xóa bằng `source_prune.py` cuối phiên.

### Bước 3: đo điểm bám (bằng mắt, có lưới)
- `foot_marks.json`: x chân trước (chân đứng yên) của từng ảnh. Chân này đứng yên giữa hai pose, thân lao tới.
- `weapon_marks.json`: toạ độ gốc (tsuba/cán) và mũi đao của A và B; đường quét: gốc đi theo đường cong qua trên đầu (`root_ctrl_up`, `root_ctrl_dx`), đao quay **thuận kim đồng hồ trên màn hình** qua hướng "lên" (hoặc ngược lại tuỳ động tác); `ease` cho gia tốc.
- Vẽ đường gốc-mũi lên ảnh (`debug_marks.png`) để kiểm tra có nằm đúng trên lưỡi không.

### Bước 4: tách rig và dây chằng
`python out/heroes/<id>/source/rig/make_rigs.py` ghi `rig_a.json`, `rig_b.json`. Mỗi rig:
- Xương `root` > `body` > `arms` (pivot ở vai).
- Ba lớp: `torso` (rest, gồm đầu, thân, chân, áo choàng; `fill_under` cho `arms` với `erode` lớn, `reach` nhỏ; `deform` làm áo choàng vẩy), `blade`, `arms` (hai tay, nắm đấm, giáp vai).
- Dây chằng `shoulder_chest` (`links`, `mode: stretch`): khi xương `arms` trượt (`tx`, `ty`), ảnh thân quanh vai và ngực đi theo. Vai nhô khi tay vươn, chìm khi tay đập xuống.
- Chạy `python scripts/puppet.py check <rig>` rồi xem `rig_overlay.png`: đa giác phải ôm đúng tay, nắm đấm, giáp vai, đao; **cạnh của đa giác `arms` không được cắt qua mặt** và không được ăn vào tóc.

### Bước 5: viết nhịp (4 pose của skill)
`make_anim.py` (một `anims/crescent.json`, 15 fps):

| Pose | Nội dung | Kênh chính |
|---|---|---|
| P1 | từ pose A, nâng đao hơi cao, hít vào, vai và ngực nhô | `arms.ty` -28, `arms.rot` -2,5, `body.sy` 1,022 |
| P2 | hạ về đúng pose A, thở ra, giữ | trả về 0, `body.sy` 0,992 rồi 1 |
| (cắt A→B, vệt che) | hit frame = khung đầu của pose B | |
| P3 | pose B (đập xuống), thân nén | `body.sy` 0,93 rồi nảy 1,015 |
| P4 | quán tính: nhún xuống, tay nảy, rồi về đúng pose B; sau đó thở nhẹ | `arms.ty` 20, -9, 6, -2, 0; `arms.rot` ±2 tắt dần; `torso.sway` 2,4 về 1 |

Đơn vị: `tx/ty` là px ảnh gốc 1024 (1 px ở @2x ≈ 7 px gốc). Biên độ phải **nhỏ**: bước dịch lớn nhất của thân giữa hai khung liền nhau chỉ ~2 px @2x (1 px cỡ game). Lần đầu lắc ngang cả người (34 px) bị người dùng chê "như động đất".

### Bước 6: xuất thân bằng Puppet Kit
```
python scripts/puppet.py init out/heroes/<id> --cell 176x140 --height 120     # một lần
python out/heroes/<id>/source/rig/make_rigs.py && python out/heroes/<id>/source/rig/make_anim.py
python scripts/puppet.py render out/heroes/<id> out/heroes/<id>/source/rig/anims/crescent.json --sheet skill_crescent_puppet_side
```
Thân ra `frames/skill_crescent_puppet_side/` (cell 352x280 @2x, chân ở pivot, cỡ thân chung `unit` = chiều cao thân của master).

### Bước 7: vệt chém (lib-fx)
`PYTHONHASHSEED=0 python out/heroes/<id>/source/vfx/crescent/build_crescent.py` (bắt buộc `PYTHONHASHSEED=0` vì `gen_slash_loop` đặt vết đứt bằng `hash()`).
- Gốc/mũi đao mỗi bước lấy từ `weapon_marks.json`; qua cùng phép đăng ký của rig nên vệt nằm đúng chỗ đao trong thân.
- Hai lớp: (a) bộ sinh layered `slash_from_track.py` (`scripts/slash_fx/`) (sợi, răng, vụn; mờ) và (b) **bề mặt lưỡi quét**: vẽ mọi đường gốc→mũi, nên dải **dày đúng bằng lưỡi**, mép dẫn song song lưỡi.
- Màu: đuôi xanh đậm, giữa xanh sáng, **đầu vệt trắng**, đường trắng mảnh theo quỹ đạo mũi; **mũi đậm và đục, cán nhạt và mờ**; quầng xanh.
- Đặt vệt: bước mọc đầu tiên trên khung cuối pose A (bắt đầu **đúng trên lưỡi pose A**), vệt đầy trên khung đầu pose B, rồi 3 khung tan. Không đặt vệt bước giữa lên thân pose A vì lưỡi trong thân vẫn ở vị trí cũ (lệch).

### Bước 8: duyệt và chốt
- Xem `contact.png` và `preview_game_1x_x3.gif` (**duyệt ở cỡ game H = 60 px @1x**, không chỉ @2x).
- Ghi vào `brief.md` (manifest) và `history.md`; `source_prune.py` xóa bản không chọn.

## 5. Checklist bắt buộc

**Pose (bước 1-2)**
- [ ] Master đã duyệt; hero không chibi, không dễ thương (3,5 đến 4,5 đầu).
- [ ] Prompt pose A và B giữ `{design}` nguyên văn, ghi rõ hai tay cùng cỡ, hai chân cùng cỡ.
- [ ] Prompt **cấm mọi fx** (vệt, bụi, phát sáng, bóng dưới đất).
- [ ] Hướng đao và vị trí tay mô tả bằng vị trí trên ảnh, không bằng "trái/phải" của nhân vật.
- [ ] Pose B dùng pose A làm ảnh tham chiếu, kèm câu "không chép dáng".
- [ ] Hai pose cùng hướng nhìn; nhân vật cùng cỡ gần bằng nhau (đầu rộng bằng nhau); ghi lại nếu lệch.
- [ ] Mỗi pose đạt theo mắt: đúng động tác mô tả, hai tay nắm đúng, vũ khí **nguyên cả lưỡi trong khung**, lề ≥ 8%.
- [ ] Người dùng duyệt từng pose trước khi dựng rig.

**Điểm đo và rig (bước 3-4)**
- [ ] `foot_marks.json`: đúng chân đứng yên (không phải mũi đao đang nằm trên đất).
- [ ] `weapon_marks.json`: đường gốc→mũi trùng lưỡi trong `debug_marks.png` ở cả A và B.
- [ ] Đa giác `arms` không cắt qua mặt, không ăn tóc; đa giác `blade` ôm kín lưỡi và cán.
- [ ] `fill_under` của `arms`: `erode` ≥ 10, `reach` ≤ 30 (nếu lớn thì lộ mảng tóc giả khi tay nhấc).
- [ ] **Không** `fill_under` cho phần đao nằm trên nền trống (sinh đao ma khi đao di chuyển).
- [ ] Dây chằng `shoulder_chest` có mỏ neo ở vai và ngực của lớp `torso` (không đặt trên lớp tay).
- [ ] `puppet.py check` chạy sạch, xem `rig_overlay.png`.

**Chuyển động (bước 5-6)**
- [ ] Không có lắc ngang cả thân; bước dịch thân lớn nhất giữa hai khung ≤ ~2 px @2x.
- [ ] Đúng bốn pose của mô tả: P1 nâng đao nhẹ, P2 về pose A, P3 pose B, P4 nhún và về pose B.
- [ ] Về **đúng** pose A / pose B ở cuối mỗi đoạn (kênh về 0 và 1).
- [ ] Hit frame = khung đầu pose B; ghi vào `anims/*.json`.

**Vệt chém (bước 7)**
- [ ] Chạy với `PYTHONHASHSEED=0`.
- [ ] Mũi đao ở khung vệt đầy khớp mũi đao của pose B; mép trắng nằm dọc lưỡi.
- [ ] Khung vệt đầu tiên bắt đầu trên lưỡi pose A, không có lớp nào lơ lửng.
- [ ] Độ dày = cả lưỡi; mũi đậm, cán nhạt; có trắng; đúng màu theo yêu cầu.
- [ ] Vệt tan hết trong vài khung, không biến mất đột ngột.

**Chốt**
- [ ] Xem GIF ở cỡ game (H = 60 px @1x); người dùng duyệt.
- [ ] `brief.md`, `history.md` cập nhật; `source_prune.py` chạy; ghi chi phí.

## 6. Chi phí thực tế (azure_blade, 2026-11-12)

| Hạng mục | Giá |
|---|---|
| Pose A (1 lần) | 0,0155 USD |
| Pose B (3 lần: cắm đao, hai bản nằm ngang) | 0,0155 + 0,0159 + 0,0159 = 0,0473 USD |
| Rig, nhịp, vệt chém, GIF | 0 USD |
| **Skill hoàn chỉnh (hai pose, có retry)** | **0,063 USD** |
| (Ngoài skill) 6 master thử, 3 chibi bị loại và 3 chiến binh | 0,091 USD |
| So sánh: một clip video 4 s | ~0,06 USD, mất cả clip khi sai |

## 7. Vướng mắc đã biết và việc nên làm tiếp
- Nét tóc nhỏ lộ giữa cánh tay xa và đầu khi tay nhấc cao (pose A). Có thể thêm một lớp đầu riêng hoặc giảm độ nhấc cánh tay xa.
- Pose B chỉ tách tay, chưa tách đầu.
- `build_crescent.py` còn hằng số cho nhân vật này (vị trí đặt vệt theo khung hit, màu xanh lam); khi dùng cho nhân vật khác cần tách ra tham số (tên pose, hit frame, màu).
- Chưa kiểm GIF ở cỡ @1x trên màn hình thật; hiện duyệt qua ảnh tĩnh và GIF phóng 3 lần.
- Đòn cần xoay người, đổi mặt hoặc chạy vẫn phải dùng video (`video-sprite`) hoặc pose reel.

## 8. Phụ lục: vì sao `ref/alien` làm được (đo trực tiếp trên khung)

| Đặc điểm | Số đo / quan sát |
|---|---|
| Cỡ | Nhân vật cao 32-41 px trong ô 168x112. Ở cỡ này mắt đọc bóng dáng và hiệu ứng, không đọc chi tiết khớp |
| Số hình | Chạy (0002-0006): **5 hình**. Đòn đánh đôi (0007-0032): 26 khung nhưng **~15 hình**; hầu hết mỗi hình giữ đúng **2 khung** (khung 0008, 0010, 0012... trùng 100% khung trước) |
| Lấy đà | Một tư thế giữ 6 khung (0007-0012), chỉ ánh sáng nhấp nháy (~600 px đổi) |
| Ra đòn | Đổi thẳng sang **tư thế mới**, không có khung chuyển tiếp, không nội suy |
| Hiệu ứng | Vệt chém hình lưỡi liềm **rất to** trong 2-3 khung, **che gần hết thân** đúng lúc đổi tư thế. Vệt chém gánh cảm giác chuyển động và che chỗ nhảy hình |
| Thiết kế | Cân đối, mập, chi ngắn, hai tay bằng nhau, chân bằng nhau, tay không đè lên thân; góc gần nhìn thẳng |
| Thân | Gần như không di chuyển; chạy chỉ nhún 1-2 px |

Cách họ làm (suy luận, chưa xác nhận): vẽ tay các **tư thế khoá** (rất có thể vector, tái dùng mảnh, đổi mảnh khi đổi tư thế), xuất ra cỡ nhỏ, giữ
khung on twos, và vẽ riêng vài hình vệt chém. Họ không mô phỏng vật lý từng khung: **người vẽ quyết định tư thế đúng**, hiệu ứng che phần còn lại.
Phương pháp ở file này thay "người vẽ tư thế đúng" bằng hai pose do model ảnh vẽ từng hình và người duyệt, còn vệt chém lớn che chỗ đổi pose.
