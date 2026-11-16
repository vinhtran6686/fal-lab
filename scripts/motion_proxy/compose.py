"""Ghép animation từ các ảnh khung khoá đã duyệt theo nhịp của proxy (cách 'đổi tranh + vệt chém che' của ref/king).

    python scripts/motion_proxy/compose.py <compose.json> [--out DIR] [--ss 2]

compose.json:
  {"build": "<thư mục build của proxy: frames.json, params_used.json>",
   "keys": [{"still": "<ảnh khung khoá, nền magenta>", "proxy_frame": 0, "frames": [0, 7]}, ...],
   "align": {"<tên file ảnh>": {"head_top": y, "feet": y, "center": x}},   (tuỳ chọn: sửa số đo tự động, px ảnh)
   "bg": [78, 80, 84], "trail": {"span": 1.6, "inward": 1.3}}   (vệt chém: số khung quỹ đạo, độ rộng vào trong)
Mỗi ảnh được tách nền, đo (đỉnh đầu, đáy ủng, tâm hai chân) rồi đặt vào toạ độ camera proxy sao cho khớp khung
'proxy_frame': đáy ủng trên mặt đất, chiều cao đầu và tâm chân như proxy. Trong các khung 'frames' của nó, ảnh được
nghiêng (shear) và co giãn dọc, NEO Ở CHÂN, theo đầu của proxy (chân không trượt). Vệt chém lấy từ quỹ đạo mũi vũ khí
của proxy: nửa xa vẽ SAU ảnh, nửa gần vẽ TRƯỚC ảnh.
Ra: frames/fNN.png (RGBA), preview.gif, preview_slow.gif, preview_game.gif (cao 60 px), sheet.png, check/align.png.
Doc: docs/scripts/motion_proxy/motion-proxy-guide.md
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "puppet_kit"))
from skeleton import Proxy  # noqa: E402
from build import Cam, slash_trail  # noqa: E402
from paint import Painter  # noqa: E402
from core import key_magenta  # noqa: E402  (scripts/puppet_kit/core.py)


def measure(rgba):
    """Đỉnh đầu, đáy ủng, tâm hai chân của nhân vật trên ảnh đã tách nền (px ảnh)."""
    m = rgba[..., 3] > 128
    ys, xs = np.where(m)
    feet = int(ys.max())
    top = int(ys.min())
    h = feet - top
    band = m[int(feet - 0.10 * h): feet + 1]           # dải ủng
    bx = np.where(band.any(axis=0))[0]
    center = float(np.median(np.where(band)[1])) if len(bx) else float(xs.mean())
    # đỉnh đầu: điểm cao nhất trong cột quanh tâm thân (loại mũi thương ở xa hai bên)
    half = int(0.11 * m.shape[1])
    cols = m[:, max(0, int(center) - half): int(center) + half]
    rows = np.where(cols.any(axis=1))[0]
    head_top = int(rows.min()) if len(rows) else top
    return {"head_top": head_top, "feet": feet, "center": center}


def affine_inv(A):
    """Hệ số cho PIL Image.transform (AFFINE, ánh xạ ngược) từ ma trận 3x3 (ảnh nguồn -> đích)."""
    Ai = np.linalg.inv(A)
    return tuple(Ai[0, :3]) + tuple(Ai[1, :3])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out")
    ap.add_argument("--ss", type=int, default=2)
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    bdir = spec["build"]
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.spec)), "compose")
    for sub in ("frames", "check"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    P = Proxy(os.path.join(bdir, "params_used.json"))
    cam0 = Cam(**P.p.get("camera", {}))
    ss = a.ss
    cam = Cam(pitch_deg=math.degrees(cam0.pitch), scale=cam0.s * ss,
              size=(cam0.size[0] * ss, cam0.size[1] * ss), origin=(cam0.o[0] * ss, cam0.o[1] * ss))
    painter = Painter(P, cam)
    TS = P.frame_times()
    F = [P.pose(t) for t in TS]
    N = len(TS)
    head_r = P.b["head_r"]

    def proxy_marks(i):
        J, inf = F[i]
        head_top = cam.proj(J["head"] + np.array([0, head_r + 0.12, 0]))[1]   # đỉnh búi tóc
        feet_y = cam.o[1]
        cx = (cam.proj(J["toeR"])[0] + cam.proj(J["toeL"])[0]) / 2
        return {"head_top": head_top, "feet": feet_y, "center": cx,
                "head_x": cam.proj(J["head"])[0]}

    # ---- ảnh khoá: tách nền, đo, ma trận đặt vào toạ độ proxy
    keys = []
    for k in spec["keys"]:
        img = Image.open(k["still"])
        rgba = key_magenta(img)
        mk = measure(rgba)
        mk.update(spec.get("align", {}).get(os.path.basename(k["still"]), {}))
        pm = proxy_marks(k["proxy_frame"])
        s = (pm["feet"] - pm["head_top"]) / (mk["feet"] - mk["head_top"])
        M = np.array([[s, 0, pm["center"] - s * mk["center"]], [0, s, pm["feet"] - s * mk["feet"]], [0, 0, 1]])
        keys.append(dict(k, rgba=Image.fromarray(rgba.clip(0, 255).astype("uint8"), "RGBA"), M=M, mk=mk, pm=pm, s=s))

    def key_of(i):
        for k in keys:
            if k["frames"][0] <= i <= k["frames"][1]:
                return k
        return min(keys, key=lambda k: min(abs(i - k["frames"][0]), abs(i - k["frames"][1])))

    # ---- kiểm tra căn: ảnh khoá đặt lên khung khối proxy cùng khung
    chk = []
    for k in keys:
        base = Image.new("RGBA", cam.size, (200, 200, 200, 255))
        painter.draw(base, *F[k["proxy_frame"]])
        ghost = k["rgba"].transform(cam.size, Image.AFFINE, affine_inv(k["M"]), Image.BICUBIC)
        g = np.asarray(ghost).copy()
        g[..., 3] = (g[..., 3] * 0.6).astype("uint8")
        base.alpha_composite(Image.fromarray(g))
        d = ImageDraw.Draw(base)
        for y, col in ((k["pm"]["head_top"], (220, 40, 40)), (k["pm"]["feet"], (40, 160, 60))):
            d.line([(0, y), (cam.size[0], y)], fill=col, width=2)
        chk.append(base.resize(cam0.size, Image.LANCZOS))
    sheet = Image.new("RGB", (cam0.size[0] * 2, cam0.size[1] * 2), "white")
    for j, im in enumerate(chk[:4]):
        sheet.paste(im.convert("RGB"), ((j % 2) * cam0.size[0], (j // 2) * cam0.size[1]))
    sheet.save(os.path.join(out, "check", "align.png"))

    # ---- từng khung
    bg = tuple(spec.get("bg", [78, 80, 84]))
    frames_rgba, frames_bg = [], []
    for i in range(N):
        k = key_of(i)
        J, inf = F[i]
        pm_i = proxy_marks(i)
        A = np.array([k["pm"]["center"], k["pm"]["feet"]])
        h_key = k["pm"]["feet"] - k["pm"]["head_top"]
        sy = float(np.clip((pm_i["feet"] - pm_i["head_top"]) / h_key, 0.85, 1.12))
        shear = float(np.clip((pm_i["head_x"] - k["pm"]["head_x"]) / h_key, -0.25, 0.25))
        W = np.array([[1, -shear, shear * A[1]], [0, sy, A[1] - sy * A[1]], [0, 0, 1]])  # neo ở chân: x += shear·(y_chân − y)
        body = k["rgba"].transform(cam.size, Image.AFFINE, affine_inv(W @ k["M"]), Image.BICUBIC)
        layer_far = Image.new("RGBA", cam.size, (0, 0, 0, 0))
        layer_near = Image.new("RGBA", cam.size, (0, 0, 0, 0))
        tr = spec.get("trail", {})
        trail = slash_trail(P, TS[i], span=tr.get("span", 0.8), inward=tr.get("inward", 1.1))
        if trail:
            for name, d_, fn in painter.parts(J, inf, trail):
                if name == "trail_far":
                    fn(ImageDraw.Draw(layer_far))
                elif name == "trail_near":
                    fn(ImageDraw.Draw(layer_near))
        fr = Image.new("RGBA", cam.size, (0, 0, 0, 0))
        fr.alpha_composite(layer_far)
        fr.alpha_composite(body)
        fr.alpha_composite(layer_near)
        fr = fr.resize(cam0.size, Image.LANCZOS)
        fr.save(os.path.join(out, "frames", f"f{i:02d}.png"))
        frames_rgba.append(fr)
        b = Image.new("RGBA", cam0.size, bg + (255,))
        sh = Image.new("RGBA", cam0.size, (0, 0, 0, 0))
        g = (k["pm"]["center"] / ss, k["pm"]["feet"] / ss)        # bóng dưới chân của ảnh khoá
        ImageDraw.Draw(sh).ellipse([g[0] - 95, g[1] - 13, g[0] + 95, g[1] + 13], fill=(0, 0, 0, 60))
        b.alpha_composite(sh)
        b.alpha_composite(fr)
        frames_bg.append(b.convert("RGB"))

    dur = int(1000 / P.fps)
    frames_bg[0].save(os.path.join(out, "preview.gif"), save_all=True, append_images=frames_bg[1:], duration=dur, loop=0)
    frames_bg[0].save(os.path.join(out, "preview_slow.gif"), save_all=True, append_images=frames_bg[1:], duration=220, loop=0)
    # cỡ game: đầu đến chân khoảng 60 px
    h_px = (keys[0]["pm"]["feet"] - keys[0]["pm"]["head_top"]) / ss
    g = 60.0 / h_px
    small = [im.resize((max(1, int(im.width * g)), max(1, int(im.height * g))), Image.LANCZOS) for im in frames_bg]
    small[0].save(os.path.join(out, "preview_game.gif"), save_all=True, append_images=small[1:], duration=dur, loop=0)
    cols = 6
    tw, th = cam0.size[0] // 2, cam0.size[1] // 2
    sh = Image.new("RGB", (cols * tw, math.ceil(N / cols) * (th + 18)), "white")
    d = ImageDraw.Draw(sh)
    for i, im in enumerate(frames_bg):
        x, y = (i % cols) * tw, (i // cols) * (th + 18)
        sh.paste(im.resize((tw, th), Image.LANCZOS), (x, y + 18))
        d.text((x + 4, y + 3), f"{i:02d} {P.phase_of(TS[i])} · {os.path.basename(key_of(i)['still'])}", fill="black")
    sh.save(os.path.join(out, "sheet.png"))
    print(json.dumps({os.path.basename(k["still"]): {"measured": k["mk"], "scale": round(k["s"], 4)} for k in keys},
                     indent=1))
    print("->", out)


if __name__ == "__main__":
    main()
