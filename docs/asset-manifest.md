# Asset manifest: checklist của từng nhân vật

Mỗi nhân vật có một bảng **Asset manifest** trong `out/<class>/<id>/brief.md`. Đây là danh sách mọi thứ nhân
vật cần (ảnh tĩnh, clip animation, hiệu ứng), mỗi dòng có trạng thái. Hai skill dùng chung bảng này:
`fal-image` làm các dòng ảnh tĩnh và hiệu ứng, `video-sprite` làm các dòng clip. Nhìn bảng là biết đã xong
gì, còn thiếu gì, bước tiếp theo là gì.

Quy tắc đầy đủ (bảng nào sinh ra dòng nào): `.claude/skills/fal-image/format.md` §8 và §9.

## Ví dụ: hero cận chiến, 2 skill

```
## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v03 | chốt 2026-10-18 |
| icon | fal-image | ảnh tĩnh | ⏳ | chờ duyệt |
| pose_skill_gale | fal-image | ảnh tĩnh | ❌ | đỉnh chiêu lốc xoáy |
| pose_skill_dash | fal-image | ảnh tĩnh | ❌ | đỉnh chiêu lướt chém |
| run_side | video-sprite | loop | ❌ | |
| attack_side | video-sprite | one-shot | ❌ | |
| death_side | video-sprite | one-shot | ❌ | |
| respawn_side | video-sprite | one-shot | ❌ | |
| levelup_side | video-sprite | one-shot | ❌ | |
| skill_gale_side | video-sprite | one-shot | ❌ | từ master tới pose |
| skill_dash_side | video-sprite | one-shot | ❌ | từ master tới pose |
| fx_gale | fal-image vfx | hiệu ứng | ❌ | lốc xoáy, asset riêng |
Ước tính: 5 ảnh x ~0.014 + 7 clip x ~0.08 ≈ USD 0.63
```

Trạng thái:
| Dấu | Nghĩa |
|---|---|
| ✅ v03 / ✅ t02 | xong và đã duyệt (version ảnh / take video) |
| ⏳ | đã làm, chờ bạn duyệt |
| ❌ | chưa làm |
| ⏭ | để sau hoặc bỏ qua (lý do ở Ghi chú) |

## Mỗi class có những dòng nào

| Dòng | Hero | Quân ta | Quái đi bộ | Quái bay | Boss |
|---|---|---|---|---|---|
| master (= idle, nhìn ngang) | có | có | có | có, đang bay | có |
| icon | có | có | có | có | có |
| view_front, view_back | - | - | có | có | có |
| projectile (đạn) | nếu đánh xa | nếu đánh xa | nếu đánh xa | nếu đánh xa | nếu đánh xa |
| run_side | có | có | - | - | - |
| walk_side, walk_down, walk_up | - | - | có | fly_* thay thế | có |
| idle_fly (lơ lửng) | - | - | - | có | - |
| attack_side | cận chiến | cận chiến | cận chiến | - | cận chiến |
| shoot_side | đánh xa | đánh xa | đánh xa | đánh xa | đánh xa |
| death_side | có | có | có | có | có |
| respawn_side, levelup_side | có | - | - | - | - |
| raise_side (trồi lên) | - | được triệu hồi | được triệu hồi | - | - |
| thorn_side, thorn_free_side | - | - | ⏭ để sau | - | - |
| mỗi skill: pose + clip + fx | 2-3 skill | 0-2 | hiếm | hiếm | 0-3 |

Vì sao ít hướng: game chỉ vẽ nhiều hướng cho việc di chuyển (quái, boss: ngang, lên, xuống). Mọi trạng thái
khác chỉ vẽ nhìn ngang rồi lật trái/phải. Hero và lính chỉ có một hình chạy ngang.

Mỗi skill có 3 phần: **pose** (ảnh đỉnh chiêu), **clip thân** (từ master tới pose) và **fx** (hiệu ứng lớn
như mưa lửa, lốc xoáy, sét: một asset riêng, game đặt chồng lên). Đòn đánh thường không cần pose.

## Mở rộng sau này

Thêm hướng, trạng thái hay skill mới là thêm dòng vào manifest. Size, style và điểm neo không đổi.
| Muốn | Thêm dòng |
|---|---|
| Đòn đánh thứ 2 cho đỡ lặp | attack2_side |
| Boss chết 2 pha | death_end_side |
| Biến hình (vd. thành gấu) | master_bear + bộ dòng của dạng mới + to_bear_side, to_base_side |
| Đi bộ rồi bay | bộ fly_* + take_off_* và land_* cho 3 hướng |
| Bắn lên/xuống | shoot_up, shoot_down |

## Xem tiến độ

Hỏi trong chat: **"trạng thái tới đâu rồi"** hoặc `/fal-image --status`. Kết quả:
```
| Nhân vật | Class | Xong | Chờ duyệt | Còn lại | Để sau | Bước tiếp |
|---|---|---|---|---|---|---|
| goblin | enemies | 4/9 | 0 | 5 | 1 | walk_side, walk_down, walk_up ... |
| wind_dancer | heroes | 1/12 | 1 | 10 | 0 | duyệt: icon |
```
Xem một nhân vật: **"xem manifest của wind_dancer"** hoặc `/fal-image --status wind_dancer`.
Chạy tay: `python scripts/asset_status.py` (tất cả) hoặc `python scripts/asset_status.py wind_dancer`.

## Cách yêu cầu

| Kiểu | Ví dụ |
|---|---|
| Đầy đủ, không bị hỏi | `/fal-image --hero --tier M --role melee nữ kiếm sĩ gió; skill: lốc xoáy - xoay người tạo lốc (vfx); skill: lướt chém - lướt tới chém` |
| Ngắn, skill hỏi phần thiếu | `/fal-image hero nữ kiếm sĩ gió` |
| Gợi ý thiết kế | `/fal-image hero nữ dùng gió --creative` |
| Xem ví dụ | `/fal-image --example --hero` |
| Làm animation | "làm animation cho wind_dancer": video-sprite làm các dòng ❌ của manifest, báo số clip và chi phí trước |
