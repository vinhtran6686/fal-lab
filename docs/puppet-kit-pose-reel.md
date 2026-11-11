# Pose Reel: mẫu video tư thế cơ bản cho một nhân vật (v1.1)

Cập nhật 2026-11-11. Trạng thái: **v1.1 đã chạy trọn trên lion_brawler, chờ user duyệt để thành mẫu cho mọi nhân vật.** Liên quan: `docs/puppet-kit-next.md` §9.
v1 (3 clip, ảnh đầu là master nguyên bản) bị advisor trả lại trước khi chạy; các sửa đổi ghi ở §9.

## 1. Vì sao cần

- Rig cắt lớp gãy ở khớp khi gập; khớp uốn liền (`skin`) đỡ hơn nhưng user đánh giá **vẫn gãy** (2026-11-11). Uốn hình có sẵn không vẽ lại được nếp gập, cơ và phối cảnh.
- Ảnh pose tĩnh rời rạc: mỗi ảnh một cỡ, tay chân sai ngẫu nhiên (tay "tật" ở run), không có hình trung gian.
- Video thì model **vẽ lại** khớp ở từng frame, cỡ đều trong một clip và có sẵn hình trung gian.

Pose reel = vài clip ngắn, mỗi clip **một bài vận động chuẩn**, quay một lần cho mỗi nhân vật, cắt frame thành **thư viện pose**. Animation về sau ghép từ thư viện này
(chọn frame, đặt nhịp bằng JSON) cộng rig cho phần rig làm tốt. Reel **không** thay rig: frame là ảnh phẳng cả người, không tách lớp được.

| Việc | Dùng gì |
|---|---|
| idle, nhịp thở, nhún vai, lấy đà và hồi biên độ nhỏ (khớp gập dưới ~30°) | rig (`skin`) |
| khớp gập lớn: ngồi xổm, giơ tay, gập khuỷu | frame của reel |
| chạy, đi | frame của reel (clip run) |
| xoay người, đổi hướng | frame của reel (clip turn_a, turn_b) |
| đòn đánh, skill riêng của nhân vật | pose still hoặc một clip riêng, ghép với reel + rig + fx |

## 2. Nguyên tắc chung của mọi clip

1. **Một khung đặt cố định cho cả reel.** Master được thu 0,70 lần và đặt lên canvas 1024x1024 màu key phẳng `#FF00FF`, chân cách mép dưới 60 px, còn khoảng 30% khoảng trống phía trên
   (`puppet_reel.py input`). Vì biết tỉ lệ và độ dời, mọi frame nằm sẵn trong hệ toạ độ của rig: `ground_frame = (ground_rig × scale + offset) × cạnh_frame / 1024`, `unit` tương tự.
   Không cần căn cỡ từng frame. (Master nguyên bản chỉ còn 34 px trên đầu: giơ tay sẽ bị cắt.)
2. **Ghim ảnh cuối khi động tác có điểm dừng rõ**: clip tại chỗ kết thúc ở master; clip xoay kết thúc ở ảnh góc tiếp theo. **Clip chạy không ghim ảnh cuối** và chạy tới hết clip (ghim làm mất frame vào đoạn hãm).
3. **Một bài vận động một clip**, có 0,4 s đứng yên ở đầu. Xoay người không quá 90° mỗi clip.
4. **Hướng viết theo màn hình** (trái, phải, lên, xuống), không dùng "quay lại", "phía xa", "ra sau lưng".
5. **Hai bàn chân ghim** trên cùng hai chỗ, trừ clip run và turn.
6. **Mỗi tay nối đúng vai của nó**, nêu tay gần/xa theo phía màn hình; ghi góc khuỷu, góc gối bằng số; clip quay phải thì thêm "hips, shoulders and face stay turned to the right; the shoulders never square to the camera".
7. Camera khoá, nền key phẳng, chỉ có thân. Câu nền và style đặt **cuối** prompt.
8. Model và giá: `h3-max-turbo`, 480p, 0,015 USD/s (`scripts/fal_video.py`); mỗi clip tối đa 2 take, take 2 chỉ khi biết rõ nguyên nhân.
9. Cắt frame ở 15 fps; **không frame nào được dùng nếu chưa xem bảng contact và số đo độ nét**.

