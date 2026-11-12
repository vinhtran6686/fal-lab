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

## Chuẩn bị tài nguyên (`scripts/puppet_prep.py`)

- `python scripts/puppet_prep.py list <asset> [--write-prompts] [--layers far_arm,far_leg,tail]`: bảng tài nguyên của `docs/scripts/puppet_kit/puppet-kit-asset-prep-and-rig-v2.md` 2.1 (có/thiếu, bản `_vNN` mới nhất).
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
- So sánh bản cắt rời và bản `skin`: dựng cùng animation với hai rig rồi đặt cạnh nhau.
- Chưa có: trọng số tự vẽ (weight painting), uốn theo lưới tam giác; `blend` là một số cho mỗi khớp.

## Ngã ngửa và bóng đi theo thân (2026-11-11)

Ngã ngửa chỉ bằng rig, không video. Cả thân xoay quanh bàn chân (`root.rot` tới −90); vì thân xoay quanh gót nên phần lưng sẽ lún dưới đất,
nên `root.ty` được **giải từng frame**: render thử, lấy hàng pixel thấp nhất của thân (ẩn đuôi bằng `tail.alpha` 0 khi đo) và nhấc lên cho bằng tư thế đứng.
Animation thêm `"shadow": "follow"`: bóng chân trượt và dài ra theo phần thân chạm đất (dùng cho mọi động tác thân rời khỏi chỗ đứng: ngã, lăn, quỳ).
Đây là động tác hợp với rig: khớp chỉ gập vừa, phần xoay lớn là cả thân (cứng), nên không lộ chỗ gãy.

## Rig & Pose Studio và `links` (2026-11-11)

Công cụ cục bộ xem/sửa rig, tạo dáng và lưu pose: `docs/tools/studio/puppet-studio-guide.md`. Core có thêm một khóa rig tùy chọn `links` (cơ dãn theo khi vai trượt ra bằng `tx/ty` của bone vai; `Rig._pulls`, `Rig.render`) và các khóa mà core bỏ qua nhưng Studio dùng (`bone.limit.rot`). Không có `links` thì kết quả y hệt trước (đã kiểm trên mọi frame của `anims/*.json`).
