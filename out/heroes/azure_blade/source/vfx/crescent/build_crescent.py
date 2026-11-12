# Trảm Trăng Khuyết, final GIF: studio-rig body (idle -> pose A -> pose B -> idle) + a bright blue crescent slash from the blade sweep.
# Run (after `puppet.py render ... --sheet skill_crescent_puppet_side`):
#   PYTHONHASHSEED=0 python out/heroes/azure_blade/source/vfx/crescent/build_crescent.py   (gen_slash_loop places breaks with hash())
# Slash = (1) the milestone-01 layered generator on the blade sweep (streaks, teeth, debris; kept faint) under (2) the swept surface of the blade
# itself: every blade line root->tip is drawn, so the band is exactly as thick as the blade and its leading edge is parallel to it.
# Colour: tip deep blue and opaque, hilt pale and faint, a white hot leading edge and a white line on the tip's path.
import sys, json, math, pathlib
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "lib-fx" / "_core" / "formulas"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "slash_fx"))
import slash_from_track as SFT  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
ASSET = HERE.parents[2]
RIG = ASSET / "source" / "rig"
W2, H2, PX, PY = 352, 280, 176.0, 246.4
MARKS = json.loads((HERE / "weapon_marks.json").read_text())
P = json.loads((HERE / "slash_params.json").read_text())
ANIM = json.loads((RIG / "anims" / "crescent.json").read_text())
BODY = sorted((ASSET / "frames" / "skill_crescent_puppet_side" / "frames" / "@2x").glob("*.png"))


def tf_of(rig_json, key):
    """Source px of a still -> @2x cell px, the way Puppet Kit registers it (ground -> pivot, unit -> body height 120)."""
    r = json.loads(rig_json.read_text())
    s = 120.0 / r["unit"]; gx, gy = r["ground"]
    return lambda p: (PX + (p[0] - gx) * s, PY + (p[1] - gy) * s)


tfA, tfB = tf_of(RIG / "rig_a.json", "A"), tf_of(RIG / "rig_b.json", "B")
rootA, tipA, rootB, tipB = tfA(MARKS["A"]["root"]), tfA(MARKS["A"]["tip"]), tfB(MARKS["B"]["root"]), tfB(MARKS["B"]["tip"])


def sweep_samples(n):
    """Blade root/tip per step: the root on a quadratic path over the head, the blade turning clockwise on screen through 'up'."""
    LA, LB = math.dist(rootA, tipA), math.dist(rootB, tipB)
    aA = math.atan2(tipA[1] - rootA[1], tipA[0] - rootA[0]); aB = math.atan2(tipB[1] - rootB[1], tipB[0] - rootB[0])
    while aB <= aA:
        aB += 2 * math.pi
    ctrl = ((rootA[0] + rootB[0]) / 2 + MARKS["root_ctrl_dx"], min(rootA[1], rootB[1]) - MARKS["root_ctrl_up"])
    out = []
    for k in range(n):
        t = k / (n - 1); te = t ** MARKS["ease"]
        r = [(1 - t) ** 2 * rootA[i] + 2 * (1 - t) * t * ctrl[i] + t ** 2 * rootB[i] for i in (0, 1)]
        a = aA + (aB - aA) * te; L = LA + (LB - LA) * t
        out.append({"frame": k + 1, "root_px2x": r, "tip_px2x": [r[0] + L * math.cos(a), r[1] + L * math.sin(a)]})
    return out


n = P["steps"]
L = P["layered"]
fades = sorted(L["after"], key=int)
after = [L["after"][f] for f in fades]
L["after"] = {str(n + 1 + k): a for k, a in enumerate(after)}
L["grow"] = [1.0] * n
L["lag_frames"] = P["lag"]
track = {"frames": n + len(fades), "hit_frame": n, "samples": sweep_samples(n), "fit": {"frames": list(range(1, n + 1))}, "speed": {"vfx_start_frame": 2}}
frame, _, _, gen_frames, extra = SFT.render_layered(track, P)
Lnom = extra["Lnom_px2x"]
FX = P["swept"]


def lerp(a, b, t):
    return np.asarray(a, float) * (1 - t) + np.asarray(b, float) * t


