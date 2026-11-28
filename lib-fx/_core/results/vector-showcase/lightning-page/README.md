# Trang xem bộ sét (Lightning-2 Remake)

Nguồn của trang artifact https://claude.ai/artifact/4cbfa2MD123GvG3iVK3ubb: so sánh ba bản remake `lightning-2`, bản remake Prism Spark
(`lightning-3`), "Xưởng sét" (6 dáng × 5 màu) và Charge v2 (Prism Spark quanh thân, 5 màu).

- `index.html`: trang (HTML tĩnh, không thư viện ngoài; nhớ dáng / màu đã chọn bằng localStorage).
- `files.json`: tên file trang dùng → đường dẫn trong repo (mọi GIF đã có trong git: `lightning-2/*/compare.gif`,
  `lightning-3/spark/compare.gif`, `generated/gen-lightning-<dáng>-blue/preview*.gif` và `colours/<màu>*.gif`).

Đăng lại (Claude Code, Artifact tool): publish `index.html` với `url` ở trên và `files` = nội dung `files.json`. Tạo lại GIF: lệnh trong
`lib-fx/_core/formulas/rules/vfx/lightning/README.md` §8.
