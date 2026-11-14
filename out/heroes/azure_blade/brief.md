# azure_blade (Lam Đao)

## Request
User (2026-11-12): hero mới để test quy trình "pose A + pose B + fx" kiểu `ref/alien` (docs/pipeline/pose-pair-fx-method.md §9), tránh lỗi của lion (tay lệch cỡ, chân lệch).
Chạy `/fal-image --creative`. Người dùng tự viết concept: "nhân tộc, thân người, giáp hạng nhẹ ôm sát, không quá phức tạp; cầm 1 thanh đao tầm trung vừa với cơ thể".

## Concepts offered (2026-11-12)
- A. Hiệp Sĩ Áo Choàng: người chibi đội mũ trùm, áo choàng sau lưng, hai kiếm ngắn giống nhau.
- B. Rùa Chiến Binh: mai trên lưng, hai nắm đấm bọc đá.
- C. Cáo Lửa: đuôi xù và khăn sau lưng, hai tonfa.
Người dùng chọn hướng A nhưng sửa: người thường (không mũ trùm), giáp nhẹ, **một đao** ở tay phải của nhân vật, tay trái trống.

## Class / size
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 176x140 @1x
- Role: melee

## Slots
- `{id}`: azure_blade
- `{body}`: biped
- `{design}` (master_p02, **master v06 được duyệt 2026-11-12**): battle-hardened human swordsman warrior, serious and powerful, NOT chibi/cute (rule mới trong `format.md`); broad shoulders, deep chest, thick forearms and thighs; hard grim face, short cropped dark hair, amber headband; light angular blue-grey armour (V breastplate, same-size pauldrons with amber trim, a bracer on each forearm, plate skirt, greave and boot on each leg), amber belt; short dark blue-grey cape to the knees BEHIND the body; ONE medium dao (blade waist-to-knee, pale steel, amber edge and hilt) in the hand on the LEFT of the image (= nhân vật cầm tay phải), the other fist empty; main colour saturated blue-grey, accent amber.
- Lịch sử: master v01-v03 (chibi 2,3 đầu) bị loại vì user yêu cầu không chibi; v04-v06 (chiến binh). Điểm yếu v06: tỉ lệ ~6 đầu (mục tiêu 4), giáp nặng hơn "giáp nhẹ"; chấp nhận theo lựa chọn của user.
- `{idle}`: đứng thẳng, hai chân rộng hơn vai trên một đường đất, hai tay buông chếch xa thân (A-pose nhẹ), đao cầm thấp bên hông, mũi chếch xuống phía trước. Gần nhìn thẳng, xoay ~20° sang phải (hai nửa thân gần đối xứng).
- `{attack}`: chưa làm (kỹ năng 1 là đòn chính để test).
- `{skills}`: xem dưới.

Lưu ý thiết kế rút từ lion: nhấn mạnh "EXACTLY THE SAME SIZE" cho tay và chân; vũ khí chỉ ở một tay nhưng cánh tay, bao tay, hộ tay cùng cỡ; áo choàng chỉ lộ ra hai bên thân, không đè lên tay; cả thanh đao nằm trong khung.
Nếu muốn đổi tay cầm: chỉ cần đổi "LEFT" thành "RIGHT" trong prompt (hiện đặt theo nghĩa nhân vật cầm tay phải khi nhìn thẳng).

## Skills, level 2 (format.md §11): theo mô tả của người dùng
### 1. Trảm Trăng Khuyết (`pose_skill_crescent_p1`, `pose_skill_crescent_p2` + `fx_crescent_slash`)
Mô tả gốc: "xoay người ngang, cầm đao bằng 2 tay, giơ lên cao qua đầu, lưỡi đao hướng xuống đất. Tung 1 đòn mạnh tới trước và kết thúc ở form tiếp đất với đao đập xuống đất, thân khom xuống, hạ thấp chân và khuỵu gối."
| Pha | Thân | Liên kết | Hiệu ứng |
|---|---|---|---|
| 1 pose A (chuẩn bị) | thân xoay ngang (nhìn nghiêng), hai tay nắm cán đao giơ cao qua đầu, mũi đao chúc xuống đất sau lưng; chân đứng vững; áo choàng nằm sau lưng | hai tay cùng trên cán; vai, khuỷu cao hơn đầu | không (giữ vài khung) |
| 2 chuyển | cắt thẳng sang pose B, không khung trung gian | - | vệt lưỡi liềm lớn từ mũi đao ở A xuống mũi đao ở B, che thân |
| 3 pose B (tiếp đất) | thân khom, hạ thấp, khuỵu gối, đao đập xuống đất phía trước, áo choàng bay ra lộ lưng | hai tay vẫn nắm cán; chân trước khuỵu, chân sau duỗi | vệt tan, bụi nhỏ (tùy) |
| 4 giữ | giữ pose B vài khung rồi về idle | - | - |
Rủi ro: model nhầm tay, hai tay không cùng nắm cán; đao quá dài ra khỏi khung ở pose A; pose B không đủ khom. Duyệt từng pose, chỉ làm lại pose sai.

