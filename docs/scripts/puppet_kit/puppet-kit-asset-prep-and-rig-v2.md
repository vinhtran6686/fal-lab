# Puppet Kit: chuẩn bị tài nguyên và rig v2 (đặc tả + tech debt)

Phạm vi: bước chuẩn bị tài nguyên trước khi dựng rig (§2), bộ xương chuẩn 17 xương (§3), Rig Tuner v2 (§4), quy tắc xin lớp rời bằng model ảnh, và nợ kỹ thuật còn lại (§6).
Công cụ: `scripts/puppet_prep.py`, `scripts/puppet_kit/`, `scripts/puppet_kit/rig_tuner.html`. Đọc trước: `puppet-kit-guide.md` (kit), `docs/scripts/puppet_kit/puppet-kit-motion-recipes.md` (công thức chuyển động).
Đã có công cụ: gói tài nguyên, rig v2 (17 xương), Rig Tuner v2, test hồi quy. Chưa làm: rig profile cho run/walk, xoay thân.

## 2. Bước mới: chuẩn bị tài nguyên (làm trước mọi thứ)

Ý của user (2026-11-11): bước chuẩn bị tài nguyên là quan trọng nhất. Ngoài pose 3/4 hiện có, chuẩn bị thêm **bộ pose đứng nghiêng (profile)**, gồm cả bước chân,
để chia khớp linh hoạt hơn và làm được skill bắt đầu bằng xoay thân (từ pose đối diện sang pose ngang). Ảnh mẫu user gửi: người chạy nhìn ngang, vẽ khối rời
từng đoạn chi (bắp tay, cẳng tay, bàn tay, đùi, ống chân, bàn chân, ngực, hông).

### 2.1 Gói tài nguyên chuẩn của một nhân vật (`source/design/` + `source/rig/`)

| Nhóm | File | Nội dung | Dùng cho |
|---|---|---|---|
| Master | `master_vNN` | 3/4 quay phải, tư thế nghỉ (đã có) | idle, mốc style và cỡ |
| Plate 3/4 | `plate_vNN` | master bỏ tay, vũ khí, đuôi (đã có) | lớp thân |
| **Plate chân** | `plate_legs_vNN` | master bỏ tay **và cả hai chân**: thấy trọn hông, đáy áo/quần | khớp háng, rig chân |
| **Lớp khuất** (xem §7: ưu tiên plate ERASE) | `layer_<tên>_vNN` | từng bộ phận bị che vẽ **đầy đủ một mình**: áo choàng trọn, tay xa trọn, chân xa trọn, đuôi trọn | thay cho `fill_under`/`grow` |
| **Tờ part (A-pose)** (xem §7: dễ lệch tỉ lệ, chỉ cho profile) | `parts_vNN` | cả nhân vật ở tư thế chữ A, tay chân dang rời thân, mỗi đoạn chi thấy trọn khớp | cắt đùi, ống chân, bàn chân, cánh tay, cẳng tay, bàn tay |
| **Profile** | `profile_vNN` | nhìn ngang hẳn (không 3/4), quay phải, đứng nghỉ | rig thứ hai cho run/walk và mốc cho xoay thân |
| **Plate profile** | `profile_plate_vNN`, `profile_parts_vNN` | như trên cho góc ngang | rig profile |
| Pose khoá | `pose_<động tác>_<n>_vNN` | chỉ cho những gì rig không làm được (đã có) | tầng 2 |
| **Pose chuyển góc** | `pose_turn_<n>_vNN` | 1-2 pose giữa 3/4 và profile | xoay thân |

Chi phí ước tính một nhân vật: 8-10 ảnh low ngoài master, khoảng 0,12-0,15 USD, một lần.

### 2.2 Quy tắc viết prompt cho tài nguyên (rút từ các lỗi đã gặp)

