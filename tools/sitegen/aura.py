"""The Aura colour field (the app's PaydarKit AuraPalette and AuraBackground), for the site.

The field behind a page is made from subscriptions' brand colours: biggest monthly cost first,
greys skipped, one colour per 20° of hue, at most five, each softened so text stays readable.
static/home.js runs the same steps in the browser when the visitor picks services.
"""

import colorsys

MAX_SPOTS = 5
HUE_GAP = 20.0
NEUTRAL_BELOW = 0.1
DEFAULTS = ("#16A374", "#F2B35A", "#8A6BD6")


def _hsl(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    return hue * 360, sat, light


def _hex(h: float, s: float, l: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h / 360, l, s)
    return "#{:02X}{:02X}{:02X}".format(*(round(x * 255) for x in (r, g, b)))


def soften(hex_color: str, dark: bool) -> str:
    h, s, l = _hsl(hex_color)
    l = min(max(l, 0.45), 0.58) if dark else min(max(l, 0.60), 0.72)
    return _hex(h, min(max(s, 0.45), 0.80), l)


def spots(items: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """(hex, monthly cost) pairs → (hex, weight) spots, weights summing to 1."""
    by_cost = sorted(enumerate(items), key=lambda p: (-p[1][1], p[0]))
    kept: list[tuple[str, float, float]] = []
    for _, (hex_color, cost) in by_cost:
        if len(kept) >= MAX_SPOTS:
            break
        h, s, _l = _hsl(hex_color)
        if s < NEUTRAL_BELOW or any(min(abs(k[1] - h) % 360, 360 - abs(k[1] - h) % 360) < HUE_GAP for k in kept):
            continue
        kept.append((hex_color, h, max(0.0, cost)))
    if not kept:
        return [(c, 1 / len(DEFAULTS)) for c in DEFAULTS]
    total = sum(k[2] for k in kept)
    return [(k[0], k[2] / total if total > 0 else 1 / len(kept)) for k in kept]


def field_style(items: list[tuple[str, float]]) -> str:
    """Inline custom properties for .field: --sN (light), --dN (dark) and --rN (radius, a fraction of the width)."""
    out, kept = [], spots(items)
    biggest = max(w for _, w in kept)
    for i, (hex_color, weight) in enumerate(kept, start=1):
        # The app's AuraBackground: radius = width × (0.30 + 0.18 × weight / biggest weight).
        out += [f"--s{i}:{soften(hex_color, False)}", f"--d{i}:{soften(hex_color, True)}",
                f"--r{i}:{0.30 + 0.18 * weight / biggest:.3f}"]
    return ";".join(out)
