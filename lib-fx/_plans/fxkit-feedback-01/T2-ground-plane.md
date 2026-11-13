# T2. Hiệu ứng mặt đất nằm trên mặt phẳng đất

Phụ thuộc: T1.

## Vấn đề
Ở `impact/quake/slam` bụi và vòng nằm đúng trên mặt đất, nhưng **chớp nổ** (`star`), **quầng sáng** và **mảnh văng** (`scraps`) vẽ trong mặt phẳng
màn hình: chớp là một quạt tròn, quầng là một đĩa tròn. Game nhìn từ trên chếch xuống, nên vụ nổ trên đất phải đọc là một **ellipse dẹp** bám đất,
chỉ phần bốc lên mới đứng.

## File được sửa
- `lib-fx/_core/formulas/draw/fxkit/ink.py` (biến đổi mặt phẳng), `effect.py` (`Layer` nhận tham số `plane`)
- `lib-fx/_core/formulas/draw/fxkit/layers/burst.py` (`star`), `scraps.py` (`scraps`)
- `lib-fx/impact/quake/quake.py`, `lib-fx/explosion/blast/blast.py` (dùng tham số mới)
- `FXKIT.md` (mục 3: tham số `plane`)

## Cách làm
1. **Biến đổi mặt phẳng ở một chỗ**, không sửa từng hình: thêm thuộc tính lớp `plane` (mặc định `None`) = `("ground", k)` với `k` = tỉ lệ y / x
   (chuẩn dự án: 0.3, bằng `squash` của `ring`). Trong `Ink.add` / `Ink.cut`, nếu lớp có `plane`, mọi điểm `(x, y)` được đổi thành
   `(x, oy + (y - oy) * k)` với `oy = c.o[1]` (điểm neo của lớp). Vì glow lấy từ mặt nạ đã vẽ nên quầng sáng tự thành ellipse.
   `Layer("star", ..., plane=("ground", 0.3))`.
2. Vụ nổ trên đất gồm **hai phần** (đây là điều làm nó đúng vật lý), thay cho một `star` duy nhất:
   - `star` id `splash`, `plane=("ground", 0.32)`, `arc=(-180, 180)`, `n=7`, `length≈150`: tia toé **dẹp sát đất** ra mọi phía, z `back` cho nửa xa
     nếu làm được (không bắt buộc), còn lại `front`.
   - `star` id `column`, không `plane`, `arc=(60, 120)`, `n=3`, `length≈110`, `width≈34`: cột chớp **đứng lên** hẹp ở giữa.
   Hai lớp cùng sinh ở khung trúng đòn; `column` tàn sớm hơn `splash` 2 khung.
3. `scraps` cho mặt đất: thêm tham số `floor=True`: mảnh rơi xuống tới `c.sp.floor` thì biến mất (không vẽ dưới đất); điểm xuất phát rải trên một
   ellipse dẹp bán kính `r0` thay vì một điểm.
4. Áp dụng: `impact/quake/slam`, `stomp` (chỉ `splash` nhỏ), `shockwave` (có cả hai), `explosion/blast/blast` và `small` (thêm `splash` dẹp dưới lửa;
   vòng của blast đổi `squash` 1.0 → 0.3 nếu hiệu ứng dùng trên đất: thêm biến thể `ground` thay vì đổi bản gốc).
5. Kiểm tra `plane` với `--from/--to` hướng trái và `--s 0.7`: ellipse phải nằm ngang, tâm đúng điểm neo.

## Tiêu chí nghiệm thu
- [ ] Khung đỉnh của `slam`: khung bao của lớp `splash` có tỉ lệ cao / rộng trong khoảng 0.28-0.4; quầng sáng quanh nó cũng dẹp.
- [ ] Cột chớp đứng vẫn đọc được "có lực đập xuống" ở khung trúng đòn (ảnh cỡ game).
- [ ] Bụi (`dust`) không đổi so với trước (người dùng đã khen): so ảnh.
- [ ] Không mảnh nào vẽ dưới đường đất.
- [ ] `impact/quake`, `explosion/blast` `--check` không FAIL; `fxkit_test.py` qua.

## Lệnh
```
python lib-fx/_tools/fxkit_sheet.py impact/quake/slam          # chụp TRƯỚC
python lib-fx/_tools/fxkit_sheet.py star plane=ground,0.32      # nếu sheet chưa nhận tham số lớp, thêm cờ --plane vào fxkit_sheet.py (được phép sửa file này)
python lib-fx/build.py impact/quake --check && python lib-fx/build.py explosion/blast --check
```

## Kết quả (người làm điền)

Làm: `Layer(plane=("ground", k))` (effect.py) + `Ink._px` bóp mọi điểm của `add` / `cut` về y/x = k quanh `c.o[1]` (ink.py); `star` nhận `even` (làm đều chiều dài tia, để splash tròn dẹp thay vì lệch một tia dài); `scraps` nhận `floor` (sinh trên ellipse dẹp bán kính `r0`, biến mất khi rơi về độ cao nơi sinh ra, không dùng `c.sp.floor` vì mảnh sinh ở nửa gần đã nằm dưới nó); `slam` = `splash` (plane 0.32, n=9, length 160, even 0.7) + `column` (n=3, arc 60-120, tàn sớm 2 khung); `stomp` chỉ `splash` nhỏ; `shockwave` có cả hai (`column` thay `star`); `blast` thêm `splash` (z back, plane 0.32), `small` splash nhỏ, biến thể mới `blast/ground` (ring squash 0.3, scraps floor). `FXKIT.md` mục 3 ghi `plane`, `even`, `floor`.

Trước / sau (`slam`, seed 0, @1x, kết xuất lớp `splash` một mình, mép đặc alpha > 200): khung 1-4 sau khi trúng đòn, cao / rộng = 0.33, 0.35, 0.35, 0.35 (khoảng 46x139 tới 88x255 ở @2x); hướng trái `--s 0.7`: 0.32-0.36. Kể cả quầng sáng (alpha > 20) tỉ lệ là 0.45-0.47: mờ nhoè có bề dày cố định nên không dẹp tuyệt đối, vẫn dẹp rõ so với trước. Trước: một ngôi sao 5 tia đứng, quầng tròn (ảnh `before-impact-quake-slam.png` trong scratchpad); sau: hoa tia dẹp nằm ngang bám đất + cột chớp đứng hẹp (xem `lib-fx/_gallery/kinds/impact-quake-slam.png`, git-ignored). Tâm splash lệch tâm neo 0-4 px @2x ở khung đỉnh (một số khung quầng lệch 9-15 px vì tia lệch).
Bụi: id `dust`, `dust_back` và thứ tự rng không đổi, ảnh sheet cho cùng hình đám bụi như trước. Không mảnh `scraps` nào dưới độ cao sinh.

Kiểm tra: `fxkit_test.py` all checks passed. Chấm qua `fxcheck` (không chạy `build.py` để khỏi ghi đè đầu ra, việc dựng lại là T6): `slam`, `stomp` ok; `shockwave`, `blast`, `small`, `ground` chỉ `warn linger` (shockwave đã có cảnh báo y hệt ở bản trước: 7 / 20 khung), không FAIL.
Chưa làm / hạn chế: cờ `--plane` cho `fxkit_sheet.py` chưa thêm (không cần: plane đặt trong khai báo lớp); chưa chụp trước / sau cho `stomp`, `shockwave`, `blast` (render quá chậm trên máy dùng chung); chưa xem `preview_game.gif`; `explosion/blast` chưa có ảnh trước để so, xem tại T6.
