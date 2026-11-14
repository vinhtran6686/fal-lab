"""lib-fx / melee / slash: the smear of an edged weapon (fxkit). a = where the blade starts, b = where it ends: the smear is drawn
along the bowed path between them, so any swing of any character is one --from / --to away."""
from fxkit import Effect, Layer, Life
from fxkit.layers.slash import plane_point

TAGS = ["melee", "blade", "slash", "one-shot", "anchor:path"]
_slash = Effect("crescent", title="Chém lưỡi liềm", space="span", weight="medium", pal="frost", reach=210, extent=230, tags=["medium"],
    desc="a SWORD smear swept from a to b: a smooth crescent of three touching strands, a needle tail, a fat belly on the inside of "
         "the bow, a darker inner tone, a hot clean outer edge, two hair streaks beside it; it fades into two or three long thin "
         "strokes that run the way of the swing; scraps fly off the end",
    layers=[
        Layer("slash",  role="primary",              life=Life(0.0, 0.1, 0.033, 0.3), weapon="sword", bend=0.34, width=46),
        Layer("scraps", role="particles", at="b",    life=Life(0.066, 0.033, 0.0, 0.4), n=6, arc=(-70, 20), speed=(160, 380), size=14, gravity=120),
        Layer("streaks", role="accent", at=("path", 0.8, 0.34), life=Life(0.066, 0.033, 0.033, 0.13), n=3, arc=(-60, 10), length=90, r0=20),
    ])
EFFECTS = {
    "crescent": _slash,
    "swing": _slash.variant("swing", title="Chém theo vũ khí", tags=["tracked"],
        desc="a SWORD smear that follows a real weapon swing: use it with --track (the tip's arc is the outer edge, the blade the inner); born one "
             "frame before the hit as a thin slice on the blade of pose A, whole on the hit frame with a white edge along the blade, the tail "
             "draws in at once; the tip strand is dense and lasts, the hilt strand is faint and goes first; set the hit frame of the fx on the "
             "character's hit frame",
        layers={"slash": {"life": Life(-1 / 15, 1 / 15, 0.0, 0.27), "streaks": 0, "linger": 1.8}, "streaks": {"life": Life(0.0, 0.033, 0.033, 0.13)},
                "scraps": {"floor": True, "life": Life(0.033, 0.033, 0.0, 0.3)}}),
    "heavy": _slash.variant("heavy", title="Chém nặng", weight="heavy", pal="blaze", reach=250, tags=["heavy"],
        desc="a great SWORD (a big blade): a wider, deeper bow, a second fainter smear behind it, more scraps",
        layers={"slash": {"width": 70, "bend": 0.42, "streaks": 2, "life": Life(0.0, 0.12, 0.05, 0.36)}, "scraps": {"n": 10, "size": 18, "life": Life(0.1, 0.033, 0.0, 0.5)}}),
    "thrust": _slash.variant("thrust", title="Đâm thẳng", pal="sun", reach=230, tags=["piercing", "fast"],
        desc="a straight SWORD thrust or dash: the same smear with no bow, thin and fast, a small flash where it ends",
        layers={"slash": {"bend": 0.0, "width": 34, "life": Life(0.0, 0.066, 0.033, 0.22)},
                "streaks": {"at": "b", "arc": (-40, 40), "n": 4}, "scraps": {"arc": (-50, 50)}}),
    "axe": _slash.variant("axe", title="Chém rìu", weight="heavy", pal="sun", reach=210, tags=["heavy", "axe"],
        desc="an AXE swing: a short, thick smear of 4-6 parallel bands apart by narrow gaps, a blunt head; it fades band by band "
             "from the tail, the thin ones first, into parallel strokes",
        layers={"slash": {"weapon": "axe", "width": 80, "bend": 0.3, "life": Life(0.0, 0.1, 0.05, 0.33)}, "scraps": {"n": 8, "size": 16}}),
    "axe_heavy": _slash.variant("axe_heavy", title="Chém rìu lớn", weight="heavy", pal="blaze", reach=250, tags=["heavy", "axe"],
        desc="a great AXE: a wider, longer-lived smear of six bands, more scraps",
        layers={"slash": {"weapon": "axe", "width": 104, "strands": 6, "bend": 0.38, "life": Life(0.0, 0.12, 0.06, 0.38)},
                "scraps": {"n": 12, "size": 20, "life": Life(0.1, 0.033, 0.0, 0.5)}}),
}


def _plane_effect(name, title, desc, sw, tags, linger, sparks=((-10, 60), (0, 50)), release=0.36):
    """A smear of a swing in a PLANE seen from the game's camera (kind slash, parameter swing): a = the shoulder, b = one `reach` ahead of it,
    the tip runs on a circle of radius `reach` round a; the far half goes behind the character, the near half in front. The sparks start at
    the tip's last position (worked out from the same plane, so they follow the plane if it is changed)."""
    (x, y), _ = plane_point(sw, sw["u1"], 120.0)
    end = ("a", round(x, 1), round(-y, 1))
    return _slash.variant(name, title=title, space="aim", reach=120, extent=260, tags=["planar"] + tags, desc=desc,
        layers={"slash": {"life": Life(-1 / 15, 1 / 15, 0.0, release), "streaks": 0, "linger": linger, "swing": sw},
                "scraps": {"at": end, "floor": True, "arc": sparks[0], "life": Life(0.033, 0.033, 0.0, 0.33)},
                "streaks": {"at": end, "arc": sparks[1], "life": Life(0.0, 0.033, 0.033, 0.13)}})


EFFECTS["sweep"] = _plane_effect("sweep", "Chém ngang", "a SWORD swung level with the ground (a horizontal sweep) seen from the game's camera: a very flat ellipse, nearly a line; the "
    "far half passes BEHIND the character, cool and thin, the near half in FRONT, bright and thick; use it with the shoulder as --from",
    dict(k=0.3, roll=0.0, u0=175, u1=460, blade=0.75, ease=1.3, w_near=12), ["horizontal"], 3.4, sparks=((150, 215), (160, 200)), release=0.33)
EFFECTS["diag_down"] = _plane_effect("diag_down", "Chém xéo xuống", "a SWORD slash on a slanted plane, from high behind the shoulder to low in front, seen from the "
    "game's camera: a half-flattened ellipse turned 35 degrees; use it with the shoulder as --from",
    dict(k=0.6, roll=35.0, u0=205, u1=400, blade=0.8, ease=1.3), ["diagonal"], 2.4)
EFFECTS["diag_up"] = _plane_effect("diag_up", "Chém xéo lên", "a SWORD slash on a slanted plane, from low behind the hip to high in front, seen from the game's "
    "camera: a half-flattened ellipse turned the other way; use it with the shoulder as --from",
    dict(k=0.6, roll=-35.0, u0=160, u1=-35, blade=0.8, ease=1.3), ["diagonal"], 2.0)
EFFECTS["heavy"].layers.insert(0, Layer("slash", id="echo", role="secondary", z="back", life=Life(0.033, 0.12, 0.033, 0.3), bend=0.5, width=44, streaks=0, tones=1))
EFFECTS["thrust"].layers.append(Layer("star", role="core", at="b", life=Life(0.05, 0.05, 0.0, 0.22), n=4, length=60, width=24, arc=(-60, 60), minor=2))
for _k in ("axe", "axe_heavy"):                                              # a fainter sword-like smear behind the bands, for depth
    EFFECTS[_k].layers.insert(0, Layer("slash", id="echo", role="secondary", z="back", life=Life(0.033, 0.12, 0.033, 0.3), weapon="sword", bend=0.46, width=40, strands=2, streaks=0, tones=1))
