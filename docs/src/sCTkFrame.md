## sCTkFrame

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkFrame` is a themeable subclass of `customtkinter.CTkFrame`. It adds automatic light/dark theme resolution from `sCTkThemes.json`. Unlike every other widget in this library, it has no disabled state and no per-state color swapping — frames are containers, not interactive controls, so there's nothing to dim or lock.

Dark Mode: ![sCTkFrame in dark mode](images/sCTkFrame_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode: ![sCTkFrame in light mode](images/sCTkFrame_Light.png)

---

### Constructor

```python
sCTkFrame(master=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `**kwargs` | — | — | Any native `CTkFrame` argument, or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). |

```python
panel = sCTkFrame(control_root)
panel.pack(expand=True, fill="both", padx=20, pady=20)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(mode=None)` | `str` | No-op. Always returns `"normal"` regardless of what's passed in — deliberate, not a bug, so generic code written against every widget's `state()`/`get_state()`/`configure(state=...)` API doesn't need a special case for frames. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. Always `"normal"`. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: passing `state=...` is silently absorbed (a no-op) rather than forwarded to the native widget, which has no real state concept; calling `configure("propname")` with a single property name returns a Tkinter-style `(name, name, name, default, current)` tuple for `state`, `fg_color`, and `border_color` — since neither varies by state here, `default` and `current` are always identical. Queries for any other property name fall through to the native `CTkFrame.configure`. |

---

### Theming (`sCTkThemes.json`)

Everything is applied once, at construction — there's no `disabled_map` for this widget, and no runtime color-swapping logic at all.

```json
{
    "sCTkFrame": {
        "border_width": 0,
        "corner_radius": 0,
        "border_color": ["gray", "gray"],
        "fg_color": "transparent"
    }
}
```

With `border_width` at `0`, `border_color` never actually renders visibly regardless of its value — the two are set to the neutral Tkinter color name `"gray"` for both light and dark mode here, but that's moot while the border has no width.

Colors are passed through as raw `(light, dark)` tuples at construction and never touched again, so CustomTkinter's own native appearance-mode tracking handles light/dark repaints on its own — there's no `_set_appearance_mode()` override here, since there's nothing for one to re-trigger. This is the same underlying mechanism validated more deliberately on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family.

---

### Example

```python
#!/usr/bin/python3

from scustomtkinter import sCTkButtonPrimary, sCTkLabelPrimary, sCTk, sCTkFrame


if __name__ == "__main__":

    root = sCTk()
    root.geometry("500x300")
    root.title("sCTkFrame Container Validation Bench")

    # Instantiate your custom theme-compliant frame element chassis
    base_container = sCTkFrame(root, border_width=2)
    base_container.pack(expand=True, fill="both", padx=30, pady=30)
#
#     # Add a simple sub-element child widget to verify structural clipping layouts
    lbl_marker = sCTkLabelPrimary(base_container, text="FRAME BACKPLANE CONTAINER OPERATIONAL\n"+
                                  "Border Visible for Testing Purposes only")
    lbl_marker.pack(expand=True)

    root.mainloop()
```

---

### Known Limitations

- `state()`/`get_state()`/`configure(state=...)` are all no-ops by design — there's no way to visually disable a frame through this API, since the widget has no disabled state at all.
- Calling `configure("fg_color")` or `configure("border_color")` returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for `state`/`fg_color`/`border_color`, and falls through to the native widget's `configure()` for anything else.

[Return to Table of Contents](#contents)
