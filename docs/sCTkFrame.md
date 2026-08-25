## sCTkFrame

### Table of Contents
* [API Property Reference](#api-property-reference)
* [Constructor](#constructor)
* [Centralized Stylesheet Setup](#centralized-stylesheet-setup-sctkthemesjson)
* [Other Notes](#other-notes)
* [Implementation Example & Test Harness](#implementation-example--test-harness)

---

A clean, theme-compliant standard backplane container layout chassis widget. It functions as the geometric foundation card for stacking controls, isolating interface subsections, and grouping multi-frequency layout grids.

### API Property Reference

| Property / Feature | Standard CustomTkinter | Your `sCustomTkinter` Setup |
| :--- | :--- | :--- |
| **Instantiation** | `ctk.CTkFrame(master)` | `sCTkFrame(master)` *(Backplane Container Chassis)* |
| **File Mapping** | Everything runs under one core native framework layout tracker. | Streamlined and compiled programmatically across `sCTkFrame.py` and `ThemeableWidget.py`. |
| **State Lock** | *Not Supported Natively* | `base_container.state("disabled")`<br>**OR**<br>`base_container.configure(state="disabled")`<br><br>**Dual-Routing State Bypasser:** Absorbs state parameters smoothly without crashing. This prevents interface layout exceptions when cascading operational locks down across complex structural grids. |
| `get_state()` | *Not Supported Natively* | `Method -> str` explicit verification query matching system test assertions, always returning `"normal"`. |

---

### Constructor

Initialize a custom backplane container frame card instance. High-level custom configuration parameters passed by Pygubu (like `translator`, `on_first_object_cb`, `image_loader`, and `data_pool`) are automatically intercepted, processed, and purged early by the `ThemeableWidget` mixin layer before the native constructor fires. Geometry shapes, border offsets, and corner styles map cleanly out of central stylesheet parameters.

```python
# Instantiate a master panel frame container card layout
dashboard_card = sCTkFrame(
    master=root_window,
    border_width=2
)

# Render the container frame widget inside your view using geometry packers
dashboard_card.pack(expand=True, fill="both", padx=25, pady=25)
```

---

### Centralized Stylesheet Setup (`sCTkThemes.json`)
```json
{
    "sCTkFrame": {
        "fg_color": ["#F8FAFC", "#1E293B"],
        "border_color": ["#E2E8F0", "#334155"],
        "border_width": 1,
        "corner_radius": 8
    }
}
```

### Other notes
* **Bypassing the BaseUI Middleman:** This component inherits cleanly and directly from `ctk.CTkFrame` and `ThemeableWidget`, bypassing the intermediate template layout files entirely. It connects the component straight to CustomTkinter's appearance modes while using the multiple inheritance protocol layer to sanitize keyword arrays.
* **Automated Lifecycle Handshake:** At the absolute bottom of the initialization routine, the constructor fires `self._finalize_themeable_lifecycle()` to safely dispatch first-object registration notifications back up to Pygubu's master parent script controllers, unlocking full composition support.
* **Deep-Copy Dictionary Isolation Shield:** Because CustomTkinter's native container initialization loops mutate and delete attributes directly out of raw dictionary data footprints during its boot pass, the constructor clones your configurations into `self._local_defaults = dict(self.final_kw)` beforehand. This preserves your color mappings safely.
* **Passive Operation Parity:** Background chassis containers do not implement a variable `disabled_map`. They remain perpetually active (`"normal"`) to allow child inputs sitting on top of their canvas face to handle their own active drawing states independently.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkFrame` asset container along with a cascading lock simulation pass.

```python
#!/usr/bin/python3
"""
sCTkFrame - Standalone Interactive Testing Harness
"""
import customtkinter as ctk

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
import sCTkThemes                # 🔍 Duplicate import kept close for script scannability
from sCTkFrame import sCTkFrame  # Testing application wrapper container frame

if __name__ == "__main__":
    # Natively resolves your package assets and populates configurations cleanly
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("450x300")
    root.title("sCTkFrame Container Validation Bench")

    # Instantiate your custom theme-compliant frame element chassis
    base_container = sCTkFrame(root, border_width=2)
    base_container.pack(expand=True, fill="both", padx=30, pady=30)

    # Add a simple sub-element child widget to verify structural clipping layouts
    lbl_marker = ctk.CTkLabel(base_container, text="FRAME BACKPLANE CONTAINER OPERATIONAL")
    lbl_marker.pack(expand=True)

    def toggle_panel_lock():
        """Toggles the helper input field between normal active and dimmed disabled profiles."""
        current_mode = base_container.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        
        # Explicitly testing the dual-routing capability via configure()
        base_container.configure(state=target)
        print(f"Logged Verification Hook -> base_container.get_state() = {base_container.get_state()}")

    btn_lock = ctk.CTkButton(root, text="Simulate Cascading Interface Lock", command=toggle_panel_lock)
    btn_lock.pack(side="bottom", pady=15)

    # Run the interactive boot tracking logs
    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    base_container.state("disabled")
    print("state (Disabled Pass) =", base_container.get_state())  # Output: normal (Frames bypass disabled masks)

    base_container.state("normal")
    print("state (Normal Pass)   =", base_container.get_state())  # Output: normal
    print("========================================\n")

    root.mainloop()
```

[Return to Table of Contents](#contents)
