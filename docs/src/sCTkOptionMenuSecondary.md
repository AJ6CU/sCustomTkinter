## sCTkOptionMenuSecondary

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkOptionMenuSecondary` is the quiet variant of the dropdown option-selection menu — a themeable subclass of `customtkinter.CTkOptionMenu`, with a border. See also [`sCTkOptionMenuPrimary`](sCTkOptionMenuPrimary.md), the emphasised variant.

The two are now **architecturally identical**. They differ only in their theme blocks: this one has a border and an arrow that blends into the control, Primary has no border and an arrow with its own colour. Either look is reachable from either widget by changing the theme.

 ![sCTkOptionMenuSecondary in dark mode](images/sCTkOptionMenuSecondary_Dark.png)&emsp; &emsp; &emsp; &emsp;
	![sCTkOptionMenuSecondary in light mode](images/sCTkOptionMenuSecondary_Light.png)

**This widget used to be a composite** — a `CTkFrame` wrapping a plain `CTkOptionMenu`, because native `CTkOptionMenu` has no border option and this variant needs one. That structure cost more than it bought: `values`, `command` and `variable` lived on the inner menu, so `cget("values")` returned `None` here while returning a list on Primary; every option CustomTkinter added had to be forwarded by hand; and the frame's rounded rectangle did not line up with the menu's, leaving visibly broken corners.

`sCTkOptionMenuBorderMixin` now supplies the border, so this is a plain subclass and `get()`, `set()`, `values`, `command` and `variable` are all native again. `self._menu` no longer exists.

---

### Constructor

```python
sCTkOptionMenuSecondary(master=None, width=160, height=28, **kw)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `width` | `int` | `160` | Widget width, used unless overridden by a kwarg or the theme. |
| `height` | `int` | `28` | Widget height, used unless overridden by a kwarg or the theme. |
| `**kw` | — | — | `values` (list[str]), `command` (callable) and `variable` (tkinter.StringVar) are applied once the native widget exists. Everything else is a native `CTkOptionMenu` argument, `border_width`/`border_color`, or an override for one of the theme keys under [Theming](#theming-sctkthemesjson). |

```python
band_menu = sCTkOptionMenuSecondary(
    master=control_panel,
    values=["80m", "40m", "20m", "10m"],
    command=on_band_changed,
)
band_menu.pack(fill="x", padx=40, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(mode=None)` | `str` | Gets or sets the widget's enabled/disabled state. Only `"disabled"` (case-insensitive) disables it; `"normal"`, `"enabled"` or `"active"` all enable it. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `get()` / `set(value)` | — | Native `CTkOptionMenu` behaviour. |
| `cget(name)` | varies | Native, extended to `border_width` and `border_color`. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard configuration, plus: `border_width`/`border_color`; `values`/`command`/`variable` routed individually; `state=...` through `state()`. `configure("propname")` returns a Tkinter-style query tuple for `state`, the border properties, and `fg_color`/`button_color`/`button_hover_color`/`text_color`; anything else gets a proper tuple from the shared query helper. |
| `update_list(new_values, default_index=0)` | `None` | Replaces the options and resets the visible selection. Empty list falls back to a blank option; out-of-range `default_index` falls back to `0`. |

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block.
- **Re-applied on every `state()` change** — `fg_color`, `text_color` and `border_color` are recomputed from the theme's normal values or its `disabled_map`. The font and dropdown keys are static and set once.

```json
{
    "sCTkOptionMenuSecondary": {
        "border_width": 1.25,
        "corner_radius": 6,
        "border_color": ["#64748B", "#94A3B8"],
        "fg_color": ["#F3F4F6", "#0B0F19"],
        "font": ["Arial", 13, "normal"],
        "dropdown_font": ["Arial", 13, "normal"],
        "text_color": ["#1F2937", "#F9FAFB"],
        "button_hover_color": ["#94A3B8", "#374151"],
        "dropdown_fg_color": ["#FFFFFF", "#1F2937"],
        "dropdown_text_color": ["#1F2937", "#F9FAFB"],
        "dropdown_hover_color": ["#E5E7EB", "#374151"],
        "disabled_map": {
            "text_color": ["#94A3B8", "#64748B"],
            "border_color": ["#CBD5E1", "#374151"],
            "fg_color": ["#E5E7EB", "#0B0F19"]
        }
    }
}
```

**`button_color` is absent deliberately.** It is set from `fg_color` in code, so the arrow blends into the control rather than standing out — that is what makes this the quiet variant. Adding the key would be misleading: the value would be read and then overwritten. Primary gives the arrow its own colour.

**The border comes from `sCTkOptionMenuBorderMixin`,** which both variants share. Native `CTkOptionMenu` has no border option; the mixin supplies one. Primary carries the same keys with `border_width` at 0.

`fg_color` and `text_color` are required to be present in whichever map is active — if either is missing, the widget raises immediately rather than substituting a hardcoded color, per this project's design of failing hard on incomplete theme data (see `sCTkLabelPrimary`/`Secondary`/`Tertiary` for the precedent). An earlier version of this widget used hardcoded hex fallbacks for both, and separately had a real bug where the theme's actual `button_hover_color` was computed correctly and then immediately overwritten with `fg_color` — both are fixed as of this project's audit.

**A colour set at runtime survives a state change,** and clearing it returns to the theme's value rather than to whatever was set before. See [Theming](Theming.md#changing-values-at-runtime) for the general rule.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family, though not separately re-confirmed for this specific widget.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkOptionMenuSecondary, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x250")
    root.title("OptionMenuSecondary Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    band_menu = sCTkOptionMenuSecondary(
        base, values=["80m", "40m", "20m", "10m"], command=lambda choice: print(f"Selected: {choice}")
    )
    band_menu.pack(pady=10)

    def toggle_disabled():
        target = "disabled" if band_menu.get_state() == "normal" else "normal"
        band_menu.state(target)
        disable_toggle.configure(text="Enable Menu" if target == "disabled" else "Disable Menu")

    disable_toggle = sCTkButtonPrimary(base, text="Disable Menu", command=toggle_disabled)
    disable_toggle.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- `state()` only recognizes `"disabled"` and `"normal"`/`"enabled"`/`"active"`; any other value matches neither branch, though colors are still harmlessly re-applied.
- **Fixed:** single-argument queries used to return `str(value)` of a `(light, dark)` tuple rather than a resolved colour. The shared query helper now resolves the pair, so the Designer reads a usable value.
- Passing a positional dict to `configure()` merges into the update; a positional property-name string returns the query tuple described above for five specific properties, and falls through to the native widget's `configure()` for anything else.
- **The border depends on a CustomTkinter internal.** `sCTkOptionMenuBorderMixin` replaces the widget's private `_draw()` and calls the private draw engine, because native `CTkOptionMenu` passes a hardcoded `0` where the border width belongs. If an upstream release changes that method, the border disappears — a visual regression, not a crash.
- **`self._menu` is gone.** Code written against the previous composite structure, which reached the inner dropdown directly, needs updating: this widget *is* the dropdown now.

[Return to Table of Contents](#contents)
