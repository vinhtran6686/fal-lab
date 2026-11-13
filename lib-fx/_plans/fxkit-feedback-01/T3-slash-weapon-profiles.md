# T3. Vệt chém đọc ra loại vũ khí

Phụ thuộc: T1. Làm trước T4 (cùng file).

## Vấn đề
Vệt `slash` hiện tan bằng mòn nhiễu từ trong ra (`erode(..., hollow=True, holes=0.38)`), để lại **hoa văn ngoằn ngoèo** không gắn với vũ khí nào;
răng cưa (`teeth=4`) bật cho mọi vũ khí. Người dùng:
- **Kiếm, đao**: vệt **mịn**, các nét **cùng hướng, chạy đều** theo cung chém; chém xong không để lại hoa văn.
- **Rìu**: vệt gồm **các vết song song** (do răng / lưỡi dày).

## File được sửa
- `lib-fx/_core/formulas/draw/fxkit/layers/slash.py`
- `lib-fx/melee/slash/slash.py` (hiệu ứng và biến thể)
- `FXKIT.md` (bảng kind), `lib-fx/GUIDE.md` (dòng `melee/slash`), `lib-fx/_core/formulas/rules/vfx/slash/README.md` (thêm mục "theo loại vũ khí")

## Cách làm
Nguyên tắc: **mọi chi tiết và mọi pha tàn của vệt chém sống trong toạ độ nét** (`v` dọc cung 0 đuôi → 1 đầu, `c` ngang nét 0 mép trong → 1 mép ngoài),
không dùng nhiễu trong không gian màn hình. Hàm `at(f)` và `strip(...)` có sẵn trong `slash.py` đã làm việc trong toạ độ này.

1. Thêm tham số `weapon="sword"` (`"sword" | "axe" | "saw"`), và đổi mặc định `teeth=0`.
2. **Pha tàn mới, hình học, dùng chung** (thay `erode(..., hollow=True)`): vệt được coi là một bó `K` **sợi dọc** song song với cung:
   - sợi `j` chiếm dải ngang `[c0_j, c1_j]`, dải dọc `[v0_j, v1_j]`; lúc đỉnh các sợi khít nhau nên trông là **một dải liền** (không thấy khe);
   - khi `d = on_twos(ph, c)` tăng: mỗi sợi **mỏng đi** về tâm của nó (`bề rộng *= (1 - d) ** p_j`), **đuôi rút lên** (`v0_j += d * rút_j`),
     **đầu lùi nhẹ**; mỗi sợi có `p_j`, `rút_j` riêng từ `c.rng("strand", j)` nên chúng tách nhau thành các nét dài, mảnh, **cùng hướng**, rồi ngắn dần và hết;
   - hai đầu mỗi sợi thuôn nhọn (profile `sin(pi * u) ** 0.7` như `streaks` trong file);
   - không lỗ, không mảnh vụn ngẫu nhiên. `drop_specks` vẫn gọi cuối.
   Tông `deep` và `hot` là các sợi riêng (sợi `hot` ở mép ngoài tàn sau cùng với kiếm: mép lưỡi sáng lưu lại lâu nhất).
3. **Kiếm / đao** (`weapon="sword"`): `K = 3`, sợi chia không đều (ví dụ 50 % / 30 % / 20 % bề rộng, có jitter), mép ngoài là **một cung sạch**,
   không răng, không khía; thêm 1-2 `streaks` tóc rất mảnh chạy song song ngoài mép. Pha tàn: 3 nét dài mảnh dần. Bề rộng mặc định 46.
4. **Rìu** (`weapon="axe"`): ngay từ đỉnh đã thấy **4-6 dải song song** tách nhau bằng khe hẹp cố định (khe = 6-10 % bề rộng, vị trí không đều),
   dải rộng hẹp khác nhau; vệt **ngắn và dày hơn** (bề rộng mặc định 80, chỉ phủ 70 % cung), đầu vệt **tù** (profile đầu `(1 - v**3)` thay vì nhọn);
   pha tàn: từng dải ngắn dần từ đuôi, dải mảnh hết trước.
5. **Cưa / răng** (`weapon="saw"`, tuỳ chọn, làm nếu còn thời gian): như kiếm nhưng mép trong có răng đều `teeth=6`.
6. Hiệu ứng trong `lib-fx/melee/slash/slash.py`: `crescent` (kiếm), `heavy` (đại đao: kiếm, rộng 70, có `echo`), `thrust` (kiếm, `bend=0`),
   thêm `axe` (rìu) và `axe_heavy`. Mô tả (`desc`) ghi rõ vũ khí.
7. Quầng sáng giữ tới cuối (`glow=1.0`) như hiện tại.

## Tiêu chí nghiệm thu
- [ ] Đặt `crescent` và `axe` cạnh nhau ở cỡ game: người không biết trước vẫn nói được cái nào là kiếm, cái nào là rìu (ghi nhận xét vào "Kết quả").
- [ ] Kiếm: ở mọi khung, mọi nét của vệt gần song song với cung chém (không có nét ngang, không lỗ, không hoa văn); khung tàn chỉ còn 2-3 nét dài mảnh.
- [ ] Rìu: đếm được 4-6 dải song song ở khung đỉnh và trong pha tàn.
- [ ] 4 seed khác nhau cho 4 bản khác nhau nhưng cùng tính chất.
- [ ] `bend=0`, `bend=-0.3`, `--reach 80`, `--reach 260` vẫn đúng (bụng vệt nằm phía trong cung).
- [ ] `fxcheck` không `cut`, không `pop`; `melee/slash --check` không FAIL.

## Lệnh
```
python lib-fx/_tools/fxkit_sheet.py slash --life 0,0.1,0.033,0.3 --pal frost --pal2 blaze --reach 200            # chụp TRƯỚC
python lib-fx/_tools/fxkit_sheet.py slash weapon=axe width=80 --life 0,0.1,0.05,0.33 --pal sun --reach 200
python lib-fx/build.py melee/slash --check
```
Mẫu để đối chiếu: `ref/vfx/slash-trio/` (nhát chém mịn), `lib-fx/_core/results/vector-showcase/generated/gen-slash-blue/` (đã được người dùng chấm 8-9/10),
`ref/vfx/axe-swing-idea/reference.png` (rìu).

## Kết quả (người làm điền)
