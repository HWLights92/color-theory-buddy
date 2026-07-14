#!/usr/bin/env python3
"""
Color Theory Buddy
-------------------
An interactive, terminal-based color theory assistant for painters and
digital artists. Give it a skin tone or any color and it suggests a full
value palette (highlights, halftones, core shadow, reflected light,
occlusion shadow) plus classic color-wheel schemes (complementary,
analogous, triadic, split-complementary).

No third-party dependencies -- just the Python standard library.

Run it with:
    python3 color_theory_buddy.py
"""

import colorsys
import os
import re
import sys

# ---------------------------------------------------------------------------
# Color parsing / formatting
# ---------------------------------------------------------------------------

NAMED_COLORS = {
    # basics
    "black": "#000000", "white": "#FFFFFF", "gray": "#808080", "grey": "#808080",
    "red": "#FF0000", "orange": "#FFA500", "yellow": "#FFFF00", "green": "#008000",
    "blue": "#0000FF", "purple": "#800080", "pink": "#FFC0CB", "brown": "#8B4513",
    "cyan": "#00FFFF", "teal": "#008080", "magenta": "#FF00FF", "gold": "#FFD700",
    "navy": "#000080", "olive": "#808000", "maroon": "#800000", "indigo": "#4B0082",
    "violet": "#EE82EE", "turquoise": "#40E0D0", "coral": "#FF7F50", "salmon": "#FA8072",
    "khaki": "#F0E68C", "lavender": "#E6E6FA", "crimson": "#DC143C", "scarlet": "#FF2400",
    "beige": "#F5F5DC", "ivory": "#FFFFF0", "tan": "#D2B48C", "sienna": "#A0522D",
    "umber": "#635147", "sepia": "#704214", "ochre": "#CC7722",

    # skin-tone presets (rough guide, quick to type -- always tweak with a real hex)
    "fair": "#F6DCC8", "light": "#EFC8A2", "light-medium": "#E0AC81",
    "medium": "#C68863", "tan-skin": "#A9724F", "deep": "#7A4A32",
    "dark": "#4A2B1F", "ebony": "#2E1A12",
}

HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$")


class ColorParseError(ValueError):
    pass


def parse_color(text):
    """Parse hex, rgb(...), 'r,g,b', or a known color name into (r, g, b)."""
    text = text.strip()
    if not text:
        raise ColorParseError("empty input")

    lowered = text.lower()
    if lowered in NAMED_COLORS:
        return hex_to_rgb(NAMED_COLORS[lowered])

    m = HEX_RE.match(text)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return hex_to_rgb(h)

    rgb_match = re.match(r"^rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$", lowered)
    if rgb_match:
        r, g, b = (int(x) for x in rgb_match.groups())
        return clamp_rgb((r, g, b))

    parts = re.split(r"[,\s]+", text)
    if len(parts) == 3 and all(p.lstrip("-").isdigit() for p in parts):
        r, g, b = (int(p) for p in parts)
        return clamp_rgb((r, g, b))

    raise ColorParseError(
        f"couldn't understand '{text}'. Try a hex code (#E0AC81), "
        f"rgb(224,172,129), or a name like 'medium' or 'tan'."
    )


def clamp_rgb(rgb):
    return tuple(max(0, min(255, int(round(c)))) for c in rgb)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    r, g, b = clamp_rgb(rgb)
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def clamp01(x):
    return max(0.0, min(1.0, x))


def adjust(rgb, hue_shift_deg=0.0, light_frac=0.0, sat_mult=1.0):
    """Return a new RGB shifted in hue/lightness/saturation (HSL space).

    light_frac moves lightness a fraction of the way toward white (if
    positive) or toward black (if negative), rather than by a flat amount.
    That way an already-light base color's "highlight" doesn't blow out to
    pure white, and an already-dark base color's "shadow" doesn't crush to
    pure black.
    """
    r, g, b = (c / 255.0 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + hue_shift_deg / 360.0) % 1.0
    if light_frac >= 0:
        l = l + (1.0 - l) * light_frac
    else:
        l = l + l * light_frac
    l = clamp01(l)
    s = clamp01(s * sat_mult)
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return clamp_rgb((r2 * 255, g2 * 255, b2 * 255))


# ---------------------------------------------------------------------------
# Terminal color output
# ---------------------------------------------------------------------------

def supports_color():
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


USE_COLOR = supports_color()


def swatch(rgb, width=4):
    """A block of terminal color, or blank padding if color isn't supported."""
    if not USE_COLOR:
        return ""
    r, g, b = rgb
    block = "\x1b[48;2;{};{};{}m{}\x1b[0m".format(r, g, b, " " * width)
    return block


def row(label, rgb, note=""):
    hexcode = rgb_to_hex(rgb)
    r, g, b = rgb
    label_col = f"{label:<16}"
    rgb_col = f"rgb({r:>3},{g:>3},{b:>3})"
    line = f"  {label_col} {swatch(rgb)}  {hexcode}  {rgb_col}"
    if note:
        line += f"   {note}"
    return line


# ---------------------------------------------------------------------------
# Painting palette (light/shadow value scale)
# ---------------------------------------------------------------------------

