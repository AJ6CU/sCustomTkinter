## sCTkButtonSecondary

A specialized, theme-compliant secondary button component widget variant wrapping `customtkinter.CTkButton` designed to act as a latching status toggle selector. It implements a deep-copy keyword caching shield to preserve custom visual style parameters from native mutation traps and prevent `NoneType` canvas validation exceptions.

### API Property Reference

| Property / Feature | Standard CustomTkinter | Your `sCustomTkinter` Setup |
| :--- | :--- | :--- |
| **Instantiation** | `ctk.CTkButton(master)` | `sCTkButtonSecondary(master)` *(Latching Toggle Selector)* |
| **File Mapping** | Component definitions bundle under single active tracks. | Streamlined and compiled programmatically across `sCTkButtonSecondary.py` and `ThemeableWidget.py`. |
| `state(mode)` | `self.configure(state=...)` | `Method (str)` managing layout tracking maps and toggling active canvas event binds natively. |
| `get_state()` | `self.cget("state")` | `Method -> str` explicit verification query matching system test assertions. |
| `set_pressed(bool)` | *Not Available Natively* | **Latching Hook:** Dynamically updates visual button states to look locked down. |

---

### Constructor

Initialize a custom secondary latching toggle button instance. Custom parameters passed from Pygubu builder allocations (like string `translator` tracks or `data_pool` environments) are automatically intercepted, processed, and purged early by the `ThemeableWidget` mixin layer before the native constructor fires.

```python
# Instantiate a secondary latching toggle button element
vfo_lock_toggle = sCTkButtonSecondary(
    master=control_panel,
    text="LOCK ACTIVE VFO MODE",
    command=on_vfo_lock_toggled
)

# Render the widget inside your parent container geometry tracker layout
vfo_lock_toggle.pack(fill="x", padx=40, pady=10)
```

---

### Convenience Functions
```python
# Force an active button press visual accent highlight on the fly
vfo_lock_toggle.set_pressed(True)   # Shifts colors to match your pressed_map rules

# Evaluate active visual modes or apply absolute user interaction locks
current_mode = vfo_lock_toggle.get_state() # Returns 'normal' or 'disabled'
vfo_lock_toggle.state("disabled")          # Unbinds mouse canvas routines and applies muted gray fills
```

### Centralized Stylesheet Setup (`sCTkThemes.json`)
```json
{
    "sCTkButtonSecondary": {
        "fg_color": "transparent",
        "border_color": ["#CBD5E1", "#44403C"],
        "text_color": ["#334155", "#E7E5E4"],
        "border_width": 1,
        "corner_radius": 6,
        "disabled_map": {
            "fg_color": ["#F1F5F9", "#171412"],
            "border_color": ["#E2E8F0", "#292524"],
            "text_color": ["#94A3B8", "#57534E"]
        },
        "pressed_map": {
            "fg_color": ["#E2E8F0", "#44403C"],
            "border_color": ["#94A3B8", "#6B7280"],
            "text_color": ["#000000", "#FFFFFF"]
        }
    }
}
```

### Other notes
* **Bypassing the BaseUI Skeletons:** This component inherits cleanly and directly from native CustomTkinter classes and `ThemeableWidget`, completely bypassing the intermediate template layout files entirely to preserve high-DPI image scaling.
* **Canvas Interaction Toggles:** When shifted into a `disabled` state configuration, the widget explicitly unbinds mouse events (`<Enter>`, `<Leave>`, `<Button-1>`) at the canvas level to lock interactions and prevent memory leaks. Shifting back to `normal` restores the listeners seamlessly.
* **Automated Lifecycle Handshake:** At the absolute bottom of the initialization track, the constructor triggers `self._finalize_themeable_lifecycle()` to safely notify top-level Pygubu container managers that the widget is compiled.

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkButtonSecondary` alongside an interactive latch controller.

```python
#!/usr/bin/python3
"""
sCTkButtonSecondary - Standalone Interactive Testing Harness
"""
import customtkinter as ctk
import sCTkThemes
from sCTkFrame import sCTkFrame
from sCTkButtonSecondary import sCTkButtonSecondary

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()
    root = ctk.CTk()
    root.geometry("400x200")
    root.title("Secondary Toggle Button Telemetry Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    widget = sCTkButtonSecondary(base, text="System Action Button")
    widget1 = sCTkButtonSecondary(base, text="Latching Preset Toggle")

    widget.pack(padx=40, pady=20)
    widget1.pack(padx=40, pady=20)

    widget.state("normal")
    widget1.set_pressed(True)

    widget.state("disabled")
    print("--- DISABLED PASS ---")
    print("Widget 0 state =", widget.get_state())
    print("Widget 1 state =", widget1.get_state())

    widget.state("normal")
    print("\n--- NORMAL PASS ---")
    print("Widget 0 state =", widget.get_state())
    print("Widget 1 state =", widget1.get_state())
    print("\n=== SYSTEM ONLINE: SECONDARY BUTTON INTERACTION ACTIVE ===\n")

    widget.configure(command=lambda: [print("System Action Button Clicked"), widget.set_pressed(not widget.is_pressed)])
    widget1.configure(command=lambda: [print("Testpressed Button Clicked"), widget1.set_pressed(not widget1.is_pressed)])

    root.mainloop()
```

[Return to Table of Contents](#contents)
