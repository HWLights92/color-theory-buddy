# color-theory-buddy

An interactive, terminal-based color theory assistant for painters and digital
artists. Give it a skin tone or any color and it suggests a full painter's
value palette — highlight, light, halftone, core shadow, reflected light,
occlusion shadow — plus classic color-wheel schemes (complementary, analogous,
triadic, split-complementary). Color swatches print right in your terminal.

No installs, no dependencies — just Python's standard library.

## Running it on macOS

1. Open **Terminal** (Applications → Utilities → Terminal, or search
   Spotlight for "Terminal").
2. Check you have Python 3 (macOS usually ships with it, or install via
   [python.org](https://www.python.org/downloads/) or `brew install python`):
   ```
   python3 --version
   ```
3. From this project folder, run:
   ```
   python3 color_theory_buddy.py
   ```

That's it — no `pip install` needed.

## Using it

At the `>` prompt, type a color in any of these formats:

- Hex: `#E0AC81`
- RGB: `rgb(224,172,129)` or `224,172,129`
- A name: `medium`, `tan`, `sienna`, `crimson`, etc. (type `presets` to see
  all built-in shortcuts, including a handful of quick skin-tone presets)

Other commands:

- `light warm|cool|neutral` — set the assumed light source (default `warm`).
  Shadows shift cooler under warm light and vice versa.
- `presets` — list built-in color/skin-tone shortcuts.
- `help` — show command help.
- `quit` / `exit` — leave.

### Example

```
> #E0AC81

Analyzing #E0AC81  (hue 27°, saturation 61%, lightness 69%)
Assuming a warm light source (change with: light warm|cool|neutral)

Painting value scale (highlight to shadow):
  Highlight        #E9E2D6  rgb(233,226,214)   brightest point, catches the light source's color
  Light            #E4C9A9  rgb(228,201,169)   lit side of the form
  Base             #E0AC81  rgb(224,172,129)   your original color
  Halftone         #D4833F  rgb(212,131, 63)   turning point between light and shadow
  Core Shadow      #872918  rgb(135, 41, 24)   darkest edge of the shadow, cools/warms opposite the light
  Reflected Light  #B2542B  rgb(178, 84, 43)   bounce light inside the shadow shape
  Occlusion Shadow #481D14  rgb( 72, 29, 20)   darkest crevices, where forms meet

Color-wheel schemes:
  Complementary        #81B5E0
  Analogous            #E08185   #E0DB81
  Triadic              #81E0AC   #AC81E0
  Split-Complementary  #81E0DC   #8185E0
```

The value scale follows traditional atelier/portrait-painting terminology
(highlight → light → halftone → core shadow → reflected light → occlusion
shadow) using simplified HSL-based heuristics. It's a strong starting point
for mixing paint or picking digital brush colors — always cross-check
against your reference and your own eye.
