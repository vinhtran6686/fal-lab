# Handoff 3: holy_commander, phiên tiếp theo (2026-10-20)

Phiên trước (cloud, nhánh `claude/holy-commander-export-ld6594`) export 4 trạng thái, thu phản hồi của user, nhưng
**không có `FAL_KEY`** nên chưa quay clip nào. Phiên mới cần `FAL_KEY` (user đã thêm vào environment; chỉ có hiệu
lực ở phiên mới). Kiểm tra: `[ -n "$FAL_KEY" ] && echo set` (không in giá trị). Network policy phải cho phép host fal API
và `*.fal.media`.

Đọc theo thứ tự: `docs/handoff-holy-commander-2.md`, `docs/holy-commander-report.md` (đặc biệt §9-§11),
`out/heroes/holy_commander/history.md`, `brief.md`, `docs/issue-frame-recipe-sync.md`.

## 1. Quy tắc phiên (user đặt)
- **Không sửa `SKILL.md`** (user tự sửa sau). Chỉ ghi vào `history.md`, `brief.md`, report.
- **Không cắt/bớt frame thêm trong phiên này** (làm sau, theo issue). Quay clip 3-4 s, đủ động tác, giữ nguyên frame.
  (Lý do: rút ngắn `--duration` làm model cắt mất động tác, xem attack t05/t06. Cắt frame sau khi clip đạt thì animation nhanh hơn, nhưng để phiên sau.)
