# Prompt bàn giao (dán nguyên văn vào session mới)

```
Repo fal-lab, branch ccr-72a8430f-p86a1r (git pull trước).

Nhiệm vụ DUY NHẤT của session này: nghiên cứu và dựng lại ĐÚNG HÌNH (shape) của một hiệu ứng vẽ tay bằng path Bézier. Không làm hiệu ứng,
không chuyển động, không quầng sáng: chỉ hình tĩnh của từng lớp màu ở một vài frame.

Đọc trước, theo thứ tự:
1. lib-fx/research/bezier-shapes/BRIEF.md: bối cảnh, phân tích đã có (số lớp, màu, hình từng lớp, nhịp), các hướng đã thử và vì sao
   chưa đạt, nhiệm vụ, tiêu chí đạt.
2. ref/vfx/swirl-slash/README.md: dữ liệu: reference.gif (GIF gốc), frames/ (frame cắt sẵn 700x700 của từng biến thể) và layers/ (mặt nạ
   đen trắng của TỪNG LỚP MÀU ở từng frame, lửa: yellow/amber/pink/crimson, băng: ice/cyan/mid/deep).
3. CLAUDE.md (quy tắc repo).

Giả thuyết cần kiểm chứng: designer vẽ từng frame trong công cụ vector (Adobe Animate, Toon Boom...), mỗi lớp màu là một path Bézier khép kín
tô phẳng; vậy nếu đo được path thật và tìm ra công thức sinh path cho từng loại hình đặc trưng (lưỡi liềm có mũi kim, lưỡi lửa, lông vũ,
lưỡi trắng, móc vỡ, viền mỏng), thì code tái tạo được đúng hình và dùng lại được về sau.

Các bước:
1. Vector hoá mặt nạ layers/*.png thành path Bézier bậc 3 (sai số dưới ~1,5 px, có phát hiện góc nhọn); xuất SVG và chồng lên frame gốc để
   kiểm tra. Có thể dùng potrace / svgpathtools / find_contours + fit Bézier, hoặc tự viết.
2. Phân tích cấu trúc path của từng loại hình: số điểm neo, góc nhọn ở đâu, tay nắm, độ dày dọc xương sống, cách hai lớp chạm nhau.
3. Viết hàm sinh path tham số cho từng loại hình (xương sống + profile độ dày + gai/điểm nhọn...), không chép toạ độ.
4. Demo: dựng lại các lớp frame 3, 4, 5 của cả hai biến thể bằng các hàm đó, SVG + PNG đặt cạnh bản gốc, tính IoU với mặt nạ.
5. Lưu code và công thức vào lib-fx/research/bezier-shapes/, ghi kết luận (cái gì đúng, tham số nào quan trọng) để bổ sung vào
   lib-fx/SHAPE-RULES.md.

Tiêu chí đạt: IoU ≥ 0,85 cho lớp lớn, ≥ 0,7 cho lớp nhỏ; nhìn bằng mắt có cùng điểm nhọn, chỗ lồi lõm và nhịp to-nhỏ như bản gốc; không lặp
khuôn, không gradient. Báo kết quả bằng ảnh so sánh, rồi commit và push lên branch trên.
```