# Each entry: (label, hue_shift_degrees, light_frac, sat_mult, note)
# hue_shift is expressed for a *warm* light source; it is mirrored (negated)
# automatically for a *cool* light source, and zeroed out for 'neutral'.
# light_frac moves lightness a fraction of the way toward white (+) or
# black (-) rather than by a flat amount -- see adjust().
PALETTE_STEPS = [
    ("Highlight",        10, 0.60, 0.50, "brightest point, catches the light source's color"),
    ("Light",             5, 0.28, 0.85, "lit side of the form"),
    ("Base",              0, 0.00, 1.00, "your original color"),
    ("Halftone",          0, -0.22, 1.05, "turning point between light and shadow"),
    ("Core Shadow",     -18, -0.55, 1.15, "darkest edge of the shadow, cools/warms opposite the light"),
    ("Reflected Light",   -6, -0.35, 0.95, "bounce light inside the shadow shape"),
    ("Occlusion Shadow", -22, -0.75, 0.75, "darkest crevices, where forms meet"),
]

LIGHT_TEMPS = {"warm": 1, "neutral": 0, "cool": -1}


def build_painting_palette(rgb, light_temp="warm"):
    mult = LIGHT_TEMPS.get(light_temp, 1)
    palette = []
    for label, hue, light_frac, sat_mult, note in PALETTE_STEPS:
        if label == "Base":
            palette.append((label, rgb, note))
            continue
        shifted = adjust(rgb, hue_shift_deg=hue * mult, light_frac=light_frac, sat_mult=sat_mult)
        palette.append((label, shifted, note))
    return palette


# ---------------------------------------------------------------------------
# Classic color-wheel schemes
# ---------------------------------------------------------------------------

def build_schemes(rgb):
    return {
        "Complementary": [adjust(rgb, hue_shift_deg=180)],
        "Analogous": [adjust(rgb, hue_shift_deg=-30), adjust(rgb, hue_shift_deg=30)],
        "Triadic": [adjust(rgb, hue_shift_deg=120), adjust(rgb, hue_shift_deg=240)],
        "Split-Complementary": [adjust(rgb, hue_shift_deg=150), adjust(rgb, hue_shift_deg=210)],
    }


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def describe_color(rgb):
    r, g, b = (c / 255.0 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    hue_deg = h * 360
    return f"hue {hue_deg:.0f}°, saturation {s * 100:.0f}%, lightness {l * 100:.0f}%"


def print_analysis(rgb, light_temp):
    hexcode = rgb_to_hex(rgb)
    print()
    print(f"Analyzing {hexcode}  {swatch(rgb, width=6)}  ({describe_color(rgb)})")
    print(f"Assuming a {light_temp} light source (change with: light warm|cool|neutral)")

    print("\nPainting value scale (highlight to shadow):")
    for label, prgb, note in build_painting_palette(rgb, light_temp):
        print(row(label, prgb, note))

    print("\nColor-wheel schemes:")
    for name, colors in build_schemes(rgb).items():
        swatches = "  ".join(f"{swatch(c)} {rgb_to_hex(c)}" for c in colors)
        print(f"  {name:<20} {swatches}")
    print()


def print_help():
    print(
        """
Commands:
  <color>              analyze a color -- hex (#E0AC81), rgb(224,172,129),
                        '224,172,129', or a name (see 'presets')
  light warm|cool|neutral   set the assumed light source (default: warm)
  presets              list built-in skin-tone and named color shortcuts
  help                 show this message
  quit / exit          leave

Notes:
  This uses simplified HSL-based heuristics inspired by traditional atelier
  painting theory (highlight -> light -> halftone -> core shadow ->
  reflected light -> occlusion shadow). It's a strong starting point --
  always cross-check against your reference and your own eye.
"""
    )


def print_presets():
    print("\nBuilt-in shortcuts:")
    width = max(len(k) for k in NAMED_COLORS)
    for name, hexcode in NAMED_COLORS.items():
        rgb = hex_to_rgb(hexcode)
        print(f"  {name:<{width}}  {swatch(rgb)}  {hexcode}")
    print()


def main():
    print("Color Theory Buddy")
    print("Type a color to get started (or 'help' for commands).")
    if not USE_COLOR:
        print("(Color swatches disabled -- not a color-capable terminal, or NO_COLOR is set.)")

    light_temp = "warm"

    while True:
        try:
            text = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if not text:
            continue

        lowered = text.lower()
        if lowered in ("quit", "exit", "q"):
            print("Goodbye!")
            return
        if lowered in ("help", "h", "?"):
            print_help()
            continue
        if lowered == "presets":
            print_presets()
            continue
        if lowered.startswith("light "):
            choice = lowered.split(maxsplit=1)[1].strip()
            if choice in LIGHT_TEMPS:
                light_temp = choice
                print(f"Light source set to '{light_temp}'.")
            else:
                print("Usage: light warm|cool|neutral")
            continue

        try:
            rgb = parse_color(text)
        except ColorParseError as e:
            print(f"Sorry -- {e}")
            continue

        print_analysis(rgb, light_temp)


if __name__ == "__main__":
    main()
