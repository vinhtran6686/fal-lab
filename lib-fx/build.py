#!/usr/bin/env python3
"""Render the lib-fx library: every effect on its own (no character), as frames plus a gallery to review them. 0 USD.

Usage (repo root):
  python lib-fx/build.py                         every family in the library
  python lib-fx/build.py force                   every family under a group
  python lib-fx/build.py force/shock             one family (and its gallery)
  python lib-fx/build.py force/shock/drill       one effect

A family is a folder holding one module (e.g. force/shock/shock.py). The module exposes
  VARIANTS {id: fn(t, P, front, back)}, CATALOG {id: {name, desc, status, tags}}, TAGS, PAL_SUN, DUR, FRAME, ANCHOR, FPS
and every effect is written next to it: <family>/<id>/sheet.png (one transparent row), frames/<id>_NN.png, preview.gif, meta.json.
Per family: _gallery/<family with - for />.png (every other frame) and .gif (all effects playing together, real speed).
All effects: catalog.json. Map of the folders: GUIDE.md.
"""
import importlib.util, json, math, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_core"))
from PIL import Image, ImageDraw
import fxcore

BG = (34, 38, 36)
STATUS_COL = {"approved": (125, 220, 140), "rework": (255, 110, 150), "draft": (170, 180, 172)}


def families():
    """{family path: module} for every module inside the library (folders starting with _ are not families)."""
    out = {}
    for py in sorted(HERE.rglob("*.py")):
        rel = py.relative_to(HERE)
        if len(rel.parts) < 2 or any(p.startswith(("_", ".")) for p in rel.parts): continue
        fam = rel.parent.as_posix()
        spec = importlib.util.spec_from_file_location("fx_" + fam.replace("/", "_"), py)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        if hasattr(mod, "VARIANTS"): out[fam] = mod
    return out


def render(mod, name):
    (W, H), P, fps = mod.FRAME, mod.ANCHOR, mod.FPS
    n = int(math.ceil(mod.DUR * fps)) + 1
    frames = []
    for i in range(n):
        fc, bc = fxcore.Canvas(W, H), fxcore.Canvas(W, H)
        mod.VARIANTS[name](i / fps, P, fc, bc)
        img = bc.done(); img.alpha_composite(fc.done())
        frames.append(fxcore.halo(img, mod.PAL_SUN["light"], 0.45, 8))
    return frames


