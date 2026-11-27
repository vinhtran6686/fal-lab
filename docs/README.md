# Docs của fal-image-lab

Cây thư mục dưới đây phản chiếu repo: mỗi thư mục là một đối tượng trong repo, mỗi file là một chủ đề của đối tượng đó, tên file cho biết nội dung.
Doc mới đặt vào thư mục của đối tượng nó mô tả rồi thêm một dòng vào cây này. Không có doc cho thử nghiệm, báo cáo phiên hay kế hoạch đã xong (lịch sử nằm ở git và `out/<class>/<id>/history.md`).

```
docs/
├── README.md                                              (file này)
├── repo-structure-rules.md                                quy tắc đặt tool, skill, công thức, fx, doc, asset vào đâu
├── pipeline/                                              quy trình xuyên nhiều công cụ, trên một nhân vật
│   ├── asset-manifest.md                                  bảng checklist asset trong brief.md, lệnh asset_status.py
│   ├── pose-pair-fx-method.md                             skill bằng pose A/B + vệt chém lib-fx + rig Studio (quy trình, checklist, chi phí)
│   ├── pose-from-reference-clip-method.md                 pose cắt từ một clip video tham chiếu + vệt chém lib-fx + rig lớp (đứng yên, lấy đà, quán tính)
│   ├── images/pose-pair-sweep-fit-before-after.png       ảnh trước / sau của mục "Hai pose lệch nhau" trong pose-pair-fx-method.md
│   ├── images/pose-pair-sweep-abc-before-after.png       ảnh trước (hai pose A, B) / sau (ba pose A, B, C) của mục 10.6 trong pose-pair-fx-method.md
├── skills/                                                tài liệu bổ sung cho .claude/skills/<skill>/
│   ├── fal-image/                                         ảnh tĩnh qua scripts/gen_image.py
│   │   ├── fal-image-manual-prompt-style-transfer.md      prompt chuyển concept image sang style của dự án (chế độ --manual)
│   │   └── fal-image-manual-prompt-assets-from-master.md  prompt cho các ảnh còn lại từ master đã duyệt (chế độ --manual)
│   └── video-sprite/                                      animation bằng video qua scripts/fal_video.py
│       ├── video-sprite-motion-description-rules.md       quy tắc viết mô tả động tác (hệ quy chiếu, hướng từng bước, mục tiêu)
│       └── video-sprite-reference-video-route.md          route video tham chiếu (scripts/make_ref_video.py)
├── styles/                                                phong cách thiết kế nhân vật (nghiên cứu riêng, skill đọc khi người dùng yêu cầu)
│   └── heroic-vector-style/                               "style heroic" của fal-image (mặc định vẫn là style-chunky)
│       ├── style-spec.md                                  đặc tả: đơn giản sạch, thân hình theo giới tính và vai, thẻ mô tả, nét, màu, mặt, kiểm duyệt
│       ├── prompt-recipe.md                               cách viết prompt: khung lưới, mẫu đoạn nhân vật, khối style, từ nên dùng và tránh
│       ├── lessons.md                                     bài học bản v01 rối và v02 đạt
│       ├── style-board.md                                 10 ảnh tham khảo và nhận xét (ảnh ở ref/style_board/)
│       ├── prompt-template.txt                            prompt lưới 10 nhân vật hỗn hợp đã chạy được
│       ├── prompt-template-female-lineup.txt              prompt lưới 10 nữ (chunky, tô khối, nét dày, vật khổng lồ, 3840x2160)
│       ├── prompt-template-hero-faithful-redraw.txt       prompt master hero vẽ lại sát ảnh tham khảo (một con, 1024x1024, --ref ảnh đã xóa chữ ký)
├── scripts/                                               tài liệu cho code trong scripts/
│   ├── puppet_kit/                                        scripts/puppet*.py, scripts/puppet_kit/
│   │   ├── puppet-kit-guide.md                            cách dùng kit: rig, lệnh check/render/track/slash, skin, links
│   │   ├── puppet-kit-motion-recipes.md                   công thức viết anims/*.json (dấu, bảng nhịp, run cycle, checklist)
│   │   ├── puppet-kit-asset-prep-and-rig-v2.md            chuẩn bị tài nguyên, bộ xương 17 xương, Rig Tuner v2, quy tắc mỏ neo, nợ kỹ thuật
│   │   └── puppet-kit-pose-reel.md                        pose reel: clip tư thế cho động tác rig không vẽ được (puppet_reel.py)
│   ├── ref_atlas/                                         scripts/ref_atlas/
│   │   └── ref-atlas-split-and-animations.md              tách atlas tham khảo (png + lua) thành frame, gif và animation có tên
│   └── lineup/                                            scripts/lineup/
│       ├── lineup-workflow.md                             quy trình lưới nhiều nhân vật trong một clip cho mọi class: 5 bước, bảng thông số (kích thước, thời lượng, giá), bảng cấp và class
│       ├── lineup-heroes-from-masters.md                  lưới hero ghép từ master đã chốt: các bước, khung prompt mỗi con độc lập, quy trình duyệt
│       ├── lineup-heroes-lessons.md                       bài học từ các lần chốt / trả lại: master vẽ lại, clip, khi nào để model tự sáng tạo
│       ├── prompts/                                       prompt đã chạy: lưới 10 quái, đòn chém từ trên xuống, chết tại chỗ; hero-lineup-* (attack, death, run, skill 1-3)
│       └── lineup-split-guide.md                          tách clip lưới nhiều nhân vật thành bộ khung từng con (lineup_split.py)
├── tools/                                                 tài liệu cho ứng dụng trong tools/
│   ├── studio/                                            tools/studio/ (Rig & Pose Studio)
│   │   ├── puppet-studio-guide.md                         cách dùng Studio, schema limit/links, quy tắc
│   │   ├── puppet-studio-concepts.md                      khái niệm cho người dùng (khớp, dây chằng, IK, mối nối tròn)
│   │   ├── puppet-studio-ai-guide.md                      sổ tay cho AI khi sửa rig theo yêu cầu
│   │   └── puppet-studio-limits.md                        tính năng đã có và giới hạn của rig cắt từ một ảnh
│   └── frame_tuner/
│       └── frame-tuner-guide.md                           tools/frame_tuner/: bật/tắt frame, chỉnh thời gian, lưu công thức
```

