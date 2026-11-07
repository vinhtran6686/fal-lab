# Luật dựng hình VFX bằng code: phương pháp trường nhiệt cắt tầng (field method)

Rút ra từ việc phân tích GIF tham khảo "xoáy chém" (2026-11-07, [RECIPE-swirl.md](RECIPE-swirl.md)) và đối chiếu với cách làm VFX
truyền thống. Code: `_core/fieldfx.py`. Dùng cho mọi hiệu ứng có **nhiều tầng màu phẳng chồng lên nhau** (chém, lửa, nước, băng,
năng lượng): đây là cách mặc định từ nay, thay cho việc vẽ từng mảng màu riêng.

## 1. Bản chất của kiểu hình này

Mở GIF ra đếm màu từng điểm ảnh: mỗi biến thể chỉ có **3-4 màu tô phẳng**, mỗi màu đúng một mã màu; phần chuyển màu duy nhất là
quầng sáng. Ba điều quan sát được:

1. **Các tầng lồng nhau, không chồng lên nhau tuỳ ý**: vàng luôn nằm trong vùng hồng, hồng trong vùng đỏ. Tầng nóng nhỏ hơn và nằm
   trong tầng nguội.
2. **Ranh giới giữa các tầng là đường liền mạch** (cong mềm, răng cưa sắc), không có khe hở hay mép chồng.
3. **Tầng nóng biến mất trước**: vàng hết ở frame 6, hồng hết ở frame 8, đỏ còn những móc nhỏ tới frame 13. Hình tự vỡ thành mảnh ở
   những chỗ "nguội" nhất.

Ba điều đó đúng là hành vi của **một trường xám liên tục được cắt bằng nhiều ngưỡng cứng**: tầng = khoảng giữa hai ngưỡng, ranh giới
= đường đồng mức của trường (nên luôn liền mạch và lồng nhau), nguội = nâng ngưỡng (tầng trên co lại trước, chỗ trường thấp thủng trước).

## 2. Cách làm truyền thống tương ứng

- **Vẽ tay (2D cel)**: hoạ sĩ VFX vẽ hình lửa / nước bằng các mảng màu phẳng lồng nhau: lõi sáng, thân, viền tối. Họ cho hình tan
  bằng cách cắt hình ra thành nhiều mảnh nhỏ dần, đa dạng cỡ, không đối xứng. Đây là các nguyên tắc trong *Elemental Magic* của Joseph
  Gilland: mảng to/vừa/nhỏ, khoảng cách không đều, tránh đối xứng.
- **Real-time (shader)**: tương đương đúng với cách trên là **alpha erosion**.
  - Một texture xám, cộng một gradient có hướng (để tan từ một phía), cắt bằng ngưỡng: hình tan khi ngưỡng tăng.
  - Cắt bằng `step` (cứng) cho kiểu toon; `smoothstep` (mềm) cho kiểu mờ.
  - Tô màu bằng color ramp nhiều bậc.
  - Gradient hướng thường lấy theo đường đi (path) của vệt chém, kèm một giá trị "tuổi" 0..1.
- Code của mình làm đúng việc của shader đó, nhưng trên CPU, từng frame, ở độ phân giải siêu mẫu 3x rồi thu nhỏ để mép mịn.