def write_effect(fam, mod, name, frames):
    (W, H), fps = mod.FRAME, mod.FPS
    d = HERE / fam / name
    (d / "frames").mkdir(parents=True, exist_ok=True)
    for old in (d / "frames").glob("*.png"): old.unlink()
    sheet = Image.new("RGBA", (W * len(frames), H), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        f.save(d / "frames" / f"{name}_{i + 1:02d}.png"); sheet.paste(f, (i * W, 0))
    sheet.save(d / "sheet.png")
    prev = []
    for f in frames:
        bg = Image.new("RGBA", (W, H), BG + (255,)); bg.alpha_composite(f); prev.append(bg.resize((W * 2, H * 2), Image.LANCZOS))
    prev[0].save(d / "preview.gif", save_all=True, append_images=prev[1:], duration=[round(1000 / fps)] * (len(prev) - 1) + [400], loop=0, disposal=2)
    c = mod.CATALOG[name]
    meta = {"id": f"{fam}/{name}", "name": c["name"], "desc": c["desc"], "status": c.get("status", "draft"),
            "tags": list(dict.fromkeys(list(getattr(mod, "TAGS", [])) + list(c.get("tags", [])))),
            "fps": fps, "frames": len(frames), "frame_size_2x": [W, H], "anchor_2x": list(mod.ANCHOR), "direction": "+x (mirror for -x)",
            "palette": mod.PAL_SUN, "files": {"sheet": "sheet.png", "frames": f"frames/{name}_NN.png", "preview": "preview.gif"},
            "source": f"lib-fx/{fam}/{pathlib.Path(mod.__file__).name}: {mod.VARIANTS[name].__name__}"}
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf8")
    return meta


def gallery(fam, mod, rows):
    """A still contact sheet (every other frame) and an animated grid with every effect of the family playing together."""
    (W, H), fps = mod.FRAME, mod.FPS
    out = HERE / "_gallery"; out.mkdir(exist_ok=True)
    stem = fam.replace("/", "-")
    f_lab, f_small = fxcore.font(22), fxcore.font(15)
    n = max(len(fr) for _, fr in rows); cols = list(range(0, n, 2)); lab = 200
    sheet = Image.new("RGB", (lab + W * len(cols), 30 + H * len(rows)), BG)
    d = ImageDraw.Draw(sheet)
    for c, i in enumerate(cols): d.text((lab + c * W + 6, 6), f"{i + 1:02d}  {i / fps:.2f}s", fill=(150, 160, 152), font=f_small)
    for r, (name, fr) in enumerate(rows):
        y, st = 30 + r * H, mod.CATALOG[name].get("status", "draft")
        d.text((14, y + H // 2 - 34), f"{r + 1}. {mod.CATALOG[name]['name']}", fill=(255, 226, 140), font=f_lab)
        d.text((14, y + H // 2 - 4), f"{fam}/{name}", fill=(150, 160, 152), font=f_small)
        d.text((14, y + H // 2 + 16), st, fill=STATUS_COL.get(st, STATUS_COL["draft"]), font=f_small)
        for c, i in enumerate(cols):
            if i < len(fr):
                cell = Image.new("RGBA", (W, H), BG + (255,)); cell.alpha_composite(fr[i]); sheet.paste(cell.convert("RGB"), (lab + c * W, y))
        d.line([(0, y), (sheet.width, y)], fill=(48, 54, 50))
    sheet.save(out / f"{stem}.png")
    k = 1.5; cw, ch = round(W * k), round(H * k)
    anim = []
    for i in range(n):
        g = Image.new("RGB", (cw * len(rows), ch + 40), BG); dg = ImageDraw.Draw(g)
        for r, (name, fr) in enumerate(rows):
            cell = Image.new("RGBA", (W, H), BG + (255,)); cell.alpha_composite(fr[min(i, len(fr) - 1)])
            g.paste(cell.resize((cw, ch), Image.LANCZOS).convert("RGB"), (r * cw, 0))
            dg.text((r * cw + 12, ch + 8), f"{r + 1}. {mod.CATALOG[name]['name']}", fill=(255, 226, 140), font=f_lab)
        anim.append(g)
    anim[0].save(out / f"{stem}.gif", save_all=True, append_images=anim[1:], duration=[round(1000 / fps)] * (n - 1) + [700], loop=0)
    return out / f"{stem}.png"


def main():
    want = sys.argv[1].strip("/") if len(sys.argv) > 1 else ""
    fams = families()
    catalog_path = HERE / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf8")) if catalog_path.exists() else {}
    hit = False
    for fam, mod in fams.items():
        if want and not (fam == want or fam.startswith(want + "/") or want.startswith(fam + "/")): continue
        names = [want[len(fam) + 1:]] if want.startswith(fam + "/") else list(mod.VARIANTS)
        if names[0] not in mod.VARIANTS: sys.exit(f"no effect {want}; {fam} has {', '.join(mod.VARIANTS)}")
        hit = True
        if len(names) == len(mod.VARIANTS):                                 # a whole family: drop entries of effects that no longer exist
            catalog = {k: v for k, v in catalog.items() if not k.startswith(fam + "/")}
        rows = []
        for name in names:
            fr = render(mod, name); meta = write_effect(fam, mod, name, fr); rows.append((name, fr))
            catalog[meta["id"]] = {k: meta[k] for k in ("name", "status", "tags", "desc", "fps", "frames", "frame_size_2x", "anchor_2x")} | {"dir": f"{fam}/{name}"}
            print(f"{meta['id']}: {len(fr)} frames ({meta['status']})")
        if len(names) == len(mod.VARIANTS):
            print("gallery:", gallery(fam, mod, rows).relative_to(HERE.parent).as_posix())
    if not hit: sys.exit(f"nothing matches '{want}'. Families: {', '.join(fams)}")
    catalog_path.write_text(json.dumps(dict(sorted(catalog.items())), ensure_ascii=False, indent=1), encoding="utf8")


if __name__ == "__main__":
    main()
