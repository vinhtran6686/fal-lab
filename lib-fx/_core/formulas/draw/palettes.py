"""lib-fx standard palettes. Every palette has the same five steps, dark to bright:
  rim    dark outline of the same hue      body   main colour
  light  lit side / soft fill              core   hot inner line       white  the brightest point
An effect takes any of them (pal=...), so "a shock wave in ice" is a palette, not a new effect.
"""

SUN = dict(rim=(168, 90, 18), body=(255, 182, 46), light=(255, 222, 128), core=(255, 245, 220), white=(255, 255, 250))       # warm gold (Surya)
FIRE = dict(rim=(140, 30, 10), body=(240, 90, 20), light=(255, 160, 50), core=(255, 225, 140), white=(255, 250, 225))
ICE = dict(rim=(30, 80, 140), body=(90, 170, 235), light=(160, 220, 255), core=(225, 245, 255), white=(250, 254, 255))
WATER = dict(rim=(20, 60, 120), body=(40, 130, 210), light=(110, 190, 245), core=(200, 235, 255), white=(245, 252, 255))
LIGHTNING = dict(rim=(60, 50, 150), body=(120, 150, 255), light=(185, 210, 255), core=(235, 245, 255), white=(255, 255, 255))
EARTH = dict(rim=(80, 52, 28), body=(150, 105, 60), light=(200, 160, 105), core=(235, 210, 165), white=(250, 240, 220))
WIND = dict(rim=(60, 120, 110), body=(140, 210, 190), light=(195, 240, 225), core=(235, 252, 245), white=(255, 255, 255))
NATURE = dict(rim=(30, 90, 30), body=(80, 170, 60), light=(150, 220, 100), core=(215, 245, 170), white=(245, 255, 230))
POISON = dict(rim=(60, 90, 20), body=(140, 200, 40), light=(195, 235, 90), core=(230, 255, 170), white=(250, 255, 225))
HOLY = dict(rim=(170, 120, 40), body=(255, 210, 90), light=(255, 238, 160), core=(255, 250, 225), white=(255, 255, 255))
SHADOW = dict(rim=(30, 15, 50), body=(90, 50, 140), light=(150, 100, 200), core=(210, 175, 245), white=(240, 225, 255))
ARCANE = dict(rim=(70, 30, 120), body=(160, 80, 230), light=(205, 150, 255), core=(240, 215, 255), white=(255, 250, 255))
SPIRIT = dict(rim=(38, 76, 200), body=(52, 132, 238), light=(82, 208, 252), core=(178, 242, 255), white=(238, 252, 255),   # soul fire
              dark=(26, 36, 112), deep=(38, 76, 200), blue=(52, 132, 238), cyan=(82, 208, 252), pale=(178, 242, 255),
              violet=(128, 96, 226), lilac=(190, 156, 244))                 # extra steps: the tail ramp cyan -> blue -> violet -> lilac
BLAZE = dict(rim=(209, 47, 87), body=(255, 98, 140), light=(255, 152, 58), core=(255, 215, 113), white=(255, 236, 180),   # pink fire
             crimson=(209, 47, 87), hotpink=(254, 68, 123), pink=(255, 98, 140), amber=(254, 172, 76), yellow=(255, 214, 112),
             glow1=(96, 26, 52), glow2=(160, 36, 76), glow3=(232, 60, 112))        # stepped glow, far -> near
FROST = dict(rim=(30, 109, 157), body=(59, 169, 226), light=(105, 231, 254), core=(239, 255, 255), white=(250, 255, 255),   # frost
             deep=(30, 109, 157), blue=(34, 119, 172), mid=(59, 169, 226), cyan=(105, 231, 254), ice=(239, 255, 255), ghost=(28, 74, 104),
             glow1=(18, 52, 80), glow2=(30, 90, 140), glow3=(60, 170, 227))        # stepped glow, far -> near
BLOOD = dict(rim=(80, 10, 15), body=(170, 25, 35), light=(220, 70, 70), core=(250, 160, 150), white=(255, 225, 220))

PALETTES = {"sun": SUN, "fire": FIRE, "ice": ICE, "water": WATER, "lightning": LIGHTNING, "earth": EARTH, "wind": WIND,
            "nature": NATURE, "poison": POISON, "holy": HOLY, "shadow": SHADOW, "arcane": ARCANE, "blood": BLOOD, "spirit": SPIRIT, "blaze": BLAZE, "frost": FROST}


def _lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def fit(pal, like):
    """`pal` (any palette above) with every key the effect's own palette `like` has, so any effect can be drawn in any palette.
    Keys both have are taken from pal. A key only the effect has (tip, back, crimson, amber ...) is placed on pal's ramp
    rim -> body -> light -> core -> white at the same lightness rank it has in the effect's own ramp, so the order of the tones
    (which one is darkest, which one is the hot core) survives the swap."""
    ramp = sorted((pal[k] for k in ("rim", "body", "light", "core", "white") if k in pal), key=_lum)
    own = sorted(like.values(), key=_lum); lo, hi = _lum(own[0]), _lum(own[-1])
    out = dict(like)
    for k, c in like.items():
        if k in pal: out[k] = tuple(pal[k]); continue
        x = (_lum(c) - lo) / max(1e-6, hi - lo) * (len(ramp) - 1)
        i = min(len(ramp) - 2, int(x)); f = x - i
        col = tuple(round(a + (b - a) * f) for a, b in zip(ramp[i], ramp[i + 1]))
        rim = like.get("rim", own[0])
        if _lum(c) < _lum(rim) - 1:                                          # darker than the effect's rim (backing, far glow): as much darker than pal's rim
            col = tuple(round(v * _lum(c) / _lum(rim)) for v in pal.get("rim", ramp[0]))
        out[k] = col
    return out
