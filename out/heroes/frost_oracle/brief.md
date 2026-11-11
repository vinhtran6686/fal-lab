# frost_oracle (Băng Sư)

## Request
User (2026-11-11): "chạy skill fal-image để tạo 1 nhân vật mới. Mình cho bạn quyết nhân vật đó là gì ... và áp dụng puppet-kit". Chạy như
`/fal-image --hero --tier M --creative`; **mọi lựa chọn do Claude quyết theo uỷ quyền của user** (không hỏi AskUserQuestion), master tự duyệt (>= 8) như `--auto`.
User có thể đổi bất kỳ lựa chọn nào: xem "Chờ user duyệt" cuối file.

## Concepts offered (2026-11-11)
- **A. Băng Sư (Frost Oracle)**: thấp đậm, mũ trùm nhọn rất to, áo choàng dài che chân, trượng pha lê băng cao bằng người. Đánh xa. ← chosen
- B. Thợ Săn Gió: thon, cung dài, khăn quàng bay. Đánh xa, nhanh.
- C. Vệ Binh Đá: vai và tay khổng lồ, búa đá hai tay. Cận chiến, chậm.
Lý do chọn A: khác hẳn hình bóng Holy Commander; không lộ chân và có một tay tự do nên hợp với rig cắt lớp; chưa có hero đánh xa nào dựng bằng Puppet Kit.

## Class / size
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 176x140 @1x (352x280 @2x), body 120 @2x (cả hình bóng đứng, tính cả trượng dựng)
- Role: ranged

## Slots
- `{id}`: frost_oracle
- `{body}`: biped
- `{design}`: A top-heavy frost oracle about 2.5 heads tall (a huge rounded pointed hood and wide shoulders, small hands, short legs), wearing a long plain deep-blue hooded robe that reaches his ankles with a wide lighter-blue shoulder mantle and one flat white fur band at the hem, two small dark-blue boots showing under the hem, the face deep in the hood's shadow with only two small white eye slits and a short pointed white beard drawn as one flat shape; a thick wooden staff exactly as tall as his body, topped with ONE big angular cyan ice crystal, held upright in his LEFT mitten hand (on the RIGHT side of the picture) and planted on the ground in front of him; his RIGHT arm (on the LEFT side of the picture) hangs straight down at his side, clear of the body, in a wide sleeve with an open mitten hand; saturated blue main colour, bright cyan-white accent, brown wood.
- `{idle}` (master_v01): UPRIGHT calm stance facing right, the staff planted on the ground in front of him in the left hand, the right arm hanging at his side
- `{attack}` (shoot): leans back and lifts the staff, then thrusts the crystal forward; an ice shard leaves from the crystal
- `{death}`: sinks down in place, the hood drops forward, the staff falls
- `{skills}`:
  - bão tuyết: raises the staff high with the crystal up and the free hand open; snow and ice shards fall on an area ahead (vfx, separate asset)
  - gai băng: slams the staff butt on the ground; a row of ice spikes rises in front of him (vfx, separate asset)

## Skills, level 2 (format.md §11; chưa làm, bảng để user sửa trước khi làm)
### bão tuyết (~1,6 s, hit ở đỉnh giơ trượng)
| Pha | Thân | Hiệu ứng |
|---|---|---|
| 1 wind-up | gối khuỵu, thân nén, trượng kéo sát người, đầu cúi | - |
| 2 load | chân đạp, thân vươn, tay trái đẩy trượng lên cao, tay phải mở ra sau | tinh thể sáng dần (lớp phẳng) |
| 3 release | trượng lên đỉnh, hơi ngả ra sau, mũ trùm ngửa | chớp ở tinh thể |
| 4 travel | giữ đỉnh, rung nhẹ | bão tuyết rơi ở vùng phía trước (vfx riêng) |
| 5 hold | hạ trượng, cắm lại | tan |
Rủi ro: trượng giơ cao phải nằm trong ô (còn ~2 H trên chân). Giá: 0 USD nếu làm bằng rig (đã có động tác tương tự ở `levelup`).
### gai băng (~1,2 s, hit lúc trượng chạm đất)
| Pha | Thân | Hiệu ứng |
|---|---|---|
| 1 wind-up | nhấc trượng khỏi đất, thân vươn | - |
| 2 load | trượng lên cao nhất, tay phải đưa ra trước | - |
| 3 release | dộng đuôi trượng xuống, thân nén mạnh | vòng sốc dưới chân |
| 4 impact | giữ nén, vạt áo tung | hàng gai băng mọc về phía trước (vfx riêng) |
| 5 hold | nảy về tư thế nghỉ | gai tan |
Rủi ro: gai dài hơn ô phải là lớp fx. Giá: 0 USD nếu làm bằng rig.

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ⏳ v01 | 9/10, Claude tự duyệt theo uỷ quyền; chờ user xác nhận |
| icon | fal-image | ảnh tĩnh | ⏳ v02 | v01 lộ cả người (6/10) → v02 cận mặt (8,5/10); đã pack `frames/icon` |
| projectile | fal-image | ảnh tĩnh | ⏳ v01 | mảnh băng, 9/10 |
| projectile_fly, projectile_hit | fx-layers | hiệu ứng | ❌ | xuất phát từ socket `cast` của rig ở hình hit |
| rig (plate_v01 + rig.json) | Puppet Kit | rig | ⏳ v01 | `source/rig/`: 5 lớp, 6 xương, tay áo xa co giãn theo tay cầm trượng |
| idle_side | Puppet Kit (rig, $0) | loop | ⏳ p01 | 24 hình, 1,60 s |
| shoot_side | Puppet Kit (rig, $0) | one-shot | ⏳ p01 | 16 hình, hit 8 |
| levelup_side | Puppet Kit (rig, $0) | one-shot | ⏳ p01 | 24 hình, hit 10 |
| run_side | video-sprite | loop | ❌ | rig 2D không làm được bước chạy: cần video |
| death_side | video-sprite | one-shot | ❌ | thử rig trước (sụp xuống tại chỗ), không đạt thì video |
| pose_respawn | fal-image | ảnh tĩnh | ❌ | |
| respawn_side | video-sprite | one-shot | ❌ | |
| fx_respawn | fx-layers | hiệu ứng | ❌ | |
| fx_levelup | fx-layers | hiệu ứng | ❌ | |
| skill_blizzard_side | Puppet Kit (rig) | one-shot | ❌ | bảng pha ở trên |
| fx_blizzard | fx-layers | hiệu ứng | ❌ | |
| skill_ice_spikes_side | Puppet Kit (rig) | one-shot | ❌ | bảng pha ở trên |
| fx_ice_spikes | fx-layers | hiệu ứng | ❌ | |
| package | export | gói | ⏭ | khi asset rời repo |

Estimated cost so far: 5 ảnh gpt-image-2 low (master, icon x2, projectile, plate) ~USD 0.063. Ba state đã xuất: 0 USD.

## Chờ user duyệt
- Thiết kế (master_v01), icon_v02, projectile_v01.
- Ba chuyển động rig: xem `frames/<sheet>/preview.gif` và `check/contact.png`.
- Hai kỹ năng mới chỉ có bảng pha.
