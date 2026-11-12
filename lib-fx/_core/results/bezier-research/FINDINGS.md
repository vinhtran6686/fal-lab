# Kết luận: hình xoáy chém dựng lại bằng path Bézier (2026-11-07)

Ảnh: [compare_fire.png](compare_fire.png), [compare_frost.png](compare_frost.png) (gốc | mục tiêu màu phẳng | dựng lại từ công thức |
bản đồ lỗi), [generated_demo.png](generated_demo.png) (hình mới, không lấy toạ độ nào từ GIF). Số liệu: `out/rebuild_report.json`,
`out/analysis.json`, `out/trace_stats.json`.

## 1. Giả thuyết "mỗi lớp màu là một path Bézier khép kín tô phẳng": ĐÚNG

- **Mã màu phẳng tuyệt đối**: trong frame lửa 4, 11 089 điểm ảnh đúng `211,48,85`, 13 552 điểm đúng `255,100,142`. Mặt nạ cũ
  (`layers/`, sai số < 30) lẫn **quầng sáng**: lớp đỏ sẫm của lửa và xanh sẫm của băng ở đó phần lớn là quầng, không phải hình. Mặt nạ
  đúng = sai số < 12 (`masks.py`); riêng lưỡi trắng băng bị quầng cộng thêm màu cyan ở mép nên lấy mọi điểm gần trắng (R>200, G,B>235).
- **Vector hoá** (`vectorize.py`): mọi lớp f3-f5 khớp bằng Bézier bậc 3 với sai số tối đa 1,0-1,41 px, trung bình 0,3-0,46 px.
- **Rất ít điểm neo**: lớp lớn chỉ 21-34 điểm neo (vàng f3: 34, trắng f3: 21), trung bình **26 px viền / một điểm neo**. Đúng kiểu
  vẽ bằng bút vector: vài đường cong dài, không phải nét run tay.
- **Tay nắm theo luật 1/3**: độ dài tay nắm / dây cung: trung vị **0,32**, 80% nằm trong 0,21-0,38. Không có tay nắm kéo dài. Mỗi
  đoạn là một cung "êm" gần cung tròn; độ cong dồn vào điểm neo chứ không vào tay nắm.
- **Góc nhọn** (điểm neo không trơn) có góc trong trung vị **62°**; theo lớp: đỏ sẫm 51°, xanh 52° (mũi kim), hồng 68°, cyan 64°,
  trắng 83°, vàng **102°** (vàng gần như không có mũi: đầu tù, mép trơn). Mũi nhọn nằm ở lớp nguội / lớp trong, không ở lớp nóng.
- **Hai lớp không bao giờ chung một cạnh**: không có điểm ảnh vàng nào cách một lớp khác ≤ 3 px; giữa các lớp luôn có dải chuyển
  2-4 px (đường tối mảnh hoặc pha màu). Nên mỗi lớp là một path riêng tô riêng, không phải một path chung cắt đôi.

## 2. Công thức: mọi loại hình là MỘT nét thon trong toạ độ của xoáy

Mở ảnh sang toạ độ cực quanh tâm xoáy (tâm = đường tròn khớp với viền ngoài): lưỡi liềm thành dải ngang, lưỡi lửa thành gai ngang.
Mỗi hình = một **nét thon** (`shapes.py`):

```
t ∈ [0,1] chạy theo chiều quét, θ = θ0 + (θ1-θ0)·t
xương sống  r_c(t) = Bernstein(b0..bn)                       vị trí (bán kính) của nét
bề rộng     w(t)   = W · (t+e0)^a · (1-t+e1)^b · (1 + Bernstein(m1..mk))
mép         r = r_c ± w/2  -> toạ độ màn hình -> fit Bézier bậc 3, mũi nhọn = điểm neo góc
```

