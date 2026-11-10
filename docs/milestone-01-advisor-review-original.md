# Milestone 01: phản hồi gốc của chuyên gia (nguyên văn)

User dán vào session 2026-11-10. Tóm tắt có cấu trúc: [milestone-01-advisor-review.md](milestone-01-advisor-review.md).

---

MILESTONE 01 – TECHNICAL ADVISOR REVIEW
Character-Synchronized Diagonal Slash
Tôi đã xem xét kế hoạch nháp, các module Python và dữ liệu Holy Commander được cung cấp.
Tôi đồng ý với phạm vi Milestone 01 và hướng Character-first.
Mục tiêu của thử nghiệm:
Tạo một animation chém xéo thực tế của Holy Commander → lấy Weapon Trajectory → sinh Slash bằng Vector Kit → ghép với nhân vật thành một skill hoàn chỉnh.
Tôi có các quyết định và điều chỉnh sau.
Q1. POSE – ĐỒNG Ý, NHƯNG ƯU TIÊN TÁI SỬ DỤNG
Đồng ý với hai pose:
P1 – Anticipation

* Kiếm được đưa cao về phía sau vai.
* Mũi kiếm hướng lên và hơi ra sau.
* Thân hơi xoay và nghiêng về sau để lấy lực.
* Chân trước bước lên, tạo tư thế chuẩn bị chém.
* Hai tay giữ kiếm nhất quán.

P3 – Follow-through

* Kiếm ở vị trí thấp phía trước.
* Mũi kiếm hướng xuống.
* Thân hơi nghiêng về phía trước.
* Trọng tâm dồn về chân trước.
* Vũ khí vẫn phải nằm trọn trong khung.

Hướng chém:
Từ phía trên-sau xuống phía dưới-trước.
Trong hệ tọa độ nhân vật:

* X tăng theo hướng nhân vật đang nhìn (phải).
* Y tăng lên phía trên.

Quỹ đạo tổng thể tương ứng với chuyển động từ trái-trên sang phải-dưới trên màn hình.
Không tạo P2 ở thời điểm này.
Có hai pose đầu-cuối là đủ để thử nghiệm video-sprite.
Chỉ tạo P2 nếu kết quả video cho thấy model không nội suy được chuyển động chém rõ ràng.
Bổ sung tiết kiệm chi phí
Trước khi gọi fal-image:

* Kiểm tra `pose_skill_radiant_slash` đã có trong repository.
* Kiểm tra các frame của `attack_side`, đặc biệt các frame nâng kiếm và kết thúc đòn.
* Đánh giá xem có thể tái sử dụng một pose làm P1 hoặc P3 hay không.

Không sử dụng trực tiếp các frame đã bị dính VFX làm animation cuối, nhưng có thể dùng chúng làm tài liệu tham khảo về tư thế.
Chỉ tạo ảnh mới cho những pose thực sự còn thiếu.
Q2. VIDEO SPRITE – ĐỒNG Ý CÓ ĐIỀU KIỆN
Đồng ý:

* Model: `h3-max-turbo`.
* Image-to-video.
* Sử dụng P1 làm frame đầu.
* P3 làm frame cuối.
* Prompt tập trung vào chuyển động cơ thể và vũ khí.

Không sử dụng:

* Sword trail.
* Slash VFX.
* Glow.
* Sparks.
* Motion streak.
* Các hiệu ứng ánh sáng do model tự tạo.

Mục tiêu là có một animation thân sạch để xây dựng VFX độc lập.
Điều chỉnh về timing
Không cố định duration cuối là 0.7 giây và hit ở 40%.
Lý do:
Chúng ta chưa biết choreography thực tế của clip sẽ diễn ra như thế nào. Nếu ép timing quá sớm, có thể làm chuyển động mất tự nhiên.
Đề xuất:

* Source video: 3–4 giây theo yêu cầu vận hành của video-sprite.
* Sau khi có clip, chọn đoạn hành động thực tế.
* Cắt đoạn preparation → active swing → follow-through.
* Xuất về 15 FPS.
* Mục tiêu duration của animation cuối khoảng 0.8–1.2 giây, có thể điều chỉnh theo kết quả thực tế.
* Xác định strike/contact frame dựa trên chuyển động kiếm thực tế, không áp đặt 40%.

Giữ state mới `attack_diag_side`, không ghi đè `attack_side` hiện có.
Giới hạn số lần thử
Tối đa 4 lần tạo video.
Tuy nhiên:

* Chỉ tạo một clip mỗi lần.
* Sau take đầu tiên phải review.
* Nếu lỗi, xác định nguyên nhân và điều chỉnh prompt hoặc pose trước khi retry.
* Nếu hai take liên tiếp không đạt, dừng để review lại choreography.
* Không sử dụng hết 4 lượt chỉ để thử prompt ngẫu nhiên.

Không gọi API nếu chưa có xác nhận chi phí từ chủ dự án.
Q3. WEAPON TRAJECTORY – CHỌN PHƯƠNG ÁN A
Chọn A: sử dụng giao diện click thủ công.
Không cần xây dựng một annotation editor tổng quát.
Chỉ tạo một giao diện nhỏ phục vụ milestone này:

* Hiển thị frame được phóng lớn 3–4 lần.
* Người dùng click Blade Root.
* Người dùng click Blade Tip.
* Tự lưu tọa độ.
* Tự ánh xạ tọa độ sang hệ H.
* Hiển thị đường nối Root–Tip để kiểm tra hướng của lưỡi kiếm.
* Có thể bật/tắt từng sample.

Sampling
Đánh dấu mọi frame trong đoạn active swing, dự kiến khoảng 5–8 frame ở 15 FPS.
Không chỉ đánh dấu 3–5 keyframe rồi nội suy toàn bộ nếu đã có thể lấy dữ liệu từ các frame thực tế.
Dữ liệu cần có:

* frame.
* timestamp.
* Blade Root.
* Blade Tip.
* visible.
* note nếu cần.

Frame kiếm bị che hoặc mờ:

* Đánh dấu `visible: false`.
* Không tự đoán tọa độ.
* Có thể nội suy sau này, nhưng phải phân biệt sample quan sát trực tiếp và sample ước lượng.

Sai số mục tiêu: ±0.05H.
Sau khi đánh dấu cần xuất contact sheet có đầy đủ:

* Vị trí Root.
* Vị trí Tip.
* Đoạn kiếm.
* Frame index.
* Timestamp.

Chủ dự án phải duyệt dữ liệu này trước khi sinh VFX.
Q4. COORDINATE SYSTEM – ĐIỀU CHỈNH H
Chọn hệ tọa độ:

* Origin: Character Feet Pivot.
* X: hướng phía trước của nhân vật.
* Y: hướng lên trên.
* Unit: H.
* Time: milliseconds.
* Output: 15 FPS.

H sử dụng trong phép tính
Sử dụng H thực tế = 55.5 px @1x.
Căn cứ:
`body_height_2x = 111` trong `meta.json`.
Đồng thời lưu:

* `tier_H_px = 60`
* `body_height_px = 55.5`
* `coordinate_H_px = 55.5`

Lý do:
`fx_layers.tier_height()` hiện đã đọc chiều cao thân thực tế từ metadata.
Sử dụng 55.5 px để tránh sai lệch khi chuyển tọa độ từ sprite frame sang H.
Giữ 60 px làm thông số kích thước thiết kế tier M, không dùng nó thay cho kích thước thực tế trong phép biến đổi tọa độ của milestone này.
Timestamp phải phản ánh thời gian của animation sau khi đã chốt retime và export.
Q5. SLASH REPRESENTATION – CHỌN PHƯƠNG ÁN C
VFX được biểu diễn dưới dạng một dải năng lượng bám theo đường chuyển động của mũi kiếm.
Cụ thể:

