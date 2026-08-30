## sCTkEntryPrimary

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkEntryPrimary` is a themeable subclass of `customtkinter.CTkEntry` — the higher-emphasis of the library's two entry-field tiers (see also `sCTkEntrySecondary`). It adds automatic light/dark theme resolution from `sCTkThemes.json` and a distinct enabled/disabled visual state.

Dark Mode:	![sCTkEntryPrimary in dark mode](images/sCTkEntryPrimary_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode:	![sCTkEntryPrimary in light mode](images/sCTkEntryPrimary_Light.png)

> **Unresolved design question — read before relying on "disabled" behavior.** This widget's "disabled" state maps to Tkinter's native `"readonly"`, not `"disabled"`. Unlike every other widget in this library, this hasn't been independently confirmed correct or incorrect through direct testing. Behaviorally, `readonly` typically still permits focus, text selection, and copying, while `disabled` fully locks the widget — these are not the same thing. Confirm which behavior you actually want before depending on this.

---

### Constructor

```python
sCTkEntryPrimary(master=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `**kwargs` | — | — | Any native `CTkEntry` argument (e.g. `placeholder_text`, `width`), or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). `state` is extracted and applied after construction rather than passed to the native constructor. |

```python
freq_entry = sCTkEntryPrimary(
    master=control_panel,
    placeholder_text="Enter frequency (MHz)",
)
freq_entry.pack(fill="x", padx=40, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(state_string=None)` | `str` | Gets or sets the widget's enabled/disabled state. Only `"disabled"` (case-insensitive) disables it; `"normal"`, `"enabled"`, or `"active"` all enable it. See the unresolved design note above for what "disabled" actually does at the native level. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: passing `state=...` routes to `state()` rather than the native option; calling `configure("propname")` with a single property name returns a Tkinter-style `(name, name, name, default, current)` tuple for `state`, `fg_color`, `text_color`, `border_color`, and `placeholder_text_color`. Queries for any other property name fall through to the native `CTkEntry.configure`. |

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block, including `font` and `corner_radius`, is merged with any matching keyword arguments and applied when the widget is built.
- **Re-applied on every `state()` change** — `fg_color`, `border_color`, `text_color`, and `placeholder_text_color` are recomputed from the theme's normal values or its `disabled_map` every time you call `state()`.

```json
{
    "sCTkEntryPrimary": {
        "font": ["Arial", 15, "normal"],
        "border_width": 1.5,
        "border_color": ["#1A4375", "#64748B"],
        "fg_color": ["#FFFFFF", "#111827"],
        "text_color": ["#1F2937", "#F9FAFB"],
        "corner_radius": 6,
        "disabled_map": {
            "fg_color": ["#F3F4F6", "#1F2937"],
            "border_color": ["#CBD5E1", "#475569"],
            "text_color": ["#94A3B8", "#64748B"]
        }
    }
}
```

There's no `placeholder_text_color` key here, even though the widget's `configure()`/repaint logic checks for one. If the field ever shows placeholder text, its color comes from CTkEntry's native default, not the theme file. Worth deciding whether to add a real theme key for this (following the precedent of `sCTkCheckBox`'s `checkmark_color`, which had the same gap) or leave it as native.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family, though not separately re-confirmed for this specific widget.

---

### Example

```python
#!/usr/bin/python3

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary, sCTk, sCTkLabelPrimary, sCTkEntryPrimary



if __name__ == "__main__":

    root = sCTk()
    root.geometry("450x260")
    root.title("sCTkEntryPrimary Testing Deck")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    # Label notice layer to monitor buffer array activity
    lbl_monitor = sCTkLabelPrimary(base, text="Console monitor active...")
    lbl_monitor.pack(pady=10)

    # Instantiate your custom Primary helper field
    input_field = sCTkEntryPrimary(base, placeholder_text="Enter configuration metadata...")
    input_field.pack(expand=False, fill="x", padx=40, pady=10)

    # Monitor keystrokes live
    input_field.bind("<KeyRelease>", lambda e: lbl_monitor.configure(text=f"Live Buffer: {input_field.get()}"))

    def toggle_operational_state():
        """Toggles the helper input field between normal active and dimmed disabled profiles."""
        current_mode = input_field.get_state()
        target = "disabled" if current_mode == "normal" else "normal"

        # Explicitly testing the dual-routing capability via configure()
        input_field.configure(state=target)
        btn_toggle.configure(
            text="Lock Helper Input (Set 'disabled')" if target == "normal" else "Unlock Helper Input (Set 'normal')")
        print(f"Logged Verification Hook -> input_field.get_state() = {input_field.get_state()}")

    btn_toggle = sCTkButtonPrimary(base, text="Lock Helper Input (Set 'disabled')", command=toggle_operational_state)
    btn_toggle.pack(side="bottom", pady=15)

    # Run the interactive boot tracking logs
    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    input_field.state("disabled")
    print("state (Disabled Pass) =", input_field.get_state())  # Output: disabled

    input_field.state("normal")
    print("state (Normal Pass)   =", input_field.get_state())  # Output: normal
    print("========================================\n")

    root.mainloop()
```

---

### Known Limitations

- **"Disabled" is actually native "readonly", not "disabled"** — see the note at the top of this document. This may permit focus, selection, and copying even while "disabled".
- `placeholder_text_color` is checked by the widget's code but not defined anywhere in the theme file — see [Theming](#theming-sctkthemesjson).
- `state()` only recognizes `"disabled"` and `"normal"`/`"enabled"`/`"active"`; any other value (including typos) leaves the internal state flag unchanged, though colors are still harmlessly re-applied.
- Calling `configure("fg_color")` (or similar) returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for five specific properties, and falls through to the native widget's `configure()` for anything else.

[Return to Table of Contents](#contents)
