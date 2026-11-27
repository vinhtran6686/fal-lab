# cinder_maul (Búa Tro Hồng)

## Request
`/fal-image vẽ lại master image cho nhân vật này dựa trên ảnh tham khảo` (2026-11-27), ảnh: `ref/style_board/hero_ref/hammer_knight_crest.png`.

## Choices (2026-11-27)
- Class: hero (`classes/hero.md`), tier **L**, `{H}` 84 px, canvas 220x196 @1x; role: melee
- style: heroic (`docs/styles/heroic-vector-style/`), vẽ lại bám sát thiết kế ảnh tham khảo
- Tags: male, melee warrior, earth (fire core), human
- Khác ảnh gốc (người dùng duyệt): ~5 đầu (gốc ~7); giáp thép xám-xanh thay đen; khe mắt mũ phát sáng cam (ngoại lệ "mặt có biểu cảm" của style heroic: mũ kín)
- Idle: như ảnh gốc, búa dựng đứng phía trước (bên phải ảnh), tay bên phải ảnh nắm cán ngang ngực, tay kia nắm đấm buông
- Ref gửi model: `.work/ref_mirrored.png` (bản gốc xóa chữ ký, lật ngang để quay phải)

## Skills (level 1, ý tưởng nhanh; bảng pha chi tiết khi bắt đầu làm)
- leap_slam (Nhảy nện búa): nhảy lên, lao tới một điểm xa, nện búa xuống; vụ nổ tròn tại điểm rơi (vfx)
- quake (Địa chấn): đứng tại chỗ, giơ búa nện đất; vết nứt lan thẳng ra trước (vfx)
- sweep (Quét ngang): xoay hông quét búa ngang tầm thắt lưng; vệt quét nặng

## Design note (preflight)
1. Hero L 84 px, melee, nam trưởng thành, búa chiến hai tay cao bằng người, màu chủ thép xám-xanh.
2. Body: brawny cao (~5 đầu theo yêu cầu): vai ngực rộng, eo hẹp hơn, nắm đấm găng to.
3. Tỷ lệ: đầu đội mũ ~1/5 chiều cao; búa cao ≈ hình (đỉnh búa ngang đỉnh mào).
4. Búa: cán thép dài có vòng nắm, chuôi tròn chạm đất cạnh chân trước; đầu = 3 khối đá + gai trên + ngọc cam giữa; dựng đứng bên phải ảnh.
5. Frame: búa cao hơn đầu w≈0,05 → hình 66% khung, đỉnh ≥12% dưới mép.
6. Signature: mào đỏ cao + đầu búa đá khổng lồ. Mảng trang phục: mũ, vai, ngực trần + dây, giáp bụng, váy vải, áo choàng.
7. COLOUR PLAN: thép #5C6C80 / #2E3848 / #95A6BA; đá #8A8478 / #4E4A44 / #BDB6A8; da #B4B0A8 / #7A7670; vải #8E7038 / #4E3C1E; mào #D63A2C / #7E1C18; ngọc + khe mắt #FF9A2A; kem #FFF4DC.
8. Face: mũ kín, chỉ một khe mắt cam.
9. View: master side 30°, có danh sách visible / NOT visible.
10. Lint: clean (`prompts/master_p01.txt`).
12. Cost: 1 ảnh low 1024x1024 với ref, ~0.015 USD.

## Slots
- `{id}`: cinder_maul; `{body}`: biped
- `{design}`: xem `source/design/prompts/master_p01.txt` (đoạn CINDER MAUL)

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ⏳ v01 chờ duyệt | vẽ lại từ ảnh tham khảo, style heroic |
| icon | fal-image | ảnh tĩnh | ❌ | |
| pose_respawn | fal-image | ảnh tĩnh | ❌ | |
| pose_skill_leap_slam | fal-image | ảnh tĩnh | ❌ | |
| pose_skill_quake | fal-image | ảnh tĩnh | ❌ | |
| pose_skill_sweep | fal-image | ảnh tĩnh | ❌ | |
| run_side | video-sprite | loop | ❌ | |
| attack_side | video-sprite | one-shot | ❌ | |
| death_side | video-sprite | one-shot | ❌ | |
| respawn_side | video-sprite | one-shot | ❌ | |
| levelup_side | video-sprite | one-shot | ❌ | |
| skill_leap_slam_side | video-sprite | one-shot | ❌ | |
| skill_quake_side | video-sprite | one-shot | ❌ | |
| skill_sweep_side | video-sprite | one-shot | ❌ | |
| fx_leap_slam, fx_quake, fx_sweep, fx_respawn, fx_levelup | lib-fx / fx-layers | hiệu ứng | ❌ | |
| package | export | gói | ❌ | |

Estimated cost: 6 stills (~USD 0.09) + 8 clips (~USD 0.64) + retakes; fx in code (0 USD).
