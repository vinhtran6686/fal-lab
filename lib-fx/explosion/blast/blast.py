"""lib-fx / explosion / blast: an explosion at a point (fxkit). a = the centre."""
from fxkit import Effect, Layer, Life

TAGS = ["explosion", "one-shot", "anchor:centre"]
_blast = Effect("blast", title="Nổ", space="point", weight="heavy", pal="fire", extent=300, tags=["heavy", "fire"],
    desc="a pointed flash, flames thrown up and out over a dark smoke mass, a ring racing out, scraps in every direction, embers after",
    layers=[
        Layer("smoke",  role="smoke", z="back", life=Life(0.066, 0.13, 0.13, 0.65), height=170, width=190, n=5),
        Layer("ring",   role="secondary", z="back", life=Life(0.033, 0.12, 0.0, 0.25), r=(30, 170), width=16),
        Layer("flames", role="primary",          life=Life(0.0, 0.1, 0.13, 0.6), n=5, height=150, width=150, fan=150, minor=5, linger=2.7),
        Layer("star",   role="core",             life=Life(0.0, 0.066, 0.0, 0.25), n=6, length=140, width=46),
        Layer("star",   id="splash", role="accent", z="back", plane=("ground", 0.32), life=Life(0.0, 0.066, 0.033, 0.25), n=9, arc=(-180, 180), length=160, even=0.7, width=38, minor=3),
        Layer("scraps", role="particles",        life=Life(0.033, 0.033, 0.0, 0.55), n=14, speed=(220, 520), gravity=320),
        Layer("embers", role="particles", id="embers", life=Life(0.3, 0.05, 0.3, 0.45), n=9, area=(100, 50)),
    ])
EFFECTS = {
    "blast": _blast,
    "small": _blast.variant("small", title="Nổ nhỏ", weight="medium", tags=["medium", "fire"], desc="a small burst: a bomb, a barrel",
        layers={"ring": {"r": (20, 100), "width": 11}, "flames": {"n": 4, "height": 90, "width": 90, "minor": 3}, "smoke": {"height": 100, "width": 110, "n": 4},
                "star": {"n": 5, "length": 86, "width": 32}, "splash": {"n": 5, "length": 90, "width": 26}, "scraps": {"n": 8, "speed": (170, 380)}, "embers": False}),
}
EFFECTS["ground"] = _blast.variant("ground", title="Nổ trên đất", tags=["heavy", "fire", "ground"], desc="the blast on the floor: the ring lies flat on the ground and the splash is a flat ellipse under the flames",
    layers={"ring": {"squash": 0.3}, "scraps": {"floor": True, "r0": 40, "arc": (20, 160)}})
