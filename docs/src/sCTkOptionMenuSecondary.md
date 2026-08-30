## sCTkOptionMenuSecondary

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkOptionMenuSecondary` is a themeable, composite bordered dropdown option-selection menu. Unlike every other widget in this library, it is **not** a direct subclass of the widget it wraps — it's a `customtkinter.CTkFrame` containing a plain, native `customtkinter.CTkOptionMenu` inside it, giving the dropdown a themed border the native widget has no way to draw on its own. See also `sCTkOptionMenuPrimary`, a simpler direct-subclass variant.

Dark Mode: ![sCTkOptionMenuSecondary in dark mode](images/sCTkOptionMenuSecondary_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode:	![sCTkOptionMenuSecondary in light mode](images/sCTkOptionMenuSecondary_Light.png)

Because configuring the outer widget affects the frame (border, background, size) while the dropdown itself is a separate inner object, most of this widget's behavior comes from keeping those two pieces in sync — see [Theming](#theming-sctkthemesjson) for how that split works.

---

### Constructor

```python
sCTkOptionMenuSecondary(master=None, width=160, height=28, **kw)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `width` | `int` | `160` | Frame width, used unless overridden by a kwarg or the theme. |
| `height` | `int` | `28` | Frame height, used unless overridden by a kwarg or the theme. |
| `**kw` | — | — | `values` (list[str]), `command` (callable), and `variable` (tkinter.StringVar) are forwarded to the inner dropdown. Theme keys that belong to the inner menu rather than the outer frame — `font`, `dropdown_font`, `text_color`, `dropdown_fg_color`, `dropdown_text_color`, `dropdown_hover_color`, `button_hover_color` — are automatically routed there; everything else applies to the outer frame. See [Theming](#theming-sctkthemesjson). |

```python
band_menu = sCTkOptionMenuSecondary(
    master=control_panel,
    values=["80m", "40m", "20m", "10m"],
    command=on_band_changed,
)
band_menu.pack(fill="x", padx=40, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(mode=None)` | `str` | Gets or sets the widget's enabled/disabled state. Only `"disabled"` (case-insensitive) disables it. Passes `state="disabled"` to the **inner dropdown**, not the outer frame (which has nothing interactive to lock), consistent with the other widgets in this library confirmed to correctly block interaction this way. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `get()` | `str` | Delegates to the inner dropdown's `get()`. |
| `set(value)` | `None` | Delegates to the inner dropdown's `set()`. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard configuration for the **outer frame**, plus: `values`/`command`/`variable` are routed to the **inner dropdown**, not the frame; `state=...` routes through `state()`; calling `configure("propname")` with a single property name returns a Tkinter-style query tuple for `state`, `fg_color`, `border_color`, `text_color`, `width`, and `height`. Queries for any other property name fall through to the native `CTkFrame.configure`. |
| `update_list(new_values, default_index=0)` | `None` | Replaces the inner dropdown's options and resets the visible selection. Empty list falls back to a blank option; out-of-range `default_index` falls back to `0`. |

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block is split between the outer frame and the inner dropdown (see the constructor table above for which keys go where), then applied when each is built.
- **Re-applied on every `state()` change** — the outer frame's `border_color`, `fg_color`, `border_width`, and `corner_radius` are recomputed from the theme's normal values or `disabled_map`; the inner dropdown's `fg_color`, `button_color`, and `text_color` are recomputed the same way. `font`, `dropdown_font`, `dropdown_fg_color`, `dropdown_text_color`, `dropdown_hover_color`, and `button_hover_color` are **not** re-applied on state changes — they're static properties of the inner dropdown, set once and left alone.

```json
{
    "sCTkOptionMenuSecondary": {
        "border_width": 1.25,
        "corner_radius": 6,
        "border_color": ["#64748B", "#94A3B8"],
        "fg_color": ["#F3F4F6", "#0B0F19"],
        "font": ["Arial", 13, "normal"],
        "dropdown_font": ["Arial", 13, "normal"],
        "text_color": ["#1F2937", "#F9FAFB"],
        "button_hover_color": ["#94A3B8", "#374151"],
        "dropdown_fg_color": ["#FFFFFF", "#1F2937"],
        "dropdown_text_color": ["#1F2937", "#F9FAFB"],
        "dropdown_hover_color": ["#E5E7EB", "#374151"],
        "disabled_map": {
            "text_color": ["#94A3B8", "#64748B"],
            "border_color": ["#CBD5E1", "#374151"],
            "fg_color": ["#E5E7EB", "#0B0F19"]
        }
    }
}
```

`fg_color` and `text_color` are required to be present in whichever map is active — if either is missing, the widget raises immediately rather than substituting a hardcoded color, per this project's design of failing hard on incomplete theme data (see `sCTkLabelPrimary`/`Secondary`/`Tertiary` for the precedent). An earlier version of this widget used hardcoded hex fallbacks for both, and separately had a real bug where the theme's actual `button_hover_color` was computed correctly and then immediately overwritten with `fg_color` — both are fixed as of this project's audit.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family, though not separately re-confirmed for this specific widget.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkOptionMenuSecondary, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x250")
    root.title("OptionMenuSecondary Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    band_menu = sCTkOptionMenuSecondary(
        base, values=["80m", "40m", "20m", "10m"], command=lambda choice: print(f"Selected: {choice}")
    )
    band_menu.pack(pady=10)

    def toggle_disabled():
        target = "disabled" if band_menu.get_state() == "normal" else "normal"
        band_menu.state(target)
        disable_toggle.configure(text="Enable Menu" if target == "disabled" else "Disable Menu")

    disable_toggle = sCTkButtonPrimary(base, text="Disable Menu", command=toggle_disabled)
    disable_toggle.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- `state()` only recognizes `"disabled"` and `"normal"`/`"enabled"`/`"active"`; any other value matches neither branch, though colors are still harmlessly re-applied.
- Calling `configure("fg_color")` (or similar) returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for five specific properties, and falls through to the native widget's `configure()` for anything else.
- Because this widget wraps rather than subclasses its inner control, `configure()` on the outer widget and `configure()` on `self._menu` (the inner dropdown) are genuinely different calls affecting different objects — code that expects a single unified `configure()` surface (as every other widget in this library provides) needs to be aware of this split.

[Return to Table of Contents](#contents)
