# Puppet Kit: chuyển động từ ảnh tĩnh bằng rig cắt lớp (0 USD mỗi animation)

Cập nhật 2026-11-11. Nhánh `claude/puppet-kit`. Code: `scripts/puppet.py`, `scripts/puppet_kit/`. Ví dụ đầy đủ: `out/heroes/holy_commander/source/rig/`.

## Vì sao có kit này

Video AI (`video-sprite`) cho chuyển động đẹp nhưng không tất định: mỗi lần sửa nhịp hay tư thế là một take mới, model tự vẽ vệt cung, tự xoay người.
Puppet Kit dựng chuyển động **bằng code từ chính pixel của ảnh đã duyệt**: chạy lại ra đúng kết quả cũ, sửa nhịp là sửa số trong JSON, không gọi API.
Video chỉ còn dùng cho động tác rig 2D không làm được (xoay người, đổi mặt trang bị, chạy).

## Ba tầng

| Tầng | Nguồn | Dùng cho | Chi phí |
|---|---|---|---|
| 1. Rig cắt lớp | master + một ảnh "thân sạch" (plate) | idle, levelup, buff, hit, cast, mọi động tác thân gần tư thế master | 1 ảnh plate (~0,012 USD) cho mỗi nhân vật, một lần |
| 2. Pose-to-pose | rig + các ảnh `pose_*` của `fal-image` | attack, skill: mỗi pose là một "pose rig" một lớp (nghiêng, nén, giãn, áo choàng bay); đoạn vung là một nhát cắt, vệt chém che | ~0,015 USD mỗi pose |
| 3. Video | `video-sprite` | xoay người, chạy, ngã phức tạp | như cũ |

## Khái niệm

- **rig.json**: `sources` (ảnh), `ground` (điểm chân, px của ảnh), `unit` (số px của ảnh ứng với `body_height_2x` trong `meta.json`), `bones` (tên, cha, `pivot`),
  `parts` (theo thứ tự vẽ, sau lên trước), `ik` (chuỗi hai xương, vd. cánh tay bám theo chuôi kiếm), `sockets` (điểm bám theo xương: `weapon_root`, `weapon_tip`).
- **Part** = một vùng của một ảnh nguồn, gắn vào một xương. `select`: `{"poly": [...]}` (đa giác), `{"colour": "red", "ymin": ...}` (áo choàng theo màu),
  `{"rest": true}` (phần còn lại của ảnh). `fill_under`: vá kín phần thân nằm dưới một part khác (để khi part đó nhúc nhích không lộ lỗ).
  `grow`: kéo dài part ra dưới các part bên cạnh. `deform`: trường dao động (áo choàng, mào), biên độ tăng theo khoảng cách tới phần cứng.
- **Kênh của xương**: `rot` (độ), `tx`, `ty` (px ảnh), `sx`, `sy`, `shx` (nghiêng). Kênh của part: `sway` (hệ số biên độ), `alpha`, `grey`.
- **anim.json**: `fps`, `loop`, `hit_frame` (tính từ 1), và `shots` (mỗi shot: `rig`, `frames`, `tracks`). Track là danh sách `[frame, giá trị, ease]`
  (`linear in out inout in3 out3 step back`) hoặc `{"base": v, "osc": {"amp", "period", "phase"}}` cho vòng lặp. Frame tính từ 0 trong từng shot.
  `transitions`: cách kiếm đi qua nhát cắt giữa hai shot (`dir`: `cw`/`ccw` trên màn hình) để xuất quỹ đạo và vệt chém.

## Lệnh

```bash
python scripts/puppet.py init   out/heroes/<id> --cell 176x140 --height 120   # asset mới, chưa có meta.json
python scripts/puppet.py check  out/heroes/holy_commander/source/rig/rig.json
python scripts/puppet.py render out/heroes/holy_commander out/heroes/holy_commander/source/rig/anims/idle.json --sheet idle_side
python scripts/puppet.py render out/heroes/holy_commander out/heroes/holy_commander/source/rig/anims/levelup.json --sheet levelup_puppet_side
python scripts/puppet.py render out/heroes/holy_commander out/heroes/holy_commander/source/rig/anims/attack_diag_puppet.json --sheet attack_diag_puppet_side
python scripts/puppet.py track  out/heroes/holy_commander out/heroes/holy_commander/source/rig/anims/attack_diag_puppet.json --name slash_diag_puppet --sheet attack_diag_puppet_side --sub 4
python scripts/puppet.py slash  out/heroes/holy_commander out/heroes/holy_commander/source/rig/anims/attack_diag_puppet.json --name slash_diag_puppet --sheet attack_diag_puppet_side
```

