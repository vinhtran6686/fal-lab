# Milestone 01: trả lời của chuyên gia (Technical Advisor) cho 12 câu hỏi

Ghi ngày 2026-11-10, nguyên ý phản hồi chuyên gia gửi user (bản gốc trong chat của session này), trả lời
`docs/milestone-01-advisor-questions.md`. Đây là **nguồn quyết định** của kế hoạch chính thức `docs/milestone-01-plan.md`; chỗ nào hai file lệch nhau thì
file này đúng.

**Kết luận chung:** đồng ý phạm vi Milestone 01 và hướng Character-first. Mục tiêu: animation chém xéo thật của Holy Commander → Weapon Trajectory →
Slash bằng Vector Kit → ghép với nhân vật thành một skill hoàn chỉnh.

## Q1. Pose: đồng ý, ưu tiên tái sử dụng

- **P1 (chuẩn bị):** kiếm cao về phía sau vai, mũi hướng lên và hơi ra sau; thân hơi xoay, nghiêng về sau lấy lực; chân trước bước lên; hai tay giữ kiếm.
- **P3 (kết thúc):** kiếm thấp phía trước, mũi hướng xuống; thân nghiêng về trước; trọng tâm dồn chân trước; vũ khí nằm trọn trong khung.
- Hướng chém: trên-sau → dưới-trước. Hệ nhân vật: X tăng theo hướng nhìn (phải), Y tăng lên trên; trên màn hình: trái-trên → phải-dưới.
- **Không tạo P2** lúc này; chỉ tạo nếu video cho thấy model không nội suy được nhát chém rõ.
- Trước khi gọi fal-image: kiểm tra `pose_skill_radiant_slash`, các frame của `attack_side` (nâng kiếm, kết thúc đòn); tái dùng nếu được. Frame dính VFX
  không dùng làm animation cuối, nhưng dùng được làm tham khảo tư thế. Chỉ tạo ảnh mới cho pose thực sự thiếu.

## Q2. Video sprite: đồng ý có điều kiện

- `h3-max-turbo`, image-to-video, P1 frame đầu, P3 frame cuối, prompt về cơ thể + vũ khí.
- Không: sword trail, slash VFX, glow, sparks, motion streak, ánh sáng do model tự tạo. Mục tiêu: thân sạch.
- **Timing không cố định 0,7 s / hit 40%.** Clip nguồn 3-4 s; chọn đoạn chuẩn bị → vung → kết thúc; xuất 15 fps; animation cuối mục tiêu **0,8-1,2 s**
  (chỉnh theo thực tế); frame chạm xác định theo chuyển động kiếm thật.
- State mới `attack_diag_side`, không ghi đè `attack_side`.
- Tối đa 4 lần tạo; **một clip mỗi lần**, review sau mỗi take; lỗi thì xác định nguyên nhân, sửa prompt hoặc pose rồi mới thử lại; **hai take liên tiếp
  không đạt thì dừng**, review lại choreography; không dùng lượt để thử prompt ngẫu nhiên. Không gọi API khi chưa có xác nhận chi phí.

## Q3. Quỹ đạo vũ khí: phương án A (click tay)

- Giao diện nhỏ chỉ cho milestone này (không làm annotation editor tổng quát): frame phóng 3-4×, click Root rồi Tip, tự lưu, tự đổi sang hệ H, vẽ đoạn
  Root-Tip, bật / tắt từng sample.
- Đánh dấu **mọi frame** đoạn active swing (dự kiến 5-8 frame @15 fps), không chỉ keyframe rồi nội suy.
- Dữ liệu: frame, timestamp, root, tip, visible, note. Kiếm bị che / mờ: `visible: false`, không đoán; nội suy sau này phải tách bạch sample quan sát và
  sample ước lượng.
- Sai số mục tiêu ±0,05 H. Contact sheet: Root, Tip, đoạn kiếm, frame index, timestamp. **User duyệt trước khi sinh VFX.**

## Q4. Hệ toạ độ: điều chỉnh H

- Gốc = pivot chân; X về trước; Y lên; đơn vị H; thời gian ms; xuất 15 fps.
- **H dùng trong phép tính = 55,5 px @1x** (`body_height_2x` = 111 trong `meta.json`; `fx_layers.tier_height()` cũng đọc số này). Lưu cả
  `tier_H_px = 60`, `body_height_px = 55.5`, `coordinate_H_px = 55.5`. 60 px chỉ là thông số thiết kế bậc M.
- Timestamp theo animation **sau khi đã chốt retime và export**.

## Q5. Biểu diễn slash: phương án C

- Dải năng lượng theo đường đi của mũi kiếm: quỹ đạo **Tip** là đường tham chiếu chính; **Root** cho hướng / tư thế lưỡi; **độ rộng là tham số độc lập**,
  không khoá vào chiều dài kiếm, không bắt buộc phủ hết vùng Root-Tip.
- **Đầu dẫn bám sát Tip.** Không đặt mặc định lùi 20%; có thể có `tip_offset_ratio` sau này, **mặc định 0**.
- Thử `EllipseFrame` trước. Ngưỡng: sai số trung bình ≤ 0,08 H, lớn nhất ≤ 0,15 H. Vượt ngưỡng: không ép; thử cubic Bézier / đường cong tự do, chỉ cho
  milestone này, chưa đưa PathFrame tổng quát vào core.
- Lưu ý: `EllipseFrame` chỉ là phép ánh xạ toạ độ, **chưa có hàm fit**; cần helper fit riêng và đo sai số thật.

## Q6. Thời gian VFX: không cho VFX đi trước kiếm

