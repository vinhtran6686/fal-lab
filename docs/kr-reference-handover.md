# Handover: phân tích thiết kế nhân vật từ game tham chiếu (KR) và đối chiếu với fal-lab

Viết ngày 2026-10-19 để một session khác đối chiếu với fal-lab và làm tiếp. Tài liệu này chỉ giải thích
và đối chiếu, không đặt ra luật mới: luật hiện hành nằm trong skill (`fal-image/format.md`, `classes/*.md`,
`video-sprite/SKILL.md`), và số đo gốc nằm trong `fal-image/reference.md`.

> **Quy tắc giữ nguyên:** không ghi tên game tham chiếu hay tên nhân vật của nó vào file skill hoặc prompt.
> Tài liệu này là ghi chú trong `docs/` nên được phép gọi tắt là "KR". `ref/` chỉ để nhìn, không bao giờ gửi lên API.

## 0. Nguồn dữ liệu

| Nguồn | Nội dung | Nằm ở đâu |
|---|---|---|
| A. Atlas asset của game | 112 nhân vật có frame (hero, lính, quái, boss): tên animation, số frame, kích thước, alias | `data.json` trong artifact atlas của user; số đã tóm tắt ở `fal-image/reference.md` |
| B. Tài liệu đọc từ code đã decompile | cách game chọn hình theo góc, ý nghĩa từng trạng thái, anchor, fps, các mẫu mở rộng | file user gửi ("Thiết kế bộ asset nhân vật theo chuẩn Kingdom Rush"); nội dung chính chép lại ở §1-§4 bên dưới |
| C. Một hero mẫu trong repo | đòn đánh của hero lửa (fire elemental): 19 frame, 30 fps, canvas 86x102, thân ~51x64 | `ref/hero/` (`frames/`, `manifest.json`) |
| D. Đo hiệu ứng trên atlas (2026-10-19) | số hình vẽ thật mỗi animation, cách ghép lớp hiệu ứng | kết quả nằm trong `video-sprite/SKILL.md` "Body clips and effect layers" |

## 1. Luật lõi của game (từ code)

1. **Chỉ di chuyển mới có nhiều hướng.**
   - Quái đi bộ, quái bay và boss vẽ 3 hình đi: ngang (`walkingRightLeft`), lưng (`walkingUp`), mặt (`walkingDown`).
   - Hướng trái là hình ngang lật lại. Không có hình chéo.
   - Hero và lính phe mình chỉ có 1 hình chạy ngang (`running`), lật khi đi sang trái.
2. **Mọi trạng thái khác** (idle, attack, death, skill) chỉ vẽ 1 hình nhìn ngang; game lật trái/phải để quay về phía mục tiêu.
3. **Chọn hình đi theo góc phần tư**, với độ "dính" 10° để khỏi giật hình ở khúc đường chéo:

   | Góc (0° = sang phải, 90° = đi lên) | Hình | Lật |
   |---|---|---|
   | 315°-45° | ngang | không |
   | 45°-135° | lưng (up) | không |
   | 135°-225° | ngang | có |
   | 225°-315° | mặt (down) | không |

   Hệ quả: hình lưng và hình mặt phải trông ổn cả khi nhân vật thật ra đang đi chéo tới 45°.
4. **`idle` chỉ là 1 frame tĩnh** với quái đi bộ, boss, hero và lính. Riêng quái bay có idle động (lơ lửng).
5. **30 fps, đa số vẽ "on twos"**: mỗi hình giữ 2 frame (frame thứ hai là alias), nên thực chất khoảng 15 hình mỗi giây.
   - Hero mẫu (C): đòn đánh 19 frame nhưng chỉ có 10 hình thật.
6. **Một khung và một điểm neo cho mọi trạng thái** của cùng nhân vật; lệch thì nhân vật nhảy lên xuống khi đổi trạng thái.
   - Anchor (điểm chạm đất) cách đáy khung 0.10-0.25, trung vị 0.18.
7. **Không có trạng thái "bị đánh" (hurt)** ở bất kỳ lớp nào.

## 2. Ma trận lớp nhân vật

