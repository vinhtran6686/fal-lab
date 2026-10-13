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
- "Làm sprite đi bộ 4 frame cho con goblin vừa duyệt"
- "Vẽ nền màn chơi sa mạc có 8 ô xây tháp"
- "Hôm nay mình đã tiêu bao nhiêu?"

Claude dùng skill `fal-image`: chọn template → viết prompt → chạy script → mở ảnh xem → chấm điểm → sửa prompt → lặp tối đa 3 vòng, rồi báo ảnh tốt nhất và tổng chi phí.

## Sprite theo class (enemy)

Cấu trúc: **format chung → class → level → archetype**.

- `.claude/skills/fal-image/format.md`: style (rút ra từ `ref/`), góc nhìn, khung, pivot, tên file, `meta.json`, quy trình, checklist. Mọi class dùng chung.
- `.claude/skills/fal-image/classes/enemy.md`: class Enemy, hiện có **Level 1** (cận chiến / đánh xa): walk **8 hướng** (5 sheet tạo + 3 lật), walk 8 frame, attack/death 9 frame, icon, khung 128px, `move_speed`.
- Playtest: `python scripts/build_playtest.py` rồi nhờ Claude publish `out/playtest/` để xem quái đi trên map.

Ví dụ:
- `Tạo sprite enemy nhện quái vật cận chiến` → Claude chỉ tạo **master** rồi dừng; bạn chốt (vd. "chốt v02") → Claude tạo hết các sheet.
- `Tạo sprite enemy nhện quái vật cận chiến --auto` → chạy hết một mạch, Claude tự chốt master.
- `Sửa attack của spider cho cú cắn uy lực hơn` → chỉ tạo version mới của sheet attack, bản cũ giữ nguyên.

Kết quả trong `out/enemies/<id>/`: mỗi sheet một thư mục (`walk_side/`, `attack_side/`…) gồm `raw/<sheet>_vNN.png`
(mọi lần gen) và thư mục `vNN/` (bản đã đóng gói). **Số `vNN/` cao nhất là bản final.**
`brief.md` = nội dung đã điền + master đã chốt; `history.md` = mỗi lần gen một dòng (điểm, lỗi, sửa gì).

Hậu kỳ: `python scripts/sprite_pack.py --help`. Ảnh `--ref` dùng endpoint edit để giữ nhân vật đồng nhất.

## Template asset game (khác)

13 template nằm trong `.claude/skills/fal-image/templates.md`: lính, anh hùng, quái, boss, sprite đi bộ, tấn công, 4 hướng nhìn, tháp 3 cấp, vật trang trí, hiệu ứng, icon kỹ năng, khung UI, nền màn chơi.

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
