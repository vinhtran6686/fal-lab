#!/usr/bin/env python3
"""Puppet Kit CLI: animate a character from its approved stills with a cut-out rig. No API call, deterministic.

  python scripts/puppet.py check  <asset>/source/rig/rig.json            # parts, bones, rest pose -> <asset>/.work/puppet/
  python scripts/puppet.py render <asset> <asset>/source/rig/anims/idle.json --sheet idle_side [--no-export]
  python scripts/puppet.py track  <asset> <anim.json> --name <vfx name>   # weapon root/tip -> source/vfx/<name>/weapon_track.json
  python scripts/puppet.py slash  <asset> <anim.json> --name <fx name> --sheet <sheet>   # slash fx on the cut of a pose-to-pose attack

render writes the ONE final version of the sheet into <asset>/frames/<sheet>/ (frames/@2x and @1x, sheet.png,
preview.gif, check/) in the asset's cell, pivot and body size (meta.json), with the foot shadow, and records the
state in meta.json ("split": "puppet"). Guide: docs/puppet-kit.md
"""
import argparse
import json
import pathlib
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from puppet_kit.core import Animation, Rig, T, S, apply  # noqa: E402

SS = 3  # supersampling of the @2x cell while rendering


def to_img(arr):
    return Image.fromarray(np.asarray(arr).clip(0, 255).astype(np.uint8), "RGBA")


def cmd_check(a):
    rig = Rig(a.rig)
    out = pathlib.Path(a.out) if a.out else rig.dir.parents[1] / ".work" / "puppet"
    out.mkdir(parents=True, exist_ok=True)
    rig.overlay().save(out / "rig_overlay.png")
    shape = next(iter(rig.masks.values())).shape
    # exploded view: every part on its own tile
    tiles = []
    for p in rig.parts:
        im = to_img(p["img"])
        t = Image.new("RGBA", (im.width + 20, im.height + 40), (70, 80, 90, 255))
        t.alpha_composite(im, (10, 30))
        ImageDraw.Draw(t).text((6, 6), f"{p['name']} -> {p['bone']}", fill=(255, 255, 255, 255))
        tiles.append(t)
    W = sum(t.width for t in tiles)
    sheet = Image.new("RGBA", (W, max(t.height for t in tiles)), (70, 80, 90, 255))
    x = 0
    for t in tiles:
        sheet.paste(t, (x, 0))
        x += t.width
    sheet.save(out / "rig_parts.png")
    rest, _ = rig.render({}, 0, np.eye(3), shape)
    bg = Image.new("RGBA", (shape[1], shape[0]), (255, 0, 255, 255))
    bg.alpha_composite(to_img(rest))
    bg.convert("RGB").save(out / "rig_rest.png")
    print(f"parts: {[p['name'] for p in rig.parts]}\nwrote {out}/rig_overlay.png, rig_parts.png, rig_rest.png")


def shadow_cell(meta, c2):
    sh = meta.get("shadow")
    if not sh:
        return Image.new("RGBA", c2, (0, 0, 0, 0))
    px, py = c2[0] * meta["pivot"][0], c2[1] * meta["pivot"][1]
    rgb = tuple(int(sh["color"].lstrip("#")[k:k + 2], 16) for k in (0, 2, 4))
    big = Image.new("RGBA", (c2[0] * 4, c2[1] * 4), (0, 0, 0, 0))
    ImageDraw.Draw(big).ellipse([(px - sh["w_2x"] / 2) * 4, (py - sh["h_2x"] / 2) * 4,
                                 (px + sh["w_2x"] / 2) * 4, (py + sh["h_2x"] / 2) * 4],
                                fill=rgb + (round(255 * sh["alpha"]),))
    return big.resize(c2, Image.LANCZOS)