| Lớp | Di chuyển | Lõi | Phản ứng chung | Theo vai trò | Kỹ năng |
|---|---|---|---|---|---|
| Quái đi bộ | 3 hình | idle (tĩnh), attack, death | thorn, thornFree (bị dây gai trói) | shoot nếu đánh xa, raise nếu được triệu hồi | hiếm (22/41 không có) |
| Quái bay | 3 hình bay | idle động, death (thường không có attack) | không | shoot | hiếm |
| Boss | 3 hình (vài con chỉ có ngang) | idle, attack, death (+ death_end nếu chết 2 pha) | không | shoot | 0-3 (đa số 1) |
| **Hero** | **1 hình `running`** | idle, attack (+ attack2) | không | **respawn, levelup**, shoot nếu đánh xa | **2-3** (có hero tới 7-9) |
| Lính phe mình | 1 hình `running` | idle, attack (+ attack2) | không | shoot, raise | hiếm (lính tinh nhuệ 2-3) |

Các mẫu mở rộng có sẵn trong game:
- `attack2` / `idle2`: biến thể để đỡ lặp.
- `death` + `death_end`: boss chết 2 pha (ngã, rồi nằm lại hoặc tan biến).
- **Biến hình:** mỗi dạng là một bộ asset gần đủ, cộng hình chuyển dạng (`toBear`, `demonTransform`).
- **Đi bộ ↔ bay:** thêm hình cất cánh và hạ cánh cho từng hướng.
- **Biến thể tốc độ:** `walking*_fast`.
- **Ngắm bắn 3 hướng:** `shootAimUp`, `shootAimDown`, `shootAimRightLeft` (một hero bắn xa).

## 3. Một HERO trong KR gồm những gì

### 3.1 Vai trò
Nhân vật có tên, mỗi màn chỉ một. Người chơi đưa hero tới một điểm trên đường để chặn quái. Hero đánh
cận chiến hoặc bắn, dùng 2-3 kỹ năng, lên cấp, chết rồi hồi sinh. Hero chỉ đi quãng ngắn nên chỉ có 1 hình chạy ngang.

### 3.2 Bộ trạng thái (15 hero trong atlas; số frame ở 30 fps, trung vị)

| Trạng thái | Số hero có | Frame | Thời lượng | Số hình thật (on twos) | Ghi chú |
|---|---|---|---|---|---|
| idle | 15/15 | 1 | - | 1 | tư thế đứng tĩnh = master |
| running | 15/15 | ~6 | 0.2 s | 5-6 | vòng chạy ngắn, lặp nhanh |
| attack | 14/15 | ~22 (12-22) | 0.75 s | ~10 | hero mẫu (C): 19 frame, 10 hình |
| attack2 | 4/15 | ~27 | 0.9 s | | biến thể đòn đánh |
| shoot | 4/15 | ~22 | 0.75 s | | hero đánh xa |
| death | 13/15 | ~9 | 0.3 s | 7-9 | ngắn |
| respawn | 13/15 | ~18 | 0.6 s | | kèm cột sáng và vòng đất (object riêng) |
| levelup | 13/15 | 18-23 | 0.7 s | | kèm hiệu ứng riêng |
| kỹ năng | 2-9 mỗi hero | 28-68 | 1-2 s | 4-13 | phần lớn là **giữ pose** trong lúc hiệu ứng chạy |

### 3.3 Kỹ năng
- Số lượng: 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 7, 9 (trung vị 2-3).
- Các kiểu kỹ năng:
  - mưa hoặc bão phép trên một vùng;
  - đập đất hoặc sóng xung kích;
  - triệu hồi;
  - biến hình;
  - buff hoặc hỗ trợ;
  - đòn vũ khí đặc biệt (lưỡi cưa, bắn nhiều tên, phản đòn, chuỗi);
  - dịch chuyển.
- Mỗi kỹ năng có 3 phần:
  1. **Thân:** động tác vào pose rồi giữ pose. Ví dụ mưa phép dài 39 frame nhưng chỉ có 13 hình; buff tháp dài 39 frame chỉ có 4 hình.
  2. **Pose đỉnh:** tư thế mà thân giữ.
  3. **Hiệu ứng:** các **object nhỏ riêng**, không vẽ vào frame thân.

### 3.4 Hiệu ứng: cách KR làm (đo 2026-10-19)
- **Cỡ thân không bao giờ đổi** trong mọi animation; camera không zoom.
- **Hiệu ứng trong frame thân rất ít và phẳng:**
  - vệt chém là một hình lưỡi liềm xám phẳng, không phải vệt mờ gradient;
  - vài cung nhỏ quanh khiên.
