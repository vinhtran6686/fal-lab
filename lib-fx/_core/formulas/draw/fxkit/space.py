"""fxkit / space: where an effect is. Every effect is drawn between two points chosen by the caller:
  a = where it starts (the caster's hand, the muzzle, the start of a swing, the impact point of a burst)
  b = where it ends or points to (the target, the end of the swing). A burst only uses b for its direction.
Layers never use canvas coordinates: they ask the Space. Moving a and b moves, turns and stretches the whole effect.

Two frames:
  axis frame  x along a -> b, y to the effect's upper side, in px at s = 1      -> Space.pt(x, y), Space.ang(deg)
  world       the screen: gravity pulls +y (down), smoke rises -y, the floor is level -> plain numbers, Space.s for size
"""
import math


class Space:
    def __init__(self, a, b=None, s=1.0, hand=None, floor=None):
        self.a = (float(a[0]), float(a[1]))
        self.b = (float(b[0]), float(b[1])) if b is not None else (self.a[0] + 100.0 * s, self.a[1])
        self.s = float(s)
        dx, dy = self.b[0] - self.a[0], self.b[1] - self.a[1]
        self.len = math.hypot(dx, dy) or 1e-6                             # px between a and b
        self.ux, self.uy = dx / self.len, dy / self.len                   # unit vector a -> b
        # the upper side: for an effect aimed right it is the screen's up; aimed left it is mirrored (still up), so an
        # asymmetric effect keeps its heavy side up whichever way it faces. hand = -1 swaps it.
        self.hand = hand if hand is not None else (1 if self.ux >= -1e-9 else -1)
        self.nx, self.ny = self.uy * self.hand, -self.ux * self.hand      # unit normal to the upper side
        self.floor = floor if floor is not None else self.a[1]            # y of the ground line (ground effects)

    def pt(self, x, y=0.0, at="a"):
        """Canvas point of axis-frame (x, y) px (scaled by s), measured from a or b."""
        ox, oy = self.at(at)
        return (ox + (self.ux * x + self.nx * y) * self.s, oy + (self.uy * x + self.ny * y) * self.s)

    def ang(self, deg):
        """Screen angle (radians) of an axis-frame direction: 0 = along a -> b, 90 = to the upper side, 180 = back."""
        r = math.radians(deg)
        return math.atan2(self.uy * math.cos(r) + self.ny * math.sin(r), self.ux * math.cos(r) + self.nx * math.sin(r))

    def path(self, f, bend=0.0):
        """Point and screen angle of travel at fraction f (0 = a, 1 = b) of the path a -> b. bend bows the path to the upper
        side by bend * len at its middle (a thrown arc, the bow of a slash); negative bows it down."""
        cx = (self.a[0] + self.b[0]) / 2 + self.nx * bend * self.len * 2
        cy = (self.a[1] + self.b[1]) / 2 + self.ny * bend * self.len * 2
        x = (1 - f) ** 2 * self.a[0] + 2 * (1 - f) * f * cx + f * f * self.b[0]
        y = (1 - f) ** 2 * self.a[1] + 2 * (1 - f) * f * cy + f * f * self.b[1]
        tx = 2 * (1 - f) * (cx - self.a[0]) + 2 * f * (self.b[0] - cx)
        ty = 2 * (1 - f) * (cy - self.a[1]) + 2 * f * (self.b[1] - cy)
        return (x, y), math.atan2(ty, tx)

    def at(self, where="a"):
        """A named point: "a", "b", "mid", ("a", dx, dy) / ("b", dx, dy) in the axis frame, ("path", f[, bend])."""
        if where == "a": return self.a
        if where == "b": return self.b
        if where == "mid": return ((self.a[0] + self.b[0]) / 2, (self.a[1] + self.b[1]) / 2)
        if where[0] == "path": return self.path(where[1], where[2] if len(where) > 2 else 0.0)[0]
        return self.pt(where[1], where[2], where[0])
