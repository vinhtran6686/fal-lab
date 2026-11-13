"""lib-fx / impact / spark: a blow landing on a target (fxkit). a = the contact point, b = where the blow is going (its direction)."""
from fxkit import Effect, Layer, Life

TAGS = ["impact", "hit", "one-shot", "anchor:contact"]
_heavy = Effect("heavy", title="Trúng đòn nặng", space="aim", weight="heavy", pal="sun", extent=240, tags=["heavy", "melee"],
    desc="a bold pointed flash in three stacked tones bursts at the contact point and breaks into needles; a shock ring behind it, "
         "speed lines along the blow, curved scraps thrown forward that outlive everything",
    layers=[
        Layer("ring",    role="secondary", z="back", life=Life(0.033, 0.1, 0.0, 0.23), r=(24, 118), width=12),
        Layer("star",    role="primary",             life=Life(0.0, 0.066, 0.033, 0.33), n=5, length=124, width=46),
        Layer("streaks", role="accent",              life=Life(0.0, 0.033, 0.033, 0.13), n=4, arc=(-50, 50), length=140),
        Layer("scraps",  role="particles",           life=Life(0.033, 0.033, 0.0, 0.5), n=10, arc=(-75, 75), speed=(190, 460)),
    ])
EFFECTS = {
    "light": _heavy.variant("light", title="Trúng đòn nhẹ", weight="light", tags=["light", "melee"],
        desc="a quick small pointed flash and a few scraps: for fast, weak hits",
        layers={"ring": False, "streaks": False, "star": {"n": 4, "length": 74, "width": 30, "minor": 3, "life": Life(0.0, 0.05, 0.0, 0.25)},
                "scraps": {"n": 5, "speed": (150, 320), "size": 13, "life": Life(0.033, 0.033, 0.0, 0.36)}}),
    "heavy": _heavy,
    "crit": _heavy.variant("crit", title="Chí mạng", pal="holy", tags=["crit", "heavy"],
        desc="the heavy hit drawn larger and sharper: longer needles, a wider ring, more scraps in every direction",
        layers={"star": {"n": 6, "length": 160, "width": 40, "minor": 6}, "ring": {"r": (30, 150), "width": 15},
                "streaks": {"n": 6, "arc": (-180, 180), "length": 170}, "scraps": {"n": 14, "arc": (-180, 180), "speed": (220, 520)}}),
}