- `a`, `b` = **độ nhọn hai đầu**: < 1 đầu tròn/phình (cạnh lồi), ≈ 1 nêm thẳng, > 1 **mũi kim** (cạnh lõm). `e0`, `e1` = 0 cho mũi
  nhọn, > 0 cho đầu cụt (gốc lưỡi cắm vào thân). Đây là tham số quan trọng nhất cho "điểm nhọn và chỗ lồi lõm".
- `m1..mk` (lượn) chỉ dùng cho nét dài (mỗi ~25 px một hệ số); lưỡi ngắn không cần.
- Hình nào mũi chĩa theo bán kính (móc trắng của băng): dùng cùng công thức theo trục `r` (`axis="r"`).
- **Thứ tự dựng một lớp** (`rebuild.py`): thân trơn trước (fit bền vững: gốc lưỡi lửa dính vào thân bị coi là ngoại lai), rồi cộng
  lưỡi lửa / lông vũ và **khoét** vết (nét thon trừ đi), chỉ giữ mảnh làm IoU tăng ≥ 0,003. Khoét vết là có thật: 1-5 vết mỗi lớp,
  bề rộng ~6 px, dài ~4 lần rộng, hai đầu tròn (a, b ≈ 0,4).

## 3. Kết quả dựng lại f3-f5 (IoU với mặt nạ màu đúng)

| Lớp | f3 | f4 | f5 | Ngưỡng |
|---|---|---|---|---|
| vàng | 0,954 | 0,952 | 0,941 | 0,85 |
| hồng | 0,895 | 0,900 | 0,896 | 0,85 |
| trắng (băng) | 0,966 | 0,960 | 0,905 | 0,85 |
| xanh (băng) | 0,863 | 0,882 | 0,855 | 0,85 |
| hổ phách | 0,766 | 0,819 | 0,781 | 0,7 |
| đỏ sẫm | 0,855 | 0,888 | 0,816 | 0,7 |
| cyan | 0,896 | 0,930 | 0,915 | 0,7 |
| xanh sẫm | 0,815 | 0,813 | 0,819 | 0,7 |

Đạt ở cả 24 lớp. So với mặt nạ cũ `layers/` (có quầng) IoU thấp hơn, nhất là đỏ sẫm (0,58-0,65) và xanh sẫm (0,29-0,34): phần
chênh là quầng sáng, nằm ngoài phạm vi. Số nét mỗi lớp: 2-27; số điểm neo của path sinh ra ≈ 1,1-2 lần path vẽ tay (vàng f3: 38
so với 34; xanh f5: 126 so với 62). Nghĩa là công thức đúng hình nhưng **chưa gọn bằng designer** ở lớp nhiều chi tiết.

## 4. Số đo theo loại hình (trung vị, `out/analysis.json`)

| Loại | a (đầu cũ) | b (đầu mới) | dài / rộng | rộng | Ghi chú |
|---|---|---|---|---|---|
| lưỡi liềm chính | 0,74 | 0,47 | 6,9 | 49 px | quét ~118°; đầu mới tròn, đuôi thon (mũi kim là lớp đỏ / xanh nằm trong) |
| lưỡi lửa / gai | 0,60 | 0,45 | 2,4 | 9 px | cạnh **lồi**, không lõm; 55% chĩa ngược chiều quét, 45% xuôi |
| lông vũ cyan / xanh | 0,53 | 0,62 | 2,5 | 14 px | hai đầu nhọn, bụng gần giữa |
| viền hổ phách | 1,46 | 2,55 | 9,4 | 4,5 px | dải mỏng, hai đầu kim, đứt đoạn chứ không bao kín |
| vết khoét | 0,40 | 0,42 | 4,3 | 6 px | trừ vào lớp, đầu tròn |
| móc / mảnh nhỏ | 1,73 | 1,02 | 1,5 | 5,5 px | ngắn, mũi kim một đầu |

