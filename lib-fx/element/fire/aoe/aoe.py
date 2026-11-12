"""lib-fx / element / fire / aoe: fire that erupts from the ground under a target (fxkit; rules in lib-fx/_core/formulas/rules/vfx/explosion)."""
from fxkit import Effect, Layer, Life

TAGS = ["element", "fire", "aoe", "one-shot", "anchor:ground"]
EFFECTS = {
    "eruption": Effect("eruption", title="Lửa phun", space="ground", weight="light", pal="fire", extent=260,
                       desc="flame tongues erupt from the ground, flicker for a moment, then are eaten in place into rising pieces; the hot pool at the foot goes last",
                       layers=[Layer("flames", role="primary", life=Life(0.0, 0.1, 0.1, 0.55))]),
}
