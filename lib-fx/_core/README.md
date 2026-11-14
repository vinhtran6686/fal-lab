# lib-fx/_core: công thức và kết quả

Hai nhánh, không trộn: **formulas** là thứ chạy được hoặc là luật để dựng hiệu ứng; **results** là thứ đã dựng ra để xem và đối chiếu.

```
_core/
├── formulas/                       CÔNG THỨC
│   ├── draw/                       bộ vẽ fx bằng code: fxcore.py (nét, lớp, xuất frame), palettes.py (bảng màu 5 bậc), organic.py (hình vẽ tay), fieldfx.py (lớp màu cắt từ một trường liên tục)
│   │                               dùng bởi mọi hiệu ứng trong thư viện (nhóm/họ/id) qua lib-fx/build.py
│   │                               fxkit/ (hệ thống dựng hiệu ứng theo lớp: không gian a → b, vòng đời lớp, biến thiên theo seed, tô tông phẳng, các loại lớp trong layers/), hướng dẫn FXKIT.md
│   │                               kèm tài liệu: DESIGN.md, SHAPE-RULES.md, RESEARCH-organic-impact.md, recipes/RECIPE-*.md (công thức từng hiệu ứng mẫu)
│   ├── vector/                     bộ dựng lại hiệu ứng vẽ tay từ GIF thành path Bézier (README.md, CLI lib-fx/_tools/vectorfx.py)
│   │   └── profiles/               một file JSON cho mỗi hiệu ứng mẫu (swirl-slash, element-trio, slash-trio)
│   └── rules/                      luật thiết kế đã đo (01-05), REFERENCE-GIF.md (cách học một GIF mẫu), số đo gốc (data/), luật theo loại VFX (vfx/slash, vfx/explosion)
└── results/                        KẾT QUẢ
    ├── vector-showcase/            hiệu ứng dựng lại từ mẫu (compare.gif, frames, svg) và hiệu ứng sinh mới (generated/)
    └── bezier-research/            số đo và demo gốc của phương pháp Bézier (FINDINGS.md, ảnh so sánh, out/)
```

Mẫu tham khảo gốc: `ref/vfx/`. Kết quả dựng lại xuất bằng `python lib-fx/_tools/vectorfx.py showcase PROFILE` (vào `results/vector-showcase/`).
Thư viện hiệu ứng dùng được cho game nằm ngoài `_core`: `lib-fx/<nhóm>/<họ>/<id>/`.