- **Hiệu ứng kỹ năng là nhiều object nhỏ chồng lên nhau.** Mỗi object chỉ 4-18 hình:
  - decal mặt đất: vòng elip phẳng nở ra rồi mờ;
  - tia từ trời: một đường sét mảnh;
  - nổ khi trúng: cụm hình nhỏ;
  - particle cỡ ~8x16 px, phát ra nhiều lần;
  - cột sáng cho respawn và levelup.
- Ví dụ: cú sấm của hero sét = 3 lớp (tia, nổ, tan).
- Đạn: bay 2-4 hình (ảnh xoay hoặc nhấp nháy), trúng 4-8 hình (`bolt_*_flying` / `bolt_*_hit`).
- Bóng dưới chân: một elip phẳng được vẽ sẵn trong từng frame của nhân vật đi bộ.

### 3.5 Hình dáng và style (đo trên hero mẫu C và atlas)
- **Chiều cao thân hero:** 43-77 px ở 1x, đa số 50-70.
  - Ví dụ: pháp sư 43, cung thủ 44, hiệp sĩ 52, hero lửa 64, robot cưa 77.
- **Tầm với tính từ chân** (đơn vị = chiều cao thân, phân vị 85):
  - lên trên 2.00, sang ngang 1.29, xuống dưới 0.16;
  - nên khung hero là 2.6 x 2.3 thân: chừa chỗ phía trên cho chiêu, levelup và respawn.
- **Hero mẫu C (hero lửa, 64 px):**
  - tỷ lệ: khoảng 3.8 đầu, nặng phần trên (vai và tay to, đầu nhỏ, chân ngắn);
  - mặt chỉ là một nét mày và khe mắt; tay hình găng;
  - thân 3 tông của một màu cam, viền nâu đậm (không đen);
  - lửa là các lớp vàng phẳng có viền lưỡi lửa;
  - vẽ vector lớn rồi thu nhỏ, **không phải pixel art**.
- **Palette:** hero và phe mình dùng màu chính bão hoà, sáng, kèm một màu nhấn sáng. Quái tối hơn, đục hơn, kèm một màu cảnh báo.

### 3.6 Hero trong fal-lab (thực thi của §3, `classes/hero.md` §6)
- **Ảnh tĩnh:**
  - `master` (= idle);
  - `icon`;
  - `projectile` (hero đánh xa);
  - `pose_skill_<name>` cho mỗi kỹ năng;
  - mảnh `fx` lẻ, chỉ khi hiệu ứng cần một hình có dáng riêng.
- **Clip thân:** `run_side`, `attack_side` (hoặc `shoot_side`), `death_side`, `respawn_side` (despawn phát ngược), `levelup_side`, `skill_<name>_side`.
- **Công thức lớp hiệu ứng:** `fx_respawn`, `fx_levelup`, `fx_<name>`, `projectile_fly/hit`, và vệt chém của attack.
- **Chi phí** (hero cận chiến, 2 kỹ năng): khoảng 4 ảnh + 7 clip ≈ 0.66 USD, chưa tính làm lại.

## 4. Đối chiếu KR ↔ fal-lab

### 4.1 Đã khớp

| KR | fal-lab | Ở đâu |
|---|---|---|
| Hướng: 1 hình chạy (hero, lính) / 3 hình đi (quái, boss); trái = lật; không chéo | giống | `format.md` §3, `classes/*.md` §4 |
| Góc phần tư + độ dính 10° | playtest chọn hình theo đúng luật này | `tools/playtest/index.html`, `motion.html` |
| idle = 1 frame (trừ quái bay) | idle = master, export `--rest-frame` | `video-sprite/SKILL.md` |
| Ma trận lớp, vai trò, số kỹ năng | 5 file class, mỗi file có bảng vai trò và manifest | `classes/*.md` §2, §6, §7 |
| Mẫu mở rộng | bảng mẫu mở rộng | `format.md` §9 |
| Một khung và một cỡ thân cho mọi trạng thái | `--cell`, `--target-height`, `meta.json` | `video-sprite/SKILL.md` "One canvas" |
| On twos, ít hình | plan `--fps 15`, số hình mục tiêu cho từng animation | `video-sprite/SKILL.md` "Timing" |
| Kỹ năng = vào pose rồi giữ | `endStill` = pose, pose đạt ở 40% thì giữ | `sprite_set.py` (ONESHOT_TIMING) |
| Clip thân không có hiệu ứng | lọc chữ hiệu ứng khỏi prompt, thêm câu "body only, no zoom" | `sprite_set.py` (`strip_effect_words`) |
| Hiệu ứng = object nhỏ chồng lớp | `fx_layers.py`: slash, ring, burst, bolt, pillar, particles, sprite | `scripts/fx_layers.py` |
| Respawn = chìm đất phát ngược, kèm cột sáng và vòng đất | despawn `--reverse` + công thức pillar và ring | `video-sprite/SKILL.md` |
| Bóng elip vẽ sẵn trong frame | export vẽ bóng 35% đen (hero có thể dùng màu riêng) | `video_to_sheet.py` |
| Không có hurt | không có dòng hurt trong manifest | `classes/*.md` |

