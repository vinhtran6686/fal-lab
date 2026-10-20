# Hiệu ứng (fx) vẽ bằng Python: công thức đầy đủ (0 USD)

Viết 2026-10-20 từ việc làm 10 phiên bản fx levelup cho `holy_commander`. Mục đích: lần sau làm fx cho bất kỳ hero,
trạng thái hay skill nào, đọc file này là làm được mà **không phải quay thêm clip trả phí**.

> Không sửa `SKILL.md` (user tự sửa). File này là ghi chú trong `docs/`. Mã nguồn chạy được: `out/heroes/holy_commander/fx/levelup_variants.py`.

## 1. Tóm tắt một đoạn

Quay **một** clip thân sạch (không mời hiệu ứng), tách **toàn bộ** frame, rồi dùng Python (numpy + Pillow) **vẽ ánh sáng
bằng màu và độ trong suốt** chồng lên từng frame theo thứ tự lớp: lớp sau thân, thân, lớp trước thân. Đổi màu, độ đậm, nhịp,
kích thước chỉ là đổi tham số và chạy lại (~50 giây mỗi phiên bản). Không gọi model, không tốn phí. Nhờ vậy ta làm được 10
phiên bản khác nhau từ đúng một clip 0.045 USD.

## 2. Vì sao làm vậy (so với gen video + cắt frame)

| | Python vẽ fx lên clip thân sạch | Gen video có fx + cắt frame |
|---|---|---|
| Chi phí fx | **0 USD**, chạy lại không giới hạn | ~0.045 USD mỗi take (3 s, h3-max-turbo), mỗi lần đổi ý là một take mới |
| Đổi nhịp, màu, kích thước | Sửa tham số | Quay lại clip |
| Rủi ro | Không (thân không bị fx làm méo) | Model tự thêm vòng lớn, zoom (charge_v4: vòng lửa; 3 skill cũ: zoom 2.4-2.9x) |
| Thân clip | Luôn sạch, gate `area`/`identity` đọc đúng | fx trong clip làm gate đọc sai |
| Tái lập | Clip trong `raw/` + một script | Phụ thuộc lần quay |
| Độ chi tiết | Mềm, ánh sáng, hào quang, tia, vòng, hạt: **rất tốt** | Hình có hoạ tiết thật (xoáy có kết cấu, sét nhiều nhánh, lửa có hình, khói): tốt hơn |

**Quy tắc (user chốt):** Python trước. Chỉ khi fx cần hình dạng phức tạp hay phải bám vũ khí từng frame mà Python vẽ sẽ thô thì
mới gen video + cắt frame, và báo giá, chờ user ok trước mỗi take. Chi tiết trong `out/heroes/holy_commander/brief.md`, mục "FX policy".

## 3. Quy trình, từng bước

### Bước 0. Chuẩn bị
- Cần: `python` có `numpy`, `Pillow`; `ffmpeg` trên PATH; chạy **từ thư mục gốc repo** (script import `scripts/sprite_pack.py`, `key_out`).
- Cài nếu thiếu: `pip install -r requirements.txt` (và `numpy`).

### Bước 1. Có clip thân sạch
- Quay bằng `scripts/fal_video.py` (hoặc `sprite_set.py`) với prompt **không nhắc hiệu ứng** và có câu "locked tripod" (lấy từ
  `raw/skill_side_skill_charge_v2_t01.json`). Ví dụ levelup: `raw/levelup_side_extra_v2_t01.mp4` (3 s, 832x480, nền magenta).
- Ảnh đầu = master, ảnh cuối = pose đỉnh. Điều này giữ cỡ người ổn định (đã đo: cao 431 px frame đầu, 423 px frame cuối).

### Bước 2. Tách toàn bộ frame và key nền
- `ffmpeg -i clip.mp4 -vf fps=15 %03d.png` cho clip 3 s ra **46 frame** (script tự làm trong `load_frames`).
- Key nền magenta bằng `sprite_pack.key_out()` (cũng trong `load_frames`).
- **Không bỏ frame nào.** Lỗi đã gặp: bản A2 đầu chỉ ghép `[:45]` nên mất frame cuối. Số frame fx phải bằng số frame thân.

