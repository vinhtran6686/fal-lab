# moon_crane: history

| date | sheet/still | vNN | model | score | verdict | issue | change for next version | requested by |
|---|---|---|---|---|---|---|---|---|
| 2026-11-15 | master | v01 | gpt-image-2 low | 6 | rejected (deleted) | khối vector mảnh, 7 đầu, nét viền mảnh, lộ cơ bắp, giáp vai lệch bên | prompt có số đầu, nét dày | user: chọn concept A |
| 2026-11-15 | master | v02 | gpt-image-2 low | 7 | rejected (deleted) | painterly giàu chi tiết, hơn 6 đầu | user: bớt chi tiết, theo vector | user |
| 2026-11-15 | master | v03 | gpt-image-2 low | 7.5 | rejected (deleted) | vector, ~4 đầu, mặt còn nhiều chi tiết | mặt tối giản | user |
| 2026-11-15 | master | v04 | gpt-image-2 low | 7.5 | rejected (deleted) | mặt tối giản, cánh hạc đổi sang sai bên | theo ảnh mẫu: 3 đầu, nắm đấm lớn | user |
| 2026-11-15 | master | v05 | gpt-image-2 low | 8 | rejected (deleted) | tỉ lệ 3 đầu, vector chắc khối; vũ khí rìu | đổi sang cây thương | user: "hợp lý hơn, đổi vũ khí là cây thương" |
| 2026-11-15 | master | v06 | gpt-image-2 low | 8 | rejected (deleted) | thương; thân chàm gần đen, vàng mảnh, mắt nhỏ, mũi thương tối (thử thu nhỏ 60 px) | sáng hơn, mắt phát sáng, vàng dày, nét viền dày, dáng có sức sống | user: "đồng ý, tạo v07" |
| 2026-11-15 | master | v07 | gpt-image-2 low | 8.5 | rejected (deleted) | màu: bốn họ bão hoà cạnh tranh, giống màu pháp sư mẫu | bảng màu hex: một sắc chủ đạo bốn độ sáng, họ ấm, vàng | user: "màu chưa matching ảnh mẫu" |
| 2026-11-15 | master | v08 | gpt-image-2 low | 9 | approved by user | màu hài hoà; mũi thương to, chắn trăng nhỏ; da hơi sẫm; dáng còn cứng | - | user: "style này ổn nhất và khớp với mong đợi" |
| 2026-11-15 | skill_sweep_spear (video) | take a | h3-max-turbo | 7 | dùng một phần | A đúng, mid và B đúng, C đúng; có 4 khung nhoè và thương bay khỏi khung (khung 47-50) | bỏ khung nhoè, ghép với clip B->C | user: "v01 tốt hơn nhiều" |
| 2026-11-15 | skill_sweep_spear (video) | take b (B->C ghim) | h3-max-turbo | 7.5 | dùng | ghim đầu cuối đúng; 2 khung nhoè; thương hạ chúi | - | user |
| 2026-11-15 | skill_sweep_spear (video) | join | ghép 0 USD | 7.5 | approved by user | một cú nhảy 0,04 s từ quay lưng sang nghiêng | - | user: "Chốt phiên bản đó" |

## 2026-11-15 — pose_horse_stance_v01 (low horse stance, spear across the shoulders)
Pose copied from a user reference frame (single pixel-art frame as `--ref`, design not copied). 2 images (0.0188 + 0.0189 USD); v2 kept, cropped and rescaled to a 10% margin (the model ignored the margin and the 50-degree turn). Body still near-front.
