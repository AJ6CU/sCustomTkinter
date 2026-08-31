## sCTkToplevel

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkToplevel` is a themeable subclass of `customtkinter.CTkToplevel`, for secondary windows, modal dialogs, and popups. It adds automatic light/dark theme resolution from `sCTkThemes.json`. This is the simplest widget in the library — no disabled state, no `state()`/`get_state()` at all, and no per-state color-swapping logic, since a top-level window has no interactive "enabled/disabled" concept the way a control does.

Dark Mode:  ![sCTkToplevel in dark mode](images/sCTkToplevel_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode: ![sCTkToplevel in light mode](images/sCTkToplevel_Light.png)

---

### Constructor

```python
sCTkToplevel(master=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent window. |
| `**kwargs` | — | — | Any native `CTkToplevel` argument, or an `fg_color` override — the theme block for this widget currently defines only `fg_color`. |

```python
settings_window = sCTkToplevel(root)
settings_window.title("Settings")
settings_window.geometry("300x200")
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, with positional-dict support (e.g. `configure({"fg_color": "red"})`). There's no single-argument property-query support here — unlike every other widget in this library, a bare positional string (e.g. `configure("fg_color")`) currently has no effect at all, since the only positional-argument handling implemented is the dict-merge case. |

---

### Theming (`sCTkThemes.json`)

Everything is applied once, at construction — there's no `disabled_map` and no runtime color-swapping logic at all.

```json
{
    "sCTkToplevel": {
        "fg_color": ["#F8FAFC", "#0F172A"]
    }
}
```

**Safe to use as a base class for your own composite widgets.** If you build a composite widget by inheriting `sCTkToplevel` directly, construction is protected on two fronts: a run-once guard in `ThemeableWidget.__init__` stops your composite's own `final_kw` from being silently overwritten if your widget explicitly calls `ThemeableWidget.__init__` before `super().__init__()`; and this widget's own constructor only forwards the specific keys native `CTkToplevel` actually accepts. This matters more here than for most widgets — confirmed directly against CustomTkinter's own source, `CTkToplevel.__init__` explicitly validates that no unrecognized keyword survives after its own known-valid keys are popped, and raises immediately if one does. This only matters for the base-class composition pattern — constructing a plain `sCTkToplevel` directly is unaffected either way.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkToplevel, sCTkLabelPrimary, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x250")
    root.title("Toplevel Example")

    def open_settings():
        settings_window = sCTkToplevel(root)
        settings_window.title("Settings")
        settings_window.geometry("300x200")
        sCTkLabelPrimary(settings_window, text="Settings go here").pack(expand=True)

    open_button = sCTkButtonPrimary(root, text="Open Settings", command=open_settings)
    open_button.pack(pady=20)

    root.mainloop()
```

---

### Known Limitations

- No single-argument property-query support (e.g. `configure("fg_color")` does nothing) — consistent with this widget's overall minimalism, but different from every other widget in this library.
- No `state()`/`get_state()`/disabled concept at all — this widget has no visual state to toggle.

[Return to Table of Contents](#contents)
