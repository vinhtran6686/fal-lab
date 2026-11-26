# Quy trình lưới nhiều nhân vật trong một clip: bước làm, thông số kỹ thuật, áp dụng cho các class

Quy trình chung cho mọi class có nhiều đơn vị cùng tộc/hệ (enemy, ally, và hero khi cần tạo hàng loạt). Mục tiêu: một ảnh lưới 10 nhân vật → mỗi động tác chỉ MỘT clip → tách ra 10 bộ khung. Đã chạy thật ngày 2026-11-26 (lưới 10 quái, động tác chết và tấn công). Mọi con số dưới đây là số đã đo; lần sau dùng lại đúng các số này để kết quả nhất quán.

## Áp dụng cho các class khác (cách làm một bộ mới)
**Bước 0, thiết kế bộ (ghi trong câu trả lời cho người dùng hoặc `brief.md`; viết trước khi vẽ, theo `fal-image/preflight.md`):**
1. **Một lưới = một tộc/hệ.** Lấy hệ từ `lib-fx/element/` (lửa, băng, sét, độc, cây, đất, nước, gió) để fx và kỹ năng sau này khớp. Một dòng màu chủ đạo (hue riêng, không trùng tộc khác, 4 giá trị hex), một dòng ấm chung cho da/da thuộc/gỗ, một màu nhấn (mắt, giọt, đốm). Tộc đã làm: Độc (tím 285°, nhấn lục độc, xem `prompts/lineup-grid-poison-clan.txt`). Các hệ kế tiếp gợi ý: lửa ~8°, băng ~195°, sét ~52°, cây ~110°, đất ~35°, nước ~220°, gió ~165°.
2. **10 con xếp theo cấp**: hàng trên từ thấp đến cao, hàng dưới từ thấp đến cao (hoặc hai hàng là lính và tinh nhuệ). Mỗi con: tên, cấp (`{H}`), thân (brawny / agile / slender), một vũ khí cầm thấp bên trái ảnh hoặc tay không, hai chân hai tay (không nhện, rắn).
3. **Bảng chiều cao đích** từ cấp (xem bảng dưới).

**Bảng cấp, kích thước và bố cục lưới** (`{H}` theo `fal-image/format.md` §7; clip 768P, 24 fps):
| Cấp | `{H}` @1x | Cao @2x = cao trong clip 768P | Dùng cho class |
|---|---|---|---|
| XS | 24 | ~48 px | enemy nhỏ (spiderling, imp) |
| S | 40 | ~80 px | enemy S (mặc định), ally S (mặc định), hero S, flying S |
| M | 60 | ~120 px | enemy M, ally M, hero M (mặc định), flying M (mặc định) |
| L | 84 | ~168 px | enemy L, ally L, hero L |
| XL | 120 | ~240 px | boss XL |
| XXL | 170 | ~340 px | boss XXL |

- **Chiều cao đích mỗi con** (`--heights`, % chiều cao ô) = cao @2x / chiều cao ô trong clip. Với lưới 5×2 ở 768P (ô cao 384): XS 0,12, S 0,21, M 0,31, L 0,44. **Giới hạn:** con lớn nhất không quá ~44% chiều cao ô (còn chỗ giơ vũ khí lên). Vượt quá thì đổi bố cục:
  - Có XL: một hàng, 3 cột (ô 448×768, XL ≈ 31% chiều cao ô). Có XXL: một hàng, 2 cột (ô 672×768, ≈ 44%). Mỗi clip vẫn $0,12 nên giá mỗi boss cao hơn ($0,04-0,06). **Chưa thử**; dùng `--cols 3 --rows 1`.
  - **Con nhỏ (XS, S) phóng to lúc làm video** (XS 0,22, S 0,27) để video làm đúng chuyển động, rồi thu nhỏ lại khi tách khung (hệ số 0,55 và 0,78). Bước thu nhỏ: `lineup_split.py --scales ...` (hệ số theo thứ tự đọc).
- **Lưới 5×2, ô 512×720 ở ảnh gốc**; ảnh 2560×1440 là cố định cho mọi class.

