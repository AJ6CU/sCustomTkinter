## sCTkOptionMenuSecondary

### Table of Contents
* [API Property Reference](#api-property-reference)
* [Constructor](#constructor)
* [Convenience Functions](#convenience-functions)
* [Centralized Stylesheet Setup](#centralized-stylesheet-setup-themesjson)
* [Other Notes](#other-notes)
* [Implementation Example & Test Harness](#implementation-example--test-harness)

---

The auxiliary secondary option menu drop-down selector widget component variant wrapping a composite `ctk.CTkFrame` chassis encasing an inner text selector. It is tailored specifically for sub-metadata channels, filter widths, or tuning resolution parameters.

*For dominant form drop-downs or principal system mode choices, see the master component documentation page:* [sCTkOptionMenuPrimary](sCTkOptionMenuPrimary.md).

### API Property Reference

| Property / Feature | Standard CustomTkinter | Your `sCustomTkinter` Setup |
| :--- | :--- | :--- |
| **Instantiation** | `ctk.CTkOptionMenu(master)` | `sCTkOptionMenuSecondary(master)` *(Secondary Helper Dropdown)* |
| **File Mapping** | Component settings span single un-managed file layouts. | Separated safely across `sCTkOptionMenuSecondary.py` and `ThemeableWidget.py`. |
| **State Lock** | `self.configure(state="disabled")` | `widget.state("disabled")`<br>**OR**<br>`widget.configure(state="disabled")`<br><br>**Dual-Routing State Pipeline:** Natively intercepts state updates. Locks both the base frame container layer and the interior dropdown menu elements securely to mask interactive hover events out of `disabled_map` guidelines. |
| `get_state()` | `self.cget("state")` | `Method -> str` explicit verification query matching system test assertions. |

---

### Constructor

Initialize a custom secondary drop-down helper option menu instance. Keywords that cause collision errors with native container borders are filtered dynamically beforehand.

```python
# Instantiate an auxiliary DSP filter bandwidth selection drop-down menu
filter_dropdown = sCTkOptionMenuSecondary(
    master=control_panel,
    values=["Filter: Narrow", "Filter: Medium", "Filter: Wide"],
    command=on_filter_width_changed
)

# Render the widget inside your parent layout frame panel
filter_dropdown.pack(fill="x", padx=40, pady=10)
```
### Convenience Functions
```python
# Programmatically manipulate selection items or fetch choice parameters
filter_dropdown.set("Filter: Narrow")      # Forces the visible dropdown face to display a specific option text
active_filter = filter_dropdown.get()       # Returns the active string variable currently selected
filter_dropdown.update_list(["A", "B"])     # Replaces choice index items safely while protecting bounds

# Evaluate current state configurations or apply absolute user interaction locks via dual-routing syntax
current_mode = filter_dropdown.get_state()  # Returns 'normal' or 'disabled'
filter_dropdown.state("disabled")           # Freezes selection paths and applies muted flat gray skins
```

### Centralized Stylesheet Setup (`themes.json`)
```json
{
    "sCTkOptionMenuSecondary": {
        "fg_color": ["#FAFAFA", "#11141A"],
        "border_color": ["#CBD5E1", "#222933"],
        "border_width": 1,
        "corner_radius": 6,
        "text_color": ["#475569", "#94A3B8"],
        "font": ["Arial", 11],
        "disabled_map": {
            "fg_color": ["#F1F5F9", "#0A0D14"],
            "border_color": ["#E2E8F0", "#171C24"],
            "text_color": ["#94A3B8", "#4B5563"]
        }
    }
}
```

---

### Other Notes
* **Inversion Blacklist Filter Shield:** Because this widget is a compound object utilizing an underlying `CTkFrame` container, passing core text parameters (like `font` or `text_color`) straight into the initialization tree causes a fatal `ValueError` crash. The constructor parses and pulls these tokens beforehand, feeding them explicitly down to the nested dropdown item instead.
* **Deep-Copy Dictionary Isolation Shield:** Because CustomTkinter's native option menu initialization code mutates, strips, and deletes keys directly out of raw dictionary data footprints during its boot phase, the constructor clones your configurations into `self._local_defaults = dict(self.final_kw)` beforehand. This prevents normal state restorations from crashing on missing keys.
* **Real-Time Repaint Loop:** The internal core engine is fortified to run color tuple lookups dynamically across both normal and locked state selections. This forces the secondary option menu dropdown faces, text fonts, and outer chassis frame layouts to adapt fluidly to theme skin toggle commands without white-out freezes.
* **Automated Lifecycle Handshake:** At the absolute bottom of the initialization routine, the constructor fires `self._finalize_themeable_lifecycle()` to safely notify top-level Pygubu container managers that the widget is compiled.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkOptionMenuSecondary` dropdown helper while actively reporting choice changes onto a secondary telemetry label and supporting light/dark switches.

```python
#!/usr/bin/python3
"""
sCTkOptionMenuSecondary - Standalone Interactive Testing Harness
"""
import customtkinter as ctk

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
import sCTkThemes                    
from sCTkFrame import sCTkFrame      
from sCTkLabelSecondary import sCTkLabelSecondary
from sCTkOptionMenuSecondary import sCTkOptionMenuSecondary

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("450x320")
    root.title("sCTkOptionMenuSecondary Real-Time Validation Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    # Telemetry reporting label updates live on interaction changes
    lbl_monitor = sCTkLabelSecondary(base, text="Active Selection: Filter: Narrow")
    lbl_monitor.pack(pady=10)

    # Instantiate your custom drop-down menu helper element chassis
    menu_field = sCTkOptionMenuSecondary(
        base,
        values=["Filter: Narrow", "Filter: Medium", "Filter: Wide"],
        command=lambda choice: lbl_monitor.configure(text=f"Active Selection: {choice}")
    )
    menu_field.pack(expand=False, fill="x", padx=40, pady=10)
    menu_field.set("Filter: Narrow")

    def toggle_operational_state():
        """Toggles the option menu between normal active and dimmed disabled profiles."""
        current_mode = menu_field.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        menu_field.configure(state=target)
        btn_toggle.configure(text="Lock Dropdown (Set 'disabled')" if target == "normal" else "Unlock Dropdown (Set 'normal')")

    def toggle_skin_mode():
        current_skin = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_skin == "Dark" else "Dark")

    btn_toggle = ctk.CTkButton(base, text="Lock Dropdown (Set 'disabled')", command=toggle_operational_state)
    btn_toggle.pack(side="bottom", pady=5)

    btn_theme = ctk.CTkButton(base, text="Simulate Global Theme Shift", command=toggle_skin_mode)
    btn_theme.pack(side="bottom", pady=5)

    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    menu_field.state("disabled")
    print("state (Disabled Pass) =", menu_field.get_state())  

    menu_field.state("normal")
    print("state (Normal Pass)   =", menu_field.get_state())  
    print("========================================\n")

    root.mainloop()
```

[Return to Table of Contents](#contents)
