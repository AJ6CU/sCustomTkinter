## sCTkSlider

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkSlider` is a themeable subclass of `customtkinter.CTkSlider`. It adds automatic light/dark theme resolution from `sCTkThemes.json` and a distinct enabled/disabled visual state. Unlike every other widget in this library, its state isn't tracked in a separate instance attribute — it reads and writes CustomTkinter's own native `state` property directly, treating it as the single source of truth.

  ![sCTkSlider in dark mode](images/sCTkSlider_Dark.png)&emsp; &emsp; &emsp; &emsp;
 ![sCTkSlider in light mode](images/sCTkSlider_Light.png)

---

### Constructor

```python
sCTkSlider(master=None, command=None, variable=None, **kw)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `command` | `callable` | `None` | Called with the current value as the slider is dragged. |
| `variable` | `tkinter.Variable` | `None` | Optional variable bound to the current value. |
| `**kw` | — | — | Any native `CTkSlider` argument (e.g. `from_`, `to`, `number_of_steps`), or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). |

```python
volume_slider = sCTkSlider(
    master=control_panel,
    command=on_volume_changed,
)
volume_slider.pack(fill="x", padx=40, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(mode=None)` | `str` | Gets or sets the widget's enabled/disabled state. Queries read directly from the native widget's own `state` property rather than a parallel attribute. Setting forwards to `configure(state=mode)`, which reaches the native widget's own state handling — confirmed by direct testing to correctly block interaction. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: `command`/`variable` are routed individually; `state` is **not** specially intercepted — it flows straight through to the native widget's own `configure()`, which is what makes this widget's disable mechanism correct. Calling `configure("propname")` with a single property name returns a Tkinter-style query tuple for `state`, `fg_color`, `progress_color`, `button_color`, and `button_hover_color`. |

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block, including `width`, `height`, `button_length`, and `border_width`, is merged with any matching keyword arguments and applied when the widget is built.
- **Re-applied on every `state()`/`configure(state=...)` change** — `fg_color`, `progress_color`, `button_color`, and `button_hover_color` are recomputed from the theme's normal values or its `disabled_map`.

```json
{
    "sCTkSlider": {
        "width": 200,
        "height": 24,
        "button_length": 12,
        "border_width": 9,
        "fg_color": ["#E5E7EB", "#4B5563"],
        "progress_color": ["#1A4375", "#2471A3"],
        "button_color": ["#2471A3", "#2471A3"],
        "button_hover_color": ["#112A4B", "#1F618D"],
        "disabled_map": {
            "fg_color": ["#CBD5E1", "#374151"],
            "progress_color": ["#CBD5E1", "#4B5563"],
            "button_color": ["#94A3B8", "#4B5563"]
        }
    }
}
```

`button_color` is the same value for both light and dark mode here — a deliberate accent color that doesn't shift with appearance mode. `disabled_map` has no `button_hover_color` entry; while disabled, the widget explicitly forces `button_hover_color` to match `button_color` instead, since hover can't trigger once natively disabled anyway.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family, though not separately re-confirmed for this specific widget.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkSlider, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x250")
    root.title("Slider Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    volume_slider = sCTkSlider(base, command=lambda v: print(f"Value: {v:.2f}"))
    volume_slider.pack(fill="x", pady=10)

    def toggle_disabled():
        target = "disabled" if volume_slider.get_state() == "normal" else "normal"
        volume_slider.state(target)
        disable_toggle.configure(text="Enable Slider" if target == "disabled" else "Disable Slider")

    disable_toggle = sCTkButtonPrimary(base, text="Disable Slider", command=toggle_disabled)
    disable_toggle.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- Calling `configure("fg_color")` (or similar) returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for four specific properties, and falls through to the native widget's `configure()` for anything else.

[Return to Table of Contents](#contents)