- `check`: ghi `rig_overlay.png` (xương, đa giác, socket), `rig_parts.png` (từng lớp), `rig_rest.png` (tư thế nghỉ ghép lại, so với master) vào `<asset>/.work/puppet/`.
- `render`: xuất **một bản cuối** vào `frames/<sheet>/` đúng ô, pivot, cỡ thân và bóng chân của `meta.json`; ghi state vào `meta.json` (`"split": "puppet"`).
  Thêm `--no-export` để chỉ xem thử trong `.work/puppet/<sheet>/`.
- `track`: gốc/mũi kiếm từng frame từ socket của rig, cùng định dạng `weapon_track.json` của Milestone 01 (không cần đánh dấu tay).
- `slash`: vẽ vệt chém bằng bộ sinh layered của M01 (import, không sửa) trong vùng lưỡi quét của nhát cắt, đặt lên frame hit rồi tan. `--lag` là độ dài vệt, `--set layered.width_scale=0.8` đổi tham số.
- Cần `numpy pillow scipy`; `slash` cần thêm `opencv-python-headless scikit-image` (như Vector Kit).

## Quy trình cho một nhân vật mới

1. Có master đã duyệt (`fal-image`). Không cần vẽ lại master.
2. **Plate**: một ảnh `gpt-image-2` low, `--ref master`, prompt "giữ nguyên mọi thứ, bỏ vũ khí và cẳng tay, vẽ phần bị che" (mẫu: `source/rig/plate_v01.json`). Kiểm tra bbox và hàng chân trùng master.
3. **rig.json**: AI đọc ảnh có lưới toạ độ, đặt đa giác, khớp, socket. Chạy `check`, xem ba ảnh, sửa. Người dùng chỉnh tay bằng `scripts/puppet_kit/rig_tuner.html`
   (mở file, nạp ảnh + rig.json, kéo điểm, tải rig.json về).
4. `unit` và `ground`: chỉnh tới khi frame nghỉ trùng cỡ và vị trí với một state đã xuất (so bbox).
5. Viết `anims/*.json`, `render --no-export`, xem `contact.png` và GIF, rồi `render` thật.
6. Pose rig cho ảnh `pose_*`: một part `{"rest": true}`, `ground`/`unit` căn theo frame đã có hoặc theo rig chính; socket đo trên ảnh phóng to.

## Giới hạn đã biết

- Rig 2D không xoay ra ngoài mặt phẳng. Tay giơ qua đầu, xoay hông: cần pose still (tầng 2) hoặc video (tầng 3).
- Tầng 2 không có frame trung gian: đòn đánh là "pose - cắt - pose" (limited animation). Vệt chém và nghiêng/nén che nhát cắt; muốn mượt hơn thì thêm một pose giữa.
- `fill_under` vá bằng màu lân cận: chỉ đủ cho chuyển động nhỏ của part nằm trên. Part cần lộ nhiều thì xin thêm một plate.
- Toạ độ khớp do AI đặt chỉ gần đúng (±10 px ảnh nguồn): luôn chạy `check` và chỉnh bằng Rig Tuner.
- Tay xa (bị che trong master) không có trong rig Holy Commander.
- IK chỉ đặt lại hai xương của chuỗi; xương con gắn vào cẳng tay (chưa có) sẽ không đi theo.
- `source/rig/` không thuộc các loại mà `source_prune.py` dọn nên không bao giờ bị xoá. Ảnh pose và thư mục vfx mà rig dùng được `render`/`track`/`slash` tự ghi vào `meta.json` "sources" để không bị dọn.

## Holy Commander: đã làm (2026-11-11)

| State | Tầng | Frame | Ghi chú |
|---|---|---|---|
| `idle_side` | 1 | 24, lặp 1,6 s | thay bản 1 frame: thở, kiếm cắm yên, tay bám chuôi bằng IK, áo choàng và mào dao động |
| `levelup_puppet_side` | 1 | 26, hit 15 | khuỵu, nhấc kiếm, cắm mạnh xuống, nảy; để so với `levelup_side` (video) |
| `attack_diag_puppet_side` | 2 | 16, hit 8 | master → `pose_downcut_p1` → `pose_downcut_p2` → master; để so với `attack_diag_side` (video) |
| fx `slash_diag_puppet` | - | 16 | vệt chém từ socket của rig, không đánh dấu tay |

