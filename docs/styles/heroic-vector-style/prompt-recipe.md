# heroic-vector-style: cách viết prompt (công thức đã cho ra bản thử v02 được duyệt)

Mẫu đầy đủ đã chạy: `prompt-template.txt` (10 nhân vật hỗn hợp) và `prompt-template-female-unit-lineup.txt` (10 nữ khác dáng và class, bản "game unit": vật khổng lồ định nghĩa hình bóng, hệ nằm trong cơ thể; ảnh 3840×2160) (lưới 10 nhân vật, ~9.200 ký tự, một ảnh `gpt-image-2` chất lượng low 2560×1440, khoảng $0,02). Kết quả: `out/enemies/_lineups/style_test_heroic_vector/source/design/grid_v02_simple.png`. Đặc tả phong cách: `style-spec.md`.

## 1. Khung một lệnh vẽ
```
python scripts/prompt_lint.py <prompt.txt> --body brawny        # không được có ERROR (cảnh báo "8 họ màu" là chấp nhận: mỗi con một bảng màu)
python scripts/gen_image.py --prompt-file <prompt.txt> --size 2560x1440 --png --name <tên> --versioned --out <thư mục>
```
Với một nhân vật đơn lẻ dùng cùng nội dung nhưng một đoạn nhân vật, ảnh `1024x1024`.

## 2. Thứ tự các khối trong prompt
1. **Mở đầu lưới (một đoạn):** "Game character lineup sheet: TEN different fantasy characters ... in a strict grid of 5 columns by 2 rows ... every character in its own invisible cell". Nêu: mỗi nhân vật nhìn **nghiêng phải** (SIDE VIEW từ camera cao nghiêng ~60°, thân xoay ~30° về phía người xem, tay chân xa che một phần), **đứng thẳng** (UPRIGHT), hai chân trên một đường đất, đầu nghiêng ~8°; `TWO ARMS OF EXACTLY THE SAME SIZE AND LENGTH`, `TWO LEGS ...` (thú: `FOUR LEGS`).
2. **Câu về giới và vai:** "the men are stocky with huge shoulders and enormous fists and big beards or moustaches, the women are slim with a clear waist, flowing hair and a confident look, the beast and the monsters have their own anatomy". Câu về mặt: "heavy angular brows and a snarl, a grin showing teeth or a big moustache for the men, long eyelashes and a confident look for the women, glowing eyes".
3. **Bố cục lưới:** nhân vật **LARGE and sharp, about 80% of the cell height**, giữa ô, **chân ở 92% chiều cao ô**, có nền trống giữa các nhân vật, không vũ khí hay áo choàng chạm ô bên cạnh. Cả mười cùng cỡ về khối và **cùng đơn giản** ("like a clean sticker illustration").
4. **Mười đoạn nhân vật** theo mẫu ở mục 3.
5. **Đoạn COLOUR PLAN** (phải có chữ `COLOUR PLAN` để lint qua): "every character has its own colour plan above: one saturated dominant hue with a bright accent close to its complement and a cream-white highlight, strong contrast, deep shadows tinted toward their own colour, never pure black; the outline ... a thick dark shade of its own dominant colour".
6. **Câu nền và biên:** "Everything stays inside the frame with a margin ... Background: one flat solid pure magenta color (#FF00FF) everywhere, no gradient, no ground, no cast shadow, no grid lines, no text ... Do not use magenta or pink anywhere on the subject."
7. **Khối Style** (mục 4), luôn ở cuối.

