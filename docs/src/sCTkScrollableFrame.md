## sCTkScrollableFrame

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkScrollableFrame` is a themeable subclass of `customtkinter.CTkScrollableFrame`. It adds automatic light/dark theme resolution from `sCTkThemes.json`, plus carefully-tuned cross-platform mouse wheel and macOS trackpad scroll handling that native CustomTkinter doesn't reliably provide on its own.

Dark Mode:  ![sCTkScrollableFrame in dark mode](images/sCTkScrollableFrame_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode: ![sCTkScrollableFrame in light mode](images/sCTkScrollableFrame_Light.png)

Like `sCTkFrame`, this widget has no disabled-state concept at all — no `state()` or `get_state()` exists here. Disabling child widgets placed inside it is entirely the caller's responsibility (loop over `get_children()` and call `.configure(state=...)` on each one yourself).

---

### Constructor

```python
sCTkScrollableFrame(master=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `**kwargs` | — | — | Any native `CTkScrollableFrame` argument (e.g. `label_text`, `orientation`), or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). |

```python
log_viewport = sCTkScrollableFrame(dashboard, width=380, height=250, label_text="Telemetry Log")
log_viewport.pack(padx=20, pady=20, fill="both", expand=True)
log_viewport._finalize_split_bindings()  # required -- see Methods below
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `winfo_children(include_private=False)` | `list` | By default, filters out children whose exact class name is `"CTkScrollbar"`, `"CTkCanvas"`, or `"Canvas"` — internal furniture this widget creates for its own scrolling machinery. **Confirmed correct by direct, live testing** — printing `get_children()` alongside the widget's internal `_parent_frame.winfo_children()` confirmed the real content widgets are found correctly by this method, and are *not* reachable via `_parent_frame` at all (they're nested deeper, inside the internal scrolling canvas). Pass `include_private=True` for the raw, unfiltered list. |
| `get_children()` | `list` | Equivalent to `winfo_children(include_private=False)`. |
| `get_all_children()` | `list` | Equivalent to `winfo_children(include_private=True)`. |
| `_finalize_split_bindings()` | `None` | **Must be called manually, once, after the widget has been placed** with `pack()`/`grid()`/`place()`. This is not an oversight — the scroll-binding logic inspects the widget's actual parent hierarchy via `winfo_parent()`, which may not be fully realized until after placement. Calling this sets up cross-platform mouse wheel and trackpad scrolling (see below); without it, the widget will render correctly but won't scroll via mouse wheel or trackpad at all. |

**On the scroll-handling itself:** this is maintainer-verified, hard-won working code, left completely untouched during this project's audit (only unrelated bugs elsewhere in the same file — argument handling, dead code, color-tuple resolution — were fixed). `_finalize_split_bindings()` binds standard wheel and platform-specific touchpad events across multiple layers (this widget itself, its actual parent canvas if one exists, that canvas's own parent in turn, and this widget's own children) using regular, scoped `.bind()` calls — not `bind_all()` — so it doesn't interfere with any other scrollable widget elsewhere in the same application. It handles three genuinely different platform behaviors: Windows' `/120`-scaled `<MouseWheel>` delta, Linux's discrete `<Button-4>`/`<Button-5>` events (no continuous delta at all on Linux), and macOS's own `<MouseWheel>` scaling plus a separate, higher-precision `<TouchpadScroll>` synthetic event — which packs a two-axis scroll delta into a single 32-bit integer, decoded via bit-shifting into signed 16-bit X and Y components.

---

### Theming (`sCTkThemes.json`)

Everything is applied once, at construction — this widget has no state to re-apply colors for.

```json
{
    "sCTkScrollableFrame": {
        "border_width": 1.5,
        "border_color": ["#64748B", "#94A3B8"],
        "corner_radius": 8,
        "fg_color": ["#FFFFFF", "#111827"],
        "label_fg_color": "transparent",
        "scrollbar_fg_color": ["#FFFFFF", "#111827"],
        "scrollbar_button_color": ["#64748B", "#4B5563"],
        "scrollbar_button_hover_color": ["#1A4375", "#2471A3"],
        "disabled_map": {
            "border_color": ["#CBD5E1", "#374151"],
            "scrollbar_button_color": ["#CBD5E1", "#1F2937"]
        }
    }
}
```

`label_fg_color` is deliberately `"transparent"`, so the internal title-row label blends with the frame's own `fg_color` via CustomTkinter's native parent-to-child color propagation, rather than showing its own distinct background.

**The `disabled_map` block above is currently unused, dead data** — confirmed by reading the actual widget code: there is no `state()` method or disabled-state logic anywhere in this widget, so nothing ever consults `disabled_map` at all. It doesn't cause incorrect behavior, but it's not doing anything either.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family, though not separately re-confirmed for this specific widget.

**Safe to use as a base class for your own composite widgets.** If you build a composite widget by inheriting `sCTkScrollableFrame` directly, construction is protected on two fronts: a run-once guard in `ThemeableWidget.__init__` stops your composite's own `final_kw` from being silently overwritten if your widget explicitly calls `ThemeableWidget.__init__` before `super().__init__()`; and this widget's own constructor only forwards the specific keys native `CTkScrollableFrame` actually accepts (confirmed directly against CustomTkinter's source, which has no fallback `**kwargs` at all — every parameter is explicitly named, so this matters more here than for most widgets).

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkButtonPrimary, sCTkEntryPrimary, sCTkScrollableFrame

if __name__ == "__main__":
    root = sCTk()
    root.title("ScrollableFrame Example")
    root.geometry("450x420")

    log_viewport = sCTkScrollableFrame(root, width=380, height=250, label_text="Telemetry Log")
    log_viewport.pack(padx=20, pady=20, fill="both", expand=True)

    for i in range(12):
        entry = sCTkEntryPrimary(log_viewport, placeholder_text=f"Channel {i + 1}")
        entry.pack(padx=10, pady=5, fill="x")

    # Required once, after placement -- see Methods above.
    log_viewport._finalize_split_bindings()

    _is_locked = False
    def toggle_lock():
        global _is_locked
        _is_locked = not _is_locked
        target = "disabled" if _is_locked else "normal"
        toggle_btn.configure(text="Enable All" if _is_locked else "Disable All")

        # This widget has no disabled concept of its own -- cascade to
        # children explicitly, matching how you'd handle any container
        # that doesn't lock interactivity on its own.
        for child in log_viewport.get_children():
            if hasattr(child, "configure"):
                try:
                    child.configure(state=target)
                except Exception:
                    pass

    toggle_btn = sCTkButtonPrimary(root, text="Disable All", command=toggle_lock)
    toggle_btn.pack(side="bottom", pady=15)

    root.mainloop()
```