- Cost guard: báo số clip + giá, chờ user "ok" trước mỗi lần chạy trả phí. `--quality low`; clip ~0.06 USD (h3-max-turbo, 4 s).
- Mỗi take: tách + key frame, user duyệt bằng mắt, ghi `history.md`, cập nhật manifest trong `brief.md`.
- User không có PC/source local, chỉ xem được qua artifact. Với respawn, đăng lên **một artifact mới riêng**
  (không đụng artifact compare https://claude.ai/artifact/MxiAuzsxrmnLt7EgZm1JCj).

## 2. Quyết định user đã đưa
| Chủ đề | Quyết định |
|---|---|
| Hiệu ứng skill 2/3 | Thử CẢ HAI: (a) vẽ thẳng vào thân như charge_v4, (b) thân sạch + `fx_layers`; rồi so |
| Vòng lửa charge_v4 | Giữ bản này; đồng ý là lỗi; lần sau dùng hiệu ứng vừa khung hơn |
| Tốc độ export | Giữ đúng bản đã duyệt (attack 1530 ms, death 2600 ms), không rút ngắn clip |
| Canvas | Nới 156x140 -> **176x140** (nhát chém attack không vừa). run/idle đã đệm lại |
| Vệt chém trắng ở attack | Thích, giữ; user sẽ sửa skill để cho phép (không còn coi là lỗi) |

## 3. Trạng thái hiện tại
| Trạng thái | Tình trạng |
|---|---|
| idle, run | ✅ (canvas 176x140) |
| attack | ✅ 23 hình, 1.53 s, hit frame 10 (t04 bớt 1/2 frame) |
| death | ✅ 39 hình, 2.60 s (t01 bớt 1/2 frame) |
| charge_v4 | ✅ 67 hình, 4.47 s, còn vòng lửa lớn ~frame 46-72 và hình lạ cạnh vai ~frame 5 |
| respawn | export bản đảo despawn (78 hình, 5.2 s) nhưng **user chê** (giống pho tượng cứng nhắc): làm lại hoàn toàn |
| levelup | thiết kế mới, cần clip mới (t01 cũ không dùng) |
| holy_banner, radiant_slash | thiết kế lại hoàn toàn (t01 zoom + hiệu ứng vẽ vào thân) |

Body 111 (area-matched, rescale ~x1.09 theo frame nghỉ), pivot (0.5, 0.88), canvas 176x140, meta.json đã cập nhật.

## 4. Việc phải làm, theo thứ tự
1. **Respawn mới** (user bảo bắt đầu ngay):
   - Thiết kế: bắt đầu **quỳ**, **gục đầu vào thanh kiếm dựng đứng**, **cả hero màu xám**; sau đó **hồi màu** rồi **đứng lên** (vừa được khôi phục).
   - Cần ảnh tĩnh `pose_respawn` (chưa có): `gen_image.py`, ref master_v07, quality low (~0.014 USD/ảnh, 2-3 ảnh nháp), user chọn.
   - Clip `rise` (side_extra, từ `pose_respawn` đến master, `endStill` = master), **4 s**, h3-max-turbo, ~3 take (~0.18 USD). Prompt tách nhịp: giữ quỳ xám, màu hồi dần, ngẩng đầu, chống kiếm đứng dậy, kết bằng master. Câu "locked tripod" lấy từ `raw/skill_side_skill_charge_v2_t01.json`. Không nhắc hiệu ứng ngoài chuyển màu.
   - Nếu model không chuyển xám -> màu: đề xuất xám hoá các frame đầu rồi hồi màu dần bằng hậu kỳ (miễn phí), hỏi user trước.
   - Export `respawn_side` (canvas 176x140), đăng artifact riêng để user xem.
2. **Levelup mới**: hero đứng, đấm một tay lên trời như chiến thắng/đạt thành tựu; ánh sáng chớp quanh người theo nhịp vung tay. Hiệu ứng ánh sáng: theo quyết định A (thử cả hai). `fx/levelup.json` (pillar hoặc burst).
3. **holy_banner và radiant_slash**: thiết kế lại hoàn toàn dựa trên bài học charge_v4 (tách nhịp có thứ tự, chỉ dồn về trước, "locked tripod", hiệu ứng nhỏ sát vũ khí/nắm đấm). **Ý tưởng chi tiết chưa chốt**: hỏi/đề xuất cho user trước khi quay. Endstill: `pose_skill_holy_banner_v01`, `pose_skill_radiant_slash_v01`. Ước tính ~0.25-0.40 USD mỗi skill.
4. Cuối mỗi bước: `video_prune.py` nếu có set hợp lệ (set `.work` không có trong git), publish artifact.

## 5. Kỹ thuật cần biết
- **`.work/` không có trong git**: `video_to_sheet.py` chỉ đọc set đã finish. Phiên trước dùng `tools/kr_compare/export_frames.py` (set tạm `.work/side_export`, frame từ `tools/kr_compare/sprites/holy_commander/<state>/`, scale 120/268, neo chân frame 0 tại (256,400) trên canvas 512x512, 67 ms/frame, hit 40%) rồi `video_to_sheet.py --kind hero --sheet <sheet>`. Với clip mới, tách bằng `ffmpeg fps=15` + `sprite_pack.key_out()`. Công thức cần được ghi chuẩn (issue).
- Đệm run/idle lên 176x140 bằng script tạm (lossless @2x; @1x tính lại từ @2x).
- Phiên trước cài thêm `scipy` bằng pip để chạy script; `static_ffmpeg` không có (dùng `ffmpeg` hệ thống).
- `tools/kr_compare/build_manifest.py` cần repo KR1 ở `E:\` và `static_ffmpeg`: không chạy được trong cloud. Artifact compare cập nhật bằng cách chạy trên máy user (hoặc bỏ qua).
- Skill: `fal-image` (stills) và `video-sprite` (clip); các lệnh trong `CLAUDE.md` và `.claude/skills/video-sprite/SKILL.md` (bảng Tools).

## 6. Bài học (chưa có trong SKILL.md; xem handoff-2 §2)
1. Chỉ dồn người về phía trước, không nói "ngả/dồn ra sau" (model đọc thành xoay người).
2. `--duration` có ngưỡng dưới theo số động tác (combo 2 nhát cần 3 s). Đừng quay ngắn.
3. Tăng tốc = bớt frame của take đã đạt, không quay lại video (phiên sau).
4. Vệt chém trắng ở attack: chấp nhận, không loại take vì nó.
5. Hiệu ứng vẽ vào thân (lửa, vòng) dễ ra vòng lớn/zoom; "locked tripod" chỉ hiệu quả khi prompt không mời hiệu ứng.

## 7. Prompt khởi động phiên mới (dán nguyên)
```
git pull origin claude/holy-commander-export-ld6594. Đọc docs/handoff-holy-commander-3.md trước, rồi
docs/holy-commander-report.md (§9-§11), out/heroes/holy_commander/history.md và brief.md.
Kiểm tra FAL_KEY có trong môi trường (không in giá trị).
Việc đầu tiên: làm respawn mới (quỳ gục đầu vào kiếm dựng đứng, hero xám -> hồi màu -> đứng lên), clip 4 s.
Báo giá trước khi chạy ảnh/clip trả phí và chờ mình ok. Không sửa SKILL.md, không cắt frame thêm.
Xong thì đưa lên 1 artifact riêng (không đụng artifact compare) để mình xem.
```
