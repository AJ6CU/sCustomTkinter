## sCTkSwitch

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkSwitch` is a themeable subclass of `customtkinter.CTkSwitch`. It adds automatic light/dark theme resolution from `sCTkThemes.json` and a distinct enabled/disabled visual state that dims every color property, not just the label text. A previously separate widget, `sCTkSwitchAlt`, existed specifically to work around limitations that have since been resolved directly in this widget and has been retired.

Dark Mode:  ![sCTkSwitch in dark mode](images/sCTkSwitch_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode: ![sCTkSwitch in light mode](images/sCTkSwitch_Light.png)

Disabling combines two mechanisms: CustomTkinter's native `state="disabled"`, and a bindtag-based click interceptor that prepends a dedicated binding returning `"break"` on click. This is more robust than a simple event-unbind, since it intercepts clicks regardless of which internal level the native click handler is actually bound at.

---

### Constructor

```python
sCTkSwitch(master=None, onvalue=1, offvalue=0, command=None, **kw)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `onvalue` | any | `1` | Value reported when the switch is on. |
| `offvalue` | any | `0` | Value reported when the switch is off. |
| `command` | `callable` | `None` | Called on toggle. May accept the new value as a single argument, or no arguments at all — both styles are supported. |
| `**kw` | — | — | `state` is pulled out explicitly. Everything else is either a native `CTkSwitch` argument or a theme-key override (see the "sCTkSwitch" block in [Theming](#theming-sctkthemesjson)). |

```python
notify_switch = sCTkSwitch(
    master=control_panel,
    text="Enable notifications",
    command=on_notify_toggled,
)
notify_switch.pack(anchor="w", padx=40, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `state(mode=None)` | `str` | Gets or sets the widget's enabled/disabled state. |
| `get_state()` | `str` | Equivalent to calling `state()` with no argument. |
| `cget("state")` / `cget("command")` | varies | Both intercepted specially, since they're tracked on the instance rather than delegated to the native widget. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard widget configuration. Note the signature is `configure(require_redraw=None, **kwargs)`, matching real CTk's own convention, rather than `*args` — calling `configure("state")` positionally returns a Tkinter-style query tuple; a positional dict is merged into the update. |

**Exceptions from your `command` propagate normally.** An earlier version silently swallowed every exception a command raised, hiding real bugs completely; this is now fixed, confirmed by direct testing. Tkinter's own default callback-exception handling reports propagated exceptions to the console without crashing the running application.

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key in the widget's theme block, including `font`, is merged with any matching keyword arguments and applied when the widget is built.
- **Re-applied on every `state()`/`configure()` change** — all five color properties (`fg_color`, `progress_color`, `button_color`, `button_hover_color`, `text_color`) are recomputed from the theme's normal values or its `disabled_map`. This full dimming is confirmed working by direct testing.

```json
{
    "sCTkSwitch": {
        "font": ["Arial", 14, "normal"],
        "fg_color": ["#1A4375", "#1F6AA5"],
        "progress_color": ["#1A4375", "#1F6AA5"],
        "button_color": ["#CBD5E1", "#CBD5E1"],
        "button_hover_color": ["#E5E7EB", "#94A3B8"],
        "text_color": ["#1F2937", "#F9FAFB"],
        "disabled_map": {
            "text_color": ["#94A3B8", "#64748B"],
            "fg_color": ["#94A3B8", "#526071"],
            "progress_color": ["#64748B", "#526071"],
            "button_color": ["#CBD5E1", "#94A3B8"],
            "button_hover_color": ["#CBD5E1", "#94A3B8"]
        }
    }
}
```

`button_color` uses the same light-mode value for both normal and hover states by design — it was retuned from an earlier pure-white value, which had too little contrast against light backgrounds in general (not a code bug; CustomTkinter already resolves the widget's background to match its real parent correctly on its own). The disabled-state track colors (`fg_color`/`progress_color`) were similarly retuned for the same reason — the original values were close enough to typical light backgrounds that a disabled switch's track could become hard to see at all.

All five color properties are required to be present in both the top-level block and `disabled_map` — if any are missing, the widget raises immediately rather than substituting a hardcoded color.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they correctly follow system/app appearance-mode changes automatically — confirmed by direct testing, including while disabled.

---

### Example

```python
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkSwitch, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x250")
    root.title("Switch Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    notify_switch = sCTkSwitch(base, text="Enable notifications", command=lambda v: print(f"Value: {v}"))
    notify_switch.pack(anchor="w", pady=10)

    def toggle_disabled():
        target = "disabled" if notify_switch.get_state() == "normal" else "normal"
        notify_switch.state(target)
        disable_toggle.configure(text="Enable Switch" if target == "disabled" else "Disable Switch")

    disable_toggle = sCTkButtonPrimary(base, text="Disable Switch", command=toggle_disabled)
    disable_toggle.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- If your `command` accepts exactly one argument and raises a `TypeError` for a reason unrelated to argument count, the wrapper's fallback logic can't tell the difference from "this command doesn't accept an argument" — it will retry calling your command with no arguments, which then fails with a second, different `TypeError` (a missing-argument error) layered on top of your real bug. Python's exception chaining keeps both visible in the console, so the real bug isn't hidden, just noisier than ideal.
- Calling `configure("propname")` for a property name other than `"state"` is forwarded to the native widget's `configure()`, which does not support single-argument property queries — a known limitation shared with the wider Pygubu query investigation set aside elsewhere in this project.

[Return to Table of Contents](#contents)
