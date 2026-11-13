# Cách người làm VFX chuyên nghiệp dựng một hiệu ứng (bản nháp phương pháp, chưa phải luật)

Mục đích: hiểu **cách làm**, không học thuộc từng loại hiệu ứng. Hai mẫu `flame-burst` và `lightning` chỉ là **bài kiểm tra** cho phương pháp này.
Trạng thái: bản nháp của người lập kế hoạch. Sau khi R1-R3 có số đo và người dùng duyệt, nội dung đúng mới được chuyển vào `lib-fx/_core/formulas/rules/`.
Ký hiệu: **[nguồn]** = có trong tài liệu tìm được (danh sách cuối file); **[đo]** = repo đã đo trên mẫu 9-10/10 (`rules/01`, `02`, `05`);
**[suy luận]** = suy ra của người lập kế hoạch, cần R1-R3 xác nhận.

## 1. Thứ tự làm việc của hoạ sĩ FX (và bước tương ứng của chúng ta)

| Bước của hoạ sĩ | Họ quyết định gì ở bước này | Bước tương ứng trong repo | Hiện trạng |
|---|---|---|---|
| 1. Mục đích | hiệu ứng nói gì với người chơi: ai gây ra, mạnh cỡ nào, trúng ở đâu, kéo dài bao lâu. Rõ ràng cho gameplay đứng trên đẹp **[nguồn: style guide VFX của một game MOBA lớn, mục tiêu số một là "visual clarity"]** | `Effect(space, weight, tags, desc)` | có, nhưng chưa có thang cường độ chung (xem góp ý B của người dùng: nặng và chí mạng chưa khác nhau) |
| 2. Năng lượng và đường đi | lực từ đâu tới, đi theo đường nào, mạnh nhất ở đâu, tiêu tan ra sao **[nguồn: Gilland: chương "energy, action path, timing"]** | `Space` (a → b, đường cong) | có đường a → b; **thiếu "đường năng lượng" cho từng lớp** (lửa rút về nguồn, khói trôi đi) **[suy luận]** |
| 3. Nhịp trước, hình sau | chia thời gian thành pha: báo trước → bùng → đỉnh → tan; khoảng cách giữa các hình vẽ **không đều** (đều thì máy móc) **[nguồn: VFX Apprentice timing; Willoughbys: "2D-first drawings provided the abstract timing and shape-language"]** | `Life(start, attack, hold, release)` | có 4 pha cho mỗi lớp; **thiếu pha báo trước ở cấp hiệu ứng** và thiếu khoảng lặng **[suy luận, H1]** |
| 4. Hình bóng thô | vẽ nhanh khối lớn bằng một màu, kiểm hình bóng: to / vừa / nhỏ, cong S và C, không song song, không đối xứng **[nguồn: thiết kế hình sớm để giảm công làm sạch]** **[đo: thứ bậc mảnh 1 / 0,4-0,8 / < 0,25]** | "thiết kế hình ở đỉnh" trong mỗi kind (`fxkit/layers/*.py`) | có; kiểm bằng mắt, chưa có phép đo hình bóng tự động |
| 5. Hình chính, hình phụ, hình giữa | key (hình chính) được duyệt trước, rồi breakdown, cuối cùng mới in-between **[nguồn: quy trình làm sạch: key → breakdown → in-between]** | hàm theo thời gian trong kind | chúng ta nội suy bằng công thức: **chưa có khái niệm "key pose được duyệt trước"** |
| 6. Làm sạch nét | nét cong liền, ít điểm neo, mũi nhọn thật **[đo: ~26 px viền / điểm neo, tay nắm ≈ 1/3 dây cung]** | `Ink` | **thiếu** (task T1 của `fxkit-feedback-01`) |
| 7. Màu và độ sáng | giá trị sáng tối quyết định thứ bậc nhìn; màu, độ bão hoà, chuyển màu và quầng sáng thể hiện cường độ **[nguồn: color, value, saturation, shape language, visual hierarchy, timing là 6 kỹ năng lõi; "color combinations, transitions, glow to show intensity"]** **[đo: 3-4 tông, bước sáng 50-65]** | `Ramp.tone`, glow | có; chưa kiểm ảnh xám (thứ bậc giá trị) |
| 8. Ghép lớp và ánh sáng | lớp sau / trước nhân vật, quầng sáng, khung chớp, phản chiếu | `z`, `Effect.glow` | có |
| 9. Xem ở cỡ thật, trong ngữ cảnh | xem trên nền game, cạnh nhân vật, ở tốc độ thật; sửa cái mắt vấp | `preview_game.gif`, ghép lên thân nhân vật | có công cụ; chưa là bước bắt buộc trước khi duyệt |

## 2. Sáu thứ quyết định chất lượng, áp dụng cho MỌI loại hiệu ứng

