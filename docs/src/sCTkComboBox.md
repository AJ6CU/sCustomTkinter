## sCTkComboBox

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkComboBox` is a themeable subclass of `customtkinter.CTkComboBox`. It adds automatic light/dark theme resolution from `sCTkThemes.json`, a distinct enabled/disabled visual state (separate from, but synchronized with, the widget's native interactive lock), and Pygubu Designer property introspection support.

![sCTkComboBox in dark mode](images/sCTkComboBox_Dark.png)
![sCTkComboBox in light mode](images/sCTkComboBox_Light.png)

---

### Constructor

```python
sCTkComboBox(master=None, values=None, command=None, variable=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `values` | `list[str]` | `[""]` | Dropdown options. If the first entry is a non-empty string, it is selected automatically on creation. |
| `command` | `callable` | `None` | Called with the selected value when the user picks an item. |
| `variable` | `tkinter.StringVar` | `None` | Optional variable bound to the current selection. |
| `**kwargs` | — | — | Any native `CTkComboBox` argument (e.g. `width`, `height`, `font`, `corner_radius`), or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). Anything not supplied falls back to the `sCTkComboBox` block of `sCTkThemes.json`. |

```python
frequency_dropdown = sCTkComboBox(
    master=control_panel,
    values=["Channel A (VHF)", "Channel B (UHF)", "Direct Audio Feed"],
    command=on_frequency_channel_changed,
)
frequency_dropdown.pack(fill="x", padx=40, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `get()` | `str` | Currently selected text (native `CTkComboBox` behavior). |
| `set(value)` | `None` | Sets the displayed text (native `CTkComboBox` behavior). |
| `state(mode=None)` | `str` \| `None` | Gets or sets the widget's enabled/disabled visual state. Accepts `"normal"`, `"enabled"`, or `"active"` (all equivalent) and `"disabled"`. Any other value is silently ignored. Called with no argument, returns the current state as a lowercase string. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration, with two additions: passing `state=...` routes to `state()` rather than the native Tkinter `state` option; calling `configure("propname")` with a single property name returns a Tkinter-style `(name, name, name, default, current)` tuple for `state`, `fg_color`, `border_color`, `text_color`, and `hover_color`. Queries for any other single property name fall through to the native `CTkComboBox.configure`. |

---

### Theming (`sCTkThemes.json`)

Theme values are used in two different ways, worth keeping separate:

- **Applied once, at construction** — every key in the widget's theme block (including `corner_radius`) is merged with any matching keyword arguments you pass in and applied when the widget is built.
- **Re-applied on every `state()` change** — only `fg_color`, `border_color`, `text_color`, `button_color`, `button_hover_color`, `dropdown_fg_color`, `dropdown_text_color`, `dropdown_hover_color`, `border_width`, and `font` are swapped between the theme's normal values and its `disabled_map` values when you call `state("disabled")` / `state("normal")`. Toggling state also sets the native Tkinter `state` flag, so a disabled combo box is both visually muted and non-interactive.

```json
{
    "sCTkComboBox": {
        "fg_color": ["#FFFFFF", "#1E1E1E"],
        "border_color": ["#94A3B8", "#4B5563"],
        "text_color": ["#111827", "#F9FAFB"],
        "button_color": ["#1A4375", "#1F6AA5"],
        "button_hover_color": ["#112A4B", "#194A7A"],
        "dropdown_fg_color": ["#FFFFFF", "#1F2937"],
        "dropdown_text_color": ["#374151", "#F3F4F6"],
        "dropdown_hover_color": ["#F3F4F6", "#374151"],
        "border_width": 2,
        "corner_radius": 6,
        "disabled_map": {
            "fg_color": ["#F3F4F6", "#111111"],
            "border_color": ["#CBD5E1", "#333333"],
            "text_color": ["#94A3B8", "#4B5563"],
            "button_color": ["#E5E7EB", "#222222"]
        }
    }
}
```

> **Note:** `disabled_map` above has no entries for `dropdown_fg_color`, `dropdown_text_color`, `dropdown_hover_color`, or `button_hover_color`. Since only keys present in `disabled_map` are swapped, those four properties keep their *enabled*-state color when the widget is disabled. Add entries for them here if you want the dropdown portion to visually mute along with the rest of the widget.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkButtonPrimary, sCTkComboBox

if __name__ == "__main__":
    root = sCTk()
    root.geometry("450x300")
    root.title("ComboBox Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    widget = sCTkComboBox(
        base,
        values=["Channel A (VHF)", "Channel B (UHF)", "Direct Audio Feed"],
        command=lambda choice: print(f"Selected: {choice}"),
    )
    widget.pack(expand=True, fill="none", padx=10, pady=10)

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

- `state()` silently ignores any value other than `normal`, `enabled`, `active`, or `disabled` — no exception is raised and no warning is logged.
- Passing a positional `dict` to `configure()` (e.g. `configure({"fg_color": "red"})`) is not merged into the update; only keyword arguments are applied. Use `configure(**your_dict)` instead.


[Return to Table of Contents](#contents)