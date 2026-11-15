#!/usr/bin/env python3
"""Lint a character prompt BEFORE it is sent to gen_image.py (costs nothing).

    python scripts/prompt_lint.py <prompt.txt> [--body brawny|slender|agile] [--kind master|pose]

It checks what the chunky style (`.claude/skills/fal-image/style-chunky.md`) and `preflight.md` ask for:
required parts, banned words, words that return the wrong body, vague quantity words, frame fit, colour families.
Exit code 1 when there is an ERROR; WARN lines are things to read and decide.
"""
import argparse
import colorsys
import re
import sys

BANNED = ["ornate", "intricate", "highly detailed", "pixel art", "kawaii", "adorable", "rim light"]
CONTEXT_OK = ["cute", "chibi", "mascot"]            # allowed only after never / not / no
WRONG_BODY = ["stout", "massive", "enormous", "barrel", "bean-like", "squash and stretch", "big round", "huge"]
VAGUE = ["slightly", "a little", "somewhat", "a bit", "dynamic", "natural", "elegant", "more or less", "powerful stance"]
GAMES = ["kingdom rush", "iron marines", "warcraft", "hearthstone", "league of legends", "genshin", "diablo", "dota", "clash of clans"]


def hexes(text):
    return re.findall(r"#([0-9A-Fa-f]{6})\b", text)


def hsv(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(r, g, b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("--body", choices=["brawny", "slender", "agile"], default="brawny")
    ap.add_argument("--kind", choices=["master", "pose"], default="master", help="pose: a pose still of an approved master (no UPRIGHT, a named ORIENTATION instead of a master view)")
    a = ap.parse_args()
    t = open(a.prompt, encoding="utf-8").read()
    low = t.lower()
    err, warn = [], []

    # required parts
    req = [("Background:", "background sentence"), ("#FF00FF", "magenta key colour"),
           ("TWO ARMS", "two arms the same size"), ("TWO LEGS", "two legs the same size")]
    if a.kind == "master":
        req.append(("UPRIGHT", "upright idle"))
    for key, why in req:
        if key not in t:
            err.append(f"missing {why} ({key!r})")
    if a.kind == "master":
        if not re.search(r"NEAR-FRONT VIEW|SIDE VIEW|FRONT VIEW|BACK VIEW|VIEWED FROM BEHIND", t):
            err.append("missing a named view (NEAR-FRONT VIEW / SIDE VIEW ...)")
    else:
        if "ORIENTATION:" not in t:
            err.append("missing a named ORIENTATION (action-planes.md section 4b)")
        if "visible" not in low and "NOT visible" not in t:
            warn.append("no visible / NOT visible list for the body orientation")
    if "COLOUR PLAN" not in t:
        err.append("missing COLOUR PLAN with hex values")
    if "outline" not in low:
        err.append("missing outline description")
    if "glowing" not in low and "fewest" not in low:
        warn.append("no face rule (glowing eyes / fewest marks)")

    # banned words and context-only words
    for w in BANNED:
        if w in low:
            err.append(f"banned word: {w!r}")
    for w in CONTEXT_OK:
        for m in re.finditer(w, low):
            before = low[max(0, m.start() - 14):m.start()]
            if not re.search(r"never|not |no |nor ", before):
                err.append(f"{w!r} outside a negation: ...{t[max(0, m.start() - 20):m.end() + 10]!r}")
    for g in GAMES:
        if g in low:
            err.append(f"commercial game name: {g!r}")

    # words that return the wrong body
    if a.body in ("slender", "agile"):
        for w in WRONG_BODY:
            for m in re.finditer(w, low):
                warn.append(f"{w!r} returns a brawny body (--body {a.body}): ...{t[max(0, m.start() - 25):m.end() + 15]!r}")

    # vague words
    for w in VAGUE:
        for m in re.finditer(w, low):
            ctx = low[m.start():m.end() + 16]
            if w == "a little" and "bigger than life" in ctx:
                continue
            warn.append(f"vague word {w!r}: ...{t[max(0, m.start() - 25):m.end() + 20]!r}")

    # magenta / pink outside the background sentence
    body = re.sub(r"Background:.*?Do not use magenta or pink anywhere on the subject\.", "", t, flags=re.S)
    if re.search(r"magenta|pink", body, flags=re.I):
        err.append("magenta or pink named outside the background sentence")

    # frame fit
    fill = re.search(r"filling about (\d+)% of the frame height", t)
    top = re.search(r"at least (\d+)% below the top edge", t)
    tall = re.search(r"(taller than|longer than)", low)
    if fill and tall and int(fill.group(1)) > 66:
        warn.append(f"a weapon taller than the figure with the figure filling {fill.group(1)}%: use 60-66% or the tip leaves the frame")
    if top and int(top.group(1)) < 8:
        warn.append(f"tip margin {top.group(1)}% is below 8%")
    if a.kind == "pose":
        mm = re.search(r"margin of at least (\d+)%", t)
        if not mm:
            warn.append("no frame margin sentence ('a margin of at least 10% on every side')")
    elif not top and re.search(r"staff|spear|glaive|dao|polearm|bow", low):
        warn.append("a long weapon without a tip margin sentence ('at least 8% below the top edge')")

    # colour plan
    hx = hexes(t)
    uniq = sorted(set(h.upper() for h in hx))
    if len(uniq) < 10:
        warn.append(f"only {len(uniq)} distinct hex values (a colour plan has about 14-20)")
    fams = set()
    for h in uniq:
        hh, s, v = hsv(h)
        if s >= 0.15 and v >= 0.15:
            fams.add(int(hh * 360 // 40) % 9)
    if len(fams) > 5:
        warn.append(f"{len(fams)} hue families in the hex list (target: dominant + warm + accent + cream, at most 5)")
    for m in re.finditer(r"base (#[0-9A-Fa-f]{6})", t):
        v = hsv(m.group(1)[1:])[2]
        if v < 0.40:
            warn.append(f"base colour {m.group(1)} is near-black (value {v:.2f}): large areas turn into a dark mass at 60 px")

    print(f"{a.prompt}: {len(t)} characters, {len(uniq)} hex values, {len(fams)} hue families")
    for e in err:
        print("ERROR", e)
    for w in warn:
        print("WARN ", w)
    if not err and not warn:
        print("clean")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
