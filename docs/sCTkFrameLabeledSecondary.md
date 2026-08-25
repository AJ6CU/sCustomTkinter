## sCTkLabelSecondary

### Table of Contents
* [API Property Reference](#api-property-reference)
* [Constructor](#constructor)
* [Centralized Stylesheet Setup](#centralized-stylesheet-setup-sctkthemesjson)
* [Other Notes](#other-notes)
* [Implementation Example & Test Harness](#implementation-example--test-harness)

---

The custom secondary interface typography display label widget component wrapping `customtkinter.CTkLabel`. It features an independent deep-copy keyword caching shield and an advanced multi-state color-dimming interceptor to automatically shift text contrasts when subsystem components enter disabled sequences.

### API Property Reference

| Property / Feature | Standard CustomTkinter | Your `sCustomTkinter` Setup |
| :--- | :--- | :--- |
| **Instantiation** | `ctk.CTkLabel(master)` | `sCTkLabelSecondary(master)` *(Secondary Interface Text Label)* |
| **File Mapping** | Direct module definitions run without structured configuration. | Streamlined and compiled programmatically across `sCTkLabelSecondary.py` and `ThemeableWidget.py`. |
| **State Lock** | *Not Supported Natively* | `secondary_label.state("disabled")`<br>**OR**<br>`secondary_label.configure(state="disabled")`<br><br>**Framework-Wide State Support:** Natively supported across all label components (`Primary`, `Secondary`, `Tertiary`). It intercepts state configuration calls and dynamically dims typography layouts based on centralized `disabled_map` metrics. |
| `get_state()` | *Not Supported Natively* | `Method -> str` explicit verification query matching system test assertions. |

---

### Constructor

Initialize a custom secondary text label instance. Configuration metrics map cleanly out of central stylesheet parameters and are automatically sanitized by the `ThemeableWidget` mixin layer before the native constructor fires.

```python
# Instantiate a secondary user interface text display label element
lane_label = sCTkLabelSecondary(
    master=control_panel,
    text="Active Teleceiver Signal Frequency Lane [94.1 MHz]"
)

# Render the widget inside your layout panel using geometry managers
lane_label.pack(expand=True, padx=20, pady=20)
```
### Centralized Stylesheet Setup (`sCTkThemes.json`)
```json
{
    "sCTkLabelSecondary": {
        "fg_color": "transparent",
        "text_color": ["#475569", "#94A3B8"],
        "font": ["Arial", 11, "bold"],
        "disabled_map": {
            "text_color": ["#CBD5E1", "#4B5563"]
        }
    }
}
```

---

### Other Notes
* **Bypassing the BaseUI Middleman:** This component inherits cleanly and directly from native CustomTkinter classes and `ThemeableWidget`, completely bypassing the intermediate template layout files entirely to avoid argument deadlocks and preserve image scaling properties.
* **Deep-Copy Dictionary Isolation Shield:** Because CustomTkinter's native geometry constructor routines mutate and drop keys directly out of parsed configuration structures during early boot phases, the constructor clones your data configurations into `self._local_defaults = dict(self.final_kw)` beforehand. This prevents layout repaints from failing.
* **Dynamic Dark Mode Pass-Through:** When returning to an active state, the visual interceptor reads directly from your protected `_local_defaults` cache. If no hardcoded text color is explicitly discovered, it hands control back to CustomTkinter's master `ThemeManager` to natively paint high-contrast system fonts.
* **Automated Lifecycle Handshake:** Triggers `self._finalize_themeable_lifecycle()` at the absolute bottom of the initialization track to cleanly pass instance registration hooks straight back up to Pygubu parent controllers.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkLabelSecondary` component element along with an interactive status switch toggle.

```python
#!/usr/bin/python3
"""
sCTkLabelSecondary - Standalone Interactive Testing Harness
"""

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
import customtkinter as ctk
import sCTkThemes
from sCTkFrame import sCTkFrame
from sCTkLabelSecondary import sCTkLabelSecondary

if __name__ == "__main__":
    # Natively resolves your package assets and populates configurations cleanly
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("450x240")
    root.title("sCTkLabelSecondary Testing Deck")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    # Instantiate your custom text component cell
    widget = sCTkLabelSecondary(base, text="Active Teleceiver Signal Frequency Lane [94.1 MHz]")
    widget.pack(expand=True, padx=20, pady=20)

    def toggle_operational_state():
        current_mode = widget.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        widget.configure(state=target)
        btn_toggle.configure(text="Lock Label Text" if target == "normal" else "Unlock Label Text")

    def toggle_appearance_skin():
        current_mode = ctk.get_appearance_mode()
        target = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(target)

    btn_theme = ctk.CTkButton(base, text="Toggle Skin Mode (Dark / Light)", command=toggle_appearance_skin)
    btn_theme.pack(side="bottom", pady=(5, 5))

    btn_toggle = ctk.CTkButton(base, text="Lock Label Text", command=toggle_operational_state)
    btn_toggle.pack(side="bottom", pady=(10, 5))

    root.mainloop()
```

[Return to Table of Contents](#contents)
