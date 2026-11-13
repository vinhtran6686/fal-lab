"""lib-fx / impact / quake: something heavy hits the ground (fxkit). a = the impact point on the floor; the effect stays level."""
from fxkit import Effect, Layer, Life

TAGS = ["impact", "ground", "one-shot", "anchor:ground"]
_slam = Effect("slam", title="Nện đất", space="ground", weight="heavy", pal="sun", extent=300, tags=["heavy", "dust"],
    desc="a weapon or a fist slams the floor: a pointed flash stands up from the impact, a flat shock ring races out on the ground, "
         "a dark dust bank behind and a light one in front roll out to both sides with unequal lobes and pointed tails, scraps are "
         "thrown up and fall back; the dust opens from the middle and is eaten in place last",
    layers=[
        Layer("dust",   id="dust_back", role="smoke", z="back", life=Life(0.033, 0.12, 0.1, 0.6), tone="dark", reach=170, height=84, n=6),
        Layer("ring",   role="secondary", z="back", life=Life(0.033, 0.12, 0.0, 0.25), r=(30, 165), width=17, squash=0.3),
        Layer("star",   role="primary",             life=Life(0.0, 0.066, 0.033, 0.3), n=5, arc=(25, 155), length=120, width=44, minor=3),
        Layer("scraps", role="particles",           life=Life(0.033, 0.033, 0.0, 0.55), n=9, arc=(35, 145), speed=(240, 470), gravity=900),
        Layer("dust",   role="smoke",               life=Life(0.066, 0.1, 0.1, 0.6), tone="light", reach=150, height=60, n=8),
    ])
EFFECTS = {
    "slam": _slam,
    "stomp": _slam.variant("stomp", title="Dậm chân", weight="medium", tags=["medium", "dust"],
        desc="a landing or a stomp: a small flash, low dust rolling out, no ring",
        layers={"ring": False, "dust_back": False, "star": {"n": 4, "length": 64, "width": 28, "life": Life(0.0, 0.05, 0.0, 0.22)},
                "scraps": {"n": 5, "speed": (170, 320), "size": 12}, "dust": {"reach": 110, "height": 44, "n": 6, "life": Life(0.033, 0.1, 0.07, 0.5)}}),
    "shockwave": _slam.variant("shockwave", title="Sóng chấn động", pal="arcane", weight="medium", tags=["heavy", "ring", "magic"],
        desc="a magic ground wave: two flat rings one after the other, a tall flash, no dust",
        layers={"dust": False, "dust_back": False, "ring": {"r": (30, 190), "width": 20},
                "star": {"n": 4, "arc": (50, 130), "length": 150, "width": 34}, "scraps": {"gravity": 200, "arc": (10, 170)}}),
}
EFFECTS["shockwave"].layers.insert(1, Layer("ring", id="ring2", role="secondary", z="back", life=Life(0.13, 0.12, 0.0, 0.25), r=(24, 130), width=12, squash=0.3))
