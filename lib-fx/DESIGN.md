# Phương pháp thiết kế fx của lib-fx

Ghi lại cách đã làm ra bộ `force/shock` (5 sóng xung kích, user đánh giá "đẹp hơn rất nhiều" ngày 2026-11-06) để làm lại
cho mọi hiệu ứng sau này. Bản đồ thư mục: [GUIDE.md](GUIDE.md); lệnh và cấu trúc file: [README.md](README.md).

## 1. Ba nhịp: báo trước → bùng → tan

Mọi hiệu ứng một lần (one-shot) đi đủ ba nhịp, không nhịp nào bị bỏ:

| Nhịp | Thời lượng (30 fps) | Làm gì | Easing |
|---|---|---|---|
| Báo trước | 1-3 frame | gom lực: tia hút vào tâm, chấm sáng co lại, vòng đập vào rồi nóng lên, vết nứt lớn dần | vào nhanh |
| Bùng | 2-5 frame | hình chính bung ra hết cỡ, có vượt đà (overshoot) rồi lùi về | `out_back`, `out_expo` |
| Tan | phần còn lại | mỏng dần, nguội màu (trắng → vàng → cam), tách rời, trôi, mờ; **không bao giờ biến mất đột ngột** | `out_cubic`, `smooth` |

Nhanh lúc vào, chậm lúc ra. Chỗ quan trọng nhất (cú chạm, lúc vỡ) được giữ thêm 1-2 frame.

## 2. Bốn lớp, mỗi lớp một vai trò

1. **Chớp lõi**: trắng nóng, rất ngắn (2-4 frame), là nơi mắt bắt được cú chạm (`stepped_glow`, `starburst`).
2. **Hình chính**: hình đọc ra hiệu ứng là gì (vòng, xoắn, cánh hoa). To nhất, rõ nhất, đủ 4 bậc màu.
3. **Lớp phụ**: vòng sóng mảnh, bóng mờ chuyển động (motion echo), vệt sáng dọc trục. **Sinh ra từ hình chính**, không đứng riêng.
4. **Hạt**: tia lửa, mảnh vụn, hạt hơi. **Luôn phát ra từ một điểm có lý do** (rìa vòng, chỗ nứt, mũi cánh), bay theo quán tính có
   lực cản (`drag_pos`), không bao giờ rải ngẫu nhiên.

Các lớp phải liền mạch: lớp sau bắt đầu từ chỗ lớp trước đang ở (vòng sinh ra trên vệt sáng trục, mảnh vụn bắn ra từ đúng chỗ nứt,
tàn lửa rời từ mũi cánh).

## 3. Chiều sâu (2.5D)

- Vòng đứng ngang trục đòn được vẽ như vòng 3D nhìn 3/4 (`arc3d`): **nửa gần** dày, sáng, nằm trên lớp `front` (trước nhân vật);
  **nửa xa** mỏng, tối, nằm trên lớp `back` (sau nhân vật).
- Mọi vật có hướng sâu (dải xoắn, cánh hoa, mảnh vỡ) được sắp xếp xa trước gần sau, màu và độ đậm đổi theo độ gần.
- Độ dẹt `sq` (0.34-0.5) quyết định góc nhìn: dẹt quá thì mảnh trên/dưới mất hình (lỗi gặp ở bản vòng vỡ đầu).

## 4. Màu

- Bảng màu 5 bậc (`_core/palettes.py`): `rim` (viền tối cùng tông), `body`, `light`, `core`, `white`.
- Một hình vẽ thành nhiều lượt lồng nhau: viền → thân → sáng → lõi trắng mảnh bám mép trước. Không dùng gradient, không dither.
- Nguội màu theo tuổi: phần trắng mất trước, rồi vàng, còn lại cam rồi tan.
- Đổi màu = đổi bảng màu; không nhân bản hiệu ứng.

## 5. Biên độ và khung

- Chuyển động phải rộng: phình to gấp 2-3 lần, bay xa, vượt đà; tầng sau to và gần, tầng trước nhỏ và xa.
- Khung đủ rộng để không frame nào chạm mép (`force/shock`: 320x320, neo (64,160), 0,6 s, 19 frame). Nới khung thay vì thu nhỏ chuyển động.