* Blade Tip trajectory là đường tham chiếu chính.
* Blade Root dùng để xác định hướng và tư thế lưỡi kiếm.
* Độ rộng VFX là một parameter độc lập.
* Không khóa độ rộng VFX với chiều dài vật lý của kiếm.
* Không bắt buộc vùng VFX phải bao phủ toàn bộ diện tích quét từ Root đến Tip.

Đặc biệt:
Đầu dẫn của Slash phải bám sát vị trí Blade Tip.
Không đặt mặc định một offset 20% chiều dài kiếm nếu điều đó khiến vệt chém không còn khớp với đường đi của mũi kiếm.
Có thể bổ sung `tip_offset_ratio` thành một parameter sau này, nhưng default = 0 trong thử nghiệm này.
Geometric fitting
Đồng ý thử EllipseFrame trước.
Ngưỡng đánh giá ban đầu:

* Mean fitting error ≤ 0.08H.
* Maximum fitting error ≤ 0.15H.

Nếu vượt ngưỡng:

* Không cố ép dữ liệu vào EllipseFrame.
* Thử cubic Bezier hoặc một đường cong tự do phù hợp hơn với trajectory.
* Chỉ xây dựng giải pháp cho milestone này.
* Chưa cần đưa một PathFrame tổng quát vào core nếu chưa có nhu cầu thực tế.

Lưu ý kỹ thuật: `EllipseFrame` hiện có là coordinate mapping, chưa có phương thức fit tự động từ trajectory samples. Cần có một helper fitting riêng và đánh giá sai số thực tế.
Không nhầm lẫn giữa việc có EllipseFrame và việc đã có thuật toán ellipse fitting.
Q6. VFX TIMING – KHÔNG CHO VFX ĐI TRƯỚC KIẾM
Chọn nguyên tắc:
Slash head đồng bộ với Blade Tip. Tail nằm phía sau theo hướng chuyển động.
Không cho đầu VFX đi trước kiếm một frame trong milestone vật lý đầu tiên.
Lý do:

* Chúng ta đang thử nghiệm Weapon Trail.
* Cần chứng minh VFX sinh ra từ chuyển động thật.
* Việc cho VFX đi trước là một artistic parameter có thể thử nghiệm ở giai đoạn sau.

Start condition
Không hardcode 0.3H/frame làm ngưỡng duy nhất.
Đề xuất dùng ngưỡng vận tốc tương đối:

* Dựa trên peak velocity của nhát chém.
* Bắt đầu tạo VFX khi tốc độ đạt khoảng 20% peak velocity.
* Có thể dùng ngưỡng tối thiểu khoảng 0.1H/frame để tránh sinh VFX khi nhân vật chỉ đang đưa kiếm vào vị trí chuẩn bị.

Cần ghi timestamp và frame bắt đầu thực tế.
Dissipation
Sau strike/contact:

* Giữ vệt thêm khoảng 1 frame.
* Bắt đầu giãn và phân rã.
* Fade trong khoảng 3 frame tiếp theo.
* Có thể thử 4 frame nếu preview cho thấy hiệu ứng biến mất quá nhanh.

Không kéo dài VFX quá mức khiến người chơi tưởng rằng nhân vật vẫn đang tiếp tục chém.
Q7. LAYERING & BLENDING
Đồng ý phân lớp back/front nhưng phải căn cứ vào occlusion thực tế.
Quy tắc:

* Back: phần VFX thực sự đi phía sau cơ thể hoặc cape.
* Front: phần VFX đi phía trước nhân vật.
* Không chia layer tùy tiện theo nửa trên/nửa dưới của cung.

