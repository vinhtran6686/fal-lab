# T3 (Sonnet): Rig Tuner v2

Trạng thái: TODO

## Mục tiêu
Một trang HTML tự chứa để **user tự đặt và sửa khớp** của một rig rồi xem thử khớp xoay ngay trên trang, không cần Python. Lý do: toạ độ khớp do AI đặt chỉ gần đúng, và user đã chỉ ra khuỷu tay của lion đặt sai chỗ (ở mép găng).

## Đọc trước
- `docs/tasks/README.md` mục "Quy tắc chung".
- `docs/puppet-kit.md` mục "Khái niệm" (định dạng `rig.json`).
- `docs/puppet-kit-next.md` §3 (bộ xương chuẩn 17 xương) và §4.
- `scripts/puppet_kit/rig_tuner.html` (bản v1, 70 dòng: chỉ kéo điểm có sẵn; chưa từng được mở thử).
- Một rig thật để thử: `out/heroes/lion_brawler/source/rig/rig.json`, ảnh `out/heroes/lion_brawler/source/design/master_v01.png` và `out/heroes/lion_brawler/source/rig/plate_v01.png`.
- Trong `scripts/puppet_kit/core.py`: `Rig.pose` (thứ tự ma trận: `T(pivot + t) · R(rot) · SH(shx) · S(sx, sy) · T(−pivot)`, thế giới = cha · cục bộ; `rot` dương = thuận chiều kim đồng hồ trên màn hình, y hướng xuống).

## Được sửa
- `scripts/puppet_kit/rig_tuner.html` (viết lại)
- File task này và dòng T3 trong `docs/tasks/README.md`
Không sửa file Python nào. Không đổi định dạng `rig.json`: file tải về phải nạp được bằng `python scripts/puppet.py check`.

## Yêu cầu chức năng
1. **Nạp**: nhiều ảnh nguồn (mỗi ảnh gán cho một khoá trong `sources`, ví dụ `master`, `plate`) và một `rig.json`. Không có `rig.json` thì bắt đầu rỗng. Chọn ảnh nền đang xem bằng danh sách nguồn.
2. **Xương**: thêm, đổi tên, xoá, đổi cha (không cho tạo vòng); kéo `pivot` trên ảnh. Nút "Biped chuẩn" thêm 17 xương của `puppet-kit-next.md` §3 ở vị trí mặc định theo tỉ lệ khung hình bóng (ước lượng từ bbox của ảnh), để user chỉ việc kéo.
3. **Lớp (part)**: thêm, xoá, đổi thứ tự vẽ (lên/xuống); chọn `source`, `bone`; vẽ đa giác (nhấp để thêm điểm, kéo điểm, nhấp đúp lên cạnh để chèn điểm, nhấp phải để xoá điểm). Lớp kiểu `{"rest": true}` và `{"colour": ...}` giữ nguyên, chỉ hiển thị, không sửa hình.
4. **Socket**, `ground`, `unit`: kéo điểm, nhập số.
5. **Xem thử (quan trọng nhất)**: chế độ "Thử khớp": mỗi xương có thanh trượt `rot` (−180..180). Trang vẽ lại nhân vật bằng canvas 2D: mỗi lớp đa giác được cắt (`clip`) từ ảnh nguồn của nó và vẽ với ma trận thế giới của xương (đúng thứ tự ma trận ở trên, cha trước con), theo thứ tự lớp. Lớp `rest` vẽ nguyên ảnh nguồn trừ vùng các đa giác cùng nguồn. Nút "Về 0" đặt mọi thanh trượt về 0. Không cần IK, deform, fill.
6. **Xuất**: nút "Tải rig.json"; vì trang chạy trong artifact (link `download` bị chặn với người xem), **phải có thêm** ô văn bản chứa JSON và nút "Chép" (clipboard, có bắt lỗi và tự chọn văn bản khi bị từ chối).
7. Hoàn tác (Ctrl+Z, ít nhất 30 bước) cho mọi thao tác sửa.

## Yêu cầu trang
- Một file, không thư viện ngoài, không gọi mạng. Văn bản giao diện tiếng Việt.
- Theo hợp đồng trang artifact: không có `<!doctype>`, `<html>`, `<head>`, `<body>`; có `<title>Rig Tuner</title>`; màu qua biến CSS trên `:root` với khối tối cho `prefers-color-scheme: dark` (dạng `:root:not([data-theme="light"])`) và `:root[data-theme="dark"]`; `body` có nền rõ ràng; lề hai bên `max(16px, env(safe-area-inset-left/right, 0px))`; không cuộn ngang ở bề rộng điện thoại (canvas nằm trong vùng `overflow: auto`).
- Mọi điều khiển có `id` ổn định; có trạng thái focus thấy được.

## Nghiệm thu (tự kiểm bằng Playwright có sẵn: `require('playwright')`, `chromium.launch()`)
1. Mở file, nạp `rig.json` và hai ảnh của lion qua `setInputFiles`: canvas hiện ảnh và 8 xương, 7 lớp.
2. Bật "Thử khớp", đặt `near_upper` = −60: chụp màn hình, cánh tay gần phải vung ra trước, găng đi theo (xương con).
3. Kéo pivot `near_fore` 40 px lên trên, tải/chép JSON: `python scripts/puppet.py check <file vừa lưu>` chạy không lỗi (lưu tạm vào `out/heroes/lion_brawler/.work/`, không ghi đè rig thật).
4. Không có lỗi console.
Ghi vào Kết quả: 2 ảnh chụp đã xem (mô tả ngắn), kết quả từng bước.

## Ngoài phạm vi
Sửa `rig.json` thật của nhân vật, IK, deform, animation, xuất bản artifact (Fable sẽ xuất bản sau khi duyệt).

## Kết quả
(model điền)