## 3. Bộ clip chuẩn (v1.1)

| Mã | Clip | Dài | Ảnh đầu → cuối | Lấy được gì | Giá |
|---|---|---|---|---|---|
| R1a | **turn_a**: xoay tại chỗ từ quay phải tới chính diện | 3 s | master → `view_front` | góc 3/4 phải → chính diện | 0,045 |
| R1b | **turn_b**: xoay tiếp từ chính diện tới quay trái | 3 s | `view_front` → master lật ngang | chính diện → quay trái | 0,045 |
| R2 | **run**: chạy tại chỗ | 4 s | master → (không ghim) | vòng chạy, tay ngược chân, khuỷu gập đúng | 0,06 |
| R3a | **squat**: ngồi xổm sâu, hai nắm tay co lên vai, rồi đứng lên | 3 s | master → master | gối gập sâu, khuỷu gập hết | 0,045 |
| R3b | **press**: đứng thẳng, co tay lên vai rồi đẩy hai tay qua đầu, hạ xuống | 3 s | master → master | tay giơ cao | 0,045 |
| R4 | walk: đi tại chỗ (tuỳ chọn, cho class có walk) | 4 s | master → (không ghim) | vòng đi | 0,06 |

Bắt buộc cho hero: R1a-R3b, **16 s ≈ 0,24 USD**, cộng 1 ảnh `view_front` (~0,014 USD) nếu nhân vật chưa có (enemy và boss đã có sẵn).
**Đây là thay đổi định dạng**: `format.md` §3 và `classes/hero.md` §4 nói hero không có góc chính diện; pose reel cần một `view_front` làm ảnh ghim (chỉ là tài nguyên, game không hiển thị). Nếu mẫu được duyệt thì sửa hai file đó.

## 4. Prompt

Thứ tự khối: (1) Identity: "Animate this EXACT isolated character, do not redesign it. The same {design}"; (2) câu tay và hướng (nguyên tắc 6); (3) Motion + Timeline của clip;
(4) camera khoá, cỡ đầu không đổi, nằm trong khung; (5) body only + avoid; (6) nền và style.
Prompt thật đã chạy tốt, dùng làm mẫu và chỉ thay `{design}` cùng câu tay/đuôi: `out/heroes/lion_brawler/source/video/reel_{turn_a,turn_b,run,squat,press}.prompt.txt`.

Các câu quyết định kết quả:
- turn: "He pivots on the spot in ONE direction only: his chest turns toward the viewer until we see him straight from the FRONT. He never turns back toward the right and never shows his back."
  Không dùng "turns around". Nói đuôi (hoặc dấu bất đối xứng) ở phía nào của màn hình lúc cuối.
- run: "RUNS IN PLACE as on a treadmill ... never travelling across the screen", nêu chân nào ra trước trước, "always alternating", "both elbows bent about 90 degrees the whole time".
- squat / press: "BOTH FEET STAY PLANTED on the same two spots"; press thêm "the legs stay straight ... never squats", "the fists stay inside the picture".

## 5. Quy trình