Nếu thực tế đường chém luôn nằm phía trước nhân vật thì chỉ cần một lớp front.
Nếu có sự chuyển đổi giữa phía sau và phía trước thì mới tách thành hai lớp.
Blend mode
Ưu tiên kế thừa phương thức `screen` của `radiant_slash`.
Output phải có RGBA transparent PNG cho từng layer.
Không bake nền đen hoặc nền tối vào VFX asset.
Lưu blend mode trong metadata.
Lưu ý:
Vector Kit hiện dùng `render_sequence()` để tạo RGB output có background. Cần bổ sung khả năng export các layer trong suốt, dựa trên coverage và alpha của geometry.
Có thể tham khảo cơ chế alpha conversion trong `tools/frame_tuner/export_fx.py`.
Không tạo một hệ thống export tổng quát mới. Chỉ bổ sung phần cần thiết cho milestone này.
Q8. COLOR & PIXEL READABILITY
Chọn màu vàng/trắng, phù hợp với Holy Commander và Radiant Slash hiện tại.
Visual:

* 2–3 lớp màu.
* Core sáng.
* Main trail vàng.
* Outer trail vàng cam nhẹ.
* Glow nhỏ, không lấn át nhân vật.

Độ dày nét chính tối thiểu: 1.5 px @1x.
Output size
Xuất đồng thời:

* @1x.
* @2x.

Không cần duy trì hai thiết kế VFX khác nhau ở milestone này.
Tạo từ cùng một geometry ở độ phân giải @2x, sau đó downsample thành @1x.
Kiểm tra riêng ở @1x. Nếu các chi tiết nhỏ biến mất thì bỏ hoặc giản lược chúng, không cố giữ mọi chi tiết.
Q9. FILE LOCATION & MODULE STRUCTURE
Đồng ý với vị trí dữ liệu:
`out/heroes/holy_commander/source/vfx/slash_diag/`
Chứa:

* `weapon_track.json`
* `slash_params.json`
* Các dữ liệu và cấu hình tái tạo.

Output:
`out/heroes/holy_commander/frames/fx/slash_diag/`
Chứa:

* Back layer nếu cần.
* Front layer nếu cần.
* Frames @1x.
* Frames @2x.
* Preview.
* `fx.json`.

Code
Trong milestone đầu tiên, giữ generator ở khu vực experiment riêng, ví dụ:
`scripts/experiments/milestone_01/`
Tận dụng các module Vector Kit hiện tại qua import.
Không refactor core.
Không thay đổi các generator cũ.
Không promote thành generator chính thức trước khi sản phẩm đạt.
Sau khi milestone thành công mới quyết định có chuyển thành module ổn định trong `lib-fx/_core/vector/` hay không.
Chưa đăng ký asset vào global VFX Library.
Q10. ACCEPTANCE CRITERIA
Đồng ý các tiêu chí và chốt như sau:
Criterion 1 – Character Choreography
Nhân vật thực hiện một nhát chém xéo rõ ràng, không có chuyển động thừa làm sai ý đồ.
Criterion 2 – VFX Separation
VFX tách khỏi body hoàn toàn.
Có thể bật/tắt từng layer.
Criterion 3 – Weapon Synchronization

* Khoảng cách đầu dẫn VFX và Blade Tip ≤ 0.1H tại các sample quan sát được.
* Sai lệch hướng tiếp tuyến ≤ 15 độ tại các sample đủ điều kiện đo.
* Không tính sample mà vũ khí bị che hoặc không nhìn rõ.

Criterion 4 – Parameter Independence
Tạo ba biến thể:

1. Width variation.
2. Length variation.
3. Curvature variation.

Mỗi biến thể chỉ thay đổi đúng một parameter.
Các thông số khác giữ nguyên.
Criterion 5 – Actual-size Readability

* Kiểm tra ở H = 55.5 px thực tế, tương ứng tier M 60 px.
* Độ dày đường chém chính tối thiểu 1.5 px @1x.
* Chủ dự án phải nhận ra hướng chém và hình dạng khi xem GIF @1x mà không phóng lớn.

Criterion 6 – Reproducibility
Có thể tái tạo toàn bộ VFX từ:
`weapon_track.json + slash_params.json`
bằng một lệnh.
Không phải sửa hình ảnh từng frame bằng tay sau khi generate.
Fitting Gate
Giữ ngưỡng fitting đề xuất:

* Mean ≤ 0.08H.
* Max ≤ 0.15H.

