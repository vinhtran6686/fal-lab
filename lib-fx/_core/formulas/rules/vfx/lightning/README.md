# VFX loại "lightning" (sét)

Một tia sét đánh, vỡ ra rồi tắt, và một tia mới mọc ở đường khác. Không có chuyển động liên tục: **mỗi hình vẽ là một tia vẽ lại**.
Luật chung cho mọi loại hiệu ứng nằm ở [../../README.md](../../README.md) và các file 01-05; file này chỉ ghi phần riêng của sét.

## 0. Bản gốc đã đọc

| Bản gốc | Biến thể | Profile | Kết quả | Trạng thái |
|---|---|---|---|---|
| `ref/vfx/lightning-2/lightnings.mp4` (1920×640, 30 fps, 20 s; ba hiệu ứng lặp cạnh nhau) | `arc` (trái: cung sét xanh bò ngang), `strike` (giữa: sét vàng đánh thẳng xuống đất), `bolt` (phải: sét xanh lớn từ trên xuống đất) | [`lightning-2.json`](../../../vector/profiles/lightning-2.json) | [showcase/lightning-2](../../../../results/vector-showcase/lightning-2/) | **đạt** (2026-11-28): nguồn hình của bộ sét quanh nhân vật (§7) |
| `ref/vfx/lightning-3/reference.gif` (1286×723, 52 frame, 25 fps, mỗi frame một hình) | `spark` = **Prism Spark** ("Điện lăng kính"): tia điện ngoằn ngoèo, lõi trắng, **viền tách màu** (xanh ngọc trên-trái, hồng dưới-phải), quầng xanh rộng | [`lightning-3.json`](../../../vector/profiles/lightning-3.json) | [showcase/lightning-3](../../../../results/vector-showcase/lightning-3/) | **đạt** (2026-11-28) |
| `ref/vfx/lightning/dmitry-sarkisov-lqafinal.gif` (400×400, 127 frame) | `bolt` / `green`: nét mảnh xanh lá + quầng | `lightning.json`, `lightning-trace.json` | [lightning/bolt](../../../../results/vector-showcase/lightning/bolt/), [lightning-trace/green](../../../../results/vector-showcase/lightning-trace/green/) | lần dựng đầu, nét béo gấp ~3 (xem §6) |

Số đo của `lightning-2`: [`data/lifecycle_lightning-2.json`](../../data/lifecycle_lightning-2.json) (từng hình vẽ: diện tích, số mảnh, bề rộng nét,
diện tích từng lớp, số frame giữ; các cú đánh trong vòng lặp), bảng nhịp `recipe/exposure.json` và kiểm tra `recipe/rebuild_check_bright.json`, `recipe/rebuild_check_dark.json` trong thư mục showcase.

## 1. Dựng lại (công thức chạy được, 0 USD)

```
python lib-fx/_tools/vectorfx.py ingest    lightning-2      # mp4 -> 3 vùng cắt, một PNG cho mỗi HÌNH VẼ (bỏ frame giữ), nền = phân vị 20, exposure.json
python lib-fx/_tools/vectorfx.py check     lightning-2      # điểm ảnh sáng chưa lớp nào nhận
python lib-fx/_tools/vectorfx.py measure   lightning-2      # gradient mép, quầng chung + độ mạnh từng hình, quầng riêng của lớp chớp đất / lớp mực (~2 phút)
python lib-fx/_tools/vectorfx.py rebuild   lightning-2      # fit.mode = trace: viền thẳng từ mặt nạ qua Smooth & Simplify (~3 phút cho 56 hình)
python lib-fx/_tools/rebuild_check.py      lightning-2 --bright 120   # diện tích + bề rộng nét phần sáng so với ẢNH gốc
python lib-fx/_tools/rebuild_check.py      lightning-2 --mode dark --dark-l 40 --dark-d 25   # khung mực: diện tích + IoU phần đen
python lib-fx/_tools/vectorfx.py lifecycle lightning-2      # vòng đời, các cú đánh
python lib-fx/_tools/vectorfx.py showcase  lightning-2      # compare.gif đúng nhịp gốc (mỗi hình giữ đúng số frame)
```

Kết quả `rebuild_check` (so với ảnh gốc). Phần sáng, ngưỡng 120 = toàn hình sét, không tính quầng (màu mép nét có độ sáng 120-165, quầng < 110);
bề rộng = 2 × trung bình khoảng cách tới mép trên khung xương:

