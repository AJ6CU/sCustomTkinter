## sCTkSwitchAlt

The `sCTkSwitchAlt` is an advanced custom composite toggle switch component built on a high-performance vector graphics `ctk.CTkCanvas` layout engine. Unlike the native inheritance model found in the `sCTkSwitch` (Standard Switch), the alternative variant is engineered specifically to shatter CustomTkinter's low-level polygon color caching locks. This enables **100% complete color rendering control** driven straight out of your central `themes.json` sheets across both the track background and moving selector handle elements, completely eliminating square bounding box ghosts and artifact dropouts.

<a name="contents"></a>
### 📍 Table of Contents
* [API Constructor Reference](#constructor)
* [Vector Canvas Drawing Architecture](#canvas-engine)
* [Architectural Comparison (Standard Switch vs. Alt)](#comparison)
* [Global Object Instance Methods](#methods)
* [Centralized Stylesheet Integration](#stylesheet)
* [Implementation Reference Template](#template)

---

<a name="constructor"></a>
### 📋 API Constructor Reference

```python
sCTkSwitchAlt(master=None, text="", command=None, variable=None, textvariable=None, onvalue=1, offvalue=0, state="normal", font=None, **kw)
```

| Parameter Name | Data Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `master` | `any` | `None` | Reference pointer tracking your root window or parent layout layer capsule container. |
| `text` | `str` | `""` | The descriptive typography text string label displayed natively alongside the custom toggle switch canvas track. |
| `command` | `callable` | `None` | Optional event logging callback function executed instantly on state shifts, passing the active value. |
| `variable` | `Variable` | `None` | Persistent Tkinter variable tracking hook (e.g. `tk.IntVar` or `tk.StringVar`) mapped to the toggle state value. |
| `textvariable` | `Variable` | `None` | Dynamic data trace observer variable instance to update text description labels automatically. |
| `onvalue` | `any` | `1` | The value coordinate written to variables and passed to callbacks when the slider knob is checked. |
| `offvalue` | `any` | `0` | The value coordinate written to variables and passed to callbacks when the slider knob is unchecked. |
| `state` | `str` | `"normal"` | Execution state controller. Toggling to `"disabled"` dampens colors and activates total interaction locks. |
| `font` | `tuple` / `str` | `None` | Typography configuration specifically assigned to resolve descriptive text labels. |

---

<a name="canvas-engine"></a>
### 🛡️ Vector Canvas Drawing Architecture
Standard CustomTkinter switches lock color palettes inside native canvas properties upon birth initialization, making post-boot track recoloring impossible. Furthermore, nesting traditional rounded shapes frequently results in white or black hard-edged "square" background bounding boxes bleeding through the layout under alternative global preference skins.

The `sCTkSwitchAlt` overcomes this limitation by implementing a **Pure Primitives Reconstruct Engine**. Built using `ctk.CTkCanvas`, the widget deletes and redraws the precise geometry lines of the capsule track (`create_oval` + `create_rectangle`) and a proportional 16px circle knob disc handle dynamically on every state transition. This guarantees high-visibility rendering, zero layout drift, and smooth color changes with absolute fidelity to your central stylesheets.

---

<a name="comparison"></a>
### 🔀 Architectural Comparison (Standard Switch vs. Alt)
The framework provides two unified, parallel switch variants engineered for distinct interface layout profiles:

1. **`sCTkSwitch` (Standard Switch Base Variant):**
   * *Underlying Engine:* Direct subclass of `ctk.CTkSwitch` maintaining native performance properties.
   * *Color Management:* Retains native color caching constraints. When disabled, the track background remains frozen on its base palette; only the description typography text dims down to gray.
   * *Animations:* Retains the native multi-frame linear handle slide translation animation curves.

2. **`sCTkSwitchAlt` (Alternative Composite Variant):**
   * *Underlying Engine:* Powered by an open vector canvas primitive layout container.
   * *Color Management:* Fully unlocked look layers. When enabled, the track remains a static blue (matching primary panel elements) instead of shifting hues. When disabled, the track capsule and circular disc knob instantly paint themselves in high-visibility steel and slate disabled tokens.
   * *Animations:* Bypasses sliding transitions; the indicator knob disc snaps to true coordinates instantly.

---

<a name="methods"></a>
### ⚡ Global Object Instance Methods

#### Fetch Active State Coordinates
```python
# Returns the active onvalue or offvalue parameter matching the position ledger register
active_choice = switch_alt.get()
```

#### Programmatically Toggle Placements
```python
# Forcefully sets the toggle position value, rendering the knob handle on or off instantly
switch_alt.set("on")
```

#### Query Active Operation Modes
```python
# Returns the active interaction mode string ('normal' or 'disabled')
current_state = switch_alt.get_state()
```

#### Apply Absolute Operational Interaction Locks
```python
# Disables click events on the canvas primitives while dimming all shapes down to custom gray levels
switch_alt.state("disabled")
```

---

<a name="stylesheet"></a>
### 🎨 Centralized Stylesheet Integration (`sCTkThemes.json`)

To minimize repository file footprint configurations, both the standard and alternative widgets share a single unified `"sCTkSwitch"` style map profile block. The alternative variant leverages the shared parameters to drive its track and circular knob fills dynamically:

```json
{
    "sCTkSwitch": {
        "fg_color": ["#1A4375", "#1F6AA5"],
        "progress_color": ["#1A4375", "#1F6AA5"],
        "button_color": ["#FFFFFF", "#CBD5E1"],
        "button_hover_color": ["#E5E7EB", "#94A3B8"],
        "text_color": ["#1F2937", "#F9FAFB"],
        "font": ["Arial", 14, "normal"],
        "disabled_map": {
            "text_color": ["#94A3B8", "#64748B"],
            "fg_color": ["#E5E7EB", "#526071"],
            "progress_color": ["#CBD5E1", "#526071"],
            "button_color": ["#8A94A6", "#94A3B8"],
            "button_hover_color": ["#8A94A6", "#94A3B8"]
        }
    }
}
```

---

<a name="template"></a>
### 💻 Implementation Reference Template

This standalone verification program demonstrates how to correctly embed both the `sCTkSwitch` (Standard Switch) and the advanced `sCTkSwitchAlt` within a shared panel interface, tracking live variables and skin preferred overrides simultaneously.

```python
import customtkinter as ctk
import sCTkThemes
from sCTkFrame import sCTkFrame
from sCTkLabelSecondary import sCTkLabelSecondary
from sCTkSwitch import sCTkSwitch
from sCTkSwitchAlt import sCTkSwitchAlt

if __name__ == "__main__":
    # 1. Initialize centralized framework look records natively out of themes.json
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("520x460")
    root.title("sCustomTkinter Dual Switch Validation Bench")
    root.configure(fg_color=("#F1F5F9", "#1C1C1C"))

    base = sCTkFrame(root, border_width=2)
    base.pack(expand=True, fill="both", padx=30, pady=30)
    base.grid_columnconfigure(0, weight=1)

    # =====================================================================
    # 🎛️ MODULE 1: Standard Switch (Native Inheritance Variant)
    # =====================================================================
    lbl_std = sCTkLabelSecondary(base, text="[Standard ctk.CTkSwitch Subclass]", font=("Arial", 11, "bold"))
    lbl_std.grid(row=0, column=0, padx=40, pady=(15, 2), sticky="w")
    
    switch_std = sCTkSwitch(
        base, 
        text="Standard Pre-Amp Link Channel",
        command=lambda val: print(f"Standard Pass -> State Value: {val}")
    )
    switch_std.grid(row=1, column=0, padx=40, pady=10, sticky="w")

    # =====================================================================
    # 🎛️ MODULE 2: Alternative Switch (Custom Composite Drawing Variant)
    # =====================================================================
    lbl_alt = sCTkLabelSecondary(base, text="[Alternative sCTkSwitchAlt Custom Draw]", font=("Arial", 11, "bold"))
    lbl_alt.grid(row=2, column=0, padx=40, pady=(25, 2), sticky="w")
    
    switch_alt = sCTkSwitchAlt(
        base, 
        text="Advanced VFO Frequency Lock Link",
        command=lambda val: print(f"Alternative Pass -> State Value: {val}")
    )
    switch_alt.grid(row=3, column=0, padx=40, pady=10, sticky="w")

    # =====================================================================
    # 🛠️ INTERACTIVE BENCH LOOK CONTROLLERS
    # =====================================================================
    def toggle_framework_locks():
        current_std = switch_std.get_state()
        target = "disabled" if current_std == "normal" else "normal"
        
        switch_std.configure(state=target)
        switch_alt.configure(state=target)
        
        btn_lock.configure(text="Unlock Panel (Set 'normal')" if target == "disabled" else "Lock Panel (Set 'disabled')")

    def toggle_skin_preference():
        ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")

    btn_lock = ctk.CTkButton(root, text="Lock Panel (Set 'disabled')", command=toggle_framework_locks)
    btn_lock.pack(side="bottom", pady=5)

    btn_skin = ctk.CTkButton(root, text="Toggle UI Light/Dark Appearance", command=toggle_skin_preference)
    btn_skin.pack(side="bottom", pady=5)

    root.mainloop()

