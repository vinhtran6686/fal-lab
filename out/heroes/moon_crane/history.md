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

## Tóm tắt các lần thử 2026-11-15 đến 2026-11-17 (đã dọn; file bỏ vẫn nằm trong lịch sử git)

**Giữ lại (được chọn hoặc đáng tham khảo):**
- `master_v08`: master đã chốt.
- `sweep_spear_join.mp4` và hai take: cú chém ngang quay người, đã chốt 2026-11-15.
- `skill_spin_back_v5_t01.mp4` (prompt `prompts/skill_spin_back_v5.txt`): một cú quét ngang hông liên tục, thân xoay từ hông, quay lưng về người xem, mắt nhìn mục tiêu bên phải; đã chốt. Vệt thừa của mô hình được loại bằng cách tách nền chặt hơn.
- `pose_library_h3_t02.mp4` (prompt `prompts/pose_library_h3_t02.txt`, khung đầu `prompts/pose_library_h3_first_frame_768.png`): video 10 giây, 11 động tác nối nhau, bản tốt nhất trong các thử nghiệm thư viện pose; danh sách khung dùng được ở `source/video/pose_library_h3_t02_poses.json`. Còn lỗi: ba động tác "nhìn nghiêng hoàn toàn" quay về camera, một pose bị giữ khoảng 2,3 giây, vài khung nhòe.
- `pose_profile_right_v01.png` (prompt `source/design/prompts/pose_profile_right_p01.txt`): góc nghiêng thật nhìn sang phải, bước đâm, thương nằm ngang; một ảnh `fal-image`, 0,0183 USD.
- Doc: `docs/pipeline/reference-gif-pose-extraction-difficulties.md` (tham chiếu king, khung ứng với video, khó khăn còn lại).

**Đã bỏ vì không đạt:** các cú quét xoay nhiều vòng (vòng 2 đến 4 của `skill_spin_back`), tư thế tấn thấp chép từ một khung mẫu, dựng pose-to-pose bằng Puppet Kit (6 pose tĩnh, rig một mảnh, vệt `ring_fast` trên thân), clip thư viện pose bản đầu (8 động tác), prompt cho Google Flow, thử LTX-2.3 reference-video-to-video (2/10), clip ghim từ master sang góc nghiêng. Chi phí của các lần thử vẫn nằm trong `out/costs.csv`.
