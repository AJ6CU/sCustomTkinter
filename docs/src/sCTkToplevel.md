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
