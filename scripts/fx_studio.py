#!/usr/bin/env python3
"""Fx Studio engine: a sprite sheet of a 2D effect -> game frames for Kingdom Rush 1 (LOVE 0.10.2), optionally redrawn
through vectors, then packed into the game and playable there (F6/F7). The editor page is tools/fx_studio/ (fx_studio.bat).

Usage:
  python scripts/fx_studio.py import <sheet.png> --id fire_breath [--grid 3x3] [--bg auto|black|alpha|magenta] [--force]
  python scripts/fx_studio.py render <id> [--set scale=0.6 --set mode=vector --set anchor=0.04,0.45 ...]
  python scripts/fx_studio.py install <id> [<id> ...] [--game DIR]   pack go_fx_lab (fullhd + ipad) and register in the game
  python scripts/fx_studio.py uninstall <id> [<id> ...] | --all      remove from the game (the last one removes every trace)
  python scripts/fx_studio.py install-pack <key>.fxskill.zip [--game DIR]  a skill (or <id>.fxpack.zip, one effect) from the app
  python scripts/fx_studio.py install-pack <assets dir> --skill skills/<key>.json  the same, from the app's saved data
  python scripts/fx_studio.py list

Asset folder out/vfx/<id>/ (fal-image format.md section 4):
  design/sheet_vNN.png     the imported sheet, every version
  fx.json                  the recipe: everything render and install need (edited by hand, with --set or by the page)
  .work/cells/cell_NN.png  each cell of the sheet with the background removed (straight alpha, source px), for the page
  game/                    the ONE current export: frames/@2x, frames/@1x (= the game's fullhd), frames/ipad (x 768/1080),
                           svg/ (vector mode), manifest.json (ref/hero format), preview.gif (over a KR map, a hero for scale), sheet.png

Recipe (fx.json):
  source        design/sheet_vNN.png;  bg  black (fire painted on black: alpha = brightest channel) | alpha | magenta
  black_floor   channel value (0-1) that still counts as background on a black sheet, so dark noise does not become specks
  cells         [[x0, y0, x1, y1], ...] boxes in the sheet; every cell is cropped at the size of the largest
  frames        [{"cell": 0, "hold": 2}, ...] drawings in play order; hold = game frames at 30 fps (2 = "on twos", KR style)
  scale         sheet px -> @1x (fullhd) px.  anchor  [x, y] in the cell, fractions from the LEFT and the TOP (the
                emission point: a breath's mouth, an explosion's centre); install converts y to the game's bottom-up anchor
  mode          raster (default: the sheet as drawn, soft glow kept) | vector (flat core traced with vtracer, glow redrawn)
  color         hue (degrees), saturation, brightness, alpha multipliers, applied to every mode
  vector        colors, core (alpha that counts as the flat core), glow_radius (sheet px), glow_strength, glow_color (null = from the sheet)
  game          name (template, animation and frame prefix, default fx_<id>), z (Z_EFFECTS | Z_OBJECTS | Z_DECALS),
                loop, runs (plays before the fx removes itself), installed
"""
import argparse, colorsys, datetime, io, json, os, pathlib, re, shutil, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
VFX = ROOT / "out" / "vfx"
GAME_DIR = pathlib.Path(os.environ.get("KR1_GAME_DIR", r"E:\work\reverse\games\kr1"))
FPS = 30
IPAD = 768 / 1080            # TEXTURE_SIZE_ALIAS.ipad / fullhd (all/constants.lua)
GROUP = "go_fx_lab"          # the atlas group every installed effect is packed into
MARK = "fx_lab"              # marker of every line or block install writes into the game
SIZES = {"@2x": 2.0, "@1x": 1.0, "ipad": IPAD}


# ---------------------------------------------------------------- recipe
def asset(fx_id: str) -> pathlib.Path:
    return VFX / fx_id


def load(fx_id: str) -> dict:
    p = asset(fx_id) / "fx.json"
    if not p.exists():
        sys.exit(f"no recipe {p}: run import first")
    return json.loads(p.read_text(encoding="utf-8"))