| | diện tích dựng / gốc (tb, thấp nhất) | bề rộng nét dựng / gốc (tb) | hình trong 0,8-1,25 | lệch |
|---|---|---|---|---|
| arc | 0,99 (0,92) | 1,12 | 15/17 | 14, 15: mảnh vụn cuối, bề rộng 1,27 / 1,38 |
| strike | 0,92 (0,70) | 1,12 | 13/16 | 7: mảnh vụn cuối, diện tích 0,70; 12: khung mực (chỉ còn vài điểm sáng); 14: chớp đất to |
| bolt | 1,02 (0,96) | 1,03 | 18/18 | không |

Phần đen (khung mực, `--mode dark --dark-l 40 --dark-d 25`): `strike` 12 diện tích 0,95, IoU 0,90; `bolt` 0 diện tích 0,99, IoU 0,90.
Mảnh vụn nhỏ (< 300 px) dựng hơi béo: Smooth & Simplify làm tròn mũi vuốt. Ở ngưỡng 200 (chỉ lõi sáng) `bolt` còn 0,46 diện tích: gradient mép
đo được (s = 3 px) kéo lõi phẳng (độ sáng 209) xuống dưới 200; mắt không thấy khác. Ngưỡng sai cho kết quả sai: nêu ngưỡng cùng con số.

## 2. Lớp và màu

Mỗi biến thể là **một lớp thân phẳng có gradient mép** (không tách lõi thành lớp riêng: thử tách lõi trắng của `arc` làm diện tích lõi lệch
1,25 / 0,51, tệ hơn một lớp), cộng hai lớp đặc biệt và một quầng chung.

| | Thân: màu phẳng (lõi) → mép, `s` | Chớp đất | Khung mực (đảo màu) | Quầng chung (σ px: màu × độ mạnh) |
|---|---|---|---|---|
| arc (xanh) | trắng (255,255,255) → (101,197,248), s 8,5 | không | không | 2,4: (−3,72,309); 28: (−28,74,260) |
| strike (vàng) | vàng nhạt (250,254,186) → (249,210,129), s 4,3 | (255,255,58), elip ~60-90 × 14-24 px | 1 hình | 5,6: (102,48,−21); 52: (213,87,−4) |
| bolt (xanh) | lục lam (126,230,252) → (24,147,238), s 3,1 | (60,255,255), elip ~80 × 20 px | 1 hình | 2,7: (−94,73,290); 67: (−3,49,200) |

- **Lõi sáng nhất ở giữa nét, mép tối hơn một bậc cùng sắc** (gradient mép, không có nét viền tối). Mảnh mỏng (< 2·s) gần như chỉ còn màu mép:
  nét càng mỏng càng đậm màu.
- **Quầng là bản làm nhoè của hình, hai tầng**: một tầng hẹp (σ 2-6 px) bám sát nét, một tầng rộng (σ 28-67 px) phủ cả cụm. Màu quầng là sắc
  chính bão hoà (xanh lam đậm / cam), không phải màu lõi.
- **Chớp đất** (`flash`): elip phẳng màu bão hoà quá mức (một kênh = 255, kênh còn lại 58-60) ở điểm chạm đất, mép mềm (`feather` 2,5 px), quầng
  riêng hình elip rộng ngang gấp ~4 (σ dọc × ngang: 6-9 × 25-36 và 20-22 × 75-80). Chỉ có ở hình tia chạm đất.
- **Khung mực** (`ink`): cả tia tô đen (0,0,0) trong một quầng **mạnh và rộng gấp 2-3 lần** quầng thường (strike: σ 26-28 với màu (490,340,−70),
  cộng một tầng σ 300 dọc × 45 ngang chạy theo thân tia). Quầng chung đo bằng độ mạnh từng hình bị chặn ở 2 nên lớp này có quầng riêng (`own_halo`).

## 3. Nhịp

Video 30 fps nhưng **vẽ ở 24 fps "on ones"** (mỗi hình một tia mới); cứ 5 frame video có một frame lặp lại (pulldown 24 → 30), nên bảng nhịp
trong `exposure.json` có nhiều số 2 không phải là frame giữ thật. Số frame giữ thật = khoảng trống (tia đã tắt).

| | Vòng lặp | Hình vẽ | Cú đánh / vòng | Khoảng trống giữa hai cú |
|---|---|---|---|---|
| arc | 30 frame video (1,0 s) | 19 | 3 | 0, 2 và 6 frame video |
| strike | 23 frame video (0,77 s) | 17 | 2 (+ 1 tia ngược từ đất) | 4 frame |
| bolt | 30 frame video (1,0 s) | 20 | 3 | 5 frame |

Mỗi cú đánh đi qua cùng các pha (số hình vẽ ở 24 fps):