## Docs nằm cạnh code (không chuyển vào docs/)

| Vị trí | Nội dung |
|---|---|
| `.claude/skills/fal-image/` | `SKILL.md`, `format.md` (style, góc nhìn, thư mục, manifest), `classes/*.md` (hero, ally, enemy, enemy-flying, boss), `reference.md`, `templates.md`, `examples.md`, `action-planes.md` (góc nhìn của game và mặt phẳng của động tác: chém dọc, ngang, xéo, đâm, phép; cách viết pose và nơi đặt vfx), `preflight.md` (suy nghĩ và kiểm tra trước khi tạo ảnh: ghi chú thiết kế, lint prompt, một quyết định một ảnh), `style-chunky.md` (phong cách mặc định cho nhân vật mới: tỉ lệ 3 đầu, nét viền, bảng màu hài hoà, mặt, mức chi tiết, mẫu prompt, checklist có phép thử thu nhỏ 60 px) |
| `.claude/skills/video-sprite/` | `SKILL.md`, `references/` (prompt chuyển động; `action-planes.md`: mặt phẳng của động tác trong clip), `playtest/`, `scripts/` |
| `lib-fx/` | `README.md` (lệnh, luật nhìn), `GUIDE.md` (bản đồ thư mục), `MINDSET.md`, `lib-fx/_core/formulas/draw/FXKIT.md` (fxkit: hệ thống dựng hiệu ứng theo lớp, phong cách, hợp đồng của một lớp), `lib-fx/_core/formulas/draw/DESIGN.md`, `RECIPE-*.md`, `lib-fx/_core/formulas/draw/SHAPE-RULES.md`, `RESEARCH-*.md` |
| `lib-fx/_core/` | `README.md` (bản đồ công thức vs kết quả), `formulas/vector/README.md`, `formulas/rules/` (luật + số đo) |
| `tools/studio/README.md` | lệnh chạy Studio (trỏ tới `docs/tools/studio/`) |
| `CLAUDE.md` | quy tắc làm việc và chỉ dẫn ngắn cho từng công cụ |
