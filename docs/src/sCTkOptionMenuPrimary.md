## sCTkOptionMenuPrimary

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkOptionMenuPrimary` is a themeable subclass of `customtkinter.CTkOptionMenu` — a dropdown option-selection button. It adds automatic light/dark theme resolution from `sCTkThemes.json` and a distinct enabled/disabled visual state. See also `sCTkOptionMenuSecondary`, a composite bordered variant with a different internal architecture.

Dark Mode: ![sCTkOptionMenuPrimary in dark mode](images/sCTkOptionMenuPrimary_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode: ![sCTkOptionMenuPrimary in light mode](images/sCTkOptionMenuPrimary_Light.png)

---

### Constructor

```python
sCTkOptionMenuPrimary(master=None, values=None, command=None, variable=None, **kw)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `values` | `list[str]` | native default | The dropdown options. |
| `command` | `callable` | `None` | Called with the selected value when the user picks an item. |
| `variable` | `tkinter.StringVar` | `None` | Optional variable bound to the current selection. |
| `**kw` | — | — | Any native `CTkOptionMenu` argument, or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). |

```python
mode_menu = sCTkOptionMenuPrimary(
    master=control_panel,
    values=["AM", "FM", "SSB"],
    command=on_mode_changed,
)
mode_menu.pack(fill="x", padx=40, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(mode=None)` | `str` | Gets or sets the widget's enabled/disabled state. Only `"disabled"` (case-insensitive) disables it; `"normal"`, `"enabled"`, or `"active"` all enable it. Uses CTk's native `state="disabled"`, consistent with the other widgets in this library confirmed to correctly block interaction this way, though not independently re-tested for this specific widget. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: `values`/`command`/`variable` are routed individually; `state=...` routes through `state()`; calling `configure("propname")` with a single property name returns a Tkinter-style `(name, name, name, default, current)` tuple for `state`, `fg_color`, `button_color`, `button_hover_color`, and `text_color`. Queries for any other property name fall through to the native `CTkOptionMenu.configure`. |
| `update_list(new_values, default_index=0)` | `None` | Replaces the dropdown's options and resets the visible selection. If `new_values` is empty, the widget is set to a single blank option. If `default_index` is out of range, falls back to index `0` rather than raising. |

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block, including `font`, `dropdown_font`, and `corner_radius`, is merged with any matching keyword arguments and applied when the widget is built.
- **Re-applied on every `state()` change** — `fg_color`, `button_color`, `button_hover_color`, `text_color`, `dropdown_fg_color`, `dropdown_text_color`, and `font` are recomputed from the theme's normal values or its `disabled_map` every time you call `state()`.

```json
{
    "sCTkOptionMenuPrimary": {
        "font": ["Arial", 15, "normal"],
        "dropdown_font": ["Arial", 15, "normal"],
        "fg_color": ["#1A4375", "#2471A3"],
        "button_color": ["#112A4B", "#1F618D"],
        "button_hover_color": ["#0D1F38", "#1A5276"],
        "text_color": ["#FFFFFF", "#FFFFFF"],
        "corner_radius": 6,
        "dropdown_fg_color": ["#FFFFFF", "#1F2937"],
        "dropdown_text_color": ["#1F2937", "#F9FAFB"],
        "dropdown_hover_color": ["#E5E7EB", "#374151"],
        "disabled_map": {
            "fg_color": ["#CBD5E1", "#374151"],
            "button_color": ["#CBD5E1", "#374151"],
            "text_color": ["#94A3B8", "#64748B"]
        }
    }
}
```

`disabled_map` doesn't cover `button_hover_color`, `dropdown_fg_color`, `dropdown_text_color`, or `dropdown_hover_color` — consistent with every other themed widget in this library: once natively disabled, hover and dropdown-open interactions can't fire in the first place, so there's nothing for a disabled-state color on those properties to ever visibly apply to.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family, though not separately re-confirmed for this specific widget.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkOptionMenuPrimary, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x250")
    root.title("OptionMenuPrimary Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    mode_menu = sCTkOptionMenuPrimary(
        base, values=["AM", "FM", "SSB"], command=lambda choice: print(f"Selected: {choice}")
    )
    mode_menu.pack(pady=10)

    def toggle_disabled():
        target = "disabled" if mode_menu.get_state() == "normal" else "normal"
        mode_menu.state(target)
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

[Return to Table of Contents](#contents)
