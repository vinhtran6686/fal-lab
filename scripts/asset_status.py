"""Show how far every character is, from the Asset manifest in each out/<class>/<id>/brief.md.

Usage:
  python scripts/asset_status.py            overview: one row per character
  python scripts/asset_status.py <id>       one character's manifest, with its next steps

The manifest is the table under the heading "## Asset manifest" (fal-image/format.md §8). Status column:
✅ done, ⏳ waiting for approval, ❌ not made, ⏭ later or skipped. Read-only: nothing is written.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
MARKS = {"✅": "done", "⏳": "wait", "❌": "todo", "⏭": "later"}


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def read_manifest(brief: pathlib.Path) -> list[dict] | None:
    lines = brief.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip().lower() == "## asset manifest")
    except StopIteration:
        return None
    table = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if line.strip().startswith("|"):
            table.append(cells(line))
    if len(table) < 2:
        return []
    head = [h.lower() for h in table[0]]
    col = lambda *names: next((i for i, h in enumerate(head) if h in names), None)
    a, src, kind, st, note = col("asset"), col("từ", "tu", "from"), col("loại", "loai", "kind"), \
        col("trạng thái", "trang thai", "status"), col("ghi chú", "ghi chu", "note")
    rows = []
    for r in table[1:]:
        if set("".join(r)) <= set("-: "):
            continue
        get = lambda i: r[i] if i is not None and i < len(r) else ""
        status = get(st)
        state = next((v for k, v in MARKS.items() if k in status), "todo")
        rows.append({"asset": get(a), "from": get(src), "kind": get(kind), "status": status,
                     "state": state, "note": get(note)})
    return rows


def characters() -> list[tuple[str, str, pathlib.Path, list[dict] | None]]:
    found = []
    for brief in sorted(OUT.glob("*/*/brief.md")):
        found.append((brief.parent.parent.name, brief.parent.name, brief, read_manifest(brief)))
    return found


def next_steps(rows: list[dict], n: int = 3) -> str:
    wait = [r["asset"] for r in rows if r["state"] == "wait"]
    if wait:
        return "duyệt: " + ", ".join(wait[:n])
    todo = [r for r in rows if r["state"] == "todo"]
    # stills before clips: video-sprite needs the approved stills
    todo.sort(key=lambda r: 0 if r["from"].startswith("fal-image") else 1)
    return ", ".join(r["asset"] for r in todo[:n]) + (" ..." if len(todo) > n else "") if todo else "xong"


def overview() -> None:
    chars = characters()
    if not chars:
        print("Chưa có nhân vật nào trong out/ (chưa có brief.md).")
        return
    print("| Nhân vật | Class | Xong | Chờ duyệt | Còn lại | Để sau | Bước tiếp |")
    print("|---|---|---|---|---|---|---|")
    for klass, cid, _, rows in chars:
        if rows is None:
            print(f"| {cid} | {klass} | - | - | - | - | chưa có Asset manifest trong brief.md |")
            continue
        c = {k: sum(r["state"] == k for r in rows) for k in ("done", "wait", "todo", "later")}
        total = len(rows) - c["later"]
        print(f"| {cid} | {klass} | {c['done']}/{total} | {c['wait']} | {c['todo']} | {c['later']} | {next_steps(rows)} |")


def detail(cid: str) -> None:
    match = [c for c in characters() if c[1] == cid]
    if not match:
        sys.exit(f"Không thấy nhân vật '{cid}' trong out/*/*/brief.md")
    klass, _, brief, rows = match[0]
    print(f"**{cid}** ({klass}): {brief.relative_to(ROOT).as_posix()}\n")
    if rows is None:
        print("Chưa có `## Asset manifest` trong brief.md.")
        return
    print("| Asset | Từ | Loại | Trạng thái | Ghi chú |")
    print("|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['asset']} | {r['from']} | {r['kind']} | {r['status']} | {r['note']} |")
    done = sum(r["state"] == "done" for r in rows)
    total = sum(r["state"] != "later" for r in rows)
    print(f"\nXong {done}/{total}. Bước tiếp: {next_steps(rows, 5)}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # the status marks are emoji; Windows consoles default to cp1252
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
    elif len(sys.argv) > 1:
        detail(sys.argv[1])
    else:
        overview()
