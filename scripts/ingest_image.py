#!/usr/bin/env python3
"""Take a still made outside this project (ChatGPT, by hand: fal-image --manual), check it against our rules and file it as the next version.

Usage:
  python scripts/ingest_image.py <image> --out <asset>/design --name master [--prompt-file p.txt] [--note "why chosen"]
  python scripts/ingest_image.py <image> --check      checks only: prints the report, writes nothing (use before the user approves)

What it does: opens any format (webp, jpg, png), puts it on a 1024x1024 canvas (a non-square image is centred on magenta, a different
square size is resized), measures the flat magenta background, the margins around the subject and the share of the frame it fills,
writes <name>_vNN.png (next free number) and a <name>_vNN.json sidecar (source "manual", the prompt if given, cost 0). It never
touches out/costs.csv: nothing was paid to fal. Only files the user has approved ("chốt") should be ingested; a candidate is checked with --check.
Exit status 0 even when a warning is printed: the warnings are for the art director's review (format.md §6)."""
import argparse, json, pathlib, sys, time
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from gen_image import next_version

KEY = np.array([255, 0, 255], np.float32); SIDE = 1024; HARD = 90

def to_canvas(im: Image.Image):
    im = im.convert("RGBA"); flat = Image.new("RGBA", im.size, (255, 0, 255, 255)); flat.alpha_composite(im); im = flat.convert("RGB")
    notes = []
    if im.size == (SIDE, SIDE): return im, notes
    w, h = im.size
    if w == h:
        notes.append(f"resized {w}x{h} -> {SIDE}x{SIDE}"); return im.resize((SIDE, SIDE), Image.LANCZOS), notes
    s = min(SIDE / w, SIDE / h); nw, nh = round(w * s), round(h * s)
    c = Image.new("RGB", (SIDE, SIDE), (255, 0, 255)); c.paste(im.resize((nw, nh), Image.LANCZOS), ((SIDE - nw) // 2, (SIDE - nh) // 2))
    notes.append(f"{w}x{h} is not square: fitted and centred on magenta ({nw}x{nh}); better to ask for 1024x1024 again"); return c, notes

def measure(im: Image.Image) -> dict:
    a = np.asarray(im, np.float32); d = np.sqrt(((a - KEY) ** 2).sum(axis=2)); bg = d < HARD
    border = np.concatenate([bg[0], bg[-1], bg[:, 0], bg[:, -1]])
    subject = ~bg; ys, xs = np.nonzero(subject)
    r = {"border_is_magenta": round(float(border.mean()), 3), "subject_px": int(subject.sum())}
    if not len(ys): r["bbox"] = None; return r
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    r["bbox"] = [x0, y0, x1, y1]; r["margins"] = {"left": x0, "top": y0, "right": SIDE - x1, "bottom": SIDE - y1}
    r["height_fill"] = round((y1 - y0) / SIDE, 3); r["width_fill"] = round((x1 - x0) / SIDE, 3)
    k = np.minimum(a[..., 0], a[..., 2]) - a[..., 1]
    inner = subject.copy()                     # ignore the 3px anti-aliased fringe next to the background (always tinted)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            inner &= np.roll(np.roll(subject, dy, 0), dx, 1)
    r["magenta_tint_in_subject"] = round(float(((k > 60) & inner).sum() / max(1, inner.sum())), 4)
    r["bg_noise"] = round(float(d[bg].std()), 2) if bg.any() else None
    return r

def warnings(m: dict) -> list:
    w = []
    if m["bbox"] is None: return ["no subject found: the whole image is background"]
    if m["border_is_magenta"] < 0.97: w.append(f"background is not one flat magenta at the border ({m['border_is_magenta']:.0%} magenta): the key will leave a halo or cut the subject")
    mg = min(m["margins"].values())
    if mg < 24: w.append(f"the subject comes within {mg}px of the frame edge ({m['margins']}): something may be cut off; format.md wants margin on every side")
    if not 0.55 <= m["height_fill"] <= 0.85: w.append(f"the subject fills {m['height_fill']:.0%} of the frame height; the target is about 70% (a long weapon or a flyer may differ)")
    if m["magenta_tint_in_subject"] > 0.01: w.append(f"{m['magenta_tint_in_subject']:.1%} of the subject has a magenta/pink tint: the key will turn it transparent; check clothing and fire")
    if m["bg_noise"] and m["bg_noise"] > 12: w.append(f"background is noisy/gradient (std {m['bg_noise']}): it should be one flat colour")
    return w

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("image"); p.add_argument("--out"); p.add_argument("--name"); p.add_argument("--prompt-file"); p.add_argument("--note", default="")
    p.add_argument("--check", action="store_true", help="report only, write nothing")
    a = p.parse_args()
    src = pathlib.Path(a.image)
    if not src.is_file(): sys.exit(f"image not found: {src}")
    im, notes = to_canvas(Image.open(src)); m = measure(im); warn = notes + warnings(m)
    print(json.dumps({"source": str(src), "checks": m, "warnings": warn}, ensure_ascii=False, indent=1))
    if a.check: return
    if not a.out or not a.name: sys.exit("--out and --name are needed to file the image (or use --check)")
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in a.name.strip())[:40]
    path = out / f"{stem}_v{next_version(out, stem):02d}.png"; im.save(path, optimize=True)
    prompt = pathlib.Path(a.prompt_file).read_text(encoding="utf-8").strip() if a.prompt_file else None
    path.with_suffix(".json").write_text(json.dumps({"source": "manual", "tool": "chatgpt (sent by the user)", "original": src.name, "prompt": prompt,
        "note": a.note, "size": f"{SIDE}x{SIDE}", "cost_usd": 0, "checks": m, "warnings": warn, "ingested": time.strftime("%Y-%m-%d %H:%M:%S")},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(path.resolve().relative_to(ROOT).as_posix() if path.resolve().is_relative_to(ROOT) else path)

if __name__ == "__main__":
    main()
