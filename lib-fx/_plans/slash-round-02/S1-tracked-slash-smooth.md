# S1. Vệt chém bám vũ khí phải mượt như bản đã duyệt

## Hiện trạng (đo ngày 2026-11-13, lệnh ở mục "Dựng mốc")
Quỹ đạo đã đúng (mép ngoài trùng đường mũi đao). Bốn lỗi còn lại, so với `out/heroes/azure_blade/frames/skill_crescent_side` (bản đã duyệt):

| # | Lỗi | Nguyên nhân trong `lib-fx/_core/formulas/draw/fxkit/layers/slash.py` |
|---|---|---|
| 1 | Khung đầu là mảng trắng lớn che vai và đầu nhân vật | `fh = 0.45 + 0.55 * out_quint(g)`: sinh ra đã dài 45 % quãng quét; `ph.first` tô quá sáng cả mảng |
| 2 | Ở 15 fps vệt giữ gần nguyên cỡ 4-5 khung rồi tắt phụt (`fxcheck`: "cut: frame 6 still holds 59 %") | `on_twos` (trong `layers/flames.py`) lượng tử hoá `decay` theo 2 khung: ở 15 fps `release` 0,3 s chỉ có 4,5 khung nên `d` chỉ nhận 0 → 0,44 → 0,89; thêm vào đó `p` của sợi nhỏ (0,8) nên mỏng chậm |
| 3 | Đuôi vệt treo ở chỗ mũi đao pose A khi đao đã nằm dưới đất | `rut` (độ rút đuôi) chỉ 0,2-0,75 và chỉ tác dụng khi `d` lớn |
| 4 | Mất cảm giác lưỡi đao quét: mảng phẳng đục; không có mũi đậm / chuôi nhạt; không có mép trắng dọc lưỡi ở pose B | chế độ `track` dùng lại nguyên bộ sợi của chế độ cung: mọi sợi cùng độ đục, tông `hot` chạy dọc **cung ngoài** chứ không dọc **lưỡi** |

## File được sửa
- `lib-fx/_core/formulas/draw/fxkit/layers/slash.py` (chỉ nhánh `track`, trừ khi ghi khác)
- `lib-fx/_core/formulas/draw/fxkit/layers/flames.py` (hàm `on_twos`, một dòng)
- `lib-fx/melee/slash/slash.py` (thêm một hiệu ứng `swing`)
- `lib-fx/_core/formulas/draw/FXKIT.md` (mục 6), `docs/pipeline/pose-pair-fx-method.md` (bước 7), `lib-fx/GUIDE.md` (dòng `melee/slash`)

## Dựng mốc (làm trước khi sửa, giữ lại để so)
Số liệu `azure_blade` (px ô @2x): mũi A (107.3, 191.1), chuôi A (118.5, 144.1), mũi B (238.6, 241.0), chuôi B (202.9, 241.5); thân: `out/heroes/azure_blade/frames/skill_crescent_puppet_side/frames/@2x/*.png`
(44 khung, 15 fps, khung trúng đòn = 23); bản đã duyệt: `out/heroes/azure_blade/frames/skill_crescent_side/frames/@2x/*.png`; đường mũi đao: `.../skill_crescent_side/track.json` → `samples[].tip_px2x`.
```
python lib-fx/build.py melee/slash/crescent --from 107.3,191.1 --to 238.6,241.0 --pal frost --fps 15 --split \
    --track "root_a=118.5,144.1;root_b=202.9,241.5;up=35;turn=cw;ease=1.3" --out <thư mục tạm>/before
```
Viết một script tạm (không đưa vào repo) ghép `back/` dưới thân và `front/` trên thân, dán khung fx tại `meta.json → origin`, đặt **`hit_frame` của fx trùng khung 23 của thân**
(hiện `hit_frame` = 1 nên bản "trước" đặt khung fx 1 vào khung thân 22 để giống cách bản đã duyệt mọc sớm một khung); xuất ảnh lưới khung thân 21-29, mỗi ô: trái = đã duyệt, phải = mới. Giữ ảnh "trước".
Cũng tách **fx của bản đã duyệt** để đo: `alpha_fx = alpha(skill_crescent_side khung i) khác alpha/màu của skill_crescent_puppet_side khung i` (điểm ảnh khác nhau quá 12 mức ở bất kỳ kênh nào).

## Cách làm

