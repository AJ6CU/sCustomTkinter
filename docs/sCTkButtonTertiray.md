## sCTkButtonTertiary

An outline-driven custom toggle variant button widget component styled specifically for sub-presets, tuning markers, and option lock keys wrapping `customtkinter.CTkButton`. It utilizes an independent deep-copy keyword caching shield and a dynamic runtime accent fallback detector to align button typography with CustomTkinter system configurations automatically.

### API Property Reference

| Property / Feature | Standard CustomTkinter | Your `sCustomTkinter` Setup |
| :--- | :--- | :--- |
| **Instantiation** | `ctk.CTkButton(master)` | `sCTkButtonTertiary(master)` *(Outline Latching Button)* |
| **File Mapping** | Everything runs under one core native framework layout layer. | Streamlined and compiled programmatically across `sCTkButtonTertiary.py` and `ThemeableWidget.py`. |
| `state(mode)` | `self.configure(state=...)` | `Method (str)` handling layout tracking map transformations (`'normal'`, `'disabled'`) and canvas unbindings. |
| `get_state()` | `self.cget("state")` | `Method -> str` explicit verification query matching system test assertions. |
| `set_pressed(bool)` | *Not Available Natively* | **Latching Hook:** Locks background contrast styles to match `pressed_map` guidelines. |

---

### Constructor

Initialize a custom tertiary button instance. Custom parameters passed from Pygubu (like `translator`, `on_first_object_cb`, `image_loader`, and `data_pool`) are automatically intercepted, processed, and purged early by the `ThemeableWidget` mixin layer before the native constructor fires. If no explicit `text_color` parameters are discovered inside `sCTkThemes.json`, the constructor queries CustomTkinter's baseline colors (`["#3B8ED0", "#1F6AA5"]`) automatically to preserve unified system highlights.

```python
# Instantiate a tertiary outline latching button
preset_select = sCTkButtonTertiary(
    master=control_panel,
    text="PRESET CHANNEL A",
    command=on_preset_selected
)

# Render the widget inside your parent container geometry packer panel
preset_select.pack(fill="x", padx=40, pady=10)
```

---

### Centralized Stylesheet Setup (`sCTkThemes.json`)
```json
{
    "sCTkButtonTertiary": {
        "fg_color": "transparent",
        "border_color": ["#3B8ED0", "#1F6AA5"],
        "text_color": null,
        "border_width": 1,
        "corner_radius": 4,
        "disabled_map": {
            "fg_color": "transparent",
            "border_color": ["#CBD5E1", "#374151"],
            "text_color": ["#94A3B8", "#64748B"]
        },
        "pressed_map": {
            "fg_color": ["#3B8ED0", "#1F6AA5"],
            "border_color": ["#3B8ED0", "#1F6AA5"],
            "text_color": ["#FFFFFF", "#FFFFFF"]
        }
    }
}
```

### Other Notes
* **Bypassing the BaseUI Middleman:** This component inherits cleanly and directly from native CustomTkinter classes and `ThemeableWidget`, bypassing the intermediate template layout files entirely to avoid signature collisions.
* **Automated Lifecycle Handshake:** At the absolute bottom of the initialization track, the constructor triggers `self._finalize_themeable_lifecycle()` to safely notify top-level Pygubu container managers that the widget is compiled.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkButtonTertiary` alongside latching switches.

```python
#!/usr/bin/python3
"""
sCTkButtonTertiary - Standalone Interactive Testing Harness
"""
import customtkinter as ctk
import sCTkThemes                
from sCTkFrame import sCTkFrame  
from sCTkButtonTertiary import sCTkButtonTertiary

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("450x300")
    root.title("Tertiary Outline Button Telemetry Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    widget1 = sCTkButtonTertiary(base)
    widget = sCTkButtonTertiary(base)

    widget1.configure(
        text="Latching Preset Toggle",
        command=lambda: [
            widget1.set_pressed(not widget1.is_pressed),
            print(f"Logged Verification Hook -> widget1.is_pressed = {widget1.is_pressed}")
        ]
    )

    widget.configure(
        text="System Action",
        command=lambda: print("System Action Clicked")
    )

    widget.pack(expand=False, fill="none", padx=40, pady=10)
    widget1.pack(expand=False, fill="none", padx=40, pady=10)

    # Standard test assertions routine verification sequences
    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    widget.state("disabled")
    print("widget (Disabled Pass) =", widget.get_state())

    widget.state("normal")
    print("widget (Normal Pass)   =", widget.get_state())
    print("========================================\n")

    root.mainloop()
```

[Return to Table of Contents](#contents)