| Pha | Số hình | Hình dạng (số đo) |
|---|---|---|
| **Báo trước / mồi** (có thể bỏ) | 0-1 | một mẩu đầu tia ở nguồn: `strike` 9 (đầu tia rơi ở 80 px trên cùng); `arc` 4 (một lưỡi mảnh 260 × 60 px) |
| **Vào: cú quệt** | 1 | hình rộng gấp 2-3 lần nét thường, chưa chạm đất: `bolt` 17 rộng 80 px (nét đỉnh sau đó 28 px), `bolt` 5 rộng 23 → 37 |
| **Đỉnh: chạm** | 1-2 | **một mảnh** (largest = 100 % diện tích), dài hết khung (cao 540 px của khung 640), chớp đất sáng; `strike` 0: đầu mũi tên ở đỉnh, rộng 22 px |
| **Mỏng dần** | 1-3 | vẽ lại theo cùng đường, gấp khúc dịch chỗ; bề rộng còn ~0,5-0,6 (strike 22 → 13 → 11) |
| **Khung mực** | 1 (giữ 1-2 frame video) | **hình thứ hai sau cú chạm** (sau một hình mỏng: `strike` 10 chạm → 11 → **12**; `bolt` 18 chạm → 19 → **0**), cùng đường tia, mỏng như hình trước (`bolt` 0: rộng 14,5 so với 28 ở đỉnh); quầng ×2-3 |
| **Vỡ** | 3-5 | đứt thành 3-12 mảnh dọc đường cũ; diện tích còn 0,5-0,8 mỗi hình (`bolt` 0,79 / 0,65; `strike` 0,56; `arc` 0,28-0,56); bề rộng xuống 4-6 px; mỗi mảnh là một vuốt / lưỡi liềm nhọn hai đầu, **tan tại chỗ** (không bay, không co về một điểm) |
| **Tắt** | 2-6 frame video | trống; cú sau ở **đường khác** (không bao giờ lặp đường cũ) |

Độ mạnh quầng chung (`halo.gain`) **tăng** khi tia vỡ: 1,0 ở đỉnh → 1,3-1,5 khi vỡ → 2,0-2,3 ở mảnh cuối (`arc` 15, `bolt` 15). Quầng sáng theo
từng mảnh, không theo tổng diện tích: mảnh vụn vẫn chói. Ngược hẳn loại nổ, nơi quầng tắt trước hình ([../explosion/README.md](../explosion/README.md) §3).

## 4. Hình

Đo trên mảnh lớn nhất ở các hình đỉnh (khung 640 px; viền đơn giản hoá sai số 3 px):

| | bề rộng nét p10 / p50 / p90 / max (px) | điểm neo viền | góc trong 60-150° | mũi < 60° |
|---|---|---|---|---|
| strike 0, 2, 11, 15 | 2-10 / 10-26 / 14-43 / 27-52 | 11-21, mỗi điểm ~60-115 px viền | 3-14 | 1-4 |
| bolt 1, 6, 9, 19 | 4-16 / 11-52 / 26-84 / 34-104 | 13-34, ~44-68 px | 3-15 | 1-3 |
| arc 5, 11, 12, 18 | 4-6 / 12-16 / 26-39 / 35-50 | 27-32, ~40-53 px | 8-12 | 2-3 |

1. **Thân là đa giác gấp khúc, cạnh thẳng hoặc hơi cong**, không phải đường cong mềm: 2-4 đoạn lớn mỗi tia (strike: đoạn đứng 300 px, gập 30-50 px
   sang ngang, đoạn ngắn 100-150 px), góc gập trong 60-150°.
2. **Bề rộng dao động mạnh dọc nét** (p90 / p50 ≈ 1,5-3): một hoặc hai đoạn phình to (rộng 35-100 px) nối bằng đoạn mảnh; hai đầu và các điểm gập
   vuốt nhọn thành mũi (1-4 mũi < 60° mỗi tia).
3. **Mũi tên ở đầu tia đánh xuống / bật lên** (`strike` 0, 1, 2: đầu nhọn có ngạnh ở đỉnh; `strike` 11, 12: ngạnh ở chân).
4. **Tia nhánh ngắn ở chân** khi chạm đất: 2-3 vạch nhọn 20-40 px chĩa ra hai bên (`strike` 0, 15).
5. Tia **xuất phát ngoài khung hoặc ở mép trên** (`strike`, `bolt` y = 2-8) và kết thúc đúng ở điểm chớp đất (y ≈ 545).

## 5. Luật đo được của một cú sét (đọc để hiểu vì sao bản remake đẹp)