1. **Mỗi tay nối đúng vai của nó**, ghi rõ tay nào ở phía nào của ảnh, và ghi **góc khuỷu bằng số** ("elbow bent about 90 degrees"); không để model tự chọn. Lỗi run pose 1 và 3: tay trái gập sát, nhìn như tật.
2. Với pose chạy/đi: ghi cả **tay ngược chân** và nói rõ tay nào ra trước ở từng pose; cấm "both arms on the same side".
3. Ghi "the head and the mane/helmet exactly as big as in the reference" và kiểm bằng `puppet.py pose` (cỡ theo màu); lệch quá 5% thì tạo lại, không bù bằng tay.
4. Lớp khuất: "draw ONLY the <part>, complete, including what the body normally hides, same size and same position as in the reference, nothing else in the picture".
5. Tờ part: "A-pose, arms 45 degrees away from the body, legs apart, every joint (shoulder, elbow, wrist, hip, knee, ankle) clearly visible, no limb overlapping another".
6. Profile: "pure SIDE PROFILE facing right, one eye visible, the near arm and near leg fully visible, not a three-quarter view". Đây là ngoại lệ có chủ ý so với `format.md` §3
   (vốn chỉ có 3/4): ghi vào `brief.md` là tài nguyên rig, không phải góc nhìn của game. **Cần user xác nhận** game có hiển thị góc profile hay chỉ dùng làm trung gian.
7. Sau mỗi ảnh: chồng lên master bằng `puppet.py check` (bbox, hàng chân); không khớp thì tạo lại ngay, tối đa 3 lần.

### 2.3 Lệnh cần thêm cho bước này

| Lệnh | Việc |
|---|---|
| `puppet.py prep <asset>` | in danh sách tài nguyên còn thiếu theo bảng 2.1 và prompt đã điền sẵn `{design}` |
| `puppet.py align <asset> <ảnh>` | chồng ảnh mới lên master: lệch bbox, lệch hàng chân, tỉ lệ cỡ theo màu; trả pass/fail |
| `puppet.py pose` (đã có) | thêm nhiều mốc màu, và `--feet x1,x2` để chỉ điểm chân khi vuốt thấp hơn chân |

## 3. Rig v2: bộ xương chuẩn

Tên xương cố định cho mọi biped (để animation dùng lại giữa các nhân vật; công thức ở `docs/scripts/puppet_kit/puppet-kit-motion-recipes.md` dùng đúng các tên này):

```
root
└─ hips                      (pivot: giữa hai khớp háng)      <- khớp háng: xoay/nghiêng hông
   ├─ spine                  (pivot: eo)                       <- thân trên xoay độc lập với hông
   │  ├─ head                (pivot: cổ)
   │  ├─ near_upper_arm      (pivot: vai gần)
   │  │  └─ near_forearm     (pivot: KHUỶU, không phải mép găng)
   │  │     └─ near_hand     (pivot: cổ tay; găng, vũ khí)
   │  └─ far_upper_arm → far_forearm → far_hand
   ├─ near_thigh             (pivot: háng gần)
   │  └─ near_shin           (pivot: gối)
   │     └─ near_foot        (pivot: cổ chân)
   ├─ far_thigh → far_shin → far_foot
   └─ tail / cape            (deform)
```

Việc phải làm trong engine (`scripts/puppet_kit/core.py`):

| Việc | Ghi chú |
|---|---|
| IK chân: `near_thigh`+`near_shin` tới đích là `near_foot` ghim trên đất | đã có IK hai xương; cần đích là điểm cố định trong hệ `root` và cập nhật xương con sau IK (lỗi đã biết: IK không cập nhật con) |
| `hips.ty` hạ xuống thì gối tự gập | hệ quả của IK chân; thay cho nén cả khối (`body.sy`) |
| Thứ tự vẽ đổi theo frame (`z` là kênh) | tay gần vung ra sau thân, chân đổi trước sau khi chạy |
| Đổi lớp theo frame (`swap`) | bàn tay nắm/mở, mặt gầm/thường, thân 3/4 ↔ profile khi xoay |
| Hai rig cho một nhân vật: `rig.json` (3/4) và `rig_profile.json` | shot đã cho phép đổi rig; cần chung tên xương và chung `unit` |
| Nội suy giữa hai rig khi xoay | bước đầu: cắt qua 1-2 `pose_turn`; không nội suy hình |
| Bóng chân theo `ground` của shot, co khi nhảy | hiện cố định ở pivot |

