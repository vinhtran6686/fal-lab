# Bảng phong cách tham khảo (style board): ghi nhận từ ảnh người dùng gửi

Tài liệu làm việc, **còn mở**: người dùng có thể gửi thêm ảnh. Tổng hợp của 10 ảnh đã thành bản nháp preset `style-vivid.md` trong `.claude/skills/fal-image/` (cạnh `style-chunky.md`); sau khi thử với Lôi Tộc và được duyệt sẽ thành mặc định. Ảnh gốc nằm ở `ref/style_board/` (chỉ đọc). Không đặt tên game nguồn trong prompt (luật của `format.md`).

## 1. Ảnh đã nhận (10)
| File trong `ref/style_board/` | Là gì | Ghi nhận |
|---|---|---|
| `mage_hero_announce.png` | anh hùng nam, pháp sư (ảnh giới thiệu) | thấp bè (~2,5-3 đầu), đầu to, vai áo vàng khổng lồ, bàn tay to, râu dê, lông mày dữ, mắt tím sáng; áo choàng tím, trượng vàng; quả cầu phép: các vòng phẳng đồng tâm tím-hồng-trắng; sao nền |
| `fire_golem_smash.png` | quái golem lửa đấm xuống (góc nhìn từ trên, xa gần mạnh) | nắm đấm khổng lồ ở tiền cảnh (foreshortening), giáp nâu rỉ có khe và đinh tán, đầu nhỏ lõm trong vai, mắt vàng sáng, lửa trên vai là các mảng phẳng vàng-cam-đỏ, nổ chạm đất gồm các mũi nhọn dài và mảnh vụn bay, bóng xám ellipse dưới đất |
| `witch_gunslinger.png` | nữ phù thủy xạ thủ (sprite nhỏ, 225 px) | mũ rộng vành che gần hết mặt, tóc đỏ cam dài bay, áo choàng xanh xám, hai súng; tư thế lao thấp bất đối xứng; khói là các đám phẳng xám xanh có viền; dơi bay; đọc rõ ở cỡ nhỏ nhờ cái mũ |
| `slingshot_girl_dragon.png` | nữ trẻ bắn ná + rồng tím (tranh quảng bá) | đầu to, mặt biểu cảm (cười nheo mắt), tóc cam xù thành mảng lớn có đầu nhọn; rồng tím hồng với quả cầu lửa vàng-cam xoáy hồng (mảng phẳng); nét viền mỏng hơn, nền mềm (tranh quảng bá, không phải sprite) |
| `shield_paladin.png` | hiệp sĩ nam, khiên (nhân vật chặn) | cực thấp bè, ngực tròn khổng lồ có huy hiệu sư tử vàng, ria trắng cong lớn, cười nhe răng, nắm đấm to hơn mặt, chân rất ngắn; khiên lớn hơn người phát sáng cyan (mảng phẳng + tia vạch) |
| `dwarf_stag_rider.png` | chiến binh lùn cưỡi hươu linh hồn xanh (kỵ binh) | râu cam lớn, tay cơ bắp, rìu giơ cao; hươu thân lục trong mờ sáng, sừng vàng, vòng gió xanh lục quanh rìu; dominant lục + nhấn vàng |
| `fire_elemental_man.png` | người lửa nam (nguyên tố) | thân cơ bắp có múi vẽ bằng mảng cứng, tóc và cánh tay là lưỡi lửa vàng-cam-đỏ phẳng, một nắm đấm giáp nâu to; mặt dữ; có quầng sáng mềm quanh lửa (khác với phần còn lại: nên tách khi làm sprite) |
| `berserker_chain_sword.png` | chiến binh cuồng nộ, kiếm xích (nam) | ~2,5 đầu, lông mày nặng, mắt đỏ phát sáng trên nền trắng, râu và tóc dài, mặt nhăn gầm, áo choàng đỏ tím rách, huy hiệu chéo, đai và giáp tay, kiếm khổng lồ cắm đất phát sáng hồng-vàng có xích quấn; nền tối |
| `jungle_group_keyart.webp` | tranh nhóm anh hùng trong rừng (tranh quảng bá) | nữ tư tế áo trắng cao mảnh (~5 đầu) với trượng vàng và vầng sáng cyan, tinh linh băng mảnh, khỉ chiến binh với chùy gai, phù thủy tím với đầu lâu, dũng sĩ lửa; nền rừng vẽ tay chi tiết, ánh sáng viền cyan và tím trên nhân vật |
| `ice_heroine_and_wizard_popups.png` | khung "anh hùng mới" và "tháp mới" (giao diện) | nữ anh hùng băng mảnh (~5 đầu), tóc trắng tết, áo choàng cam tím tung bay, mặt tự tin có lông mi, mắt cyan; phù thủy già râu trắng biểu cảm hoạt họa, sách vàng bay; nét viền xanh lục tối, nền xoáy xanh ngọc, tia sáng và mảnh vụn phẳng |