1. **Một ý, một hướng nhìn.** Mỗi hiệu ứng có một điểm nhấn; mọi lớp khác phục vụ nó và yên hơn nó (thứ bậc nhìn). **[nguồn]**
2. **Nhịp không đều.** Vào nhanh, ra chậm; có khung giữ, khung chớp, khoảng lặng; lớp nhanh chết trước, lớp chậm ở lại. **[nguồn][đo]**
3. **Hình bóng đọc được khi tô một màu.** Nếu tô đen toàn bộ mà không đoán ra là gì thì chi tiết bên trong không cứu được. **[nguồn][suy luận]**
4. **Giá trị sáng tối trước, màu sau.** Chuyển sang xám vẫn phải thấy rõ chỗ nóng nhất và thứ bậc lớp. **[nguồn]**
5. **Mỗi phần tử một số phận.** Không hai mảnh nào sinh, đi, chết giống nhau; biến thiên có thứ bậc. **[đo]**
6. **Chất liệu qua cách chuyển động và cách tan**, không qua hoa văn: lửa bốc lên và rút, khói trôi và rách, điện giật và tắt, kim loại để lại nét thẳng, chất lỏng kéo sợi và nhỏ giọt. **[suy luận, cần H2-H8]**

## 3. Phương pháp này đổi gì trong cách chúng ta làm (đề xuất, chờ duyệt)

- **Bảng thiết kế trước khi code** cho mỗi hiệu ứng mới (một bảng ngắn, 6 dòng): mục đích và cường độ; đường năng lượng; bảng nhịp theo khung; hình bóng ở 3 khung chính
  (báo trước, đỉnh, tan); thang giá trị (xám); chất liệu = cách chuyển động + cách tan.
- **Duyệt theo tầng**: (1) nhịp bằng hình khối một màu → (2) hình bóng 3 khung chính → (3) nét sạch và tông màu → (4) quầng và ghép lên nhân vật.
  Tầng trước chưa đạt thì không làm tầng sau. Hiện tại ta làm cả bốn cùng lúc nên lỗi nhịp và lỗi hình bị che bởi màu và quầng.
- **Phép đo thêm cho cổng chất lượng**: đọc được ở ảnh xám; hình bóng (tỉ lệ to / vừa / nhỏ); khoảng cách khung không đều; có pha báo trước khi `weight` nặng.
- **"Chất liệu" là dữ liệu của kind**: mỗi kind khai báo cách chuyển động và cách tan của chất liệu nó vẽ, thay vì mỗi hiệu ứng tự chọn tham số mòn.

## 4. Hai mẫu kiểm tra phương pháp ở đâu
`flame-burst`: kiểm bước 2 (đường năng lượng: lửa rút, khói trôi), bước 3 (pha báo trước và khoảng lặng), mục 2.6 (hai chất liệu trong một hiệu ứng).
`lightning`: kiểm bước 3 (nhịp cực ngắn, khung chớp), bước 4 (hình bóng nét mảnh, thân + nhánh), mục 2.5 (chuỗi tia không lặp).
R3 xuất số đo theo đúng các mục này, không theo "luật riêng của lửa" hay "luật riêng của sét".

## Nguồn
- Riot Games, League of Legends VFX Style Guide (bài công bố): https://nexus.leagueoflegends.com/en-us/2017/10/dev-leagues-vfx-style-guide/
- VFX Apprentice, 10 Design Tips from the League of Legends VFX Style Guide: https://www.vfxapprentice.com/blog/10-league-of-legends-vfx-design-tips
- VFX Apprentice, The Must-Know Artistic Principles of Video Game VFX: https://www.vfxapprentice.com/blog/five-artistic-principles-gaming-vfx
- VFX Apprentice, The Soul of Effects: What is Timing in VFX?: https://www.vfxapprentice.com/blog/the-soul-of-effects-what-is-timing-in-vfx
- VFX Apprentice, Animating Small 2D FX: https://www.vfxapprentice.com/courses/animating-small-2d-fx
- GDC, Visual Effects Bootcamp: Artistic Principles of VFX: https://www.gdcvault.com/play/1024439/Visual-Effects-Bootcamp-Artistic-Principles
- 80.lv, Constructing VFX Worthy of League of Legends: https://80.lv/articles/constructing-vfx-worthy-of-league-of-legends/
- J. Gilland, Elemental Magic, Volume I: https://www.routledge.com/Elemental-Magic-Volume-I-The-Art-of-Special-Effects-Animation-1st-Edition/Gilland/p/book/9780240811635
- Befores & Afters, How 'The Willoughbys' used 2D effects in a 3D world: https://beforesandafters.com/2020/04/22/how-the-willoughbys-used-2d-effects-in-a-3d-world
- Disney Animation, Hand-drawn animation process: https://disneyanimation.com/process/hand-drawn-animation/
Lưu ý: mình chỉ đọc được phần tóm tắt của kết quả tìm kiếm, chưa đọc toàn văn các tài liệu này; các dòng **[nguồn]** là ý chính được trích trong tóm tắt.