1. Một cú = 6-10 hình vẽ ở 24 fps: [mồi 0-1] → quệt 1 → đỉnh 1-2 → [mực 1] → mỏng 1-3 → vỡ 3-5 → trống 2-5. Ba cú mỗi giây ở cỡ khung này.
2. Mỗi hình **vẽ lại** cả tia theo một đường gấp khúc cố định của cú đó (neo đầu và chân giữ nguyên, các điểm gập dịch 5-20 px mỗi hình, đoạn phình
   đổi chỗ). Không nội suy, không tịnh tiến.
3. Bề rộng theo pha: quệt 2-3 × nét đỉnh, đỉnh = 1 (≈ 4 % chiều cao khung), mỏng ×0,5-0,6, vỡ còn 4-6 px.
4. Vỡ = cắt đường cũ thành 3-12 đoạn, mỗi đoạn thành vuốt nhọn hai đầu, diện tích × 0,5-0,8 mỗi hình, mảnh lớn nhất ≤ 0,5 tổng.
5. Chớp đất chỉ ở hình chạm đất, elip 4:1, màu bão hoà, quầng elip rộng ngang.
6. Khung mực (tuỳ chọn, cú mạnh): 1 hình, đặt sau hình mỏng đầu tiên (hình thứ hai sau cú chạm), tô đen, quầng ×2-3.
7. Quầng chung hai tầng (σ ≈ 0,4-0,9 % và 4-10 % chiều cao khung), độ mạnh 1 ở đỉnh, tăng tới ~2 ở mảnh cuối; tắt cùng lúc với hình.
8. Màu: lõi sáng phẳng, gradient mép cùng sắc (s 3-8 px), quầng là sắc chính bão hoà; một hệ màu cho một hiệu ứng.

## 6. Bẫy khi đọc bản gốc (đã gặp)

- **Video, không phải GIF**: frame lặp do pulldown 24 → 30 và nhiễu nén h264. `ingest_video` gộp frame giống nhau (ngưỡng: > 200 điểm ảnh lệch > 40
  ở một kênh = hình mới) và ghi `exposure.json`; nền = phân vị 20 của mỗi frame thứ 3 (bỏ được lưới, viền tối, góc méo của bản quay màn hình).
- **Vòng lặp tìm theo nội dung**, không theo nhịp giả định: nét của `strike` lặp sau 23 frame nhưng video chỉ lặp chính xác sau 115 frame
  (5 × 23). Đã so 7 hình "khác" ở các vòng sau với hình cùng chỗ của vòng đầu: **nét giống hệt**, chỉ chớp đất / quầng sáng hơn hoặc tối hơn,
  và khoảng trống có khi chứa mẩu đầu tia rơi sớm một frame. Tức là lớp chớp và quầng chạy theo nhịp riêng, lệch một frame giữa các vòng. Bản dựng
  lấy vòng đầu (frame 0-22).
- **Vùng cắt theo phạm vi thật** (cột nào có điểm ảnh lệch nền trên cả video): cắt đều 640 px làm mất mép cung `arc` (tới x = 636).
- **Màu mép chớp đất trùng màu mép thân sét xanh** (48,200,250) ↔ (73,188,247): lớp chớp ăn mép thân. Chỉ lấy màu lõi bão hoà của chớp (tol 34),
  để phần mềm cho `feather` + quầng riêng.
- **Khung mực**: quầng của nó vượt trần độ mạnh 2 của quầng chung → lớp có quầng riêng (`own_halo`), `halo_gain_max` 6.
  Giới hạn của mô hình: quầng riêng của mực `strike` có một tầng σ dọc chạm biên 300 (300 × 45): thực ra là một cột sáng gần đều chạy dọc cả
  thân tia, không phải quầng tròn; mực `bolt` có một tầng hẹp màu âm (σ ~2, (−18,−122,−199)): bù mép mặt nạ (khử răng cưa), không phải quầng
  của designer.
- **Phần tối cần ngưỡng riêng**: viền quầng xanh tối (38,35,62) lệch nền > 14 ở một kênh và tối hơn 40, nên `--mode dark` với `--dark-d` 14 đếm
  nhầm quầng thành mực; dùng `--dark-d 25`. Bản dựng tô trên nền phẳng của profile, bản gốc trên lưới + viền tối: mỗi ảnh so với nền của nó.
- **Kiểm bằng diện tích và bề rộng nét**, không bằng IoU (`rebuild_check.py`): lần dựng `lightning` đầu đạt IoU 0,999 với nét béo gấp 3. Chọn ngưỡng
  sáng giữa màu mép nét và màu quầng (ở đây 120).
- Bản gốc `lightning` (GIF 400 px, nét 2-5 px) chưa sửa: nét béo vì quầng sát nét cùng màu nét; cách sửa đề xuất (lọc "sáng hơn vùng quanh") ở
  `lib-fx/_plans/vfx-rebuild-02/R2b-lightning-thin.md`.

