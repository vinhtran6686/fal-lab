"""lib-fx / melee / slash: the smear of an edged weapon (fxkit). a = where the blade starts, b = where it ends: the smear is drawn
along the bowed path between them, so any swing of any character is one --from / --to away."""
from fxkit import Effect, Layer, Life

TAGS = ["melee", "blade", "slash", "one-shot", "anchor:path"]
_slash = Effect("crescent", title="Chém lưỡi liềm", space="span", weight="medium", pal="frost", reach=210, extent=230, tags=["medium"],
    desc="a crescent smear swept from a to b: a needle tail, a fat belly on the inside of the bow, a darker inner tone and a hot "
         "leading edge, teeth cut into the inner edge, hair streaks beside it; it is eaten from the inside out into curved slivers; "
         "scraps fly off the end of the swing",
    layers=[
        Layer("slash",  role="primary",              life=Life(0.0, 0.1, 0.033, 0.3), bend=0.34, width=56),
        Layer("scraps", role="particles", at="b",    life=Life(0.066, 0.033, 0.0, 0.4), n=6, arc=(-70, 20), speed=(160, 380), size=14, gravity=120),
        Layer("streaks", role="accent", at=("path", 0.8, 0.34), life=Life(0.066, 0.033, 0.033, 0.13), n=3, arc=(-60, 10), length=90, r0=20),
    ])
EFFECTS = {
    "crescent": _slash,
    "heavy": _slash.variant("heavy", title="Chém nặng", weight="heavy", pal="blaze", reach=250, tags=["heavy"],
        desc="a great weapon: a wider, deeper bow, a second fainter smear behind it, more scraps",
        layers={"slash": {"width": 84, "bend": 0.42, "teeth": 5, "streaks": 4, "life": Life(0.0, 0.12, 0.05, 0.36)}, "scraps": {"n": 10, "size": 18, "life": Life(0.1, 0.033, 0.0, 0.5)}}),
    "thrust": _slash.variant("thrust", title="Đâm thẳng", pal="sun", reach=230, tags=["piercing", "fast"],
        desc="a straight thrust or dash: the same smear with no bow, thin and fast, a small flash where it ends",
        layers={"slash": {"bend": 0.0, "width": 34, "teeth": 2, "streaks": 4, "life": Life(0.0, 0.066, 0.033, 0.22)},
                "streaks": {"at": "b", "arc": (-40, 40), "n": 4}, "scraps": {"arc": (-50, 50)}}),
}
EFFECTS["heavy"].layers.insert(0, Layer("slash", id="echo", role="secondary", z="back", life=Life(0.033, 0.12, 0.033, 0.3), bend=0.5, width=44, teeth=0, streaks=0, tones=1))
EFFECTS["thrust"].layers.append(Layer("star", role="core", at="b", life=Life(0.05, 0.05, 0.0, 0.22), n=4, length=60, width=24, arc=(-60, 60), minor=2))
