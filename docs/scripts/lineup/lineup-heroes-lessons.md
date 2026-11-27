# Bài học: lưới hero từ master đã chốt

Những gì rút ra từ các lần người dùng chốt hoặc trả lại khi làm 5 hero (`out/heroes/_lineups/heroic_ref_five/`, 2026-11-27). Đọc trước khi viết prompt master vẽ lại hoặc prompt chuyển động cho lưới hero. Quy trình: `lineup-heroes-from-masters.md`; mẫu prompt: `prompts/hero-lineup-*.txt`.

## 1. Master vẽ lại từ ảnh tham khảo
- Model vẽ to hơn số xin khoảng 1,4-1,7 lần (xin 52-66% → được 82-95%); model theo tỷ lệ của ảnh tham khảo hơn số đầu trong prompt (xin 5 đầu cho ảnh gốc 7 đầu → ~6,5 đầu); nét viền mảnh dần nếu ảnh gốc nét mảnh. Kiểm bằng cách đặt các con cạnh nhau ở 84 px và 60 px.
- Ảnh gốc quay trái thì lật ngang trước khi gửi; viết tay cầm vũ khí theo phía màn hình (near/far đổi khi lật).
- 5/5 con đạt ở ảnh đầu khi prompt bắt đầu bằng "FAITHFUL REDRAW ... take ONLY its design" và giữ khối style heroic đã duyệt.

## 2. Clip chuyển động: các lần chốt và trả lại
| Tình huống | Điều xảy ra | Cách làm đúng |
|---|---|---|
| Death: "its killing blow comes from an unseen attacker" | model vẽ một đòn lửa đánh vào cả 5 con | không mô tả gì từ bên ngoài đánh vào; nhân vật tự ngã; cấm lửa, nổ, đạn, va chạm |
| Câu chung cho cả nhóm | hành động lan sang con khác | mỗi con một đoạn riêng, câu "independent, never copy" (người dùng: "mỗi nhân vật phải độc lập") |
| Cung thủ: "the arrow simply vanishes" | 3 mũi tên bay sang ô bên cạnh | không có mũi tên nào: "pulls the bare string with two EMPTY fingers", cấm mũi tên hai lần; model vẫn vẽ một mũi tên lúc kéo dây → xóa khi tách khung |
| Cung thủ bắn trên không (nhảy rồi mới kéo) | kéo cung xảy ra trên đất | **giương cung sẵn trước khi nhảy**, chỉ nhả ở đỉnh cú nhảy, bàn tay bung ra rõ ("flies open behind his head") |
| Mưa tên | cần cung hướng trời, kéo thả liên tục | "aiming HIGH ... about 60 degrees", "THREE times in a row", mũi tên là vfx riêng |
| Xoay vòng với vũ khí dài (rìu) | đầu rìu chạm ô bên cạnh | tránh xoay với vũ khí dài trong lưới, hoặc chạy con đó riêng |
| Khổng lồ đá (vai to, đầu nhỏ) | khi đấm hoặc khom, đầu lún giữa vai, thân xoay đi, mất mặt | khóa "head, eyes, beard stay visible above his shoulders and face screen right in every frame", kết thúc đứng hoặc khom vừa; động tác to (giơ hai tay, dậm hai lần) cho ra hình sinh động hơn ("đơn điệu quá" khi chỉ dậm một lần) |
| Nhân vật bay | đẩy chưởng thành lao bay hoặc dang hai tay | chấp nhận được; ghi "never touches the ground" |

## 3. Động tác khó: để model tự sáng tạo (hiệp sĩ búa, skill 3)
Skill 3 của `cinder_maul` thử 5 lần. Bốn lần mô tả chi tiết đều hỏng: quét ngang (búa chĩa thẳng như giáo), "vòng tiếp về phía xa" (búa dừng ở sau lưng), combo 3 nhịp viết rõ (nhịp quét dừng sai phía), hất búa từ dưới lên (cuối nâng búa ngang như nâng tạ). Lần thứ năm chỉ viết chung: "unleashes a fierce combo of THREE different powerful strikes in a row ... choose the strikes freely and make them heavy, fast and varied ... hammer staying inside his own cell" → **người dùng chốt**.
Quy tắc: với cú vung ngang hoặc chuỗi đòn khó tả bằng hướng màn hình, sau **hai** lần mô tả chi tiết không đạt thì viết một câu mục đích (số đòn, tính chất, ràng buộc ô) và để model chọn đòn. Cú bổ và đập theo chiều dọc màn hình (attack, skill 1) model làm đúng ngay lần đầu.