Chi phí API: 1 ảnh plate, ~0,012 USD.

## Frost Oracle (Băng Sư): nhân vật mới làm thẳng bằng kit (2026-11-11)

Hero đánh xa cỡ M, tạo bằng `fal-image` (master, icon, projectile) rồi dựng rig ngay, không có state video nào.

| State | Frame | Ghi chú |
|---|---|---|
| `idle_side` | 24, lặp | áo nén quanh chân, trượng cắm yên, tay áo xa co giãn theo tay cầm trượng (`stretch`), vạt áo dao động (`deform.band`) |
| `shoot_side` | 16, hit 8 | ngả ra sau, nhấc trượng, đẩy tinh thể ra trước; đạn rời socket `cast` |
| `levelup_side` | 24, hit 10 | khuỵu, giơ trượng và tay tự do lên cao, giữ, hạ |

Rig đúng tư thế master ngay lần `check` đầu; 5 ảnh, ~0,063 USD. Thêm vào engine cho nhân vật này: `puppet.py init` (tạo `meta.json` cho asset chưa có sheet),
ràng buộc `stretch` (một xương kéo giãn tới điểm đích) và `deform.band` (dao động trong một dải cao độ, hai đầu đứng yên).

## Lion Brawler (Sư Vương): thử nhiều pose (2026-11-11)

Hero cận chiến cỡ M. Một master, một plate (bỏ hai tay và đuôi), 5 pose still, tất cả đạt ngay lần đầu; 8 ảnh, ~0,112 USD.

| State | Tầng | Frame | Ghi chú |
|---|---|---|---|
| `idle_side` | 1 | 24, lặp | hai tay mỗi tay hai xương (FK), đuôi quẫy, đầu nhún |
| `levelup_side` | 2 | 21, hit 4 | rig khuỵu → pose gầm (ngực phập phồng bằng `osc`) → rig |
| `attack_side` + fx `claw_swipe` | 2 | 16, hit 8 | rig → `pose_claw_p1` → `pose_claw_p2` → rig |
| `skill_slam_side` + fx `slam` | 2 | 20, hit 9 | rig → `pose_skill_slam_p1` → `pose_skill_slam_p2` → rig |

Bài học: model vẽ mỗi pose ở một cỡ khác nhau (0,74-1,02 lần master). `unit` của pose rig lấy bằng trung bình nhân của tỉ lệ diện tích hình bóng và diện tích
màu bờm so với master, rồi chỉnh bằng mắt trên bảng contact (pose vươn người bị đánh giá nhỏ quá). `ground` là trung điểm hai bàn chân đọc trên ảnh, không phải
điểm thấp nhất (vuốt có thể thấp hơn chân). Việc này nên thành một lệnh căn pose tự động.

### Vòng chạy bằng pose-to-pose (2026-11-11)

`run_side` của Lion Brawler: 4 pose khoá (`pose_run_1..4`), mỗi pose giữ 2 hình với nhún và nén khác nhau, 8 hình lặp. `scripts/motion_check.py --loop` không gắn cờ nào
(nhún 22 px = 17% thân, chuyển 8→1 ngang các chuyển khác). Cỡ pose lấy tự động bằng lệnh mới:

```bash
python scripts/puppet.py pose out/heroes/lion_brawler source/design/pose_run_1_v01.png --name run_1 --colour 118,49,21 --ref-source plate
```

`--colour` là màu của một bộ phận giữ nguyên cỡ ở mọi pose (bờm). Đo trên `--ref-source plate` vì đầu của rig lấy từ plate; đo trên master cho pose to hơn rig ~10%.
Số đo cỡ đầu trong frame đã xuất (căn bậc hai diện tích bờm, px @2x): rig 31-32, mọi pose sau khi căn 31-33; trước khi căn `claw_p2` +12%, `slam_p2` +16%, các pose chạy +10%.
Cách đo này sai khi đầu bị che (`slam_p1`: hai tay che bờm) nên pose đó vẫn căn bằng mắt.

