# Example requests (printed by `/fal-image --example [--<class>]`)

Print only the section the flag asks for (no flag: the overview table and the first example of each class).
Every example names its class and tier, so it runs without the size question. Users copy one, then change the
content. Sizes and canvases come from `format.md` §7; never name a commercial game or its characters here.

## Overview
| Flag | Class | Tiers (default *) | Canvas @1x |
|---|---|---|---|
| `--hero` | Hero | S, M*, L | 104x92, 156x140, 220x196 |
| `--ally` | Quân phe ta | S*, M, L | 92x80, 136x120, 192x168 |
| `--enemy-small` | Quái nhỏ | XS* | 56x48 |
| `--enemy` | Quái thường | S*, M | 92x80, 136x120 |
| `--enemy-large` | Quái lớn | L* | 192x168 |
| `--boss` | Boss | XL, XXL* | 308x204, 436x292 |

## --creative (any class)
Give only the idea; the skill proposes 3 concepts and asks shape, weapon, palette and size in one question box.
- `/fal-image hero nữ có biệt tài sử dụng gió --creative`
- `/fal-image quái rừng nhỏ biết ẩn mình --creative`
- `/fal-image --boss chúa tể dưới lòng đất --creative`

## --hero
- **S (40 px)**: `/fal-image --hero --tier S nữ pháp sư băng nhỏ nhắn, áo choàng xanh nhạt có mũ trùm, cầm quyền trượng pha lê tay phải; attack: phóng một mảnh băng ngắn về phía trước; death: ngã quỵ, quyền trượng rơi`
- **S (40 px)**: `/fal-image --hero --tier S cung thủ elf thanh mảnh, áo xanh lá, cung gỗ dài tay trái, tóc buộc đuôi ngựa`
- **M (60 px)**: `/fal-image --hero --tier M hiệp sĩ thánh giáp bạc viền vàng, khiên tròn tay trái, kiếm dài tay phải, áo choàng đỏ; attack: chém chéo từ trên xuống`
- **M (60 px)**: `/fal-image --hero --tier M võ tăng hỏa ngục da nâu, đầu trọc có hình xăm phong ấn đỏ, cà sa cam cháy xém, côn sắt có vòng; idle đứng một chân như thiền`
- **L (84 px)**: `/fal-image --hero --tier L robot chiến đấu hơi nước to lớn, thân đồng thau, một tay là lưỡi cưa tròn, ống khói sau lưng; attack: vung cưa ngang trước mặt`
- **L (84 px)**: `/fal-image --hero --tier L golem đá rêu khổng lồ, vai u to, nắm đấm đá, mắt phát sáng xanh lá; attack: đập hai tay xuống đất tại chỗ`

## --ally
- **S (40 px)**: `/fal-image --ally --tier S lính bộ binh mặc giáp da, khiên gỗ tròn, kiếm ngắn, áo khoác xanh dương`
- **S (40 px)**: `/fal-image --ally --tier S lính cung trường, mũ sắt nhỏ, cung dài, ống tên sau lưng; attack: bắn tên (không vẽ mũi tên trong clip)`
- **M (60 px)**: `/fal-image --ally --tier M hiệp sĩ nặng giáp tấm, khiên tháp, chùy một tay, áo choàng xanh dương`
- **L (84 px)**: `/fal-image --ally --tier L người tuyết thuần hóa lông trắng, vai to, chiến đấu bằng nắm đấm; attack: vồ hai tay về phía trước`

## --enemy-small
- **XS (24 px)**: `/fal-image --enemy-small nhện con đen tím, tám chân ngắn, mắt đỏ; attack: lao cắn ngắn tại chỗ; death: lật ngửa co chân`
- **XS (24 px)**: `/fal-image --enemy-small chuột cống khổng lồ lông xám, đuôi dài nâu nhạt, răng cửa to`
- **XS (24 px)**: `/fal-image --enemy-small slime xanh lá dạng giọt, thân đặc không trong suốt, một giọt nhớt bên PHẢI; di chuyển bằng cách co giãn`

## --enemy
- **S (40 px)**: `/fal-image --enemy --tier S yêu tinh goblin da xanh, dao găm gỉ tay phải, giáp da vá víu; attack: đâm dao tới trước`
- **S (40 px)**: `/fal-image --enemy --tier S đạo tặc đầu trọc bụng phệ, đao lớn tay phải, khăn đỏ ngang hông; attack: bổ đao từ trên xuống trước mặt, đứng tại chỗ`
- **S (40 px)**: `/fal-image --enemy --tier S bộ xương cầm khiên tròn gỗ mục và kiếm gãy; death: sụp thành đống xương`
- **M (60 px)**: `/fal-image --enemy --tier M người sói lông xám, móng vuốt dài, đứng hai chân khom lưng; attack: cào chéo hai tay`
- **M (60 px)**: `/fal-image --enemy --tier M hắc kỵ sĩ giáp đen gai nhọn, kiếm hai tay, mắt đỏ trong mũ giáp`

## --enemy-large
- **L (84 px)**: `/fal-image --enemy-large ogre da nâu xanh béo to, chùy gỗ to tay phải, khố da; attack: nện chùy xuống đất trước mặt`
- **L (84 px)**: `/fal-image --enemy-large golem dung nham, thân đá đen nứt có dung nham cam chảy giữa khe (lớp hình phẳng), nắm đấm to`
- **L (84 px)**: `/fal-image --enemy-large troll núi lông trắng cầm rìu đá hai tay; death: ngã sấp về phía trước tại chỗ`

## --boss
- **XL (120 px)**: `/fal-image --boss --tier XL tướng orc mini-boss, giáp sắt nặng, rìu hai lưỡi khổng lồ, cờ chiến sau lưng; special: gầm thét (hiệu ứng sóng âm là vfx riêng)`
- **XL (120 px)**: `/fal-image --boss --tier XL nhện chúa bụng phình xanh độc, tám chân dài; special: đẻ trứng tại chỗ`
- **XXL (170 px)**: `/fal-image --boss --tier XXL quỷ vương sừng cong, cánh dơi gấp sau lưng, giáp đỏ đen, đinh ba lửa; attack: đâm đinh ba tới trước; special: triệu hồi mưa lửa (mưa lửa là vfx riêng)`
- **XXL (170 px)**: `/fal-image --boss --tier XXL người khổng lồ băng, râu băng, chùy băng to bằng người; attack: đập chùy xuống trước mặt`

Note for skills and specials: describe only what the body does; a big effect (rain, storm, beam, shockwave)
is a separate vfx asset (`format.md` §7).