**Nhịp to-nhỏ** (lưỡi / lông vũ xếp theo chiều quét): tỉ lệ độ dài hai chi tiết liền nhau trung vị **2,3-5** (không bao giờ ≈ 1,
trừ 4 lông vũ cyan f4: 1,2), hệ số biến thiên khoảng cách **0,54-1,2**. Đây là định lượng của "không lặp khuôn".

## 5. Cái gì đúng, cái gì chưa

- Đúng: ngôn ngữ đường nét = ít điểm neo, tay nắm ≈ 1/3 dây cung, độ nhọn nằm ở số mũ hai đầu (a, b), chi tiết theo chiều quét.
- Đúng: phân rã "thân + lưỡi cộng + vết khoét" khớp mọi lớp với ít tham số đọc được (mỗi nét 10-30 số).
- Chưa: tham số ở bước 4 là **đo** từ GIF (công thức là chung, con số là của frame đó). Dựng hình mới cần luật bố cục: `generate.py`
  là bản thử đầu (thân + viền + lưỡi theo nhịp đo được), đúng ngôn ngữ nhưng còn thưa và gốc lưỡi còn cụt; chưa đạt độ đẹp của gốc.
- Chưa: mũi móc chĩa theo bán kính (đáy lưỡi trắng f4-f5) vẫn hơi tròn; nét theo trục `r` ít khi được chọn. Cần một nét tự do
  (xương sống Bézier bất kỳ, không theo cực) cho các móc này.
- Chưa: path sinh ra nhiều điểm neo hơn path vẽ tay ở lớp nhiều chi tiết (xanh, đỏ sẫm): bước sau là gộp nét kề nhau.

## 6. Bản v2 sau review của user (2026-11-08)

User đánh giá v1: tỉ lệ, hướng và góc đúng, nhưng (1) nét lổm chổm, như nhiều nét rời ghép lại, gấp khúc ở chỗ đáng lẽ là đường cong
trơn; (2) thiếu gradient theo màu chính làm hiệu ứng mượt. Code: `rebuild2.py`, `pen.py`, `masks.family_masks`; số liệu
`out2/report.json`, `out/edge_gradient_fit.json`, `out/halo_fit.json`; xem trên trang Swirl Slash Shapes (`review.html`).

**Phát hiện chính: mặt nạ v1 đọc sai hình.** Lớp vàng và lưỡi trắng có **gradient trong** sát mép: vàng `255,214,112` ngả dần sang
cam `255,163,69` trong ~8 px; trắng ngả sang xanh nhạt `178,253,252` trong ~3,4 px (hồng ~2,7 px, cyan ~1,5 px; đỏ sẫm, xanh, xanh sẫm
phẳng). Mặt nạ "đúng mã màu" bỏ mất dải đó: vàng hụt ~30 % diện tích, mũi lưỡi lửa hồng đâm vào dải cam bị mất, giữa các lớp còn khe
tối. "Hổ phách" không phải một lớp: đó là dải mép của lớp vàng. Mặt nạ v2 (`family_masks`) coi mỗi lớp là một đường màu
(màu phẳng → màu mép). Lửa còn 3 lớp: vàng, hồng, đỏ sẫm.

**Cách dựng v2:**
1. **Tô chồng** theo thứ tự (lửa: vàng → hồng → đỏ sẫm; băng: xanh sẫm → xanh → cyan, lưỡi trắng riêng). Lớp dưới được khớp với vùng
   của nó cộng phần lớp trên nằm trong 10 px, nên chạy liền dưới lớp trên: hết khe, hết mối nối. Đường tối mảnh giữa lưỡi trắng và
   ngọn lửa xanh được giữ (là thiết kế).
2. **Pen pass** (`pen.py`): hợp các nét công thức của một lớp → bỏ vụn < 8 px → viền → chỉ giữ góc thật (góc trong < 150° trên cửa sổ
   ±4 px) → làm trơn dọc viền giữa hai góc (gauss σ 2,5 px, góc ghim cố định, mảnh nhỏ σ nhỏ hơn) → fit Bézier nối G1. Kết quả: mỗi
   đoạn giữa hai mũi nhọn là một đường cong liền.
