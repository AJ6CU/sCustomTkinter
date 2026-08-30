
## sCTkCheckBox

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkCheckBox` is a themeable subclass of `customtkinter.CTkCheckBox`. It adds automatic light/dark theme resolution from `sCTkThemes.json`, including the checkmark color itself, and a distinct enabled/disabled visual state.

![sCTkCheckBox_Dark.png](images/sCTkCheckBox_Dark.png)
![sCTkCheckBox_Light.png](images/sCTkCheckBox_Light.png)
---

### Constructor

```python
sCTkCheckBox(master=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `**kwargs` | — | — | Any native `CTkCheckBox` argument (e.g. `text`, `command`, `variable`, `onvalue`, `offvalue`), or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). No special extraction step — everything flows straight through to construction. |

```python
agree_checkbox = sCTkCheckBox(
    master=form_panel,
    text="I agree to the terms",
    command=on_agreement_toggled,
)
agree_checkbox.pack(anchor="w", padx=20, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(mode=None)` | `str` | Gets or sets the widget's enabled/disabled state. Only `"disabled"` (case-insensitive) disables it; `"normal"`, `"enabled"`, or `"active"` all enable it. Any other value leaves the state unchanged. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: passing `state=...` routes to `state()` rather than the native option; calling `configure("propname")` with a single property name returns a Tkinter-style query tuple for `state`, `fg_color`, `border_color`, `text_color`, `hover_color`, and `checkmark_color`. Queries for any other property name fall through to the native `CTkCheckBox.configure`. |

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block is merged with any matching keyword arguments and applied when the widget is built.
- **Re-applied on every `state()` change** — `fg_color`, `border_color`, `hover_color`, `text_color`, `checkmark_color`, `border_width`, and `font` are recomputed from the theme's normal values or its `disabled_map` every time you call `state()`.

```json
{
    "sCTkCheckBox": {
        "font": ["Arial", 15, "normal"],
        "border_width": 3,
        "border_color": ["#64748B", "#94A3B8"],
        "fg_color": ["#1A4375", "#2471A3"],
        "hover_color": ["#112A4B", "#1F618D"],
        "text_color": ["#1F2937", "#D1D5DB"],
        "checkmark_color": ["#FFFFFF", "#FFFFFF"],
        "disabled_map": {
            "text_color": ["#94A3B8", "#64748B"],
            "fg_color": ["#E5E7EB", "#374151"],
            "border_color": ["#CBD5E1", "#475569"],
            "checkmark_color": ["#94A3B8", "#64748B"]
        }
    }
}
```

`checkmark_color` was added as a real theme key during this project's audit — previously the theme block didn't define it at all, so the checkmark silently always used CTkCheckBox's native default color regardless of what theme was active, even though the widget's own code was already set up to read it. When disabled, the checkmark dims to match `disabled_map.text_color`'s gray rather than staying bright against a grayed-out box.

Note there's no `hover_color` entry in `disabled_map` — the widget's native disabled state is expected to suppress hover interaction entirely (consistent with the same behavior confirmed on other themed widgets in this project), so a disabled-specific hover color was judged unnecessary; this hasn't been independently re-confirmed for this specific widget.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and `sCTkButtonPrimary`, though not separately re-confirmed for this widget's light/dark toggle specifically.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkCheckBox, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x300")
    root.title("CheckBox Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    agree_checkbox = sCTkCheckBox(
        base, text="I agree to the terms", command=lambda: print("Toggled")
    )
    agree_checkbox.pack(anchor="w", pady=10)

    def toggle_disabled():
        target = "disabled" if agree_checkbox.get_state() == "normal" else "normal"
        agree_checkbox.state(target)
        disable_toggle.configure(text="Enable" if target == "disabled" else "Disable")

    disable_toggle = sCTkButtonPrimary(base, text="Disable Checkbox", command=toggle_disabled)
    disable_toggle.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- `state()` only recognizes `"disabled"` and `"normal"`/`"enabled"`/`"active"`; any other value (including typos) silently leaves the state unchanged.
- Calling `configure("fg_color")` (or similar) returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for five specific properties, and falls through to the native widget's `configure()` for anything else.
- Color reapplication after a `state()` change is deferred by one event-loop tick (`after_idle`), as a precaution carried over from a confirmed race condition on `sCTkButtonPrimary`. In virtually all normal usage this is imperceptible, but code that inspects colors in the same tick as a `state()` call may see the pre-change values.

[Return to Table of Contents](#contents)
