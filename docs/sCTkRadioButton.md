## sCTkRadioButton

### Table of Contents
* [System Architecture Overview](#system-architecture-overview)
* [API Constructor Reference](#api-constructor-reference)
* [Convenience Functions](#convenience-functions)
* [Centralized Stylesheet Setup](#centralized-stylesheet-setup-sctkthemesjson)
* [Other Notes](#other-notes)
* [Implementation Example & Test Harness](#implementation-example--test-harness)

---

A theme-compliant custom mutual exclusion radio selection switch component wrapping `customtkinter.CTkRadioButton`. Specially engineered for cockpit tuning tasks—such as VFO selection banks, transmitter operation modes, and antenna relay switches—it decouples low-level parameter configurations to prevent layout validation crashes while keeping disabled states 100% theme-adaptive.

### System Architecture Overview

Unlike standard checkbox elements that track states independently, radio buttons operate in synchronized clusters linked by a shared data backplane container. 

To maintain pristine layout integrity, the architecture implements two vital paradigms:
1. **The Shared Variable Anchor:** By routing your `tk.StringVar` or `tk.IntVar` straight inside the initialization routine, the low-level Tkinter event loops bind correctly to a mutual exclusion track, automatically un-toggling adjacent options when a new choice is pressed.
2. **The Virtual Repaint Shield:** Instead of using CustomTkinter's native state flag (which freezes drawing updates), a virtual state coordinator paralyzes mouse clicking by unbinding Tkinter canvas triggers on the fly, allowing look preferences and grays to translate smoothly during active lockout passes.

---

### API Constructor Reference

```python
sCTkRadioButton(master=None, variable=None, value=None, command=None, **kwargs)
```

| Parameter Name | Data Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `master` | `any` | *Required* | Reference pointer tracking your root window, parent layout layer, or container frame capsule. |
| `variable` | `tk.Variable` | `None` | Shared Tkinter variable tracker (e.g. `tk.StringVar`) that logically interlocks multiple radio selections together. |
| `value` | `any` | `None` | The specific absolute data value passed up to the shared variable anchor when this unique choice row is clicked. |
| `command` | `callable` | `None` | Single-click selection callback executed automatically whenever a valid, active selection shift occurs. |

---

### Convenience Functions
```python
# Evaluate current configurations or apply absolute user interaction locks via dual-routing syntax
current_mode = switch_node.get_state()      # Returns 'normal' or 'disabled'
switch_node.state("disabled")               # Freezes mouse selections and applies desaturated grays safely

# Programmatically query state tracks out of application controllers
active_choice = shared_radio_var.get()     # Extracts the active value string out of the central interlock lane
```
### Centralized Stylesheet Setup (`sCTkThemes.json`)

The component queries your centralized theme sheet profile matrix using standard `self._resolve_color()` lookup calls, ensuring that indicator dots and canvas borders translate colors smoothly across appearance updates.

To satisfy the framework configuration guidelines, ensure your theme matrix includes this structured asset block:

```json
{
    "sCTkRadioButton": {
        "fg_color": ["#1A4375", "#1F6AA5"],
        "border_color": ["#94A3B8", "#4B5563"],
        "text_color": ["#1F2937", "#FFFFFF"],
        "hover_color": ["#112A4B", "#194A7A"],
        "radiobutton_width": 22,
        "radiobutton_height": 22,
        "border_width": 3,
        "font": ["Arial", 11, "bold"],
        "disabled_map": {
            "fg_color": ["#CBD5E1", "#334155"],
            "border_color": ["#E5E7EB", "#222222"],
            "text_color": ["#94A3B8", "#4B5563"]
        }
    }
}
```

---

### Other Notes
* **Crash-Shield Parameter Interceptor:** Passing `value` or `variable` parameters directly into CustomTkinter's public `.configure()` pass after instantiation raises a fatal `ValueError`. The class overrides `.configure()` to catch these keys, assigning them safely through low-level hidden hooks to support dynamic updates without throwing errors.
* **Chassis Alignment Rule:** Because radio string fields frequently contain disparate character lengths, packing them using standard parameters causes staggered checkbox positions. Always apply `anchor="w"` paired with `fill="x"` to cleanly lock indicator circles into a flat vertical left column.
* **Automated Lifecycle Handshake:** Fires `self._finalize_themeable_lifecycle()` at the absolute end of the constructor initialization track to cleanly pass instance registration hooks straight back up to Pygubu layouts out of the box.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to layout a mutually exclusive radio stack inside a themeable frame capsule along with real-time feedback labels.

```python
#!/usr/bin/python3
"""
sCTkRadioButton - Standalone Interactive Testing Harness
"""
import customtkinter as ctk
import tkinter as tk

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
import sCTkThemes                    
from sCTkFrame import sCTkFrame      
from sCTkLabelSecondary import sCTkLabelSecondary
from sCTkRadioButton import sCTkRadioButton

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("450x320")
    root.title("sCTkRadioButton Mutual Exclusion Validation Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    # Centralized StringVar linking both buttons together natively
    radio_var = tk.StringVar(value="VFO_A")

    lbl_monitor = sCTkLabelSecondary(base, text="Active Telemetry Target: VFO_A")
    lbl_monitor.pack(pady=10)

    def print_result():
        lbl_monitor.configure(text=f"Active Telemetry Target: {radio_var.get()}")

    # Packed using horizontal expansion and left anchoring for perfect checkbox stacking
    widget = sCTkRadioButton(base, text="Primary VFO A Link Target", variable=radio_var, value="VFO_A", command=print_result)
    widget.pack(expand=False, fill="x", padx=60, pady=10, anchor="w")

    widget2 = sCTkRadioButton(base, text="Secondary VFO B Link Target", variable=radio_var, value="VFO_B", command=print_result)
    widget2.pack(expand=False, fill="x", padx=60, pady=10, anchor="w")

    def toggle_radio_lock():
        """Toggles operational availability states back and forth."""
        current_mode = widget.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        widget.configure(state=target)
        widget2.configure(state=target)
        btn_lock.configure(text="Lock Radio Switch" if target == "normal" else "Unlock Radio Switch")

    def toggle_skin_mode():
        current_skin = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_skin == "Dark" else "Dark")

    btn_lock = ctk.CTkButton(base, text="Lock Radio Switch", command=toggle_radio_lock)
    btn_lock.pack(pady=5)

    btn_theme = ctk.CTkButton(base, text="Simulate Global Theme Shift", command=toggle_skin_mode)
    btn_theme.pack(side="bottom", pady=10)

    root.mainloop()
```

[Return to Table of Contents](#contents)
