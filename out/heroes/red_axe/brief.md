# red_axe (Rìu Đỏ)

## Request
"tiếp tục với ảnh này" (2026-11-27), ảnh: `ref/style_board/hero_ref/axe_barbarian_redhair.png`. Nhân vật 4/5 của lô vẽ lại từ ảnh tham khảo (ghép lưới + video pose chung). Không dùng tên nhân vật in trên ảnh gốc.

## Choices
- Class: hero, tier **L** (`{H}` 84 px, canvas 220x196; cùng cỡ cả lô), role: **melee**
- Hệ: **không có**, thuần vật lý (user: "chỉ vật lý, không có hệ, sử dụng với rìu và tung các đòn vật lý")
- style: heroic, bám sát thiết kế, ~5 đầu như gốc
- Tags: female, berserker, physical, human
- Idle: như ảnh gốc, rìu kép cầm ở tay bên phải ảnh ngang eo, cán nghiêng ~15°, đầu rìu trên cao bên phải; tay kia nắm đấm
- Ref gửi model: `.work/ref_clean.png` (xóa logo, tên, dòng chữ; đã quay phải nên không lật)

## Skills (level 1, ý tưởng nhanh)
- axe_combo (Liên hoàn rìu): tung chuỗi đòn chém bằng rìu (vật lý)
- axe_whirl (Lốc xoáy rìu): xoay tròn với rìu dài, chém mọi quái quanh mình

## Design note (preflight)
1. Hero L, melee, nữ trưởng thành, rìu kép cao hơn người ~15%.
2. Body athletic, đồng hồ cát, ~5 đầu.
4. Rìu: cán gỗ đai vàng, mũi nhọn vàng ở chuôi; đầu 2 lưỡi trăng khuyết sứt mẻ + bánh trục tròn hoa văn xoắn.
5. Frame: hỏi 52% → được 88%.
6. Signature: bờm tóc cam đỏ lớn + rìu kép khổng lồ; vai lông xám.
7. COLOUR PLAN: tóc #E8622A / #9A3018 / #FF9A4A; da #F0B888; da thuộc #5E4C44; xám #A8A49C; vải #DCD4C2; vàng #DCAA48; sắt #727078; gỗ #7A5434; ngọc #4ED86A; kem #FFF4DE.
10. Lint: chỉ cảnh báo "huge / big round" cho đồ vật (không phải thân), chấp nhận.
12. Cost: 1 ảnh low ~0.016 USD.

## Slots
- `{id}`: red_axe; `{body}`: biped; `{design}`: `source/design/prompts/master_p01.txt` (đoạn RED AXE)

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v01 (chốt 2026-11-27) | vẽ lại từ ảnh tham khảo |
| idle_side | Puppet Kit (rig từ master, $0) | loop | ❌ | user 2026-11-27: idle tách rig từ master |
| icon | fal-image | ảnh tĩnh | ❌ | |
| pose_respawn | - | - | ⏭ | không cần (respawn = vfx + idle) |
| pose_skill_axe_combo | fal-image | ảnh tĩnh | ❌ | |
| pose_skill_axe_whirl | fal-image | ảnh tĩnh | ❌ | |
| run_side | video-sprite (lưới heroic_ref_five) | loop | ✅ clip run_t01 (chưa tách khung) | `out/heroes/_lineups/heroic_ref_five/source/video/run_t01` |
| attack_side | video-sprite (lưới heroic_ref_five) | one-shot | ✅ clip attack_t01 (chưa tách khung) | `out/heroes/_lineups/heroic_ref_five/source/video/attack_t01` |
| death_side | video-sprite (lưới heroic_ref_five) | one-shot | ✅ clip death_t01 (chưa tách khung; bỏ khung có lửa) | `out/heroes/_lineups/heroic_ref_five/source/video/death_t01` |
| respawn_side | idle (rig) + lib-fx | one-shot | ❌ | không làm clip (user 2026-11-27): vfx sáng -> hiện nhân vật ở idle |
| levelup_side | idle (rig) + lib-fx | one-shot | ❌ | không làm clip (user 2026-11-27): dùng idle + tự thêm vfx như holy_commander |
| skill_axe_combo_side, skill_axe_whirl_side | video-sprite | one-shot | ❌ | |
| fx_axe_combo, fx_axe_whirl, fx_respawn, fx_levelup | lib-fx | hiệu ứng | ❌ | `melee/slash/axe` |
| package | export | gói | ❌ | |
