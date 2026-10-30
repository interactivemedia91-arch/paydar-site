"""Where a renewal sits on the radar: the app's RadarLayout (PaydarKit/Logic/RadarLayout.swift).

The closer to Today (the centre of the half-disc), the sooner it charges. Bearings come from a hash
of the id and are nudged apart so logos don't overlap. Angles are degrees from the right edge
(0) over the top (90) to the left edge (180); radii are fractions of the radar's radius.
"""

import math
from collections.abc import Callable

MIN_ANGLE, MAX_ANGLE = 15.0, 165.0
NUDGE_STEP, NUDGE_TRIES = 12.0, 7
MAX_DAYS = 30


def hash01(item_id: str) -> float:
    """FNV-1a over UTF-16 code units, as the app does."""
    h = 0x811C9DC5
    raw = item_id.encode("utf-16-le")
    for i in range(0, len(raw), 2):
        h ^= raw[i] | raw[i + 1] << 8
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h / 4_294_967_296


def linear_radius(days: int, inner: float = 0.18) -> float:
    """The app's default scale (RadarLayout.radius)."""
    return inner + (days / MAX_DAYS) * (1 - inner)


def aura_radius(days: int) -> float:
    """The square-root scale the Aura radar is drawn at (7 days sits well out from the centre)."""
    return 0.2 + 0.8 * math.sqrt(min(max(days, 0), MAX_DAYS) / MAX_DAYS)


def place(items: list[tuple[str, int]], min_gap: float = 0.16, max_blips: int = 12,
          radius_for_days: Callable[[int], float] = linear_radius) -> dict[str, tuple[float, float]]:
    """(id, days) → {id: (angle, r)} for the renewals within the next 30 days, soonest first."""
    visible = sorted((i for i in items if 0 <= i[1] <= MAX_DAYS),
                     key=lambda i: (i[1], i[0].encode("utf-16-be")))[:max_blips]
    placed: dict[str, tuple[float, float]] = {}

    def xy(angle: float, r: float) -> tuple[float, float]:
        a = math.radians(angle)
        return r * math.cos(a), r * math.sin(a)

    for item_id, days in visible:
        r = radius_for_days(days)
        base = MIN_ANGLE + hash01(item_id) * (MAX_ANGLE - MIN_ANGLE)

        def clearance(angle: float) -> float:
            x, y = xy(angle, r)
            return min((math.hypot(x - px, y - py) for px, py in (xy(a, pr) for a, pr in placed.values())),
                       default=math.inf)

        best, best_clear = base, -1.0
        k = 0
        while k < NUDGE_TRIES * 2 + 1 and best_clear < min_gap:
            step = 0 if k == 0 else (1 if k % 2 == 1 else -1) * ((k + 1) // 2)
            angle = base + step * NUDGE_STEP
            if MIN_ANGLE <= angle <= MAX_ANGLE:
                c = clearance(angle)
                if c > best_clear:
                    best, best_clear = angle, c
            k += 1
        angle = MIN_ANGLE
        while best_clear < min_gap and angle <= MAX_ANGLE:
            c = clearance(angle)
            if c > best_clear:
                best, best_clear = angle, c
            angle += 3
        placed[item_id] = (best, r)
    return placed
