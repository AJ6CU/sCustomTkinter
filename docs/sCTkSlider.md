# sCTkSlider

Standardized live track calibration adjustment slider providing real-time data value interception, disabled layout mapping overrides, and multi-zone Pygubu designer compatibility.

---

## 🛠️ Architectural Design Features

*   **Direct Native Inheritance:** Inherits directly and cleanly from `customtkinter.CTkSlider` to completely preserve native high-performance mouse dragging handle calculations, scaling boundaries, and coordinate snap thresholds without unneeded structural layers.
*   **Decoupled Style Cascade Engine:** Color tracks and telemetry handle visuals are driven 100% via your centralized `themes.json` configuration file, avoiding duplicate style overrides scattered across your backend modules.
*   **Asynchronous Repaint Protection:** Utilizes a tight internal thread buffer on look resets to completely guard against layout collisions and prevent recursive infinite execution loop freezes.
*   **Pygubu Live Workspace Compatibility:** Safely handles Pygubu inspector property positional queries and feeds theme parameters directly into your designer workspace canvas to support accurate real-time visual mock sweeps.

---

## 🎨 Centralized Stylesheet Setup (`themes.json`)

To drive linear progress track filling and custom knob coordinate handle styles accurately across both look preference sweeps, ensure your centralized theme profile file includes this exact element block:

```json
{
    "sCTkSlider": {
        "fg_color": ["#E2E8F0", "#4B5563"],
        "progress_color": ["#2471A3", "#3B8ED0"],
        "button_color": ["#1A4375", "#1F6AA5"],
        "button_hover_color": ["#112A4B", "#194A7A"],
        "disabled_map": {
            "fg_color": ["#CBD5E1", "#374151"],
            "progress_color": ["#94A3B8", "#4B5563"],
            "button_color": ["#94A3B8", "#4B5563"]
        }
    }
}
```

---

## ⚙️ Public API Methods Reference

| Method Name | Arguments | Return Type | Description |
| :--- | :--- | :--- | :--- |
| `state(mode)` | `mode: str (Optional)` | `str` | Dedicated operational state manager. If empty, returns the current active state (`'normal'` or `'disabled'`). If passed, shifts tracking map parameters and cleanly freezes/unfreezes input handle loops. |
| `get_state()` | `None` | `str` | Explicit state tracking query synchronized with framework validation benchmarks. |
| `set(value)` | `value: float` | `None` | Manually positions the tracking slider handle directly onto a specific floating-point decimal location coordinate. |
| `cget(attribute)` | `attribute: str` | `Any` | Intercept shield layer that safely queries current active arguments from native CustomTkinter property arrays. |

---

## 💻 Implementation Code Template

```python
import customtkinter as ctk
import sCTkThemes
from sCTkFrame import sCTkFrame
from sCTkSlider import sCTkSlider
from sCTkLabelSecondary import sCTkLabelSecondary

# 1. Initialize global theme definitions
sCTkThemes.apply_sCTkThemes()

root = ctk.CTk()
root.geometry("450x220")
root.title("Slider Real-Time Telemetry Monitor")

# 2. Build parent layout track frame
base = sCTkFrame(root)
base.pack(expand=True, fill="both", padx=20, pady=20)

# 3. Live feedback layer to catch floating point data changes instantly
lbl_telemetry = sCTkLabelSecondary(base, text="Slider Coordinate: 0.450", font=("Courier New", 12, "bold"))

# 4. Instantiate the clean native-inheriting tracking slider widget
widget = sCTkSlider(base)
widget.configure(command=lambda val: lbl_telemetry.configure(text=f"Slider Coordinate: {val:.3f}"))
widget.pack(expand=False, fill="x", padx=40, pady=15)
widget.set(0.450)
lbl_telemetry.pack(pady=10)

root.mainloop()
```