### Bước 1. `on_twos` không được làm giật ở fps thấp (`layers/flames.py`)
Thêm vào đầu hàm: `if c.fps < 20: return ph.decay` (15 fps đã là "on twos" của 30 fps; lượng tử thêm lần nữa làm hình đứng yên rồi tắt).
**Kiểm**: `python lib-fx/build.py melee/slash --check` ở 30 fps cho khung **giống hệt trước** (so hash `frames/*.png` của `crescent` trước và sau).

### Bước 2. Hiệu ứng `swing` cho vệt bám vũ khí (`lib-fx/melee/slash/slash.py`)
Thêm `EFFECTS["swing"]` = biến thể của `_slash`: `title="Chém theo vũ khí"`, `tags=["tracked"]`, mô tả ghi rõ "dùng với `--track`". Lớp `slash` của nó có
`life=Life(-0.0667, 0.0667, 0.0, 0.27)`: **sinh trước khung trúng đòn một khung ở 15 fps** (hai khung ở 30 fps), nên `meta.json → hit_frame` = 2 ở 15 fps và khung fx đầu rơi đúng vào khung cuối của pose A.
Lớp `scraps` và `streaks` giữ `start` ≥ 0 (chỉ có sau khi đao tới đích). Không đổi `crescent` và các hiệu ứng khác.

### Bước 3. Nhịp của đầu vệt trong chế độ `track` (`slash.py`)
Gọi `t = ph.sec + c.layer.life.start` (giây tính từ khung trúng đòn; âm = trước đòn) và `pre = -c.layer.life.start` (> 0 với `swing`).
- `t < 0` (đao còn ở pose A): `fh = 0.10 + 0.06 * (1 + t / pre)` → vệt chỉ phủ 10-16 % đầu quãng quét: **một lát mỏng nằm trên lưỡi đao pose A**.
- `t >= 0`: `fh = 1.0` ngay (đao đã ở pose B; vệt đầy trên khung trúng đòn, đúng luật "cú vung dài một khung").
- Khi `pre <= 0` (ai đó dùng `--track` với hiệu ứng khác): giữ công thức hiện tại.
Bỏ tô quá sáng cả mảng trong chế độ `track`: không dùng nhánh `ph.first` (xem bước 6 cho phần trắng).

### Bước 4. Nhịp tan (chế độ `track`)
Yêu cầu theo số đo của bản gốc (`rules/vfx/slash/README.md`: diện tích ×0,3-0,5 mỗi hình sau đỉnh):
- số mũ mỏng của sợi: `p` = `(1.6 + 1.6 * phi) * jitter * lk` (hiện `0.8 + 1.5 * phi`);
- hệ số chung: thay `min(1.0, (0.93 - d) / 0.3)` bằng `(1 - d) ** 0.6` để không có đoạn giữ nguyên rồi rơi;
- **đuôi rút sớm và mạnh**: `fa = lo + st["start"] * L + L * (0.55 + 0.35 * phi_rut) * out_cubic(d * 1.6)` với `phi_rut` = `st["rut"]` chuẩn hoá về 0..1
  (ở `d = 0.3` đuôi đã lùi ≥ 45 % chiều dài; ở `d = 0.6` chỉ còn phần gần lưỡi pose B);
- đầu vệt (`fb`) không lùi trong chế độ `track` (mép dẫn luôn nằm trên lưỡi đao pose B cho tới khi sợi biến mất).

### Bước 5. Mũi đậm, chuôi nhạt (chế độ `track`)
Toạ độ ngang nét `c` trong chế độ `track`: 1 = mũi đao, 0 = phía chuôi (kiểm lại bằng cách tô thử một sợi rồi xem ảnh). Chia bó thành 3 sợi theo tỉ lệ bề rộng mũi → chuôi `[0.42, 0.33, 0.25]` (có jitter ±10 %):
- sợi mũi: tông `main`, đục hoàn toàn, có mép `hot` ở cung ngoài như hiện tại; tàn **sau cùng**;
- sợi giữa: tông `main`, tô với độ đục 0,7 (thêm tông tên `mid` cùng màu `c.pal.tone("main")`, truyền `opacity={"mid": 0.7}` cho `ink.paint`);
- sợi chuôi: tông tên `faint`, màu `c.pal.tone("main")`, độ đục 0,4; **ngắn hơn** (bắt đầu từ `lo + 0.25 * L`) và tàn **đầu tiên** (`phi` = 1).
Thứ tự tô: `faint`, `mid`, `main`, `deep`, `hot`. Tông `deep` chỉ nằm trong sợi mũi.
Quầng sáng: `ink.paint(..., glow=1.0)` như cũ (quầng lấy từ hợp các tông; chấp nhận).

