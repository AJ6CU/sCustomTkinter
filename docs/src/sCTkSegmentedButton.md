## sCTkSegmentedButton

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkSegmentedButton` is a themeable subclass of `customtkinter.CTkSegmentedButton` — a horizontal strip of connected text buttons where selecting one automatically unselects the others, similar to a row of radio buttons. It adds automatic light/dark theme resolution from `sCTkThemes.json`, a distinct enabled/disabled visual state, and per-segment text-color handling for the currently selected segment.

Dark Mode: ![sCTkSegmentedButton_Dark.png](images/sCTkSegmentedButton_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode: ![sCTkSegmentedButton_Light.png](images/sCTkSegmentedButton_Light.png)
---

### Constructor

```python
sCTkSegmentedButton(master=None, values=None, variable=None, command=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `values` | `list[str]` | native default (empty) | The segment labels. |
| `variable` | `tkinter.StringVar` | `None` | Optional variable bound to the current selection. |
| `command` | `callable` | `None` | Called with the selected value when the user picks a segment. |
| `**kwargs` | — | — | Any native `CTkSegmentedButton` argument, or an override for `fg_color` / `selected_color`. |

> **Not settable via constructor:** `unselected_color`, `unselected_hover_color`, `border_width`, `border_color`, and `selected_color_padding` are intentionally stripped out before the native widget is built, regardless of what you pass in. They're only ever pulled from `sCTkThemes.json` — see [Known Limitations](#known-limitations) for why setting them later doesn't stick either.

```python
mode_selector = sCTkSegmentedButton(
    master=control_panel,
    values=["Alpha", "Beta", "Gamma"],
    command=on_mode_changed,
)
mode_selector.pack(fill="x", padx=40, pady=10)
```

Colors are first applied roughly 15ms after construction, not immediately — the widget's individual segment buttons don't exist yet at the moment `sCTkSegmentedButton.__init__` returns, so the initial color pass is deferred with `self.after(15, ...)`. In virtually all normal usage this is unnoticeable, but code that inspects a segment's color in the same tick as construction may see it before this pass runs.

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `get()` | `str` | Currently selected value (native `CTkSegmentedButton` behavior). |
| `set(value)` | `None` | Selects a segment programmatically and repaints (native `set()`, plus a theme-color refresh). |
| `state(mode=None)` | `str` \| `None` | Gets or sets the widget's enabled/disabled visual state. Only the literal string `"disabled"` (case-insensitive) is treated as disabled — **any other value, including typos, is treated as `"normal"`** with no error raised. Called with no argument, returns the current state as a lowercase string. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `configure(**kwargs)` / `config(**kwargs)` | — | Standard widget configuration. Passing `state=...` routes through `state()` rather than the native `state` option. A single positional argument (string or dict) is accepted, but — unlike `sCTkComboBox`/`sCTkCheckBox` — a single property-name string does **not** return a Pygubu-style query tuple here; it's forwarded directly to the native widget instead. (Broader Pygubu query-behavior gaps across the library are a known follow-up item, not specific to this widget.) |

---

### Theming (`sCTkThemes.json`)

Same two-tier model as the other themed widgets:

- **Applied once, at construction** — every key in the widget's theme block is merged with any matching keyword arguments and applied when the widget is built, *except* the five keys listed under [Constructor](#constructor), which are deliberately excluded and applied only through the mechanism below.
- **Re-applied on `state()` change, on selection, and on click** — `fg_color`, `selected_color`, `unselected_color`, `unselected_hover_color`, and each segment's `text_color` are recomputed from the theme's normal values or its `disabled_map` every time you call `state()`, `set()`, or click a segment.

Colors are stored and passed through as raw `(light, dark)` tuples rather than being resolved to a single value ahead of time, which means they correctly follow system/app appearance-mode changes automatically — including while the widget is disabled. Confirmed by direct testing: toggling light/dark mode on a disabled, pre-selected widget repaints it immediately, with no manual intervention needed.

```json
{
    "sCTkSegmentedButton": {
        "fg_color": ["#4F75A2", "#2B4C7E"],
        "selected_color": ["#1A4375", "#3A6FA2"],
        "unselected_hover_color": ["#3A5C85", "#3A5F8C"],
        "text_color": ["#FFFFFF", "#FFFFFF"],
        "disabled_map": {
            "fg_color": ["#B2B9BC", "#222527"],
            "selected_color": ["#70777B", "#45494D"],
            "text_color": ["#94A3B8", "#64748B"],
            "selected_text_color": ["#1F2937", "#FFFFFF"]
        }
    }
}
```

A couple of design decisions worth knowing if you're editing this block:

- **Unselected segments always match `fg_color`, by design** — there's no independent `unselected_color` key. Segments are meant to blend into the widget's own background color rather than appear individually distinct or transparent.
- **Hover is fully suppressed while disabled**, at the native widget level — confirmed by direct testing. There's no `disabled_map` entry for hover colors because a disabled segment never fires a hover event in the first place; any color set there would never be visible.
- **The selected segment keeps a distinct, more prominent text color while disabled** (`disabled_map.selected_text_color`), so you can still tell which option was chosen even though the whole control is grayed out. Every other segment's disabled text color comes from the plain `disabled_map.text_color`.

**Every key above is required,** at the top level or in `disabled_map` as shown. Construction raises `KeyError` naming the missing one.

The colour lookups previously carried hardcoded fallbacks. Those were unreachable given the theme block as shipped — every key they guarded was present — but that was a property of the *theme file*, not the code. Deleting a key would have silently activated a fallback, producing a plausible-looking wrong colour instead of the loud failure every other widget now gives. They're gone.

`selected_hover_color` has also been removed from the block. It was present in the theme but read by no code path at all — dead data, the same situation `pointer_color` was in for the dial family. A selected segment's hover behaviour comes from CustomTkinter's own default, since this widget never set it.

Every color in this widget comes from `sCTkThemes.json` — there are no hardcoded hex values left in the widget's own source.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkButtonPrimary, sCTkSegmentedButton

if __name__ == "__main__":
    root = sCTk()
    root.geometry("450x300")
    root.title("SegmentedButton Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    widget = sCTkSegmentedButton(
        base,
        values=["Alpha", "Beta", "Gamma"],
        command=lambda choice: print(f"Selected: {choice}"),
    )
    widget.pack(expand=True, fill="none", padx=10, pady=10)
    widget.set("Beta")

    def toggle_widget_state():
        target = "disabled" if widget.get_state() == "normal" else "normal"
        widget.configure(state=target)
        btn_toggle.configure(text="Enable" if target == "disabled" else "Disable")

    btn_toggle = sCTkButtonPrimary(base, text="Disable", command=toggle_widget_state)
    btn_toggle.pack(side="bottom", pady=15)

    root.mainloop()
```

---

### Known Limitations

- `state()` treats any value other than `"disabled"` (case-insensitive) as `"normal"` — including typos like `"disbaled"`. No exception is raised and no warning is logged.
- `unselected_color`, `unselected_hover_color`, `border_width`, `border_color`, and `selected_color_padding` cannot be set via constructor kwargs (see [Constructor](#constructor)); the color-related ones only take effect through the theme file or the widget's own repaint logic.
- Calling `configure("some_property_name")` with a single property name does not return a Pygubu-style query tuple the way `sCTkComboBox`/`sCTkCheckBox` do; it's forwarded to the native widget's `configure()`, which — per the wider Pygubu-query investigation set aside earlier in this project — does not support single-argument property queries at all for most properties.


[Return to Table of Contents](#contents)