### 6.1 Mẫu `lightning-3` (tia điện tách màu): cách đọc

- **Phóng ×2 khi ingest** (`source.scale` 2): viền màu chỉ 1-3 px và nét mảnh 2-4 px; ở cỡ gốc bước làm mượt xoá mất chúng, phần hụt bị tính vào
  quầng (quầng sát nét thành trắng, nét trông béo). Đo và dựng mất ~7 phút mỗi bước ở cỡ này.
- **Mặt cắt một nét** (frame 27): (112,179,175) → (204,255,255) → trắng (255,255,255) → (144,108,113) → (131,51,77): mép trên xanh ngọc, mép dưới
  đỏ sẫm. Nét mảnh là trắng xám (205,215,215) / (170,192,198).
- **Viền tách màu = hai bản của lõi dịch hai phía** (khoá `chroma` của profile, không dò viền như lớp riêng: dò ra loang lổ). Đo bằng tương quan
  mặt nạ lõi với mặt nạ viền: lệch tâm (−2,5, −4,5) / (+2,2, +4,5) px gốc, nhưng bề rộng viền thấy được = chính khoảng dịch, nên dùng **một nửa**:
  (−1,2, −2,3) xanh ngọc (140,232,205), (+1,1, +2,3) hồng (205,95,130).
- **Quầng ép về một sắc** (`halo_tint` = màu tầng rộng (185,449,827)): tầng hẹp đo tự do ra gần trắng vì ăn các điểm mép chưa có lớp.
- Kết quả: `rebuild_check --bright 200`: diện tích 1,06, bề rộng nét 1,00, 40/50 frame trong 0,8-1,25 (ở 120: 1,11 / 1,15, 35/50). Còn hụt: vài
  nét rất mảnh chỉ có màu viền (không có lõi trắng) bị đứt.

## 7. Bộ sét quanh nhân vật (ĐÃ DUYỆT 2026-11-28): công thức đầy đủ

**Đây là phong cách chính để làm VFX cho game 2D của dự án.** User duyệt cả 6 dáng × 5 màu ("đúng ý", "cực kỳ tốt", "đẹp, final").
Lệnh: `python lib-fx/_tools/vectorfx.py gen-lightning NAME --style STYLE [--colour COLOUR] [--preview-only]`; code
[`vector/gen_lightning.py`](../../../vector/gen_lightning.py) (mọi thông số của một dáng là một dòng trong `STYLES`, màu trong `PALETTES`); kết quả
`lib-fx/_core/results/vector-showcase/generated/gen-lightning-<style>-blue/` (+ `colours/<màu>.gif`); trang xem Lightning-2 Remake
https://claude.ai/artifact/4cbfa2MD123GvG3iVK3ubb (mục "Xưởng sét": chọn dáng và màu).

### 7.1 Ý chính

**Không vẽ sét mới. Lấy chính các hình vẽ tay đã dựng lại (remake vector) và chỉ biến đổi hình học cho hợp dáng nhân vật, có vật lý.**
Mọi thứ làm nên vẻ đẹp của bản gốc được giữ nguyên: khối phẳng màu dịu, lõi sáng + gradient mép cùng sắc, quầng mềm hai tầng với độ mạnh đo từng
hình, chớp đất elip, khung mực (tia đen trong quầng mạnh), nhịp vẽ tay (`exposure.json`). Những gì user đã loại (giữ làm luật, không giữ bản):
nét sét vẽ lại bằng code (mảnh, cứng, màu đậm tối, bóng đen tự thêm), lịch xuất hiện đều / đường bao lớn-nhỏ đều (máy móc), tia đứng rời không bao
quanh, hình lố xuống dưới mặt đất.

### 7.2 Các bước (làm lại cho nhân vật, bộ phận, nguyên tố khác)

1. **Remake mẫu vẽ tay** bằng bộ vector (§1) tới mức khớp ảnh gốc (`rebuild_check`: diện tích và bề rộng nét 0,8-1,25). Mỗi hình vẽ là một
   `svg/NN.svg` có lớp `body` (+ `ink`, `flash`); profile giữ màu, gradient, quầng chung + `halo.gain` từng hình, quầng riêng (`own_halo`) của chớp và
   mực; `recipe/exposure.json` giữ nhịp. Đây là kho hình của phong cách.
2. **Phác dáng bằng khối**: thân chữ nhật cao H, rộng 0,36 H, chân trên mặt đất; tay là thanh từ vai (`arms`: `side` ±1, `angle` độ, 0 = ngang
   phải, 90 = thẳng lên, `length`, `thick` 0,11 H, `y` vai 0,18-0,24 H dưới đỉnh đầu). Khối chỉ để xem; sản phẩm là lớp sau / trước nền trong suốt.