## 6. Những lỗi đã gặp và cách sửa

| Lỗi | Sửa |
|---|---|
| Hình "khô", vô nghĩa (gai rải lung tung, vạch dọc như nan lồng) | mỗi hình có mục đích; vạch dòng khí thành vệt ngắn thon hai đầu chạy theo dòng |
| Tầng không rõ | mỗi tầng sinh cách nhau 1 frame, tầng xa/cũ mờ hơn tầng gần/mới |
| Mảnh vỡ trông thành vụn | giữ cung dày, mặt gãy phẳng có vạch sáng, mỗi mảnh tốc độ/xoay/rơi khác nhau |
| "Nổ" không ra nổ | thêm báo trước (tia hút vào), chớp lớn, vòng sóng nổ, tàn lửa từ mũi cánh, cánh rời khỏi tâm |
| Mảnh xoay ngược chiều nhau dồn thành cặp | xoay cùng chiều, cách đều |
| Đường nối giữa các đoạn | vẽ theo lượt (viền hết → thân hết → sáng), các đoạn gối nhau một chút |
| Lũy thừa của sin âm thành số phức | kẹp `max(0, sin(...)) ** p` |
| Nét mờ (alpha < 1) vẽ sau một hình làm thủng hình đó | `fxcore.Canvas` vẽ bằng ImageDraw, **ghi đè** điểm ảnh chứ không trộn; vẽ nét mờ lên một lớp riêng rồi `paste` (alpha_composite), như `_layer` trong `force/shock/shock.py` |
| Vòng chia thành nhiều đoạn ngắn trông như lá rời, không ra vòng | mỗi vòng 2-3 cung dài (1,5-2,5 rad), khe hẹp; vòng rộng hơn (`sq` 0,44) và nghiêng đầu về trước |

## 7. Quy trình kiểm tra trước khi đưa user xem

1. `python lib-fx/build.py <nhóm>/<họ>`, xem `_gallery/<nhóm>-<họ>.png` **và phóng to từng hàng**.
2. Xem **từng frame liên tiếp** ở các chỗ chuyển nhịp (gallery chỉ có frame cách 1, giật 1 frame sẽ lọt).
3. Kiểm tra không frame nào chạm mép khung (bbox alpha > 8 của từng frame).
4. Hiệu ứng mới để `draft`; chỉ đổi `approved` khi user duyệt.
5. Kiểm tra lặp lại và khô cứng theo §10 (frame dừng, khoảng cách, dáng qua 4-6 frame, số kiểu hình mỗi nhóm màu).

## 8. Hình tự do (organic): bước tiến từ bộ impact

Từ bộ `impact/*` (2026-11-06): thay vì ghép tròn, elip, tam giác, hình chính được dựng bằng **một mặt nạ gộp từ nhiều gai cong
thon, khối méo, giọt**, bo góc lõm bằng closing, tô màu theo **khoảng cách tới mép** (lõi dày thành trắng, mũi mảnh thành cam), tan
bằng **ăn mòn có nhiễu**, đặt trên một **nền tối trong suốt** thay cho viền. Khói là các cụm gộp lại, tô 3 tông theo hướng sáng.
Code: `_core/organic.py`. Nghiên cứu, nguồn, công thức và nhật ký lặp: [RESEARCH-organic-impact.md](RESEARCH-organic-impact.md).
Hiệu ứng mới nên dùng cách này cho hình chính; hình học cơ bản (`fxcore`) vẫn hợp cho vòng sạch, dải, xoắn.

## 9. Nhiều lớp: bộ `force/shock/inferno` (Hỏa xung tầng)