def save(r: dict) -> None:
    (asset(r["id"]) / "fx.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def defaults(fx_id: str) -> dict:
    return {"version": 1, "id": fx_id, "source": None, "bg": "black", "black_floor": 0.05, "grid": None, "cells": [],
            "frames": [], "scale": 1.0, "anchor": [0.5, 0.5], "mode": "raster",
            "color": {"hue": 0, "saturation": 1.0, "brightness": 1.0, "alpha": 1.0},
            "vector": {"colors": 4, "core": 0.6, "glow_radius": 7, "glow_strength": 1.5, "glow_color": None},
            "game": {"name": f"fx_{fx_id}", "z": "Z_EFFECTS", "loop": False, "runs": 1, "installed": False}}


def recipe_hash(r: dict) -> str:
    """What the export depends on: the recipe without the install flag."""
    import hashlib
    g = dict(r.get("game", {})); g.pop("installed", None)
    return hashlib.sha1(json.dumps({**r, "game": g}, sort_keys=True).encode()).hexdigest()[:12]


def set_value(r: dict, key: str, text: str) -> None:
    """--set a.b=value: JSON when it parses (numbers, true, null, [..]), x,y -> [x, y], otherwise a string."""
    try:
        v = json.loads(text)
    except ValueError:
        v = [float(t) for t in text.split(",")] if re.fullmatch(r"[-\d.]+(,[-\d.]+)+", text) else text
    node, parts = r, key.split(".")
    for p in parts[:-1]:
        node = node.setdefault(p, {})
    node[parts[-1]] = v


# ---------------------------------------------------------------- sheet -> straight-alpha cells
def detect_bg(im: Image.Image) -> str:
    a = np.asarray(im.convert("RGBA"))
    if (a[..., 3] < 250).mean() > 0.05:
        return "alpha"
    corners = np.concatenate([a[:4, :4, :3].reshape(-1, 3), a[-4:, -4:, :3].reshape(-1, 3),
                              a[:4, -4:, :3].reshape(-1, 3), a[-4:, :4, :3].reshape(-1, 3)]).mean(0)
    if corners.max() < 30:
        return "black"
    if corners[0] > 200 and corners[1] < 80 and corners[2] > 200:
        return "magenta"
    sys.exit(f"background not recognised (corner colour {corners.round()}): pass --bg")


def straight(im: Image.Image, bg: str, floor: float) -> np.ndarray:
    """Sheet -> float RGBA with straight alpha. black: the effect was painted as light on black, so alpha is the
    brightest channel (minus a small floor) and the colour is un-multiplied; magenta: chroma key with soft edges."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32) / 255
    rgb = a[..., :3]
    if bg == "alpha":
        return a
    if bg == "black":
        m = rgb.max(2)
        alpha = np.clip((m - floor) / max(1e-6, 1 - floor), 0, 1)
        col = np.where(m[..., None] > 1e-4, rgb / np.maximum(m, 1e-4)[..., None], 0)
        return np.dstack([col, alpha])
    if bg == "magenta":
        key = np.array([1.0, 0.0, 1.0])
        d = np.sqrt(((rgb - key) ** 2).sum(2)) / np.sqrt(3)
        alpha = np.clip((d - 0.12) / 0.2, 0, 1)
        # remove the magenta spill from soft edges: pull the green channel up to the red/blue mean where keyed
        col = rgb.copy()
        spill = np.minimum(col[..., 0], col[..., 2]) - col[..., 1]
        col[..., 0] -= np.clip(spill, 0, None) * (1 - alpha)
        col[..., 2] -= np.clip(spill, 0, None) * (1 - alpha)
        return np.dstack([np.clip(col, 0, 1), alpha])
    sys.exit(f"unknown bg {bg}")


def runs(occ: np.ndarray, gap: int) -> list:
    """Occupied index ranges [start, end), merging holes narrower than gap."""
    out, s = [], None
    for i, v in enumerate(occ):
        if v and s is None:
            s = i
        if not v and s is not None:
            out.append([s, i]); s = None
    if s is not None:
        out.append([s, len(occ)])
    merged = []
    for r in out:
        if merged and r[0] - merged[-1][1] < gap:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return merged


def find_cells(sa: np.ndarray, grid: tuple | None) -> tuple:
    """-> (grid [cols, rows], boxes in reading order with content). Equal cells keep the artist's placement."""
    h, w = sa.shape[:2]
    occ = sa[..., 3] > 0.1
    if grid is None:
        rr = runs(occ.any(1), max(4, h // 60))
        cc = runs(occ.any(0), max(4, w // 60))
        grid = (len(cc), len(rr))
        if not grid[0] or not grid[1]:
            sys.exit("the sheet is empty after removing the background")
    cols, rows = grid
    cw, ch = w / cols, h / rows
    boxes = []
    for r in range(rows):
        for c in range(cols):
            b = [round(c * cw), round(r * ch), round((c + 1) * cw), round((r + 1) * ch)]
            if occ[b[1]:b[3], b[0]:b[2]].sum() > 20:
                boxes.append(b)
    return [cols, rows], boxes


def cell_canvas(r: dict) -> tuple:
    return (max(b[2] - b[0] for b in r["cells"]), max(b[3] - b[1] for b in r["cells"]))


def cells(r: dict) -> list:
    """Every cell as float RGBA (straight alpha) on the common cell canvas."""
    sa = straight(Image.open(asset(r["id"]) / r["source"]), r["bg"], r["black_floor"])
    cw, ch = cell_canvas(r)
    out = []
    for b in r["cells"]:
        c = np.zeros((ch, cw, 4), np.float32)
        crop = sa[b[1]:b[3], b[0]:b[2]]
        c[:crop.shape[0], :crop.shape[1]] = crop
        out.append(despeckle(c))
    return out


def despeckle(c: np.ndarray, min_px: int = 12) -> np.ndarray:
    """Drop specks (JPEG dust on a black sheet, stray key pixels) so they neither show in game nor widen the atlas trim."""
    from scipy import ndimage
    lab, n = ndimage.label(c[..., 3] > 0)
    if n:
        area = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
        small = np.isin(lab, np.nonzero(area < min_px)[0] + 1)
        c[small] = 0
    return c


def to_image(a: np.ndarray) -> Image.Image:
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")


def to_array(im: Image.Image) -> np.ndarray:
    return np.asarray(im.convert("RGBA")).astype(np.float32) / 255


# ---------------------------------------------------------------- colour
def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rc = np.where(m & (mx == r), ((g - b) / np.where(m, d, 1)) % 6, 0)
    gc = np.where(m & (mx == g) & (mx != r), (b - r) / np.where(m, d, 1) + 2, 0)
    bc = np.where(m & (mx == b) & (mx != r) & (mx != g), (r - g) / np.where(m, d, 1) + 4, 0)
    h = (rc + gc + bc) / 6
    s = np.where(mx > 1e-6, d / np.where(mx > 1e-6, mx, 1), 0)
    return np.stack([h % 1, s, mx], -1)


def hsv_to_rgb(hsv):
    h, s, v = hsv[..., 0] * 6, hsv[..., 1], hsv[..., 2]
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    sel = [np.stack(x, -1) for x in ((v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q))]
    out = np.zeros(hsv.shape, np.float32)
    for k in range(6):
        out = np.where((i == k)[..., None], sel[k], out)
    return out


def recolor(a: np.ndarray, c: dict) -> np.ndarray:
    """Same maths as the page (tools/fx_studio/index.html recolor): HSV hue shift, saturation and value multipliers."""
    if c.get("hue", 0) == 0 and c.get("saturation", 1) == 1 and c.get("brightness", 1) == 1 and c.get("alpha", 1) == 1:
        return a
    hsv = rgb_to_hsv(a[..., :3])
    hsv[..., 0] = (hsv[..., 0] + c.get("hue", 0) / 360) % 1
    hsv[..., 1] = np.clip(hsv[..., 1] * c.get("saturation", 1), 0, 1)
    hsv[..., 2] = np.clip(hsv[..., 2] * c.get("brightness", 1), 0, 1)
    out = a.copy()
    out[..., :3] = hsv_to_rgb(hsv)
    out[..., 3] = np.clip(a[..., 3] * c.get("alpha", 1), 0, 1)
    return out


def recolor_hex(hexcode: str, c: dict) -> str:
    px = np.array([[[int(hexcode[i:i + 2], 16) / 255 for i in (1, 3, 5)] + [1.0]]], np.float32)
    v = recolor(px, c)[0, 0, :3]
    return "#" + "".join(f"{round(x * 255):02x}" for x in v)


# ---------------------------------------------------------------- vector mode
def vector_palette(cs: list, vec: dict) -> np.ndarray:
    """One palette for every frame (shared, so colours do not flicker between frames); near-identical entries merged."""
    px = np.concatenate([c[c[..., 3] >= vec["core"]][:, :3] for c in cs])
    if not len(px):
        sys.exit("vector mode: no pixel reaches the core alpha; lower vector.core")
    img = Image.fromarray((px.reshape(-1, 1, 3) * 255).astype(np.uint8))
    q = img.quantize(int(vec["colors"]), method=Image.Quantize.MEDIANCUT)
    pal = np.array(q.getpalette()[:3 * int(vec["colors"])], np.float32).reshape(-1, 3)
    keep = []
    for p in pal:
        if all(np.abs(p - k).sum() > 36 for k in keep):
            keep.append(p)
    return np.array(keep)


def trace_cell(c: np.ndarray, pal: np.ndarray, vec: dict) -> str:
    """Flat core of one cell -> SVG (vtracer). Traced on a smooth 4x upscale so the curves follow the shape, not the pixels."""
    import vtracer
    from scipy import ndimage
    h, w = c.shape[:2]
    up = to_array(to_image(c).resize((w * 4, h * 4), Image.BICUBIC))
    mask = up[..., 3] >= vec["core"]
    mask = ndimage.binary_closing(ndimage.binary_opening(mask, iterations=2), iterations=2)
    d = ((up[..., None, :3] * 255 - pal[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1)
    # majority filter on the label map: removes speckles inside flat areas (fast: one blurred plane per label)
    planes = np.stack([ndimage.uniform_filter((idx == k).astype(np.float32), 7) for k in range(len(pal))], -1)
    idx = planes.argmax(-1)
    out = np.zeros((h * 4, w * 4, 4), np.uint8)
    out[..., :3] = pal[idx].astype(np.uint8)
    out[..., 3] = mask * 255
    buf = io.BytesIO(); Image.fromarray(out).save(buf, "PNG")
    svg = vtracer.convert_raw_image_to_svg(buf.getvalue(), img_format="png", colormode="color", hierarchical="stacked",
                                           mode="spline", filter_speckle=24, color_precision=6, layer_difference=24,
                                           corner_threshold=60, length_threshold=6.0, splice_threshold=45, path_precision=2)
    # a viewBox in the traced (4x) units, so the same file renders at any size
    return re.sub(r'<svg ([^>]*?)width="(\d+)" height="(\d+)"', r'<svg \1width="\2" height="\3" viewBox="0 0 \2 \3"', svg, count=1)


def render_svg(svg: str, w: int, h: int) -> np.ndarray:
    import resvg_py
    svg = re.sub(r'(<svg [^>]*?)width="\d+" height="\d+"', rf'\1width="{w}" height="{h}"', svg, count=1)
    return to_array(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg)))))


def glow_colour(cs: list, vec: dict) -> np.ndarray:
    if vec.get("glow_color"):
        g = vec["glow_color"].lstrip("#")
        return np.array([int(g[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
    px = np.concatenate([c[(c[..., 3] > 0.08) & (c[..., 3] < vec["core"])] for c in cs])
    if not len(px):
        return np.array([1.0, 0.3, 0.0], np.float32)
    return (px[:, :3] * px[:, 3:]).sum(0) / px[:, 3].sum()


def with_glow(core: np.ndarray, colour: np.ndarray, radius: float, strength: float) -> np.ndarray:
    a = Image.fromarray((core[..., 3] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(0.5, radius)))
    ga = np.clip(np.asarray(a).astype(np.float32) / 255 * strength, 0, 1)
    out = np.zeros_like(core)
    ca = core[..., 3:]
    out[..., 3] = ca[..., 0] + ga * (1 - ca[..., 0])
    out[..., :3] = (core[..., :3] * ca + colour * (ga * (1 - ca[..., 0]))[..., None]) / np.maximum(out[..., 3:], 1e-6)
    return out


# ---------------------------------------------------------------- render
def canvas_sizes(r: dict) -> dict:
    cw, ch = cell_canvas(r)
    one = (max(1, round(cw * r["scale"])), max(1, round(ch * r["scale"])))
    return {k: (max(1, round(one[0] * f)), max(1, round(one[1] * f))) for k, f in SIZES.items()}


def drawings(r: dict, log=print) -> tuple:
    """-> ({size: [RGBA float per used cell]}, {cell: svg}) for every cell the frames use."""
    cs = cells(r)
    used = sorted({f["cell"] for f in r["frames"]})
    sizes = canvas_sizes(r)
    out = {k: {} for k in sizes}
    svgs = {}
    if r["mode"] == "vector":
        vec = r["vector"]
        pal = vector_palette([cs[i] for i in used], vec)
        gcol = glow_colour([cs[i] for i in used], vec)
        log(f"vector: {len(pal)} colours {[('#%02x%02x%02x' % tuple(int(v) for v in p)) for p in pal]}, glow #{''.join(f'{round(v * 255):02x}' for v in gcol)}")
        for i in used:
            svgs[i] = trace_cell(cs[i], pal, vec)
            for k, (w, h) in sizes.items():
                f = w / cs[i].shape[1]
                core = render_svg(svgs[i], w, h)
                out[k][i] = recolor(with_glow(core, gcol, vec["glow_radius"] * f, vec["glow_strength"]), r["color"])
    else:
        for i in used:
            src = to_image(recolor(cs[i], r["color"]))
            for k, (w, h) in sizes.items():
                out[k][i] = to_array(src.resize((w, h), Image.LANCZOS))   # Pillow resamples RGBA premultiplied
    for k in out:   # alpha below 2/255 is resampling dust: cut it so the atlas trim stays tight
        for i in out[k]:
            out[k][i][..., 3] = np.where(out[k][i][..., 3] < 2 / 255, 0, out[k][i][..., 3])
    return out, svgs


def sequence(r: dict) -> list:
    """Game frames in order: [(game index 1.., cell, first index of that drawing or None)]."""
    seq, n = [], 0
    for f in r["frames"]:
        first = n + 1
        for j in range(max(1, int(f.get("hold", 2)))):
            n += 1
            seq.append((n, f["cell"], None if j == 0 else first))
    return seq


def bbox(a: np.ndarray):
    ys, xs = np.nonzero(a[..., 3] > 0)
    if not len(xs):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def game_assets(game: pathlib.Path) -> pathlib.Path:
    return game / "src" / "_assets" / "kr1-desktop" / "images"


def backdrop(size: tuple) -> Image.Image:
    """A grass crop of KR1 stage 1 (fullhd px = @1x px) when the game is there, a checker otherwise."""
    bg = game_assets(GAME_DIR) / "fullhd" / "go_stage01_bg-1.png"
    w, h = size
    if bg.exists():
        im = Image.open(bg).convert("RGBA")
        x0, y0 = 760, 470
        tile = im.crop((x0, y0, x0 + min(w, im.width - x0), y0 + min(h, im.height - y0)))
        return tile.resize((w, h)) if tile.size != (w, h) else tile
    im = Image.new("RGBA", size, (90, 90, 100, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, 16):
        for x in range((y // 16) % 2 * 16, w, 32):
            d.rectangle((x, y, x + 15, y + 15), fill=(110, 110, 120, 255))
    return im


def hero_for_scale() -> Image.Image | None:
    p = ROOT / "ref" / "hero" / "frames" / "hero_elemental_0014.png"   # a KR1 hero at fullhd (= @1x) size
    return Image.open(p).convert("RGBA") if p.exists() else None


def render(r: dict, log=print, out: pathlib.Path | None = None) -> dict:
    """Export the recipe into <asset>/game (or `out`, e.g. the page's vector preview in .work/preview)."""
    if not r["frames"]:
        sys.exit("the recipe has no frames")
    if r.get("pack"):
        sys.exit(f"{r['id']} was made in the Fx Studio app: change it there and install its new pack")
    out = out or asset(r["id"]) / "game"
    if out.exists():
        shutil.rmtree(out)
    pics, svgs = drawings(r, log)
    sizes = canvas_sizes(r)
    name = r["game"]["name"]
    seq = sequence(r)
    frames_meta = {}
    for k in sizes:
        (out / "frames" / k).mkdir(parents=True)
    for gi, cell, alias in seq:
        fname = f"{name}_{gi:04d}"
        for k in sizes:
            to_image(pics[k][cell]).save(out / "frames" / k / f"{fname}.png", optimize=True)
        bb = bbox(pics["@1x"][cell]) or (0, 0, 1, 1)
        frames_meta[fname] = {"size": list(sizes["@1x"]), "trim_offset": [bb[0], bb[1]],
                              "content": [bb[2] - bb[0], bb[3] - bb[1]], "cell": cell,
                              "alias_of": None if alias is None else f"{name}_{alias:04d}"}
    if svgs:
        (out / "svg").mkdir()
        for i, s in svgs.items():
            s = re.sub(r'fill="(#[0-9A-Fa-f]{6})"', lambda m: f'fill="{recolor_hex(m.group(1), r["color"])}"', s)
            (out / "svg" / f"{name}_cell{i + 1:02d}.svg").write_text(s, encoding="utf-8")
    ax, ay = r["anchor"]
    manifest = {"object": name, "kind": "animation", "fps": FPS, "exported": datetime.datetime.now().isoformat(timespec="seconds"),
                "source": r["source"], "recipe_hash": recipe_hash(r), "mode": r["mode"], "scale": r["scale"],
                "canvas": {k: list(v) for k, v in sizes.items()},
                "anchor": [ax, round(1 - ay, 4)], "anchor_note": "game anchor: x from the left, y from the BOTTOM of the canvas",
                "loop": r["game"]["loop"], "frames": frames_meta,
                "animations": {name: {"prefix": name, "from": 1, "to": len(seq)}}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    preview(r, pics["@1x"], out)
    log(f"render {r['id']}: {len(r['frames'])} drawings, {len(seq)} game frames ({len(seq) / FPS:.2f} s at {FPS} fps), "
        f"@1x canvas {sizes['@1x'][0]}x{sizes['@1x'][1]}, mode {r['mode']} -> {out}")
    return manifest


def preview(r: dict, pics: dict, out: pathlib.Path) -> None:
    """preview.gif at game size over a KR map, a KR hero standing on the anchor (where the game places the effect when
    it is spawned at the hero's position); sheet.png: the drawings in a row."""
    w, h = canvas_sizes(r)["@1x"]
    hero = hero_for_scale()
    ax, ay = round(r["anchor"][0] * w), round(r["anchor"][1] * h)
    # boxes around the pivot (0, 0): the effect, and the hero with its feet on the pivot (KR1 hero anchor 0.5, 0.1)
    boxes = [(-ax, -ay, w - ax, h - ay)]
    if hero:
        hx, hy = -round(hero.width * 0.5), -round(hero.height * 0.9)
        boxes.append((hx, hy, hx + hero.width, hy + hero.height))
    pad = 30
    x0, y0 = min(b[0] for b in boxes) - pad, min(b[1] for b in boxes) - pad
    W, H = max(b[2] for b in boxes) + pad - x0, max(b[3] for b in boxes) + pad - y0
    px, py = -x0, -y0
    ox, oy = px - ax, py - ay
    base = backdrop((W, H))
    if hero:
        base.alpha_composite(hero, (px + hx, py + hy))
    frames, durs = [], []
    for f in r["frames"]:
        im = base.copy()
        im.alpha_composite(to_image(pics[f["cell"]]), (ox, oy))
        d = ImageDraw.Draw(im)
        d.line((ox + ax - 4, oy + ay, ox + ax + 4, oy + ay), fill=(0, 255, 255, 160))
        d.line((ox + ax, oy + ay - 4, ox + ax, oy + ay + 4), fill=(0, 255, 255, 160))
        frames.append(im.convert("RGB"))
        durs.append(round(1000 * max(1, int(f.get("hold", 2))) / FPS))
    if r["game"]["loop"] is False:
        durs[-1] += 400   # a short rest before the gif repeats, so a one-shot effect reads as one
    frames[0].save(out / "preview.gif", save_all=True, append_images=frames[1:], duration=durs, loop=0)
    used = [f["cell"] for f in r["frames"]]
    uniq = list(dict.fromkeys(used))
    sheet = Image.new("RGBA", (w * len(uniq), h), (0, 0, 0, 0))
    for j, c in enumerate(uniq):
        sheet.alpha_composite(to_image(pics[c]), (j * w, 0))
    sheet.save(out / "sheet.png", optimize=True)


# ---------------------------------------------------------------- import
def next_version(folder: pathlib.Path, stem: str) -> pathlib.Path:
    n = 1
    while (folder / f"{stem}_v{n:02d}.png").exists():
        n += 1
    return folder / f"{stem}_v{n:02d}.png"


def write_cells(r: dict) -> None:
    d = asset(r["id"]) / ".work" / "cells"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for i, c in enumerate(cells(r)):
        to_image(c).save(d / f"cell_{i + 1:02d}.png")


def do_import(sheet: pathlib.Path, fx_id: str, grid=None, bg="auto", force=False, log=print) -> dict:
    if not re.fullmatch(r"[a-z0-9_]+", fx_id):
        sys.exit("id: lowercase letters, digits and _ only (it becomes a Lua name)")
    a = asset(fx_id)
    old = None
    if (a / "fx.json").exists():
        if not force:
            sys.exit(f"{a / 'fx.json'} exists: pass --force to import a new sheet version (the recipe keeps its settings)")
        old = load(fx_id)
    (a / "design").mkdir(parents=True, exist_ok=True)
    dst = next_version(a / "design", "sheet")
    im = Image.open(sheet)
    im.save(dst)
    r = defaults(fx_id)
    if old:   # keep the tuned settings; cells and frames follow the new sheet
        for k in ("scale", "anchor", "mode", "color", "vector", "game", "black_floor"):
            r[k] = old.get(k, r[k])
    r["source"] = dst.relative_to(a).as_posix()
    r["bg"] = detect_bg(im) if bg == "auto" else bg
    sa = straight(im, r["bg"], r["black_floor"])
    r["grid"], r["cells"] = find_cells(sa, grid)
    r["frames"] = [{"cell": i, "hold": 2} for i in range(len(r["cells"]))]
    # default anchor: the middle of everything drawn in the cells (set the real emission point in the page)
    cw, ch = cell_canvas(r)
    acc = np.zeros((ch, cw), bool)
    for c in cells(r):
        acc |= c[..., 3] > 0.1
    ys, xs = np.nonzero(acc)
    r["anchor"] = old["anchor"] if old else [round(float((xs.min() + xs.max()) / 2 / cw), 4), round(float((ys.min() + ys.max()) / 2 / ch), 4)]
    save(r)
    write_cells(r)
    log(f"import {fx_id}: {dst.relative_to(ROOT)} bg={r['bg']} grid {r['grid'][0]}x{r['grid'][1]} -> {len(r['cells'])} cells "
        f"of {cw}x{ch} px, anchor {r['anchor']}")
    return r


# ---------------------------------------------------------------- install into KR1
def lua_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def read_text(p: pathlib.Path) -> tuple:
    raw = p.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), nl


def write_text(p: pathlib.Path, text: str, nl: str) -> None:
    p.write_bytes(text.replace("\n", nl).encode("utf-8"))


BLOCK = re.compile(rf"-- {MARK} begin[^\n]*\n.*?-- {MARK} end\n", re.S)


def put_block(text: str, body: str | None, before: str | None) -> str:
    """Replace the marked block (or remove it when body is None); a new block goes before `before`, else at the end."""
    text = BLOCK.sub("", text)   # the block is inserted bare (no blank lines around it), so removing it restores every byte
    if body is None:
        return text
    block = f"-- {MARK} begin (generated by fal-lab scripts/fx_studio.py install; do not edit, rerun install)\n{body}-- {MARK} end\n"
    if before:
        i = text.rindex(before)
        return text[:i] + block + text[i:]
    return (text if text.endswith("\n") else text + "\n") + block


def pack(items: list, max_w: int = 2048) -> tuple:
    """Shelf packing of (key, w, h) -> ({key: (page, x, y)}, [(page_w, page_h)]). 2 px apart."""
    items = sorted(items, key=lambda t: (-t[2], -t[1]))
    width = min(max_w, max(256, int(np.ceil(np.sqrt(sum((w + 2) * (h + 2) for _, w, h in items)) * 1.15))))
    width = max(width, max(w for _, w, _ in items) + 2)
    place, pages, page, x, y, row_h, used_w = {}, [], 0, 0, 0, 0, 0
    for key, w, h in items:
        if x + w + 2 > width:
            x, y, row_h = 0, y + row_h, 0
        if y + h + 2 > max_w:
            pages.append((used_w, y + row_h)); page, x, y, row_h, used_w = page + 1, 0, 0, 0, 0
        place[key] = (page, x, y)
        x += w + 2; row_h = max(row_h, h + 2); used_w = max(used_w, x)
    pages.append((used_w, y + row_h))
    return place, pages


def build_atlas(fxs: list, size_key: str, folder: pathlib.Path) -> tuple:
    """Pack every installed effect's frames of one texture size into go_fx_lab-N.png + go_fx_lab.lua (KR1 atlas format).
    -> (pages, frame table as the reverse repo's dumper writes it: {name: {a_name, a_size, alias, f_quad, size, trim}})."""
    uniq, alias = {}, {}
    for r in fxs:
        man = json.loads((asset(r["id"]) / "game" / "manifest.json").read_text(encoding="utf-8"))
        for fname, m in man["frames"].items():
            if m["alias_of"]:
                alias.setdefault(m["alias_of"], []).append(fname)
                continue
            im = Image.open(asset(r["id"]) / "game" / "frames" / size_key / f"{fname}.png").convert("RGBA")
            bb = im.getbbox() or (0, 0, 1, 1)
            uniq[fname] = (im, bb)
    place, pages = pack([(k, bb[2] - bb[0], bb[3] - bb[1]) for k, (im, bb) in uniq.items()])
    sheets = [Image.new("RGBA", p, (0, 0, 0, 0)) for p in pages]
    table = {}
    lines = [f"-- chunkname: @./_assets/kr1-desktop/images/{folder.name}/{GROUP}.lua", "-- generated by fal-lab scripts/fx_studio.py install", "", "return {"]
    for k in sorted(uniq):
        im, bb = uniq[k]
        pg, x, y = place[k]
        sheets[pg].paste(im.crop(bb), (x, y))   # an exact copy: the sliced sprites must match the atlas pixel for pixel
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        trim = [bb[0], bb[1], im.width - bb[2], im.height - bb[3]]
        al = ", ".join(lua_str(a) for a in alias.get(k, []))
        table[k] = {"a_name": f"{GROUP}-{pg + 1}.png", "a_size": list(pages[pg]), "alias": alias.get(k) or {},
                    "f_quad": [x, y, w, h], "size": [im.width, im.height], "trim": trim}
        lines.append(f"\t{k} = {{\n\t\ta_name = {lua_str(f'{GROUP}-{pg + 1}.png')},\n\t\tsize = {{{im.width}, {im.height}}},\n"
                     f"\t\ttrim = {{{', '.join(map(str, trim))}}},\n\t\ta_size = {{{pages[pg][0]}, {pages[pg][1]}}},\n"
                     f"\t\tf_quad = {{{x}, {y}, {w}, {h}}},\n\t\talias = {{{al}}}\n\t}},")
    lines.append("}")
    for old in folder.glob(f"{GROUP}-*.png"):
        old.unlink()
    for i, s in enumerate(sheets):
        s.save(folder / f"{GROUP}-{i + 1}.png", optimize=True)
    (folder / f"{GROUP}.lua").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sheets, table


def mirror(game: pathlib.Path, tables: dict, pages: dict) -> None:
    """The reverse repo's own copies, so its viewer and tools/verify_assets.py see go_fx_lab like any shipped group:
    data/_assets/.../images/<res>/go_fx_lab.json (frame table, the dumper's compact form) and, for fullhd,
    sprites/fullhd/go_fx_lab/<frame>.png cut from the atlas + their entries in sprites/fullhd/_index.json.
    Empty tables remove all of it."""
    data = game / "data" / "_assets" / "kr1-desktop" / "images"
    for res in ("fullhd", "ipad"):
        t = data / res / f"{GROUP}.json"
        if tables.get(res):
            t.write_text(json.dumps(tables[res], separators=(",", ":"), sort_keys=True), encoding="utf-8")
        elif t.exists():
            t.unlink()
    out = game / "sprites" / "fullhd"
    idx_p = out / "_index.json"
    if not idx_p.exists():
        return
    shutil.rmtree(out / GROUP, ignore_errors=True)
    index = {k: v for k, v in json.loads(idx_p.read_bytes()).items() if not k.startswith(GROUP + "/")}
    if tables.get("fullhd"):
        (out / GROUP).mkdir()
        for name, fr in tables["fullhd"].items():   # the same cut as tools/slice_sprites.py
            x, y, w, h = fr["f_quad"]
            page = pages["fullhd"][int(fr["a_name"].rsplit("-", 1)[1][:-4]) - 1]
            im = Image.new("RGBA", tuple(fr["size"]), (0, 0, 0, 0))
            im.paste(page.crop((x, y, x + w, y + h)), (fr["trim"][0], fr["trim"][1]))
            for n in [name] + list(fr["alias"] or []):
                im.save(out / GROUP / f"{n}.png")
                entry = {**fr, "name": n, "file": f"{GROUP}/{n}.png"}
                if n != name:
                    entry["alias_of"] = name
                index[f"{GROUP}/{n}"] = entry
    idx_p.write_bytes(json.dumps(index, indent=0).replace("\n", "\r\n").encode())   # slice_sprites' own form: indent 0, CRLF


RUNTIME = '''-- fx_lab: plays what fal-lab Fx Studio installed (scripts/fx_studio.py install writes this file, uninstall removes it).
-- In a level: F7 plays the current effect at the mouse, F6 picks the next effect;
-- F5 plays the current skill (the character's pose + its effects, each at its own frame), Ctrl+F5 picks the next skill.
-- Shift mirrors (the character looking left). KR_FX_LAB_DEMO=1 plays every skill (or, without skills, every effect)
-- at the screen centre every few seconds, mirrored every other time (for scripted checks).
local log = require("klua.log"):new("fx_lab")
local E = require("entity_db")
local fx_lab = {idx = 1, sidx = 1, queue = {}}

local function names()
	return FX_LAB_LIST or {}
end

local function skills()
	return FX_LAB_SKILLS or {}
end

local function screen_to_world(game, sx, sy)
	local gui = game.game_gui

	return gui:u2g({x = (sx - gui.window.origin.x) / gui.gui_scale, y = (sy - gui.window.origin.y) / gui.gui_scale})
end

function fx_lab.spawn(game, name, x, y, flip)
	local e = E:create_entity(name)

	if not e then
		log.error("fx_lab: no template %s", name)

		return
	end

	e.pos.x, e.pos.y = x, y
	e.render.sprites[1].ts = game.store.tick_ts
	e.render.sprites[1].flip_x = flip and true or false

	game.simulation:queue_insert_entity(e)
end

-- a skill: the pose now, each effect `at` game frames (1/30 s) later, all at the same feet position
function fx_lab.play_skill(game, s, x, y, flip)
	local now = game.store.tick_ts

	if s.pose then
		fx_lab.spawn(game, s.pose, x, y, flip)
	end

	for _, l in ipairs(s.layers) do
		table.insert(fx_lab.queue, {at = now + l[2] / 30, name = l[1], x = x, y = y, flip = flip})
	end
end

function fx_lab.keypressed(game, key, isrepeat)
	if key ~= "f5" and key ~= "f6" and key ~= "f7" then
		return false
	end

	if not game.store or not game.game_gui or isrepeat then
		return true
	end

	local x, y = screen_to_world(game, love.mouse.getPosition())
	local shift = love.keyboard.isDown("lshift") or love.keyboard.isDown("rshift")
	local ctrl = love.keyboard.isDown("lctrl") or love.keyboard.isDown("rctrl")

	if key == "f5" then
		local list = skills()

		if #list > 0 then
			if ctrl then
				fx_lab.sidx = fx_lab.sidx % #list + 1

				log.error("fx_lab skill: %s (%d/%d)", list[fx_lab.sidx].key, fx_lab.sidx, #list)
			else
				fx_lab.play_skill(game, list[math.min(fx_lab.sidx, #list)], x, y, shift)
			end
		end
	else
		local list = names()

		if #list > 0 then
			if key == "f6" then
				fx_lab.idx = fx_lab.idx % #list + 1

				log.error("fx_lab: %s (%d/%d)", list[fx_lab.idx], fx_lab.idx, #list)
			else
				fx_lab.spawn(game, list[math.min(fx_lab.idx, #list)], x, y, shift)
			end
		end
	end

	return true
end

function fx_lab.update(game, dt)
	if not game.store or not game.store.tick_ts then
		return
	end

	local now = game.store.tick_ts

	for i = #fx_lab.queue, 1, -1 do
		local q = fx_lab.queue[i]

		if now >= q.at - 1e-4 then
			table.remove(fx_lab.queue, i)
			fx_lab.spawn(game, q.name, q.x, q.y, q.flip)
		end
	end

	if not os.getenv("KR_FX_LAB_DEMO") or not game.game_gui then
		return
	end

	local list, sk = names(), skills()
	local every = 2

	for _, s in ipairs(sk) do
		every = math.max(every, s.length / 30 + 1)
	end

	if #list == 0 and #sk == 0 or fx_lab.demo_ts and now - fx_lab.demo_ts < every then
		return
	end

	fx_lab.demo_ts = now
	fx_lab.demo_flip = not fx_lab.demo_flip

	local cx, cy = screen_to_world(game, love.graphics.getWidth() / 2, love.graphics.getHeight() / 2)

	if not fx_lab.demo_logged then
		fx_lab.demo_logged = true

		log.error("fx_lab demo: %d skill(s), %d effect(s) at world %.0f, %.0f every %.1f s", #sk, #list, cx, cy, every)
	end

	if #sk > 0 then
		for i, s in ipairs(sk) do
			fx_lab.play_skill(game, s, cx + (i - (#sk + 1) / 2) * 220, cy, fx_lab.demo_flip)
		end
	else
		for i, name in ipairs(list) do
			fx_lab.spawn(game, name, cx, cy + ((#list + 1) / 2 - i) * 90, fx_lab.demo_flip)
		end

		local qx, qy = screen_to_world(game, love.graphics.getWidth() / 4, love.graphics.getHeight() / 4)

		fx_lab.spawn(game, list[1], qx, qy, fx_lab.demo_flip)
	end
end

return fx_lab
'''

HOOKS = [   # (line to find in all/game.lua, line inserted after it); every inserted line ends with "-- fx_lab"
    ('local game_gui = require("game_gui")',
     'local fx_lab = (function() local ok, m = pcall(require, "fx_lab") return ok and m or nil end)() -- fx_lab'),
    ("game.required_textures = {", f'\t"{GROUP}", -- {MARK}'),
    ("function game:update(dt)", f"\tif fx_lab then fx_lab.update(self, dt) end -- {MARK}"),
    ("function game:keypressed(key, isrepeat)", f"\tif fx_lab and fx_lab.keypressed(self, key, isrepeat) then return true end -- {MARK}"),
]


def game_files(game: pathlib.Path) -> dict:
    src = game / "src"
    return {"anims": src / "kr1" / "data" / "game_animations.lua", "templates": src / "kr1" / "game_templates.lua",
            "game": src / "all" / "game.lua", "runtime": src / "kr1" / "fx_lab.lua",
            "json": game / "data" / "kr1" / "data" / "game_animations.json", "images": game_assets(game)}


Z_LAYERS = ("Z_EFFECTS", "Z_OBJECTS", "Z_DECALS")


def check_game(r: dict) -> None:
    """name and z are written into Lua as bare identifiers: a bad one would stop the game from booting."""
    g = r["game"]
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", str(g.get("name", ""))):
        raise ValueError(f'game.name "{g.get("name")}": lowercase letters, digits and _ only, not starting with a digit')
    if g.get("z", "Z_EFFECTS") not in Z_LAYERS:
        raise ValueError(f'game.z "{g.get("z")}": one of {", ".join(Z_LAYERS)}')


def check_names(fxs: list, f: dict) -> None:
    """A template or animation name that already exists outside our block would silently replace the game's own."""
    tpl = BLOCK.sub("", read_text(f["templates"])[0])
    anim = BLOCK.sub("", read_text(f["anims"])[0])
    for r in fxs:
        n = r["game"]["name"]
        if re.search(rf'(RT|register_t)\(\s*"{re.escape(n)}"', tpl) or re.search(rf"^\t{re.escape(n)} = \{{", anim, re.M):
            sys.exit(f'{n} already exists in the game: set another name (render --set game.name=fx_my_{r["id"]})')


def apply_game(fxs: list, game: pathlib.Path, log=print) -> None:
    f = game_files(game)
    for k in ("anims", "templates", "game"):
        if not f[k].exists():
            sys.exit(f"not a KR1 game folder: {f[k]} missing (pass --game or set KR1_GAME_DIR)")
    for r in fxs:
        try:
            check_game(r)
        except ValueError as e:
            sys.exit(f'{r["id"]}: {e}')
    if fxs:
        check_names(fxs, f)
    # animations: a.<name> = {...} statements after the table, before "local o = {}"
    text, nl = read_text(f["anims"])
    body = "".join(f'a.{r["game"]["name"]} = {{\n\tprefix = {lua_str(r["game"]["name"])},\n\tfrom = 1,\n\tto = {len(sequence(r))}\n}}\n' for r in fxs)
    write_text(f["anims"], put_block(text, body or None, "local o = {}"), nl)
    # templates: appended at the end (RT, Z_* and the fx base template are in scope there)
    text, nl = read_text(f["templates"])
    body = ""
    for r in fxs:
        g, (ax, ay) = r["game"], r["anchor"]
        body += (f'tt = RT({lua_str(g["name"])}, "fx")\n'
                 f'tt.render.sprites[1].name = {lua_str(g["name"])}\n'
                 f"tt.render.sprites[1].anchor.x = {ax}\n"
                 f"tt.render.sprites[1].anchor.y = {round(1 - ay, 4)}\n"
                 f'tt.render.sprites[1].z = {g.get("z", "Z_EFFECTS")}\n'
                 f'tt.render.sprites[1].loop = {"true" if g.get("loop") else "false"}\n'
                 f'tt.timed.runs = {int(g.get("runs", 1))}\n')
    if fxs:
        body += "FX_LAB_LIST = {\n" + "".join(f'\t{lua_str(r["game"]["name"])},\n' for r in fxs) + "}\n"
    names = {r["game"]["name"] for r in fxs}
    sk = [k for k in installed_skills() if all(n in names for n, _ in k["layers"])]
    if sk:
        lines = []
        for i, k in enumerate(sk, 1):
            pose = "nil"
            if k.get("anim") and k.get("pivot"):   # the character's own animation, played by an fx entity at the feet
                pose = lua_str(f"fx_lab_pose_{i}")
                body += (f'tt = RT({pose}, "fx")\n'
                         f'tt.render.sprites[1].name = {lua_str(k["anim"])}\n'
                         f'tt.render.sprites[1].anchor.x = {k["pivot"][0]}\n'
                         f'tt.render.sprites[1].anchor.y = {round(1 - k["pivot"][1], 4)}\n'
                         f'tt.render.sprites[1].z = Z_OBJECTS\n'
                         f'tt.render.sprites[1].loop = false\n')
            layers = ", ".join(f"{{{lua_str(n)}, {int(at)}}}" for n, at in k["layers"])
            lines.append(f'\t{{key = {lua_str(k["key"])}, pose = {pose}, length = {int(k.get("length", 30))}, layers = {{{layers}}}}},\n')
        body += "FX_LAB_SKILLS = {\n" + "".join(lines) + "}\n"
        log(f"skills: {', '.join(k['key'] for k in sk)}")
    write_text(f["templates"], put_block(text, body or None, None), nl)
    # game.lua hooks + the runtime module + the atlas group in both texture sizes
    text, nl = read_text(f["game"])
    lines = [ln for ln in text.split("\n") if not ln.rstrip().endswith(f"-- {MARK}")]
    if fxs:
        for find, add in HOOKS:
            i = next((j for j, ln in enumerate(lines) if ln.strip() == find), None)
            if i is None:
                sys.exit(f"all/game.lua changed: line not found: {find}")
            lines.insert(i + 1, add)
        # a skill plays its character's own animation: that character's atlas group must be loaded in every level,
        # not only when the character is the selected hero
        i = next(j for j, ln in enumerate(lines) if ln.strip() == "game.required_textures = {")
        for group in sorted({g for g in (anim_group(game, k["anim"]) for k in sk if k.get("anim")) if g}):
            lines.insert(i + 1, f'\t"{group}", -- {MARK}')
    write_text(f["game"], "\n".join(lines), nl)
    tables, pages = {}, {}
    if fxs:
        f["runtime"].write_text(RUNTIME.replace("\n", "\r\n"), encoding="utf-8", newline="")
        for size_key, folder in (("@1x", "fullhd"), ("ipad", "ipad")):
            pages[folder], tables[folder] = build_atlas(fxs, size_key, f["images"] / folder)
            log(f"atlas {folder}/{GROUP}.lua + {len(pages[folder])} page(s)")
    else:
        if f["runtime"].exists():
            f["runtime"].unlink()
        for folder in ("fullhd", "ipad"):
            for p in list((f["images"] / folder).glob(f"{GROUP}-*.png")) + [f["images"] / folder / f"{GROUP}.lua"]:
                if p.exists():
                    p.unlink()
    mirror(game, tables, pages)
    # the JSON mirror the reverse repo's viewer and verify_assets read
    if f["json"].exists():
        d = json.loads(f["json"].read_text(encoding="utf-8"))
        anims = d["animations"]
        for k in [k for k, v in anims.items() if isinstance(v, dict) and v.get(MARK)]:
            del anims[k]
        for r in fxs:
            anims[r["game"]["name"]] = {"prefix": r["game"]["name"], "from": 1, "to": len(sequence(r)), MARK: True}
        f["json"].write_text(json.dumps(d, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")   # the dump's own compact form
    log(f"game {game}: {len(fxs)} effect(s) installed" + ("" if fxs else ", every fx_lab trace removed"))


def installed() -> list:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(VFX.glob("*/fx.json"))
            if json.loads(p.read_text(encoding="utf-8")).get("game", {}).get("installed")]


def do_install(ids: list, game: pathlib.Path, on: bool, log=print) -> None:
    for i in ids:
        r = load(i)
        r["game"]["installed"] = on
        save(r)
    fxs = installed()
    for r in fxs:   # an installed effect whose recipe changed after its last render is rendered again
        if r.get("pack"):
            continue   # made in the Fx Studio app: its frames ARE the export, never re-rendered here
        man = asset(r["id"]) / "game" / "manifest.json"
        if not man.exists() or json.loads(man.read_text(encoding="utf-8")).get("recipe_hash") != recipe_hash(r):
            render(r, log)
    apply_game(fxs, game, log)


def anim_group(game: pathlib.Path, anim: str) -> str | None:
    """The atlas group (go_*.lua under the fullhd images) that holds the first frame of a game animation."""
    text = (game / "src" / "kr1" / "data" / "game_animations.lua").read_text(encoding="utf-8")
    m = re.search(rf"^\t(?:a\.)?{re.escape(anim)} = \{{(.*?)\n\t?\}}", text, re.M | re.S)
    if not m:
        return None
    prefix = re.search(r'prefix\s*=\s*"(\w+)"', m.group(1)).group(1)
    first = int(re.search(r"from\s*=\s*(\d+)", m.group(1)).group(1))
    needle = f"\t{prefix}_{first:04d} = {{"
    for lua in sorted((game_assets(game) / "fullhd").glob("go_*.lua")):
        if needle in lua.read_text(encoding="utf-8", errors="ignore"):
            return lua.stem
    return None


SKILLS = VFX / "_skills"   # one <key>.json per skill installed from the app: which effects, at which frame of which pose


def installed_skills() -> list:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(SKILLS.glob("*.json"))] if SKILLS.exists() else []


def install_skill(skill: dict, layer_dirs: list, game: pathlib.Path, force: bool = False, log=print) -> str:
    """A skill from the app: every layer is an fx pack (cut and installed as is), plus the timing that ties them to the
    character's pose. Muted layers are installed but left out of the skill."""
    key = skill["key"]
    if not re.fullmatch(r"[a-z0-9_]+", key):
        sys.exit(f"skill key {key!r}: lowercase letters, digits and _ only")
    layers = []
    for meta, folder in zip(skill["layers"], layer_dirs):
        fx_id = install_pack(folder, game, force, log, apply=False)
        if not meta.get("muted"):   # the game name comes from the pack itself (the saved document may not repeat it)
            layers.append([load(fx_id)["game"]["name"], int(meta["start"])])
    SKILLS.mkdir(parents=True, exist_ok=True)
    rec = {"key": key, "title": skill.get("title", key), "character": skill.get("character"), "pose_id": skill.get("pose"),
           "anim": skill.get("anim"), "pivot": skill.get("pivot"), "length": skill.get("length", 30), "layers": layers}
    (SKILLS / f"{key}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"skill {key}: {len(layers)} effect(s) on " + (f"{skill.get('anim')}" if skill.get("anim") else "no game animation (effects only)"))
    do_install([], game, True, log)
    return key


def pack_from_ids(ids: dict, assets_dir: pathlib.Path) -> pathlib.Path:
    """A pack named by asset ids ({json, @2x, @1x, ipad}), the assets saved as <id>.json / <id>.png -> a pack folder."""
    import tempfile
    folder = pathlib.Path(tempfile.mkdtemp())
    shutil.copyfile(next(assets_dir.glob(ids["json"] + ".*")), folder / "pack.json")
    for k, f in json.loads((folder / "pack.json").read_text(encoding="utf-8"))["sheets"].items():
        shutil.copyfile(next(assets_dir.glob(ids[k] + ".*")), folder / f)
    return folder


def pack_from_assets(project: pathlib.Path, assets_dir: pathlib.Path) -> pathlib.Path:
    """The app's saved project (db document projects/<id>, read with ArtifactData) names its pack by asset ids; the
    assets, read with the Artifact tool, are saved as <id>.json / <id>.png. -> a folder laid out as a pack."""
    import tempfile
    doc = json.loads(project.read_text(encoding="utf-8"))
    ids = doc["pack"]
    folder = pathlib.Path(tempfile.mkdtemp())
    shutil.copyfile(next(assets_dir.glob(ids["json"] + ".*")), folder / "pack.json")
    sheets = json.loads((folder / "pack.json").read_text(encoding="utf-8"))["sheets"]
    for k, f in sheets.items():
        shutil.copyfile(next(assets_dir.glob(ids[k] + ".*")), folder / f)
    return folder


def install_pack(src: pathlib.Path, game: pathlib.Path, force: bool = False, log=print, apply: bool = True) -> str:
    """A pack exported by the Fx Studio app (tools/fx_studio/app.html): a .zip, or a folder (or its pack.json) holding
    pack.json + sheet@2x.png, sheet@1x.png, sheet_ipad.png. The app's frames are the final frames: they are cut out of
    the sheets into out/vfx/<id>/game/ exactly as render() lays it out, then installed. Nothing is re-rendered."""
    import tempfile, zipfile
    tmp = None
    if src.suffix.lower() == ".zip":
        tmp = pathlib.Path(tempfile.mkdtemp())
        with zipfile.ZipFile(src) as z:
            z.extractall(tmp)
        folder = tmp
    else:
        folder = src.parent if src.is_file() else src
    if (folder / "skill.json").exists():   # a skill zip from the app: skill.json + one pack folder per layer
        skill = json.loads((folder / "skill.json").read_text(encoding="utf-8"))
        key = install_skill(skill, [folder / L["dir"] for L in skill["layers"]], game, force, log)
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
        return key
    pack = json.loads((folder / "pack.json").read_text(encoding="utf-8"))
    if pack.get("format") != "fx-studio-pack":
        sys.exit(f"{folder / 'pack.json'} is not an Fx Studio pack")
    fx_id, name = pack["id"], pack["name"]
    if not re.fullmatch(r"[a-z0-9_]+", fx_id):
        sys.exit(f"pack id {fx_id!r}: lowercase letters, digits and _ only")
    a = asset(fx_id)
    if (a / "fx.json").exists() and not load(fx_id).get("pack") and not force:
        sys.exit(f"{a} holds an effect made with the local tool: pass --force to replace it with the app's pack")
    keep = (a / "fx.json").exists() and load(fx_id)["game"].get("installed")
    rec = pack["recipe"]
    r = {"version": 1, "id": fx_id, "pack": True, "title": pack.get("title", fx_id), "source": "app pack",
         "mode": "raster", "bg": rec.get("bg"), "black_floor": rec.get("black_floor"), "grid": rec.get("grid"), "cells": [],
         "frames": rec["frames"], "scale": rec["scale"], "anchor": pack["anchor"], "color": rec.get("color"),
         "game": {"name": name, "z": pack.get("z", "Z_EFFECTS"), "loop": bool(pack.get("loop")), "runs": int(pack.get("runs", 1)),
                  "installed": keep}}
    check_game(r)
    # keep the pack itself (what the app exported) next to the cut frames
    (a / "pack").mkdir(parents=True, exist_ok=True)
    for f in ["pack.json", *pack["sheets"].values()]:
        shutil.copyfile(folder / f, a / "pack" / f)
    out = a / "game"
    if out.exists():
        shutil.rmtree(out)
    sheets = {k: Image.open(folder / f).convert("RGBA") for k, f in pack["sheets"].items()}
    for k in SIZES:
        (out / "frames" / k).mkdir(parents=True)
    frames_meta = {}
    for fr in pack["frames"]:
        src_name = fr["alias_of"] or fr["name"]
        for k in SIZES:
            d = pack["drawings"][src_name][k]
            x, y, w, h = d["rect"]
            im = Image.new("RGBA", tuple(d["size"]), (0, 0, 0, 0))
            im.paste(sheets[k].crop((x, y, x + w, y + h)), (d["trim"][0], d["trim"][1]))
            im.save(out / "frames" / k / f"{fr['name']}.png", optimize=True)
        d1 = pack["drawings"][src_name]["@1x"]
        frames_meta[fr["name"]] = {"size": d1["size"], "trim_offset": d1["trim"][:2], "content": d1["rect"][2:],
                                   "alias_of": fr["alias_of"]}
    ax, ay = pack["anchor"]
    manifest = {"object": name, "kind": "animation", "fps": pack.get("fps", FPS), "exported": pack.get("exported"),
                "source": "Fx Studio app pack", "recipe_hash": recipe_hash(r), "mode": "raster", "scale": r["scale"],
                "canvas": pack["canvas"], "anchor": [ax, round(1 - ay, 4)],
                "anchor_note": "game anchor: x from the left, y from the BOTTOM of the canvas",
                "loop": r["game"]["loop"], "frames": frames_meta,
                "animations": {name: {"prefix": name, "from": 1, "to": len(pack["frames"])}}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    save(r)
    if len(sequence(r)) != len(pack["frames"]):
        sys.exit("pack.json: frames and recipe holds disagree")
    log(f"pack {fx_id}: {len(pack['frames'])} game frames ({len(pack['drawings'])} drawings) -> {out.relative_to(ROOT)}")
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    if apply:
        do_install([fx_id], game, True, log)
    else:
        r["game"]["installed"] = True
        save(r)
    return fx_id


# ---------------------------------------------------------------- cli
def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("import"); s.add_argument("sheet"); s.add_argument("--id", required=True)
    s.add_argument("--grid", help="COLSxROWS (default: found from the gaps)"); s.add_argument("--bg", default="auto")
    s.add_argument("--force", action="store_true")
    s = sub.add_parser("render"); s.add_argument("id"); s.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    for name in ("install", "uninstall"):
        s = sub.add_parser(name); s.add_argument("ids", nargs="*"); s.add_argument("--game", default=str(GAME_DIR))
        if name == "uninstall":
            s.add_argument("--all", action="store_true")
    s = sub.add_parser("install-pack", help="install a pack exported by the Fx Studio app (.zip or folder with pack.json)")
    s.add_argument("pack", help="a .zip, a folder with pack.json, or (with --project) the folder the app's assets were saved to")
    s.add_argument("--project", help="the app's saved project document (projects/<id>.json): pack assets named by asset id")
    s.add_argument("--skill", help="the app's saved skill document (skills/<key>.json): every layer's pack named by asset ids")
    s.add_argument("--game", default=str(GAME_DIR)); s.add_argument("--force", action="store_true")
    sub.add_parser("list")
    a = p.parse_args()
    if a.cmd == "import":
        grid = tuple(int(v) for v in a.grid.lower().split("x")) if a.grid else None
        do_import(pathlib.Path(a.sheet), a.id, grid, a.bg, a.force)
    elif a.cmd == "render":
        r = load(a.id)
        for kv in a.set:
            k, _, v = kv.partition("=")
            set_value(r, k, v)
        save(r)
        render(r)
    elif a.cmd == "install":
        if not a.ids:
            sys.exit("install <id> [...]")
        do_install(a.ids, pathlib.Path(a.game), True)
    elif a.cmd == "uninstall":
        ids = [r["id"] for r in installed()] if a.all else a.ids
        if a.all and SKILLS.exists():
            shutil.rmtree(SKILLS)
        do_install(ids, pathlib.Path(a.game), False)
    elif a.cmd == "install-pack":
        if a.skill:
            doc = json.loads(pathlib.Path(a.skill).read_text(encoding="utf-8"))
            install_skill(doc, [pack_from_ids(L["pack"], pathlib.Path(a.pack)) for L in doc["layers"]], pathlib.Path(a.game), a.force)
        else:
            src = pack_from_assets(pathlib.Path(a.project), pathlib.Path(a.pack)) if a.project else pathlib.Path(a.pack)
            install_pack(src, pathlib.Path(a.game), a.force)
    elif a.cmd == "list":
        for fx in sorted(VFX.glob("*/fx.json")):
            r = json.loads(fx.read_text(encoding="utf-8"))
            st = "installed" if r["game"].get("installed") else ("rendered" if (fx.parent / "game" / "manifest.json").exists() else "imported")
            print(f"{r['id']:24} {r['mode']:7} {len(r['frames']):3} drawings  scale {r['scale']:<5} {st}")


if __name__ == "__main__":
    main()