## Tồn đọng (đánh giá 2026-11-11, gồm feedback của user)

Kế hoạch xử lý và tech debt đầy đủ: `docs/puppet-kit-next.md`. Công thức chuyển động cho model viết animation: `docs/puppet-kit-motion-recipes.md`.

User đánh giá tốt: nhịp thở và các nhịp phụ (nhún vai) sống động; pose đơn không xoay; áp fx.

| # | Vấn đề | Ai nêu | Hướng xử lý |
|---|---|---|---|
| 1 | **Chưa có rig chân**: chân nằm trong lớp thân, chỉ nén/giãn cả khối, không gập gối | user | plate thứ hai bỏ cả chân; lớp đùi, ống chân, bàn chân; IK chân với bàn chân ghim đất |
| 2 | **Chưa có khớp háng**: thân trên không xoay/nghiêng độc lập với hông | user | tách thân trên và hông thành hai lớp, vá phần eo |
| 3 | **Khớp khuỷu của lion đặt sai**: xương cẳng tay bắt đầu ở mép găng nên găng chính là "khuỷu"; đúng phải là vai → cánh tay → cẳng tay → bàn tay | user | tách lại đa giác; công cụ để user tự đặt khớp (Rig Tuner hiện chỉ kéo điểm, chưa tạo/xoá xương hay xem thử chuyển động) |
| 4 | **Tách lớp còn mất hình**: áo choàng Holy Commander và các phần khuất bị vá bằng màu lân cận, lộ góc khi cử động | user | bước chuẩn bị tài nguyên: xin model vẽ riêng từng lớp khuất (áo choàng đầy đủ, thân sau tay) thay cho vá tự động |
| 5 | **Chưa có động tác xoay thân** (cào từ trước mặt sang bên trái cần xoay hông): rig 2D một góc nhìn không làm được, pose-to-pose chưa thử | user | nhiều pose khoá hơn cho đoạn xoay, hoặc lớp thân theo từng góc; đây là bài khó nhất, có thể vẫn cần video |
| 6 | Pose-to-pose không có hình trung gian: nhát cắt giữa hai pose, run chỉ 4 hình vẽ | Claude | thêm pose giữa; hoặc rig chân/tay đủ để nội suy |
| 7 | Căn cỡ pose phụ thuộc một màu không bị che; `ground` lấy điểm thấp nhất (sai khi vuốt thấp hơn chân) | Claude | đo bằng nhiều mốc; cho phép chỉ điểm chân trong Rig Tuner |
| 8 | Bóng chân cố định ở pivot, không đi theo khi thân rời đất hoặc lệch | Claude | bóng theo `ground` của shot, co lại khi nhảy |
| 9 | Vệt vuốt của lion mượn tham số màu của Holy Commander; dộng đất chưa có vòng sốc | Claude | bộ tham số riêng trong `source/vfx/` |
| 10 | Không có test tự động; `stretch`, `band`, `init`, `pose` chưa qua advisor; Rig Tuner chưa mở thử trong trình duyệt | Claude | test hồi quy (hash frame), rà advisor |
| 11 | Chưa có MCP (ý tưởng ban đầu của user); mọi thứ là CLI | Claude | bọc `check/render/pose/track` thành MCP khi format rig ổn định |
| 12 | Run của lion: tay trái ở `pose_run_1` và `pose_run_3` bị gập, nhìn như tật | user | bước chuẩn bị tài nguyên: ghi góc khuỷu bằng số, bộ pose profile (`puppet-kit-next.md` §2) |

## Rig v2 (2026-11-11): lion_brawler

Bộ xương chuẩn 17 xương (`docs/puppet-kit-next.md` §3), 16 lớp cắt từ 5 ảnh lớp rời (`layer_torso_v01`, `layer_legs_v02`, `layer_near_arm_v02`, `layer_far_arm_v02`, `layer_tail_v02`):
phần khuất là hình vẽ thật, không còn vá màu (trừ dưới đầu). Rig cũ giữ ở `rig_v1.json`.