**Khác biệt theo class** (đã đọc `classes/*.md`; chỉ enemy đã chạy thật):
| Class | Hướng | Động tác cần | Ghi chú cho lưới |
|---|---|---|---|
| enemy (đã chạy) | 3 hướng: side, down, up | walk ×3, attack, death (ranged: thêm shoot + ảnh đạn) | lưới side chạy được. Walk down và up cần lưới đã vẽ mặt trước và mặt sau (hai lưới nữa) — chưa thử. Đi bộ trên lưới chưa đặt lại ô trôi khỏi ô; đặt lại ô rồi mới thử lại |
| ally | 1 hướng: side | walk, attack, death | giống enemy side, hợp nhất cho lưới (ít hướng) |
| enemy-flying | 3 hướng | bay, attack, death | không có đường đất: thân lơ lửng ~1/3 ô trên mặt đất; chưa thử. `--feet` phải nâng lên khoảng 0,55-0,60 và cánh sải ngang làm chiều rộng lớn hơn, dùng ô rộng hơn |
| hero | side | run, attack, death, skill | mỗi hero thường duy nhất và có skill + vfx: dùng lưới chỉ cho các clip thân (run, attack, death); canvas M rộng 176×140 nên ô rộng hơn khi vũ khí dài. Chưa thử |
| boss | 3 hướng | idle, attack, death, skill | XL, XXL: bố cục một hàng như trên. Chưa thử |

**Việc cần làm cho mỗi bộ mới (theo thứ tự):** (0) ghi thiết kế bộ → (1) prompt lưới + lint sạch → hỏi "yes" vẽ → xem từng ô → (2) đặt lại ô → (3) với mỗi động tác: viết prompt chuyển động, liệt kê trong chat, dry run, hỏi "yes" kèm số tiền, chạy → (4) tách khung, xem ảnh kiểm → (5) chọn khung, thu nhỏ theo cấp, nhập asset.

## Tóm tắt một dòng mỗi bước
| Bước | Việc | Công cụ | Vào → ra | Tiền |
|---|---|---|---|---|
| 1 | Vẽ lưới, mỗi con nằm giữa ô của nó | `gen_image.py` | prompt → PNG 2560×1440 | ~$0,019 |
| 2 | Đặt lại ô: thu nhỏ, đặt giữa ô, chừa khoảng trống | `lineup_regrid.py` | PNG → PNG 2560×1440 | 0 |
| 3 | Một clip cho mỗi động tác | `fal_video.py` | PNG + prompt → mp4 | $0,12 / clip |
| 4 | Tách khung từng con, xóa nền (+ công cụ tẩy từng khung, chưa làm) | `lineup_split.py` | mp4 → 10 thư mục khung | 0 |
| 5 | Chọn khung, xuất bản cuối | xem ảnh kiểm; `video_to_sheet.py` | khung → sheet | 0 |

## Bước 1. Vẽ lưới (nhân vật nằm giữa từng ô)
- **Ảnh:** gpt-image-2, `--quality low`, `--size 2560x1440` (16:9, chia hết cho 16), `--png`, nền magenta #FF00FF. Thời gian vẽ đo được 22-26 giây.
- **Lưới:** 5 cột × 2 hàng, mỗi ô 512×720 px. Con 1-5 hàng trên, con 6-10 hàng dưới, trái sang phải.
- **Prompt lưới** (~7.000 ký tự; bản đã chạy: `prompts/lineup-grid-10-enemies.txt`; đổi roster thì sửa 10 đoạn nhân vật, giữ nguyên phần quy cách ô và style):
  - mở đầu: "TEN different enemy sprites in a strict grid of 5 columns by 2 rows, each in its own invisible cell";
  - mọi con SIDE VIEW quay sang PHẢI, đứng thẳng (UPRIGHT), hai chân trên một đường đất, `TWO ARMS`, `TWO LEGS`, mặt ít nét;
  - mỗi con: tên, thân (brawny / agile / slender), vũ khí cầm thấp bên trái ảnh, **bảng màu hex riêng** (bóng, nền, sáng, điểm sáng nhất); vũ khí dài cầm chéo, không dựng đứng;
  - quy cách ô: "con ở giữa ô, chừa khoảng trống hai bên và phía trên, không vũ khí nào chạm ô bên cạnh";
  - đuôi prompt: câu nền magenta, câu style chunky của `style-chunky.md` §7;
  - chạy `python scripts/prompt_lint.py <prompt> --body brawny`: không được có ERROR (đừng viết "magenta" ngoài câu nền).
