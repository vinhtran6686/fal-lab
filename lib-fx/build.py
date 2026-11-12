#!/usr/bin/env python3
"""Render the lib-fx library: every effect on its own (no character), as frames plus a gallery to review them. 0 USD.

Usage (repo root):
  python lib-fx/build.py                         every family in the library
  python lib-fx/build.py force                   every family under a group
  python lib-fx/build.py force/shock             one family (and its gallery)
  python lib-fx/build.py force/shock/drill       one effect
  python lib-fx/build.py --check [path]          build, then exit 1 when an effect FAILS the quality gate (lib-fx/_tools/fxcheck.py)

A variant for a character (another palette, size, side or frame rate; nothing in the library or catalog.json changes):
  python lib-fx/build.py impact/hit/star --pal ice --s 0.8 --mirror --fps 15 --out out/heroes/<id>/frames/fx/hit_ice
    --pal NAME   a palette of _core/formulas/draw/palettes.py (the effect's own extra colours are remapped onto it by lightness)
    --s K        size factor: shapes, frame, anchor and glow all scale by K
    --mirror     faces -x      --fps N   drawn at N frames per second (effects are functions of time: no frame is dropped)
    --name ID    file prefix (default: the effect id)
  writes <out>/frames/@2x and @1x/<name>_NN.png, sheet.png, preview.gif, preview_game.gif, meta.json

A family is a folder holding one module (e.g. force/shock/shock.py). The module exposes
  VARIANTS {id: fn(t, P, front, back)}, CATALOG {id: {name, desc, status, tags}}, TAGS, PAL_SUN, DUR, FRAME, ANCHOR, FPS
(a CATALOG entry may override frame, anchor, dur, palette, glow and halo for that one effect)
and every effect is written next to it: <family>/<id>/sheet.png (one transparent row), frames/<id>_NN.png, preview.gif,
preview_game.gif (game size: @1x shown x3 beside a 60 px body mark; review THIS one) and meta.json (with "qa": the quality gate).
Per family: _gallery/<family with - for />.png (every other frame) and .gif (all effects playing together, real speed).
All effects: catalog.json. Map of the folders: GUIDE.md.
"""
import argparse, importlib.util, inspect, json, math, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_core" / "formulas" / "draw"))
sys.path.insert(0, str(HERE / "_tools"))
from PIL import Image, ImageDraw
import fxcore, palettes
import fxcheck

BG = (34, 38, 36)
STATUS_COL = {"approved": (125, 220, 140), "rework": (255, 110, 150), "draft": (170, 180, 172)}


NOT_LIBRARY = {"research"}   # top-level folders that hold research code, not library families


def families():
    """{family path: module} for every module inside the library (folders starting with _ are not families)."""
    out = {}
    for py in sorted(HERE.rglob("*.py")):
        rel = py.relative_to(HERE)
        if len(rel.parts) < 2 or any(p.startswith(("_", ".")) for p in rel.parts) or rel.parts[0] in NOT_LIBRARY: continue
        fam = rel.parent.as_posix()
        spec = importlib.util.spec_from_file_location("fx_" + fam.replace("/", "_"), py)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        if hasattr(mod, "VARIANTS"): out[fam] = mod
    return out


def frame_of(mod, name):
    """Frame size and anchor: per effect when its CATALOG entry says so, else the family's."""
    c = mod.CATALOG[name]
    return tuple(c.get("frame", mod.FRAME)), tuple(c.get("anchor", mod.ANCHOR))


def palette_of(mod, name):
    """The palette an effect is drawn in: per effect when its CATALOG entry says so ("palette"), else the family's PAL_SUN."""
    return mod.CATALOG[name].get("palette", mod.PAL_SUN)


def glow_of(mod, name):
    """Tint, strength and blur of the soft glow under an effect: CATALOG "glow" / "halo" (alpha, blur), else the family's."""
    c = mod.CATALOG[name]
    return tuple(c.get("glow", palette_of(mod, name)["light"])), tuple(c.get("halo", (getattr(mod, "HALO", 0.45), 8)))