def render_frames(asset, anim, meta, body_only=False):
    c2 = (meta["cell"][0] * meta["scale_2x"], meta["cell"][1] * meta["scale_2x"])
    body2x = meta["body_height_2x"]
    shadow = shadow_cell(meta, c2)
    cells, socks = [], []
    for g in range(anim.total):
        shot, f = anim.locate(g)
        rig = shot["rig"]
        view = S(SS, SS) @ anim.view(rig, c2, meta["pivot"], body2x)
        img, world = rig.render(shot["tracks"], f, view, (c2[1] * SS, c2[0] * SS))
        body = to_img(img).resize(c2, Image.LANCZOS)
        cell = Image.new("RGBA", c2, (0, 0, 0, 0)) if body_only else shadow.copy()
        cell.alpha_composite(body)
        cells.append(cell)
        v2 = anim.view(rig, c2, meta["pivot"], body2x)
        socks.append({n: apply(v2, p).tolist() for n, p in rig.sockets(world).items()})
    return cells, socks, c2


def gif(cells, path, fps, scale=1, bg=(200, 200, 190, 255)):
    fr = []
    for c in cells:
        im = Image.alpha_composite(Image.new("RGBA", c.size, bg), c)
        if scale != 1:
            im = im.resize((round(c.width * scale), round(c.height * scale)), Image.NEAREST if scale > 1 else Image.LANCZOS)
        fr.append(im.convert("P", palette=Image.ADAPTIVE))
    fr[0].save(path, save_all=True, append_images=fr[1:], duration=round(1000 / fps), loop=0)


