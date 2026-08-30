

## sCTkButtonTertiary

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkButtonTertiary` is a themeable subclass of `customtkinter.CTkButton` — the lowest-emphasis of the library's three button tiers (see also `sCTkButtonPrimary`, `sCTkButtonSecondary`), styled as an outline button: border and text only, no filled background. It adds automatic light/dark theme resolution from `sCTkThemes.json`, a three-state visual model (normal, disabled, pressed), and Pygubu Designer property introspection.


![sCTkButtonTertiary_Dark.png](images/sCTkButtonTertiary_Dark.png)
![sCTkButtonTertiary_Light.png](images/sCTkButtonTertiary_Light.png)
---

### Constructor

```python
sCTkButtonTertiary(master=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `**kwargs` | — | — | Any native `CTkButton` argument, or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). No special extraction step — `command` and every other native argument flow straight through to construction. |

```python
learn_more_button = sCTkButtonTertiary(
    master=control_panel,
    text="Learn More",
    command=on_learn_more_clicked,
)
learn_more_button.pack(fill="x", padx=40, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(mode=None)` | `str` | Gets or sets the widget's enabled/disabled state. Only `"disabled"` (case-insensitive) disables it; `"normal"`, `"enabled"`, or `"active"` all enable it. Any other value leaves the state unchanged. Uses CTk's native `state="disabled"`, confirmed by direct testing to correctly block clicks and hover color changes. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `set_pressed(pressed)` | `None` | Forces the visual "pressed" look on or off. No-op while disabled. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: passing `state=...` routes to `state()` rather than the native option; calling `configure("propname")` with a single property name returns a Tkinter-style query tuple for `state`, `fg_color`, `border_color`, `text_color`, and `hover_color`. Queries for any other property name fall through to the native `CTkButton.configure`. |

---

### Theming (`sCTkThemes.json`)

Three visual states, with precedence **disabled > pressed > normal**.

```json
{
    "sCTkButtonTertiary": {
        "font": ["Arial", 15, "normal"],
        "fg_color": "transparent",
        "text_color": ["#3B8ED0", "#1F6AA5"],
        "corner_radius": 6,
        "border_width": 1.25,
        "border_color": ["#64748B", "#94A3B8"],
        "hover_color": ["#E2E8F0", "#1E293B"],
        "disabled_map": {
            "border_color": ["#E5E7EB", "#374151"],
            "text_color": ["#94A3B8", "#64748B"]
        },
        "pressed_map": {
            "fg_color": ["#E2E8F0", "#1E293B"],
            "border_color": ["#112A4B", "#1F618D"],
            "text_color": ["#112A4B", "#1F618D"]
        }
    }
}
```

A few design decisions specific to this outline style, worth knowing before editing this block:

- **`fg_color` is the literal string `"transparent"`, not a color pair** — this is a border-and-text-only button by design.
- **`disabled_map` has no `fg_color` or `hover_color` entries, deliberately.** Since only keys present in a map get swapped, omitting these means the button stays transparent when disabled instead of gaining an unwanted solid gray fill — a filled button (Primary/Secondary) wants that fill; this one doesn't.
- **`pressed_map` has no `hover_color` entry either.** Rather than leaving hover color unset while pressed, the widget explicitly falls back to the normal-state `hover_color` in that case.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and `sCTkButtonPrimary`.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkButtonTertiary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x300")
    root.title("ButtonTertiary Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    learn_more_button = sCTkButtonTertiary(base, text="Learn More", command=lambda: print("Clicked"))
    learn_more_button.pack(pady=10)

    def toggle_disabled():
        target = "disabled" if learn_more_button.get_state() == "normal" else "normal"
        learn_more_button.state(target)
        disable_toggle.configure(text="Enable" if target == "disabled" else "Disable")

    disable_toggle = sCTkButtonTertiary(base, text="Disable Learn More", command=toggle_disabled)
    disable_toggle.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- `state()` only recognizes `"disabled"` and `"normal"`/`"enabled"`/`"active"`; any other value (including typos) silently leaves the state unchanged.
- Calling `configure("fg_color")` (or `"border_color"`/`"text_color"`/`"hover_color"`) returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for four specific properties, and falls through to the native widget's `configure()` for anything else.

[Return to Table of Contents](#contents)