## 2. Tổng hợp phong cách từ 10 ảnh
**Thân hình theo giới và vai trò (khác biệt quan trọng nhất so với chunky)**
| Nhóm | Số đầu | Hình dáng |
|---|---|---|
| Nam chiến binh, đấu sĩ, tank | ~2,5-3 | đầu to, ngực và vai khổng lồ, nắm đấm bằng hoặc lớn hơn mặt, chân rất ngắn, râu hoặc ria lớn, mặt gầm hoặc cười nhe răng |
| Nam pháp sư, già | ~3, caricature | biểu cảm hoạt họa (miệng há, mắt nhắm), râu dài, tay nhỏ biểu diễn |
| Nữ anh hùng, tư tế, pháp sư | ~4-5 | mảnh, có đường cong, tóc dài bay, áo choàng tung, mặt tự tin có lông mi, mắt sáng; **không** là chibi |
| Nguyên tố, quái | ~2,5-3 | thân tạo bằng vật chất của hệ (lửa, linh hồn xanh, đá), cơ bắp rõ, tay hoặc nắm đấm lớn nhất |
| Thú, vật cưỡi | cân đối | sừng hoặc đặc điểm lớn, thân phát sáng hoặc hệ màu |

**Nét, tô, chi tiết**
- **Nét viền dày, đều, đậm** nhưng **ngả màu của vùng đó** (xanh tím đậm, nâu tím, xanh lục tối), không phải đen thuần ở mọi nơi; dày hơn ở ngoài, góc bo tròn.
- **Tô theo ô 3-4 tông cạnh cứng, tương phản mạnh:** tối sâu (đậm gần như chạm đen nhưng còn ngả màu), nền, sáng, và mảng điểm sáng kem trắng. Có viền sáng (rim) bằng mảng phẳng và vài điểm bóng loáng trên kim loại.
- **Chất liệu:** đốm và vết xước phẳng, đinh tán, khe giáp, đường chỉ bằng mảng; tóc, lông, ngọn lửa là cụm phẳng nhọn đầu.
- **Một thứ khổng lồ mỗi nhân vật:** thanh kiếm, khiên, mũ, nắm đấm, vai giáp, vật cưỡi. Hình bóng đọc được ở cỡ nhỏ.

**Màu**
- Một màu chủ đạo **bão hòa** + một màu nhấn **tương phản gần bù** (tím + vàng, lục + vàng, xanh dương + vàng-cyan, cam + xanh xám) + kem trắng ngả vàng cho điểm sáng.
- Vùng tối là màu đậm của chính nó. Ảnh nền cũng thường là màu bù (nền xanh ngọc cho nhân vật cam tím).
- Phát sáng (mắt, phép, kiếm) bằng mảng phẳng cyan, vàng hoặc đỏ nhiều lớp; một số ảnh có thêm quầng sáng mềm (không đưa vào sprite thân: hiệu ứng vẽ riêng).

**Mặt và tính cách**
- Mọi nhân vật đều **có tính cách ở mặt**: lông mày nặng, nhe răng, nhăn mũi, cười nheo mắt, ria râu lớn, mắt sáng; không là "mặt ít nét nhất". Dữ pha hài; vẫn không phải linh vật dễ thương.

**Hiệu ứng trong tranh (cho vfx sau, không vẽ trong thân sprite)**
- Lớp phẳng nhiều tông có viền: lưỡi lửa, vòng gió, mũi nhọn nổ, mảnh vụn, khói phẳng, sao hình thoi, vòng cầu đồng tâm, tia vạch.

## 3. So với bản chunky hiện tại (`style-chunky.md`)
| Mục | Chunky hiện tại | Phong cách tham khảo (vivid) |
|---|---|---|
| Tính cách | nghiêm, không dễ thương | dữ pha hài, mặt biểu cảm |
| Mặt | ít nét nhất | nhiều nét hơn (răng, ria, nheo mắt, lông mi) |
| Tương phản | vùng lớn ở **tông giữa**, sáng không trắng | tối sâu ngả màu, điểm sáng kem trắng, viền sáng, điểm bóng loáng |
| Nét viền | một màu nâu tím | đậm, ngả màu vùng (nhiều màu) |
| Chi tiết | không hoa văn nhỏ | đinh tán, khe giáp, đốm xước, huy hiệu |
| Màu | chủ đạo + ấm + vàng | chủ đạo bão hòa + nhấn bù + kem trắng |
| Tỉ lệ | ~3 đầu brawny; slender 4; agile 4,3 | nam 2,5-3; nữ và nhẹ 4-5; vật cầm khổng lồ |
| Nữ | thân slender chibi-không | mảnh, đường cong, tóc và áo choàng bay |

## 4. Việc cần làm khi nhận đủ ảnh
1. Đo từng ảnh theo phương pháp của `style-chunky.md` §3 (lượng tử hóa màu, tách phần nền, giá trị H/S/V) và tỉ lệ đầu/thân/chân.
2. Phân nhóm: nam, nữ, quái, class (cận chiến, pháp sư, xạ thủ, đấu sĩ, boss) rồi viết quy tắc hình dáng theo nhóm.
3. Đề xuất bản phong cách mới (khối `{STYLE}`, quy tắc mặt, bảng màu mẫu) cho người dùng duyệt, rồi cập nhật `style-chunky.md`.
4. Thử một lưới (một tộc) theo phong cách mới để so với lưới hiện tại, trước khi áp cho mọi tộc.
