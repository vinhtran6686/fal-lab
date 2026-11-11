# T5 (Sonnet): viết hurt, death, roar cho lion theo công thức

Trạng thái: DONE (2026-11-11, Sonnet)

**Điều kiện bắt đầu**: `out/heroes/lion_brawler/source/rig/rig.json` có xương tên `hips` và `near_shin`. Kiểm: `grep -c '"hips"' out/heroes/lion_brawler/source/rig/rig.json` > 0.
Chưa có thì dừng, không làm.

## Mục tiêu
Ba animation mới cho Lion Brawler, viết **bằng cách chép bảng** trong `docs/puppet-kit-motion-recipes.md`, không tự nghĩ lại cơ học.

## Đọc trước
- `docs/tasks/README.md` mục "Quy tắc chung".
- `docs/puppet-kit-motion-recipes.md` toàn bộ (quy ước dấu ở §1 là bắt buộc).
- `out/heroes/lion_brawler/source/rig/rig.json` (tên xương thật) và một animation mẫu do Fable viết cho rig v2 trong `source/rig/anims/` (Fable sẽ ghi tên file mẫu vào mục "Ghi chú của Fable" dưới đây khi mở khoá task).

## Được sửa
- Tạo mới trong `out/heroes/lion_brawler/source/rig/anims/`: `hurt.json`, `death.json`, `skill_roar.json`
- Sinh bằng lệnh: `out/heroes/lion_brawler/frames/hurt_side/`, `death_side/`, `skill_roar_side/`, và `meta.json`
- `out/heroes/lion_brawler/brief.md` (dòng manifest của ba state), `history.md` (một dòng mỗi state)
- `scripts/puppet_kit/golden.json` qua `python scripts/puppet_test.py --update` (nếu T1 đã xong)
- File task này và dòng T5 trong `docs/tasks/README.md`

## Việc cần làm
| State | Công thức | Frame | Ghi chú |
|---|---|---|---|
| `hurt_side` | recipes §7 "Hit / hurt" | 6 | chỉ rig; thân giật ra sau rồi về; đầu và tay trễ 1 frame |
| `death_side` | recipes §7 "Death" | 12 | chỉ rig: `hips.ty` hạ (gối tự gập nhờ IK chân), thân đổ trước, tay buông; frame cuối nằm yên. Nếu thân đổ quá 60° lộ khe giữa lớp thì dừng ở góc không lộ và ghi lại |
| `skill_roar_side` | recipes §7 "Level up / gầm" | 22 | rig khuỵu 3 frame → pose `source/rig/poses/levelup.json` giữ 14 frame (ngực phập phồng) → rig 5 frame; `hit_frame` 4 |

Với mỗi state: viết JSON → `python scripts/puppet.py render out/heroes/lion_brawler <anim> --sheet <state> --no-export` → mở `.work/puppet/<state>/contact.png` → đi hết checklist recipes §9 → sửa → `render` thật.

## Nghiệm thu
- Ba lệnh `render` thật chạy không lỗi; `python scripts/motion_check.py out/heroes/lion_brawler/frames/<state> --once` không có cờ "frozen" ngoài frame giữ cố ý.
- Checklist recipes §9 đạt cho từng state; ghi kết quả từng mục vào Kết quả.
- Mọi dòng manifest mới ở trạng thái ⏳ (chờ user duyệt), không tự đánh ✅.

## Ghi chú của Fable
Mở khoá 2026-11-11. Rig v2 đã có (`rig.json`; bản cũ là `rig_v1.json`, không dùng).
- **File mẫu**: `source/rig/anims/v2_test.json` (ngồi xổm, xoay eo, gập khuỷu, đấm) và `idle.json` (vòng lặp bằng `osc`). Mẫu shot rig trong animation pose-to-pose: shot `ready` và `recover` của `attack.json`.
- **Xương**: `root`, `hips`, `spine`, `head`, `near_upper_arm` → `near_forearm` → `near_hand`, `far_upper_arm` → `far_forearm` → `far_hand`, `near_thigh` → `near_shin` → `near_foot`, `far_thigh` → `far_shin` → `far_foot`, `tail`.
- **Chân chạy bằng IK**: không đặt `rot` cho `*_thigh`, `*_shin`. Muốn gập gối: tăng `hips.ty` (0 = đứng thẳng, 100 = ngồi xổm sâu nhất; quá 110 chân bị kéo giãn). `hips.tx` dời trọng tâm (±25). Bàn chân ghim đất; `*_foot.rot` xoay bàn chân tại chỗ.
- **Giới hạn an toàn** (quá thì lộ mép cắt): `spine.rot` −8..+16; `head.rot` −10..+10; `near_upper_arm.rot` −60..+45 (vung ra trước quá 60° lộ đỉnh vai bị cắt); `near_forearm.rot` −110..+5; `near_hand.rot` −30..+15; `far_upper_arm.rot` −35..+35; `far_forearm.rot` −90..0; `tail.rot` −20..+20.
- Death: rig không cho thân nằm ngang được (quá `spine.rot` +16). Làm "khuỵu gối tại chỗ": `hips.ty` → 100, `spine.rot` → +16, đầu gục +10, hai tay buông (`*_forearm.rot` → 0, `*_upper_arm.rot` → +10), giữ hình cuối; ghi rõ trong Kết quả là chưa có đoạn đổ người.
- Quy ước dấu ở recipes §1: chi buông xuống, `rot` âm = ra trước; khuỷu gập tự nhiên là `forearm.rot` âm.

## Kết quả
Ba anim ở `source/rig/anims/`: `hurt.json` (6 hình, hit 1), `death.json` (12), `skill_roar.json` (22 = 3 + 14 + 5, hit 4). Render thật xong, `golden.json` đã cập nhật (15 case).
- motion_check `--once`: hurt không cờ; death chỉ cờ FROZEN ở hình 9-11 (giữ hình cuối cố ý); roar chỉ cờ FROZEN ở hình 11-17 (giữ gầm 14 hình, chỉ nhún 0,5 px, cố ý).
- Checklist §9: (2) không chạm mép ô: đạt; (3) chân ghim đất nhờ IK: đạt; (4) không dùng shot pose mới, cỡ đầu giữ nguyên: đạt; (5) hit_frame: hurt 1 (nén mạnh nhất), roar 4 (đầu pose gầm): đạt; (6) không hai hình liền giống hệt ngoài đoạn giữ cố ý, không có release: đạt; (7) vòng lặp: không áp dụng (one-shot); (8) không dùng sway: đạt; (9) manifest ⏳ và history đã ghi: đạt. Không thấy lộ khe giữa lớp trên contact sheet (chưa xem phóng to).
- Death: chưa có đoạn đổ người, thân dừng ở `spine.rot` +16, `hips.ty` 100-102 (theo giới hạn rig).
