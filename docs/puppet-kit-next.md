# Puppet Kit: kế hoạch bổ sung và tech debt

Cập nhật 2026-11-11, sau feedback của user. Trạng thái: **chưa làm, chờ user báo bắt đầu**. Nhánh `claude/puppet-kit`.
Đọc trước: `docs/puppet-kit.md` (kit hiện tại), `docs/puppet-kit-motion-recipes.md` (công thức chuyển động cho model viết animation).

## 1. Kết luận từ lần thử đầu

Làm tốt (user xác nhận): nhịp thở và nhịp phụ (nhún vai, đầu), pose đơn không xoay, áp fx.

Chưa đạt, theo thứ tự ưu tiên user đã đồng ý:

| # | Vấn đề | Bằng chứng | Gốc rễ |
|---|---|---|---|
| A | **Tài nguyên đầu vào thiếu và không đều** | áo choàng Holy Commander mất góc; run của lion: tay trái ở pose 1 và 3 bị gập, nhìn như tật; cỡ pose lệch tới 16% trước khi căn | mỗi pose là một ảnh độc lập do model tự vẽ; phần khuất vá bằng màu lân cận; không có bộ pose chuẩn |
| B | **Rig thiếu khớp** | chân đơ, không gập gối; không có khớp háng; khuỷu lion đặt ở mép găng | chân và hông nằm chung lớp thân; đa giác tay cắt sai chỗ |
| C | **Chưa có động tác xoay thân** | chưa thử cào từ trước mặt sang trái | chỉ có một góc nhìn (3/4), không có tài nguyên góc ngang |
| D | Pose-to-pose không có hình trung gian | attack, run giật | hệ quả của A và B |

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
| **Lớp khuất** | `layer_<tên>_vNN` | từng bộ phận bị che vẽ **đầy đủ một mình**: áo choàng trọn, tay xa trọn, chân xa trọn, đuôi trọn | thay cho `fill_under`/`grow` |
| **Tờ part (A-pose)** | `parts_vNN` | cả nhân vật ở tư thế chữ A, tay chân dang rời thân, mỗi đoạn chi thấy trọn khớp | cắt đùi, ống chân, bàn chân, cánh tay, cẳng tay, bàn tay |
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

Tên xương cố định cho mọi biped (để animation dùng lại giữa các nhân vật; công thức ở `puppet-kit-motion-recipes.md` dùng đúng các tên này):

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

## 5. Thứ tự làm và tiêu chí nghiệm thu

| Mốc | Việc | Nghiệm thu | Tiền |
|---|---|---|---|
| P02 | Gói tài nguyên cho **lion_brawler** theo 2.1 (bỏ profile); `prep`, `align` | mọi ảnh `align` pass; lớp khuất thay hết `fill_under` | ~0,08 USD |
| P03 | Rig v2 cho lion: 17 xương, khuỷu đúng chỗ, IK chân, khớp háng | khuỵu gối bằng `hips.ty` không trượt chân; skill có gập khuỷu thấy rõ; user duyệt | 0 |
| P04 | Rig Tuner v2 trên artifact | user tự chuyển được một khớp và tải rig về | 0 |
| P05 | Profile: `profile`, plate, parts, `rig_profile.json`; run và walk bằng rig theo công thức | `motion_check --loop` không cờ; tay không còn "tật"; user duyệt cạnh bản 4 pose | ~0,06 USD |
| P06 | Xoay thân: skill cào từ trước mặt sang trái, 3/4 → `pose_turn` → profile | user duyệt; nếu không đạt thì ghi rõ và dùng video cho đoạn xoay | ~0,05 USD |
| P07 | Áp lại cho Holy Commander (áo choàng trọn lớp) | áo choàng không mất góc ở mọi state | ~0,05 USD |

Mỗi mốc: hỏi advisor trước khi chốt kế hoạch và trước khi báo xong (quy tắc repo); cập nhật `docs/puppet-kit.md`, `experiment-log.md`, `roadmap.md`.

## 6. Tech debt (ngoài các mục trên)

