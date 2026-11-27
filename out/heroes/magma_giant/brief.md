# magma_giant (Khổng Lồ Dung Nham)

## Request
"chốt -> tiếp tục với nhân vật này" (2026-11-27), ảnh: `ref/style_board/hero_ref/magma_stone_giant.png`. Nhân vật 5/5 của lô vẽ lại từ ảnh tham khảo (ghép lưới + video pose chung).

## Choices
- Class: hero, tier **L** (`{H}` 84 px, canvas 220x196), role: **melee tank**
- Hệ: đất + lửa; style: heroic, bám sát thiết kế, tỷ lệ như gốc (~4 đầu, đầu nhỏ, vai và tay khổng lồ)
- Tags: male, tank, earth + fire, stone giant (dáng người lùn khổng lồ)
- Idle: hai tay buông, ngọn lửa nhỏ trên lòng bàn tay bên phải ảnh, tay kia nắm đấm; bỏ cột khói cao của ảnh gốc
- Ref gửi model: `.work/ref_clean.png` (xóa chữ ký và tên; không lật)

## Skills (level 1, ý tưởng nhanh)
- lava_fist (Nắm đấm dung nham): giáng nắm đấm xuống đất; vũng dung nham lan ra đốt quái (vfx)
- stone_skin (Giáp đá): lõi dung nham bùng sáng, đá dày lên; giảm sát thương (buff)
- stomp (Dậm đất): nhấc chân dậm mạnh; sóng chấn làm choáng quái gần

## Design note (preflight)
1. Hero L, tank, nam, không vũ khí, nắm đấm đá to bằng đầu.
2. Body brawny, ~4 đầu, vai gù.
5. Frame: hỏi 58% → được 82%.
6. Signature: lõi dung nham răng cưa ở bụng + râu đen 3 khoen vàng + nắm đấm khổng lồ.
7. COLOUR PLAN: đá #8C8894 / #4E4A5A / #BCB8C4; dung nham #FF8A2A / #FFD25A / #C2461A; râu #3E3A46; vàng #DCAA48; mắt #FFE45A; khố #4A4044; chữ rune #6AF0A0; kem #FFF4DE.
10. Lint: clean.
12. Cost: 1 ảnh low ~0.016 USD.

## Slots
- `{id}`: magma_giant; `{body}`: biped; `{design}`: `source/design/prompts/master_p01.txt` (đoạn MAGMA GIANT)

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ⏳ v01 chờ duyệt | vẽ lại từ ảnh tham khảo |
| idle_side | Puppet Kit (rig từ master, $0) | loop | ❌ | user 2026-11-27: idle tách rig từ master |
| icon | fal-image | ảnh tĩnh | ❌ | |
| pose_respawn | - | - | ⏭ | không cần (respawn = vfx + idle) |
| pose_skill_lava_fist, pose_skill_stone_skin, pose_skill_stomp | fal-image | ảnh tĩnh | ❌ | |
| run_side | video-sprite (lưới heroic_ref_five) | loop | ✅ clip run_t01 (chưa tách khung) | `out/heroes/_lineups/heroic_ref_five/source/video/run_t01` |
| attack_side | video-sprite (lưới heroic_ref_five) | one-shot | ✅ clip attack_t01 (chưa tách khung) | `out/heroes/_lineups/heroic_ref_five/source/video/attack_t01` |
| death_side | video-sprite (lưới heroic_ref_five) | one-shot | ✅ clip death_t01 (chưa tách khung; bỏ khung có lửa) | `out/heroes/_lineups/heroic_ref_five/source/video/death_t01` |
| respawn_side | idle (rig) + lib-fx | one-shot | ❌ | không làm clip (user 2026-11-27): vfx sáng -> hiện nhân vật ở idle |
| levelup_side | idle (rig) + lib-fx | one-shot | ❌ | không làm clip (user 2026-11-27): dùng idle + tự thêm vfx như holy_commander |
| skill_lava_fist_side, skill_stone_skin_side, skill_stomp_side | video-sprite | one-shot | ❌ | |
| fx_lava_fist, fx_stone_skin, fx_stomp, fx_respawn, fx_levelup | lib-fx | hiệu ứng | ❌ | |
| package | export | gói | ❌ | |