3. **Gán vai trò cho từng loại hình gốc**:
   - hình có **điểm chạm + chớp** (`bolt`) = **tia giữa hai điểm vật lý**. Mỗi hình: đầu tia của chính hình đó (trung bình các điểm y < 40) → điểm
     nguồn, đáy chớp đất gốc (340, 556) → điểm đích (phép đồng dạng: tỉ lệ + xoay + lật). Điểm: `sky` (mép trên), `hand` (bàn tay), `along`
     (theo hướng tay, cách bàn tay d·H), `ground` (mặt đất). Đánh xuống đất: `flash_flat` giữ chớp nằm phẳng trên mặt đất. Phóng từ tay: chớp thành
     điểm va chạm ở đầu xa.
   - hình **cung bò ngang nhiều mảnh** (`arc`) = **cung quấn trên một hình trụ**. Trụ đứng quanh thân (`wrap`): x gốc → góc 300°, y gốc → chiều cao,
     bán kính 0,48 H, vòng nghiêng 0,22. Trụ dọc một tay (`wrap_h` tay ngang, `wrap_axis` tay góc bất kỳ): x gốc → vị trí dọc tay, y gốc → góc
     quanh tay 360° + xoắn 0,9-1,2 vòng (lò xo), bán kính 0,17-0,21 H.
4. **Mặt trước / sau bằng tra ngược**: mỗi điểm ảnh đích có hai nghiệm góc trên trụ (trước / sau); tra về toạ độ hình gốc và lấy mẫu (`cv2.remap`)
   hình đã raster. Mặt sau vẽ trước khối nhân vật (bị che), mặt trước vẽ sau (vắt qua); hình tự hẹp ở mép trụ như dải quấn thật.
5. **Nhân mọi số đo px theo tỉ lệ của lớp** (k = kích thước đích / gốc): σ quầng chung, `s` gradient, `feather` chớp, σ quầng riêng (dọc, ngang).
   Màu và độ mạnh quầng giữ nguyên.
6. **Nhịp**: vòng lặp = vòng lặp gốc (30 frame, 30 fps). Mỗi lớp lấy hình theo `exposure.json` với độ lệch riêng (0, 7-9, 14-15, 19-22) để các lớp
   không cùng lúc bùng: sét không đồng bộ mà vẫn là nhịp vẽ tay.
7. **Vật lý**: tia đánh xuống chạm đúng mặt đất; phần nằm dưới mặt đất bị cắt (kiểm `stroke_px_below_floor = 0`); tia từ tay bắt đầu ở bàn tay.
8. **Thứ tự vẽ**: nền → quầng lớp sau → hình lớp sau (thứ tự lớp của bản gốc: chớp, mực, thân) → khối nhân vật → quầng lớp trước → hình lớp trước.
9. **Màu** (`PALETTES`): `blue` gốc; `gold` = màu đo được của sét vàng `strike` (thân (250,254,186) → mép (249,210,129), quầng, chớp (255,255,58));
   `red` +155°, `purple` +70°, `green` −80°: xoay mọi màu (thân, mép, quầng, chớp, quầng mực) quanh trục xám, giữ quan hệ sáng / tối. Profile trên
   đĩa không bị sửa (đổi màu trong bộ nhớ).
10. **Xuất**: `frames/` (có khối, để xem), `back/` và `front/` (RGBA @2x, chỉ hiệu ứng: ghép lớp sau, nhân vật, lớp trước), `preview.gif` (thân 120 px),
    `preview_game.gif` (thân 60 px, kiểm ở cỡ game), `preview_slow.gif`, `design.json` (lớp nào lấy hình nào ở mỗi frame). Màu khác:
    `--preview-only` ghi `colours/<màu>.gif`, `colours/<màu>_game.gif`.

### 7.3 Sáu dáng đã duyệt (mỗi dáng là một dòng trong `STYLES`)