---

### Known Limitations

- **No disabled-state concept at all** — no `state()`/`get_state()`, and no cascading to children. This matches `sCTkFrame`'s design; disabling content is entirely the caller's responsibility.
- **Scroll bindings are not automatic.** You must call `self._finalize_split_bindings()` yourself, once, after placing the widget — forgetting this means the widget renders correctly but never responds to mouse wheel or trackpad input.
- **The internal scrollbar cannot be truly disabled** — confirmed to be a genuine CustomTkinter limitation, not something fixable in this wrapper (the same limitation exists on an unwrapped native `CTkScrollableFrame`).
- **`winfo_children()`'s default filtering is a class-name check, not an identity check** — a plain, un-themed `customtkinter.CTkCanvas`/`CTkScrollbar`/`Canvas` added directly as a real child (not internal furniture) would be incorrectly filtered out too, since its class name matches. Themed `sCTk`-prefixed widgets are unaffected.
- **`_parent_frame`'s `width`/`height` don't reflect the real configured size** — confirmed by direct testing: reading `width`/`height` through the outer widget correctly returns the real value, but the same properties read through the internal `_parent_frame` attribute always report `0`, regardless of the widget's actual size. `fg_color`, `border_color`, and `border_width` are reliable through either path; `width`/`height` are not. There's no current code path in this widget that relies on `_parent_frame` for sizing, so this is a trap for future changes, not an active bug.
- The `disabled_map` theme block exists in `sCTkThemes.json` but is never consulted by any code in this widget — harmless, but not functional.

[Return to Table of Contents](#contents)
