# color-theory-buddy

An interactive color theory assistant for painters and digital artists.

Comes in three forms:

- **`web/index.html`** — pick a color, get the color-wheel-based color to
  shade with instead of black and highlight with instead of white. Works in
  any browser, so you can keep it open next to Procreate, Photoshop, or
  whatever you paint in.
- **`gui_app.py`** — a native macOS desktop app (CustomTkinter). Just run it;
  it sets itself up.
- **`color_theory_buddy.py`** — a terminal app, no installs needed.

The desktop and terminal apps show a fuller atelier-style value scale
(highlight through occlusion shadow) plus classic wheel schemes; the web app
is intentionally narrower — just the one question painters actually ask:
*what do I mix in instead of black/white?*

## Desktop app

```
python3 gui_app.py
```

The first time you run it, it creates a throwaway virtual environment
(`.venv-gui`, next to the script) and installs [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
into it automatically, then relaunches itself there — you never have to run
`pip install` by hand. Later runs reuse that environment and start instantly.

This needs Python's built-in Tk support. The python.org macOS installer and
Homebrew's `python-tk` both include it; if you see `ModuleNotFoundError: No
module named 'tkinter'`, run `brew install python-tk` (matching your Python
version) or reinstall Python from [python.org](https://www.python.org/downloads/).

Type a color, click a preset chip, or use the native color picker (the small
square next to the text field) to see the value scale and wheel schemes
update live. Click any swatch to copy its hex code. The Appearance menu
switches between System/Light/Dark, and Light Source switches between
Warm/Neutral/Cool.

## Web app

Double-click `web/index.html` to open it directly in your browser — that's
it, nothing to install or run. On an iPad, open it in Safari and split-view
it next to Procreate. (If your browser blocks local-file scripts, serve it
instead: `python3 -m http.server --directory web`, then visit
`http://localhost:8000`.)

Type a color into the box (or click a preset, or use the color picker). You
get two suggestions, both live-updating:

- **Shade with** — instead of just going to black, mix in the color roughly
  opposite your base on the wheel (e.g. a warm skin tone points you to
  azure/blue-violet). Black only adds gray and flattens color; the
  near-complement darkens it while keeping it looking like less light, not
  less color.
- **Highlight with** — instead of white, mix in a color near your base's hue
  tinted toward the light source, so the highlight reads as brighter light
  instead of a bleached-out hole.

Below that, a color-wheel diagram plots your color (**B**) and both
suggestions (**S**, **H**) so you can see the relationship, not just take it
on faith. The light-source toggle (Warm/Neutral/Cool) nudges which side of
the wheel the shadow/highlight suggestions lean toward. Click any swatch,
marker, or legend entry to copy its hex code.

## Terminal app

### Running it on macOS

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

### Using it

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

#### Example

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