## 4. Công cụ cho user tự đặt khớp (Rig Tuner v2)

`scripts/puppet_kit/rig_tuner.html` hiện chỉ kéo điểm có sẵn và chưa được mở thử. Cần:

1. Tạo, đổi tên, xoá xương; gán cha; tạo đa giác mới cho một lớp.
2. Chọn nguồn ảnh cho từng lớp (master, plate, parts, layer).
3. **Xem thử ngay**: thanh trượt xoay từng khớp, vẽ lại bằng canvas (không cần Python) để thấy khớp đặt đúng chưa.
4. Khung xương mẫu: nút "Biped chuẩn" đặt sẵn 17 xương của mục 3 để user chỉ kéo vào đúng chỗ.
5. Tải `rig.json`; nạp lại `rig.json` cũ.
Đưa lên artifact để user dùng trực tiếp (ảnh nạp từ máy user, không cần server).

## 5. Tech debt còn lại

| Mục | Ảnh hưởng | Khi nào |
|---|---|---|
| `fill_under`, `grow` vá bằng màu gần nhất | lộ mảng sai màu khi lớp trên nhúc nhích nhiều | P02 thay bằng lớp khuất vẽ thật |
| Căn cỡ pose bằng một màu; sai khi bộ phận đó bị che (`slam_p1` căn bằng mắt) | lệch cỡ giữa các pose | P02 (`align`, nhiều mốc) |
| `ground` của pose lấy điểm thấp nhất | sai khi vuốt/vũ khí thấp hơn chân | P02 (`--feet`) |
| IK không cập nhật xương con | chưa lộ vì chưa có con | P03 |
| Không có test tự động | sửa engine có thể đổi frame mà không biết | P03: test hash frame cho 3 nhân vật |
| `stretch`, `deform.band`, `init`, `pose` chưa qua advisor | rủi ro lỗi chưa thấy | đầu P02 |
| Rig Tuner chưa mở thử trong trình duyệt | có thể không chạy | P04 |
| `slash` phụ thuộc code thử nghiệm M01 và `PYTHONHASHSEED=0` | gắn với debt `hash()` của M01 | khi M01/M02 promote generator |
| Holy Commander: `idle_side` 24 hình đã ghi đè bản 1 hình, chưa duyệt; không có tay xa | - | P07 |
| Chưa có MCP | AI ngoài Claude Code chưa gọi được | sau P04, khi format rig ổn định |
| Máy Windows cần `scipy`, `opencv-python-headless`, `scikit-image` | lệnh `render`/`slash` không chạy nếu thiếu | ghi trong `docs/scripts/puppet_kit/puppet-kit-guide.md` |

## 6. Quy tắc mỏ neo khi xin lớp rời (bắt buộc)

- Xin "CHỈ giữ bộ phận X, xoá hết phần còn lại" thì model **phóng to và dời X ra giữa ảnh**: 4/5 lớp đầu (hai chân, tay gần, tay xa, đuôi) lệch hẳn vị trí, không dùng được.
  Lớp thân không lệch vì phần lớn nhân vật còn lại trong ảnh.
- Cách chạy được ngay lần sau (4/4 lớp khớp vị trí): viết prompt là **"ERASE"**, không "redraw", và **giữ nguyên cái đầu làm mỏ neo**:
  "Edit the reference image by ERASING parts of it. Do not redraw, move, resize or re-center anything ... The head with its mane stays untouched in its place as a fixed anchor.
  Besides the head, KEEP <bộ phận> exactly where it is ... ERASE <phần còn lại> ... complete <phần bị che>".
