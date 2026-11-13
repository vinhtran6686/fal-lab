"""fxkit / timing: the life of one layer. Every layer is born, grows, holds and decays on its own clock; an effect ends when its
last layer has decayed, so an effect that pops off or never ends cannot be written.

Seconds are measured from the HIT (t = 0: the frame the blow lands). A negative start is anticipation (a gather before the hit).
"""
import math
from dataclasses import dataclass


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def smooth(a, b, x): x = clamp((x - a) / (b - a)); return x * x * (3 - 2 * x)
def out_cubic(x): return 1 - (1 - clamp(x)) ** 3
def out_quint(x): return 1 - (1 - clamp(x)) ** 5
def out_expo(x): return 1.0 if x >= 1 else 1 - 2 ** (-10 * clamp(x))
def in_quad(x): return clamp(x) ** 2
def in_cubic(x): return clamp(x) ** 3
def out_back(x, k=1.70158): x = clamp(x) - 1; return 1 + (k + 1) * x ** 3 + k * x ** 2


@dataclass(frozen=True)
class Phase:
    sec: float      # seconds since this layer was born
    age: float      # 0 born .. 1 dead
    grow: float     # 0 .. 1 over the attack (linear: the layer applies its own easing, usually out_expo / out_back)
    decay: float    # 0 .. 1 over the release (0 while growing and holding). At 1 the layer must have drawn NOTHING.
    heat: float     # 1 fresh and white-hot .. 0 cold: drives the colour down the ramp
    first: bool     # the first drawing of this layer (use the overexposed tones here)


@dataclass(frozen=True)
class Life:
    start: float = 0.0       # s after the hit; negative = before it
    attack: float = 0.066    # s to reach full size (2 frames at 30 fps: fast in)
    hold: float = 0.0        # s at full
    release: float = 0.2     # s to decay to nothing (slow out); never 0
    step: int = 1            # 1 = a new drawing every frame; 2 = "on twos" (smoke, embers: a hand-drawn feel)
    cool: tuple = (0.05, 0.75)   # share of the life over which heat falls from 1 to 0

    @property
    def length(self): return self.attack + self.hold + self.release

    @property
    def end(self): return self.start + self.length

    def at(self, t, fps=30.0):
        """Phase at effect time t (s from the hit), or None when the layer is not alive."""
        if self.step > 1:
            q = self.step / fps
            t = self.start + math.floor((t - self.start) / q + 1e-6) * q if t >= self.start else t
        u = t - self.start
        if u < -1e-9 or u >= self.length - 1e-9: return None
        u = max(0.0, u)
        age = u / self.length
        return Phase(sec=u, age=age, grow=clamp(u / self.attack) if self.attack > 0 else 1.0,
                     decay=clamp((u - self.attack - self.hold) / self.release), heat=1 - smooth(self.cool[0], self.cool[1], age),
                     first=u < self.step / fps - 1e-9)
