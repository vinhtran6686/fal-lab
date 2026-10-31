# Brief cho fal-lab: master + 1 pose thử, dựng từ report phân tích motion

## Mục đích và cách đọc tài liệu này

Tài liệu này viết cho người vận hành `fal-lab` (bạn, dùng skill
`fal-image`/`video-sprite` của repo đó) — không phải tài liệu nội bộ của
Motion Lab. Mục tiêu: thử xem `fal-lab` có sinh được 1 nhân vật + 1 dáng
đứng khớp với độ phức tạp chuyển động mô tả dưới đây không. Đây là **phép
thử cơ chế**, không phải cam kết sản xuất — nếu kết quả không ổn, không sao,
mục đích là biết `fal-lab` làm được tới đâu.

## Cơ chế thật của fal-lab (đọc từ `format.md`, không đoán)

`fal-lab` **không** sinh "part sheet" (nhiều mảnh rời theo từng khớp) như
`project-overview.md` §6 từng kỳ vọng — đó là điểm chính tài liệu đó tự ghi
là "chưa kiểm chứng". Thực tế:
1. `generate2dsprite` (skill `fal-image`) vẽ **1 ảnh still** — master của
   nhân vật, 1 tư thế tĩnh.
2. `video-sprite` hoạt ảnh hoá still đó bằng **image-to-video**, xuất ra
   frame đã bake sẵn (đúng cách `holy_commander` đã có animation trong game
   hiện tại, theo `docs/project-overview.md` §8).

Nên brief này có 2 phần: (A) prompt cho still master, (B) mô tả chuyển động
cho bước image-to-video — không có "layout guide cắt mảnh" nào cả.

## Nguồn số liệu

Report phân tích motion, do chính Motion Lab tính (không phải mình nhìn
ảnh đoán), từ animation `idle` của 1 hero KR4 thật có rig đầy đủ (mượn làm
**tham chiếu cấu trúc**, không phải để sao chép). Tái tạo report:
```
cd E:\work\Motion-lab
cargo run -p motion-lab-cli -- report dianyun_idle
```