| Mục | Ảnh hưởng | Khi nào |
|---|---|---|
| `pose_run_1` và `pose_run_3` của lion: tay trái gập sai | run nhìn như tay tật | P05 thay bằng run rig; trước đó có thể tạo lại 2 pose với góc khuỷu ghi số |
| `fill_under`, `grow` vá bằng màu gần nhất | lộ mảng sai màu khi lớp trên nhúc nhích nhiều | P02 thay bằng lớp khuất vẽ thật |
| Căn cỡ pose bằng một màu; sai khi bộ phận đó bị che (`slam_p1` căn bằng mắt) | lệch cỡ giữa các pose | P02 (`align`, nhiều mốc) |
| `ground` của pose lấy điểm thấp nhất | sai khi vuốt/vũ khí thấp hơn chân | P02 (`--feet`) |
| IK không cập nhật xương con | chưa lộ vì chưa có con | P03 |
| Không có test tự động | sửa engine có thể đổi frame mà không biết | P03: test hash frame cho 3 nhân vật |
| `stretch`, `deform.band`, `init`, `pose` chưa qua advisor | rủi ro lỗi chưa thấy | đầu P02 |
| Rig Tuner chưa mở thử trong trình duyệt | có thể không chạy | P04 |
| Vệt vuốt lion mượn `slash_params.json` của Holy Commander; dộng đất chưa có vòng sốc | fx chưa đúng nhân vật | sau P03 |
| `slash` phụ thuộc code thử nghiệm M01 và `PYTHONHASHSEED=0` | gắn với debt `hash()` của M01 | khi M01/M02 promote generator |
| Holy Commander: `idle_side` 24 hình đã ghi đè bản 1 hình, chưa duyệt; không có tay xa | - | P07 |
| Frost Oracle: tạm giữ theo ý user | - | - |
| Chưa có MCP | AI ngoài Claude Code chưa gọi được | sau P04, khi format rig ổn định |
| Máy Windows cần `scipy`, `opencv-python-headless`, `scikit-image` | lệnh `render`/`slash` không chạy nếu thiếu | ghi trong `docs/puppet-kit.md` |

## 7. Câu hỏi mở cho user

1. Profile chỉ là tài nguyên trung gian cho rig và xoay thân, hay game sẽ hiển thị cả góc ngang? (ảnh hưởng `format.md` §3)
2. Run: thay hẳn bản 4 pose bằng run rig profile, hay giữ 3/4 và chỉ sửa tay?
3. Rig Tuner v2 trước (P04) hay rig v2 do AI đặt trước (P03)?

## 8. Phân việc và tiến độ (từ 2026-11-11)

User đã báo bắt đầu. Việc đặc tả đóng giao cho model khác qua `docs/tasks/` (bảng ở `docs/tasks/README.md`); việc cần nhìn ảnh và sửa lõi engine do Fable làm trong session chính.

| Mã | Việc | Trạng thái | Ghi chú |
|---|---|---|---|
| F1 | P02: gói tài nguyên lion (lớp thân, hai chân, tay gần, tay xa, đuôi) | ✅ 2026-11-11, chờ user duyệt | 9 ảnh, ~0,10 USD (5 ảnh đầu hỏng 4: xem "Quy tắc mỏ neo") |
| F2 | P03: engine rig v2 + rig v2 cho lion | ✅ 2026-11-11, chờ user duyệt | 17 xương, 16 lớp; IK chân ghim đất; `v2_test_side` là bài thử khớp; T5 đã mở khoá |
| F3 | P05: profile + run/walk bằng rig | chưa làm | |
| F4 | P06: xoay thân | chưa làm | |

Ba câu hỏi ở §7 chưa có trả lời; mặc định tạm dùng: (1) profile chỉ là tài nguyên trung gian, không đổi `format.md`; (2) run sẽ thay bằng bản rig khi F3 xong, bản 4 pose giữ tới lúc đó; (3) rig v2 do AI đặt trước, Rig Tuner v2 (T3) làm song song.

### Quy tắc mỏ neo khi xin lớp rời (rút ra ở F1, bắt buộc)

- Xin "CHỈ giữ bộ phận X, xoá hết phần còn lại" thì model **phóng to và dời X ra giữa ảnh**: 4/5 lớp đầu (hai chân, tay gần, tay xa, đuôi) lệch hẳn vị trí, không dùng được.
  Lớp thân không lệch vì phần lớn nhân vật còn lại trong ảnh.
- Cách chạy được ngay lần sau (4/4 lớp khớp vị trí): viết prompt là **"ERASE"**, không "redraw", và **giữ nguyên cái đầu làm mỏ neo**:
  "Edit the reference image by ERASING parts of it. Do not redraw, move, resize or re-center anything ... The head with its mane stays untouched in its place as a fixed anchor.
  Besides the head, KEEP <bộ phận> exactly where it is ... ERASE <phần còn lại> ... complete <phần bị che>". Prompt đầy đủ: `out/heroes/lion_brawler/source/design/prompts/layer_*_p02.txt`.
- Mỏ neo phải **không đè lên bộ phận cần lấy**. Ở lion, bờm đè lên đỉnh vai gần nên đỉnh vai vẫn thiếu; lần sau dùng mỏ neo khác cho lớp tay (ví dụ giữ hai bàn chân).
- Vì vậy mục 2.1 đổi: không cần "tờ part A-pose" cho rig 3/4; lớp rời lấy bằng cách xoá từ chính master cho khớp từng pixel. Tờ part chỉ còn cần cho góc profile.

### Tồn đọng của rig v2 lion (sau F2)

