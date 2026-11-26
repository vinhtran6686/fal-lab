# Quy trình lưới nhiều nhân vật trong một clip (tóm tắt)

1. **Vẽ lưới:** `python scripts/gen_image.py --prompt-file <prompt> --size 2560x1440 --png --name lineup --versioned --out <thư mục>` (nền #FF00FF, 5 cột × 2 hàng, ~$0,02). Prompt lưới: mỗi con một bảng màu hex, vũ khí cầm thấp, `prompt_lint.py` không có ERROR.
2. **Đặt lại ô:** `python scripts/lineup/lineup_regrid.py <lưới>.png --out <lưới_regrid>.png` (thu nhỏ 0,68, chân ở 70% ô; miễn phí). Bước này tạo khoảng trống để các con không dính nhau.
3. **Làm clip cho từng động tác** (mỗi động tác một clip, hỏi "yes" trước vì tốn tiền): `python scripts/fal_video.py video --model h3-max-turbo --prompt-file <prompt> --reference <lưới_regrid>.png --duration 4 --resolution 720p --out-dir <thư mục>` (768P 4 giây = $0,12). Prompt: tên vũ khí gắn từng con, con tay không đứng riêng, đứng yên tại chỗ (chết: "ngã tại chỗ, không văng"), giữ tư thế cuối, "no tail".
4. **Tách khung:** `python scripts/lineup/lineup_split.py <clip.mp4> --out <thư mục> --pad 64 --names a,b,c,...` (13 khung mỗi con, RGBA).
5. **Xem và chọn khung:** mở ảnh kiểm 6-8 khung mỗi con, bỏ khung có vũ khí sai hoặc dính hàng xóm (thường là khung giơ lên giữa clip) và khung cuối của clip tấn công (quay về dáng đứng).
6. **Dùng khung:** mỗi con một thư mục `frames/` + `sheet.png` + `preview.gif`. Con nào giữ thì nhập vào asset thật (`scripts/ingest_image.py`, `brief.md`, `scripts/video_to_sheet.py`).

Giá thật đã đo: ảnh lưới ~$0,019; clip 768P 4 giây $0,12; 1080P 5 giây $0,30. Một lưới 10 con với 2-3 động tác ≈ $0,02 + $0,12 × số động tác, tức khoảng $0,012 mỗi con mỗi động tác.

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

# Thông số lưới 10 con đã chạy tốt (h3-max-turbo, thử ngày 2026-11-26)

- **Ảnh lưới:** gpt-image-2 quality low, 2560×1440, nền #FF00FF, 5 cột × 2 hàng, mỗi con có bảng màu hex riêng (~$0,019). Model vẽ mỗi con to gấp ~2 lần số xin trong prompt, nên đưa qua `lineup_regrid.py --scale 0.68 --feet 0.70` (mỗi con ~35% cao, ~43% rộng ô, chân ở 70% ô) trước khi làm video.
- **Clip:** `minimax/h3-max-turbo/image-to-video`, `--resolution 720p` (= 768P), `--duration 4`, không có khung cuối cho đòn đánh và chết. Chi phí thật 4 giây 768P = $0,12 (1080P 5 giây = $0,30). Clip ra 1344×768, ~107 khung ở 24 fps.
- **Tách:** `lineup_split.py --pad 64` (ô 268×384 + pad), 13 khung mỗi con.
- **Prompt chuyển động:** mỗi vũ khí gắn đúng tên con, con tay không đứng riêng, "no tail". Chết: tại chỗ ("never slides, is thrown or flies back"), ngả ra sau, giữ tư thế nằm. Đòn tấn công: một đòn chém dọc từ trên xuống, giữ tư thế cuối.
- **Kết quả với lưới đã đặt lại ô:** clip chết cho 10 bộ khung không dính nhau, không lẫn vũ khí. Với lưới chưa đặt lại (ô khít), clip tấn công còn dính và đổi vũ khí ở khung giữa. Clip đi bộ trôi khỏi ô và không dùng được.
