# pale_seraph (Thiên Sứ Nhạt)

## Request
"tiếp tục với" + ảnh (2026-11-27), ảnh: `ref/style_board/hero_ref/caped_sorceress_pale.png`. Nhân vật 3/5 của lô vẽ lại từ ảnh tham khảo (ghép lưới + video pose chung).

## Choices
- Class: hero, tier **L** (`{H}` 84 px, canvas 220x196), role: **ranged** (pháp sư)
- style: heroic, bám sát thiết kế; yêu cầu ~5 đầu dáng thon
- Tags: female, light mage, light, human
- Idle: **lơ lửng như ảnh gốc** (mũi chân chĩa xuống trên đường đất, tay phía trước duỗi ra phải, tay kia buông, áo choàng xòe)
- Không vũ khí, tay không
- Ref gửi model: `.work/ref_clean.png` (xóa chữ ký; đã nhìn sang phải nên không lật)

## Skills (level 1, ý tưởng nhanh; hệ ánh sáng, màu hiệu ứng chốt khi làm bảng pha)
- soul_field (Vùng hồn xanh): chỉ tay xuống đất; vòng phép làm chậm quái (vfx)
- cape_storm (Áo choàng bão): xoay người tung áo choàng; mảnh vải sắc bay ra cắt quái xung quanh
- soul_beam (Tia hồn): duỗi thẳng tay, bắn một tia dài xuyên thẳng (vfx)

## Design note (preflight)
1. Hero L, ranged mage, nữ trưởng thành, không vũ khí.
2. Body slender, đồng hồ cát, ~5 đầu (heroic lessons: nữ đánh xa 3,8-4,2 đầu, đồ kín).
5. Frame: hỏi 55% → được 92% (áo choàng xòe + bay).
6. Signature: áo choàng xòe như cánh rách có lỗ tròn; tóc vàng bay; ngọc xanh ở hông.
7. COLOUR PLAN: bộ đồ #DCDEE6 / #9EA2B4 / #F6F8FC; áo choàng ngoài #D4D0C6, trong tím xám #6C6C8E / #44446A; vàng kim #E0B84A / #8E6C24 / #FAE48A; tóc #F2CE68; da #F4D6BE; mắt #FFE45A; ngọc #5CF08A; kem #FFF8E6.
8. Face: mắt vàng phát sáng, lông mày góc, miệng thẳng, lông mi.
10. Lint: clean.
12. Cost: 1 ảnh low ~0.016 USD.

## Slots
- `{id}`: pale_seraph; `{body}`: biped (lơ lửng); `{design}`: `source/design/prompts/master_p01.txt` (đoạn PALE SERAPH)

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ⏳ v01 chờ duyệt | lơ lửng, vẽ lại từ ảnh tham khảo |
| icon | fal-image | ảnh tĩnh | ❌ | |
| projectile | fal-image | ảnh tĩnh | ❌ | cầu sáng |
| projectile_fly, projectile_hit | fx-layers | hiệu ứng | ❌ | |
| pose_respawn | fal-image | ảnh tĩnh | ❌ | |
| pose_skill_soul_field | fal-image | ảnh tĩnh | ❌ | |
| pose_skill_cape_storm | fal-image | ảnh tĩnh | ❌ | |
| pose_skill_soul_beam | fal-image | ảnh tĩnh | ❌ | |
| run_side | video-sprite | loop | ❌ | bay lướt thay vì chạy? hỏi khi làm |
| shoot_side | video-sprite | one-shot | ❌ | |
| death_side | video-sprite | one-shot | ❌ | |
| respawn_side | video-sprite | one-shot | ❌ | |
| levelup_side | video-sprite | one-shot | ❌ | |
| skill_soul_field_side, skill_cape_storm_side, skill_soul_beam_side | video-sprite | one-shot | ❌ | |
| fx_soul_field, fx_cape_storm, fx_soul_beam, fx_respawn, fx_levelup | lib-fx / fx-layers | hiệu ứng | ❌ | |
| package | export | gói | ❌ | |
