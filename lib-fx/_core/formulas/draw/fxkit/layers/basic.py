"""fxkit / layers / basic: the smallest possible layer kind, kept as the template every other kind follows."""
from organic import Shape, blob
from .. import kind, out_back


@kind("core")
def core(c, ph, r=26.0, squash=1.0, wob=0.12):
    """The hot heart of a hit: a wobbly blob that pops in with an overshoot, cools from the edges inward (white centre closes)
    and is eaten by noisy erosion while it shrinks. r: radius px at s = 1; squash: y / x (ground: 0.5)."""
    rng = c.rng("shape")
    x, y = c.o
    R = r * c.s * (0.55 + 0.45 * out_back(ph.grow)) * (1 - 0.45 * ph.decay)
    sh = Shape(c.cv)
    sh.poly(blob(x, y, R, sy=squash, wob=wob, freq=rng.choice((3, 4, 5)), phase=rng.uniform(0, 6.28)))
    bands = [(1.2 * c.s, c.pal["light"]), (None, c.pal["white"])] if ph.first else c.pal.bands(c.s, ph.heat, k=min(1.0, r / 26))
    sh.paint(bands, fillet=2.0, erode=R * 0.9 * ph.decay ** 1.5, noise=R * 0.35 * ph.decay, seed=rng.randrange(1 << 16),
             backing=(3.0 * c.s, c.pal["back"], 0.3 * (1 - ph.decay)))
