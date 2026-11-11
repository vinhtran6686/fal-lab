"""Asset preparation helpers for the Puppet Kit (docs/puppet-kit-next.md section 2).

  puppet_prep.py list  <asset> [--write-prompts] [--layers a,b]   missing resources + filled prompts
  puppet_prep.py align <asset> <image> [--colour r,g,b] [--kind plate|pose|profile] [--overlay out.png]
"""
import argparse
import json
import pathlib
import re
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from puppet import colour_mask  # noqa: E402
from puppet_kit.core import key_magenta  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMAT_MD = ROOT / ".claude" / "skills" / "fal-image" / "format.md"

# (canonical name, glob stem in the folder, folder, what it is for); layers are expanded from --layers
FIXED = [
    ("master", "master_v*", "design", "idle, style and size anchor"),
    ("plate", "plate_v*", "rig", "torso layer (master without arms, weapon, tail)"),
    ("plate_legs", "plate_legs_v*", "design", "hip joint and leg rig (master without arms and legs)"),
    ("parts", "parts_v*", "design", "A-pose sheet to cut limb segments (profile only for 3/4 rigs)"),
    ("profile", "profile_v*", "design", "second rig for run/walk, anchor of body turns"),
    ("profile_plate", "profile_plate_v*", "design", "profile rig torso"),
    ("profile_parts", "profile_parts_v*", "design", "profile limb segments"),
    ("pose_turn", "pose_turn_*_v*", "design", "pose between 3/4 and profile (body turn)"),
]


def read_text_safe(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""


def brief_slots(asset):
    txt = read_text_safe(asset / "brief.md")
    m = re.search(r"^- `\{design\}`:\s*(.+)$", txt, re.M)
    design = m.group(1).strip() if m else None
    m = re.search(r"`\{H\}`\s*(\d+)\s*px", txt)
    h = int(m.group(1)) if m else 64
    return design, h


def format_blocks():
    """STYLE, BG and SIMPLE read from fal-image/format.md so the prompts never drift from the skill."""
    txt = FORMAT_MD.read_text(encoding="utf-8")

    def quote_after(marker):
        i = txt.index(marker)
        out = []
        for line in txt[i:].splitlines()[1:]:
            if line.startswith(">"):
                out.append(line[1:].strip())
            elif out:
                break
        return " ".join(out)

    return {"STYLE": quote_after("## 1. Style block"), "BG": quote_after("`{BG}` (append"),
            "SIMPLE": quote_after("`{SIMPLE}` (append")}


def latest(folder, pattern):
    files = sorted(folder.glob(pattern + ".png"), key=lambda p: [int(x) for x in re.findall(r"\d+", p.stem)])
    return files[-1] if files else None


def inventory(asset, layers):
    rows = []
    for name, pat, where, use in FIXED:
        d = asset / "source" / ("rig" if where == "rig" else "design")
        rows.append((name, latest(d, pat), use))
    for ly in layers:
        rows.append((f"layer_{ly}", latest(asset / "source" / "design", f"layer_{ly}_v*"),
                     f"hidden part '{ly}' drawn complete (replaces fill_under/grow)"))
    return rows


def prompts_for(name, design, h, blocks, view):
    bg, style = blocks["BG"], blocks["STYLE"].replace("{H}", str(h))
    simple = blocks["SIMPLE"]
    keep = ("Keep EXACTLY the same character, the same drawing, the same size and the same position in the frame, "
            "the same colours and outlines.")
    tail = f"{bg} {style}"
    if name == "plate_legs":
        return (f"Edit the reference image. {keep} Change only this: REMOVE both arms completely from the shoulder down "
                "and REMOVE the tail and BOTH legs and feet completely. The body ends at the hips: draw the complete hip "
                "line and the bottom hem of the garment with smooth outer edges, and the full sides of the torso and waist "
                f"that the arms used to cover. Single game hero sprite, same framing as the reference. {tail}")
    if name.startswith("layer_"):
        part = name[len("layer_"):].replace("_", " ")
        return (f"Edit the reference image by ERASING parts of it. {keep} Draw ONLY the {part}, complete, including what the "
                "body normally hides, same size and same position as in the reference, nothing else in the picture. "
                f"Every other part becomes flat background. {tail}")
    if name == "parts":
        return (f"Single game hero sprite sheet of the character in the reference image: {design} A-pose, arms 45 degrees "
                "away from the body, legs apart, every joint (shoulder, elbow, wrist, hip, knee, ankle) clearly visible, "
                "no limb overlapping another. The head and the mane or helmet exactly as big as in the reference. "
                f"Full body inside the frame with margin on every side. {simple} {tail}")
    if name == "profile":
        return (f"Single game hero sprite: {design} {view_profile()} The head and the mane or helmet exactly as big as in the "
                f"reference, same colours and outlines. {simple} {tail}")
    if name in ("profile_plate", "profile_parts"):
        base = ("Edit the reference image (the profile still). " + keep + " ")
        if name == "profile_plate":
            return (base + "Change only this: REMOVE both arms completely from the shoulder down and the tail, and draw "
                    f"what they hid behind them with smooth outer edges. {tail}")
        return (base + "Change only this: pose the character in an A-pose, arms 45 degrees away from the body, legs apart, "
                f"every joint clearly visible, no limb overlapping another. {tail}")
    if name == "pose_turn":
        return (f"Single game hero sprite: {design} Body turn halfway between the three-quarter view of the reference and a "
                "pure side profile facing right: torso rotated about 45 degrees further toward the right edge, feet stay "
                "on the same ground line. The head and the mane or helmet exactly as big as in the reference. "
                f"{simple} {tail}")
    return None


def view_profile():
    return ("Pure SIDE PROFILE facing right, one eye visible, the near arm and near leg fully visible, not a three-quarter "
            "view, standing at rest with feet apart on one ground line, arms hanging a little away from the body.")


def cmd_list(a):
    asset = pathlib.Path(a.asset)
    design, h = brief_slots(asset)
    layers = [s for s in a.layers.split(",") if s]
    rows = inventory(asset, layers)
    print(f"# {asset.name}: H={h}px, design {'found' if design else 'MISSING in brief.md'}\n")
    print("| Resource | Status | File | Used for |\n|---|---|---|---|")
    for name, f, use in rows:
        print(f"| {name} | {'có' if f else 'thiếu'} | {f.name if f else '-'} | {use} |")
    master = next((f for n, f, _ in rows if n == "master" and f), None)
    missing = [n for n, f, _ in rows if not f and (n != "master")]
    if not a.write_prompts:
        return
    if not (design and master):
        sys.exit("need the {design} line in brief.md and a master_v* still to write prompts")
    blocks = format_blocks()
    out_dir = asset / "source" / "design" / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    print()
    for name in missing:
        text = prompts_for(name, design, h, blocks, None)
        if not text:
            continue
        if re.search(r"[{\[]", text):
            sys.exit(f"[puppet_prep] prompt for {name} still has an unfilled placeholder")
        f = out_dir / f"{name}_p01.txt"
        if f.exists():
            print(f"keep  {f} (exists)")
        else:
            f.write_text(text + "\n", encoding="utf-8")
            print(f"wrote {f}")
        print(f"python scripts/gen_image.py --prompt-file {f.as_posix()} --ref {master.as_posix()} --size 1024x1024 "
              f"--png --name {name} --versioned --out {(asset / 'source' / 'design').as_posix()}")


def silhouette(rgba):
    m = rgba[..., 3] > 128
    ys, xs = np.where(m)
    return m, (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))


