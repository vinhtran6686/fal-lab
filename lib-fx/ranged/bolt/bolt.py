"""lib-fx / ranged / bolt: a projectile flies from a to b and hits there (fxkit). a = the muzzle / the hand, b = the target.
The flight takes 0.3 s whatever the distance (use --speed to change it); the hit frame is the frame it reaches b."""
from fxkit import Effect, Layer, Life

TAGS = ["ranged", "projectile", "one-shot", "anchor:caster", "target:b"]
_bolt = Effect("bolt", title="Đạn năng lượng", space="travel", weight="medium", pal="lightning", reach=260, extent=200, tags=["medium", "energy"],
    desc="a small flash where it is fired, a teardrop head with a living trail flies to the target, then a pointed impact with a ring "
         "and scraps thrown on along the flight",
    layers=[
        Layer("star",   id="muzzle", role="accent", at="a", life=Life(-0.3, 0.033, 0.0, 0.13), n=3, length=46, width=20, arc=(-50, 50), minor=2),
        Layer("bolt",   role="primary",             life=Life(-0.3, 0.3, 0.0, 0.1)),
        Layer("ring",   role="secondary", at="b", z="back", life=Life(0.033, 0.1, 0.0, 0.2), r=(18, 84), width=10),
        Layer("star",   role="core", at="b",        life=Life(0.0, 0.066, 0.0, 0.28), n=5, length=92, width=36),
        Layer("scraps", role="particles", at="b",   life=Life(0.033, 0.033, 0.0, 0.45), n=8, arc=(-80, 80), speed=(170, 400)),
    ])
EFFECTS = {
    "bolt": _bolt,
    "fireball": _bolt.variant("fireball", title="Cầu lửa", weight="heavy", pal="fire", tags=["heavy", "fire"],
        desc="a thrown fireball on a bowed path: a bigger head, then flames erupt at the target over dark smoke and embers rise",
        layers={"bolt": {"bend": 0.16, "r": 19, "tail": 150}, "ring": False,
                "star": {"n": 4, "length": 70, "width": 34, "life": Life(0.0, 0.05, 0.0, 0.2)}, "scraps": {"n": 10, "gravity": 420}}),
    "frost": _bolt.variant("frost", title="Mũi băng", pal="ice", tags=["ice", "piercing"],
        desc="an ice shard: a slim fast head, crystals snap out of the target",
        layers={"bolt": {"r": 10, "tail": 150, "width": 0.8}, "star": {"n": 3, "length": 60, "width": 24, "life": Life(0.0, 0.05, 0.0, 0.2)}}),
}
EFFECTS["fireball"].layers[3:3] = [Layer("smoke", role="smoke", at="b", z="back", life=Life(0.033, 0.13, 0.1, 0.55), height=110, width=120),
                                   Layer("flames", role="primary", at="b", life=Life(0.0, 0.1, 0.066, 0.45), height=120, width=90)]
EFFECTS["fireball"].layers.append(Layer("embers", role="particles", at="b", life=Life(0.15, 0.05, 0.3, 0.4)))
EFFECTS["frost"].layers.insert(3, Layer("crystals", role="primary", at="b", life=Life(0.0, 0.1, 0.033, 0.3), n=4, height=110, width=80, fan=110, veil=False))
