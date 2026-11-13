"""lib-fx / melee / slash: the smear of an edged weapon (fxkit). a = where the blade starts, b = where it ends: the smear is drawn
along the bowed path between them, so any swing of any character is one --from / --to away."""
from fxkit import Effect, Layer, Life

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
EFFECTS["heavy"].layers.insert(0, Layer("slash", id="echo", role="secondary", z="back", life=Life(0.033, 0.12, 0.033, 0.3), bend=0.5, width=44, streaks=0, tones=1))
EFFECTS["thrust"].layers.append(Layer("star", role="core", at="b", life=Life(0.05, 0.05, 0.0, 0.22), n=4, length=60, width=24, arc=(-60, 60), minor=2))
for _k in ("axe", "axe_heavy"):                                              # a fainter sword-like smear behind the bands, for depth
    EFFECTS[_k].layers.insert(0, Layer("slash", id="echo", role="secondary", z="back", life=Life(0.033, 0.12, 0.033, 0.3), weapon="sword", bend=0.46, width=40, strands=2, streaks=0, tones=1))