### Bước 3. Đo clip để biết đặt fx ở đâu (làm một lần cho mỗi clip)
Đo trên frame đã key (alpha > 128):
1. **Điểm chạm đất (feet):** hàng alpha dưới cùng; x = trung bình x của ~8 hàng dưới cùng. Levelup: `(370, 453)` trong khung 832x480.
2. **Chiều cao thân (BODY):** `bbox.bottom - bbox.top` ở frame nghỉ. Levelup: ~**425 px**.
3. **Vị trí nắm đấm ở đỉnh:** x trung bình của ~40 hàng trên cùng. Levelup: lệch ~**-0.08 BODY** so với chân, cao ~**0.93-0.95 BODY**.
4. **Nhịp động tác:** in `bbox.top` theo từng frame. Levelup (clip 46 frame): lấy đà (hạ người) frame 14-19, nắm đấm lên đỉnh frame 20-22,
   **đỉnh ở frame 22**, giữ pose đến hết. Dùng để đặt thời điểm các lớp.
5. Đưa vào hằng số đầu file: `FEET`, `BODY`, `BODY_AT`.

### Bước 4. Canvas
- Dùng canvas lớn hơn khung clip để fx rộng không bị cắt: `W, H = 700, 720`, chân đặt tại `FEET = (350, 630)`.
- Thân được dán vào canvas với offset `(FEET - BODY_AT)`.
- Nền xem thử `BG = (58, 74, 64)` (xanh đậm giống nền game). Đây chỉ là nền xem, xem mục 7 về xuất.

### Bước 5. Vẽ fx theo từng frame, thứ tự lớp
Với mỗi frame `i`:
1. Canvas = nền.
2. **Lớp sau thân** (quầng sáng dưới chân, sóng lan dưới đất, hào quang quanh người...): `fn(cv, i, body, sil, front=False)`.
3. Dán **thân** (alpha-over bình thường).
4. **Lớp trước thân** (viền sáng trên thân, chớp ở nắm đấm, cột sáng trong suốt, dải sáng...): `fn(..., front=True)`.

### Bước 6. Chế độ pha trộn
- **screen** cho mọi thứ phát sáng: `out = 1 - (1-nền) * (1 - màu*alpha)`. Sáng lên mà không làm tối nền, đúng cảm giác "ánh sáng". (`Canvas.screen`)
- **normal** (alpha-over) cho lớp bình thường, như dán thân. (`Canvas.normal`)
- Toàn bộ fx chỉ gồm **màu + độ trong suốt**, mép mềm (blur). Không viền nét đậm, không vector phẳng.

### Bước 7. Xuất xem thử
- Mỗi phiên bản ra: thư mục frame PNG đầy đủ (46 ảnh), `vNN.mp4` (15 fps, rộng 420 px, h264, crf 22), `vNN_peak.png` (frame 27).
- Đăng artifact: video `<video autoplay loop muted playsinline controls>`. Mỗi mp4 ~80 KB.

## 4. Bộ công cụ vẽ (hàm trong `levelup_variants.py`)

Mỗi hàm trả về một mảng alpha float 0..1 kích thước canvas (trừ `Canvas`). Dùng `cv.screen(MÀU, alpha, hệ_số)`.

| Hàm | Vẽ gì | Tham số chính |
|---|---|---|
| `ramp(i, a, b)` | 0 trước frame a, tăng tuyến tính tới 1 ở frame b | |
| `env(i, a, full, hold, end)` | đường bao thời gian: tăng a→full, giữ tới hold, giảm hold→end | levelup v03: `18, 24, 32, 41` |
| `paintL(fn, blur)` | vẽ hình bằng PIL lên ảnh xám rồi blur | `blur` làm mép mềm |
| `radial(cx, cy, rx, ry, p)` | quầng sáng tròn/elip mờ dần ra rìa | `p` càng lớn càng gọn ở giữa |
| `capsule(w, h, soft)` | cột viên nang trong suốt quanh thân | `soft` = blur mép |
| `ring(cx, cy, rx, ry, width, blur)` | vòng elip (sóng lan trên đất) | `ry ≈ 0.2 rx` cho góc nhìn trên xuống |
| `star(cx, cy, r)` | sao 4 cánh + quầng | |
| `motes(i, n, seed, ...)` | hạt sáng nổi lên, deterministic theo `seed` | `speed`, `size`, `x_half` |
| `sil_of(body)` | hình bóng (alpha) của thân trên canvas | |
| `aura(sil, grow, blur)` | **hào quang tròn bám hình người** | xem mục 5 |
| `rimlight(sil, k)` | viền sáng **bên trong** mép thân | |
| `ground(cv, e, k, wide)` | quầng sáng vàng dưới chân | `wide` × BODY là nửa bề rộng |
| `beam(cv, e, w, k)` | dải sáng cao trên đầu, mờ dần lên trên | |
| `flash_fist(cv, i, t, k, r)` | chớp trắng tại nắm đấm, tắt trong ±4 frame quanh `t` | `t=22` = frame đỉnh |