```bash
A=out/heroes/<id>; W=$A/.work/reel
# 1. ba khung đầu vào (0 USD)
python scripts/puppet_reel.py input $A $A/source/design/master_vNN.png --name master
python scripts/puppet_reel.py input $A $A/source/design/master_vNN.png --name master_flip --mirror
python scripts/puppet_reel.py input $A $A/source/design/view_front_vNN.png --name front --match master   # cùng chiều cao thân và hàng chân với master
# 2. năm clip (trả tiền; thêm --dry-run để xem giá trước)
python scripts/fal_video.py video --prompt-file $A/source/video/reel_turn_a.prompt.txt --reference $W/master_canvas.png --last-frame $W/front_canvas.png       --duration 3 --resolution 480p --model h3-max-turbo --out-dir $W/turn_a
python scripts/fal_video.py video --prompt-file $A/source/video/reel_turn_b.prompt.txt --reference $W/front_canvas.png  --last-frame $W/master_flip_canvas.png --duration 3 --resolution 480p --model h3-max-turbo --out-dir $W/turn_b
python scripts/fal_video.py video --prompt-file $A/source/video/reel_run.prompt.txt    --reference $W/master_canvas.png                                          --duration 4 --resolution 480p --model h3-max-turbo --out-dir $W/run
python scripts/fal_video.py video --prompt-file $A/source/video/reel_squat.prompt.txt  --reference $W/master_canvas.png --last-frame $W/master_canvas.png      --duration 3 --resolution 480p --model h3-max-turbo --out-dir $W/squat
python scripts/fal_video.py video --prompt-file $A/source/video/reel_press.prompt.txt  --reference $W/master_canvas.png --last-frame $W/master_canvas.png      --duration 3 --resolution 480p --model h3-max-turbo --out-dir $W/press
# 3. cắt frame: --canvas là khung mà clip BẮT ĐẦU
python scripts/puppet_reel.py cut $A $W/turn_a/clip.mp4 --name turn_a --canvas master
python scripts/puppet_reel.py cut $A $W/turn_b/clip.mp4 --name turn_b --canvas front
python scripts/puppet_reel.py cut $A $W/run/clip.mp4    --name run    --canvas master   # squat, press tương tự
```

`cut` chép clip vào `source/video/reel_<name>.mp4` (+ `.json`), ghi `source/rig/reel/<name>/NNN.png` (frame đếm từ 001), `reel.json` (`ground`, `unit`, số đo từng frame)
và `check/contact.png`; ghi clip vào `meta.json` "sources" để `source_prune.py` giữ lại. Dùng frame trong animation:

```json
{"name": "run", "reel": "source/rig/reel/run", "pick": [22, 25, 27, 30, 33, 35, 38, 40]}
```

`pick`: mỗi số là một hình. `tracks` vẫn áp được (`root.sy`, `root.shx` ...); track được tính tại vị trí của hình trong `pick`. Shot rig và shot reel xen kẽ trong cùng một animation.

Chọn frame cho vòng chạy: tìm chu kỳ bằng độ nét (frame nét nhất lặp lại mỗi nửa chu kỳ, ở chỗ tay chân đổi chiều), rồi lấy 8 frame cách đều trên một chu kỳ đầy đủ.

## 6. Nghiệm thu một clip

| Tiêu chí | Cách kiểm | Ngưỡng |
|---|---|---|
| Đúng bài, đủ pha | xem `contact.png` | thiếu pha → take 2 hoặc tách clip |
| Xoay một chiều | xem contact: mặt đổi hướng đúng một lần | xoay ngược → take 2 |
| Thiết kế không đổi (màu, găng, bờm, số vuốt, đuôi đúng phía) | xem contact | sai → bỏ frame; sai kéo dài → take 2 |
| Cỡ thân ổn định | `reel.json` metrics `body_h` ở các frame đứng thẳng | lệch ≤ 8% so với frame đầu |
| Chân ghim (clip chân ghim) | `feet_y` | lệch ≤ 2% cạnh frame |
| Không chạm mép | `edge` | không frame nào `true` |
| Độ nét | Laplacian trung bình trong thân, so với frame đầu | ≥ 0,75 mới dùng làm pose **giữ** (một frame hiện lâu hơn một hình); 0,6-0,75 chỉ dùng làm hình trung gian. Vòng chạy/đi: mọi hình đều là hình trung gian (mỗi hình hiện 67 ms, nhoè đọc như chuyển động), nên ngưỡng là ≥ 0,6 |
| Không hiệu ứng, vệt, bóng | xem contact | có → bỏ frame |
| Khớp ảnh ghim | frame cuối chồng lên ảnh ghim | cùng tư thế, lệch dưới vài px |

## 7. Kết quả bản thử trên lion_brawler (2026-11-11)

5 clip, mỗi clip **một take**, 16 s, 0,24 USD + 1 ảnh `view_front` 0,014 USD.

