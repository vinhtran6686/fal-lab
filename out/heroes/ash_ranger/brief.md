# ash_ranger (Cung Thủ Tro)

## Request
"Tiếp theo xử lý tương tự với ảnh đính kèm" (2026-11-27), ảnh: `ref/style_board/hero_ref/hooded_archer_white.png`. Nhân vật 2/5 của lô vẽ lại từ ảnh tham khảo (lô sẽ ghép lưới + video pose chung, `docs/scripts/lineup/lineup-workflow.md`).

## Choices
- Class: hero, tier **L** (`{H}` 84 px, canvas 220x196), role: **ranged**
- style: heroic, vẽ lại bám sát thiết kế; ~5 đầu (gốc ~5,5), màu gốc làm sáng và tươi hơn
- Tags: male, archer, wind, human
- Idle: đứng thẳng, cung dựng đứng cầm thấp ở tay bên phải ảnh, tay kia buông (tư thế kéo cung của ảnh gốc dành cho `shoot_side`)
- Ref gửi model: `.work/ref_clean.png` (xóa chữ ký và con dấu; nhân vật đã quay phải nên không lật)

## Skills (level 1, ý tưởng nhanh)
- pierce_shot (Tên xuyên): kéo căng lâu, bắn một mũi xuyên thẳng hàng quái; vệt gió (vfx)
- triple_shot (Ba mũi tên): bắn ba mũi tên xòe quạt ra trước

## Design note (preflight)
1. Hero L, ranged, nam; cung recurve gãy góc ~85% chiều cao hình.
2. Body agile/lean ~5 đầu; vai rộng, eo hẹp.
4. Cung dựng đứng, tay cầm ngang hông, đầu trên ngang mũ trùm, đầu dưới sát đất; dây căng, không lắp tên.
5. Frame: hỏi 55% (model vẽ to ~1,4 lần) → được 83%.
6. Signature: mũ trùm trắng + áo khoác vai vuông có huy hiệu chữ H vàng; cung đen gãy góc.
7. COLOUR PLAN: trắng ngà #E6E0CE / #A9A290 / #FFF8E6; áo choàng xám-xanh #5A6676 / #323A48 / #8E9AAC; quần nâu #6E5440; da thuộc #9A7048 / #5A3E26 / #C8965E; găng rêu #6E9058; cung #4A4650; huy hiệu #F2D23A; kem #FFF6E0. Lint: chỉ cảnh báo 6 họ màu (giữ đúng màu gốc, chấp nhận).
8. Face: một mắt sắc + lông mày, khăn che mũi miệng.
12. Cost: 1 ảnh low ~0.016 USD.

## Slots
- `{id}`: ash_ranger; `{body}`: biped; `{design}`: `source/design/prompts/master_p01.txt` (đoạn ASH RANGER)

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ⏳ v01 chờ duyệt | vẽ lại từ ảnh tham khảo, style heroic |
| icon | fal-image | ảnh tĩnh | ❌ | |
| projectile | fal-image | ảnh tĩnh | ❌ | mũi tên |
| projectile_fly, projectile_hit | fx-layers | hiệu ứng | ❌ | |
| pose_respawn | fal-image | ảnh tĩnh | ❌ | |
| pose_skill_pierce_shot | fal-image | ảnh tĩnh | ❌ | |
| pose_skill_triple_shot | fal-image | ảnh tĩnh | ❌ | |
| run_side | video-sprite | loop | ❌ | |
| shoot_side | video-sprite | one-shot | ❌ | tư thế kéo cung như ảnh gốc |
| death_side | video-sprite | one-shot | ❌ | |
| respawn_side | video-sprite | one-shot | ❌ | |
| levelup_side | video-sprite | one-shot | ❌ | |
| skill_pierce_shot_side | video-sprite | one-shot | ❌ | |
| skill_triple_shot_side | video-sprite | one-shot | ❌ | |
| fx_pierce_shot, fx_triple_shot, fx_respawn, fx_levelup | lib-fx / fx-layers | hiệu ứng | ❌ | |
| package | export | gói | ❌ | |