def geometry(mod, name, s=1.0, d=1):
    """Frame size and anchor of an effect drawn at size factor s, facing d (+1 = +x, -1 = mirrored)."""
    (W, H), (ax, ay) = frame_of(mod, name)
    if s != 1.0: W, H, ax, ay = round(W * s), round(H * s), ax * s, ay * s
    if d < 0: ax = W - ax
    return (W, H), (ax, ay)


def render(mod, name, pal=None, s=1.0, d=1, fps=None, speed=1.0):
    """Every frame of an effect (RGBA, @2x). Defaults = the library version. pal: a palette dict (fitted onto the effect's own
    palette keys), s: size factor, d: -1 mirrors, fps: frames per second, speed: time factor (2 = twice as fast).
    The effect is a function of time, so another fps or speed redraws it at those instants instead of dropping frames."""
    fn = mod.VARIANTS[name]; par = inspect.signature(fn).parameters
    (W, H), P = geometry(mod, name, s, d); fps = fps or mod.FPS
    glow, (ha, hb) = glow_of(mod, name)
    kw = {}
    for key, val, off in (("s", s, 1.0), ("d", d, 1)):
        if val != off:
            if key not in par: sys.exit(f"{name}: this effect has no '{key}' parameter (size / mirror not supported yet)")
            kw[key] = val
    if pal is not None:
        if "pal" not in par: sys.exit(f"{name}: this effect has no 'pal' parameter (palette not supported yet)")
        kw["pal"] = palettes.fit(pal, par["pal"].default); glow = tuple(kw["pal"].get("light", glow))
    n = int(math.ceil(mod.CATALOG[name].get("dur", mod.DUR) / speed * fps)) + 1
    frames = []
    for i in range(n):
        fc, bc = fxcore.Canvas(W, H), fxcore.Canvas(W, H)
        fn(i / fps * speed, P, fc, bc, **kw)
        img = bc.done(); img.alpha_composite(fc.done())
        frames.append(fxcore.halo(img, glow, ha, hb * s))
    return frames


def game_gif(frames, path, fps, anchor=None, hold=400):
    """The effect at game size: @1x, shown x3 with hard pixels, next to a mark as tall as a character body (60 px @1x)."""
    W, H = frames[0].size; w, h = W // 2, H // 2; k = 3
    out = []
    for f in frames:
        bg = Image.new("RGBA", (w, h), BG + (255,)); bg.alpha_composite(f.resize((w, h), Image.BOX))
        big = bg.resize((w * k, h * k), Image.NEAREST).convert("RGB")
        dr = ImageDraw.Draw(big); y1 = min(h * k - 4, round((anchor[1] / 2 if anchor else h - 2) * k)); y0 = y1 - 60 * k
        dr.line([(3, max(0, y0)), (3, y1)], fill=(90, 100, 94), width=2)
        for y in (y0, y1):
            if 0 <= y < h * k: dr.line([(0, y), (8, y)], fill=(90, 100, 94), width=2)
        out.append(big)
    fxcore.save_gif(out, path, fps, hold)


def write_effect(fam, mod, name, frames):
    (W, H), anchor = frame_of(mod, name); fps = mod.FPS
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
    fxcore.save_gif([p.convert("RGB") for p in prev], d / "preview.gif", fps, 400)
    game_gif(frames, d / "preview_game.gif", fps, anchor)
    c = mod.CATALOG[name]
    tags = list(dict.fromkeys(list(getattr(mod, "TAGS", [])) + list(c.get("tags", []))))
    meta = {"id": f"{fam}/{name}", "name": c["name"], "desc": c["desc"], "status": c.get("status", "draft"),
            "tags": tags,
            "fps": fps, "frames": len(frames), "frame_size_2x": [W, H], "anchor_2x": list(anchor), "direction": "+x (mirror for -x)",
            "palette": palette_of(mod, name), "files": {"sheet": "sheet.png", "frames": f"frames/{name}_NN.png", "preview": "preview.gif", "preview_game": "preview_game.gif"},
            "qa": fxcheck.check(frames, tags, anchor),
            "source": f"lib-fx/{fam}/{pathlib.Path(mod.__file__).name}: {mod.VARIANTS[name].__name__}"}
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf8")
    return meta