- **Giới hạn đã đo:** model bỏ qua phần trăm trong prompt. Xin chiều cao 55% / 36% / 24% ô đều cho ra 50-70% ô (gấp ~2 lần số xin ở mức 24%). Vì vậy việc "nằm giữa ô và có khoảng trống" được bảo đảm ở bước 2 bằng code, không bằng prompt. Style cũng drift khỏi chunky (nhiều chi tiết, bóng mềm hơn).

## Bước 2. Đặt lại ô (thu nhỏ, giữ độ nét)
`python scripts/lineup/lineup_regrid.py lineup_vNN.png --out lineup_vNN_regrid.png --scale 0.68 --feet 0.70`

| Thông số | Giá trị | Vì sao |
|---|---|---|
| Kích thước ảnh ra | 2560×1440 (giữ nguyên) | cùng tỉ lệ 16:9 để clip giữ khung hình |
| Ô | 512×720 | 2560 / 5, 1440 / 2 |
| Thu nhỏ `--scale` | 0,68 | nhỏ hơn thì clip 768P không còn đủ điểm ảnh (xem bảng cỡ), lớn hơn thì các con dính nhau |
| Đường chân `--feet` | 0,70 × cao ô = 504 px từ đỉnh ô | chừa ~30% chiều cao ô phía trên đầu cho vũ khí giơ lên |
| Tâm ngang | giữa ô (256 px) | mỗi con cách mép ô 26-30% |
| Kết quả | mỗi con cao 31-41% ô (223-295 px), rộng 40-49% ô (205-250 px), vũ khí tính vào | đo trên lưới v03 |

- **Giữ nhân vật gốc:** script chỉ cắt, thu nhỏ bằng LANCZOS và dán lại; không vẽ lại gì. Màu, nét và thiết kế của từng con giữ nguyên.
- **Độ nét:** cỡ sprite đích là `{H}` = 60 px @1x (120 px @2x). Qua chuỗi dưới đây mỗi con còn ~120-157 px cao ở clip 768P, tức xấp xỉ gốc @2x, không phải phóng lớn nên không nhòe. Xuống `--scale` ~0,5 thì chỉ còn ~95 px, phải phóng lên cho @2x và sẽ mềm.
- **Viền:** kiểm bằng cách phóng to: sạch, không viền hồng.

## Bước 3. Clip cho mỗi động tác
`python scripts/fal_video.py video --model h3-max-turbo --prompt-file <prompt> --reference lineup_vNN_regrid.png --duration 4 --resolution 720p --out-dir <thư mục>` (hỏi "yes" kèm số tiền trước khi chạy).

| Thông số | Giá trị đã đo |
|---|---|
| Model / endpoint | `minimax/h3-max-turbo/image-to-video` |
| Độ phân giải | `720p` trong CLI = 768P. Clip ra **1344×768** (không phải 1280×720), 24 fps |
| Thời lượng | xin 4 giây, ra 4,458 giây = **107 khung** |
| Khung đầu | ảnh lưới đã đặt lại ô. Tấn công và chết: KHÔNG gửi khung cuối (giữ tư thế cuối). Đi bộ: gửi `--last-frame` trùng ảnh đầu để lặp vòng |
| Giá | 768P $0,03/giây → **$0,12** cho 4 giây. 1080P: $0,06/giây → 5 giây $0,30 (clip ra 1920×1080, 124 khung) |
| Thời gian chờ | 768P 4 giây: ~4 giây; 1080P 5 giây: 7-13 giây |
| Ô sau khi cắt (768P) | 1344 / 5 × 768 / 2 = **268×384** (1080P: 384×540) |
| Cỡ mỗi con trong clip 768P | ô 384 / 720 = 0,533 so với ảnh lưới → cao ~119-157 px, rộng ~110-133 px |

**Prompt chuyển động** (bản đã chạy: `prompts/motion-attack-overhead.txt`, `prompts/motion-die-in-place.txt`; đi bộ chưa có bản dùng được; theo `fal-image/action-planes.md` §9; liệt kê trong chat để duyệt trước khi chạy):
1. Hệ quy chiếu: "Left and right are the screen's"; hướng tiến = sang phải màn hình; mục tiêu ngoài khung bên phải.
2. Mỗi con **đứng tại chỗ**: "stays inside its own cell, feet never slide, never moves into another character's space". Chết: "ngã tại chỗ, không văng, không trượt".
3. Một chuỗi động tác liên tục, bắt đầu từ hông; **gắn tên vũ khí cho từng con** (mace với Knight, ...); con tay không (Wolfman, Golem) đứng riêng một câu.
4. Kết thúc và giữ tư thế cuối, không quay lại, không đòn thứ hai.
5. Giữ thiết kế, "no tail"; nền magenta cố định, không hiệu ứng, không chữ, camera cố định.