def cmd_render(a):
    asset = pathlib.Path(a.asset)
    meta = json.loads((asset / "meta.json").read_text(encoding="utf-8"))
    anim = Animation(a.anim, asset)
    cells, socks, c2 = render_frames(asset, anim, meta)
    sheet = a.sheet or pathlib.Path(a.anim).stem
    if a.no_export:
        out = asset / ".work" / "puppet" / sheet
        out.mkdir(parents=True, exist_ok=True)
        gif(cells, out / "preview.gif", anim.fps)
        gif(cells, out / "preview_3x.gif", anim.fps, 3)
        contact(cells, out / "contact.png")
        print(f"preview only: {out}")
        return
    tag = f"{meta['kind']}_{meta['id']}_{sheet}"
    folder = asset / "frames" / sheet
    if folder.exists():
        shutil.rmtree(folder)
    d2, d1, chk = folder / "frames" / "@2x", folder / "frames" / "@1x", folder / "check"
    for d in (d2, d1, chk):
        d.mkdir(parents=True)
    for n, c in enumerate(cells, 1):
        c.save(d2 / f"{tag}_{n:02d}.png")
        c.resize((c2[0] // 2, c2[1] // 2), Image.LANCZOS).save(d1 / f"{tag}_{n:02d}.png")
    strip = Image.new("RGBA", (c2[0] * len(cells), c2[1]), (0, 0, 0, 0))
    for n, c in enumerate(cells):
        strip.paste(c, (n * c2[0], 0))
    strip.save(folder / "sheet.png")
    gif(cells, folder / "preview.gif", anim.fps)
    gif(cells, chk / "preview_3x.gif", anim.fps, 3)
    gif(cells, chk / "preview_1x.gif", anim.fps, 0.5)
    contact(cells, chk / "contact.png")
    rel = pathlib.Path(a.anim).resolve().relative_to(asset.resolve()).as_posix()
    entry = {"version": anim.spec.get("version", "p01"), "dir": f"frames/{sheet}", "source": rel, "frames": len(cells),
             "fps": anim.fps, "loop": anim.loop, "files": f"frames/{sheet}/frames/@1x/{tag}_NN.png",
             "sheet": f"frames/{sheet}/sheet.png", "split": "puppet",
             "puppet": {"rigs": sorted(anim.rigs), "shots": [[s["name"], s["frames"]] for s in anim.shots]}}
    if anim.spec.get("hit_frame"):
        entry["hit_frame"] = anim.spec["hit_frame"]
    meta["states"][sheet] = entry
    (asset / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"exported {sheet}: {len(cells)} frames @ {anim.fps} fps -> {folder}")


def contact(cells, path, cols=8):
    rows = (len(cells) + cols - 1) // cols
    w, h = cells[0].size
    im = Image.new("RGBA", (w * cols, h * rows), (200, 200, 190, 255))
    for n, c in enumerate(cells):
        im.alpha_composite(c, ((n % cols) * w, (n // cols) * h))
        ImageDraw.Draw(im).text(((n % cols) * w + 4, (n // cols) * h + 4), str(n + 1), fill=(0, 0, 0, 255))
    im.convert("RGB").save(path)


def weapon_sampler(asset, anim, meta, root="weapon_root", tip="weapon_tip"):
    """g (global frame, float, 0-based) -> (root, tip) in @2x cell pixels. Inside a shot the rig gives the exact
    points. Across a cut between two shots listed in the animation's "transitions" the blade is swung from the last
    frame of one shot to the first frame of the next: the root moves on a line, the blade angle turns in the given
    direction ("cw" / "ccw" on screen), the length is interpolated."""
    c2 = (meta["cell"][0] * 2, meta["cell"][1] * 2)
    body2x = meta["body_height_2x"]
    starts, acc = [], 0
    for s in anim.shots:
        starts.append(acc)
        acc += s["frames"]
    trans = {t["after_shot"]: t for t in anim.spec.get("transitions", [])}

    def at(i, f):
        shot = anim.shots[i]
        rig = shot["rig"]
        world, _ = rig.pose(shot["tracks"], f)
        sk = rig.sockets(world)
        if root not in sk or tip not in sk:
            sys.exit(f"rig {rig.path} has no sockets {root}/{tip}")
        v2 = anim.view(rig, c2, meta["pivot"], body2x)
        return apply(v2, sk[root]), apply(v2, sk[tip])

    def sample(g):
        g = min(max(g, 0.0), anim.total - 1)
        i = max(k for k, st in enumerate(starts) if st <= g + 1e-9)
        f = g - starts[i]
        last = anim.shots[i]["frames"] - 1
        if f <= last + 1e-9 or i + 1 >= len(anim.shots):
            return at(i, min(f, last))
        u = f - last                       # 0..1 across the cut
        t = trans.get(i)
        if not t:
            return at(i, last) if u < 0.5 else at(i + 1, 0)
        from puppet_kit.core import EASE
        e = EASE[t.get("ease", "linear")](u)
        (r0, t0), (r1, t1) = at(i, last), at(i + 1, 0)
        a0, a1 = np.arctan2(*(t0 - r0)[::-1]), np.arctan2(*(t1 - r1)[::-1])
        d = (a1 - a0) % (2 * np.pi)        # cw on screen (y down) = increasing angle
        if t.get("dir", "cw") == "ccw":
            d -= 2 * np.pi
        ang = a0 + d * e
        ln = np.linalg.norm(t0 - r0) * (1 - e) + np.linalg.norm(t1 - r1) * e
        r = r0 * (1 - e) + r1 * e
        return r, r + ln * np.array([np.cos(ang), np.sin(ang)])
    return sample, starts, c2, body2x


def cmd_track(a):
    """Weapon root/tip of every frame, in the format of the hand-marked weapon_track.json (milestone 01)."""
    asset = pathlib.Path(a.asset)
    meta = json.loads((asset / "meta.json").read_text(encoding="utf-8"))
    anim = Animation(a.anim, asset)
    sample, starts, c2, body2x = weapon_sampler(asset, anim, meta, a.root, a.tip)
    px, py = c2[0] * meta["pivot"][0], c2[1] * meta["pivot"][1]
    sub = max(1, a.sub)
    H = lambda p: [round(float((p[0] - px) / body2x), 4), round(float((py - p[1]) / body2x), 4)]  # noqa: E731
    samples, prev = [], None
    for i in range((anim.total - 1) * sub + 1):
        g = i / sub
        r, t = sample(g)
        sp = 0.0 if prev is None else float(np.hypot(*(np.array(H(t)) - prev))) * sub
        prev = np.array(H(t))
        samples.append({"frame": round(g + 1, 3), "ms": round(g * 1000 / anim.fps), "visible": True, "used": True,
                        "estimated": bool(g % 1), "side": "front", "root": H(r), "tip": H(t),
                        "root_px2x": [round(float(r[0]), 1), round(float(r[1]), 1)],
                        "tip_px2x": [round(float(t[0]), 1), round(float(t[1]), 1)], "note": "", "tip_speed": round(sp, 4)})
    out = asset / "source" / "vfx" / a.name
    out.mkdir(parents=True, exist_ok=True)
    doc = {"state": a.sheet or pathlib.Path(a.anim).stem, "take": pathlib.Path(a.anim).as_posix(), "cell": meta["cell"],
           "pivot": meta["pivot"], "fps": anim.fps, "frames": anim.total, "frame_ms": round(1000 / anim.fps),
           "units": "H, origin = feet pivot, x forward (right), y up; time ms from frame 1; tip_speed in H per frame",
           "body_height_px": body2x / 2, "coordinate_H_px": body2x / 2, "subframes": sub,
           "px_to_H_2x": {"x": f"(px - {px:g}) / {body2x}", "y": f"({py:g} - py) / {body2x}"},
           "hit_frame": anim.spec.get("hit_frame"),
           "marked_by": "puppet rig sockets (exact at whole frames; 'estimated' samples are the swing across a cut)",
           "samples": samples}
    (out / "weapon_track.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out / 'weapon_track.json'}: {len(samples)} samples")


def cmd_slash(a):
    """Slash fx for a pose-to-pose attack: the blade sweep of the cut (anim "transitions") is drawn with the
    milestone-01 layered generator (imported, not modified) and laid on the hit frame, then fades."""
    import os
    if os.environ.get("PYTHONHASHSEED") != "0":      # gen_slash_loop places breaks with hash(): fixed seed = same frames
        os.execve(sys.executable, [sys.executable] + sys.argv, dict(os.environ, PYTHONHASHSEED="0"))
    asset = pathlib.Path(a.asset)
    meta = json.loads((asset / "meta.json").read_text(encoding="utf-8"))
    anim = Animation(a.anim, asset)
    sample, starts, c2, body2x = weapon_sampler(asset, anim, meta)
    tr = anim.spec.get("transitions")
    if not tr:
        sys.exit("the animation has no \"transitions\": nothing to sweep")
    i = tr[0]["after_shot"]
    g0 = starts[i] + anim.shots[i]["frames"] - 1     # last frame before the cut (0-based); the hit is g0 + 1
    n = a.steps
    P = json.loads(pathlib.Path(a.params).read_text(encoding="utf-8"))
    L = P["layered"]
    fades = sorted(L["after"], key=int)              # the generator's fade steps, re-keyed after our virtual hit
    L["after"] = {str(n + 1 + k): L["after"][f] for k, f in enumerate(fades)}
    L["grow"] = [1.0] * n
    L["lag_frames"] = a.lag                          # how many sweep steps the ribbon trails behind the blade
    for k, v in (s.split("=", 1) for s in a.set):
        node = P
        ks = k.split(".")
        for kk in ks[:-1]:
            node = node[kk]
        node[ks[-1]] = json.loads(v)
    smp = []
    for k in range(n):
        r, t = sample(g0 + k / (n - 1))
        smp.append({"frame": k + 1, "root_px2x": [float(r[0]), float(r[1])], "tip_px2x": [float(t[0]), float(t[1])]})
    track = {"frames": n + len(fades), "hit_frame": n, "samples": smp, "fit": {"frames": list(range(1, n + 1))},
             "speed": {"vfx_start_frame": 2}}
    root = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "scripts" / "experiments" / "milestone_01"))
    import slash_from_track as SFT
    _, _, _, frames2, _ = SFT.render_layered(track, P)
    fx = [SFT.to_img(f) for f in frames2[n - 1:]]    # the full sweep, then its fades
    hit = g0 + 1
    empty = Image.new("RGBA", c2, (0, 0, 0, 0))
    cells = [empty] * anim.total
    cells = [fx[g - hit] if 0 <= g - hit < len(fx) else empty for g in range(anim.total)]
    sheet = a.sheet or pathlib.Path(a.anim).stem
    out = asset / "frames" / "fx" / a.name
    if out.exists():
        shutil.rmtree(out)
    tag = f"{meta['kind']}_{meta['id']}_fx_{a.name}_front"
    for sub, sc in (("@2x", 1), ("@1x", 2)):
        d = out / "front" / "frames" / sub
        d.mkdir(parents=True)
        for k, c in enumerate(cells, 1):
            (c if sc == 1 else c.resize((c2[0] // 2, c2[1] // 2), Image.LANCZOS)).save(d / f"{tag}_{k:02d}.png")
    strip = Image.new("RGBA", (c2[0] * len(cells), c2[1]), (0, 0, 0, 0))
    for k, c in enumerate(cells):
        strip.paste(c, (k * c2[0], 0))
    strip.save(out / "sheet.png")
    body = sorted((asset / "frames" / sheet / "frames" / "@2x").glob("*.png"))
    if len(body) == len(cells):
        both = []
        for bp, c in zip(body, cells):
            im = Image.open(bp).convert("RGBA")
            im.alpha_composite(c)
            both.append(im)
        gif(both, out / "preview_with_body.gif", anim.fps, bg=(36, 38, 46, 255))
        gif(both, out / "preview_with_body_3x.gif", anim.fps, 3, bg=(36, 38, 46, 255))
        contact(both, out / "contact_with_body.png")
    gif(cells, out / "preview_fx_only.gif", anim.fps, bg=(36, 38, 46, 255))
    rel = pathlib.Path(a.anim).resolve().relative_to(asset.resolve()).as_posix()
    fxj = {"state": sheet, "fx": a.name, "frames": len(cells), "fps": anim.fps, "loop": False,
           "source": "milestone-01 layered slash generator in the blade sweep of the puppet rig's weapon sockets (no hand marking)",
           "blend": "screen", "size_2x": list(c2), "size_1x": [c2[0] // 2, c2[1] // 2],
           "pivot_2x": [c2[0] * meta["pivot"][0], c2[1] * meta["pivot"][1]],
           "layers": [{"id": "front", "z": "in front of the body", "files": f"frames/fx/{a.name}/front/frames/@2x/{tag}_NN.png (also @1x)"}],
           "timing": {"hit_frame": hit + 1, "fade_frames": [hit + 2 + k for k in range(len(fades))]},
           "rebuild": f"python scripts/puppet.py slash <asset> {rel} --name {a.name} --sheet {sheet}"}
    (out / "fx.json").write_text(json.dumps(fxj, indent=1) + "\n", encoding="utf-8")
    meta.setdefault("fx", {})[a.name] = f"frames/fx/{a.name}/fx.json"
    (asset / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"slash fx {a.name}: sweep of {n} steps on frame {hit + 1}, fades {len(fades)} frames -> {out}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("check"); c.add_argument("rig"); c.add_argument("--out"); c.set_defaults(fn=cmd_check)
    r = sp.add_parser("render"); r.add_argument("asset"); r.add_argument("anim"); r.add_argument("--sheet")
    r.add_argument("--no-export", action="store_true", help="preview into .work/puppet/<sheet>/ only"); r.set_defaults(fn=cmd_render)
    t = sp.add_parser("track"); t.add_argument("asset"); t.add_argument("anim"); t.add_argument("--name", required=True)
    t.add_argument("--sheet"); t.add_argument("--sub", type=int, default=1, help="samples per frame (1 = frames only)")
    t.add_argument("--root", default="weapon_root"); t.add_argument("--tip", default="weapon_tip"); t.set_defaults(fn=cmd_track)
    x = sp.add_parser("slash"); x.add_argument("asset"); x.add_argument("anim"); x.add_argument("--name", required=True)
    x.add_argument("--sheet"); x.add_argument("--steps", type=int, default=6, help="samples of the sweep across the cut")
    x.add_argument("--lag", type=float, default=4.2, help="ribbon length in sweep steps (steps - 1 = the whole swing)")
    x.add_argument("--params", default="out/heroes/holy_commander/source/vfx/slash_diag/slash_params.json")
    x.add_argument("--set", action="append", default=[], help="override a parameter: layered.width_scale=0.8")
    x.set_defaults(fn=cmd_slash)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