### 4.2 Khác KR (có chủ ý, cần biết khi đối chiếu)

| Điểm | KR | fal-lab | Lý do / ảnh hưởng |
|---|---|---|---|
| Anchor ở chân | 0.10-0.25 từ đáy, khác nhau theo nhân vật (trung vị 0.18, tức y ≈ 0.82 từ đỉnh) | cố định y = 0.88 từ đỉnh cho mọi asset | Đơn giản hơn. Phía dưới chân chỉ chừa 12% khung, nên cú ngã khi chết dễ tràn khung hơn |
| Khung | mỗi nhân vật một khung riêng | khung tính từ class + tier (`format.md` §7) | Đo lại: 73% nhân vật KR vừa khung của profile |
| Định dạng xuất | `<tên>_0001.png` + bảng animation `from`/`to` (`game_animations`), frame alias | `out/<class>/<id>/<category>/<sheet>/frames/` + `meta.json` + `fx.json` | Chưa xuất bảng kiểu `game_animations`; chỉ cần nếu muốn chạy trong engine đã decompile |
| thorn / thornFree | "nên có" cho quái đi bộ | ⏭ cho tới khi game có tháp trói | phụ thuộc thiết kế game của user |
| Độ dài hero run | 0.2 s (6 frame) | loop lấy theo một sải chân sạch của clip | video model không cho vòng 0.2 s sạch |
| Cách làm animation | hoạ sĩ vẽ keyframe trước rồi chèn frame | video image-to-video từ master tới pose, sau đó retime | công cụ khác, mục tiêu số hình giống nhau |

### 4.3 Chưa kiểm trên clip thật (đây là việc của session test holy_commander)
- Bộ lọc chữ hiệu ứng trong prompt có thật sự giữ clip thân sạch không.
- Nhịp 15 fps và số hình mục tiêu trên sheet đã export.
- Ghép `fx_layers` lên clip thân thật (hiện mới thử trên ảnh pose tĩnh).
- Bóng dưới chân trên sheet thật, và màu bóng riêng cho hero.
- `rise` (cách thay thế cho respawn), chưa thử.
- Palette và icon chưa đặt cạnh ref để so.

## 5. Checklist khi session khác đối chiếu một hero với KR
1. Manifest trong `brief.md` có đủ các dòng của §3.6: run, attack/shoot, death, respawn, levelup, mỗi kỹ năng có pose + clip + fx.
2. Master đứng thẳng, nhìn ngang 3/4 sang phải. Khung đúng tier: hero M = 156x140 @1x, thân 120 px @2x.
3. Mọi sheet chung một `meta.json` "cell" và một cỡ thân (không zoom, không phình to).
4. Số hình mỗi sheet gần với cột "Số hình thật" ở §3.2. Kỹ năng phải có đoạn giữ pose dài.
5. Không có quầng sáng, vệt mờ hay gradient trong clip thân. Mọi hiệu ứng nằm trong `fx/<skill>/`, phẳng, có viền, mỗi lớp 4-18 hình.
6. Respawn = despawn phát ngược + cột sáng + vòng đất. Levelup = clip thân + cột sáng hoặc nổ.
7. Ghi vào `history.md` cái gì làm nhân vật trông ổn hơn (prompt, timing, lớp fx), để cập nhật skill.

Xem thêm: `docs/handoff-holy-commander.md` (trạng thái holy_commander và thứ tự test), `docs/asset-manifest.md`.