Màu: `CREAM (255,244,200)`, `GOLD (255,201,60)`, `WHITE (255,255,240)`, `AMBER (255,158,38)`.

## 5. Những chi tiết kỹ thuật dễ sai (đọc kỹ)

1. **Hào quang bám hình người phải tròn.** Bản đầu dùng `ImageFilter.MaxFilter` để nở hình: nó nở theo **hình vuông**, hào quang ra
   góc vuông xấu. Cách đúng (hiện tại): `GaussianBlur(sil, grow*0.75)`, nhân **×2.6** rồi cắt về 0..1 (kéo mép lên), rồi blur lần nữa.
   Mép ra tròn và mềm.
2. **Viền sáng trong thân** (`rimlight`) = `sil - blur(MinFilter(sil, 9), 5)`: phần mép của thân, không tràn ra ngoài.
3. **Đừng vẽ chi tiết nhỏ.** Lưỡi sáng nhỏ ở đáy cột (A2 bản đầu) làm rối và bị user loại. Dùng lớp **rộng, mềm, dễ thấy**.
4. **Không viền nét, không vector phẳng chồng lên thân** (bản A1 qua `fx_layers` bị chê thô).
5. **Cột hình hộp góc vuông trông như hộp kính**: cột phải có đỉnh tròn (`rounded_rectangle` với `radius = w/2`) và mép mềm.
6. **Gradient độ trong suốt dọc cột**: nhạt ở đỉnh (~0.15-0.2), đậm ở chân (~0.5-0.6). Thân nhìn xuyên qua.
7. **Vị trí chớp ở nắm đấm** lấy từ số đo (mục 3.3), không đoán. Đo xong mới thấy chớp rơi đúng nắm đấm.
8. **Cú đấm sát mép trên khung**, nên dải sáng trên đầu mờ dần chứ không dừng gắt; canvas có chỗ phía trên (chân tại y=630, đỉnh nắm đấm ~y=207).
9. **Số frame**: dùng đủ mọi frame của clip. Không `[:45]`.
10. **Thời gian chạy**: ~50 giây mỗi phiên bản (700x720 x 46 frame). Chạy nhiều phiên bản song song bằng `nohup ... &`, 3-4 tiến trình.
11. **Ghi chú tồn đọng trong mã** (không ảnh hưởng kết quả): `render()` có một lệnh `cv.normal(zeros, zeros)` vô tác dụng; `V05` có biểu thức
    `motes(...) * 0 + motes(...)` thừa. Có thể dọn khi đụng tới.

## 6. Cách thiết kế một phiên bản mới (checklist)

1. Chọn ý: hào quang bám người? cột? vòng? tia? sóng? (xem 10 phiên bản dưới).
2. Chọn thời điểm: `env(i, a, full, hold, end)` với `a` ≈ lúc bắt đầu động tác chính, `full` ≈ đỉnh động tác, `end` trước khi clip hết.
3. Phân lớp: cái gì **sau thân** (quầng chân, sóng đất, hào quang), cái gì **trước thân** (viền sáng, cột trong suốt, chớp).
4. Chọn màu theo hero: holy_commander dùng kem/vàng/trắng/hổ phách. Hero khác đổi 4 hằng màu, giữ cấu trúc.
5. Chạy một phiên bản, **mở frame đỉnh ở kích thước lớn**, kiểm: hào quang tròn? chớp đúng nắm đấm? thân không bị che? mép mềm?
6. Chạy cả clip, xem mp4, chỉnh `env` và alpha.
7. Chỉ khi đạt mới chạy hết, đăng artifact cho user duyệt.