## Bước 4. Tách khung từng con
`python scripts/lineup/lineup_split.py clip.mp4 --out <thư mục> --pad 64 --names rust_knight,dune_raider,ash_wolfman,quarry_ogre,moss_troll,bog_hag,drowned_marauder,bone_reaver,gloom_monk,scrap_golem`

| Thông số | Giá trị |
|---|---|
| Lưới cắt | 5 cột × 2 hàng, cắt cố định (rộng clip / 5, cao clip / 2) |
| Nới ô `--pad` | 64 px mỗi phía ở 768P (ô 268×384 → cửa sổ **396×512**). Ở 1080P dùng 96 (576×732) |
| Số khung `--frames` | 13 khung mỗi con, lấy đều trên cả clip (cách nhau ~8,8 khung = 0,37 giây ở 24 fps). Muốn dày hơn: `--step 3` (≈ 36 khung, 8 khung/giây) |
| Phát xem trước | `--fps 12` (13 khung ≈ 1,1 giây) |
| Neo | chân (đáy hình bóng khung đầu) tại y = 64 + 0,88 × 384 = **402 px**, tâm ngang tại x = 198 px của cửa sổ; một phép dịch cố định cho cả bộ khung, không căn lại từng khung |
| Xóa nền | điểm magenta = min(R,B) − G; viền mềm, khử hồng ở rìa |
| Bỏ mảnh lạ | giữ mảnh lớn nhất qua cột giữa cửa sổ + mảnh cách nó ≤ `--gap` 14 px |
| Ra | `<tên>/frames/f01..f13.png` (RGBA 396×512), `sheet.png` (5148×512), `preview.gif` |

**Công cụ xem và xóa từng khung (CHƯA làm, đặc tả để làm sau; người dùng sẽ thử thêm trước khi làm).**
- **Vì sao:** ba bộ khung đã có mảnh dính mà script tự động không xóa được: vệt chém hình cung dính vào vũ khí (Hỏa Tộc tấn công: Goblin, Salamander, Duelist, Spark Imp, khung 5), vũ khí hoặc thân của hàng xóm dính liền (Độc Tộc tấn công khung giơ lên), vệt hồng còn sót ở đầu vũ khí. Một trang xem được tất cả khung cũng tiết kiệm token vì không phải đọc nhiều ảnh lớn qua chat.
- **Nền có sẵn:** `tools/frame_tuner/` (bật/tắt khung, thời gian, công thức lưu `export_recipe.json`, chạy cục bộ bằng `serve.py`, xem `docs/tools/frame_tuner/frame-tuner-guide.md`). Mở rộng tool đó thay vì viết tool mới; nguồn dữ liệu là `out/<class>/_lineups/<tộc>/frames/<động tác>/<con>/frames/fNN.png`.
- **Cần có:**
  1. Một lưới xem: mỗi hàng một con, mỗi cột một khung (13), nền ca-rô hoặc xám đậm, kèm tên con; chọn động tác (tấn công, chết, đi bộ); xem trước phát cả bộ ở 12 fps.
  2. Đánh dấu tự động khung nghi ngờ: cảnh báo của `lineup_split.py` (chạm mép cửa sổ), vùng màu hồng còn sót, nhiều mảnh rời hoặc mảnh liên thông lớn thứ hai, diện tích đổi đột ngột so với khung kề.
  3. Với một khung được chọn: bấm một mảnh liên thông để xóa; cọ hoặc vòng chọn để xóa vùng; hoàn tác; "chỉ giữ mảnh này"; áp cùng thao tác cho khung kề (vị trí tương tự); bỏ cả khung (tắt) hoặc thay bằng khung kề.
  4. **Không phá bản gốc:** mọi chỉnh sửa lưu thành `edits.json` (khung, thao tác, tọa độ) cạnh bộ khung; `apply_edits` dựng lại PNG từ clip gốc và công thức, để chạy lại khi đổi `--scales` hoặc khử hồng.
  5. Xuất: bộ khung sạch, `sheet.png`, `preview.gif`; cập nhật `meta.json` của tộc (số khung bỏ, lý do).
