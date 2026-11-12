# Quy tắc cấu trúc repo

Bắt buộc cho người và AI. Trước khi tạo file hoặc thư mục mới, tìm hàng phù hợp trong §2. Không có hàng phù hợp thì hỏi người dùng, đừng tự mở thư mục mới ở gốc repo.

## 1. Bản đồ

```
fal-image-lab/
├── CLAUDE.md                chỉ dẫn ngắn cho AI: quy tắc, lệnh, trỏ tới docs/. Không chứa tài liệu dài
├── README.md                giới thiệu và cài đặt cho người
├── .claude/
│   ├── skills/<skill>/      MỘT việc cho mỗi skill (SKILL.md + tài liệu và script của riêng skill)
│   └── agents/              subagent của Claude Code
├── scripts/                 lệnh dòng lệnh của pipeline (ảnh, video, puppet, fx, quản lý asset)
├── tools/<tool>/            ứng dụng có giao diện hoặc server cục bộ (studio, frame_tuner)
├── lib-fx/                  thư viện hiệu ứng (fx) và công thức dựng fx
│   ├── <nhóm>/<họ>/<id>/   KẾT QUẢ dùng được cho game: mỗi hiệu ứng một thư mục
│   ├── _core/formulas/      CÔNG THỨC: draw/ (code vẽ + tài liệu), vector/ (bộ dựng lại từ mẫu), rules/ (luật đo được)
│   ├── _core/results/       KẾT QUẢ học được: dựng lại từ mẫu, số đo gốc
│   ├── _tools/              dòng lệnh riêng của lib-fx
│   └── _gallery/ _study/    sinh ra từ code, git bỏ qua
├── ref/                     tài liệu tham khảo (chỉ đọc, không phải asset của game)
├── out/                     mọi thứ sinh ra: nhân vật, chi phí (xem §5)
└── docs/                    tài liệu, cây phản chiếu repo (xem §4)
```

## 2. Đặt cái mới vào đâu

| Bạn tạo | Đặt ở | Ghi chú |
|---|---|---|
| Lệnh dòng lệnh cho pipeline nhân vật (ảnh, video, rig, quản lý asset) | `scripts/` | Cùng họ với file có sẵn thì đặt cạnh chúng (rig: `scripts/puppet_kit/`, vệt chém: `scripts/slash_fx/`). Họ mới thì tạo thư mục con `scripts/<họ>/`, không thả thêm file lẻ vào gốc `scripts/` |
| Ứng dụng có giao diện web hoặc server cục bộ | `tools/<tên_tool>/` | Tên thư mục dùng gạch dưới, giống Python. Mỗi tool có `README.md` ngắn (lệnh chạy) trỏ tới doc đầy đủ |
| Việc mới mà AI làm theo quy trình riêng | `.claude/skills/<skill>/` | Một skill một việc. Phần dùng chung giữa các skill thì không nhân đôi, hãy để một chỗ và trỏ tới |
| Hiệu ứng dùng được cho game | `lib-fx/<nhóm>/<họ>/<id>/` | Chạy `python lib-fx/build.py <nhóm>/<họ>`. Hiệu ứng vào thư viện trước, nhân vật lấy từ đó ra (không tạo fx riêng trong thư mục nhân vật nếu dùng chung được) |
| Code vẽ fx dùng chung | `lib-fx/_core/formulas/draw/` | Chỉ code dùng chung. Không để một hiệu ứng cụ thể nằm ở đây |
| Công thức, luật hoặc bài học đo được về cách dựng fx | `lib-fx/_core/formulas/rules/` hoặc `.../draw/` (tài liệu) và `.../draw/recipes/` (công thức từng hiệu ứng) | Công thức = thứ cho phép dựng lại được. Mỗi luật kèm số đo |
| Dựng lại từ mẫu tham khảo (GIF) | profile vào `lib-fx/_core/formulas/vector/profiles/`, kết quả vào `lib-fx/_core/results/vector-showcase/` | Xuất bằng `python lib-fx/_tools/vectorfx.py showcase PROFILE` |
| Kết quả nghiên cứu, số đo | `lib-fx/_core/results/<tên>/` | Chỉ giữ số đo và demo. Quá trình, nhật ký, brief, bản v1/v2/v3 không được giữ |
| Nhân vật, ảnh, clip, frame, fx của nhân vật | `out/<class>/<id>/` | Cấu trúc ở §5 |
| Tài liệu | `docs/` | Theo §4 |
| Ảnh hoặc clip tham khảo từ bên ngoài | `ref/<chủ đề>/` | Chỉ đọc. Gửi vào API chỉ khi người dùng yêu cầu |
| Thử nghiệm một lần | Không commit vào repo. Dùng thư mục tạm hoặc `out/<...>/.work/` (git bỏ qua) | Thử xong mà dùng lại được thì đưa vào hàng đúng ở trên, không để thành `experiments/` |

## 3. Đặt tên