def cmd_align(a):
    asset = pathlib.Path(a.asset)
    rigf = asset / "source" / "rig" / "rig.json"
    master = None
    if rigf.exists():
        spec = json.loads(rigf.read_text(encoding="utf-8"))
        rel = spec.get("sources", {}).get("master")
        if rel:
            master = (rigf.parent / rel).resolve()
    if not master or not master.exists():
        master = latest(asset / "source" / "design", "master_v*")
    if not master:
        sys.exit("no master found for this asset")
    ma, na = key_magenta(Image.open(master)), key_magenta(Image.open(a.image))
    mm, mb = silhouette(ma)
    nm, nb = silhouette(na)
    names = ("left", "top", "right", "bottom")
    print(f"master {master.name}, image {pathlib.Path(a.image).name}, kind {a.kind}")
    for n, x, y in zip(names, mb, nb):
        print(f"bbox {n}: master {x}, image {y}, diff {y - x:+d} px")
    foot = nb[3] - mb[3]
    print(f"foot row diff: {foot:+d} px")
    fails = []
    k = None
    if a.colour:
        col = [float(v) for v in a.colour.split(",")]
        am, bm = colour_mask(ma, col), colour_mask(na, col)
        if am.sum() < 500 or bm.sum() < 500:
            fails.append(f"colour {a.colour} covers too few pixels (master {int(am.sum())}, image {int(bm.sum())})")
        else:
            k = float(np.sqrt(bm.sum() / am.sum()))
            print(f"scale (sqrt area ratio of colour {a.colour}): {k:.3f}")
    if a.kind == "plate":
        if abs(foot) > 8:
            fails.append(f"foot row off by {foot:+d} px (limit 8)")
        if abs(nb[1] - mb[1]) > 12:
            fails.append(f"top edge off by {nb[1] - mb[1]:+d} px (limit 12)")
        if k is not None and not 0.97 <= k <= 1.03:
            fails.append(f"scale {k:.3f} outside 0.97-1.03")
    else:
        if k is None:
            fails.append("--colour is required to check the scale of a pose/profile")
        elif not 0.95 <= k <= 1.05:
            fails.append(f"scale {k:.3f} outside 0.95-1.05")
        if a.colour:
            print(f"hint: python scripts/puppet.py pose {a.asset} --still <path under asset> --colour {a.colour} --name <pose_name>")
    if a.overlay:
        h, w = max(ma.shape[0], na.shape[0]), max(ma.shape[1], na.shape[1])
        canvas = np.zeros((h, w, 3), np.float32)
        canvas[:mm.shape[0], :mm.shape[1], 0] += mm * 127
        canvas[:nm.shape[0], :nm.shape[1], 1] += nm * 127
        Image.fromarray(np.clip(canvas * 2, 0, 255).astype(np.uint8)).save(a.overlay)
        print(f"overlay written to {a.overlay}")
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        sys.exit(1)
    print("PASS")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list")
    s.add_argument("asset")
    s.add_argument("--write-prompts", action="store_true")
    s.add_argument("--layers", default="")
    s.set_defaults(fn=cmd_list)
    s = sub.add_parser("align")
    s.add_argument("asset")
    s.add_argument("image")
    s.add_argument("--colour")
    s.add_argument("--kind", choices=["plate", "pose", "profile"], default="plate")
    s.add_argument("--overlay")
    s.set_defaults(fn=cmd_align)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