def swept(head, tail, alpha, wscale):
    """RGBA float (H2, W2, 4): the surface the blade covered between sweep time `tail` and `head`, drawn at 2x and reduced."""
    SS = 2
    nu = max(8, int((head - tail) * FX["u_density"])); nv = max(8, int(Lnom * FX["v_density"]))
    u = np.linspace(tail, head, nu); v = np.linspace(0, Lnom, nv)
    U, V = np.meshgrid(u, v)
    x, y = frame.to_xy(U, V)
    uf = ((U - tail) / max(1e-6, head - tail)).ravel(); vf = (V / Lnom).ravel()
    pts = np.c_[x.ravel() * SS, y.ravel() * SS]
    tree = cKDTree(pts)
    yy, xx = np.mgrid[0:H2 * SS, 0:W2 * SS]
    d, idx = tree.query(np.c_[xx.ravel(), yy.ravel()], distance_upper_bound=FX["reach_px"] * SS)
    ok = np.isfinite(d)
    cu = np.zeros(d.shape); cv = np.zeros(d.shape)
    cu[ok] = uf[idx[ok]]; cv[ok] = vf[idx[ok]]
    # blade thickness is a property of the sweep; the cut width of the band shrinks with `wscale` (fade) by pulling the hilt end in
    a_t = np.clip(cu, 0, 1) ** FX["trail_power"]                                  # tail faint -> head full
    if tail <= u0 + 1e-6:                                                         # the first growth steps start ON the pose-A blade: keep that edge visible
        a_t = FX["start_floor"] + (1 - FX["start_floor"]) * a_t
    a_v = FX["hilt_alpha"] + (1 - FX["hilt_alpha"]) * np.clip(cv, 0, 1) ** FX["tip_power"]   # hilt faint -> tip full
    inside = ok & (cv >= (1 - wscale) * 0.0)
    a = (a_t * a_v * inside * alpha)
    # colour: tail deep blue -> mid light blue -> head white; the tip pulled to saturated deep blue, the hilt to pale
    col = np.where((cu < 0.5)[:, None], lerp(FX["c_tail"], FX["c_mid"], (cu / 0.5)[:, None]), lerp(FX["c_mid"], FX["c_head"], ((cu - 0.5) / 0.5)[:, None]))
    tipw = (np.clip(cv, 0, 1) ** FX["tip_color_power"] * FX["tip_mix"] * (1 - np.clip((cu - 0.8) / 0.2, 0, 1)))[:, None]   # not over the white head
    hiltw = ((1 - np.clip(cv, 0, 1)) ** 1.5 * FX["hilt_mix"])[:, None]
    col = col * (1 - tipw - hiltw) + np.asarray(FX["c_tip"], float) * tipw + np.asarray(FX["c_hilt"], float) * hiltw
    # white: the leading edge (parallel to the blade) and a thin line along the tip's path
    edge = np.clip((cu - (1 - FX["edge_w"])) / FX["edge_w"], 0, 1) ** 1.6
    tipline = np.clip((cv - (1 - FX["tipline_w"])) / FX["tipline_w"], 0, 1) ** 1.2 * np.clip(cu * 1.4, 0, 1)
    wh = np.clip(np.maximum(edge * FX["edge_white"], tipline * FX["tipline_white"]), 0, 1)[:, None]
    col = col * (1 - wh) + np.array([255, 255, 255.0]) * wh
    out = np.zeros((H2 * SS * W2 * SS, 4))
    out[:, :3] = col; out[:, 3] = a
    out = out.reshape(H2 * SS, W2 * SS, 4)
    # 2x2 box down-sample with premultiplied colour so the edge is anti-aliased
    pm = out[..., :3] * out[..., 3:4]
    pm = pm.reshape(H2, SS, W2, SS, 3).mean(axis=(1, 3)); al = out[..., 3].reshape(H2, SS, W2, SS).mean(axis=(1, 3))
    rgb = np.where(al[..., None] > 1e-4, pm / np.maximum(al[..., None], 1e-4), 0)
    return np.dstack([rgb, al])


def over(base, top):
    a = top[..., 3:4]; b = base[..., 3:4]
    na = a + b * (1 - a)
    rgb = np.where(na > 1e-5, (top[..., :3] * a + base[..., :3] * b * (1 - a)) / np.maximum(na, 1e-5), 0)
    return np.dstack([rgb, na[..., 0]])


def glow_of(al):
    g = ndi.gaussian_filter(al, FX["glow_sigma"]) * FX["glow_alpha"]
    return np.dstack([np.broadcast_to(np.array(FX["glow_color"], float), al.shape + (3,)), np.clip(g, 0, 1)])