3. **Gradient trong**: màu = lerp(màu phẳng, màu mép, exp(-d/s)), d = khoảng cách tới mép phần nhìn thấy của lớp.
4. **Quầng sáng sau hình**: c_far·exp(-d/s_far) (+ thành phần gần rất nhỏ), d = khoảng cách tới hình. Lửa đỏ `195,-8,43`, s 38 px;
   băng xanh `1,57,91`, s 27 px (đo trên frame 3-5, frame 13 làm nền).

**IoU v2** (phần nhìn thấy của mỗi lớp so với mặt nạ v2, khó hơn v1 vì hình to và nhiều mũi hơn), frame 3 / 4 / 5:
vàng 0,965 / 0,943 / 0,926 · hồng **0,818 / 0,869 / 0,816** · đỏ sẫm 0,873 / 0,898 / 0,831 · trắng 0,956 / 0,953 / 0,921 ·
xanh 0,848 / 0,882 / 0,859 · cyan 0,862 / 0,905 / 0,884 · xanh sẫm 0,816 / 0,832 / 0,840.
Lớp hồng f3, f5 và xanh f3 dưới 0,85: lưỡi lửa mảnh (rộng 3-6 px) mất một phần khi làm trơn và khi lớp đỏ sẫm phía trên lấn sang.
Frame 8-12 chỉ còn móc vụn vài trăm điểm ảnh: IoU 0,25-0,66, nhìn bằng mắt vẫn đúng chỗ, đúng dáng.

**Luật rút ra:** đo hình phải đo cả gradient trong của lớp (không lấy đúng mã màu); dựng lớp bằng cách tô chồng, lớp dưới liền khối;
mọi viền đi qua một bước "pen" (làm trơn giữa các góc thật) trước khi xuất; quầng sáng là hàm của khoảng cách tới hình.

## 7. Bản v3: tự làm đều nét (2026-11-08)

User chấm v2 ~7/10 và yêu cầu cơ chế tự làm đều nét như Illustrator. Code: `lib-fx/_core/formulas/vector/smooth.py` (`smooth_simplify`), `rebuild3.py` (giữ nguyên
nét công thức của v2 trong `out2/params_*.json`, chỉ thay bước viền), `smoothness.py` (thước đo). Số liệu: `out3/report.json`,
`out3/smoothness_f3-5.json`.

