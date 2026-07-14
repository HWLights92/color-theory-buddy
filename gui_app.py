#!/usr/bin/env python3
"""
Color Theory Buddy -- desktop GUI
----------------------------------
A CustomTkinter-based desktop version of the color theory assistant: give it
a skin tone or any color and see its painter's value scale (highlight, light,
halftone, core shadow, reflected light, occlusion shadow) plus classic
color-wheel schemes, with click-to-copy swatches.

CustomTkinter isn't in the standard library, so the first run creates a
throwaway virtual environment next to this script (.venv-gui), installs it
there, and relaunches itself inside it. You never have to run `pip install`
yourself -- just:

    python3 gui_app.py

Requires Python's built-in Tk support (ships with the python.org macOS
installer and Homebrew's `python-tk`; if `import tkinter` fails, run
`brew install python-tk` or reinstall Python from python.org).
"""

import os
import subprocess
import sys
import venv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(SCRIPT_DIR, ".venv-gui")
BOOTSTRAP_MARKER = "_COLOR_THEORY_BUDDY_BOOTSTRAPPED"


def _venv_python(venv_dir):
    if sys.platform == "win32":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    return os.path.join(venv_dir, "bin", "python3")


def ensure_customtkinter():
    """Make sure CustomTkinter is importable, bootstrapping a local venv if not."""
    try:
        import customtkinter  # noqa: F401
        return
    except ImportError:
        pass

    python = _venv_python(VENV_DIR)

    if os.environ.get(BOOTSTRAP_MARKER):
        sys.exit(
            "Couldn't set up CustomTkinter automatically. Try by hand:\n"
            f"  python3 -m venv {VENV_DIR}\n"
            f"  {python} -m pip install customtkinter\n"
            f"  {python} {os.path.abspath(__file__)}"
        )

    if not os.path.exists(python):
        print("First run: setting up a local virtual environment for the GUI...")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)
        subprocess.check_call([python, "-m", "pip", "install", "--quiet", "--upgrade", "pip"])
        subprocess.check_call([python, "-m", "pip", "install", "--quiet", "customtkinter"])
        print("Done. Launching...")

    env = os.environ.copy()
    env[BOOTSTRAP_MARKER] = "1"
    os.execve(python, [python, os.path.abspath(__file__)] + sys.argv[1:], env)


ensure_customtkinter()

# --------------------------------------------------------------------------
# Everything below only runs once CustomTkinter is importable (either it was
# already installed, or we've relaunched inside .venv-gui where it just was).
# --------------------------------------------------------------------------

import colorsys
from tkinter import colorchooser

import customtkinter as ctk

import color_theory_buddy as ctb

STEEL = ("#3E6088", "#8FB4D6")
STEEL_TEXT = ("#FFFFFF", "#12202C")
MUTED = ("#6B6560", "#A39C93")
LINE = ("#C7C1B7", "#3A3836")

SERIF = ("Palatino", 20, "bold")
SERIF_SMALL = ("Palatino", 14, "bold")
MONO = ("Menlo", 12)
LABEL_FONT = ("Avenir Next", 13, "bold")
NOTE_FONT = ("Avenir Next", 11)
SECTION_FONT = ("Avenir Next", 11, "bold")

PRESET_CHIPS = [
    "fair", "light", "light-medium", "medium", "tan-skin", "deep", "dark", "ebony",
    "sienna", "umber", "ochre", "sepia",
]


def contrasting_text(rgb):
    r, g, b = rgb
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#161311" if luminance > 140 else "#F5F2EC"


class ColorTheoryBuddyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Color Theory Buddy")
        self.geometry("1100x760")
        self.minsize(880, 620)

        self.light_temp = "warm"
        self.current_rgb = ctb.hex_to_rgb("E0AC81")
        self._toast_job = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()
        self.render()

    # -- sidebar ---------------------------------------------------------

    def _section_label(self, parent, text):
        lbl = ctk.CTkLabel(parent, text=text.upper(), font=SECTION_FONT, text_color=MUTED, anchor="w")
        lbl.pack(fill="x", padx=18, pady=(18, 6))
        return lbl

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=270, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="Color Theory Buddy", font=SERIF, anchor="w", justify="left").pack(
            fill="x", padx=18, pady=(22, 4)
        )
        ctk.CTkLabel(
            sidebar,
            text="Mix a skin tone or color, see its\nvalue scale and wheel relationships.",
            font=NOTE_FONT,
            text_color=MUTED,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 6))

        self._section_label(sidebar, "Color")
        entry_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        entry_row.pack(fill="x", padx=18)
        self.color_entry = ctk.CTkEntry(entry_row, font=MONO, placeholder_text="#E0AC81")
        self.color_entry.insert(0, ctb.rgb_to_hex(self.current_rgb))
        self.color_entry.pack(side="left", fill="x", expand=True)
        self.color_entry.bind("<KeyRelease>", self._on_entry_change)

        self.picker_swatch = ctk.CTkButton(
            entry_row, text="", width=34, height=28, corner_radius=4,
            fg_color=ctb.rgb_to_hex(self.current_rgb), hover=False,
            command=self._open_color_picker,
        )
        self.picker_swatch.pack(side="left", padx=(8, 0))

        self.helper_label = ctk.CTkLabel(
            sidebar, text="Hex, rgb(224,172,129), or a name below",
            font=NOTE_FONT, text_color=MUTED, anchor="w", justify="left", wraplength=230,
        )
        self.helper_label.pack(fill="x", padx=18, pady=(6, 0))

        self._section_label(sidebar, "Presets")
        preset_grid = ctk.CTkFrame(sidebar, fg_color="transparent")
        preset_grid.pack(fill="x", padx=18)
        for i in range(3):
            preset_grid.grid_columnconfigure(i, weight=1, uniform="preset")
        for i, name in enumerate(PRESET_CHIPS):
            hexcode = ctb.NAMED_COLORS[name]
            rgb = ctb.hex_to_rgb(hexcode)
            btn = ctk.CTkButton(
                preset_grid, text=name, font=("Avenir Next", 10),
                fg_color=hexcode, hover_color=hexcode, text_color=contrasting_text(rgb),
                corner_radius=6, height=26,
                command=lambda n=name: self._set_from_text(n),
            )
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3, sticky="ew")

        self._section_label(sidebar, "Light source")
        self.light_toggle = ctk.CTkSegmentedButton(
            sidebar, values=["Warm", "Neutral", "Cool"],
            command=self._on_light_change, selected_color=STEEL[0],
        )
        self.light_toggle.set("Warm")
        self.light_toggle.pack(fill="x", padx=18)
        ctk.CTkLabel(
            sidebar,
            text="Shadows lean cool under warm light, and\nwarm under cool light.",
            font=NOTE_FONT, text_color=MUTED, justify="left", anchor="w", wraplength=230,
        ).pack(fill="x", padx=18, pady=(6, 0))

        self._section_label(sidebar, "Appearance")
        self.appearance_menu = ctk.CTkOptionMenu(
            sidebar, values=["System", "Light", "Dark"],
            command=self._on_appearance_change,
            fg_color=STEEL, button_color=STEEL,
        )
        self.appearance_menu.pack(fill="x", padx=18, pady=(0, 18))

    # -- main content ------------------------------------------------------

    def _build_main(self):
        self.main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=24, pady=24)
        self.main.grid_columnconfigure(0, weight=1)

        # base color well
        well = ctk.CTkFrame(self.main, border_width=1, border_color=LINE)
        well.pack(fill="x", pady=(0, 24))
        self.base_block = ctk.CTkFrame(well, width=90, height=90, corner_radius=6, border_width=1, border_color=LINE)
        self.base_block.pack(side="left", padx=18, pady=18)
        self.base_block.pack_propagate(False)

        info = ctk.CTkFrame(well, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=18)
        self.base_hex_label = ctk.CTkLabel(info, text="", font=MONO, anchor="w")
        self.base_hex_label.pack(fill="x", anchor="w")
        self.base_rgb_label = ctk.CTkLabel(info, text="", font=MONO, anchor="w", text_color=MUTED)
        self.base_rgb_label.pack(fill="x", anchor="w")
        self.base_hsl_label = ctk.CTkLabel(info, text="", font=MONO, anchor="w", text_color=MUTED)
        self.base_hsl_label.pack(fill="x", anchor="w")

        copy_btn = ctk.CTkButton(
            well, text="Copy hex", width=90, fg_color=STEEL, text_color=STEEL_TEXT,
            command=lambda: self.copy_hex(ctb.rgb_to_hex(self.current_rgb)),
        )
        copy_btn.pack(side="right", padx=18)

        ctk.CTkLabel(
            self.main, text="VALUE SCALE — HIGHLIGHT TO SHADOW", font=SECTION_FONT, text_color=MUTED, anchor="w",
        ).pack(fill="x", pady=(0, 10))
        self.palette_grid = ctk.CTkFrame(self.main, fg_color="transparent")
        self.palette_grid.pack(fill="x", pady=(0, 24))
        for i in range(3):
            self.palette_grid.grid_columnconfigure(i, weight=1, uniform="palette")

        ctk.CTkLabel(
            self.main, text="ON THE COLOR WHEEL", font=SECTION_FONT, text_color=MUTED, anchor="w",
        ).pack(fill="x", pady=(0, 10))
        self.wheel_grid = ctk.CTkFrame(self.main, fg_color="transparent")
        self.wheel_grid.pack(fill="x", pady=(0, 12))
        for i in range(4):
            self.wheel_grid.grid_columnconfigure(i, weight=1, uniform="wheel")

        self.toast = ctk.CTkLabel(
            self.main, text="", font=NOTE_FONT, fg_color=STEEL, text_color=STEEL_TEXT,
            corner_radius=6, width=140, height=28,
        )

        ctk.CTkLabel(
            self.main,
            text=("Value-scale labels follow atelier portrait-painting terminology using\n"
                  "simplified HSL heuristics — a strong starting point, not a replacement\n"
                  "for your reference and your own eye. Click any swatch to copy its hex."),
            font=NOTE_FONT, text_color=MUTED, justify="left", anchor="w",
        ).pack(fill="x", pady=(12, 0))

    # -- interaction -------------------------------------------------------

    def _on_entry_change(self, _event=None):
        self._set_from_text(self.color_entry.get())

    def _set_from_text(self, text):
        if text != self.color_entry.get():
            self.color_entry.delete(0, "end")
            self.color_entry.insert(0, text)
        try:
            rgb = ctb.parse_color(text)
        except ctb.ColorParseError:
            if text.strip():
                self.helper_label.configure(text=f"Keep going — couldn't read “{text.strip()}” yet")
            return
        self.current_rgb = rgb
        self.helper_label.configure(text="Hex, rgb(224,172,129), or a name below")
        self.render()

    def _open_color_picker(self):
        _, hexcode = colorchooser.askcolor(
            color=ctb.rgb_to_hex(self.current_rgb), title="Pick a color"
        )
        if hexcode:
            self._set_from_text(hexcode)

    def _on_light_change(self, value):
        self.light_temp = value.lower()
        self.render()

    def _on_appearance_change(self, value):
        ctk.set_appearance_mode(value)
        # CustomTkinter doesn't re-lay-out already-drawn rounded buttons on a
        # live theme switch, leaving a stale sliver at their edge -- rebuild
        # the swatch/dab widgets so they redraw at the correct size.
        self.render()

    def copy_hex(self, hexcode):
        self.clipboard_clear()
        self.clipboard_append(hexcode)
        self.update()
        self._show_toast(f"Copied {hexcode}")

    def _show_toast(self, text):
        self.toast.configure(text=text)
        self.toast.place(relx=1.0, rely=0.0, anchor="ne", x=-4, y=4)
        if self._toast_job:
            self.after_cancel(self._toast_job)
        self._toast_job = self.after(1100, self.toast.place_forget)

    # -- rendering -----------------------------------------------------

    def render(self):
        hexcode = ctb.rgb_to_hex(self.current_rgb)
        r, g, b = self.current_rgb
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)

        self.base_block.configure(fg_color=hexcode)
        self.picker_swatch.configure(fg_color=hexcode)
        self.base_hex_label.configure(text=f"Hex   {hexcode}")
        self.base_rgb_label.configure(text=f"RGB   {r}, {g}, {b}")
        self.base_hsl_label.configure(text=f"HSL   {h * 360:.0f}°, {s * 100:.0f}%, {l * 100:.0f}%")

        for child in self.palette_grid.winfo_children():
            child.destroy()
        palette = ctb.build_painting_palette(self.current_rgb, self.light_temp)
        for i, (label, rgb, note) in enumerate(palette):
            self._make_swatch_card(self.palette_grid, label, rgb, note).grid(
                row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6
            )

        for child in self.wheel_grid.winfo_children():
            child.destroy()
        schemes = ctb.build_schemes(self.current_rgb)
        for i, (name, colors) in enumerate(schemes.items()):
            self._make_wheel_group(self.wheel_grid, name, colors).grid(
                row=i // 4, column=i % 4, sticky="nw", padx=6, pady=6
            )

    def _make_swatch_card(self, parent, label, rgb, note):
        hexcode = ctb.rgb_to_hex(rgb)
        card = ctk.CTkFrame(parent, fg_color="transparent")

        block = ctk.CTkButton(
            card, text="", height=72, corner_radius=6, fg_color=hexcode, hover_color=hexcode,
            border_width=1, border_color=LINE, command=lambda: self.copy_hex(hexcode),
        )
        block.pack(fill="x")
        ctk.CTkLabel(
            card, text=label, font=LABEL_FONT, anchor="w", justify="left", wraplength=160,
        ).pack(fill="x", pady=(6, 0))
        ctk.CTkLabel(card, text=hexcode, font=MONO, text_color=MUTED, anchor="w").pack(fill="x")
        ctk.CTkLabel(
            card, text=note, font=NOTE_FONT, text_color=MUTED, anchor="w",
            justify="left", wraplength=160,
        ).pack(fill="x")
        return card

    def _make_wheel_group(self, parent, name, colors):
        group = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(
            group, text=name, font=LABEL_FONT, anchor="w", justify="left", wraplength=180,
        ).pack(fill="x", pady=(0, 6))
        dabs = ctk.CTkFrame(group, fg_color="transparent")
        dabs.pack(fill="x")
        for rgb in colors:
            hexcode = ctb.rgb_to_hex(rgb)
            dab = ctk.CTkFrame(dabs, fg_color="transparent")
            dab.pack(side="left", padx=(0, 12))
            dot = ctk.CTkButton(
                dab, text="", width=46, height=46, corner_radius=23,
                fg_color=hexcode, hover_color=hexcode, border_width=1, border_color=LINE,
                command=lambda h=hexcode: self.copy_hex(h),
            )
            dot.pack()
            ctk.CTkLabel(dab, text=hexcode, font=("Menlo", 10), text_color=MUTED).pack(pady=(4, 0))
        return group


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = ColorTheoryBuddyApp()
    app.mainloop()