| Mục | Thấy ở đâu | Hướng |
|---|---|---|
| Đỉnh vai gần bị cắt theo mép bờm | `v2_test_side` hình 13-17, khi tay vung quá ~60° | xin lại `layer_near_arm` với mỏ neo là bàn chân |
| Khe trắng nhỏ ở gấu quần/ống chân khi gối gập sâu | `v2_test_side` hình 6-11 | nới đa giác ống chân lên dưới gấu quần; Rig Tuner v2 (T3) |
| Đấm thẳng ra trước ở góc 3/4 khó đọc: tay vàng trên ngực vàng, không co ngắn theo phối cảnh | hình 14 | cần pose still hoặc rig profile (F3) |
| `pose_run`, `claw`, `slam`: vẫn là pose still; rig v2 mới thay phần lấy đà và hồi | - | F3 (run bằng rig) |
| Hash của test hồi quy (T1) sẽ khác nếu T1 chạy trước commit này | - | chạy `puppet_test.py --update` một lần |

## 9. Feedback 2026-11-11 (lần 2): gãy khúc ở khớp, và ý tưởng video pose

**Gãy khúc ở chỗ cắt** (user): đã xử lý bằng `skin` (khớp uốn liền), xem `docs/puppet-kit.md` mục cùng tên. Kết quả trên lion: khuỷu, eo đẹp hơn hẳn bản cắt; gối gập sâu còn răng cưa nhỏ ở nếp gập.
Còn lại: `blend` chọn bằng tay; Rig Tuner v2 (T3) chưa biết `skin` (cần thêm ô chọn "liền/cắt" và thanh `blend`).

**Ý tưởng của user: một video các pose cơ bản của nhân vật, cắt frame làm tài nguyên.** Đánh giá:

| | Video pose | Lớp rời + rig (đang làm) |
|---|---|---|
| Cho ra gì | ảnh **cả người** ở nhiều tư thế, kèm hình trung gian | từng bộ phận rời, phần khuất vẽ đủ |
| Khớp gập | đúng (model tự vẽ) | uốn hình có sẵn (`skin`): tốt ở góc vừa, kém ở góc gắt |
| Cỡ, vị trí giữa các frame | đều trong cùng một clip | khớp từng pixel với master |
| Tách lớp, đổi nhịp, tái dùng cho động tác khác | **không** (ảnh phẳng, mỗi frame dính cả người) | có |
| Rủi ro | lỗi quen của video: tự thêm vệt, đổi thiết kế, phải retry | lỗi cắt lớp, mỏ neo |
| Giá | ~0,045 USD / clip 3 s (≈45 frame) | ~0,011 USD / lớp |

Kết luận: video **không thay** rig (không tách được lớp), nhưng là nguồn tốt cho **tầng pose** ở đúng những chỗ rig yếu:
1. **Xoay thân / đổi góc nhìn** (F4): một clip "xoay người tại chỗ 3/4 → nghiêng → 3/4" cho đủ pose chuyển góc, cùng cỡ, có hình trung gian. Đây là việc ảnh tĩnh làm kém nhất.
2. **Vòng chạy, đi** (F3): một clip chạy tại chỗ cho 6-8 pose đều nhau, thay 4 pose tĩnh đang có tay "tật".
3. **Thư viện pose gập gắt** (ngồi xổm sâu, tay gập sát): lấy frame làm pose still thay cho `skin` ở góc quá lớn.

Đề xuất: mỗi nhân vật một **"pose reel"**: 2-3 clip ngắn (xoay tại chỗ; chạy tại chỗ; khởi động: ngồi xổm, giơ tay, gập tay), tổng ~0,10-0,15 USD, cắt bằng `video-sprite`,
rồi đăng ký từng frame thành pose rig bằng `puppet.py pose`. Rig vẫn lo idle, nhịp thở, lấy đà/hồi và mọi thứ cần chỉnh nhịp. **Chưa làm: video là khoản trả tiền, cần user đồng ý số clip và giá trước** (quy tắc cost guard).

## 10. Pose reel đã chạy (2026-11-11)

User duyệt làm video với điều kiện chuẩn bị kỹ để thành mẫu. Mẫu: `docs/puppet-kit-pose-reel.md` (v1.1, đã qua advisor). Chạy trên lion: 5 clip, mỗi clip một take, 0,24 USD,
cả 5 đạt; run và các đoạn chuyển nhanh còn nhoè. Đã ghép `run_side`, `turn_left_side`, `reel_test_side` từ frame reel. User cũng đánh giá khớp uốn liền (`skin`) **chưa đạt**.
**Đề xuất (chờ user đồng ý)**: rig chỉ dùng cho biên độ nhỏ, khớp gập lớn lấy từ reel; `skin` chưa được cải thiện thêm. Việc tiếp: mục 8 của file mẫu (v1.2), rồi skill cào xoay thân (F4) dùng frame turn.
