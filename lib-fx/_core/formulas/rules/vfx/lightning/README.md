# VFX loại "lightning" (sét)

Một tia sét đánh, vỡ ra rồi tắt, và một tia mới mọc ở đường khác. Không có chuyển động liên tục: **mỗi hình vẽ là một tia vẽ lại**.
Luật chung cho mọi loại hiệu ứng nằm ở [../../README.md](../../README.md) và các file 01-05; file này chỉ ghi phần riêng của sét.

## 0. Bản gốc đã đọc

| Bản gốc | Biến thể | Profile | Kết quả | Trạng thái |
|---|---|---|---|---|
| `ref/vfx/lightning-2/lightnings.mp4` (1920×640, 30 fps, 20 s; ba hiệu ứng lặp cạnh nhau) | `arc` (trái: cung sét xanh bò ngang), `strike` (giữa: sét vàng đánh thẳng xuống đất), `bolt` (phải: sét xanh lớn từ trên xuống đất) | [`lightning-2.json`](../../../vector/profiles/lightning-2.json) | [showcase/lightning-2](../../../../results/vector-showcase/lightning-2/) | dựng lại trọn vòng lặp, chờ user chấm |
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

## 5. Luật cho bộ sinh sét (chưa viết bộ sinh)

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

## 7. Bộ sinh và việc tiếp theo

**Sét quanh nhân vật: `wrap`** (**ĐÃ DUYỆT**, user 2026-11-28: "đúng ý mình rồi, hãy lưu giữ style làm sét này"; đây là phong cách sét chuẩn của repo), `python lib-fx/_tools/vectorfx.py gen-lightning NAME`, code [`vector/gen_lightning.py`](../../../vector/gen_lightning.py),
kết quả [generated/gen-lightning-wrap-blue](../../../../results/vector-showcase/generated/gen-lightning-wrap-blue/).
Không vẽ sét mới: lấy chính các hình vector của bản remake (`bolt`, `arc`: svg từng hình), giữ nguyên màu, gradient mép, quầng và độ mạnh quầng từng
hình, chớp đất, khung mực và nhịp (`exposure.json`); chỉ đổi hình học:
- **Tia đánh xuống** (hình `bolt`): điểm chạm đất của bản gốc (đáy chớp đất) ghim vào mặt đất cạnh chân, nên không lố xuống đất; một tia sau thân,
  một tia trước thân (lật ngang), lệch nhau nửa vòng lặp. Tỉ lệ 1,35 H / 551 px.
- **Cung quấn quanh thân** (hình `arc`): coi như vẽ trên một hình trụ quanh trục thân: x của bản gốc → góc (300°), y → chiều cao (0,18-1,18 H); mỗi
  điểm ảnh tra ngược mặt trước (sin > 0) và mặt sau riêng, nên nửa sau bị thân che, nửa trước vắt qua người, hình hẹp lại ở hai bên như dải quấn;
  vòng nghiêng 0,22 (nửa trước thấp hơn). Phần dưới mặt đất bị cắt (mặt đất che).
- Mọi số đo px (σ quầng, `s` gradient, mép chớp, quầng riêng) nhân theo tỉ lệ của từng lớp; vòng lặp = vòng lặp gốc (30 frame, 30 fps), ba lớp
  lệch nhịp nhau.

Bài học từ bốn vòng nhận xét của user (2026-11-28): (1) **giữ phong cách của bản remake** (khối phẳng màu dịu, quầng mềm): vẽ lại bằng nét
mảnh + bóng đen đậm (`crackle`) bị chê "đậm, tối, không tự nhiên"; (2) lịch đều hoặc đường bao đều (`aura`, `charge`) đọc ra máy móc, sét phải không
đồng bộ: dùng chính nhịp vẽ tay của bản gốc và lệch pha các lớp; (3) sét bao quanh = có phần sau thân và phần trước thân, không tia đứng rời; (4) không
gì nằm dưới mặt đất (ghim điểm chạm đất, cắt phần dưới); (5) các nét đen user thấy trong bản remake là **khung mực** (tia đen trong quầng), giữ nguyên.

**Cách làm sét chuẩn (dùng lại cho mọi nhân vật / hiệu ứng sét mới):**
1. Hình sét lấy từ một bản remake vẽ tay đã dựng lại (vector, đúng màu, gradient, quầng, chớp đất, khung mực, nhịp); không tự vẽ nét sét mới bằng code.
2. Chỉ biến đổi hình học: ghim điểm chạm đất vào mặt đất (tia đánh xuống), quấn quanh thân trên hình trụ có mặt trước / sau (cung), lật ngang,
   đổi tỉ lệ; mọi số đo px nhân theo tỉ lệ.
