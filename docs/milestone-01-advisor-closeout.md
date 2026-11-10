# Milestone 01: nhận xét nghiệm thu của chuyên gia (nguyên văn, 2026-11-10)

User dán vào session. Quyết định tóm tắt ở `docs/decision-log.md`.

---

Mình đã review báo cáo Milestone 01. Chúc mừng, đây là một kết quả tốt và chứng minh được workflow Character → Weapon Trajectory → VFX → Integration.
Các quyết định:
1. Milestone 01
Chấp nhận kết quả như một Successful Proof of Concept.
Ghi nhận:

* Đã tạo được Slash từ trajectory của nhân vật thật.
* SweepFrame là phát hiện có giá trị.
* VFX được tách khỏi body và ghép lại thành skill.
* Có thể dựng lại bằng một lệnh.

Tuy nhiên, ghi rõ các caveat:

* Direction accuracy của SweepFrame chưa được kiểm chứng độc lập vì đường tạo và cách đo hướng cùng sử dụng các điểm Catmull-Rom.
* Width variation chưa đủ khác biệt về mặt thị giác.
* Một sợi vệt cung rất nhỏ còn sót trong body frame 11.
* Deterministic build đang phụ thuộc vào PYTHONHASHSEED=0.

Không cần làm lại Milestone 01.
2. SweepFrame
Đồng ý giữ SweepFrame và slash_from_track trong experiment.
Chưa promote vào core.
Ghi nhận SweepFrame hiện tại thuộc dạng Blade Sweep Geometry: vùng chuyển động được quét bởi toàn bộ lưỡi kiếm từ Root đến Tip.
Không mặc định rằng đây là công thức chung cho tất cả Slash.
3. Deterministic hash
Đưa lỗi hash() vào technical debt riêng.
Chưa sửa core trong milestone tiếp theo. Trước khi promote generator, cần thay bằng cơ chế deterministic có seed và kiểm tra regression của các Slash cũ.
4. Milestone tiếp theo
Không tiếp tục Cross Slash hoặc Double Slash phức tạp.
Mình chọn một thử nghiệm mới:
Single Rising Diagonal Slash – Holy Commander.
Mục tiêu:

* Tái sử dụng cùng master character.
* Chỉ tạo một động tác chém từ dưới lên trên.
* Không xoay thân phức tạp.
* Không có động tác chém thứ hai.
* Lấy Root/Tip trajectory.
* Kiểm chứng khả năng sử dụng lại SweepFrame.
* Tạo VFX có thể custom và ghép vào nhân vật.

Ưu tiên tái sử dụng các module và quy trình đã thành công.
5. Quy tắc nghiệm thu bổ sung
Ở milestone tiếp theo:

* Có dữ liệu trajectory độc lập để đánh giá độ chính xác.
* Width variation phải có khác biệt nhìn thấy được tại actual size.
* Dữ liệu và output phải reproducible.
* Không promote core trước khi có đủ hai trường hợp trajectory khác nhau.

Không xây thêm Editor hoặc hệ thống tổng quát.
Trước tiên hãy cập nhật decision log, experiment log và roadmap status cho Milestone 01.
Sau đó trình bày kế hoạch thử nghiệm Rising Diagonal Slash, các tài nguyên có thể tái sử dụng và chi phí API dự kiến.
Chưa gọi API hoặc bắt đầu tạo ảnh/video cho tới khi chủ dự án duyệt.