| `--style` | Ý chiêu | Lớp (vai trò, độ lệch nhịp) |
|---|---|---|
| `wrap` | vận sức, sét bao quanh thân | `strike` sau thân (x +0,44 H, 0) + `strike` trước thân lật ngang (x −0,48 H, 15) + `wrap` quanh thân (8) |
| `arm` | tung chiêu, tay giơ ngang | 2 `wrap_h` quanh tay (bán kính 0,17 / 0,21 H, xoắn +1,2 / −0,9, lệch 0 / 14) + `shoot` từ bàn tay dài 0,95 H (7) |
| `raise` | gọi sét, tay giơ thẳng lên | `bolt2` trời → bàn tay (0) + `wrap_axis` quanh tay đứng (9) + `wrap` quanh thân (20) |
| `dual` | dang hai tay | 2 `wrap_axis` (mỗi tay một cung, xoắn ngược, 0 / 15) + 2 `bolt2` phóng ra hai phía dài 0,9 H (7 / 22) |
| `slam` | đập xuống đất, tay chéo xuống 50° | `wrap_axis` quanh tay (0) + `bolt2` bàn tay → đất phía trước (+1,3 H, 7) + `bolt2` trời → đất sau lưng (−0,5 H, 19), chớp nằm phẳng |
| `prism` | **charge v2**: vận sức với Prism Spark quanh thân (thân không tay); đạt 2026-11-28 | 3 `wrap` Prism Spark quanh thân (bán kính 0,46 / 0,52 / 0,42 H, cao 0,05-1,05 / 0,20-1,22 / 0-0,85 H, lệch 0 / 17 / 34 trên vòng 52 frame, 25 fps) |
| `thrust` | phóng chéo lên 35° | 2 `wrap_axis` quanh tay (0 / 14) + `bolt2` phóng theo hướng tay dài 1,0 H (7) |

Dáng mới: thêm một dòng `STYLES` (khối + `arms` + danh sách lớp `strike` / `shoot` / `bolt2` / `wrap` / `wrap_h` / `wrap_axis`), chạy `gen-lightning`,
xem `preview_game.gif`, kiểm `stroke_px_below_floor`.

**Nguồn hình thứ hai: Prism Spark** (`lightning-3`): mỗi frame một hình, nên frame t lấy hình `(t + lệch) mod 52`, không có bảng nhịp; svg ở
×2 ảnh GIF nên mọi số đo px nhân thêm `source.scale`. Viền tách màu (`chroma`) dịch **trong không gian màn hình sau khi quấn** (đúng bản chất lệch
kênh màu), tô dưới lõi; lõi luôn trắng. Màu (`PRISM_ROT`): xoay sắc quầng và hai màu viền: `gold` −165°, `red` +150°, `purple` +55°, `green` −95°.

### 7.4 Nguyên tố khác

Cùng đường: (1) chọn một mẫu VFX vẽ tay của nguyên tố đó (lửa, băng, độc...), (2) remake bằng bộ vector tới khi `rebuild_check` đạt và user duyệt,
(3) xếp hình của nó vào các dáng bằng đúng các vai trò trên (hình có điểm chạm → tia / cột giữa hai điểm vật lý; hình dải / cung → quấn trên trụ),
(4) lệch nhịp, đổi màu. Code `gen_lightning.py` đọc thẳng `svg/`, profile và `exposure.json` của bản remake: nguyên tố mới cần đổi `SRC`, `PROFILE`,
tên biến thể và hai điểm neo (đầu hình, điểm chạm) cho hợp mẫu mới.

### 7.5 Việc tiếp theo

Đưa dáng cần dùng vào thư viện `lib-fx/element/lightning/` (sheet, meta, @2x) khi gắn cho nhân vật thật, dùng điểm vai / bàn tay thật của nhân vật
thay khối; tách vào / giữ lặp / ra nếu thời gian gồng thay đổi.

## 8. Làm lại toàn bộ ở một session khác (bản đồ file + lệnh)

Mọi thứ cần để làm tiếp đã có trong git; `lib-fx/_study/` (frame trung gian) bị git bỏ qua và **không cần** cho bước đặt hiệu ứng quanh nhân vật.
Cần: Python 3, `numpy scipy pillow opencv-python-headless scikit-image` (`pip install -r requirements.txt` hoặc cài lẻ).

**File**

| Thứ | Ở đâu |
|---|---|
| Mẫu gốc | `ref/vfx/lightning-2/lightnings.mp4` (3 hiệu ứng: `arc`, `strike`, `bolt`), `ref/vfx/lightning-3/reference.gif` (Prism Spark) |
| Profile (màu, gradient, quầng + độ mạnh từng hình, `own_halo`, `chroma`, `halo_tint`, vùng cắt) | `lib-fx/_core/formulas/vector/profiles/lightning-2.json`, `lightning-3.json` |
| Hình vector của bản remake (nguồn của mọi hiệu ứng sinh ra) | `lib-fx/_core/results/vector-showcase/lightning-2/<arc|strike|bolt>/svg/NN.svg`, `lightning-3/spark/svg/NN.svg` |
| Nhịp của bản remake | `lightning-2/recipe/exposure.json` (Prism Spark: mỗi frame một hình, không có bảng) |
| Kiểm tra so với ảnh gốc | `lightning-2/recipe/rebuild_check_*.json`, `lightning-3/recipe/rebuild_check_bright.json` |
| Bộ đặt hiệu ứng quanh nhân vật | `lib-fx/_core/formulas/vector/gen_lightning.py` (`STYLES`, `PALETTES`, `PRISM_ROT`) |
| Kết quả đã duyệt | `lib-fx/_core/results/vector-showcase/generated/gen-lightning-<wrap|arm|raise|dual|slam|thrust|prism>-blue/` (`frames/`, `back/`, `front/`, `preview*.gif`, `design.json`, `colours/<màu>*.gif`) |
| Trang xem (artifact) | `lib-fx/_core/results/vector-showcase/lightning-page/` (`index.html`, `files.json`, README) |
| Công cụ trong bộ kit dùng ở đây | `measure.ingest_video` (video → hình vẽ + `exposure.json`), khoá `feather`, `own_halo`, `halo_gain_max`, `chroma`, `halo_tint` (`compose.py`, `measure.py`), `lib-fx/_tools/rebuild_check.py`, `lifecycle.events` |