3. Lớp sau thân và trước thân tách riêng; vài lớp lệch nhịp nhau (sét không đồng bộ); không gì nằm dưới mặt đất.
4. Màu khác (vàng, tím...): dùng bản remake cùng phong cách (`strike` vàng) hoặc đổi màu trong profile, giữ nguyên hình và nhịp.

### 7.1 Cách làm chi tiết (từng bước, để làm lại cho nhân vật / bộ phận khác)

1. **Có bản remake trước.** Dựng lại hiệu ứng tham khảo bằng bộ vector (§1): mỗi hình vẽ là một `svg/NN.svg` (lớp `body`, `ink`, `flash`), profile
   giữ màu, gradient mép, quầng chung + độ mạnh từng hình (`halo.gain`), quầng riêng của chớp đất và khung mực, `recipe/exposure.json` giữ nhịp
   (frame đầu + số frame giữ của từng hình). Đây là "kho hình" của phong cách; không vẽ thêm nét nào.
2. **Phác dáng nhân vật bằng khối**: thân chữ nhật (cao H, rộng 0,36 H, chân trên mặt đất); khi cần bộ phận thì thêm khối của nó (tay giơ ngang:
   từ vai ở 0,22 H dưới đỉnh đầu, dài 0,85 H, dày 0,11 H). Khối này chỉ để xem trước; sản phẩm là lớp sau / trước nền trong suốt.
3. **Chọn vai trò cho từng hình gốc**:
   - `bolt` (tia lớn có điểm chạm + chớp) = **tia đánh / tia phóng**: ghim một điểm của hình gốc vào một điểm vật lý. Đánh xuống: đáy chớp đất
     (340, 556) → mặt đất cạnh chân. Phóng từ tay: điểm đầu của tia (trung bình các điểm có y < 40, tính lại **từng hình** vì mỗi hình vẽ lại tia ở chỗ
     khác) → bàn tay, xoay −90° để tia chạy ra phía trước, chớp đất thành chớp va chạm ở đầu xa.
   - `arc` (cung bò ngang, nhiều mảnh) = **cung quấn**: coi như vẽ trên một hình trụ. Trụ đứng quanh thân: x gốc → góc (300°), y gốc → chiều cao,
     vòng nghiêng 0,22. Trụ nằm dọc cánh tay: x gốc → vị trí dọc tay, y gốc → góc quanh tay (360°) + xoắn 0,9-1,2 vòng theo chiều dài (thành lò
     xo). Bán kính trụ 0,17-0,21 H cho tay, 0,48 H cho thân.
4. **Mặt trước / sau bằng tra ngược**: với mỗi điểm ảnh đích, tính hai nghiệm góc (mặt trước: sin > 0 với trụ đứng, cos > 0 với trụ nằm; mặt sau:
   nghiệm còn lại), tra ngược về toạ độ hình gốc và lấy mẫu (`cv2.remap`) hình đã raster. Mặt sau vẽ **trước** khối nhân vật (bị che), mặt trước vẽ
   **sau** (vắt qua). Hình tự hẹp lại ở mép trụ như dải quấn thật.
5. **Nhân mọi số đo px theo tỉ lệ của lớp** (k = kích thước đích / kích thước gốc): σ quầng, `s` gradient, `feather` chớp, σ quầng riêng (dọc,
   ngang). Màu và độ mạnh quầng giữ nguyên.
6. **Nhịp**: vòng lặp = vòng lặp gốc (30 frame, 30 fps); mỗi lớp lấy hình theo `exposure.json` với độ lệch riêng (0, 7-8, 14-15, 21) để các lớp không
   cùng lúc bùng: sét không đồng bộ mà vẫn là nhịp vẽ tay của bản gốc.
7. **Vật lý**: tia đánh xuống chạm đúng mặt đất; phần nào rơi dưới mặt đất thì cắt (mặt đất che); tia từ tay bắt đầu ở bàn tay.
8. **Xuất**: `frames/` (có khối, để xem), `back/` và `front/` (RGBA, chỉ hiệu ứng: ghép sau nhân vật, nhân vật, trước nhân vật), `preview.gif`,
   `preview_game.gif` (thân 60 px), `design.json` (lớp nào lấy hình nào ở mỗi frame).
