# sCTkSegmentedButton

A custom, theme-compliant segmented button strip tracker widget designed for hardware-inspired radio control panel layouts. Inherits directly from `customtkinter.CTkSegmentedButton` and implements the `ThemeableWidget` mixin framework, enabling total alignment with centralized stylesheet configurations.

## 🛠️ Architectural Design Features

*   **Zero-Gap Contiguous Bar:** Bypasses CustomTkinter's native button spacing layout by programmatically flattening horizontal paddings down to absolute zero. Every tab segment welds tightly flush next to each other inside a single continuous capsule pill track profile.
*   **Dynamic High-Contrast Legibility:** Forcefully overrides child element text layers dynamically on click events. This ensures the active choice badge maintains crisp pure white lettering over deep accent container fills, while adjacent unselected choices cleanly snap back to your rested dark gray or blue typography targets.
*   **Pygubu Constructor Handshake Protection:** Implements an internal initialization shield gate that catches post-boot `.configure(state='disabled')` assignments passed down from Pygubu form layout engines before sub-button structures have completed generation. This prevents `AttributeError` freezes on initial application startup loops.
*   **Virtual Lock Dimming Engine:** Integrates operational mode state switches straight down to your look dictionaries. Toggling the component to a disabled track automatically applies cohesive, muted, desaturated industrial gray tones over the capsule chasses natively.

---

## 🎨 Centralized Stylesheet Setup (`sCTkThemes.json`)

To drive the dual-blue layout metrics and clear-contrast typography text shifts accurately across both look preference sweeps, ensure your centralized theme profile file includes this exact element block:

```json
{
    "sCTkSegmentedButton": {
        "fg_color": ["#4F75A2", "#2B4C7E"],
        "selected_color": ["#1A4375", "#3A6FA2"],
        "selected_hover_color": ["#112A4B", "#2B5885"],
        "unselected_color": "transparent",
        "unselected_hover_color": ["#3A5C85", "#3A5F8C"],
        "text_color": ["#FFFFFF", "#FFFFFF"],
        "text_color_disabled": ["#94A3B8", "#64748B"],
        "disabled_map": {
            "fg_color": ["#B2B9BC", "#222527"],
            "selected_color": ["#70777B", "#45494D"],
            "selected_hover_color": ["#70777B", "#45494D"],
            "unselected_color": "transparent",
            "unselected_hover_color": "transparent"
        }
    }
}
```

---

## ⚙️ Public API Methods Reference

| Method Name | Arguments | Return Type | Description |
| :--- | :--- | :--- | :--- |
| `state(mode)` | `mode: str (Optional)` | `str` | Dedicated operational state controller. If empty, returns the current active state (`'normal'` or `'disabled'`). If passed, triggers a look cascade pass. |
| `get_state()` | `None` | `str` | Explicit state tracking query synchronized with framework validation benchmarks. |
| `set(value)` | `value: str` | `None` | Programmatic value tracking setter. Updates the active button highlight and instantly swaps text colors across the live segment matrix. |
| `cget(attribute)` | `attribute: str` | `Any` | Intercept shield layer that safely bridges requests for the `'state'` string parameter out of underlying tkinter dictionaries. |

---

## 💻 Implementation Code Template

```python
import customtkinter as ctk
import sCTkThemes
from sCTkFrame import sCTkFrame
from sCTkSegmentedButton import sCTkSegmentedButton

# 1. Initialize global theme definitions
sCTkThemes.apply_sCTkThemes()

root = ctk.CTk()
root.geometry("500x200")

# 2. Build parent layout track frame
base = sCTkFrame(root)
base.pack(expand=True, fill="both", padx=20, pady=20)

# 3. Instantiate the clean subclass row-segments widget
widget = sCTkSegmentedButton(base, values=["VFO-A", "VFO-B", "MEM-BANK", "SPLIT"])
widget.pack(expand=False, fill="none", padx=10, pady=10)
widget.set("VFO-A")

# 4. Optional: Force dynamic operational locks programmatically
# widget.state("disabled")

root.mainloop()
```