**Lệnh**

```bash
# 1) dựng lại bản remake (chỉ cần khi đổi profile; ~5 phút lightning-2, ~15 phút lightning-3 vì ảnh phóng x2)
python lib-fx/_tools/vectorfx.py ingest  lightning-2      # rồi: measure, rebuild, showcase, lifecycle (như §1)
python lib-fx/_tools/vectorfx.py ingest  lightning-3
python lib-fx/_tools/vectorfx.py measure lightning-3
python lib-fx/_tools/vectorfx.py rebuild lightning-3
python lib-fx/_tools/rebuild_check.py    lightning-3 --bright 200
python lib-fx/_tools/vectorfx.py showcase lightning-3

# 2) đặt hiệu ứng quanh nhân vật (đọc thẳng svg + profile + exposure đã commit; ~30-60 giây mỗi dáng)
python lib-fx/_tools/vectorfx.py gen-lightning gen-lightning-wrap-blue  --style wrap
python lib-fx/_tools/vectorfx.py gen-lightning gen-lightning-prism-blue --style prism
# 3) màu khác của một dáng (không ghi đè frame bản xanh đã duyệt)
python lib-fx/_tools/vectorfx.py gen-lightning gen-lightning-prism-blue --style prism --colour gold --preview-only
```

**Gắn vào một animation thật (đã chạy: pale_seraph cape_storm + Charge v2, 2026-11-28, chờ user chấm)**:
`python lib-fx/_tools/vectorfx.py gen-lightning cape_storm_prism --style prism --colour blue --onto out/heroes/_lineups/heroic_ref_five:skill2_t01:pale_seraph --envelope 0:0,6:0.35,12:0.6,30:1,47:1.15,60:0.9,80:0.45,95:0,106:0 --body-px 174`
(thêm `--enhance` để nhân vật nét hơn: khung qua `enhance_x2` (×2, làm phẳng màu, làm nét), `body_px` nhân đôi; bản user chọn 2026-11-28 là
`cape_storm_prism_x2`) → `out/heroes/pale_seraph/.work/fx/<tên>/<màu>/` (`composite/`, `back/`, `front/`, `preview*.gif`). Khung lấy từ sprite_prep đã dọn
(`prep/pale_seraph/skill2_t01.edits.json`: despill, làm nét, xoá mũi tên lạc). Mỗi khung vỏ sét theo bóng dáng (`build_on_sprite`: tâm = trung vị x
của điểm thấy được, chân = hàng thấp nhất, bán kính = nửa bề rộng bóng (áo choàng) / chiều cao thân, kẹp 0,42-1,0 H, làm mượt 5 khung; chiều cao
thân cố định nên tỉ lệ quầng không nhảy); `--envelope` = cường độ theo khung (khoá nối tuyến tính) theo pha của chiêu.

**Gắn vào một nhân vật đứng yên** (dáng có tay): thay khối bằng số đo của nhân vật trong một dòng `STYLES` mới: `H` = chiều cao thân
@2x, `feet` (vị trí chân), `body_x`, `body_w`; với dáng có tay: `arms` (vai, góc, dài) lấy từ pose / rig của nhân vật (`out/heroes/<id>/source/rig/`
hoặc frame của skill); chọn các lớp theo §7.3; xuất `back/` + `front/` rồi ghép quanh sprite (lớp sau, nhân vật, lớp trước). Cùng canvas và tỉ lệ
với sheet của nhân vật (`meta.json` của sheet), kiểm ở cỡ game (thân 60 px).

**Kiểm hồi quy khi sửa `gen_lightning.py`**: tạo lại `wrap` và `arm` vào thư mục tạm (`gen_lightning.build('x', s, out_root=...)`), so md5 của
`frames/*.png` với bản đã commit: phải giống hệt.