9. **Biến thể mới = một dòng trong `STYLES`** của `gen_lightning.py` (khối nhân vật + danh sách lớp `strike` / `shoot` / `wrap` / `wrap_h`):
   - `wrap` (quanh thân, đã duyệt): 2 `strike` (sau thân, trước thân lật ngang, lệch nửa vòng) + 1 `wrap`.
   - `arm` (quanh tay giơ ngang): 2 `wrap_h` (xoắn ngược chiều nhau, bán kính 0,17 / 0,21 H) + 1 `shoot` từ bàn tay dài 0,95 H.

### 7.2 Phong cách VFX chính của game và các dáng chiêu

**Đây là phong cách chính để làm VFX cho game 2D của dự án** (user 2026-11-28, sau khi duyệt `wrap` và `arm`): hình vẽ tay đã dựng lại thành
vector (khối phẳng màu dịu, gradient mép cùng sắc, quầng mềm hai tầng, khung đảo màu đen, nhịp vẽ tay), đặt vào dáng nhân vật bằng biến đổi hình học
có vật lý (§7.1). Không vẽ hiệu ứng mới bằng nét code thô khi đã có bản remake phù hợp; hiệu ứng loại khác (lửa, băng...) đi cùng đường: remake một
mẫu vẽ tay tới 9-10/10 → dùng hình của nó, chỉ biến đổi hình học, màu, nhịp lệch pha.

| Dáng (`--style`) | Ý chiêu | Lớp | Trạng thái |
|---|---|---|---|
| `wrap` | vận sức, sét bao quanh thân | 2 `strike` (sau / trước thân) + 1 `wrap` | **đạt** (2026-11-28) |
| `arm` | tung chiêu bằng tay giơ ngang | 2 `wrap_h` xoắn quanh tay + 1 `shoot` từ bàn tay | **đạt** (2026-11-28) |
| `raise` | gọi sét: tay giơ thẳng lên trời | 1 `bolt2` trời → bàn tay (chớp va chạm ở tay) + 1 `wrap_axis` quanh tay đứng + 1 `wrap` quanh thân | chờ chấm |
| `dual` | dang hai tay | 2 `wrap_axis` (mỗi tay một cung, xoắn ngược) + 2 `bolt2` phóng ra hai phía | chờ chấm |
| `slam` | đập xuống đất: tay chéo xuống 50° | 1 `wrap_axis` quanh tay + 1 `bolt2` bàn tay → mặt đất phía trước (chớp đất nằm phẳng) + 1 `bolt2` trời → đất sau lưng | chờ chấm |
| `thrust` | phóng chéo lên 35° | 2 `wrap_axis` quanh tay + 1 `bolt2` phóng theo hướng tay | chờ chấm |

Lớp mới cho dáng tự do: tay là thanh từ vai theo góc bất kỳ (`arms`: `side`, `angle` 0 = ngang phải, 90 = thẳng lên, `length`, `thick`, `y` vai);
`wrap_axis` = trụ dọc theo tay bất kỳ; `bolt2` = tia giữa hai điểm vật lý (`hand`, `along` theo hướng tay, `ground` trên mặt đất, `sky` mép trên),
mỗi hình tính lại phép đồng dạng (đầu tia của hình đó → điểm nguồn, điểm chạm đất gốc → điểm đích); `flash_flat` giữ chớp đất nằm ngang trên mặt đất.

**Màu** (`--colour`): `blue` (gốc), `gold` (màu đo được của sét vàng `strike` cho thân, quầng, chớp), `red`, `purple`, `green` (xoay sắc mọi màu
của bản remake quanh trục xám: +155°, +70°, −80°; giữ nguyên quan hệ sáng / tối và quầng). `--preview-only` chỉ ghi `colours/<màu>.gif` và
`colours/<màu>_game.gif` cạnh bản xanh (không ghi đè frame của bản đã duyệt).

Việc tiếp theo: đưa vào thư viện `lib-fx/element/lightning/aura/` (sheet, meta, @2x) khi cần cho nhân vật thật; thêm cung thứ hai hoặc đổi bán kính / độ nghiêng nếu cần; tách thành vào / giữ lặp / ra để thời gian gồng thay đổi được; các kiểu khác (sét đánh xuống mục tiêu, sét chuyền giữa hai mục tiêu, sét vàng); kiểm thêm bằng mẫu thứ ba;
đưa hiệu ứng duyệt vào `lib-fx/element/lightning/` (hiện chưa có hiệu ứng nào).
- Xuất bản dựng theo chuẩn lib-fx (nền trong suốt, @2x, `sheet.png`, `meta.json`): chưa có cho mọi bản dựng vector (`vector/README.md` §9 E).