Engine thêm: IK có `hint` (hướng gập của khớp) và `end_bone` (bàn chân nằm trên đích, giữ góc riêng), xương con cập nhật sau IK, kênh `<part>.z` đổi thứ tự vẽ theo frame.
Hạ `hips.ty` thì gối tự gập, chân không trượt. `v2_test_side` (30 hình) là bài thử khớp: ngồi xổm, xoay eo, gập khuỷu, đấm.
Các state `idle`, `levelup`, `attack`, `skill_slam` của lion đã chuyển phần rig sang v2 (`"version": "p02"`). Tồn đọng: `docs/puppet-kit-next.md` §8.

## Chuẩn bị tài nguyên (`scripts/puppet_prep.py`)

- `python scripts/puppet_prep.py list <asset> [--write-prompts] [--layers far_arm,far_leg,tail]`: bảng tài nguyên của `puppet-kit-next.md` 2.1 (có/thiếu, bản `_vNN` mới nhất).
  `--write-prompts` ghi prompt đã điền đủ (`{design}`, STYLE, BG đọc từ `format.md`) cho mỗi mục thiếu vào `source/design/prompts/<tên>_p01.txt`, không ghi đè, và in lệnh `gen_image.py` (không chạy).
- `python scripts/puppet_prep.py align <asset> <ảnh> [--colour r,g,b] [--kind plate|pose|profile] [--overlay out.png]`: so ảnh mới với master (lệch bbox, hàng chân, tỉ lệ cỡ theo màu), in `PASS`/`FAIL`, mã thoát 0/1.
  `plate`: hàng chân ≤ 8 px, cạnh trên ≤ 12 px, scale 0,97-1,03; `pose`/`profile`: chỉ scale 0,95-1,05. Plate đo trên master có thể lệch scale vì bờm trên plate bị vẽ lại (xem `--ref-source plate` ở mục Lion Brawler).

## Khớp uốn liền (`skin`, 2026-11-11)

Feedback của user: cắt rời ở khuỷu, gối, eo làm hình **gãy khúc** khi khớp gập. Cách sửa (giống mesh + weights của Spine): mỗi chi và thân là **một hình liền**, vùng quanh khớp uốn theo.

```json
{"name": "near_arm", "source": "near_arm", "bone": "near_upper_arm",
 "skin": {"bones": ["near_upper_arm", "near_forearm", "near_hand"], "tip": [330, 790], "blend": [45, 28]},
 "select": {"poly": [...cả cánh tay...]}}
```

- `bones`: chuỗi xương từ gốc ra ngọn; hình gắn vào xương đầu. `tip`: điểm cuối chi (để biết trục của đoạn cuối). `blend`: nửa bề rộng (px) của vùng uốn quanh từng khớp.
- Mỗi pixel xoay quanh khớp một góc bằng `w × góc khớp`, `w` tăng mượt từ 0 tới 1 dọc theo chi qua vùng `blend`. Không còn mép cắt.
- Trong nếp gập gắt (mặt trong gối khi ngồi xổm) có vài pixel không có nguồn: engine để trống, không kéo vệt.
- Lion: `rig.json` dùng `skin` cho hai tay (3 xương), hai chân (đùi + ống chân; bàn chân vẫn là lớp cứng ghim đất) và thân (hông + eo). Bản cắt rời giữ ở `rig_v2_cut.json` để so.
  Ảnh so sánh: chạy đoạn mã trong `docs/puppet-kit-next.md` §9 hoặc xem trang review.
- Chưa có: trọng số tự vẽ (weight painting), uốn theo lưới tam giác; `blend` là một số cho mỗi khớp.

## Ngã ngửa và bóng đi theo thân (2026-11-11)

`death_back_side` của lion: chỉ rig v2, không video. Cả thân xoay quanh bàn chân (`root.rot` tới −90); vì thân xoay quanh gót nên phần lưng sẽ lún dưới đất,
nên `root.ty` được **giải từng frame**: render thử, lấy hàng pixel thấp nhất của thân (ẩn đuôi bằng `tail.alpha` 0 khi đo) và nhấc lên cho bằng tư thế đứng.
Mã sinh lại: `python scripts/puppet_kit/examples_death_back.py` (chép rồi đổi số cho nhân vật khác).
Animation thêm `"shadow": "follow"`: bóng chân trượt và dài ra theo phần thân chạm đất (dùng cho mọi động tác thân rời khỏi chỗ đứng: ngã, lăn, quỳ).
Đây là động tác hợp với rig: khớp chỉ gập vừa, phần xoay lớn là cả thân (cứng), nên không lộ chỗ gãy.