- **Đo khi làm xong:** thời gian xử lý một bộ 10 con × 13 khung bằng tay so với số khung cần chạm; token đọc ảnh so với cách đọc ảnh kiểm hiện tại.

## Hình dáng theo loại quái (vai trò đọc được từ hình bóng)
Thử ngày 2026-11-26 trên Hàn Tộc (`out/enemies/_lineups/ice/`). Mỗi vai một kiểu thân; viết dáng bằng số và hình khối, tránh các chữ làm model đổi thân (`stout, massive, huge, round` đẩy về dáng mập: lint báo khi `--body slender`).
| Vai | Thân | Dáng nói trong prompt |
|---|---|---|
| Cận chiến thường | trung bình, ~3,8 đầu | vai vừa, tay chân cân đối, một vũ khí cầm thấp |
| Pháp sư, shaman | slender (shaman gù) | áo choàng thắt eo xòe gấu, mũ trùm, trượng ngắn không cao hơn đầu |
| Cung thủ, phóng lao | slender, ~4 đầu | cao mảnh, tay chân dài, vai hẹp, cung cầm thấp / lao chếch 40° đầu lao không cao hơn đỉnh đầu |
| Sát thủ | agile, ~4,3 đầu | nghiêng về trước, nhiều góc nhọn, khăn quàng, hai dao |
| Đấu sĩ, tank | brawny, ~3 đầu | thân vuông như golem, vai vuông, nắm đấm khổng lồ, chân ngắn dày, trọng tâm thấp |
| Thủ lĩnh | cao oai vệ | ~4,2 đầu, đầu ~22% chiều cao, chân ~45%, vai góc cạnh gai nhọn, eo hẹp, đứng thẳng ưỡn ngực, áo choàng dài, mũ sừng cao, "không bụng, không hình tròn" |
Nguyên tắc tra cứu: mỗi vai một ngôn ngữ hình khối (tank rộng và vuông, kẻ nhanh góc cạnh và nghiêng về trước, hỗ trợ mềm), hình bóng phải đọc được ở cỡ nhỏ, thứ bậc yếu-mạnh phải rõ ([RocketBrush](https://rocketbrush.com/blog/shape-language-in-game-character-design-how-to-make-characters-readable-and-consistent), [The Level Design Book](https://https-book_leveldesignbook_com.proxy.bugsmash.io/process/combat/enemy), [CG Wire](https://blog.cg-wire.com/character-shape-language/)). Không có tài liệu chuẩn về tỉ lệ từng vai; các con số trên là của dự án, đo trên ảnh vẽ để chỉnh.
- **Bài học Hỏa Tộc:** `Flame Drake` bị vẽ thấp, tròn (prompt chỉ ghi "four legs, folded wings"). Thủ lĩnh và boss phải ghi kiểu "cao oai vệ" như trên.
- **Sửa riêng một hai con mà không vẽ lại cả lưới:** vẽ lại các con đó trong một tờ nhỏ (một hàng, mỗi con to ~70% ô nên chi tiết rõ nét hơn trong lưới 10 con), rồi `python scripts/lineup/lineup_replace.py <lưới>.png --new <tờ nhỏ>.png --cell <ô cần thay> --pick <thứ tự con mới> --out <lưới mới>.png`. Script xóa con cũ, thu con mới về cùng diện tích và đặt cùng chân, cùng tâm; các con còn lại giữ nguyên. Hàn Tộc: Icicle Stalker và Frost Warlord (`prompts/lineup-pair-ice-assassin-warlord.txt`).
- **Hồng trên nhân vật:** model đôi khi vẽ một phần hồng (quần của Icicle Stalker) dù đã cấm; khóa nền ăn mất phần đó. Chạy `python scripts/lineup/lineup_fix_pink.py <lưới>.png --out <lưới_sửa>.png` trước khi đặt lại ô.

## Bước 5. Bản cuối (và nơi lưu)
0. **Lưu lên git** (thư mục `.work/` bị git bỏ qua, mất khi phiên kết thúc): ảnh lưới, bản đặt lại ô, clip gốc và bộ khung đã tách đi vào `out/<class>/_lineups/<tộc>/` (xem `docs/repo-structure-rules.md`); `meta.json` ghi tham số để phiên khác làm tiếp. Đã có `out/enemies/_lineups/poison/` (tấn công và chết) và `out/enemies/_lineups/fire/` (mới có lưới).
1. Mở ảnh kiểm (6-8 khung mỗi con, thu nhỏ 1/3); bỏ khung sai vũ khí, dính hàng xóm hoặc viền hồng, và khung cuối của clip tấn công (nó quay về dáng đứng).
2. Con nào giữ: nhập vào asset thật (`scripts/ingest_image.py`, `brief.md` có manifest), rồi `scripts/video_to_sheet.py` đưa khung vào canvas chuẩn của class (enemy tier M: 136×120 @1x, `{H}` 60 px). Rồi `video_prune.py`, `motion_check.py`.
3. Dọn bằng `scripts/source_prune.py`; không để bản thử trong repo; chi phí chỉ ghi ở `out/costs.csv`.

## Tổng chi phí và thời gian một lưới
| Hạng mục | Tiền | Thời gian đo |
|---|---|---|
| Lưới (1 ảnh) | $0,019 | 22-26 giây |
| Đặt lại ô | 0 | vài giây |
| Mỗi động tác (clip 768P 4 giây) | $0,12 | ~4 giây chờ fal |
| Tách khung | 0 | vài giây mỗi clip |
Ví dụ 10 con × 2 động tác: $0,019 + 2 × $0,12 ≈ **$0,26**, khoảng $0,013 mỗi con mỗi động tác (làm từng con riêng: ~$0,12 mỗi con mỗi động tác).

## Lưới nhiều cấp kích thước (Độc Tộc, thử ngày 2026-11-26)
Khi 10 con khác cấp (`{H}` 24 / 40 / 60 / 84 px), mỗi con có chiều cao đích riêng theo `lineup_regrid.py --heights` (% chiều cao ô, thứ tự đọc). Chạy thật:
- **Tỉ lệ đúng cấp** (tính ra @2x ở clip 768P): XS 0,12, S 0,21, M 0,31, L 0,44. Con XS chỉ còn ~46 px trong clip nên video làm mờ, gần như không cử động.
- **Đã dùng cho video: phóng to các con nhỏ**: `--heights 0.22,0.22,0.27,0.27,0.27,0.31,0.31,0.31,0.44,0.44` (XS 0,22 ≈ 85 px, S 0,27 ≈ 104 px trong clip). Để video làm đúng hơn, khi tách khung xong sẽ thu nhỏ lại từng cấp về cỡ đúng: hệ số **XS 0,12 / 0,22 = 0,55; S 0,21 / 0,27 = 0,78; M và L giữ 1** (đã làm: `lineup_split.py --scales 0.55,0.55,0.78,0.78,0.78,1,1,1,1,1`, thu nhỏ cả khung quanh điểm neo chân sau khi cắt; kết quả đo trên 20 bộ khung Độc Tộc: cao 47, 46, 79-81, 118-120, 168-170 px, chân vẫn ở y = 402, khớp @2x của từng cấp: 48, 80, 120, 168).
- Gán ô theo THỨ TỰ trong hàng (model không đặt đúng cột): mỗi hàng lấy 5 mảnh lớn nhất, từ trái sang phải.
- Prompt: `prompts/lineup-grid-poison-clan.txt`, `prompts/motion-attack-poison-clan.txt`, `prompts/motion-die-poison-clan.txt` (thêm câu "giữ đúng cỡ của mình" và "no tail, trừ Plague Rat").

## Kết quả đã đo và việc còn lại
- **Chết:** sạch, 10/10 không dính nhau (lưới đã đặt lại ô, h3-max-turbo 768P 4 giây).
- **Tấn công:** đòn chém và tư thế giữ sạch; nhịp giơ lên (khung 3-5) có vũ khí lạ (Wolfman cầm búa, Monk cầm rìu). Cần công cụ tẩy từng khung hoặc chạy lại.
- **Đi bộ:** chưa chạy với lưới đã đặt lại ô. Clip đi bộ trên lưới khít (ô 1080P) đã trôi khỏi ô và không dùng được.
