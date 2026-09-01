
## sCTkButtonSecondary

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkButtonSecondary` is a themeable subclass of `customtkinter.CTkButton` — a lower-emphasis sibling of `sCTkButtonPrimary` (see also `sCTkButtonTertiary`). It adds automatic light/dark theme resolution from `sCTkThemes.json`, a three-state visual model (normal, disabled, and pressed — no "alarm" state, unlike Primary), and Pygubu Designer property introspection.

Dark Mode:  ![sCTkButtonSecondary_Dark.png](images/sCTkButtonSecondary_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode:  ![sCTkButtonSecondary_Light.png](images/sCTkButtonSecondary_Light.png)

---

### Constructor

```python
sCTkButtonSecondary(master=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `**kwargs` | — | — | Any native `CTkButton` argument (e.g. `text`, `command`, `width`, `height`, `font`, `corner_radius`), or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). As with `sCTkButtonPrimary`, there's no special extraction step — `command` and every other native argument flow straight through to construction. |

```python
cancel_button = sCTkButtonSecondary(
    master=control_panel,
    text="Cancel",
    command=on_cancel_clicked,
)
cancel_button.pack(fill="x", padx=40, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(mode=None)` | `str` | Gets or sets the widget's enabled/disabled state. Only the literal string `"disabled"` (case-insensitive) disables it; `"normal"`, `"enabled"`, or `"active"` all enable it. Any other value matches neither branch and leaves the state unchanged. Disabling uses CTk's native `state="disabled"`, confirmed by direct testing to correctly block both clicks and hover color changes. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `set_pressed(pressed)` | `None` | Forces the visual "pressed" look on or off. No-op while disabled. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: passing `state=...` routes to `state()` rather than the native option; calling `configure("propname")` with a single property name returns a Tkinter-style `(name, name, name, default, current)` tuple for `state`, `fg_color`, `border_color`, `text_color`, and `hover_color`, with `current` reflecting whichever state (disabled/pressed/normal) is presently active. Queries for any other property name fall through to the native `CTkButton.configure`. |

---

### Theming (`sCTkThemes.json`)

Three visual states, with precedence **disabled > pressed > normal** when both could apply.

- **Applied once, at construction** — every key in the widget's theme block, including `font` and `corner_radius`, is merged with any matching keyword arguments and applied when the widget is built.
- **Re-applied on every state change** — `fg_color`, `hover_color`, `border_color`, and `text_color` are recomputed from whichever map matches the current state every time you call `state()` or `set_pressed()`. `border_width`, `corner_radius`, and `font` are **not** re-applied on state changes — they don't vary between states.

```json
{
    "sCTkButtonSecondary": {
        "font": ["Arial", 15, "normal"],
        "fg_color": ["#E5E7EB", "#374151"],
        "hover_color": ["#D1D5DB", "#4B5563"],
        "text_color": ["#1F2937", "#F9FAFB"],
        "border_width": 2,
        "border_color": ["#9CA3AF", "#4B5563"],
        "corner_radius": 6,
        "disabled_map": {
            "fg_color": ["#F3F4F6", "#1F2937"],
            "hover_color": ["#F3F4F6", "#1F2937"],
            "border_color": ["#E5E7EB", "#374151"],
            "text_color": ["#94A3B8", "#64748B"]
        },
        "pressed_map": {
            "fg_color": ["#CBD5E1", "#1F2937"],
            "hover_color": ["#CBD5E1", "#1F2937"],
            "border_color": ["#475569", "#94A3B8"],
            "text_color": ["#0F172A", "#FFFFFF"]
        }
    }
}
```

Unlike `sCTkButtonPrimary` (which has no themed border at all, being a solid-fill button), this style does define `border_color` at every tier — normal, pressed, and disabled all have their own distinct border color.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and `sCTkButtonPrimary`.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkButtonSecondary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x300")
    root.title("ButtonSecondary Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    cancel_button = sCTkButtonSecondary(base, text="Cancel", command=lambda: print("Cancelled"))
    cancel_button.pack(pady=10)

    def toggle_disabled():
        target = "disabled" if cancel_button.get_state() == "normal" else "normal"
        cancel_button.state(target)
        disable_toggle.configure(text="Enable Cancel" if target == "disabled" else "Disable Cancel")

    disable_toggle = sCTkButtonSecondary(base, text="Disable Cancel", command=toggle_disabled)
    disable_toggle.pack(pady=10)

    root.mainloop()
```

---

## Known Limitations

- `state()` only recognizes `"disabled"` and `"normal"`/`"enabled"`/`"active"`; any other value (including typos) matches neither branch and silently leaves the state unchanged.
- Calling `configure("fg_color")` (or `"border_color"`/`"text_color"`/`"hover_color"`) returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for four specific properties, and falls through to the native widget's `configure()` for anything else.



[Return to Table of Contents](#contents)