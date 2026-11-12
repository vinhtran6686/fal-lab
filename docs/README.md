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
├── skills/                                                tài liệu bổ sung cho .claude/skills/<skill>/
│   ├── fal-image/                                         ảnh tĩnh qua scripts/gen_image.py
│   │   ├── fal-image-manual-prompt-style-transfer.md      prompt chuyển concept image sang style của dự án (chế độ --manual)
│   │   └── fal-image-manual-prompt-assets-from-master.md  prompt cho các ảnh còn lại từ master đã duyệt (chế độ --manual)
│   └── video-sprite/                                      animation bằng video qua scripts/fal_video.py
│       └── video-sprite-reference-video-route.md          route video tham chiếu (scripts/make_ref_video.py)
├── scripts/                                               tài liệu cho code trong scripts/
│   ├── puppet_kit/                                        scripts/puppet*.py, scripts/puppet_kit/
│   │   ├── puppet-kit-guide.md                            cách dùng kit: rig, lệnh check/render/track/slash, skin, links
│   │   ├── puppet-kit-motion-recipes.md                   công thức viết anims/*.json (dấu, bảng nhịp, run cycle, checklist)
│   │   ├── puppet-kit-asset-prep-and-rig-v2.md            chuẩn bị tài nguyên, bộ xương 17 xương, Rig Tuner v2, quy tắc mỏ neo, nợ kỹ thuật
│   │   └── puppet-kit-pose-reel.md                        pose reel: clip tư thế cho động tác rig không vẽ được (puppet_reel.py)
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
| `.claude/skills/fal-image/` | `SKILL.md`, `format.md` (style, góc nhìn, thư mục, manifest), `classes/*.md` (hero, ally, enemy, enemy-flying, boss), `reference.md`, `templates.md`, `examples.md` |
| `.claude/skills/video-sprite/` | `SKILL.md`, `references/` (prompt chuyển động), `playtest/`, `scripts/` |
| `lib-fx/` | `README.md` (lệnh, luật nhìn), `GUIDE.md` (bản đồ thư mục), `MINDSET.md`, `lib-fx/_core/formulas/draw/DESIGN.md`, `RECIPE-*.md`, `lib-fx/_core/formulas/draw/SHAPE-RULES.md`, `RESEARCH-*.md` |
| `lib-fx/_core/` | `README.md` (bản đồ công thức vs kết quả), `formulas/vector/README.md`, `formulas/rules/` (luật + số đo) |
| `tools/studio/README.md` | lệnh chạy Studio (trỏ tới `docs/tools/studio/`) |
| `CLAUDE.md` | quy tắc làm việc và chỉ dẫn ngắn cho từng công cụ |