Tham khảo: Illustrator Object > Path > Simplify (độ bám đường + ngưỡng góc:
[Adobe help](https://helpx.adobe.com/illustrator/desktop/draw-shapes-and-paths/modify-paths/simplify-paths-advanced-options-overview.html)),
Potrace / Image Trace (`alphamax` = ngưỡng góc, `opttolerance` = gộp các đoạn Bézier liền kề: [potrace(1)](https://www.mankier.com/1/potrace)),
fair curve / minimum variation curve (Moreton 1993: đường đẹp = độ cong biến thiên ít nhất:
[Berkeley tech report](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1993/5219.html)).

6 bước cho mỗi viền: nối khe < 1,5 px và bỏ vụn → góc thật phải nhọn ở cả hai tầm (±4 px < 145° và ±8 px < 165°) → làm trơn giữa hai
góc bằng hệ tuyến tính min |q-p|² + λ₂|D²q|² + λ₃|D³q|² (σ 4,5 px, góc ghim, bù diện tích bị co) → fit Bézier G1 → neo gãy < 35° nắn
thành neo trơn, rồi gộp đoạn liền kề khi sai số ≤ 0,9 px → tay nắm ≤ 0,45 dây cung.

Trung bình frame 3-5 (điểm neo / điểm gãy 5-35° / độ biến thiên độ cong mỗi 100 px):

| Lớp | Đường vẽ tay của gốc | v2 | v3 |
|---|---|---|---|
| vàng | 53 / 0 / 2,82 | 53 / 5,3 / 1,41 | 45 / 0,3 / 0,73 |
| hồng | 80 / 0 / 0,87 | 88 / 8,3 / 10,21 | 80 / 0 / 0,71 |
| đỏ sẫm | 89 / 0 / 1,57 | 78 / 7,0 / 2,87 | 62 / 0,3 / 1,00 |
| trắng | 29 / 0 / 0,28 | 41 / 3,7 / 1,24 | 36 / 0,3 / 0,55 |
| cyan | 40 / 0 / 0,63 | 34 / 2,0 / 0,35 | 34 / 0 / 0,58 |
| xanh | 56 / 0 / 0,50 | 60 / 6,3 / 2,42 | 49 / 0,3 / 0,72 |
| xanh sẫm | 41 / 0 / 5,33 | 30 / 3,0 / 0,99 | 24 / 0 / 0,88 |

(Đường vẽ tay của gốc được đo bằng cách vector hoá mặt nạ; độ biến thiên của nó ở vàng và xanh sẫm cao vì mặt nạ còn răng cưa điểm ảnh.)
v3 hết điểm gãy, độ biến thiên độ cong giảm 2-14 lần so với v2, số điểm neo bằng hoặc ít hơn đường vẽ tay. Số điểm uốn (đổi chiều cong)
tăng nhẹ (1,5-2,3 mỗi 100 px so với 1,1-1,8 ở v2). IoU gần như giữ nguyên ở frame 2-5 (thay đổi trong khoảng ±0,03; hồng f5 0,796,
đỏ sẫm f5 0,796), giảm thêm ở frame vụn 7-12.

### 7.1 Băng mượt tối đa (sau review: lửa 9/10, băng 8/10 "còn nứt nẻ")

Ba nguyên nhân "nứt nẻ" ở bản băng và cách sửa:
1. **Đường tối giữa lưỡi trắng và ngọn lửa xanh là đọc sai**: đo dải 2 px giữa hai lớp trên f3-f5 được màu `91,195,236`, tức pha giữa
   trắng và xanh (khử răng cưa), không phải nét tối. V2/v3 giữ nó thành khe tối, nhìn như vết nứt. Nay băng là một nhóm: lớp xanh chạy
   liền dưới lưỡi trắng (`rebuild2.GROUP`), nét công thức của băng được khớp lại.
2. **Viền sáng lấm tấm**: thành phần quầng gần của băng (s 0,5 px) là khử răng cưa của GIF, vẽ ra thành chấm sáng quanh mép. Bỏ
   (`rebuild3.NEAR_HALO`).
3. **Làm trơn mạnh hơn cho băng** (`rebuild3.SMOOTH`): σ 7 px, ngưỡng góc 142° (130° làm tròn mũi lông vũ), gộp đoạn khi sai số ≤ 1,5 px,
   nối khe ≤ 2,5 px, bỏ vụn < 40 px.

Trung bình f3-5 (điểm neo / điểm gãy / độ biến thiên độ cong): trắng 23 / 0 / 0,41 · cyan 36 / 0 / 0,60 · xanh 34 / 0,3 / 0,48 ·
xanh sẫm 19 / 0 / 0,36. Ít điểm neo hơn đường vẽ tay của gốc (29 / 40 / 56 / 41). Đổi lại IoU giảm nhẹ: xanh f3 0,821, f5 0,789,
cyan f3 0,814; frame vụn 6-9 giảm rõ (bỏ vụn < 40 px).
Khác biệt còn lại dễ thấy nhất với gốc: phía sau ngọn lửa xanh của bản gốc có một mảng xanh sẫm trong mờ lớn, có lỗ hình bầu dục.
Mặt nạ đúng màu chỉ bắt được một phần nhỏ của mảng này, nên bản dựng chưa có nó.