Đây là ngưỡng quyết định hình học elip có đủ phù hợp để dùng tiếp hay không, không thay thế tiêu chí kiểm tra đầu dẫn VFX bám mũi kiếm.
Nếu không đạt thì chuyển sang đường cong tự do trong phạm vi milestone.
Q11. DUMMY
Không đụng tới `dummy.py`.
Giữ nguyên chức năng hiện tại.
Không sử dụng dummy trong output cuối của milestone, vì chúng ta đã có nhân vật thật.
Có thể giữ kết quả dummy cũ làm regression reference cho Vector Kit.
Q12. REVIEW GATES & WORKFLOW
Đồng ý việc chia điểm dừng, nhưng đề xuất tách nhỏ hơn để tránh tiêu tốn API khi pose chưa đạt.
Gate 0 – Asset Reuse Review

* Kiểm tra các pose hiện có.
* Xác định pose nào tái sử dụng được.
* Chỉ xác định các pose còn thiếu.

Chưa gọi API.
Gate 1 – Pose Approval

* Tạo hoặc tái sử dụng P1/P3.
* Contact sheet hai pose.
* Kiểm tra vũ khí, độ dài, hướng nhìn, tỷ lệ thân.

Chủ dự án duyệt trước khi tạo video.
Gate 2 – Video Approval

* Tạo một clip.
* Review GIF.
* Kiểm tra body cleanliness.
* Kiểm tra chuyển động kiếm.
* Nếu chưa đạt, tìm nguyên nhân và quyết định retry.

Không gọi clip tiếp theo nếu chưa duyệt.
Gate 3 – Trajectory Approval
Xuất:

* Contact sheet có Root/Tip.
* Weapon segment overlay.
* Biểu đồ quỹ đạo Tip.
* Timestamp.
* Fitting error report.

Chủ dự án duyệt trước khi generate VFX.
Gate 4 – VFX Approval
Xuất:

* VFX-only GIF.
* VFX transparent PNG.
* 3 biến thể width/length/curvature.
* Preview tại actual size @1x.
* Preview phóng lớn 3x.

Chủ dự án duyệt trước khi tích hợp.
Gate 5 – Final Integration
Xuất:

* Body + VFX back/front.
* GIF @1x.
* GIF 3x.
* Asset metadata.
* Recipe JSON.
* Kết quả chấm 6 acceptance criteria.

ADDITIONAL TECHNICAL NOTES

1. Không tự động phát triển toàn bộ Trajectory Editor.
2. Không xây Timeline Editor tổng quát.
3. Không tự động tracking.
4. Không refactor các nhánh VFX.
5. Không tạo thêm generator mới ngoài phạm vi một Slash thử nghiệm.
6. Không thay đổi animation đã duyệt.
7. Không ghi đè asset cũ.
8. Không gọi API nếu chưa có xác nhận chi phí.

Mỗi lần thất bại phải ghi nhận rõ nguyên nhân, kết quả và hướng điều chỉnh.
Không tiếp tục các bước phía sau khi bước hiện tại chưa đạt.
FINAL DECISION
Về mặt kỹ thuật, tôi đồng ý với hướng Milestone 01 sau các điều chỉnh nêu trên.
Claude hãy:

1. Cập nhật `docs/milestone-01-plan-DRAFT.md` thành kế hoạch chính thức.
2. Cập nhật checklist và acceptance criteria.
3. Kiểm tra các tài nguyên có thể tái sử dụng trước khi tạo ảnh mới.
4. Chỉ báo cáo kế hoạch đã chốt và chi phí dự kiến.
5. Chờ chủ dự án duyệt chi phí trước khi gọi fal-image hoặc video API.

Chưa bắt đầu thực hiện B1/B2.
Mục tiêu cuối cùng vẫn là tạo được một sản phẩm có thể sử dụng:
Holy Commander thực hiện một nhát chém xéo, VFX được sinh từ Weapon Trajectory và đồng bộ với chuyển động thực tế của nhân vật.
