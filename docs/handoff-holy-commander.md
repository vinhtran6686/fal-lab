# Handoff: test toàn bộ asset của holy_commander (2026-10-19)

Mục tiêu: làm MỘT nhân vật (`out/heroes/holy_commander`) đến khi trông ổn, ghi lại cách làm, rồi cập nhật skill.

## Trạng thái skill (main, commit 70cf963)
- fal-image: 5 class (`classes/hero|ally|enemy|enemy-flying|boss.md`), master = side, đứng thẳng (`{UPRIGHT}`),
  hero 1 hướng, quái 3 hướng, manifest trong `brief.md`, size tier ở §3 mỗi class, số liệu ref ở `reference.md`.
- video-sprite: clip thân chỉ có thân (tự lọc chữ hiệu ứng), 15 fps "on twos", clip 4 s, skill = vào pose rồi
  giữ pose, pose cuối đặt đúng cỡ thân (sửa lỗi zoom), bóng dưới chân lúc export, respawn = despawn `--reverse`.
- Hiệu ứng: `scripts/fx_layers.py A/fx/<skill>.json` (slash, ring, burst, bolt, pillar, particles, sprite),
  không dùng video model. Mẫu: `out/heroes/holy_commander/fx/radiant_slash.json`.

## holy_commander hiện có
- Duyệt: `master_v07` (trường kiếm cắm đất, đầu đại bàng), `icon_v01`, `pose_skill_{holy_banner,radiant_slash,charge}_v01`.
- Clip trong `raw/` (t01, trước khi sửa skill): death ✅ dùng được, despawn ✅ dùng được (export --reverse),
  run ⚠️ (export --despill), levelup ⚠️ (có vệt chém xanh + bụi cuối clip), attack ❌ (vệt chém hồng),
  holy_banner ❌, radiant_slash ❌, charge ❌ (zoom + hiệu ứng vẽ vào thân).
- Chưa export sheet nào; chưa có `meta.json`.

## Thứ tự test đề xuất
1. Miễn phí: export từ raw/: idle_side (--rest-frame), death_side, respawn_side (despawn --reverse),
   run_side (--despill). Kiểm tra bóng, khung 156x140, body 120 @2x.
2. Quay lại 1 skill (radiant_slash, ~0.08 USD), export, chạy fx_layers lên clip thật.
3. attack, levelup, holy_banner, charge (~0.32 USD) + công thức fx cho từng cái (vệt chém, cột sáng + vòng
   đất, cờ thánh = mảnh fx riêng + vòng đất).
4. Mỗi bước: ghi vào `history.md` cái gì làm nhân vật trông ổn hơn (prompt, timing, lớp fx) để cập nhật skill.

## Còn tồn
goblin_miner `view_back` vẽ lại; mảnh fx "mây riêng" cho thunderstorm; icon và palette chưa so với ref.
