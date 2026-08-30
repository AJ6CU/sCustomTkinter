## sCTkProgressBar

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkProgressBar` is a themeable subclass of `customtkinter.CTkProgressBar`. It adds automatic light/dark theme resolution from `sCTkThemes.json` and a purely visual "disabled" state — progress bars have no click behavior to block, so disabling one only dims its colors.

Dark Mode:  ![sCTkProgressBar in dark mode](images/sCTkProgressBar_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode: ![sCTkProgressBar in light mode](images/sCTkProgressBar_Light.png)

---

### Constructor

```python
sCTkProgressBar(master=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `**kwargs` | — | — | `state` is pulled out and applied after construction. Everything else is any native `CTkProgressBar` argument, or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). |

```python
signal_meter = sCTkProgressBar(master=control_panel)
signal_meter.pack(fill="x", padx=40, pady=10)
signal_meter.set(0.65)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(mode=None)` | `str` | Gets or sets the widget's visual "disabled" state. Unlike most widgets in this library, any string is accepted and stored as-is (lowercased) — there's no validation against a fixed set of values. Only the literal `"disabled"` actually changes colors; anything else is treated as "not disabled". |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `cget("state")` | `str` | Returns the current state, same as `get_state()`. Intercepted specially because native `CTkProgressBar` has no real `"state"` option to query — without this override, `cget("state")` would raise. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: passing `state=...` routes to `state()` rather than the native option; calling `configure("propname")` with a single property name returns a Tkinter-style `(name, name, name, default, current)` tuple for `state`, `fg_color`, `progress_color`, and `border_color`. Queries for any other property name fall through to the native `CTkProgressBar.configure`. |

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block, including `width`, `height`, and `corner_radius`, is merged with any matching keyword arguments and applied when the widget is built.
- **Re-applied on every `state()` change** — `fg_color`, `progress_color`, `border_width`, and `corner_radius` are recomputed from the theme's normal values or its `disabled_map` every time you call `state()`.

```json
{
    "sCTkProgressBar": {
        "width": 200,
        "height": 6,
        "fg_color": ["#E5E7EB", "#4B5563"],
        "progress_color": ["#1A4375", "#2471A3"],
        "corner_radius": 100,
        "disabled_map": {
            "fg_color": ["#CBD5E1", "#374151"],
            "progress_color": ["#94A3B8", "#4B5563"]
        }
    }
}
```

There's no `border_color` anywhere in this theme block, even though the repaint loop checks for one — this style simply has no themed border, the same situation as `sCTkButtonPrimary`'s `border_color`.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family, though not separately re-confirmed for this specific widget.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkProgressBar, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x250")
    root.title("ProgressBar Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    meter = sCTkProgressBar(base)
    meter.pack(fill="x", pady=10)
    meter.set(0.65)

    def toggle_disabled():
        target = "disabled" if meter.get_state() == "normal" else "normal"
        meter.state(target)
        disable_toggle.configure(text="Enable Meter" if target == "disabled" else "Disable Meter")

    disable_toggle = sCTkButtonPrimary(base, text="Disable Meter", command=toggle_disabled)
    disable_toggle.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- `state()` performs no validation at all — any string you pass is stored verbatim; only `"disabled"` actually changes the rendered colors.
- Calling `configure("fg_color")` (or similar) returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for four specific properties, and falls through to the native widget's `configure()` for anything else.

[Return to Table of Contents](#contents)
