## sCTkDialContinuous

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Callbacks](#callbacks)
* [Latching](sCTkDial.md#latching)
* [Colours you can set per instance](#colours-you-can-set-per-instance)
* [Centralized Stylesheet Setup](#theming-sctkthemesjson)
* [Other Notes](#known-limitations)
* [Example](#example)

---

An infinite flywheel tuning encoder module tracking signed velocity delta step increments across an endless 360-degree rotation path (ideal for high-fidelity radio VFO controls, audio mixers, and multi-channel squelch encoders).


  ![sCTkDialContinuous_Dark.png](images/sCTkDialContinuous_Dark.png)&emsp; &emsp; &emsp; &emsp;
  ![sCTkDialContinuous_Light.png](images/sCTkDialContinuous_Light.png)


### Overview

| Property / Feature | Type / Signature | Description |
| :--- | :--- | :--- |
| **Instantiation** | *Constructor* | `sCTkDialContinuous(master)` *(Infinite Tuning Wheel Encoder)* |
| **File Mapping** | *Inheritance Tree* | Inherits vector math mechanics and 3D knob rendering directly out of `sCTkDial.py`. |
| `_scroll_cooldown_seconds`| `float` | Throttle limiting touchpad refresh rates to stabilize fast tuning rolls. |
| `set_position_index(delta)`| `Method (int)` | Manually advances the 3D dimple coordinates via an integer step. |
| `left_click_callback` | `Callable / None` | Replaces the built-in single step taken when the left half of the canvas is clicked. Use it to move by more than one position per click. |
| `right_click_callback` | `Callable / None` | Replaces the built-in single step taken when the right half of the canvas is clicked. |
| `state(mode)` | `str` | `"normal"` or `"disabled"`. `configure(state=...)` does the same thing. Disabling removes the click, wheel and trackpad bindings and repaints from `disabled_map`. On a latching dial it also clears the latch. |
| `latching` | `bool` | Opt-in. The dial starts switched off and ignores input until armed — see [Latching](sCTkDial.md#latching). Default `False`. |
| `double_click_command` | `Callable / None` | Called on a double-click, with the dial itself. Not wired to anything by the widget; typically used to arm a latching dial. |
| `shift_double_click_command` | `Callable / None` | Called on a shift-double-click, with the dial itself. Typically used to disarm. |

---

### Constructor

Initialize an infinite flywheel encoder instance. Keyword properties layer safely over centralized configuration defaults and are automatically sanitized by the `ThemeableWidget` mixin layer before the native constructor fires.

```python
# Instantiate the themed infinite VFO wheel element
tuning_dial = sCTkDialContinuous(
    master=frame_continuous,
    divisions=24,
    knob_diameter=130,
    command=on_vfo_dial_rotated,
    left_click_callback=my_custom_left_click,
    right_click_callback=my_custom_right_click
)
```

---

### Callbacks

Dispatches a raw signed directional integer step change directly to runtime listeners upon rotation changes.

#### Command 

```python
# Fires automatically on valid mouse scrolling, touchpad rolling, or click-drag actions
def on_vfo_dial_rotated(clicks_delta: int):
    # Clockwise rotation yields positive steps (+1); Counter-clockwise yields negative steps (-1)
    global current_frequency_hz
    current_frequency_hz += clicks_delta * 100
```

### Colours you can set per instance

Three of this widget's colours are properties as well as theme keys — set them in the constructor, through `configure()`, or in the Designer's inspector, and leave blank for the theme's value.

| Property | Applies to |
| :--- | :--- |
| `text_color` | The labels **and** the tick marks — both are drawn with this one key. |
| `dial_color` | The knob face. |
| `pointer_glow_color` | The glow around the finger dimple. |

The remaining five — `dial_highlight_color`, `dial_shadow_color`, `dial_rim_light_color`, `dial_rim_shadow_color` and `shadow_color` — stay theme-only on purpose. They produce the shaded dome together, and changing one in isolation tends to read as broken rather than different.

There is no separate tick colour. If you want ticks and labels to differ, that needs a new theme key and a change to the draw code.

---

### Theming (`sCTkThemes.json`)

```json
{
    "sCTkDialContinuous": {
        "fg_color": ["#F1F5F9", "#0A0A0A"],
        "text_color": ["#7B93B0", "#915404"],
        "shadow_color": ["#DCE3EC", "#06070A"],
        "dial_color": ["#C3C5C7", "#1C1E26"],
        "dial_highlight_color": ["#EAEEF2", "#292A2E"],
        "dial_shadow_color": ["#9FA4A8", "#070708"],
        "dial_rim_light_color": ["#F9FAFC", "#53565A"],
        "dial_rim_shadow_color": ["#8F9396", "#040404"],
        "pointer_glow_color": ["#DCE3EC", "#242A37"],

        "pressed_map": {
            "text_color": ["#1A4375", "#FF9100"],
            "shadow_color": ["#CBD5E1", "#02040A"],
            "dial_color": ["#9E9E9E", "#2A2F3D"],
            "dial_highlight_color": ["#E4E8EC", "#42454B"],
            "dial_shadow_color": ["#5C6165", "#050507"],
            "dial_rim_light_color": ["#FFFFFF", "#8E949C"],
            "dial_rim_shadow_color": ["#3E4245", "#000000"],
            "pointer_glow_color": ["#CBD5E1", "#3A455C"]
        },

        "disabled_map": {
            "text_color": ["#94A3B8", "#4B5563"],
            "dial_color": ["#E2E8F0", "#1A1D24"],
            "pointer_glow_color": ["#CBD5E1", "#334155"]
        }
    }
}
```

Every key above is required — construction raises `KeyError` naming any that are missing. `pressed_map` is the exception: it is read only when the dial is built with `latching=True`.

**A dial can be made to require arming before it responds.** Opt in with `latching=True` and wire the double-click callbacks; the dial then starts switched off, ignores input, and draws the resting colours until armed. The `pressed_map` above holds the operational set. See [Latching](sCTkDial.md#latching) on the base class page for the whole mechanism, including why arming and disarming use different gestures.

**A colour set at runtime survives a state change.** Disable the widget and enable it again and your value is still there; clearing the property returns it to the theme's, not to whatever was set before. See [Theming](Theming.md#changing-values-at-runtime) for the general rule.
 See [the base class page](sCTkDial.md#theme-contract) for the shared contract.

`pointer_glow_color` is **specific to this variant**: it colours the ring around the finger dimple, and only this dial draws one. It is required in both the top level and `disabled_map`. Selector and Range require `pointer_color` instead.

The dark-mode values above give a black anodised knob. For a brushed-aluminium look, raise `dial_shadow_color` and `dial_highlight_color` toward the light end and brighten the rim.

### Sizing

**`knob_diameter` names the knob; `width` and `height` name the canvas.** The property was previously called `diameter` and set both canvas dimensions to its own value, so the name described neither. This variant draws no labels, so a canvas only slightly larger than the knob is enough — given `knob_diameter` alone, it defaults to 40px more on each side.

---

### Known Limitations
* **Knob rendering:** the body is a shaded dome and the indicator is a recessed finger dimple, sized at 36% of the knob radius with 6% rim clearance — a VFO operator puts a finger in it to spin the dial quickly. Both scale with the knob. See [the base class page](sCTkDial.md#knob-rendering).
* **`.config()` now works.** This class previously had no `config = configure` alias, so `.config(...)` bypassed every override and landed on the native widget. If existing code called it expecting no effect, it will now have one.
* **Theme colours are live for the first time.** Colours were previously read from `final_kw`, which never contained them, so every dial rendered in hardcoded fallbacks regardless of the theme file. See [reading theme colours](sCTkDial.md#reading-theme-colours).
* **No end stops.** The dimple travels continuously around the knob. There is no `arc_angle`, no first or last position, and scrolling never reaches a boundary — this variant reports a signed step delta rather than a position, so there is nothing to clamp.
* **Click callbacks replace the single step,** rather than adding to it. `set_position_index(2)` inside one moves two positions per click instead of the built-in one.
* **`_finalize_themeable_lifecycle()` fires at the end of the constructor,** which is what tells a Pygubu-style consumer the widget is ready. Every widget in the library does this; a missing call means an `on_first_object_cb` callback silently never runs.

---

### Example

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkDialContinuous` alongside custom click jump hooks and an interactive VFO digital frequency display counter readout.

```python
#!/usr/bin/python3
# =====================================================================
# TESTING HARNESS IMPORTS & SETUP for Dial Continuous
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary, sCTk, sCTkLabelSecondary, sCTkDialContinuous



# Global state trackers for the interactive bench loop
current_frequency_hz = 14032000


def refresh_frequency_display():
    """Formats integers into a clean MHz telemetry layout readout string."""
    freq_str = f"{current_frequency_hz:08d}"
    formatted_freq = f"{freq_str[-8:-6]}.{freq_str[-6:-3]}.{freq_str[-3:]}"
    if formatted_freq.startswith("."):
        formatted_freq = formatted_freq[1:]

    if lbl_vfo_display.winfo_exists():
        lbl_vfo_display.configure(text=f"VFO Freq: {formatted_freq} MHz")


def on_vfo_dial_rotated(clicks_delta):
    """Event-driven callback tracking signed velocity delta step changes."""
    global current_frequency_hz
    current_frequency_hz += clicks_delta * 100
    current_frequency_hz = max(0, current_frequency_hz)
    refresh_frequency_display()


def my_custom_left_click():
    """Moves two positions left per click, instead of the built-in one."""
    if tuning_dial.cget("state") == "disabled":
        return
    tuning_dial.set_position_index(-2)  # Jump 2 steps left natively


def my_custom_right_click():
    """Moves two positions right per click, instead of the built-in one."""
    if tuning_dial.cget("state") == "disabled":
        return
    tuning_dial.set_position_index(2)  # Jump 2 steps right natively


def toggle_operational_state():
    """Toggles interaction channels and visual states back and forth."""
    current_mode = tuning_dial.cget("state")
    target = "disabled" if current_mode == "normal" else "normal"

    tuning_dial.configure(state=target)
    lbl_vfo_display.configure(state=target)
    btn_toggle.configure(text="Lock Dial (Set 'disabled')" if target == "normal" else "Unlock Dial (Set 'normal')")
    print(f"Logged Verification Hook -> tuning_dial.get_state() = {tuning_dial.get_state()}")


if __name__ == "__main__":
    root = sCTk()
    root.title("sCTkDialContinuous Test Deck")
    root.geometry("380x360")

    base = sCTkFrame(root, corner_radius=8)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    lbl_title = sCTkLabelSecondary(base, text="3. Continuous VFO WHEEL", font=("Arial", 12, "bold"))
    lbl_title.pack(pady=(12, 2))

    tuning_dial = sCTkDialContinuous(
        base,
        divisions=24,
        knob_diameter=130,
        command=on_vfo_dial_rotated,
        left_click_callback=my_custom_left_click,
        right_click_callback=my_custom_right_click
    )
    tuning_dial.pack(pady=10)

    lbl_vfo_display = sCTkLabelSecondary(base, text="VFO Freq: 14.032.000 MHz", font=("Arial", 11, "bold"))
    lbl_vfo_display.pack(pady=10)

    btn_toggle = sCTkButtonPrimary(base, text="Lock Dial (Set 'disabled')", command=toggle_operational_state)
    btn_toggle.pack(side="bottom", pady=15)

    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    print(f"Initial Dial State = {tuning_dial.get_state().upper()}")
    print("========================================\n")

    root.mainloop()
```

[Return to Table of Contents](#contents)
