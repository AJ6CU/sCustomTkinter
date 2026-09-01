## sCTkScrollbar

`sCTkScrollbar` is a themeable scrollbar — a subclass of `ctk.CTkScrollbar` with color resolution from `sCTkThemes.json` and orientation-aware default sizing. It's designed to pair with [`sCTkScrollArea`](sCTkScrollArea.md), which needs an external scrollbar, but works anywhere a `CTkScrollbar` would.

Dark Mode: ![sCTkScrollbar_Dark.png](images/sCTkScrollbar_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode: ![sCTkScrollbar_Light.png](images/sCTkScrollbar_Light.png)

**This widget contains no scroll-handling logic.** It's a scrollbar: it renders a draggable bar and reports its position. Wheel and trackpad handling belongs to the scrolling container — see [`ScrollBindingMixin`](ScrollBindingMixin.md). An earlier version of this page credited the scrollbar with an "inertial micro-delta aggregator"; that logic lives in `sCTkScrollArea`, not here.

<a name="contents"></a>
### Table of Contents
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming](#theming)
* [Example](#example)
* [Known Limitations](#limitations)

---

<a name="constructor"></a>
### Constructor

```python
scrollbar = sCTkScrollbar(master=None, orientation="vertical", **kwargs)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `master` | widget | `None` | Parent container. |
| `orientation` | `"vertical"` / `"horizontal"` | `"vertical"` | Layout direction. Sets a default `width` of 14 when vertical, or `height` of 14 when horizontal. |
| `**kwargs` | — | — | Any native `CTkScrollbar` argument, or a theme-key override (see [Theming](#theming)). |

---

<a name="methods"></a>
### Methods

| Method | Returns | Description |
| :--- | :--- | :--- |
| `configure(**kwargs)` / `config(**kwargs)` | `None` | Standard configuration. Overrides of `button_color` and `button_hover_color` **persist** — see below. |
| `configure(name)` | `tuple` | Pygubu-style single-argument query for `button_color` and `button_hover_color`. Any other name passes through to the native widget. |

**Runtime color overrides persist.** `configure()` records the tracked theme keys into the widget's stored defaults *before* repainting, so an override survives the repaint and later appearance-mode switches. This matches CustomTkinter's own semantics, where `configure(button_color=...)` sticks.

This was previously broken. `_apply_custom_theme_colors()` runs on every `configure()` call and re-pushes both colors from the stored defaults — and since `configure()` never wrote to those defaults, `configure(button_color="red")` applied red and then had it overwritten on the very next line. Runtime color overrides silently did nothing.

Two consequences worth knowing: passing a single color replaces the theme's `(light, dark)` tuple for that key, so **that property stops following light/dark** — which is what asking for one specific color means.

The single-argument query was also previously broken. The implementation tested `if args and isinstance(args, dict)`, but `args` is always a tuple, so that branch was dead and there was no query branch at all — `configure("button_color")` silently returned `None` instead of a property tuple.

---

<a name="theming"></a>
### Theming (`sCTkThemes.json`)

```json
{
    "sCTkScrollbar": {
        "corner_radius": 4,
        "fg_color": "transparent",
        "button_color": ["#64748B", "#4B5563"],
        "button_hover_color": ["#1A4375", "#2471A3"]
    }
}
```

`button_color` is the bar itself; `button_hover_color` is the bar under the cursor. `fg_color` is the track behind it.

**`button_color` and `button_hover_color` are required.** Construction raises `KeyError` naming the missing one. These previously carried hardcoded fallbacks, so a theme block missing either would silently substitute a plausible guess rather than failing loudly.

`orientation` may also be supplied from the theme block. It's read from the resolved keywords rather than the raw constructor dict, so it's picked up whichever way it arrives — an earlier version read the raw dict *after* `ThemeableWidget` had processed it, which risked a horizontal scrollbar silently getting a default `width` instead of `height`.

Colors are passed through as raw `(light, dark)` tuples rather than resolved ahead of time, so they follow appearance-mode changes automatically.

**There is no `disabled_map`, and no disabled state.** CustomTkinter's scrollbar has none to lock. Containers that need an inert scrollbar block dragging at the binding level instead and dim the bar themselves — see [`ScrollBindingMixin`](ScrollBindingMixin.md#disabling-scroll).

---

<a name="example"></a>
### Example

```python
#!/usr/bin/python3
import customtkinter as ctk
from scustomtkinter import (sCTk, sCTkFrame, sCTkLabelSecondary,
                            sCTkScrollbar, sCTkScrollArea)

if __name__ == "__main__":
    root = sCTk()
    root.geometry("480x420")
    root.title("sCTkScrollbar Validation Bench")

    main_layout = sCTkFrame(root, border_width=2)
    main_layout.pack(expand=True, fill="both", padx=15, pady=15)

    scrollbar = sCTkScrollbar(main_layout, orientation="vertical")
    scrollbar.pack(side="right", fill="y", padx=(5, 10), pady=10)

    content_chassis = sCTkFrame(main_layout, border_width=0, fg_color="transparent")
    content_chassis.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)

    scroll_view = sCTkScrollArea(content_chassis)
    scroll_view.pack(fill="both", expand=True)

    for i in range(25):
        sCTkLabelSecondary(
            scroll_view.scroll_content,
            text=f"Transceiver channel {100 + i} [OK]"
        ).pack(anchor="w", padx=10, pady=4)

    scroll_view.hook_scrollbar(scrollbar)

    root.mainloop()
```

---

<a name="limitations"></a>
### Known Limitations

- **No disabled state** — see [Theming](#theming).
- **Only `button_color` and `button_hover_color` are tracked** for the persist-on-`configure()` behavior. Other properties still repaint from the theme.

[Return to Table of Contents](#contents)