Nguồn: [alpha erosion (VFX doc)](https://vfxdoc.readthedocs.io/en/latest/shaders/alpha-erosion/),
[RealtimeVFX: erosion có hướng](https://realtimevfx.com/t/battlerite-erosion-ue4/4706/2),
[RealtimeVFX: gradient dọc theo path](https://realtimevfx.com/t/how-to-map-gradient-on-path-for-vfx-texture/23454),
[khoá học ground slash stylized (dissolve + gradient map)](https://www.udemy.com/course/unity-vfx-stylized-ground-slash/),
[Elemental Magic Vol. I (Gilland)](https://www.routledge.com/Elemental-Magic-Volume-I-The-Art-of-Special-Effects-Animation/Gilland/p/book/9780240811635).

## 3. Công thức chung (7 bước)

1. **Hình bao (silhouette)**: định nghĩa bằng toạ độ của chính hiệu ứng. Với vệt chém: toạ độ dọc nét `v` (0 đuôi → 1 đầu) và ngang
   nét `w` (-1 mép trong → +1 mép ngoài), có từ `spiral_coords` (hoặc toạ độ cực, toạ độ theo đường cong khác). Bề rộng theo `v` là một
   hàm profile (`v^a·(1-v^b)^c`).
2. **Trường nhiệt H = tổng các thành phần**, mỗi thành phần một ý nghĩa:
   - **Tuổi** `A = 1 - (t - lúc đầu nét đi qua)/τ`: phần mới vẽ nóng, phần cũ nguội. Tính được vì biết hàm quét `head(t)`, đảo ngược ra
     `time_at(θ)`.
   - **Vị trí ngang** `C`: lửa nóng ở mép ngoài (`(w+1)/2`); băng nóng ở giữa lệch ra ngoài (`1 - |w-0.3|^1.3`).
   - **Kết cấu có hướng** cho răng cưa / lông vũ: `saw(v·k + s·w + nhiễu)`. Sawtooth nghiêng: đường đồng mức thành lưỡi nhọn chĩa ngược
     chiều quét. `k` (mật độ) và pha có nhiễu 1-D để răng to nhỏ không đều.
3. **Cắt tầng** (`posterize`): danh sách ngưỡng tăng dần, mỗi ngưỡng một màu phẳng; dưới ngưỡng đầu là trong suốt (đó chính là xói mòn).
   Tầng mỏng (ví dụ viền hổ phách giữa vàng và hồng) = hai ngưỡng sát nhau.
4. **Nguội**: trừ dần `cool(t)` khỏi H. Các tầng biến mất theo thứ tự từ nóng tới nguội, đúng như bản gốc.
5. **Vỡ**: trừ thêm `brk(t)·gaps(v)` với `gaps` hình chữ V (`(1-|sin|)^p`), không dùng cos. Khe chữ V làm các mảnh kết thúc bằng mũi
   nhọn; cos cho đầu tròn như xúc xích. Nhân thêm nhiễu để mỗi mảnh vỡ một kiểu.
6. **Quầng sáng bậc thang** (`stepped_glow`): 2-3 vành phẳng trong mờ ở khoảng cách cố định quanh hình, tối dần ra ngoài. Không blur.
7. **Lớp phụ phẳng**: bóng mờ (after-image) là một màu phẳng trong mờ, tự xói từ mép bằng chính trường của nó; vết nứt là nét mảnh,
   mờ đi theo bậc (0,85 → 0,5 → 0,25 → 0).

## 4. Các luật

- **Một trường, nhiều tầng**: mọi tầng màu của một vật lấy từ cùng một trường. Không vẽ tầng nào bằng hình riêng: tầng riêng sẽ chồng,
  hở hoặc lệch, mất cảm giác liền mạch.
- **Không gradient trong thân**: màu phẳng, ranh giới cứng (mịn nhờ siêu mẫu). Quầng sáng cũng theo bậc.
- **Thứ tự tầng = thứ tự nhiệt**: tầng nóng nhất nhỏ nhất và nằm trong cùng. Nó biến mất trước.
- **Răng cưa nằm ở ranh giới tầng, không ở mép ngoài**: mép ngoài hình bao gần như trơn, các lưỡi liếm nằm bên trong thân.
- **Mọi thứ có tuổi**: phần nào sinh trước thì nguội và vỡ trước, nên đuôi tan trước đầu một cách tự nhiên.
- **Nhịp không đều**: tần số và pha của kết cấu luôn có nhiễu; khe vỡ có nhiễu (DESIGN.md §10).
- **Đo trước, chỉnh sau**: lấy nhịp quét, màu và vòng đời từng tầng (số điểm ảnh theo frame) từ bản gốc bằng `_tools/study_ref.py`
  và đếm mã màu (RECIPE-swirl.md §1), rồi mới chỉnh tham số.

## 5. Bài học vòng 7 (user, 2026-11-07): KHÔNG dùng kết cấu tuần hoàn cho hình

Vòng 6 dùng sawtooth nghiêng `saw(v·k + …)` để sinh răng cưa / lông vũ: đúng cách diễn đạt (tầng phẳng, liền mạch) nhưng **sai hình**.
Các răng cùng một khuôn lặp đều thành một dải, user đánh giá đây là điểm xấu nhất. Tách riêng từng lớp màu của GIF gốc ở độ phân giải đầy
đủ cho thấy bản gốc là **vài hình lớn khác nhau**:
- lửa: ranh giới vàng/hồng và hồng/đỏ là những đường cong trơn, chỉ có 4-6 lưỡi lửa, mỗi cái một cỡ;
- băng: **hai hình đặt cạnh nhau** (lưỡi trắng phía ngoài, ngọn lửa xanh phía trong) với đường nối tối mảnh, bên trong có 3-6 mảng cyan
  to hình lông vũ và vài vệt xanh đậm, cũng mỗi cái một cỡ.

Luật thay thế:
- Ranh giới tầng = đường cong trơn trong toạ độ nét (`C = ngưỡng(v, tuổi, nguội)` với nhiễu chậm, biên độ nhỏ), không có tuần hoàn.
- Chi tiết (lưỡi lửa, lông vũ, vệt, lỗ, khe vỡ) = **danh sách đặt tay**, mỗi phần tử có vị trí, độ dài, bề rộng, độ nghiêng, độ cong
  riêng, vẽ bằng `tongue_poly` (lưỡi nhọn) hoặc `lens_poly` (lông vũ) trong toạ độ nét, nên luôn bám theo đường cong của vệt chém.
- Khe vỡ cũng đặt tay (vị trí, bề rộng), để các mảnh có 3-4 cỡ khác nhau.
- Kết cấu tuần hoàn chỉ dùng cho thứ thật sự đều (vân nước nhỏ, hạt mịn), không bao giờ cho hình chính.

## 6. Khi nào không dùng

- Hình có cấu trúc rời rõ ràng (hạt, mảnh đá, tia lửa bay): vẽ từng phần tử (`organic`, `fxcore`).
- Hình cần chiều sâu 3D (vòng nửa trước / nửa sau): vẫn dùng được trường, nhưng tách lớp `front` / `back` theo nửa.
- Khói toon có mặt sáng tối theo hướng đèn: `organic.shade` / `cloud` hợp hơn.