# one fx image per step: growth steps 2..n (head = step), then the fades keyed on the full sweep
u0 = 1.0
fxs = []
for k in range(n):
    head = float(k + 1); tail = max(u0, head - P["lag"])
    if head - tail < 0.3:
        fxs.append(np.zeros((H2, W2, 4))); continue
    fxs.append(swept(head, tail, 1.0, 1.0))
for a in after:
    head = n + a["drift"]; tail = max(u0, n - P["lag"] * a["tail_keep"])
    fxs.append(swept(head, tail, a.get("alpha", 1.0) * min(1.0, a["w"] + 0.2), 1.0))
imgs = []
for k, s in enumerate(fxs):
    out = glow_of(s[..., 3])
    g = gen_frames[k].copy(); g[..., 3] = g[..., 3] * (FX["gen_alpha"] if k >= n - 1 else 0.0)   # the generator's loose head blob is not attached to the blade: only on the full sweep and the fades
    out = over(out, g)
    out = over(out, s)
    imgs.append(Image.fromarray(np.dstack([np.clip(out[..., :3], 0, 255), np.clip(out[..., 3], 0, 1) * 255]).round().astype(np.uint8), "RGBA"))

# timeline: fx step index onto body frame (1-based); the cut A -> B is the hit frame
hit = ANIM["hit_frame"]
place = {hit - 1: 1, hit: 5}                                   # growth step 2 over pose A (starts on its blade), the full sweep on the first pose B frame
for j in range(len(after)):
    place[hit + 1 + j] = n + j
frames = []
for i, bp in enumerate(BODY, 1):
    im = Image.open(bp).convert("RGBA")
    if i in place:
        im.alpha_composite(imgs[place[i]])
    frames.append(im)

out = ASSET / "frames" / "skill_crescent_side"
if out.exists():
    import shutil; shutil.rmtree(out)
for sub in ("@2x", "@1x"):
    (out / "frames" / sub).mkdir(parents=True, exist_ok=True)
for k, im in enumerate(frames, 1):
    im.save(out / "frames" / "@2x" / f"hero_azure_blade_skill_crescent_side_{k:02d}.png")
    im.resize((W2 // 2, H2 // 2), Image.LANCZOS).save(out / "frames" / "@1x" / f"hero_azure_blade_skill_crescent_side_{k:02d}.png")


def gif(cells, path, fps, scale, bg=(40, 44, 54, 255)):
    fr = []
    for c in cells:
        base = Image.alpha_composite(Image.new("RGBA", c.size, bg), c)
        base = base.resize((round(c.width * scale), round(c.height * scale)), Image.LANCZOS if scale < 1 else Image.NEAREST)
        fr.append(base.convert("P", palette=Image.ADAPTIVE))
    fr[0].save(path, save_all=True, append_images=fr[1:], duration=round(1000 / fps), loop=0)


fps = ANIM["fps"]
gif(frames, out / "preview_2x.gif", fps, 1.0)
gif([c.resize((W2 // 2, H2 // 2), Image.LANCZOS) for c in frames], out / "preview_game_1x_x3.gif", fps, 3)
CR = (20, 60, 300, 270)
cols = 10; cw, ch = (CR[2] - CR[0]) // 2, (CR[3] - CR[1]) // 2
sheet = Image.new("RGB", (cw * cols, ch * ((len(frames) + cols - 1) // cols)), (40, 44, 54))
for k, c in enumerate(frames):
    t = Image.alpha_composite(Image.new("RGBA", c.size, (40, 44, 54, 255)), c).crop(CR).resize((cw, ch), Image.LANCZOS)
    ImageDraw.Draw(t).text((2, 2), str(k + 1), fill=(255, 255, 0))
    sheet.paste(t.convert("RGB"), ((k % cols) * cw, (k // cols) * ch))
sheet.save(out / "contact.png")
dbg = Image.new("RGBA", (W2 * 2, H2), (40, 44, 54, 255))
for i, (idx, r, t) in enumerate(((hit - 1, rootA, tipA), (hit + 1, rootB, tipB))):
    d = frames[idx - 1].copy(); dd = ImageDraw.Draw(d)
    dd.line([r, t], fill=(255, 255, 0, 255), width=1)
    dbg.alpha_composite(Image.alpha_composite(Image.new("RGBA", d.size, (40, 44, 54, 255)), d), (i * W2, 0))
dbg.convert("RGB").save(out / "debug_marks.png")
json.dump({"samples": track["samples"], "frames": len(frames), "fps": fps, "fx_on_frames": place}, open(out / "track.json", "w"), indent=1)
print("frames", len(frames), "fx on", place, "->", out)
