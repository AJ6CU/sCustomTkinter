## sCTkSwitch

The `sCTkSwitch` is a theme-compliant, standard custom toggle switch component inheriting directly from `ctk.CTkSwitch`. It guarantees absolute layout engine continuity and native rendering execution pipelines. The widget enforces custom framework state management layers, text desaturation systems, and an airtight event priority tag shield when locked, without clashing with low-level canvas polygon caching locks.

<a name="contents"></a>
### 📍 Table of Contents
* [API Constructor Reference](#constructor)
* [Dynamic Interaction Lock Tag Shield](#tag-shield)
* [Architectural Variants (Standard vs. Alt)](#variants)
* [Global Object Instance Methods](#methods)
* [Centralized Stylesheet Integration](#stylesheet)
* [Implementation Reference Template](#template)

---

<a name="constructor"></a>
### 📋 API Constructor Reference

```python
sCTkSwitch(master=None, text="", command=None, variable=None, textvariable=None, onvalue=1, offvalue=0, state="normal", font=None, **kw)
```

| Parameter Name | Data Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `master` | `any` | `None` | Reference pointer tracking your root window or parent layout layer capsule container. |
| `text` | `str` | `""` | The descriptive typography text string label displayed natively alongside the toggle switch track. |
| `command` | `callable` | `None` | Optional event logging callback function executed instantly on state shifts, passing the active value. |
| `variable` | `Variable` | `None` | Persistent Tkinter variable tracking hook (e.g. `tk.IntVar` or `tk.StringVar`) mapped to the toggle state value. |
| `textvariable` | `Variable` | `None` | Dynamic data trace observer variable instance to update text description labels automatically. |
| `onvalue` | `any` | `1` | The value coordinate passed to callbacks and written to variables when the toggle switch is checked. |
| `offvalue` | `any` | `0` | The value coordinate passed to callbacks and written to variables when the toggle switch is unchecked. |
| `state` | `str` | `"normal"` | Execution state controller. Toggling to `"disabled"` dampens text brightness and blocks user inputs. |
| `font` | `tuple` / `str` | `None` | Typography configuration specifically assigned to resolve descriptive text labels. |

---

<a name="tag-shield"></a>
### 🛡️ Dynamic Interaction Lock Tag Shield
Natively, CustomTkinter handles `state="disabled"` passes via broad variable updates, leaving child canvas elements interactively vulnerable if theme recoloring actions occur post-initialization. 

The `sCTkSwitch` component overcomes this limitation by implementing a **High-Priority Event Capture Tag Shield**. When the widget state shifts to locked, a custom verification tag is pre-appended to the front of the sub-widget's low-level execution `bindtags` list. Clicks on the track or label instantly evaluate the blocker and return `"break"`, terminating event propagation immediately and freezing the switch toggle handle in place safely.

---

<a name="variants"></a>
### ⚡ Architectural Variants (Standard vs. Alt)
Depending on your operational interface display requirements, the library offers two parallel switch components to choose from:

1. **`sCTkSwitch` (Standard Base Variant):**
   * *Underlying Engine:* Inherits directly from `ctk.CTkSwitch` for native performance footprint rendering.
   * *Behavioral Limits:* Because CustomTkinter strictly locks down track and knob canvas polygons upon birth loop execution, this version **retains native color caching loops**. Live color shifts on the track/knob background fields are ignored when disabled; only text strings dim natively.
   * *Animations:* Preserves CustomTkinter's native smooth handle slider transition curves out-of-the-box.

2. **`sCTkSwitchAlt` (Alternative Composite Drawing Variant):**
   * *Underlying Engine:* Built as a custom composite draw frame utilising separate target capsules.
   * *Behavioral Advantages:* Grants **100% complete color rendering control** driven straight out of your central `themes.json` sheets. The background track maintains a constant unified color whether checked on or off when active, and flips entirely to distinct muted steel-gray tokens when disabled.
   * *Animations:* Bypasses the native sliding transition loop pass; the circular selector disc knob snaps coordinates instantly upon tracking clicks.

---

<a name="methods"></a>
### ⚡ Global Object Instance Methods

#### Query Dual-Routing State Parameters
```python
# Returns the active system tracking string ('normal' or 'disabled')
current_mode = switch.get_state()
```

#### Apply Absolute Operational Interaction Locks
```python
# Freezes input clicks natively while dimming text typography down to custom gray levels
switch.state("disabled")
```

#### Fetch Active State Position Values
```python
# Returns the active onvalue or offvalue coordinate matching the handle position
position_status = switch.get()
```

#### Programmatically Toggle Handle Placements
```python
# Forcefully moves the toggle switch handle to a specific value coordinate cleanly
switch.set("on")
```

---

<a name="stylesheet"></a>
### 🎨 Centralized Stylesheet Integration (`sCTkThemes.json`)

Both the standard and alternative switch widgets route look parameters natively through a single unified profile entry key block. The standard native-base version intelligently passes style tokens while ignoring the low-level track overrides it cannot natively paint.

```json
{
    "sCTkSwitch": {
        "fg_color": ["#94A3B8", "#475569"],
        "progress_color": ["#1A4375", "#1F6AA5"],
        "button_color": ["#FFFFFF", "#CBD5E1"],
        "button_hover_color": ["#E5E7EB", "#94A3B8"],
        "text_color": ["#1F2937", "#F9FAFB"],
        "font": ["Arial", 14, "normal"],
        
        "disabled_map": {
            "text_color": ["#94A3B8", "gray50"],
            "fg_color": ["#E5E7EB", "#1F2937"],
            "progress_color": ["#CBD5E1", "#334155"],
            "button_color": ["#8A94A6", "#374151"],
            "button_hover_color": ["#8A94A6", "#374151"]
        }
    }
}
```

---

<a name="template"></a>
### 💻 Implementation Reference Template

```python
import customtkinter as ctk
import sCTkThemes
from sCTkFrame import sCTkFrame
from sCTkSwitch import sCTkSwitch

if __name__ == "__main__":
    import sCTkThemes
    from sCTkFrame import sCTkFrame

    sCTkThemes.apply_sCTkThemes()
    root = ctk.CTk()
    root.geometry("450x240")
    root.title("sCTkSwitch Native Container Validation Bench")

    base_container = sCTkFrame(root, border_width=2)
    base_container.pack(expand=True, fill="both", padx=30, pady=30)

    widget = sCTkSwitch(base_container, text="Lock Transceiver Pre-Amp Link")
    widget.pack(expand=True, fill="none", padx=10, pady=10)

    def toggle_panel_lock():
        current_mode = widget.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        widget.configure(state=target)
        btn_lock.configure(text="Unlock Switch (Set 'normal')" if target == "disabled" else "Lock Switch (Set 'disabled')")
        print(f"Logged Verification Hook -> widget.get_state() = {widget.get_state()}")

    btn_lock = ctk.CTkButton(root, text="Lock Switch (Set 'disabled')", command=toggle_panel_lock)
    btn_lock.pack(side="bottom", pady=15)

    root.mainloop()
```

[Return to Table of Contents](#contents)
