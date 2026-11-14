"""lib-fx / magic / arcane / aoe: crystals of arcane energy snap out of the ground (fxkit)."""
from fxkit import Effect, Layer, Life

TAGS = ["magic", "arcane", "aoe", "one-shot", "anchor:ground"]
_spikes = Effect("crystals", title="Pha lê bùng", space="ground", weight="medium", pal="arcane", extent=300, tags=["medium"],
    desc="hard-edged crystal spikes with lit facets snap out of the ground in front of a see-through veil of wings, a flat ring on the "
         "floor; the veil is eaten into an outline of curved slivers, the spikes thin away",
    layers=[
        Layer("ring",     role="secondary", z="back", life=Life(0.0, 0.1, 0.0, 0.2), r=(30, 120), width=12, squash=0.3),
        Layer("crystals", role="primary",             life=Life(0.0, 0.1, 0.066, 0.42)),
        Layer("scraps",   role="particles",           life=Life(0.1, 0.033, 0.0, 0.6), n=7, arc=(30, 150), speed=(160, 360), gravity=60),
    ])
EFFECTS = {
    "crystals": _spikes,
    "frost": _spikes.variant("frost", title="Gai băng", pal="ice", tags=["ice"],
        desc="the same eruption as ice: more, lower spikes fanned wide, no veil",
        layers={"crystals": {"n": 7, "height": 130, "fan": 130, "width": 150, "veil": False}}),
}
