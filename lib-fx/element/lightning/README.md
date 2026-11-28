# Nguyên tố / Sét

Tia sét gấp khúc, điện nhảy, chớp.

Ví dụ sẽ có: sét đánh, sét chuyền, giật điện.

Chia theo chức năng (tạo thư mục con khi có hiệu ứng đầu tiên):
- `cast/`: tụ phép ở người dùng: vòng phép dưới chân, ánh sáng gom vào tay, trước khi phóng
- `projectile/`: vật bay: quả cầu, mũi tên phép, tia; gồm đầu đạn + vệt đuôi
- `impact/`: lúc trúng mục tiêu: nổ nhỏ, tóe, chớp
- `aoe/`: vùng ảnh hưởng trên mặt đất: vòng, cột, mưa, bãi
- `aura/`: hào quang lặp quanh người hoặc vật: cháy âm ỉ, khí bao quanh
- `status/`: dấu hiệu trạng thái gắn trên mục tiêu: bị đốt, đóng băng, nhiễm độc...

Chưa có hiệu ứng nào trong thư viện. **Phong cách sét đã duyệt** (user 2026-11-28): sét lấy từ bản remake `lightning-2` (khối phẳng màu dịu,
quầng mềm, khung tia đen, nhịp vẽ tay) đặt quanh nhân vật: `python lib-fx/_tools/vectorfx.py gen-lightning NAME`, kết quả
`lib-fx/_core/results/vector-showcase/generated/gen-lightning-<wrap|arm|raise|dual|slam|thrust>-blue/` (6 dáng × 5 màu, đã duyệt), công thức đầy đủ ở
`lib-fx/_core/formulas/rules/vfx/lightning/README.md` §7.
Hiệu ứng sét mới cho nhân vật làm theo cách đó. Xem `lib-fx/GUIDE.md` và `lib-fx/README.md` để thêm vào thư viện.