### Bước 6. Mép sáng dọc lưỡi đao ở pose B (chế độ `track`)
Thêm một dải tông `edge` phủ **toàn bộ bề ngang** của vệt (từ mép trong tới mũi, dọc theo chính đường lưỡi) trong đoạn `f` từ `fh - 0.045` tới `fh`:
`ink.add("edge", strand(fh - 0.045, fh, lambda f: 0.0, lambda f: 1.0))` (dùng đúng hàm `strand` và toạ độ nét có sẵn; nếu `c` chạy ngoài 0..1 thì dùng biên của bó).
- khung trúng đòn và khung kế tiếp (`t` từ 0 tới 0,07 s): tô `edge` bằng `c.pal.tone("white")`;
- sau đó (`d` tới 0,35): tô bằng `c.pal.tone("hot")`, bề dày giảm tuyến tính về 0; `d > 0.35`: không vẽ.
Ở khung trước đòn (`t < 0`): cũng có `edge` trắng ở đầu lát mỏng (nằm trên lưỡi pose A).
`edge` tô trên cùng (sau `hot`).

### Bước 7. Tài liệu
- `FXKIT.md` mục 6: lệnh mẫu cho nhân vật dùng `melee/slash/swing` + `--track`; ghi "đặt `hit_frame` của fx trùng khung trúng đòn của thân; khung fx đầu rơi vào khung cuối của pose A".
- `docs/pipeline/pose-pair-fx-method.md` bước 7: thêm đoạn "cách thứ hai (fxkit)" với lệnh trên; ghi rõ bản `build_crescent.py` vẫn là bản đã duyệt của `azure_blade`.
- `lib-fx/GUIDE.md`: thêm `Chém theo vũ khí (draft)` vào dòng `melee/slash`.

## Tiêu chí nghiệm thu (đo bằng script tạm ở mục "Dựng mốc", ghi số vào "Kết quả")
Dựng "sau": cùng lệnh nhưng `melee/slash/swing`. Gọi `h` = khung trúng đòn của thân (23); khung fx `hit_frame` đặt vào `h`.
- [ ] **Khung `h - 1`**: mọi điểm ảnh của fx cách đoạn thẳng chuôi A → mũi A không quá 14 px @2x; diện tích fx ≤ 1,6 lần diện tích fx của bản đã duyệt ở cùng khung; mặt nhân vật không bị che (xem ảnh).
- [ ] **Khung `h`**: mép ngoài của vệt lệch đường `tip_px2x` ≤ 4 px ở mọi mẫu; dải `edge` trắng nằm trong 5 px quanh đoạn chuôi B → mũi B và phủ ≥ 70 % chiều dài lưỡi.
- [ ] **Mũi đậm, chuôi nhạt** ở khung `h`: alpha trung bình của fx trong 30 % bề ngang phía mũi ≥ 0,9; trong 30 % phía chuôi ≤ 0,55.
- [ ] **Nhịp tan**: với `A(i)` = tổng alpha fx ở khung `i`: `A(h+1)/A(h)` ≤ 0,75; `A(h+2)/A(h)` ≤ 0,45; `A(h+3)/A(h)` ≤ 0,2; khung cuối còn thấy ≤ 5 %; khung sau đó trống.
      `fxcheck` của bản xuất 15 fps: không `pop`, không `cut`, không FAIL.
- [ ] **Đuôi**: ở khung `h + 2` không còn điểm fx nào trong bán kính 30 px quanh mũi A (107.3, 191.1).
- [ ] **Không hồi quy**: `melee/slash/crescent`, `heavy`, `thrust`, `axe`, `axe_heavy` ở 30 fps cho khung giống hệt trước (so hash); `fxkit_test.py` qua.
- [ ] Ảnh lưới khung 21-29 "trước" và "sau" cạnh bản đã duyệt, và một GIF 15 fps ba cột (đã duyệt | trước | sau), đặt ở thư mục tạm và ghi đường dẫn; **không** ghi vào `out/`.
- [ ] Thử thêm một cú vung khác để chắc không khớp riêng cho một nhân vật: `--from 60,200 --to 250,90 --track "root_a=90,170;root_b=190,150;up=20;turn=ccw;ease=1.2"` (hất lên): khung trước đòn vẫn là lát mỏng trên lưỡi đầu, khung đòn có mép trắng trên lưỡi cuối.

## Kết quả (người làm điền: số đo từng tiêu chí, đường dẫn ảnh và GIF, chỗ chưa đạt)