def gallery(fam, mod, rows):
    """A still contact sheet (every other frame) and an animated grid with every effect of the family playing together."""
    W = max(frame_of(mod, n)[0][0] for n, _ in rows); H = max(frame_of(mod, n)[0][1] for n, _ in rows); fps = mod.FPS
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
                cell = Image.new("RGBA", (W, H), BG + (255,)); cell.alpha_composite(fr[i], ((W - fr[i].width) // 2, (H - fr[i].height) // 2)); sheet.paste(cell.convert("RGB"), (lab + c * W, y))
        d.line([(0, y), (sheet.width, y)], fill=(48, 54, 50))
    sheet.save(out / f"{stem}.png")
    k = 1.5; cw, ch = round(W * k), round(H * k)
    anim = []
    for i in range(n):
        g = Image.new("RGB", (cw * len(rows), ch + 40), BG); dg = ImageDraw.Draw(g)
        for r, (name, fr) in enumerate(rows):
            f = fr[min(i, len(fr) - 1)]; cell = Image.new("RGBA", (W, H), BG + (255,)); cell.alpha_composite(f, ((W - f.width) // 2, (H - f.height) // 2))
            g.paste(cell.resize((cw, ch), Image.LANCZOS).convert("RGB"), (r * cw, 0))
            dg.text((r * cw + 12, ch + 8), f"{r + 1}. {mod.CATALOG[name]['name']}", fill=(255, 226, 140), font=f_lab)
        anim.append(g)
    fxcore.save_gif(anim, out / f"{stem}.gif", fps, 700)
    return out / f"{stem}.png"


def write_variant(out, name, frames, fps, anchor, info):
    """A variant for a character: frames @2x and @1x, sheet, previews, meta.json. Nothing of the library is touched."""
    out = pathlib.Path(out); W, H = frames[0].size
    for sub in ("@2x", "@1x"):
        (out / "frames" / sub).mkdir(parents=True, exist_ok=True)
        for old in (out / "frames" / sub).glob("*.png"): old.unlink()
    sheet = Image.new("RGBA", (W * len(frames), H), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        f.save(out / "frames" / "@2x" / f"{name}_{i + 1:02d}.png"); sheet.paste(f, (i * W, 0))
        f.resize((W // 2, H // 2), Image.BOX).save(out / "frames" / "@1x" / f"{name}_{i + 1:02d}.png")
    sheet.save(out / "sheet.png")
    prev = []
    for f in frames:
        bg = Image.new("RGBA", (W, H), BG + (255,)); bg.alpha_composite(f); prev.append(bg.convert("RGB"))
    fxcore.save_gif(prev, out / "preview.gif", fps, 400)
    game_gif(frames, out / "preview_game.gif", fps, anchor)
    qa = fxcheck.check(frames, info.get("tags", ()), anchor)
    meta = dict(info, fps=fps, frames=len(frames), frame_size_2x=[W, H], anchor_2x=[round(anchor[0], 2), round(anchor[1], 2)],
                files={"frames_2x": f"frames/@2x/{name}_NN.png", "frames_1x": f"frames/@1x/{name}_NN.png", "sheet": "sheet.png",
                       "preview": "preview.gif", "preview_game": "preview_game.gif"}, qa=qa)
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf8")
    return qa


def find(fams, want):
    """(family, module, effect id) of one effect path such as impact/hit/star."""
    fam, _, name = want.rpartition("/")
    if fam not in fams or name not in fams[fam].VARIANTS: sys.exit(f"no effect '{want}'. Effects: " + ", ".join(f"{f}/{n}" for f, m in fams.items() for n in m.VARIANTS))
    return fam, fams[fam], name


def main():
    ap = argparse.ArgumentParser(description="Render the lib-fx library, or one effect as a variant for a character (--out).")
    ap.add_argument("path", nargs="?", default="")
    ap.add_argument("--check", action="store_true", help="exit 1 when a built effect fails the quality gate")
    ap.add_argument("--out", help="variant: write ONE effect here instead of into the library")
    ap.add_argument("--pal", help="variant: palette name (" + ", ".join(palettes.PALETTES) + ")")
    ap.add_argument("--s", type=float, default=1.0, help="variant: size factor")
    ap.add_argument("--mirror", action="store_true", help="variant: face -x")
    ap.add_argument("--fps", type=float, help="variant: frames per second")
    ap.add_argument("--speed", type=float, default=1.0, help="variant: time factor (2 = twice as fast)")
    ap.add_argument("--name", help="variant: file prefix")
    a = ap.parse_args()
    want = a.path.strip("/")
    fams = families()
    if a.out:
        fam, mod, name = find(fams, want)
        if a.pal and a.pal not in palettes.PALETTES: sys.exit(f"no palette '{a.pal}'. Palettes: " + ", ".join(palettes.PALETTES))
        d = -1 if a.mirror else 1; fps = a.fps or mod.FPS
        fr = render(mod, name, palettes.PALETTES[a.pal] if a.pal else None, a.s, d, fps, a.speed)
        c = mod.CATALOG[name]
        info = {"id": a.name or name, "effect": f"{fam}/{name}", "name": c["name"], "status_in_library": c.get("status", "draft"),
                "tags": list(dict.fromkeys(list(getattr(mod, "TAGS", [])) + list(c.get("tags", [])))),
                "variant": {"pal": a.pal, "s": a.s, "mirror": a.mirror, "speed": a.speed},
                "direction": "-x" if a.mirror else "+x",
                "rebuild": "python lib-fx/build.py " + " ".join(sys.argv[1:])}
        qa = write_variant(a.out, a.name or name, fr, fps, geometry(mod, name, a.s, d)[1], info)
        print(fxcheck.line(f"{fam}/{name} -> {pathlib.Path(a.out).as_posix()}", qa))
        if a.check and qa["fail"]: sys.exit(1)
        return
    if a.pal or a.s != 1.0 or a.mirror or a.fps or a.speed != 1.0 or a.name: sys.exit("--pal / --s / --mirror / --fps / --speed / --name make a variant: add --out DIR")
    catalog_path = HERE / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf8")) if catalog_path.exists() else {}
    hit = False; bad = 0
    for fam, mod in fams.items():
        if want and not (fam == want or fam.startswith(want + "/") or want.startswith(fam + "/")): continue
        if want.startswith(fam + "/") and any(f != fam and f.startswith(fam + "/") and (want == f or want.startswith(f + "/")) for f in fams):
            continue                                                        # the wanted path belongs to a family nested deeper
        names = [want[len(fam) + 1:]] if want.startswith(fam + "/") else list(mod.VARIANTS)
        if names[0] not in mod.VARIANTS: sys.exit(f"no effect {want}; {fam} has {', '.join(mod.VARIANTS)}")
        hit = True
        if len(names) == len(mod.VARIANTS):                                 # a whole family: drop entries of effects that no longer exist
            catalog = {k: v for k, v in catalog.items() if k.rsplit("/", 1)[0] != fam}   # only this family's own effects
        rows = []
        for name in names:
            fr = render(mod, name); meta = write_effect(fam, mod, name, fr); rows.append((name, fr))
            qa = meta["qa"]; bad += bool(qa["fail"])
            catalog[meta["id"]] = {k: meta[k] for k in ("name", "status", "tags", "desc", "fps", "frames", "frame_size_2x", "anchor_2x")} | {
                "dir": f"{fam}/{name}", "qa": "fail" if qa["fail"] else "warn" if qa["warn"] else "ok"}
            print(fxcheck.line(f"{meta['id']} ({meta['status']})", qa))
        if len(names) == len(mod.VARIANTS):
            print("gallery:", gallery(fam, mod, rows).relative_to(HERE.parent).as_posix())
    if not hit: sys.exit(f"nothing matches '{want}'. Families: {', '.join(fams)}")
    catalog_path.write_text(json.dumps(dict(sorted(catalog.items())), ensure_ascii=False, indent=1), encoding="utf8")
    if bad: print(f"{bad} effect(s) FAIL the quality gate: fix them before setting status approved (lib-fx/README.md, 'Cổng chất lượng')")
    if a.check and bad: sys.exit(1)


if __name__ == "__main__":
    main()
