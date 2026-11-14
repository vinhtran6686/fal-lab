# azure_blade: history

| date | sheet/still | vNN | model | score | verdict | issue | change for next version | requested by |
|---|---|---|---|---|---|---|---|---|
| 2026-11-12 | master | v01-v03 | gpt-image-2 low | 7.5-9 | rejected (deleted) | chibi 2,3 đầu, quá dễ thương | prompt master_p02: chiến binh 4 đầu, không chibi | user: "tuyệt đối không chibi" |
| 2026-11-12 | master | v04, v05 | gpt-image-2 low | 8 | not chosen (deleted) | đầu nhỏ (~6 đầu), v05 nhấn vàng nhạt | - | - |
| 2026-11-12 | master | v06 | gpt-image-2 low | 8.5 | approved by user | tỉ lệ ~6 đầu, giáp hơi nặng | - | user: "chốt v06" |
| 2026-11-12 | pose_skill_crescent_p1 | v01 | gpt-image-2 low | 9 | awaiting user | hai nắm đấm trên cán, đao chĩa xuống sau đầu đúng ý; không có lỗi | - | user: kỹ năng Trảm Trăng Khuyết |
| 2026-11-12 | pose_skill_crescent_p2 | v01 | gpt-image-2 low | 8.5 | awaiting user | đao cắm thẳng đứng, chỉ thấy khoảng nửa lưỡi; chân sau sát mép trái (lề ~45 px) | - | pipeline (ref master + pose A) |
| 2026-11-12 | pose_skill_crescent_p2 | v01 | gpt-image-2 low | 6 | rejected | đao cắm thẳng đứng xuống đất; user: phải là chém xuống, lưỡi song song và nằm trên mặt đất | prompt p02: lưỡi nằm ngang, áp trên đường đất, chĩa về phía trước; lề 8% | user |
| 2026-11-12 | pose_skill_crescent_p2 | v02 | gpt-image-2 low | 9 | awaiting user | lưỡi nằm ngang trên đường đất, đủ cả lưỡi; hai tay cùng nắm cán; thấy lưng và áo choàng; nhân vật nhỏ hơn pose A ~10% | căn cỡ khi ghép khung | user |
| 2026-11-12 | pose_skill_crescent_p2 | v03 | gpt-image-2 low | 8 | not chosen | mũi đao hơi hếch lên, lưỡi lơ lửng trên đất | - | - |
| 2026-11-12 | pose_skill_crescent_p2 | v03 | gpt-image-2 low | 8 | approved by user | mũi đao hơi hếch (user vẫn chọn) | - | user: "chốt p2_v03" |
| 2026-11-12 | skill_crescent_side | p01 | build_crescent.py ($0) | - | awaiting user | vệt xanh lam từ quỹ đạo gốc/mũi đao A->B qua đỉnh đầu; mũi đậm, cán nhạt | - | user |
| 2026-11-12 | skill_crescent_side | p02 | puppet rig + build_crescent.py ($0) | - | awaiting user | user: slash sáng hơn (thêm trắng), đặt đúng hướng lưỡi, thêm idle/chuẩn bị bằng studio rig | vệt = bề mặt lưỡi quét (đầu vệt trắng song song lưỡi), mũi đậm cán nhạt; thân qua rig: idle, A, impact B, hold B | user |
| 2026-11-12 | skill_crescent_side | p03 | rig A/B + build_crescent.py ($0) | - | awaiting user | user: rung lắc quá, bỏ idle, chỉ pose A/B có rig và dây chằng vai-ngực | rig tách torso/arms/blade, biên độ nhỏ (bước thân lớn nhất 1 px @1x) | user |
| 2026-11-12 | skill_crescent_side | p04 | build_crescent.py ($0) | - | awaiting user | user: slash (start) chưa khớp lưỡi kiếm | khung mọc vệt đầu tiên bắt đầu đúng trên lưỡi pose A (bề mặt quét từ vị trí lưỡi A, mép đầu giữ rõ); bỏ cục xanh lơ lửng của bộ sinh ở khung này | user |
| 2026-11-14 | pose_skill_sweep_p1 | v01 | gpt-image-2 low | 3 | rejected (not kept) | nhân vật quay ngực về người xem, hai tay ở giữa thân, lộ cả lưỡi: câu "xoay hơn dáng ba phần tư một chút" không đổi được dáng | tả theo hướng thân có tên: nhìn từ sau lưng, ngực không thấy, tay và cán sau thân | user |
| 2026-11-14 | pose_skill_sweep_p1 | v02 | gpt-image-2 low | 8 | approved by user | lưng và áo choàng ở giữa, đầu nghiêng nhìn phải, chỉ mũi đao thò ra trái; một tay vẫn thấy ở bên phải | - | user: "đúng rồi, chốt pose A" |
| 2026-11-14 | pose_skill_sweep_p2 | v01-v02 | gpt-image-2 low | 6-7 | rejected (not kept) | đao nằm ngang không chếch xuống; chân lệch trái ~70-100 px so với pose A | v03: toạ độ đao trên ảnh, góc 15°, chân bằng phần trăm | user |
| 2026-11-14 | pose_skill_sweep_p2 | v03 | gpt-image-2 low | 7 | approved by user | đao chếch xuống nhẹ (~3,5% chiều cao ảnh, yêu cầu 12%); chân lệch trái và nhân vật to hơn pose A ~4%; không đo điểm bám theo yêu cầu | căn chân và cỡ khi ghép | user: "duyệt pose B v03, không cần đo điểm bám" |
| 2026-11-14 | pose_skill_sweep_p3 | v01 | gpt-image-2 low | 8 | approved by user | pose C (giữa cú quét, đao chỉ thẳng vào người xem): thân đối xứng quay thẳng về người xem, đao thành nêm ngắn ~40% chỉ xuống dưới ảnh, tay duỗi về phía người xem; to hơn pose A ~9%, nêm đao đè lên thắt lưng | căn cỡ và chân khi ghép | user: "duyệt pose C v01" |
