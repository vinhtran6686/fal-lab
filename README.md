# fal-image-lab

Claude Code (trong VS Code) làm "bộ não", fal.ai + GPT Image (quality low) làm "tay vẽ".
Claude dùng gói Claude.ai của bạn, không cần Anthropic API key. Chỉ trả tiền fal.ai.

## Cài đặt

1. Cài extension **Claude Code** trong VS Code và đăng nhập bằng tài khoản Claude.ai.
2. Mở thư mục này trong VS Code (File → Open Folder).
3. Trong terminal của VS Code:

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # rồi dán FAL_KEY vào .env
```

4. Kiểm tra nhanh (không cần Claude):

```bash
python scripts/gen_image.py "a red paper lantern on a wooden table" --name test
```

Ảnh nằm trong `out/`, kèm file `.json` (prompt, cấu hình, chi phí ước tính). Mọi lần tạo ảnh được ghi vào `out/costs.csv`.

## Dùng với Claude Code

Mở panel Claude Code và ra lệnh bằng tiếng Việt, ví dụ:

- "Tạo sprite lính bộ binh cầm khiên tròn, nền trong suốt"
- "Dùng template tháp 3 cấp, loại tháp pháo bằng đồng"
- "Làm animation đi bộ 8 hướng cho con goblin vừa duyệt"
- "Vẽ nền màn chơi sa mạc có 8 ô xây tháp"
- "Hôm nay mình đã tiêu bao nhiêu?"

Hai skill, mỗi skill một việc:
- `fal-image`: **ảnh tĩnh** (ảnh gốc): nhân vật đã chốt và các góc chuẩn (side, trước, sau, 3/4 trước, 3/4 sau), icon, tháp, map… Chọn template → viết prompt → chạy script → xem ảnh → chấm điểm → sửa prompt, tối đa 3 vòng.
- `video-sprite`: **animation** (move, attack, death…) từ các ảnh tĩnh đã chốt: image-to-video trên fal.ai → tách frame → xuất vào thư mục asset, **cùng một khung và một kích thước thân cho mọi action**. Claude hỏi trước khi tốn tiền video.

## Nhân vật theo class (enemy)

Cấu trúc: **format chung → class → level → archetype**.

- `.claude/skills/fal-image/format.md`: style (rút ra từ `ref/`), bộ góc nhìn chuẩn, cấu trúc thư mục, khung/pivot, checklist ảnh tĩnh.
- `.claude/skills/fal-image/classes/enemy.md`: class Enemy, **Level 1**: các góc cần có, prompt từng góc, khung **256×128** cho mọi action, thân cao 69 px (138 px @2x), danh sách animation (move 5 hướng + 3 lật, attack, death, icon).
- `.claude/skills/video-sprite/SKILL.md`: quy trình tạo animation từ ảnh tĩnh.
- Playtest: `python scripts/build_playtest.py` rồi nhờ Claude publish `out/playtest/` để xem quái đi trên map.

Ví dụ:
- `Tạo enemy nhện quái vật cận chiến` → Claude tạo **master** rồi dừng; bạn chốt (vd. "chốt v02") → Claude tạo các góc chuẩn để bạn duyệt.
- `Làm animation move/attack/death cho spider` → skill `video-sprite`, báo chi phí trước khi chạy.
- `Sửa attack của spider cho cú cắn uy lực hơn` → chỉ tạo version mới của sheet attack, bản cũ giữ nguyên.

Kết quả trong `out/<class>/<id>/` (vd. `out/enemies/bandit/`, `out/heroes/centaur/`):
- `design/`: **thiết kế gốc** (master, các góc, các pose), giữ mọi version.
- `raw/`: **video gốc** model trả về, giữ mọi take (`<action>_<set>_tNN.mp4` + `.json` prompt/chi phí). Video vào đây ngay khi sinh xong, nên push git là không mất.
- thư mục trạng thái `idle/`, `move/`, `attack/`, `death/`…: mỗi animation một thư mục, **chỉ giữ 1 bản cuối cùng đã chốt** (`preview.gif` để xem nhanh, `frames/` cho game, `check/` để kiểm tra).
- `.work/`: dữ liệu trung gian của tool, không đưa lên git.
- `brief.md` = nội dung đã điền + ảnh đã chốt; `history.md` = mỗi lần gen một dòng (điểm, lỗi, sửa gì).

Ảnh `--ref` dùng endpoint edit để giữ nhân vật đồng nhất giữa các góc.

## Template asset game (khác)

Template ảnh tĩnh trong `.claude/skills/fal-image/templates.md`: lính, anh hùng, quái, boss, bảng 5 góc nhìn (để so sánh), tháp 3 cấp, vật trang trí, hiệu ứng (1 khung), icon kỹ năng, khung UI, nền màn chơi.

Muốn đổi style chung cho cả bộ asset: tạo file `style.md` ở thư mục gốc, ghi mô tả style bằng tiếng Anh. Claude sẽ dùng file đó thay cho style mặc định.

## Script

| Cờ | Mặc định | Ghi chú |
|---|---|---|
| `--model` | `gpt-image-2` | hoặc `gpt-image-1.5`, `gpt-image-1-mini` (rẻ nhất) |
| `--quality` | `low` | `medium`/`high` đắt hơn nhiều |
| `--size` | `1024x1024` | `1024x1536`, `1536x1024` |
| `--transparent` | tắt | nền trong suốt, lưu PNG (dùng cho sprite) |
| `--name` | trống | tiền tố tên file, ví dụ `goblin_walk` |
| `--n` | `1` | 1–4 ảnh mỗi lần |

Báo cáo chi phí: `python scripts/cost_report.py` (thêm `--today` để xem riêng hôm nay).
Chi phí là ước tính theo bảng giá công khai của fal.ai; số thật xem ở fal.ai → Billing.
