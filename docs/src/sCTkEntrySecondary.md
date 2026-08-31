## sCTkEntrySecondary

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkEntrySecondary` is a themeable subclass of `customtkinter.CTkEntry` — the lower-emphasis of the library's two entry-field tiers (see also `sCTkEntryPrimary`). It adds automatic light/dark theme resolution from `sCTkThemes.json` and a genuine three-state visual model: normal, readonly, and disabled.

Dark Mode:	![sCTkEntrySecondary in dark mode](images/sCTkEntrySecondary_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode:	![sCTkEntrySecondary in light mode](images/sCTkEntrySecondary_Light.png)


All three states use CTk's native `state` option (`"normal"`, `"readonly"`, `"disabled"`) — see `sCTkEntryPrimary`'s documentation for the full rationale and the readonly-specific placeholder behavior worth knowing about.

---

### Constructor

```python
sCTkEntrySecondary(master=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `**kwargs` | — | — | Any native `CTkEntry` argument, or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). `state` is extracted and applied after construction rather than passed to the native constructor. |

```python
notes_entry = sCTkEntrySecondary(
    master=control_panel,
    placeholder_text="Optional notes",
)
notes_entry.pack(fill="x", padx=40, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(state_string=None)` | `str` | Gets or sets the widget's visual state. `"normal"`/`"enabled"`/`"active"` all map to `"normal"`; `"readonly"` maps to `"readonly"`; `"disabled"` maps to `"disabled"`. All three use CTk's native `state` option. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: passing `state=...` routes to `state()` rather than the native option; calling `configure("propname")` with a single property name returns a Tkinter-style `(name, name, name, default, current)` tuple for `state`, `fg_color`, `text_color`, `border_color`, and `placeholder_text_color`. Queries for any other property name fall through to the native `CTkEntry.configure`. |

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block, including `font` and `corner_radius`, is merged with any matching keyword arguments and applied when the widget is built.
- **Re-applied on every `state()` change** — `fg_color`, `border_color`, `text_color`, and `placeholder_text_color` are recomputed from the theme's normal values, its `disabled_map`, or its `readonly_map` every time you call `state()`.

```json
{
    "sCTkEntrySecondary": {
        "font": ["Arial", 13, "normal"],
        "border_width": 1,
        "border_color": ["#9CA3AF", "#4B5563"],
        "fg_color": ["#F3F4F6", "#1F2937"],
        "text_color": ["#4B5563", "#D1D5DB"],
        "placeholder_text_color": ["#94A3B8", "#64748B"],
        "corner_radius": 6,
        "disabled_map": {
            "fg_color": ["#F3F4F6", "#0B0F19"],
            "border_color": ["#CBD5E1", "#374151"],
            "text_color": ["#94A3B8", "#64748B"]
        },
        "readonly_map": {
            "fg_color": ["#F3F4F6", "#1F2937"],
            "border_color": ["#64748B", "#6B7280"],
            "text_color": ["#4B5563", "#D1D5DB"],
            "placeholder_text_color": ["#94A3B8", "#64748B"]
        }
    }
}
```

**`readonly_map` requires all four keys** whenever `readonly` is actually requested — see `sCTkEntryPrimary`'s docs for the full requirement and design rationale (`text_color` deliberately matches normal exactly; `fg_color` stays close to normal too, since Secondary's normal state is already fairly subtle and there wasn't much room to differentiate further without it starting to look disabled instead).

Same rationale as `sCTkEntryPrimary`: `placeholder_text_color` is a genuinely distinct, themed value, following CustomTkinter's own convention of giving placeholder text a visibly more muted color than typed text. CTkEntry has no separate font for placeholder text — it always shares the single `font` property with typed text; that's a real limitation of the underlying widget, not a gap in this theme file.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family, though not separately re-confirmed for this specific widget.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkEntrySecondary, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x250")
    root.title("EntrySecondary Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    notes_entry = sCTkEntrySecondary(base, placeholder_text="Optional notes")
    notes_entry.pack(fill="x", pady=10)

    def toggle_disabled():
        target = "disabled" if notes_entry.get_state() == "normal" else "normal"
        notes_entry.state(target)
        disable_toggle.configure(text="Enable Field" if target == "disabled" else "Disable Field")

    disable_toggle = sCTkButtonPrimary(base, text="Disable Field", command=toggle_disabled)
    disable_toggle.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- `state()` only recognizes `"disabled"`, `"readonly"`, and `"normal"`/`"enabled"`/`"active"`; any other value leaves the internal state flag unchanged, though colors are still harmlessly re-applied.
- **`readonly` never deactivates placeholder text, even on focus** — confirmed directly against CustomTkinter's own source; see `sCTkEntryPrimary`'s docs for the full explanation.
- The disable/enable-cycle cursor-position fix is also applied on transitions into `readonly`, as a precaution not independently verified the way normal↔disabled was — see `sCTkEntryPrimary`'s docs for why this is likely lower-risk than it sounds.
- Calling `configure("fg_color")` (or similar) returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for five specific properties, and falls through to the native widget's `configure()` for anything else.

[Return to Table of Contents](#contents)