Lệnh chạy:
```
python out/heroes/holy_commander/fx/levelup_variants.py out/heroes/holy_commander/raw/levelup_side_extra_v2_t01.mp4 <thư_mục_ra> v03
# bỏ tên variant để chạy cả 10; có thể truyền nhiều tên: v01 v05 v10
```

## 7. Chuyển sang asset game (việc còn mở: ghi rõ để khỏi quên)

Bản xem thử ghép lên nền xanh đậm bằng **screen**. Game cần lớp **trong suốt**:
- **Cần quyết khi export:** (a) xuất mỗi lớp thành PNG RGBA riêng (alpha = độ trong suốt, màu = màu lớp) rồi game ghép; hoặc
  (b) xuất bản ghép sẵn lên nền trong suốt. Screen trên nền sáng (cỏ sáng) có thể cháy trắng hơn so với bản xem; phải **xem lại trên nền sáng**
  trước khi chốt. Hero tham chiếu (malik) dùng frame PNG có alpha thật (thân + fx nửa trong suốt trong cùng frame), nên (b) khớp cách game đó.
- Canvas game 176x140 (352x280 @2x), thân 111@2x, pivot (0.5, 0.88). Hào quang v03 nở tới ~0.15 BODY quanh người; ngoài ra quầng chân rộng ~0.55 BODY mỗi bên.
  Kiểm tra có vừa canvas hay cần canvas fx riêng, như các fx của `fx_layers`.
- Chưa export, chưa cắt frame, chưa chạy gate `qc.json` cho levelup. Không cắt frame ở phiên này.

## 8. Vì sao 10 phiên bản, và kết quả đánh giá của user

| # | Tên | Ý tưởng | User đánh giá |
|---|---|---|---|
| v01 | Cột sáng + sóng lan | Cột viên nang, hào quang, 3 sóng lan dưới chân, dải sáng trên đầu | rất đẹp |
| v02 | Vệt sáng bay lên | Vệt sáng bay lên trong cột mờ | **không đẹp, bỏ** |
| **v03** | **Hào quang xung nhịp** | **3 đợt hào quang lan ra từ hình người, viền sáng trong thân, chớp ở nắm đấm** | **đẹp nhất, ĐÃ CHỌN cho levelup** |
| v04 | Tia thánh + vầng sáng | Tia quay quanh ngực, vầng sáng sau đầu, sao 4 cánh | **không đẹp, bỏ** |
| v05 | Sóng xung kích | 3 sóng rộng dưới chân, chớp, vài tia lửa | rất đẹp |
| v06 | Hai vòng xoắn sáng | Hai xoắn hạt sáng quấn thân | rất đẹp |
| v07 | Trụ sáng từ trời | Trụ rất rộng đổ xuống, bắn tung, hạt nổi lên | rất đẹp |
| v08 | Vòng sáng bay lên | 4 vòng mềm bay từ chân quá đầu | rất đẹp |
| v09 | Cột có dải chạy | Cột có dải sáng chạy lên, sóng đáy rộng | rất đẹp |
| v10 | Tổng hợp | Gộp mọi lớp | rất đẹp |

Mã của v02 và v04 vẫn nằm trong file (không xoá) nhưng không dùng. Các phiên bản đẹp còn lại là kho ý tưởng cho levelup, respawn,
skill sau này (ví dụ v08 vòng bay lên hợp respawn, v07 trụ sáng hợp buff/triệu hồi, v05 sóng xung kích hợp skill đập đất).

## 9. Bài học rút ra (cho lần sau)

1. Fx đẹp không cần model: **lớp mềm, rộng, màu + độ trong suốt**, ghép bằng screen.
2. Tự xem frame đỉnh ở kích thước lớn **trước khi** đưa user; lần đầu mình đã tự loại bản cột hộp kính và lưỡi giáo, và sửa hào quang vuông.
3. Hỏi user sau mỗi vòng; góp ý của user ("chi tiết nhỏ làm rối, dùng lớp rộng") đổi hẳn hướng và là lý do bộ 10 đẹp.
4. Bài học chi phí: clip thân (0.045 USD) + script = vô số phiên bản fx. Gen video có fx chỉ khi Python không đủ chi tiết.
5. Ghi toàn bộ số đo (feet, BODY, nắm đấm, nhịp) trước khi vẽ; đặt đúng chỗ ngay lần đầu.