## 3. Mẫu một đoạn nhân vật (cấu trúc cố định)
`<N>. <TÊN>, <giới tính>, <class>, <hệ>, <loại>, <dáng + số đầu>: <đầu và mặt: biểu cảm + râu/tóc bằng "n cụm lớn mịn">, <thân và trang phục bằng vài mảng lớn đếm được>, <ONE oversized vật khổng lồ, tay cầm bên TRÁI ảnh, cầm thấp>. Colours: <màu chủ đạo #hex với shadow #hex và light #hex>, <accent #hex>, cream highlight #hex.`
- **Đếm mảng bằng số** thay cho tính từ: "bốn cụm lửa lớn mịn", "sáu mảng cơ", "tám khối đá", "ba mũi đinh ba", "sáu gai". Đây là điều làm bản v02 sạch.
- Vũ khí dài cầm chéo hoặc cầm thấp (đầu vũ khí không cao hơn đầu), để không lấn ô trên.
- Con thú và con tay không: ghi rõ "no weapon, empty hands".

## 4. Khối Style (nguyên văn, điền `{H}` = 60)
> Style: stylized 2D vector cartoon game art for a fantasy tower defense game, in the manner of a bold heroic cartoon character illustration with a lot of personality, each character designed to read at about 60 pixels tall. Exaggerated chunky proportions: the stocky male characters about 2.5 to 3 heads tall with a big head, huge shoulders and chest, enormous fists and short legs; the female and agile characters slimmer, about 4 to 5 heads tall; every character has ONE oversized signature element. Strong expression on every face. SIMPLE AND CLEAN: every part of the body and the costume is ONE big smooth bold shape with clean crisp outlines and large flat colour areas, at most six bold shapes in the costume; hair, beards, fur, flames and capes are drawn as three to five big smooth clumps with pointed tips, never as many thin strands; the only surface detail is a few big highlight shapes and at most a few round rivets; NO texture, NO hatching, NO scratches, NO speckles, NO noise, NO fringe, NO tiny details, NO thin lines. Colour: flat solid fills in 3 hard-edged tones with strong contrast, a deep shadow tone tinted toward the colour, a bright rim-light shape on the lit edge and a cream-white highlight shape; no gradients, no airbrush, no soft glow, no blur, no painterly texture. Thick clean dark outlines of an even weight tinted toward the local colour, thicker on the outside and thinner inside, with rounded joins. High top-down camera tilted about 60 degrees; light comes from the top-left.

## 5. Từ nên dùng, từ nên tránh
| Dùng | Tránh (đã gây rối ở bản v01) |
|---|---|
| "ONE big smooth bold shape", "three big smooth clumps", "clean sticker illustration", "at most six bold shapes", số lượng mảng | "speckle spots", "scratches", "rivets and plate edges", "fur", "feathers", "moss", "coils", "many spikes", "tiny", "VERY SMALL inside its cell" |
| "drawn LARGE, about 80% of the cell height" | yêu cầu nhân vật nhỏ trong ô (model nhòe nét) |
| bảng màu hex riêng mỗi con | một bảng màu chung cho cả lưới (cũng được nếu muốn một tộc, xem lineup-workflow) |
| "plain", "simple" cho phần phụ (áo, váy, khăn) | "ornate, intricate, detailed" |

## 6. Sau khi vẽ
1. Xem ảnh; chấm theo `style-spec.md` §8.
2. Làm phẳng nền nếu có bóng đất tím hoặc nền không đều: `python scripts/lineup/lineup_fix_pink.py <ảnh> --out <ảnh_phẳng> --flatten-bg` **chỉ khi có**; **không** dùng đổi màu hồng (`--target`) trên lưới có da tím hoặc hồng thật (nó sẽ nhuộm xanh). Xem `docs/scripts/lineup/lineup-workflow.md`.
3. Phép thử thu nhỏ 60 và 120 px (cắt từng con, đặt cạnh nhau) trước khi duyệt.
4. Sửa riêng vài con không vẽ lại cả lưới: `python scripts/lineup/lineup_replace.py`.
5. Từ lưới sang clip chuyển động: quy trình `docs/scripts/lineup/lineup-workflow.md` (đặt lại ô, một clip một động tác, tách khung). Các bài học về mô tả chuyển động áp dụng như cũ.
