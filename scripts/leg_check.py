#!/usr/bin/env python3
"""Make a zoomed "legs only" contact sheet of a packed walk, so the leading leg of every
frame can be read reliably (at full-sheet size the legs are too small to tell apart).

Usage: python scripts/leg_check.py out/enemies/bandit/walk_down_side/v02 [--flip]
       python scripts/leg_check.py --observed LL?RRRLL [--expected LL-RRR-L] [--bad 7]   # suggest an --order fix

Reads <version dir>/frames/@2x/*.png, crops each frame from the thighs down (hands and
weapons above stay out of the way), enlarges it, numbers it, lays the frames out 4 per row
and writes <version dir>/check/legcheck.png. Open that image and write down, per frame,
which leg is in front (see the leg standard in classes/enemy.md). --flip previews a mirrored
direction (e.g. walk_down_left from walk_down_side): left and right legs swap.

--observed takes the lead foot seen in each frame (L/R, ? = unreadable) and --expected the
pattern from the sheet's blueprint.md (L/R, - = passing frame where either foot is fine; the
8-frame biped walk default is LL-RRR-L: contact L, down, passing, up, contact R, down, passing, up).
It prints the `sprite_pack.py --order` that replaces each wrong frame with the nearest correct
frame showing the foot it needs. --bad lists frames wrong for another reason (frozen pose,
glitch): they are always replaced and never used as a replacement.
"""
import argparse, pathlib, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps


DEFAULT_EXPECTED = {8: "LL-RRR-L"}   # 8-frame biped walk: contact, down, passing, up, then the mirrored step


def suggest_order(observed: str, expected: str, bad: set) -> str:
    obs = observed.strip().upper()
    want = expected.strip().upper()
    if not obs or set(obs) - {"L", "R", "?"}:
        sys.exit("--observed must be L, R or ? (unreadable), one per frame, e.g. LL?RRR?L")
    if len(want) != len(obs) or set(want) - {"L", "R", "-"}:
        sys.exit("--expected must be L, R or - (passing: either), same length as --observed")
    ok = lambda i: (want[i] == "-" or obs[i] in (want[i], "?")) and i + 1 not in bad
    good = [i for i in range(len(obs)) if ok(i) and obs[i] != "?"]
    order, fixes, unknown = [], [], []
    for i in range(len(obs)):
        if ok(i):
            order.append(i + 1)
            if obs[i] == "?" and want[i] != "-":
                unknown.append(str(i + 1))
            continue
        # a replacement must show the needed lead foot; for a passing frame, another passing frame
        cands = [j for j in good if (obs[j] == want[i]) if want[i] != "-"] or                 [j for j in good if want[j] == "-" and want[i] == "-"]
        if not cands:
            sys.exit(f"no correct frame can replace frame {i + 1} (needs {want[i]}): regenerate this sheet")
        j = min(cands, key=lambda j: (min(abs(j - i), len(obs) - abs(j - i)), j))
        order.append(j + 1)
        why = "marked bad" if i + 1 in bad else f"{obs[i]}, needs {want[i]}"
        fixes.append(f"frame {i + 1} ({why}) -> frame {j + 1}")
    print("expected:", want, " (- = passing, either foot)")
    print("observed:", obs)
    for f in fixes:
        print(" ", f)
    if unknown:
        print("  unreadable frames:", ",".join(unknown), "-> ask the user to confirm in Motion Lab")
    return ",".join(map(str, order)) if fixes else ""


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("version_dir", nargs="?")
    p.add_argument("--flip", action="store_true")
    p.add_argument("--observed", help="lead foot seen per frame: L, R or ?, e.g. LL?RRR?L")
    p.add_argument("--expected", help="lead foot per frame from the blueprint: L, R or - (default for 8 frames: LL-RRR-L)")
    p.add_argument("--bad", default="", help="frames wrong for another reason, e.g. 7 or 6,7")
    a = p.parse_args()
    if a.observed:
        expected = a.expected or DEFAULT_EXPECTED.get(len(a.observed.strip()))
        if not expected:
            sys.exit("give --expected (the lead-foot pattern from the sheet's blueprint.md)")
        order = suggest_order(a.observed, expected, {int(v) for v in a.bad.split(",") if v.strip()})
        print(f"--order {order}" if order else "matches the blueprint: no re-order needed")
        return
    if not a.version_dir:
        sys.exit("give a packed version folder, or --observed")
    vdir = pathlib.Path(a.version_dir)
    frames = sorted((vdir / "frames" / "@2x").glob("*.png"))
    if not frames:
        sys.exit(f"no frames in {vdir / 'frames' / '@2x'}")

    crops = []
    for f in frames:
        im = Image.open(f).convert("RGBA")
        if a.flip:
            im = ImageOps.mirror(im)
        box = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
        x0, y0, x1, y1 = box
        top = y0 + int((y1 - y0) * 0.66)            # thighs down
        leg = im.crop((max(0, x0 - 8), top, min(im.width, x1 + 8), min(im.height, y1 + 6)))
        leg = leg.resize((leg.width * 3, leg.height * 3), Image.NEAREST)
        bg = Image.new("RGBA", leg.size, (226, 214, 190, 255))
        crops.append(Image.alpha_composite(bg, leg))

    cw, ch, pad, label, per = max(c.width for c in crops), max(c.height for c in crops), 12, 34, 4
    rows = (len(crops) + per - 1) // per
    sheet = Image.new("RGB", (per * (cw + pad) + pad, rows * (ch + label + pad) + pad), (40, 44, 52))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 26)
    except OSError:
        font = ImageFont.load_default()
    for i, c in enumerate(crops):
        x = pad + (i % per) * (cw + pad)
        y = pad + (i // per) * (ch + label + pad)
        sheet.paste(c, (x + (cw - c.width) // 2, y + label + (ch - c.height)), c)
        d.text((x + 4, y), f"F{i + 1}", fill=(255, 255, 255), font=font)
    (vdir / "check").mkdir(exist_ok=True)
    out = vdir / "check" / ("legcheck_flipped.png" if a.flip else "legcheck.png")
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