**Cảnh báo bắt buộc theo đúng rule của `fal-lab`** (`format.md`: *"never
copy their designs, never name the game they come from"*): nhân vật nguồn
**không được sao chép thiết kế hay nêu tên** trong prompt gửi cho model.
Chỉ dùng **cấu trúc chuyển động** (bao nhiêu khối, tỷ lệ, nhịp) làm tham
khảo, thiết kế `{design}` phải là nguyên bản.

## Cấu trúc rig rút ra từ report

32 frame, ~1.07s (khớp chuẩn 30fps của dự án), tối đa 28 mảnh vẽ cùng lúc.
Nhóm theo tiền tố tên mảnh:

| Nhóm | Số mảnh | Hành vi |
|---|---|---|
| Đầu (`Head_1`) | 1 | mặt trong toàn bộ 32 frame, gần như tĩnh |
| Thân (`cuerpo_1`..`6`) | 6 | mặt trong toàn bộ 32 frame — 64 sample mỗi mảnh (nội suy mịn), tịnh tiến nhẹ theo chiều dọc như đang thở |
| Tay + bàn tay (`arm`, `hand`) | 2 | mặt trong toàn bộ 32 frame, hầu như cố định |
| Đuôi (`cola_1`..`7`) | 7 | mỗi biến thể chỉ "sống" 2-6 frame rồi đổi sang biến thể kế — tức đuôi KHÔNG biến dạng liên tục mà **đổi qua lại giữa ~7 tư thế rời rạc** (kiểu lật trang) |
| Bờm/tóc (`cola_pelo_1`..`7`) | 7 | cùng kiểu đổi tư thế rời rạc như đuôi |
| Cánh/khăn (`Tegobi_1`..`16`) | 16 | cùng kiểu đổi tư thế rời rạc, đổi nhanh hơn (2-4 frame/biến thể) — có vẻ là 1 chi tiết bay phấp phới (cánh hoặc khăn/áo choàng) |
| Hiệu ứng nền (`stationary_clouds`) | 1 | mặt trong toàn bộ, co giãn 0.77-1.35x — mây/hào quang dưới chân |

**Ý nghĩa cho sinh ảnh:** thân/đầu/tay là 1 khối rig biến dạng mượt (đúng
kiểu `video-sprite` làm tốt — hoạt ảnh liên tục từ 1 still). Đuôi/bờm/cánh
là chi tiết **phấp phới, nhiều tư thế rời rạc** — nên mô tả trong prompt là
chi tiết "đang bay/đang đung đưa" để image-to-video tự nội suy, không cần
(và không thể) chỉ định từng tư thế.

**Tỷ lệ/bố cục** (đơn vị KR4 gốc, không phải pixel xuất KR1 — chưa quy đổi):
toàn thân kể cả đuôi/bờm/cánh trải rộng x:[-46, 56] (~102 đơn vị), y:[-117,
-46] (~71 đơn vị) — thân chính (không tính phần đuôi/bờm/cánh) hẹp hơn
nhiều: x:[-27, 26], y:[-105, -50]. Tức các chi tiết đuôi/bờm/cánh trải ra
**rộng hơn thân chính khá nhiều** về chiều ngang.

## (A) Prompt cho still master

Dùng nguyên khối `{STYLE}` của `format.md` §1, ghép với:

- `{H}`: chưa chốt tier — nếu xếp dạng hero, mặc định tier M = 60px
  (`format.md` §7, giống `holy_commander`). Bạn chỉnh nếu muốn tier khác.
- `{design}` (gợi ý dựng từ cấu trúc trên, **nguyên bản, không sao chép
  nhân vật nguồn**): một hero cưỡi/gắn liền với sinh vật kiểu rồng nhỏ —
  thân rồng cuộn nhiều đốt, bờm/vây dài trải phía sau, một cánh hoặc dải
  vải lớn bay phấp phới, 1 tay cầm vũ khí/vật phẩm. Tỷ lệ: phần đuôi/bờm/
  cánh nên vẽ trải rộng hơn thân khá nhiều (đúng theo bbox trên). Màu sắc,
  vũ khí, chi tiết cụ thể: bạn tự quyết theo gu riêng.
- Hướng vẽ: side (nghiêng), theo đúng hướng dữ liệu rig gốc được lift.

## (B) Mô tả chuyển động cho bước image-to-video (`video-sprite`)

- Vòng lặp ngắn ~1 giây (32 frame ở 30fps), dạng "idle": thân trên nhấp nhô
  nhẹ như đang thở, gần như đứng yên tại chỗ (không dịch chuyển lớn).
  Tay/đầu gần như tĩnh.
- Đuôi, bờm/vây, cánh/khăn: đung đưa/phấp phới liên tục, biên độ vừa phải,
  không đồng pha với nhau (đuôi và cánh lệch nhịp) — đúng như dữ liệu gốc
  cho thấy mỗi chi tiết đổi tư thế ở mốc frame khác nhau.
- Hiệu ứng mây/hào quang dưới chân: co giãn nhẹ, không dịch chuyển.

## Việc cần làm tiếp (không phải việc của Motion Lab)

1. Bạn (hoặc mình nếu bạn muốn) chạy `generate2dsprite` với prompt (A) —
   xem master ra có đúng cấu trúc/tỷ lệ mô tả không.
2. Nếu master ổn, chạy `video-sprite` với mô tả (B) — xem animation sinh ra
   có "giống" về *cấu trúc chuyển động* (không phải giống hệt pixel) với
   report gốc không: đuôi/bờm/cánh có phấp phới tách biệt khỏi thân không,
   thân có nhịp thở nhẹ không.
3. Motion Lab không tự gọi bước này — đúng hard rule "không gọi API sinh
   ảnh". Bạn chạy, rồi báo lại kết quả để tính tiếp.

## Câu hỏi còn mở

- Tier size (M hay tier khác) cho nhân vật thử này?
- Có muốn mình (Claude) trực tiếp gọi skill `fal-image` để thử luôn (tốn
  phí thật, sẽ xem pricing trong `fal-lab` trước), hay bạn tự chạy bên
  `fal-lab` theo prompt (A)/(B) ở trên?
