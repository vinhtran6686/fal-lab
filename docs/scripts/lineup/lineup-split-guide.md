Quy trình đầy đủ và bảng thông số kỹ thuật: `lineup-workflow.md`. File này mô tả hai script.

# Tách clip lưới nhiều nhân vật: `scripts/lineup/lineup_split.py`

Dùng khi một ảnh lưới (ví dụ 5 cột × 2 hàng, nền magenta) đã được đưa vào model video (`scripts/fal_video.py`, h3-max-turbo) để cả lưới cùng đi bộ hoặc tấn công trong MỘT clip. Script tách từng ô thành một bộ khung riêng. Không tốn tiền, cần ffmpeg, numpy, scipy, Pillow.

```bash
python scripts/lineup/lineup_split.py <clip.mp4> --out <thư_mục> --names tên1,tên2,... [--cols 5 --rows 2] [--frames 13 | --step N] [--pad 96] [--gap 14] [--fps 12]
```

Mỗi nhân vật nhận `<out>/<tên>/frames/fNN.png` (RGBA đã xóa nền magenta, khử viền hồng), `sheet.png` (một dải ngang) và `preview.gif`.

## Cách hoạt động
- Ô cắt cố định: rộng clip / số cột, cao clip / số hàng (clip 1920×1080 với lưới 5×2 cho ô 384×540). Mỗi ô được nới thêm `--pad` px mỗi phía để vũ khí vung qua đường ô vẫn nguyên vẹn; phần ngoài clip coi là nền.
- Xóa nền: điểm "magenta" = min(R,B) − G; viền mềm, khử hồng ở rìa.
- Giữ thân chính: mảnh liên thông lớn nhất cắt qua cột giữa ô, cộng các mảnh cách nó ≤ `--gap` px. Mảnh rời của ô bên cạnh bị bỏ.
- Một phép dịch cố định cho mỗi nhân vật: chân (đáy hình bóng khung đầu) và tâm ngang của hình bóng khung đầu đưa về (giữa ô, 0,88 chiều cao ô). Không căn lại từng khung nên chuyển động được giữ nguyên.
- Khung lấy đều trên cả clip (`--frames`, mặc định 13) hoặc mỗi N khung (`--step`).

## Giới hạn đã gặp (lưới 10 quái, clip tấn công h3-max-turbo)
- Khi nhân vật hoặc vũ khí chạm nhân vật bên cạnh trong clip, mảnh của hàng xóm dính vào bộ khung (rõ nhất quanh khung 5-8 trên 13). Script chỉ bỏ được mảnh rời, không tách được phần đã dính liền; khung đó cần bỏ tay hoặc thử lại clip.
- Mô hình vẽ thêm đuôi nhọn sau lưng ở một số con khi cúi xuống; đó là lỗi của clip, không phải của script.
- Cắt kích thước ô cố định không áp dụng cho clip mà các con trôi nhiều (clip đi bộ): xem thông báo cảnh báo "silhouette touches the window edge".

# Đặt lại ô trước khi làm video: `scripts/lineup/lineup_regrid.py`

Model ảnh bỏ qua kích thước và vị trí viết trong prompt (xin 24% chiều cao ô, vẽ ra ~50%), nên khoảng trống giữa các nhân vật được tạo bằng code, miễn phí:

```bash
python scripts/lineup/lineup_regrid.py <lineup.png> --out <mới.png> [--cols 5 --rows 2] [--scale 0.68] [--feet 0.70] [--min-area 400]
```

Xóa nền magenta, gom các mảnh liên thông theo ô chứa trọng tâm của chúng (một nhân vật cùng vũ khí), thu nhỏ `--scale`, đặt vào tâm ngang của ô, điểm thấp nhất (chân; vũ khí treo thấp hơn thì tính theo vũ khí) ở `--feet` × chiều cao ô, trên nền magenta mới cùng kích thước. In kích thước từng con theo % ô. Với lưới 10 quái: `--scale 0.68` cho mỗi con ~35% cao và ~43% rộng ô, chân ở 70%.
