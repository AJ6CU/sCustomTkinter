## sCTkLabelSecondary

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkLabelSecondary` is a themeable subclass of `customtkinter.CTkLabel` — the mid-emphasis tier of the library's three label styles, between `sCTkLabelPrimary` and `sCTkLabelTertiary`. It adds automatic light/dark theme resolution from `sCTkThemes.json` and a distinct enabled/disabled visual state. Since labels have no native interactivity to block, "disabled" here is purely a text-color dim.

![sCTkLabelSecondary in dark mode](images/sCTkLabelSecondary_Dark.png)
![sCTkLabelSecondary in light mode](images/sCTkLabelSecondary_Light.png)

---

### Constructor

```python
sCTkLabelSecondary(master=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `**kwargs` | — | — | `state` is pulled out and applied after construction rather than passed to the native widget. Everything else is any native `CTkLabel` argument (e.g. `text`, `font`), or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). |

```python
panel_sub_label = sCTkLabelSecondary(
    master=control_panel,
    text="Status: Active",
)
panel_sub_label.pack(expand=True, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(mode=None)` | `str` | Gets or sets the widget's enabled/disabled state. Only the literal string `"disabled"` (case-insensitive) disables it; `"normal"`, `"enabled"`, or `"active"` all enable it. Any other value matches neither branch and leaves the state unchanged. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `cget("state")` | `str` | Returns the current state, same as `get_state()`. Intercepted specially because native `CTkLabel` has no real `"state"` option to query — without this override, `cget("state")` would raise. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: passing `state=...` routes to `state()` rather than the native option; calling `configure("propname")` with a single property name returns a Tkinter-style `(name, name, name, default, current)` tuple for `state`, `fg_color`, and `text_color`. Queries for any other property name fall through to the native `CTkLabel.configure`. |

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block is merged with any matching keyword arguments and applied when the widget is built.
- **Re-applied on every `state()` change** — `fg_color`, `text_color`, and `font` are recomputed from the theme's normal values or its `disabled_map` every time you call `state()`.

```json
{
    "sCTkLabelSecondary": {
        "font": ["Arial", 15, "normal"],
        "fg_color": "transparent",
        "text_color": ["#374151", "#D1D5DB"],
        "disabled_map": {
            "text_color": ["#94A3B8", "#64748B"]
        }
    }
}
```

Unlike `sCTkLabelPrimary`/`sCTkLabelTertiary`'s history, this widget's `_update_current_visual_state()` was already never falling back to a default — but it also wasn't raising, either; a missing `text_color` would just silently never get set. As of this project's audit, all three label widgets now raise explicitly if `text_color` is missing from whichever map is active, per this project's design of failing hard on incomplete theme data rather than working around it.

Secondary's disabled color sits deliberately in the middle of the three label tiers' disabled states — less muted than Tertiary's, more muted than Primary's — mirroring the emphasis hierarchy the three tiers already have when enabled.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family, though not separately re-confirmed for this specific widget.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkLabelSecondary, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x250")
    root.title("LabelSecondary Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    status_label = sCTkLabelSecondary(base, text="Status: Active")
    status_label.pack(pady=10)

    def toggle_disabled():
        target = "disabled" if status_label.get_state() == "normal" else "normal"
        status_label.state(target)
        disable_toggle.configure(text="Enable Label" if target == "disabled" else "Disable Label")

    disable_toggle = sCTkButtonPrimary(base, text="Disable Label", command=toggle_disabled)
    disable_toggle.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- `state()` only recognizes `"disabled"` and `"normal"`/`"enabled"`/`"active"`; any other value (including typos) matches neither branch and silently leaves the state unchanged.
- Calling `configure("fg_color")` or `configure("text_color")` returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for `state`/`fg_color`/`text_color`, and falls through to the native widget's `configure()` for anything else.

[Return to Table of Contents](#contents)