### 2. Quét ngang (`pose_skill_sweep_p1`, `pose_skill_sweep_p2` + `melee/slash/sweep`), thử mặt phẳng nằm ngang 2026-11-14
Mặt phẳng: **ground** (`fal-image/action-planes.md`). Pose A: nhìn từ sau lưng, đao nằm ngang độ cao ngực, mũi chỉ trái, tay và cán sau thân. Pose B: mở ngực về người xem, đao nằm ngang cùng độ cao, mũi chỉ phải-xuống, thấy đủ lưỡi. Chân đứng yên (thực tế lệch trái ~70-100 px ở B: căn khi ghép). Chưa đo điểm bám, chưa dựng rig.

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v06 | user chọn 2026-11-12, 8.5/10 |
| icon | fal-image | ảnh tĩnh | ⏭ | sau khi test pose |
| pose_skill_crescent_p1 | fal-image | ảnh tĩnh | ⏳ v01 9/10 | pose A, ref master |
| pose_skill_crescent_p2 | fal-image | ảnh tĩnh | ✅ v03 | user chọn: lưỡi đao nằm ngang trên mặt đất (không cắm); ref master + pose A |
| fx_crescent_slash | lib-fx (milestone-01 layered) | hiệu ứng | ⏳ p01 | vệt xanh lam phủ cả lưỡi, mũi đậm, cán nhạt; `source/vfx/crescent/` |
| skill_crescent_side | ghép khung ($0) | one-shot | ⏳ p01 | 20 khung @15 fps; `frames/skill_crescent_side/`; dựng lại: `PYTHONHASHSEED=0 python out/heroes/azure_blade/source/vfx/crescent/build_crescent.py` |
| fx_blade_charge (tụ lực) | lib-fx `melee/blade_aura/charge_blue` | hiệu ứng trạng thái | ✅ | ánh sáng xanh chạy cán→mũi trước đòn, giữ sáng sau đòn; `source/vfx/blade_charge/`, `frames/fx/blade_charge/` |
| skill_crescent_charge_side | ghép khung ($0) | one-shot | ✅ | body + tụ lực + vệt chém, 44 khung @15 fps; `frames/skill_crescent_charge_side/`; dựng lại: `build_charge.py` rồi `build_crescent.py --charge` |
| fx_blade_charge_fire (tụ lực lửa) | lib-fx `melee/blade_aura/charge_fire` | hiệu ứng trạng thái | ✅ | bản lửa của tụ lực (sáng, rực; người dùng duyệt 2026-11-12), cùng timeline; `build_charge.py --fire`, `frames/fx/blade_charge_fire/` |
| skill_crescent_charge_fire_side | ghép khung ($0) | one-shot | ✅ | body + tụ lực lửa + vệt chém xanh; `build_crescent.py --charge=fire` |
| run_side, attack_side, death_side, pose_respawn, respawn_side, levelup_side, package | - | - | ⏭ | ngoài phạm vi bài test |

| rig pose A + pose B (studio) | Puppet Kit ($0) | rig | ⏳ p02 | `source/rig/rig_a.json`, `rig_b.json`: torso / arms (hai tay, nắm đấm, giáp vai) / blade; dây chằng `shoulder_chest` (tay trượt thì vai + ngực theo); dựng lại: `make_rigs.py`, `make_anim.py` |
| skill_crescent_puppet_side | Puppet Kit pose-to-pose ($0) | one-shot | ⏳ p02 | 44 khung @15 fps, chỉ pose A và B (không idle): P1 đao nâng cao + thở, P2 về pose A, cắt, P3 pose B đập xuống, P4 nhún theo quán tính rồi về pose B; hit 23 |
| skill_crescent_side (có fx) | ghép ($0) | one-shot | ⏳ p03 | thân puppet + vệt xanh sáng bề mặt lưỡi quét; `build_crescent.py` |
| pose_skill_sweep_p1 | fal-image | ảnh tĩnh | ✅ v02 | user chốt 2026-11-14 (ground pose A, nhìn từ sau lưng) |
| pose_skill_sweep_p2 | fal-image | ảnh tĩnh | ✅ v03 | user chốt 2026-11-14; chân lệch trái và to hơn A ~4%, chưa đo điểm bám |
| skill_sweep_side | ghép + `melee/slash/sweep` | one-shot | ⏭ | chưa làm: cần foot_marks, pivot vai, rig |
