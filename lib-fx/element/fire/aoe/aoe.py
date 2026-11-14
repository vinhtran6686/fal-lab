"""lib-fx / element / fire / aoe: fire that erupts from the ground under a target (fxkit; rules in lib-fx/_core/formulas/rules/vfx/explosion)."""
from fxkit import Effect, Layer, Life

TAGS = ["element", "fire", "aoe", "one-shot", "anchor:ground"]
_eruption = Effect("eruption", title="Lửa phun", space="ground", weight="medium", pal="fire", extent=280, tags=["medium"],
    desc="flame tongues erupt from the ground over a dark smoke mass, flicker for a moment, then are eaten in place into rising pieces; "
         "the hot pool at the foot goes last and embers rise after it",
    layers=[
        Layer("smoke",  role="smoke", z="back", life=Life(0.066, 0.13, 0.1, 0.6), height=150, width=150),
        Layer("flames", role="primary",          life=Life(0.0, 0.1, 0.1, 0.55)),
        Layer("scraps", role="particles",        life=Life(0.066, 0.033, 0.0, 0.5), n=7, arc=(40, 140), speed=(200, 420), gravity=300),
        Layer("embers", role="particles", id="embers", life=Life(0.3, 0.05, 0.3, 0.45), n=8),
    ])
EFFECTS = {
    "eruption": _eruption,
    "pillar": _eruption.variant("pillar", title="Cột lửa", weight="medium", tags=["heavy", "vertical"],
        desc="a tall narrow column of fire: fewer, longer tongues close together, burning longer",
        layers={"flames": {"n": 3, "height": 230, "width": 70, "fan": 34, "minor": 4, "linger": 2.6, "life": Life(0.0, 0.12, 0.17, 0.6)},
                "smoke": {"height": 190, "width": 110}}),
    "wildfire": _eruption.variant("wildfire", title="Lửa lan", pal="blaze", tags=["medium", "wide"],
        desc="a low wide blaze spreading over the ground: many tongues fanned wide",
        layers={"flames": {"n": 5, "height": 110, "width": 190, "fan": 130, "minor": 5}, "smoke": {"height": 100, "width": 220, "n": 6}}),
}