- Đầu slash đồng bộ Tip; đuôi phía sau theo hướng chuyển động. Đi trước kiếm là tham số nghệ thuật, để giai đoạn sau.
- Bắt đầu: không hardcode 0,3 H/frame; dùng **~20% vận tốc đỉnh**, kèm ngưỡng tối thiểu **~0,1 H/frame**. Ghi frame + timestamp bắt đầu thực tế.
- Sau chạm: giữ ~1 frame, rồi giãn / phân rã, tan trong ~3 frame (thử 4 nếu preview biến mất quá nhanh). Không kéo dài khiến người chơi tưởng còn chém.

## Q7. Lớp và hoà màu

- Back / front **theo che khuất thực tế** (back = đi sau thân / cape; front = trước nhân vật), không chia theo nửa cung. Luôn ở trước → một lớp front.
- Kế thừa `screen` của `radiant_slash`; mỗi lớp RGBA PNG trong suốt, không bake nền; blend ghi trong metadata.
- `render_sequence()` hiện ra RGB có nền: bổ sung xuất lớp trong suốt (theo coverage / alpha của geometry), tham khảo `tools/frame_tuner/export_fx.py`.
  Không làm hệ thống export tổng quát mới.

## Q8. Màu và độ đọc

- Vàng / trắng; 2-3 lớp: core sáng, main vàng, outer vàng cam nhẹ; glow nhỏ không lấn nhân vật. Nét chính ≥ 1,5 px @1x.
- Xuất @1x và @2x **từ cùng một geometry** (dựng @2x rồi downsample), không duy trì hai thiết kế. Kiểm tra riêng @1x; chi tiết nhỏ mất thì bỏ / giản lược.

## Q9. Nơi lưu và cấu trúc code

- Dữ liệu: `out/heroes/holy_commander/source/vfx/slash_diag/` (`weapon_track.json`, `slash_params.json`, cấu hình tái tạo).
- Output: `out/heroes/holy_commander/frames/fx/slash_diag/` (back nếu cần, front nếu cần, @1x, @2x, preview, `fx.json`).
- Code ở khu thử nghiệm riêng **`scripts/experiments/milestone_01/`**, import Vector Kit; không refactor core, không đổi generator cũ, không promote trước
  khi đạt. Chưa đăng ký vào thư viện VFX chung.

## Q10. Tiêu chí đạt

1. **Choreography:** một nhát chém xéo rõ, không có chuyển động thừa.
2. **Tách VFX:** VFX tách hoàn toàn khỏi body; bật / tắt từng lớp.
3. **Đồng bộ vũ khí:** đầu dẫn ↔ Tip ≤ 0,1 H tại sample quan sát được; hướng tiếp tuyến lệch ≤ 15° tại sample đủ điều kiện đo; không tính sample bị che / mờ.
4. **Tham số độc lập:** 3 biến thể width, length, curvature; mỗi biến thể đổi đúng một tham số.
5. **Đọc ở cỡ thật:** kiểm tra ở H = 55,5 px (bậc M 60 px); nét chính ≥ 1,5 px @1x; user nhận ra hướng và hình chém trên GIF @1x không phóng.
6. **Tái tạo:** dựng lại toàn bộ VFX từ `weapon_track.json` + `slash_params.json` bằng một lệnh; không sửa tay frame.

**Fitting gate** (mean ≤ 0,08 H, max ≤ 0,15 H) chỉ quyết định có dùng hình elip hay không; không thay tiêu chí 3.

## Q11. Hình nộm

Không đụng `dummy.py`; không dùng trong output cuối; kết quả cũ giữ làm regression reference cho Vector Kit.

## Q12. Điểm dừng (Gate)

- **Gate 0, tái sử dụng:** kiểm tra pose có sẵn, xác định pose dùng lại được và pose còn thiếu. Chưa gọi API.
- **Gate 1, pose:** tạo / tái dùng P1, P3; contact sheet 2 pose; kiểm tra vũ khí, độ dài, hướng nhìn, tỷ lệ thân. User duyệt trước khi tạo video.
- **Gate 2, video:** một clip; review GIF; thân sạch; chuyển động kiếm; chưa đạt thì tìm nguyên nhân rồi quyết retry. Không gọi clip tiếp khi chưa duyệt.
- **Gate 3, quỹ đạo:** contact sheet Root / Tip, overlay đoạn kiếm, biểu đồ quỹ đạo Tip, timestamp, báo cáo sai số fit. User duyệt trước khi sinh VFX.
- **Gate 4, VFX:** GIF chỉ VFX, PNG trong suốt, 3 biến thể, preview @1x thật và phóng 3×. User duyệt trước khi ghép.
- **Gate 5, ghép:** body + VFX back / front, GIF @1x, GIF 3×, metadata, recipe JSON, kết quả chấm 6 tiêu chí.

## Ghi chú kỹ thuật thêm

Không làm: Trajectory Editor đầy đủ, Timeline Editor tổng quát, tự động tracking, refactor các nhánh VFX, generator mới ngoài một slash thử nghiệm,
sửa animation đã duyệt, ghi đè asset cũ, gọi API khi chưa xác nhận chi phí. Mỗi lần thất bại ghi rõ nguyên nhân, kết quả, hướng điều chỉnh. Bước hiện
tại chưa đạt thì không làm bước sau.

**Quyết định cuối:** cập nhật kế hoạch nháp thành chính thức, cập nhật checklist + tiêu chí, kiểm tra tài nguyên tái dùng trước khi tạo ảnh, báo cáo kế
hoạch đã chốt + chi phí dự kiến, chờ user duyệt chi phí. **Chưa bắt đầu B1 / B2.**