Làm theo ảnh tham khảo "scatter gun" (2026-11-06), để trả lời nhận xét "hiệu ứng cũ ít lớp nên nhìn chưa đã". Mười hai lớp, sau ra trước:
nửa xa của vòng (tối, lớp `back`) → vệt mờ của vòng (chỗ vừa đi qua) → vòng áp suất dẫn đầu (đỏ sẫm, mảnh, to nhất) → nón áp suất rất
mờ → vệt tốc độ mờ → vòng đỏ sẫm đứng quanh nắm đấm → tia lõi trắng nóng gộp với chớp gai thành **một** hình tự do → nửa gần của bốn tầng
vòng (nét bút thư pháp: giữa dày trắng vàng, hai đầu nhọn cam đỏ, móc cuộn vào trong, gai ngắn ở mép ngoài) → nét phụ mảnh chạy bên trong
mỗi vòng (cháy hết trước) → tia đạn có đầu mũi tên → tia lửa từ chớp → tàn lửa bay lên từ đầu các cung, mảnh vụn khi vòng vỡ.

Luật vật lý của sóng: **vòng sinh trước bay xa nhất và nở to nhất**; mỗi vòng vừa bay vừa nở, nguội màu (trắng → vàng → cam → đỏ), mờ dần
rồi vỡ thành móc và mảnh (ăn mòn có nhiễu). Ở mọi frame vòng gần nhỏ và nóng, vòng xa to và nhạt. Khung 640x400 @2x, neo (60,200), 0,78 s.
User duyệt (approved). Công thức đầy đủ (lớp, dòng thời gian, tham số, kỹ thuật, nhật ký lặp): [RECIPE-inferno.md](RECIPE-inferno.md).

Bộ thứ hai theo cùng cách, thêm lớp xám (khói, gió, bụi) và một hình nhân vật dựng tay (đầu hổ): `life/dash/tiger`,
User đánh giá **chưa đạt** (rework): lặp lại, khô cứng; **đã xoá 2026-11-09** (code, khung hình, công thức). Lý do và luật sửa ở §10.

## 10. Tránh lặp lại và khô cứng (bắt buộc cho mọi hiệu ứng nhiều phần tử)

User nhận xét `life/dash/tiger` (2026-11-06): **các lớp giống nhau quá, hiệu ứng có cảm giác trùng lặp, không linh động, khô cứng**. Nhiều
lớp không tự làm hiệu ứng đẹp; nhiều lớp **cùng một kiểu** chỉ nhân sự đơn điệu lên. Trong `tiger` lỗi nằm ở:

| Chỗ | Lỗi lặp |
|---|---|
| 22 lưỡi lửa | cùng một hình (chữ S), cách đều 19,5 px, cùng vòng đời (mọc → bốc lên → nguội → tan), chỉ khác vài số ngẫu nhiên |
| 8 cụm khói | cùng một khuôn (3 cụm tròn + 3 đuôi), cách đều, cùng tốc độ bay |
| 10 nét tốc độ, 14 mảnh gió | cùng cỡ, cùng nhịp sinh đều đặn |
| Cả hiệu ứng | mọi thứ đi cùng một hướng, cùng một tốc độ, cùng lúc, nên khung nào cũng giống khung trước |

Ngẫu nhiên nhỏ (±15% chiều dài, ±10° góc) **không** phải là đa dạng: mắt vẫn thấy một khuôn được nhân bản.

**Luật**

1. **Mỗi lớp một vai trò khác hẳn**, khác nhau ở ít nhất 3 trục: cỡ, hình, tốc độ, độ sắc của mép (sắc / mềm), độ đậm, thời điểm, hướng.
   Hai lớp giống nhau ở 3 trục trở lên thì gộp lại hoặc bỏ một.
2. **Nhịp lớn, vừa, nhỏ**: trong một nhóm phần tử luôn có 1-2 phần tử **chính** (to, rõ, khác hình), vài phần tử vừa, nhiều phần tử nhỏ.
   Tỉ lệ cỡ chính : vừa : nhỏ khoảng 3 : 1,5 : 1, không phải mọi thứ cùng một cỡ.
3. **Bộ hình**: mỗi nhóm màu dùng ít nhất 3 kiểu hình (lưỡi dài, móc cuộn, giọt, mảnh vỡ góc cạnh, sợi mảnh, đốm), không nhân một
   kiểu cho cả nhóm.
