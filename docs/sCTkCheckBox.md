## sCTkCheckBox

### Table of Contents
* [API Property Reference](#api-property-reference)
* [Constructor](#constructor)
* [Convenience Functions](#convenience-functions)
* [Centralized Stylesheet Setup](#centralized-stylesheet-setup-sctkthemesjson)
* [Other Notes](#other-notes)
* [Implementation Example & Test Harness](#implementation-example--test-harness)

---

A specialized, theme-compliant checkbox element component variant designed for binary option selections, telemetry locks, and parameter configurations. It integrates an independent deep-copy keyword caching shield and clean programmatic inheritance to preserve checkbox configurations without intermediate file middlemen.

### API Property Reference

| Property / Feature | Standard CustomTkinter | Your `sCustomTkinter` Setup |
| :--- | :--- | :--- |
| **Instantiation** | `ctk.CTkCheckBox(master)` | `sCTkCheckBox(master)` *(Binary Option Selector)* |
| **File Mapping** | Everything runs under a single active component module. | Streamlined and compiled programmatically across `sCTkCheckBox.py` and `ThemeableWidget.py`. |
| `state(mode)` | `self.configure(state=...)` | `Method (str)` handling layout tracking map transformations (`'normal'`, `'disabled'`) via sequential update passes. |
| `get_state()` | `self.cget("state")` | `Method -> str` explicit verification query matching system test assertions. |
| `get()` | `self.get()` | Returns `1` if selected, or `0` if empty. |
| `select()` / `deselect()` | Native methods | Forces check marks on or off programmatically. |

---

### Constructor

Initialize a custom checkbox option instance. Pygubu parameters (such as `translator` or `on_first_object_cb`) are stripped, isolated, and safely processed early by the `ThemeableWidget` mixin layer before the native constructor fires.

```python
# Instantiate a primary option selection checkbox
logging_toggle = sCTkCheckBox(
    master=control_panel,
    text="ENABLE LOGGING FRAMEWORK",
    command=on_logging_selection_changed
)

# Render the widget inside your parent container geometry tracker panel
logging_toggle.pack(padx=20, pady=10)
```

---

### Convenience Functions
```python
# Programmatically alter choices or evaluate state configurations on the fly
is_active = logging_toggle.get()          # Returns 1 (checked) or 0 (unchecked)
logging_toggle.select()                    # Forces the checkmark button state to fill inside the box
logging_toggle.state("disabled")           # Disables checking interaction and applies muted gray fills
```

### Centralized Stylesheet Setup (`sCTkThemes.json`)
```json
{
    "sCTkCheckBox": {
        "fg_color": ["#1A4375", "#1F6AA5"],
        "border_color": ["#94A3B8", "#4B5563"],
        "text_color": ["#111827", "#F9FAFB"],
        "checkmark_color": ["#FFFFFF", "#FFFFFF"],
        "border_width": 2,
        "corner_radius": 4,
        "disabled_map": {
            "fg_color": ["#E5E7EB", "#374151"],
            "border_color": ["#CBD5E1", "#4B5563"],
            "text_color": ["#94A3B8", "#64748B"],
            "checkmark_color": ["#94A3B8", "#4B5563"]
        }
    }
}
```

### Other notes
* **Bypassing the BaseUI Middleman:** Completely removes transitional `baseui` template classes, mapping directly to `ctk.CTkCheckBox` and `ThemeableWidget` multiple inheritance pathways to avoid signature collisions.
* **Automated Lifecycle Handshake:** Triggers `self._finalize_themeable_lifecycle()` at the absolute bottom of the initialization track to safely register instances with Pygubu layout trees out of the box.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkCheckBox` alongside an interactive theme state track.

```python
#!/usr/bin/python3
"""
sCTkCheckBox - Standalone Interactive Testing Harness
"""
import customtkinter as ctk
import sCTkThemes                
from sCTkFrame import sCTkFrame  
from sCTkCheckBox import sCTkCheckBox

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("450x300")
    root.title("Checkbox Interaction Telemetry Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    # Instantiate your custom theme-compliant checkbox element
    widget = sCTkCheckBox(base, text="Enable Logging Framework")
    widget.configure(command=lambda: print("Checked" if widget.get() == 1 else "Unchecked"))
    widget.pack(expand=True, fill="none", padx=10, pady=10)

    # THE OPERATION STATE TOGGLE BUTTON TRACK:
    def toggle_widget_state():
        current_mode = widget.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        
        widget.configure(state=target)
        btn_toggle.configure(
            text="Unlock Checkbox" if target == "disabled" else "Lock Checkbox (Set 'disabled')"
        )
        print(f"Logged Verification Hook -> widget.get_state() = {widget.get_state()}")

    btn_toggle = ctk.CTkButton(base, text="Lock Checkbox (Set 'disabled')", command=toggle_widget_state)
    btn_toggle.pack(side="bottom", pady=15)

    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    widget.state("disabled")
    print("state (Disabled Pass) =", widget.get_state())  

    widget.state("normal")
    print("state (Normal Pass)   =", widget.get_state())  
    print("========================================\n")

    root.mainloop()
```

[Return to Table of Contents](#contents)
