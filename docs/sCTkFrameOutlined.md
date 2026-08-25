## sCTkFrameOutlined

A clean, theme-compliant container frame variant explicitly styled to act as an outlined structural card or passive layout grouping box. It integrates a clean operational state interceptor layer to gracefully absorb cascading configuration switches without throwing unrecognized keyword violations.

### API Property Reference

| Property / Feature | Standard CustomTkinter | Your `sCustomTkinter` Setup |
| :--- | :--- | :--- |
| **Instantiation** | `ctk.CTkFrame(master)` | `sCTkFrameOutlined(master)` *(Functions as Outlined Panel Box)* |
| **Maintenance** | Manual alignment of background and boundary color borders. | Clean style updates modified globally right inside the master JSON file. |
| **File Mapping** | Everything runs under one core native pipeline track. | Streamlined and compiled programmatically across `sCTkFrameOutlined.py` and `ThemeableWidget.py`. |
| `state(mode)` | *Not Available Natively* | `Method (str)` managing layout tracking map transformations (`'normal'`, `'disabled'`). |
| `get_state()` | *Not Available Natively* | `Method -> str` explicit verification query matching system test assertions. |

---

### Constructor

Initialize a custom outlined container chassis layout instance. Border widths, corners, and framework properties layer cleanly over configuration choices and are automatically sanitized by the `ThemeableWidget` mixin layer before the native constructor fires.

```python
# Instantiate a theme-compliant outlined group card panel box
vfo_preset_card = sCTkFrameOutlined(
    master=main_dashboard,
    border_width=2,
    corner_radius=6
)

# Render the widget inside your parent container coordinate tracker layout
vfo_preset_card.pack(fill="both", expand=True, padx=20, pady=20)
```

---

### Convenience Functions
```python
# Evaluate active visual modes or apply absolute user interaction locks via dual-routing syntax
current_mode = vfo_preset_card.get_state() # Returns 'normal' or 'disabled'
vfo_preset_card.state("disabled")          # Softens border highlights and fades panel backgrounds safely

# Smoothly query standard Tkinter children references inside the grouping chassis
for child in vfo_preset_card.winfo_children():
    # Structural Check: Ensure control buttons are skipped during cascading locks
    if child == master_unlock_button:
        continue
    if hasattr(child, "configure"):
        child.configure(state="disabled")
```
### Centralized Stylesheet Setup (`themes.json`)
```json
{
    "sCTkFrameOutlined": {
        "fg_color": ["#FFFFFF", "#1E1E1E"],
        "border_color": ["#1A4375", "#FF9100"],
        "corner_radius": 8,
        "border_width": 2,
        "disabled_map": {
            "fg_color": ["#F1F5F9", "#121212"],
            "border_color": ["#CBD5E1", "#4B5563"]
        }
    }
}
```

---

### Other Notes
* **Universal State Interceptor:** Intercepts incoming `state` configuration commands, stripping them out completely to protect native CustomTkinter validation threads from fatal unhandled type exceptions, while successfully updating frame visual accents via an internal tuple resolution pass.
* **Automated Lifecycle Handshake:** Fires `self._finalize_themeable_lifecycle()` at the absolute end of the constructor initialization track to cleanly pass instance registration hooks straight back up to Pygubu parent controllers.
* **Containment Architecture Guard:** When implementing an automatic state sweep across standard `.winfo_children()` layers, always isolate your action trigger button. If it is packed inside the same outline frame layout without a bypass filter, it will freeze its own execution threads and lock the workspace.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkFrameOutlined` card along with an application-layer cascading state toggle switch.

```python
#!/usr/bin/python3
"""
sCTkFrameOutlined - Standalone Interactive Testing Harness
"""
import customtkinter as ctk
import sCTkThemes
from sCTkLabelSecondary import sCTkLabelSecondary
from sCTkEntryPrimary import sCTkEntryPrimary
from sCTkFrameOutlined import sCTkFrameOutlined

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.title("Passive Outline Frame Test Suite")
    root.geometry("450x300")

    # Instantiate your custom theme-compliant outlined frame panel card
    frame_group = sCTkFrameOutlined(root, border_width=2)
    frame_group.pack(fill="both", expand=True, padx=20, pady=20)

    lbl_title = sCTkLabelSecondary(frame_group, text="TRANSCEIVER FREQUENCY PRESET PROFILE")
    lbl_title.pack(pady=(12, 4), padx=10, fill="x")

    mock_entry = sCTkEntryPrimary(frame_group, placeholder_text="Standard data field...")
    mock_entry.pack(pady=10, padx=25, fill="x")

    def toggle_frame_states():
        """Toggles the outlined card panel and cascades the state change down to child widgets, skipping the trigger."""
        current_mode = frame_group.get_state()
        target = "disabled" if current_mode == "normal" else "normal"

        # 1. Transition the parent outline panel colors
        frame_group.configure(state=target)

        # 2. Cascade loop targeting elements resting inside the border frame card
        for child in frame_group.winfo_children():
            if child == btn_toggle:
                continue
            if hasattr(child, "configure"):
                child.configure(state=target)

        btn_toggle.configure(
            text="Lock Outline Deck (Set 'disabled')" if target == "normal" else "Unlock Outline Deck (Set 'normal')")
        print(f"Logged Verification Hook -> frame_group.get_state() = {frame_group.get_state()}")

    btn_toggle = ctk.CTkButton(frame_group, text="Lock Outline Deck (Set 'disabled')", command=toggle_frame_states)
    btn_toggle.pack(side="bottom", pady=15)

    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    print(f"Initial Outline Frame State = {frame_group.get_state().upper()}")
    print("========================================\n")

    root.mainloop()
```
