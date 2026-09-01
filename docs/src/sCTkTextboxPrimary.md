## sCTkTextboxPrimary

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkTextboxPrimary` is a themeable subclass of `customtkinter.CTkTextbox` — a multi-line text area, the higher-emphasis of the library's two textbox tiers (see also `sCTkTextboxSecondary`). It adds automatic light/dark theme resolution from `sCTkThemes.json` and a distinct enabled/disabled visual state, using CustomTkinter's native `state="disabled"`.

  ![sCTkTextboxPrimary in dark mode](images/sCTkTextboxPrimary_Dark.png)&emsp; &emsp; &emsp; &emsp;
 ![sCTkTextboxPrimary in light mode](images/sCTkTextboxPrimary_Light.png)

If `fg_color` resolves to `"transparent"` at construction, the widget copies its parent's actual `fg_color` instead, since `CTkTextbox` doesn't render true transparency the way canvas-based widgets can.

---

### Constructor

```python
sCTkTextboxPrimary(master=None, **kw)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `**kw` | — | — | `state` is pulled out and applied after construction. Everything else is any native `CTkTextbox` argument, or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). |

```python
log_area = sCTkTextboxPrimary(master=control_panel)
log_area.pack(fill="both", expand=True, padx=40, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(state_string=None)` | `str` | Gets or sets the widget's enabled/disabled state. Only `"disabled"` (case-insensitive) disables it; `"normal"`, `"enabled"`, or `"active"` all enable it. Uses CTk's native `state="disabled"`, consistent with the other widgets in this library confirmed to correctly block interaction this way. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: passing `state=...` updates the tracked state and triggers a repaint. Calling `configure("propname")` with a single property name returns a Tkinter-style query tuple for `state`, `fg_color`, `text_color`, `border_color`, `scrollbar_button_color`, and `scrollbar_button_hover_color`. |

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block, including `font`, `border_width`, and `corner_radius`, is merged with any matching keyword arguments and applied when the widget is built.
- **Re-applied on every `state()` change** — `fg_color`, `border_color`, `text_color`, `scrollbar_button_color`, and `scrollbar_button_hover_color` are recomputed from the theme's normal values or its `disabled_map`. This includes manually re-theming the widget's internal scrollbar, which isn't automatically covered by a single `configure()` call.

```json
{
    "sCTkTextboxPrimary": {
        "font": ["Arial", 13, "normal"],
        "border_width": 1,
        "corner_radius": 6,
        "border_color": ["#b5beb6", "#3d5242"],
        "fg_color": ["#cbcfcb", "#1a1a1a"],
        "text_color": ["#1c1d1c", "#e3ece4"],
        "scrollbar_button_color": ["#64748B", "#4B5563"],
        "scrollbar_button_hover_color": ["#1A4375", "#2471A3"],
        "disabled_map": {
            "fg_color": ["#E5E7EB", "#111827"],
            "border_color": ["#CBD5E1", "#1F2937"],
            "text_color": ["#94A3B8", "#64748B"],
            "scrollbar_button_color": ["#E5E7EB", "#1F2937"],
            "scrollbar_button_hover_color": ["#E5E7EB", "#1F2937"]
        }
    }
}
```

`scrollbar_button_color` and `scrollbar_button_hover_color` are required to be present in whichever map is active — if either is missing, the widget raises immediately rather than substituting a hardcoded color.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family, though not separately re-confirmed for this specific widget.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkTextboxPrimary, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("450x350")
    root.title("TextboxPrimary Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    log_area = sCTkTextboxPrimary(base)
    log_area.pack(fill="both", expand=True, pady=10)
    log_area.insert("1.0", "Log output appears here...")

    def toggle_disabled():
        target = "disabled" if log_area.get_state() == "normal" else "normal"
        log_area.state(target)
        disable_toggle.configure(text="Enable Log" if target == "disabled" else "Disable Log")

    disable_toggle = sCTkButtonPrimary(base, text="Disable Log", command=toggle_disabled)
    disable_toggle.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- Calling `configure("fg_color")` (or similar) returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for six specific properties, and falls through to the native widget's `configure()` for anything else.

[Return to Table of Contents](#contents)