4. **Khoảng cách theo cụm**, không cách đều: cụm dày, khoảng trống, phần tử lẻ. Khoảng trống cũng là thiết kế (chỗ cho mắt nghỉ).
5. **Mỗi phần tử có số phận riêng**: cái tách đôi, cái cuộn lại, cái bị kéo dài rồi đứt, cái co lại thành giọt, cái bị gió thổi lệch.
   Không dùng một vòng đời chung cho cả nhóm.
6. **Lệch pha, chồng nhịp**: các phần không bắt đầu, đạt đỉnh và kết thúc cùng lúc; mỗi nhóm có easing riêng; có chuyển động theo sau
   (follow-through), trễ, vượt đà ở những chỗ khác nhau.
7. **Bất đối xứng và hướng phụ**: ngoài hướng chính phải có lực phụ (bốc lên, xoáy, bị hút ngược, rơi), để khung hình không chỉ là
   "mọi thứ trôi về sau".
8. **Mỗi pha có dáng riêng**: báo trước, bùng, đỉnh, vỡ, tan phải có hình bao (silhouette) khác hẳn nhau; nếu dáng ở frame 6 và frame 12
   gần như nhau thì hiệu ứng đang đứng yên.
9. **Theo ảnh từng bước**: khi user có ảnh tham khảo chia bước (key pose), dựng đúng từng key pose trước, rồi mới làm chuyển tiếp giữa chúng.
10. **Mỗi phần tử là một hình độc lập** khi nó phải sống riêng (từng ngọn lửa dưới đất có chiều cao, độ lắc, nhịp chập chờn, đời và
    số phận riêng). Chỉ gộp chung một hình khi các phần là MỘT vật (một tia tóe, một vòng): gộp để không có đường nối, tách để sinh động.
11. **Mỗi lớp một bộ màu**: lớp sau tối (tím đậm), lớp giữa (xanh), lớp trước sáng (cyan); phần tóe ra có dải màu sáng nhất riêng của nó.
    Màu kể chiều sâu và làm nổi phần tóe, không phải mọi thứ chung một dải.
12. **Chỉ vẽ hiệu ứng**: không vẽ thân mục tiêu hay nhân vật (kể cả dạng bóng ma); điểm trúng chỉ là một vị trí.
13. **Hình nhân vật hiệu ứng phải đúng chất liệu**: một linh hồn lửa là một ngọn lửa (lưỡi lửa có bụng, đầu cong, vừa trôi về sau vừa
    bốc lên), không phải một quả cầu có đuôi. Lưỡi lửa dùng `tongue()` (bụng tròn, đuôi cong), gai dùng `thorn()`.

**Kiểm tra trước khi đưa user xem** (thêm vào §7)

- Dừng ở một frame: có thấy hình nào giống hệt hình bên cạnh (chỉ khác vị trí) không? Có thì đổi hình, cỡ hoặc số phận của nó.
- Nhìn dọc đường đi: khoảng cách giữa các phần có đều như hàng rào không?
- Đặt frame cách nhau 4-6 frame cạnh nhau: dáng tổng thể có thay đổi rõ không?
- Đếm kiểu hình trong mỗi nhóm màu: dưới 3 là đơn điệu.

## 11. Xuất hồn kích (`magic/spirit/soulstrike`): rework, giữ phần linh hồn nhỏ

Sau 4 vòng sửa, user đánh giá: **linh hồn nhỏ và cách chúng chuyển động đạt**, còn linh hồn lớn, các cú tóe và lửa dưới đất chưa đẹp.
Phần đạt được ghi trong [RECIPE-soul-spirits.md](RECIPE-soul-spirits.md). Dựng lại hiệu ứng từ GIF tham khảo: [REFERENCE-GIF.md](REFERENCE-GIF.md).

## 12. Nhiều tầng màu phẳng: một trường, nhiều ngưỡng

Từ phân tích GIF xoáy chém (2026-11-07): hiệu ứng stylized đẹp và liền mạch vì mọi tầng màu của một vật được cắt từ **một** trường xám
liên tục bằng các ngưỡng cứng, không phải vẽ từng mảng riêng, và không có gradient. Luật và công thức: [SHAPE-RULES.md](SHAPE-RULES.md);
code `_core/fieldfx.py`; ví dụ `melee/blade/blade.py`.

