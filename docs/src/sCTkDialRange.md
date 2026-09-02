## sCTkDialRange

### Table of Contents
* [API Property Reference](#api-property-reference)
* [Constructor](#constructor)
* [Callback Signature & Usage](#callback-signature--usage)
* [Centralized Stylesheet Setup](#centralized-stylesheet-setup-sctkthemesjson)
* [Other Notes](#other-notes)
* [Implementation Example & Test Harness](#implementation-example--test-harness)

---

A concrete rotary encoder range variant designed for hard-bounded linear controls (e.g., AF/RF volume gain level sliders, squelch limits, or power thresholds). It enforces absolute mechanical dead stops at outer thresholds, preventing directional wraparound loops.


  ![sCTkDialRange_Dark.png](images/sCTkDialRange_Dark.png)&emsp; &emsp; &emsp; &emsp;
  ![sCTkDialRange_Light.png](images/sCTkDialRange_Light.png)


### API Property Reference

| Property / Feature | Type / Signature | Description |
| :--- | :--- | :--- |
| **Instantiation** | *Constructor* | `sCTkDialRange(master)` *(Bounded Linear Range Dial)* |
| **File Mapping** | *Inheritance Tree* | Streamlined and compiled programmatically inside `sCTkDial.py` and `ThemeableWidget.py`. |
| `from_` / `min_value` | `int` | Lower boundary threshold (default 0) enforcing absolute counter-clockwise dead stops. |
| `to` / `max_value` | `int` | Upper boundary threshold (default 100) enforcing absolute clockwise dead stops. |
| `divisions` | `int` | Quantized subdivision tick line count painted geometrically across the arc limit sweep. |
| `_scroll_cooldown_seconds`| `float` | Throttle limiting touchpad refresh rates to stabilize fast range adjustments. |
| `get()` / `set(val)` | `Methods -> int` | Unified index query mechanisms to get or force selected integer values. |
| `left_click_callback` | `Callable / None` | **Custom Accelerated Click Hook:** Overrides standard single-step decrements to execute accelerated jumping intervals when clicking the left canvas edge. |
| `right_click_callback` | `Callable / None` | **Custom Accelerated Click Hook:** Overrides standard single-step increments to execute accelerated jumping intervals when clicking the right canvas edge. |
| **State**                 | `dial.state("disabled")`<br>**OR**<br>`dial.configure(state="disabled")` | **Dual-Routing State Pipeline:** Handles both syntaxes natively. Freezes canvas mouse-wheel scrolling, disables click jump hooks, and shifts visual themes out of `disabled_map` guidelines via a strict sequential re-binding engine. |

---

### Constructor

Initialize a custom bounded linear range potentiometer instance. Custom parameters passed from Pygubu builder allocations (like string `translator` tracks or `data_pool` environments) are automatically intercepted, processed, and purged early by the `ThemeableWidget` mixin layer before the native constructor fires. Bounding geometry sizes and limits scale out of central stylesheet registries.

```python
# Instantiate an AF Volume gain potentiometer control dial
volume_potentiometer = sCTkDialRange(
    master=control_panel,
    from_=0,
    to=30,
    divisions=6,
    arc_angle=270,
    command=on_volume_level_changed,
    left_click_callback=my_custom_left_click,
    right_click_callback=my_custom_right_click
)
```

---

### Callback Signature & Usage

Dispatches the current absolute active integer value directly to runtime tracking listeners upon position changes.

#### Command 

```python
# Fires automatically on valid mouse scrolling, touchpad rolling, or click-drag actions
def on_volume_level_changed(active_value: int):
    # active_value is hard constrained between your from_ and to boundary integers
    print(f"Active Selected Option Value position tracker = {active_value}")
```

### Centralized Stylesheet Setup (`sCTkThemes.json`)

```json
{
    "sCTkDialRange": {
        "fg_color": ["#F1F5F9", "#0A0A0A"],
        "text_color": ["#1A4375", "#64748B"],
        "shadow_color": ["#CBD5E1", "#02040A"],
        "dial_color": ["#9E9E9E", "#2A2F3D"],
        "dial_highlight_color": ["#E4E8EC", "#42454B"],
        "dial_shadow_color": ["#5C6165", "#050507"],
        "dial_rim_light_color": ["#FFFFFF", "#8E949C"],
        "dial_rim_shadow_color": ["#3E4245", "#000000"],
        "pointer_color": ["#1A4375", "#FF9100"],
        "disabled_map": {
            "text_color": ["#94A3B8", "#4B5563"],
            "dial_color": ["#E2E8F0", "#1A1D24"]
        }
    }
}
```

Every key above is required — construction raises `KeyError` naming any that are missing. See [the base class page](sCTkDial.md#theme-contract) for the shared contract.

`pointer_color` is **specific to this variant and its Selector sibling**, and colours the pointer line. It was present in the theme file for a long time but read by no code path at all — the pointer drew in `text_color` instead. It is now live, so the pointer can differ from the tick labels. It has no `disabled_map` entry; a disabled pointer falls back to the disabled `text_color`.

### Other notes
* **Knob rendering:** the body is a shaded dome, marked with a plain straight line from dead centre out to just short of the rim. An earlier version drew an arrowhead and a raised centre cap; both are gone, along with the cap's two hardcoded outline colours. See [the base class page](sCTkDial.md#knob-rendering).
* **`.config()` now works.** This class previously had no `config = configure` alias, so `.config(...)` bypassed every override and landed on the native widget. If existing code called it expecting no effect, it will now have one.
* **Theme colours are live for the first time.** Colours were previously read from `final_kw`, which never contained them, so every dial rendered in hardcoded fallbacks regardless of the theme file. See [reading theme colours](sCTkDial.md#reading-theme-colours).
* **Bypassing the BaseUI Middleman:** This component inherits cleanly and directly from native CustomTkinter classes and `ThemeableWidget`, completely bypassing the intermediate template layout files entirely to avoid argument deadlocks.
* **Automated Lifecycle Handshake:** At the absolute bottom of the initialization track, the constructor triggers `self._finalize_themeable_lifecycle()` to safely notify top-level Pygubu container managers that the widget is compiled.
* **Absolute Threshold Dead Stops:** Unlike continuous or selector models, scrolling past upper or lower boundaries clips inputs securely using `max(self._from, min(self._to, value))`, blocking accidental overflow.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkDialRange` alongside custom click jump hooks and an active volume gain control panel display tracker.

```python
#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Dial Range
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary, sCTk, sCTkLabelSecondary, sCTkDialRange


if __name__ == "__main__":

    root = sCTk()
    root.geometry("450x350")
    root.title("Ranged Potentiometer Telemetry Bench")

    base = sCTkFrame(root, corner_radius=8)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    # 1. Live feedback display lane tracking
    lbl_volume = sCTkLabelSecondary(base, text="AF Volume: 15 %", font=("Arial", 11, "bold"))
    lbl_volume.pack(pady=15)


    def my_custom_left_click():
        """Accelerated Jump: Drops 3 units per click tap."""
        if volume_pot.get_state() == "disabled": return
        volume_pot.set(volume_pot.get() - 3)


    def my_custom_right_click():
        """Accelerated Jump: Jumps 3 units per click tap."""
        if volume_pot.get_state() == "disabled": return
        volume_pot.set(volume_pot.get() + 3)


    # 2. Instantiate with explicit limits and tracking labels
    volume_pot = sCTkDialRange(
        base,
        from_=0,
        to=100,
        divisions=5,
        arc_angle=270,
        command=lambda val: lbl_volume.configure(text=f"AF Volume: {int((val / 100) * 100)} %"),
        left_click_callback=my_custom_left_click,
        right_click_callback=my_custom_right_click
    )
    volume_pot.pack(expand=True, fill="none", padx=10, pady=10)
    volume_pot.set(5)  # Initialize baseline startup volume index


    # 3. Dynamic panel interactive state toggle test layout
    def toggle_pot_lock():
        current_mode = volume_pot.get_state()
        target = "disabled" if current_mode == "normal" else "normal"

        volume_pot.configure(state=target)
        btn_toggle.configure(text="UNLOCK VOLUME DECK" if target == "disabled" else "LOCK POTENTIOMETER")
        print(f"Logged Verification Hook -> volume_pot.get_state() = {volume_pot.get_state()}")


    btn_toggle = sCTkButtonPrimary(base, text="LOCK POTENTIOMETER", command=toggle_pot_lock)
    btn_toggle.pack(side="bottom", pady=15)

    # Standard test assertions routine verification sequences
    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    volume_pot.state("disabled")
    print("state (Disabled Pass) =", volume_pot.get_state())  # Output: disabled

    volume_pot.state("normal")
    print("state (Normal Pass)   =", volume_pot.get_state())  # Output: normal
    print("========================================\n")

    root.mainloop()
```

[Return to Table of Contents](#contents)
