"""fxkit / vary: seeded variation. The first rule of a good effect is that no two shapes in it are alike: every thorn, puff,
spark and gap gets its own size, direction, delay and speed, with a clear hierarchy (one hero, a few medium, many small).
Everything here is deterministic: the same seed draws the same effect on every machine (no hash(), no global random)."""
import math, random, zlib


class Rand(random.Random):
    """A random stream named by its keys: Rand(seed, "slam", "puffs", 3). Same keys, same numbers, on every run and platform."""
    def __init__(self, *keys):
        super().__init__(zlib.crc32(repr(keys).encode("utf8")))

    def around(self, v, pct):
        """v moved by up to +-pct (0.2 = 20 %)."""
        return v * (1 + self.uniform(-pct, pct))

    def sign(self):
        return 1 if self.random() < 0.5 else -1


def sizes(rng, n, heroes=1, mid=0.62, small=0.3, jitter=0.12):
    """n relative sizes (largest = 1.0) with a hierarchy: `heroes` at ~1.0, about a third at ~mid, the rest at ~small, every one
    moved by +-jitter so no two are equal. Returned in an order where big and small alternate (never three alike in a row)."""
    if n <= 0: return []
    n_mid = max(0, min(n - heroes, round((n - heroes) * 0.38)))
    base = [1.0] * min(heroes, n) + [mid] * n_mid + [small] * max(0, n - heroes - n_mid)
    vals = [max(0.08, rng.around(b, jitter)) for b in base]
    vals[0] = 1.0
    big, rest = vals[:heroes + n_mid], vals[heroes + n_mid:]
    rng.shuffle(big); rng.shuffle(rest)
    out = []
    while big or rest:                                                    # interleave: big, small, small, big ...
        if big: out.append(big.pop())
        for _ in range(2 if len(rest) > len(big) else 1):
            if rest: out.append(rest.pop())
    return out


def angles(rng, n, a0, a1, jitter=0.7, gaps=0):
    """n directions (degrees) inside a0..a1, unevenly spaced: the range is cut into n + gaps cells, `gaps` random cells stay
    empty (asymmetry), and each direction sits anywhere in the middle `jitter` share of its cell. Never an even fan."""
    if n <= 0: return []
    cells = n + gaps
    keep = sorted(rng.sample(range(cells), n))
    w = (a1 - a0) / cells
    return [a0 + (c + 0.5 + rng.uniform(-0.5, 0.5) * jitter) * w for c in keep]


def delays(rng, n, spread, lead=1):
    """n birth delays in 0..spread seconds: the first `lead` items start at 0 (the hit reads at once), the others trail."""
    return [0.0 if i < lead else rng.uniform(0.15, 1.0) * spread for i in range(n)]


def varied(vals, min_cv=0.2):
    """True when the values differ enough (coefficient of variation): used by Effect.lint and the layer tests."""
    vals = list(vals)
    if len(vals) < 3: return True
    m = sum(vals) / len(vals)
    return m > 0 and math.sqrt(sum((v - m) ** 2 for v in vals) / len(vals)) / m >= min_cv