| Clip | Kết quả | Số đo |
|---|---|---|
| turn_a | **đạt**: xoay một chiều tới chính diện, thiết kế giữ nguyên | thân 291-304 px (đầu 303), chân lệch 5 px, nét 0,86-1,07 |
| turn_b | **đạt**: xoay tiếp tới quay trái, đuôi sang phải đúng | thân 295-309, chân lệch 2 px, nét 0,89-1,04 |
| run | **đạt có điều kiện**: chạy thật, khuỷu gập đúng, tay ngược chân; chu kỳ 22 frame (chạy chậm); nhiều frame nhoè vì tay chân nhanh | nét 0,61-1,06; frame nét lặp mỗi 11 frame (22, 33, 43, 54) |
| squat | **đạt**: ngồi xổm sâu, nắm tay lên vai; đoạn hạ và đứng lên chỉ có 2-3 frame, nhoè | chân không lệch; nét 0,68-0,70 ở frame 12-13 và 34, còn lại ≥ 0,9 |
| press | **đạt**: hai tay duỗi thẳng qua đầu, không bị cắt | thân cao nhất 389 px, không chạm mép; nét 0,60-0,68 ở frame 9, 15-16, 34 |

Animation ghép từ reel (0 USD): `run_side` (8 hình, độ nét 0,67-1,03, đạt ngưỡng vòng chạy ≥ 0,6; thay bản 4 ảnh tĩnh có tay "tật"; `motion_check --loop` không cờ, nhún 12 px),
`turn_left_side` (25 hình: rig → chính diện → quay trái), `reel_test_side` (37 hình: squat rồi press). Frame reel đặt cạnh frame rig trùng cỡ và vị trí chân mà không phải căn tay.

Trả lời các câu hỏi của v1:
1. Xoay người: **được** khi chia hai nửa qua ảnh chính diện và ghim cả hai đầu.
2. Gộp squat + press: không thử; tách hai clip chạy tốt.
3. 480p: đủ cho 120 px @2x ở frame nét; frame chuyển động nhanh bị nhoè.
4. Nét và màu của frame reel mềm hơn rig một chút; ở cỡ game khó thấy. Chưa đo màu.
5. Cắt rig → reel ở frame đầu clip: không nhảy cỡ, không nhảy chân.

## 8. Việc cần sửa cho v1.2 (chưa làm)

| Vấn đề | Hướng |
|---|---|
| Frame nhoè ở đoạn chuyển động nhanh (run; hạ/đứng của squat; đẩy/hạ của press) | cho động tác chậm lại: squat và press 5 s thay vì 3 s, bỏ đoạn giữ dài; run: thử 720p (cùng giá theo bảng model) hoặc model `h3-max` |
| Run là chạy chậm (22 frame một chu kỳ), lấy 8 frame cách 2-3 frame nên có frame nhoè | prompt "one pair of strides about every 0.5 s" chưa được tuân; thử ghi "fast sprint" và số bước |
| Chọn frame vòng chạy đang làm bằng tay | lệnh chọn chu kỳ tự động theo độ nét (hoặc dùng `gait_loop` của video-sprite) |
| Chưa có bước despill, dearc cho frame reel | dùng lại `video_to_sheet --despill`, `dearc.py` khi thấy viền key |
| Reel chưa có vệt chém, socket vũ khí | đánh dấu gốc/mũi trên vài frame (Blade Track Marker) khi dùng reel cho đòn đánh |
| Chưa thử trên nhân vật có vũ khí dài hoặc áo choàng | Holy Commander là ca thử tiếp theo |

## 9. Sửa đổi so với v1 (theo advisor, trước khi trả tiền)

- Clip xoay 180° một phát → chia hai clip 90° qua ảnh chính diện (bài học M01-b: model xoay cả hai chiều).
- Clip chạy ghim ảnh cuối và có đoạn dừng → không ghim, chạy tới hết (cách `run_side` của Holy Commander đã làm).
- Squat-press gộp → tách hai clip.
- Ảnh đầu là master nguyên bản → khung có lề (đầu chỉ còn 34 px trống, giơ tay sẽ bị cắt).
- Câu nền/style chuyển xuống cuối prompt; thêm câu tay và hướng; bảng nghiệm thu thêm chạm mép, xoay một chiều, độ nét.