- Thư mục trong code: chữ thường, gạch dưới (`puppet_kit`, `frame_tuner`). Thư mục trong `docs/` **trùng tên** thư mục repo nó mô tả (`docs/tools/frame_tuner/`).
- File doc: `<đối-tượng>-<chủ-đề>.md`, chữ thường, gạch ngang (`puppet-kit-motion-recipes.md`). Đọc tên là biết nội dung, không đặt tên chung chung như `notes.md`, `plan.md`, `report.md`, `new.md`.
- Không đặt tên theo tiến trình (`milestone-01`, `v2-final`, `draft`, `todo`). Phiên bản chỉ xuất hiện ở asset (`_vNN`).
- Mỗi tool có tên chỉ phương pháp, không gắn với một nhân vật hay một hiệu ứng riêng. Dữ liệu riêng của một hiệu ứng nằm trong một file profile hoặc params, không nằm trong code.
- Code không chứa hằng số của riêng một nhân vật. Đặt chúng trong file `*.json` bên cạnh asset (ví dụ `weapon_marks.json`, `slash_params.json`). Nếu chưa tách được thì ghi rõ trong doc của quy trình đó (hiện còn ở `build_crescent.py` của `azure_blade`).

## 4. Docs

1. **Một doc ứng với một đối tượng cụ thể trong repo** (một tool, một skill, một họ script, một quy trình xuyên nhiều công cụ). Không có đối tượng thì không có doc.
2. Đường dẫn trong `docs/` phản chiếu repo: `docs/scripts/<thư mục>/`, `docs/tools/<tool>/`, `docs/skills/<skill>/`, `docs/pipeline/` (quy trình xuyên nhiều công cụ).
3. Mọi doc có trong cây ở `docs/README.md`. Thêm doc thì thêm dòng vào cây. Xoá doc thì xoá dòng.
4. Doc của `lib-fx` nằm trong `lib-fx/` (xem `lib-fx/_core/README.md`). Đừng tạo `docs/lib-fx/`.
5. Doc mô tả **cách dùng và lý do hiện tại**. Không ghi: nhật ký phiên, bảng tiến độ, kế hoạch đã xong, báo cáo thử nghiệm, kết quả "chờ duyệt". Thông tin đó thuộc git, `history.md` của nhân vật, hoặc issue tracker.
6. Sửa tool thì sửa doc của tool trong cùng thay đổi. Doc sai còn hại hơn thiếu doc.
7. Không dán lại nội dung ở nhiều doc. Có một chỗ chính thì chỗ khác chỉ trỏ tới.
8. Khi đổi tên hoặc xoá doc, file hay thư mục: tìm và sửa mọi tham chiếu (`grep -rn "tên-cũ" .`) trước khi xong.

## 5. Nhân vật và asset (`out/`)

- `out/<class>/<id>/` có `brief.md` (yêu cầu, lựa chọn, manifest), `history.md`, `meta.json`, `source/` (bản gốc đã duyệt: `design/`, `video/`, `rig/`, `vfx/`) và `frames/` (cắt từ source: mỗi sheet một thư mục). `.work/` là phần công cụ, không vào git.
- Một phiên chốt một bước: dọn bản không duyệt bằng `scripts/source_prune.py` (và `video_prune.py` với clip). Không giữ "để chọn lại sau".
- Không giữ nhân vật bỏ dở hoặc thử nghiệm đã xong. Nhân vật mẫu giữ lại phải có `brief.md` với manifest cập nhật.
- `out/costs.csv` là nhật ký chi phí duy nhất, không thêm nơi ghi chi phí khác.

## 6. Skill

- Mỗi skill có `SKILL.md` ngắn gọn (khi nào dùng, quy trình, luật), phần chi tiết đặt trong `references/`, `scripts/` của chính skill đó.
- Skill không chứa dữ liệu của nhân vật và không chứa bài học của một lần chạy. Bài học chung vào luật của skill, bài học riêng vào `history.md` của nhân vật.
- Skill gọi script trong `scripts/` bằng đường dẫn đầy đủ từ gốc repo. Khi di chuyển script phải sửa cả skill.

## 7. Ngoại lệ hiện có (không mở rộng thêm)

| Chỗ | Lý do |
|---|---|
| `scripts/` còn nhiều file lẻ (`gen_image.py`, `fal_video.py`, `video_to_sheet.py`, `puppet.py`, ...) | Lệnh này được gọi bằng đường dẫn cố định từ skill và CLAUDE.md. Chỉ chuyển vào thư mục con khi sửa đồng thời mọi chỗ gọi |
| `scripts/puppet_kit/rig_tuner.html` là một trang giao diện nhưng nằm trong `scripts/` | Đi cùng engine `core.py`. Nếu mở rộng thành ứng dụng thì chuyển sang `tools/` |
| `lib-fx/_tools/` | Dòng lệnh riêng của lib-fx. Dòng lệnh dùng cho cả repo thì đặt ở `scripts/` |
| `.claude/agents/` có agent chung (`search`, `grep`, `docs`) | Dùng chung cho mọi việc, không gắn với một skill |

## 8. Checklist trước khi kết thúc việc có tạo file mới

- [ ] File nằm đúng hàng ở §2? Có file hoặc thư mục tương tự đã có để dùng lại không?
- [ ] Tên theo §3, không theo tiến trình hay nhân vật?
- [ ] Có doc cần viết hoặc sửa? Đã thêm vào cây `docs/README.md`?
- [ ] Không còn file tạm, bản thử nghiệm hay báo cáo phiên nằm lại trong repo?
- [ ] Mọi đường dẫn tham chiếu (CLAUDE.md, skill, doc, import) vẫn đúng?
