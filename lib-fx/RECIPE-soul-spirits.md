# Công thức: linh hồn nhỏ (trong `magic/spirit/soulstrike`)

Phần **user đánh giá ổn** (2026-11-06) của Xuất hồn kích: các linh hồn nhỏ (và hai linh hồn vừa vẽ cùng kiểu), **cả hình lẫn cách
chúng chuyển động**. Các phần khác của hiệu ứng (linh hồn lớn, các cú tóe, lửa dưới đất) chưa đạt, hiệu ứng để `rework`. Ghi lại ở đây
để dùng lại cho mọi hiệu ứng có "đốm lửa / tinh linh bay": ma trơi, đom đóm phép, linh hồn, tia dẫn đường.

Code: `magic/spirit/spirit.py`: `SPIRITS`, `hover`, `_pos`, `_heading`, `_tail_time`, `_tail_paint`, `_spirit` (nhánh không phải `hero`).
Bảng màu: `palettes.SPIRIT`.

## 1. Hình: một đầu tô phẳng 3 tông, một cái đuôi trong mờ

| Phần | Cách dựng | Màu |
|---|---|---|
| Đầu | `_ellipse` kéo dài theo hướng bay (squash & stretch theo tốc độ), thêm đuôi giọt nước (`thorn` ngược hướng bay, dài theo `tear`), 0-2 ngọn lửa nhỏ (`flame`) ở phía trên sau đầu, một "cổ" (`thorn`) nối vào đuôi | `organic.shade`: sáng phía trên (`pale`), thân `cyan`, bụng tối (`deep`); ánh sáng từ trên (`light=(0.15, 0.98)`) |
| Chấm nóng | một elip trắng nhỏ lệch về phía trước (chỉ 2 linh hồn vừa; linh hồn nhỏ không có, để khỏi giống "mắt") | `white` |
| Đuôi | các vị trí cũ của đầu dọc đường bay, rộng ở đầu, thon về cuối; một sóng chạy dọc đuôi | dải màu theo chiều dài: `cyan` → `blue` → `violet` → `lilac`, độ đậm 1,0 → 0,3 |

**Đuôi vẽ bằng một mặt nạ chỉ số** (`_tail_paint`): mỗi đoạn được đóng dấu số thứ tự của nó (đoạn gần đầu vẽ sau nên thắng), rồi số
được đổi ra màu và độ đậm, ghép một lần. Không có đường nối giữa các đoạn, đuôi tự cắt qua chính nó (xoắn) cũng không thủng.

**Chiều dài đuôi đo theo đường đi** (`_tail_time`): lùi thời gian cho tới khi đuôi đủ `TAIL_PX` px dọc đường bay (ít nhất `tail` giây).
Linh hồn đang lơ lửng chậm vẫn kéo một cái đuôi dài lắc lư, không co lại thành cục.

**Hướng và tốc độ làm mượt** (`_heading`, đo trên 40 ms): đầu không bị lật 180° trong một frame khi vòng ngược hay bay vòng tròn. Khi
đang lớn trên người (trước lúc phóng), đầu hướng thẳng lên.

## 2. Chuyển động: mỗi linh hồn một "tính cách"

Đường bay là một đường Catmull-Rom qua các điểm đặt tay (`path`, đơn vị px tại `s = 1`, ngực người tung chiêu ở (0, 0)), đi theo một
hàm thời gian riêng (`ease`). Ba pha:

1. **Sinh ra trên người** (`spawn` → `launch`): lớn từ 0 lên đủ cỡ có vượt đà (`out_back`), run nhẹ (`3·sin(40t)`), nhích lên 6 px.
2. **Bung ra rồi lơ lửng** (`hover(f, out, hold, drift, pw)`): tới điểm tỏa (`f` = vị trí của điểm đó trên đường) trong `out` phần đời,
   nhanh rồi chậm (`out_cubic`), trôi nhẹ `drift` trong `hold`, rồi tăng tốc lao vào đích (`v^pw`).
3. **Lao tới và kết cục riêng** (`fate`).

| Linh hồn | Cỡ (r) | Đầu | Đuôi | Đường bay | Nhịp | Kết cục |
|---|---|---|---|---|---|---|
| skim (vừa) | 14 | 2 ngọn lửa, `tear` 0,3, chấm nóng | 1 sợi, rách lỗ chỗ | lướt thấp qua đích, vòng ngược lại | `hover(2/7, 0.26, 0.1, 0.03, 1.3)` | đâm vào thân từ phía sau |
| corkscrew (vừa) | 13 | 2 ngọn lửa, `tear` 0,2, chấm nóng | **2 sợi** lệch pha | bay lên, xoắn một vòng giữa đường | `hover(1/8, 0.22, 0.08, 0.02, 1.15)` | đáp sau gáy |
| zigzag (nhỏ) | 9 | giọt nước trơn (`tear` 0,95) | ngắn, sóng nhanh (5 Hz) | zigzag sát đất | đều (`u`) | chạm đất trước đích |
| lazy (nhỏ) | 8,5 | giọt nước, không lửa | dài, sóng chậm (1,1 Hz) | bay ngược lên sau lưng | `sin(u·π/2)` | **tan giữa chừng** (co lại, thành đốm sáng), không tới đích |
| orbit (nhỏ) | 9 | giọt nước, 1 ngọn lửa | ngắn | **vòng quanh người tung chiêu** rồi lao đi; nửa vòng phía xa vẽ sau lưng (`back`) | `u^1.2` | tới sau cùng |

Vì sao nó ổn (đúng DESIGN.md §10): mỗi con khác nhau ở cỡ, hình đầu, kiểu đuôi, đường bay, nhịp và kết cục; chúng sinh lệch nhau
(0-0,1 s), tới đích lệch nhau và tăng dần nhịp; luôn có lực ngược hướng chính (vòng ngược, bay lên sau lưng, bay vòng).

## 3. Thông số dễ chỉnh

- Sóng đuôi `wig = (biên độ px, Hz)`: nhỏ và nhanh = lo lắng, lớn và chậm = lững lờ.
- `tailw` (bề rộng đuôi so với đầu), `strands` (1 hay 2 sợi), `TAIL_PX` (độ dài đuôi).
- `tear` (0 tròn → 1 giọt nước dài), `flicks` (0-2 ngọn lửa trên đầu).
- Bảng màu: mọi bảng 5 bậc đều dùng được (các bậc phụ tự suy ra), đuôi đổi theo.

## 4. Chưa đạt (đừng lấy làm mẫu)

Linh hồn lớn (hình cầu lửa/ngọn lửa lồng nhau), các cú tóe trên mục tiêu, vòng gai dưới đất, lửa đứng dưới đất: user đánh giá chưa đẹp
(2026-11-06, 4 vòng sửa). Xem nhật ký trong lịch sử git của `magic/spirit/spirit.py`.
