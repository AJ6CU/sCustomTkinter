## sCTkFrameLabeledPrimary

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkFrameLabeledPrimary` is a themeable, high-emphasis labeled container panel — the more prominent of the library's two labeled frame tiers (see also `sCTkFrameLabeledSecondary`). It's built on `customtkinter.CTkScrollableFrame`, but deliberately used purely for its native title-label feature — the model here is `ttk.LabelFrame`, which never scrolls. Scrolling is intentionally suppressed; this is a labeled, bordered panel, not a scroll viewport.

  ![sCTkFrameLabeledPrimary in dark mode](images/sCTkFrameLabeledPrimary_Dark.png)&emsp; &emsp; &emsp; &emsp;
 ![sCTkFrameLabeledPrimary in light mode](images/sCTkFrameLabeledPrimary_Light.png)

---

### Constructor

```python
sCTkFrameLabeledPrimary(master=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `**kwargs` | — | — | Any native `CTkScrollableFrame` argument (most usefully `label_text`, the panel's title), or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). |

```python
channel_panel = sCTkFrameLabeledPrimary(
    master=control_root,
    label_text="Channel Settings",
)
channel_panel.pack(expand=True, fill="both", padx=25, pady=25)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(mode=None)` | `str` | Gets or sets the widget's visual "disabled" state. This is purely cosmetic — plain frame-family widgets have no native interactivity to lock. Disabling this panel does **not** automatically disable widgets placed inside it; that's the caller's responsibility, the same pattern used in this project's own test harness (loop over the panel's children and call `.configure(state=...)` on each one). |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, plus: passing `state=...` routes to `state()`. Calling `configure("propname")` with a single property name returns a Tkinter-style query tuple for `state`, `fg_color`, `border_color`, and `label_text_color`. |
| `winfo_children(include_private=False)` | `list` | By default, filters out children whose exact class name is `"CTkLabel"`, `"Label"`, `"CTkFrame"`, or `"Frame"` — internal furniture `CTkScrollableFrame` creates for its own title row and canvas wrapper. Pass `include_private=True` for the raw, unfiltered list. **Known limitation:** this is a class-name check, not an identity check — a plain, un-themed `customtkinter.CTkLabel`/`CTkFrame` added directly as a child would be filtered out too, since its class name matches. Themed `sCTk`-prefixed widgets are unaffected. |
| `get_children()` | `list` | Equivalent to `winfo_children(include_private=False)`. |
| `get_all_children()` | `list` | Equivalent to `winfo_children(include_private=True)`. |
| `get_container()` | `self` | Returns the widget itself. Provided for API symmetry with composite widgets (like `sCTkOptionMenuSecondary`) that wrap a separate inner container. |

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block, including `label_font` and `corner_radius`, is merged with any matching keyword arguments and applied when the widget is built.
- **Re-applied on every `state()` change** — `fg_color`, `border_color`, `label_text_color`, `border_width`, and `label_font` are recomputed from the theme's normal values or its `disabled_map`.

```json
{
    "sCTkFrameLabeledPrimary": {
        "border_width": 2,
        "border_color": ["#1A4375", "#2471A3"],
        "fg_color": ["#FFFFFF", "#111827"],
        "corner_radius": 8,
        "label_font": ["Arial", 15, "bold"],
        "label_text_color": ["#111827", "#F9FAFB"],
        "disabled_map": {
            "border_color": ["#CBD5E1", "#374151"],
            "label_text_color": ["#94A3B8", "#64748B"]
        }
    }
}
```

**On the internal scrollbar:** since this widget is built on `CTkScrollableFrame`, a scrollbar exists internally even though scrolling isn't the intent. It's suppressed by matching its colors to the frame's background and collapsing its width to `0`. This is a workaround, not a true disable — confirmed by direct investigation, CustomTkinter's native scrollbar has no disabled state to lock in the first place, even on an unwrapped `CTkScrollableFrame`. Matching colors and zeroing width is the closest achievable approximation.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family, though not separately re-confirmed for this specific widget.

**Safe to use as a base class for your own composite widgets.** If you build a composite widget by inheriting `sCTkFrameLabeledPrimary` directly, construction is protected on two fronts: a run-once guard in `ThemeableWidget.__init__` stops your composite's own `final_kw` from being silently overwritten if your widget explicitly calls `ThemeableWidget.__init__` before `super().__init__()`; and this widget's own constructor only forwards the specific keys native `CTkScrollableFrame` actually accepts (confirmed directly against CustomTkinter's source, which has no fallback `**kwargs` at all — every parameter is explicitly named, so this matters more here than for most widgets). This only matters for that composition pattern — constructing a plain `sCTkFrameLabeledPrimary` directly is unaffected either way.

---

### Example

```python
from scustomtkinter import sCTkButtonPrimary, sCTkLabelSecondary, sCTk, sCTkFrameLabeledPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("450x450")
    root.title("FrameLabeledPrimary Example")

    channel_panel = sCTkFrameLabeledPrimary(root, label_text="Channel Settings")
    channel_panel.pack(expand=True, fill="both", padx=25, pady=25)

    for i in range(1, 6):
        item = sCTkLabelSecondary(channel_panel, text=f"Setting {i}")
        item.pack(pady=4, fill="x", padx=10)

    def toggle_panel_state():
        target = "disabled" if channel_panel.get_state() == "normal" else "normal"
        channel_panel.configure(state=target)

        # Disabling the panel is purely cosmetic -- cascade to children explicitly.
        for child in channel_panel.get_children():
            if hasattr(child, "configure"):
                child.configure(state=target)

        toggle_btn.configure(text="Enable Panel" if target == "disabled" else "Disable Panel")

    toggle_btn = sCTkButtonPrimary(root, text="Disable Panel", command=toggle_panel_state)
    toggle_btn.pack(pady=15)

    root.mainloop()
```

---

### Known Limitations

- Disabling this widget is purely cosmetic — it does not lock interactivity, and does not cascade to child widgets automatically.
- The internal scrollbar cannot be truly disabled (a CustomTkinter limitation, confirmed by direct investigation, not something this wrapper can work around) — only visually hidden via color-matching and zero width.
- `winfo_children()`'s default filtering is a class-name check, not an identity check — see the Methods table above for the specific edge case this can miss.
- Calling `configure("fg_color")` (or similar) returns `str(value)` where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. Known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.

[Return to Table of Contents](#contents)
