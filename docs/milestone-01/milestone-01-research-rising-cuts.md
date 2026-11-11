# Milestone 01: nghiên cứu chưa thành (chém 2 nhát vuốt lên có xoay hông), 2026-11-10

Ghi lại để không thử lại từ đầu. **Kết luận: tạm dừng.** Milestone 01 dùng một nhát chém xéo từ trên xuống
(`out/heroes/holy_commander/source/video/attack_diag_side_downcut_t01.mp4`). Chi tiết từng take nằm trong
`out/heroes/holy_commander/history.md` (các dòng 2026-11-10). File làm việc của các lần thử đã xoá; chỉ còn ghi chép này.

## Đòn đã thử

Hai nhát **vuốt từ dưới lên** cắt nhau thành chữ X. Phần khó là **thân trên xoay hông, xoay vai trong lúc vung**: người xoay
từ quay lưng sang quay mặt ra (hoặc ngược lại) và đổi phía vung ở nhát 2. Đòn này **không phải** kiếm xoay vòng quanh thân;
kiếm chỉ vuốt lên, phần xoay nằm ở hông và thân trên.

Tham chiếu của user: một tờ phác người que cầm đại kiếm, có mũi tên lực:
1. khuỵu thấp, kiếm nằm đất;
2. chân đạp, hông kéo, kiếm bị lê sát đất và đi trễ sau tay;
3. vung lên qua đầu, khuỷu gập.

## Đã thử và kết quả (h3-max-turbo, gpt-image-2 low)

| Thử | Cách làm | Kết quả |
|---|---|---|
| Cả chữ X trong 1 clip, prompt theo cơ thể ("rotate back", "far side", "behind his chest") | 1 clip 4 s | nhát 2 **nhân vật quay người** sang trái |
| Cả chữ X, hướng viết theo màn hình + khoá nhìn phải | 1 clip 4 s | hết quay người; nhưng cả hai nhát vòng qua đầu, chữ X yếu; beat chuyển hoá thành một nhát bổ thừa |
| Chỉ nhát 1, ảnh cuối tạo từ hình vẽ đường kiếm của user | ảnh + clip 3 s | đường kiếm đúng; vệt cung lớn (xoá được bằng `dearc.py`) |
| Nhát 1, mô tả theo chuỗi lực (chân → hông → vai → tay → kiếm) | clip 3 s | lực và trọng lượng tốt hơn rõ; vệt cung dính vào lưỡi kiếm ở 4 frame; tư thế cuối sai (tay duỗi thay vì khuỷu gập) |
| Trên chính hình phác, ảnh đầu = hình 1, ảnh cuối = hình 3 | clip 4 s | giữ nét phác; **kiếm biến mất** ở đoạn giữa (không ghim hình 2); người quỳ |
| Nhát 2 trên hình phác, 3 hình khoá vẽ lại bằng fal-image, 2 clip nối nhau | 2 clip 3 s | lần đầu vẽ sai chân (đảo chân gần/xa, thành thế bước) và xoay sai mặt; làm lại với hình 1 làm mốc bàn chân → **chân cắm nguyên chỗ đạt** |
| Holy Commander theo 3 khoá của bản phác (nhát 2) | 5 ảnh + 2 clip | chân đứng yên đạt; **tay bị ngược** vì bản phác trắng không cho biết đâu là ngực, đâu là lưng |
| Lần cuối: ghi rõ mặt nào quay ra ở từng khoá (khoá 3 quay lưng) | 2 ảnh + 2 clip | ảnh khoá đúng; trong clip, model **xoay người cả hai chiều** (quay mặt ra rồi mới quay lưng) và vẽ vệt cung lớn dính lưỡi kiếm → bỏ |

Tổng chi cho nhánh này khoảng 0,8 USD.

## Bài học (giữ cho lần sau)

1. **Một động tác mỗi clip.** Hai nhát, hoặc một nhát có xoay hông/xoay thân lớn, thì model không giữ được. Một nhát không xoay người thì làm được.
2. **Ghim ảnh đầu và ảnh cuối, cùng cỡ, cùng chỗ đặt bàn chân.** Đo bàn chân trên lưới rồi căn theo trung điểm hai bàn chân. Chân lệch hoặc đảo chân gần/xa thì model hiểu thành bước.
3. **Ảnh khoá giữa** cho đoạn chuyển phức tạp (kéo kiếm qua thân). Không có thì model cho kiếm biến mất hoặc đi đường khác.
4. **Hướng viết theo màn hình** (trái-dưới → phải-trên); tránh các cụm "quay ngược / phía xa / sau lưng / qua vai sau", vì model đọc thành quay người.
5. **Mô tả theo chuỗi lực**, từng bộ phận một; kiếm đi sau tay. Beat chuyển phải là khuỷu gập, tay kéo chuôi xuống, lưỡi rơi theo trọng lượng, không phải "xoay cổ tay".
6. **Ghi rõ tay nào nối vai nào** trong prompt ảnh. Không ghi thì fal-image cho cả hai tay mọc từ một vai.
7. **Hình phác trắng không có trước/sau**: phải nói bằng lời mặt nào quay về người xem.
8. **Vệt cung**: cứ vung nhanh là model vẽ, dù đã cấm. Vệt tách khỏi lưỡi kiếm thì xoá được bằng `scripts/experiments/milestone_01/dearc.py`; vệt dính vào lưỡi kiếm thì phải bỏ frame.
9. Trần 4 clip của chuyên gia đã vượt trong nhánh này (user duyệt từng lần).

## Nếu làm lại sau Milestone 01

Mỗi nhát một clip, 3 ảnh khoá có mặt trước/sau ghi bằng lời, không xoay thân quá 90° trong một clip. Có thể chia phần xoay
thành một clip riêng không vung kiếm.
