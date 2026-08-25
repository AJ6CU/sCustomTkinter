## sCTkLabelTertiary

### Table of Contents
* [API Property Reference](#api-property-reference)
* [Constructor](#constructor)
* [Centralized Stylesheet Setup](#centralized-stylesheet-setup-sctkthemesjson)
* [Other Notes](#other-notes)
* [Implementation Example & Test Harness](#implementation-example--test-harness)

---

The fine inline description, sub-legend, or auxiliary notice typography display label widget component wrapping `customtkinter.CTkLabel`. It features an independent deep-copy keyword caching shield and an advanced multi-state color-dimming interceptor to automatically shift text contrasts when subsystem components enter disabled sequences.

*For prominent main dashboard header and mid-level sections, see the companion component pages:* [sCTkLabelPrimary](sCTkLabelPrimary.md) and [sCTkLabelSecondary](sCTkLabelSecondary.md).

### API Property Reference

| Property / Feature | Standard CustomTkinter | Your `sCustomTkinter` Setup |
| :--- | :--- | :--- |
| **Instantiation** | `ctk.CTkLabel(master)` | `sCTkLabelTertiary(master)` *(Inline Legend/Description Typography)* |
| **File Mapping** | Direct module definitions run without structured configuration. | Streamlined and compiled programmatically across `sCTkLabelTertiary.py` and `ThemeableWidget.py`. |
| **State Lock** | *Not Supported Natively* | `tertiary_label.state("disabled")`<br>**OR**<br>`tertiary_label.configure(state="disabled")`<br><br>**Framework-Wide State Support:** Natively supported across all label components (`Primary`, `Secondary`, `Tertiary`). It intercepts state configuration calls and dynamically dims typography layouts based on centralized `disabled_map` metrics. |
| `get_state()` | *Not Supported Natively* | `Method -> str` explicit verification query matching system test assertions. |

---

### Constructor

Initialize a custom tertiary description label instance. Configuration metrics map cleanly out of central stylesheet parameters and are automatically sanitized by the `ThemeableWidget` mixin layer before the native constructor fires.

```python
# Instantiate a tertiary description dashboard label element
panel_legend = sCTkLabelTertiary(
    master=control_panel,
    text="Inline notice: tuning resolution bounded to 100Hz."
)

# Render the widget inside your layout panel using geometry managers
panel_legend.pack(expand=True, pady=10)
```
### Centralized Stylesheet Setup (`sCTkThemes.json`)
```json
{
    "sCTkLabelTertiary": {
        "fg_color": "transparent",
        "text_color": ["#64748B", "#94A3B8"],
        "font": ["Arial", 10, "italic"],
        "disabled_map": {
            "text_color": ["#CBD5E1", "#334155"]
        }
    }
}
```

---

### Other Notes
* **Deep-Copy Dictionary Isolation Shield:** Because CustomTkinter's native geometry constructor routines mutate and drop keys directly out of parsed configuration structures during early boot phases, the constructor clones your data configurations into `self._local_defaults = dict(self.final_kw)` beforehand. This prevents layout repaints from failing.
* **Dynamic Dark Mode Pass-Through:** When returning to an active state, the visual interceptor reads directly from your protected `_local_defaults` cache. If no hardcoded text color is explicitly discovered, it hands control back to CustomTkinter's master `ThemeManager` to natively paint high-contrast system fonts.
* **Automated Lifecycle Handshake:** Triggers `self._finalize_themeable_lifecycle()` at the absolute bottom of the initialization track to cleanly pass instance registration hooks straight back up to Pygubu parent controllers.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkLabelTertiary` inline legend element along with an interactive status switch toggle.

```python
#!/usr/bin/python3
"""
sCTkLabelTertiary - Standalone Interactive Testing Harness
"""
import customtkinter as ctk

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
import sCTkThemes
from sCTkFrame import sCTkFrame
from sCTkLabelTertiary import sCTkLabelTertiary

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("450x280")
    root.title("sCTkLabelTertiary Testing Deck")

    # Layout a clean, padded workspace container frame panel
    container = sCTkFrame(root, fg_color="transparent")
    container.pack(expand=True, fill="both", padx=30, pady=30)

    # Instantiate your custom tertiary description label widget
    tertiary_label = sCTkLabelTertiary(container, text="Inline notice: tuning resolution bounded to 100Hz.")
    tertiary_label.pack(expand=True, pady=10)

    # Live state monitoring feedback label
    lbl_status = ctk.CTkLabel(container, text="Current State Assertion: NORMAL", font=("Arial", 10, "italic"))
    lbl_status.pack(side="bottom", pady=5)

    def toggle_label_states():
        """Cycles the description label states between normal and disabled profiles."""
        current_state = tertiary_label.get_state()
        target = "disabled" if current_state == "normal" else "normal"

        tertiary_label.configure(state=target)

        if target == "disabled":
            btn_toggle.configure(text="Activate Description (Set 'normal')")
            lbl_status.configure(text="Current State Assertion: DISABLED")
        else:
            btn_toggle.configure(text="Dim Description (Set 'disabled')")
            lbl_status.configure(text="Current State Assertion: NORMAL")

        print(f"Logged Verification Hook -> tertiary_label.get_state() = {tertiary_label.get_state()}")

    # Standard interaction trigger button to dispatch state transformations
    btn_toggle = ctk.CTkButton(
        container,
        text="Dim Description (Set 'disabled')",
        command=toggle_label_states,
        fg_color=("#1A4375", "#3B8ED0"),
        hover_color=("#112A4B", "#1F6AA5")
    )
    btn_toggle.pack(expand=True, pady=15)

    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    tertiary_label.state("disabled")
    print(f"state (Disabled Pass) = {tertiary_label.get_state().upper()}")

    tertiary_label.state("normal")
    print(f"state (Normal Pass)   = {tertiary_label.get_state().upper()}")
    print("========================================\n")

    root.mainloop()
```

[Return to Table of Contents](#contents)