- Mỏ neo phải **không đè lên bộ phận cần lấy**. Với nhân vật có bờm, bờm đè lên đỉnh vai gần nên đỉnh vai vẫn thiếu; lần sau dùng mỏ neo khác cho lớp tay (ví dụ giữ hai bàn chân).
- Vì vậy mục 2.1 đổi: không cần "tờ part A-pose" cho rig 3/4; lớp rời lấy bằng cách xoá từ chính master cho khớp từng pixel. Tờ part chỉ còn cần cho góc profile.

## 7. Lớp thân (plate) và tách bộ phận: kết luận từ `pyre_witch` (2026-11-12)

Bài toán: tay nằm đè lên tóc và váy; khi tay hoặc đầu cử động, phần bị che lộ ra trống nên hình nhân vật bị "xé". Đã thử năm cách, kết luận như sau.

| Cách | Kết quả | Dùng? |
|---|---|---|
| Tờ bộ phận do AI vẽ lại (`parts_sheet`, cả bản A1 một ảnh) rồi ghép về master | Mỗi bộ phận lệch tỉ lệ riêng (1,10 đến 1,28), tóc co lại, mất mái tóc và chân, ghép lại IoU 0,66 | **Không** |
| Từng lớp rời do AI vẽ (`layer_head/body/arm_*`) | Bộ phận dời ra giữa ảnh, lệch vị trí, model tự quyết số lớp | **Không** |
| Cắt đa giác từ master + lớp thân (plate) vá bằng code (màu tối gần nhất) | Sạch ở cỡ game, kể cả biên độ gấp 6 lần; vùng tóc bị che chỉ là màu nội suy | Phương án dự phòng, 0 USD |
| **Plate do AI xoá tay trên cùng canvas (ERASE)** | Cùng vị trí và cỡ (IoU 0,988 ngoài vùng tay, sai màu 3,9/255), tóc sau tay là tóc thật; `align` PASS | **Mặc định** |
| Pose skill vẽ riêng (cặp pose A/B) + rig từng pose | Hợp cho chuyển động lớn mà rig 2D không làm được | Dùng cho skill (`docs/pipeline/pose-pair-fx-method.md`) |

**Quy trình chuẩn cho một nhân vật có tay đè lên thân** (`out/heroes/pyre_witch/source/rig/make_rig.py` là bản mẫu):
1. Đầu và hai tay cắt bằng **đa giác từ master** (không xin AI vẽ lại bộ phận). Thứ tự lớp: plate (tóc sau, váy, chân) → tay xa → đầu (mặt cùng mái tóc/vương miện trong một mảnh) → tay gần.
2. Plate: một ảnh 1 lượt gọi (khoảng 0,011 USD) theo mẫu `source/design/prompts/plate_noarms_p01.txt`: "ERASE", cùng canvas 1024, giữ đầu làm **mỏ neo bất động**, nói rõ tay bên nào ở phía nào của ảnh, yêu cầu vẽ tiếp tóc và lỗ tay áo ở chỗ tay che.
3. Kiểm: `python scripts/puppet_prep.py align <asset> <ảnh> --kind plate` (lệch bbox và hàng chân tối đa 12 px; cạnh bên phía tay bị xoá lệch là bình thường).
4. Ghép lai: lấy AI cho thân, **giữ phần nền do code vá ngay sau đầu** (đầu còn cử động nên không để đầu tĩnh nằm sau). Cờ `--code-plate` quay về plate thuần code.
5. Lỗ tay áo do AI vẽ có thể lộ mảng da khi tay xoay mạnh; kiểm khung xoay mạnh nhất, nếu lộ thì tô lại bằng màu áo.
6. Khi tay vươn xa hơn idle (skill), không cố nới plate: dùng pose riêng (hàng cuối bảng trên).

Bài học chung về AI: xin ảnh **sửa trên cùng canvas** thì giữ vị trí tốt (IoU 0,92 đến 0,99); xin **sắp lại thành tờ bộ phận** thì trôi tỉ lệ từng bộ phận. Đo bằng IoU và hệ số cỡ, không đánh giá bằng mắt.
