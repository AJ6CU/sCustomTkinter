## sCTkTextboxSecondary

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkTextboxSecondary` is a themeable subclass of `customtkinter.CTkTextbox` — a multi-line text area, the lower-emphasis of the library's two textbox tiers (see also `sCTkTextboxPrimary`). It adds automatic light/dark theme resolution from `sCTkThemes.json` and a distinct enabled/disabled visual state, using CustomTkinter's native `state="disabled"`.

Dark Mode:  ![sCTkTextboxSecondary in dark mode](images/sCTkTextboxSecondary_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode: ![sCTkTextboxSecondary in light mode](images/sCTkTextboxSecondary_Light.png)

If `fg_color` resolves to `"transparent"` at construction, the widget copies its parent's actual `fg_color` instead — same rationale as `sCTkTextboxPrimary`'s identical fallback.

---

### Constructor

```python
sCTkTextboxSecondary(master=None, **kw)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `**kw` | — | — | `state` is pulled out and applied after construction. Everything else is any native `CTkTextbox` argument, or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). |

```python
notes_area = sCTkTextboxSecondary(master=control_panel)
notes_area.pack(fill="both", expand=True, padx=40, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(state_string=None)` | `str` | Gets or sets the widget's enabled/disabled state. Only `"disabled"` (case-insensitive) disables it; `"normal"`, `"enabled"`, or `"active"` all enable it. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: passing `state=...` updates the tracked state and triggers a repaint. Calling `configure("propname")` with a single property name returns a Tkinter-style query tuple for `state`, `fg_color`, `text_color`, `border_color`, `scrollbar_button_color`, and `scrollbar_button_hover_color`. |

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block, including `font`, is merged with any matching keyword arguments and applied when the widget is built. Note `border_width` and `corner_radius` are both `0` for this style — no visible border, unlike `sCTkTextboxPrimary`.
- **Re-applied on every `state()` change** — `fg_color`, `text_color`, `scrollbar_button_color`, and `scrollbar_button_hover_color` are recomputed from the theme's normal values or its `disabled_map`, including manually re-theming the internal scrollbar.

```json
{
    "sCTkTextboxSecondary": {
        "font": ["Arial", 12, "normal"],
        "border_width": 0,
        "corner_radius": 0,
        "fg_color": ["#FFFFFF", "#111827"],
        "text_color": ["#1F2937", "#F9FAFB"],
        "scrollbar_button_color": ["#64748B", "#4B5563"],
        "scrollbar_button_hover_color": ["#1A4375", "#2471A3"],
        "disabled_map": {
            "fg_color": ["#E5E7EB", "#111827"],
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
from scustomtkinter import sCTk, sCTkFrame, sCTkTextboxSecondary, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("450x350")
    root.title("TextboxSecondary Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    notes_area = sCTkTextboxSecondary(base)
    notes_area.pack(fill="both", expand=True, pady=10)
    notes_area.insert("1.0", "Notes go here...")

    def toggle_disabled():
        target = "disabled" if notes_area.get_state() == "normal" else "normal"
        notes_area.state(target)
        disable_toggle.configure(text="Enable Notes" if target == "disabled" else "Disable Notes")

    disable_toggle = sCTkButtonPrimary(base, text="Disable Notes", command=toggle_disabled)
    disable_toggle.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- Calling `configure("fg_color")` (or similar) returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for six specific properties, and falls through to the native widget's `configure()` for anything else.

[Return to Table of Contents](#contents)
