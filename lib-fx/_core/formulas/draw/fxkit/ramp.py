"""fxkit / ramp: the colours of an effect. One Ramp = one hue family in ordered steps, dark to bright:
  back (see-through dark backing) < tip < rim < body < light < core < white, plus accent (a neighbour hue for a few sparks) and
  the smoke tones made for this ramp. Layers never pick RGB numbers: they ask the ramp by ROLE and by HEAT, so
    - the hottest tones (white, core) only appear where and when the effect is hot, and shrink as it cools;
    - dark tones sit on the outside and at the end of life; an effect cools DOWN the ramp, it never just turns transparent;
    - a palette swap recolours every layer of every effect at once.
Colour rules checked by Ramp.problems(): lightness strictly rising rim < body < light < core < white with a clear step,
the hue drifting no more than 45 degrees between neighbours, the body saturated, the white almost white.
"""
import colorsys
import palettes

ORDER = ("rim", "body", "light", "core", "white")


def _hls(c): return colorsys.rgb_to_hls(*(v / 255 for v in c))
def _rgb(h, l, s): return tuple(round(255 * v) for v in colorsys.hls_to_rgb(h % 1.0, max(0.0, min(1.0, l)), max(0.0, min(1.0, s))))
def lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
def mix(a, b, k): return tuple(round(x + (y - x) * k) for x, y in zip(a, b))


class Ramp(dict):
    @classmethod
    def of(cls, pal):
        """A Ramp from a palette name, a palette dict (the five standard steps; extra keys are kept) or a Ramp."""
        if isinstance(pal, Ramp): return pal
        if isinstance(pal, str): pal = palettes.PALETTES[pal]
        r = cls(pal)
        h, l, s = _hls(r["rim"]); hb, lb, sb = _hls(r["body"]); hl = _hls(r["light"])[0]
        away = -1 if ((hl - hb + 0.5) % 1.0 - 0.5) > 0 else 1             # the direction on the hue wheel AWAY from the light step
        r.setdefault("tip", _rgb(h + away * 0.02, l * 0.82, min(1.0, s * 1.05)))     # the outermost edge: darker, a bit deeper in hue
        r.setdefault("back", _rgb(h + away * 0.03, l * 0.5, s * 0.9))                 # dark backing under bright shapes
        r.setdefault("accent", _rgb(hb - away * 0.085, max(0.62, lb), min(1.0, sb * 1.1)))   # ~30 degrees towards the light: a few sparks
        return r

    def tone(self, name):
        """A flat tone of the house style, by what it is for (rules/01 section 3: three or four tones of one hue family, about
        50-65 apart in lightness, the brightest deepest inside the mass or at the root):
          shade  the darkest: the cold tail, a far / back shape        deep  the inner darker patches of a mass
          main   the big readable colour of the effect                 hot   the hottest part: root, core, leading edge
          white  only for one- or two-frame flashes                    smoke / smoke_dark  see-through masses behind the effect"""
        if name == "shade": return mix(self["rim"], self["body"], 0.35)
        if name == "deep": return self["body"]
        if name == "main": return self["light"]
        if name == "hot": return self["core"]
        if name == "smoke": return mix((70, 74, 84), self["rim"], 0.18)
        if name == "smoke_dark": return mix((22, 24, 30), self["rim"], 0.12)
        return self[name]

    def step(self, heat):
        """One flat colour for a small shape at heat 1 (white-hot) .. 0 (cold): white, core, light, body, rim, tip."""
        keys = ("tip", "rim", "body", "light", "core", "white")
        return self[keys[max(0, min(5, int(heat * 5.999)))]]

    def bands(self, s=1.0, heat=1.0, k=1.0):
        """Edge -> centre colour bands for organic.Shape.paint: [(px from the edge, colour), ..., (None, colour)]. k scales the
        band widths (small shapes: k < 1). As heat falls every band grows deeper into the shape, so the white centre closes first,
        then the core, then the light: the shape cools from its edges inward, step by step, and ends as rim and body with a
        little light left only in its thickest part. Never a jump from white to one flat colour."""
        c = 1 - max(0.0, min(1.0, heat))                                  # how far it has cooled
        u = s * k
        out = [(1.3 * u, self["tip"]), (3.4 * u * (1 + 0.2 * c), self["rim"]), (6.4 * u * (1 + 2.2 * c), self["body"]),
               (9.5 * u * (1 + 4.5 * c), self["light"])]
        if heat > 0.15: out.append((13.5 * u / max(0.15, heat) ** 1.3, self["core"]))
        out.append((None, self["white"] if heat > 0.15 else self["core"]))
        return out

    def smoke(self, tone="light", warm=0.0):
        """Flat tones for dust / smoke: shadow, base, light, high, curl, back. Dust is never plain grey: it takes a little of the
        effect's hue, its shadow leans cool and, while the effect is hot (warm 0..1), its lit side takes the ramp's light."""
        base = {"light": ((122, 118, 112), (172, 166, 150), (212, 206, 186), (238, 234, 218), (144, 138, 126), (88, 86, 82)),
                "dark": ((70, 70, 72), (104, 102, 98), (136, 134, 124), (164, 160, 146), (86, 84, 82), (52, 52, 56))}[tone]
        tint = self["body"]
        sh, ba, li, hi, cu, bk = (mix(c, tint, 0.09) for c in base)
        sh = mix(sh, (70, 84, 120), 0.14)                                    # cool shadow
        if warm > 0: li, hi = mix(li, self["light"], 0.45 * warm), mix(hi, self["core"], 0.55 * warm)
        return dict(shadow=sh, base=ba, light=li, high=hi, curl=cu, back=bk)

    def problems(self):
        out = []
        ls = [lum(self[k]) for k in ORDER]
        for (ka, a), (kb, b) in zip(zip(ORDER, ls), zip(ORDER[1:], ls[1:])):
            if b - a < 8 and kb != "white": out.append(f"{kb} is not clearly lighter than {ka} ({b:.0f} vs {a:.0f})")
            if b < a: out.append(f"{kb} is darker than {ka}")
        hs = [_hls(self[k]) for k in ORDER[:4]]
        for ka, kb, a, b in zip(ORDER, ORDER[1:4], hs, hs[1:]):
            if a[2] > 0.15 and b[2] > 0.15 and abs((a[0] - b[0] + 0.5) % 1.0 - 0.5) * 360 > 45: out.append(f"hue jumps more than 45 degrees from {ka} to {kb}")
        if _hls(self["body"])[2] < 0.4: out.append("body is not saturated enough (grey effect)")
        if lum(self["white"]) < 225: out.append("white is not bright enough for a flash")
        return out
