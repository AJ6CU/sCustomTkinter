## sCTkDialRange

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Sizing and Label Placement](#sizing)
* [Callbacks](#callbacks)
* [Latching](sCTkDial.md#latching)
* [Colours you can set per instance](#colours-you-can-set-per-instance)
* [Centralized Stylesheet Setup](#theming-sctkthemesjson)
* [Other Notes](#known-limitations)
* [Example](#example)

---

A concrete rotary encoder range variant designed for hard-bounded linear controls (e.g., AF/RF volume gain level sliders, squelch limits, or power thresholds). It enforces absolute mechanical dead stops at outer thresholds, preventing directional wraparound loops.


  ![sCTkDialRange_Dark.png](images/sCTkDialRange_Dark.png)&emsp; &emsp; &emsp; &emsp;
  ![sCTkDialRange_Light.png](images/sCTkDialRange_Light.png)


### Overview

| Property / Feature | Type / Signature | Description |
| :--- | :--- | :--- |
| **Instantiation** | *Constructor* | `sCTkDialRange(master)` *(Bounded Linear Range Dial)* |
| **File Mapping** | *Inheritance Tree* | Streamlined and compiled programmatically inside `sCTkDial.py` and `ThemeableWidget.py`. |
| `from_` / `min_value` | `int` | Lower boundary threshold (default 0) enforcing absolute counter-clockwise dead stops. |
| `to` / `max_value` | `int` | Upper boundary threshold (default 100) enforcing absolute clockwise dead stops. |
| `divisions` | `int` | Quantized subdivision tick line count painted geometrically across the arc limit sweep. |
| `_scroll_cooldown_seconds`| `float` | Throttle limiting touchpad refresh rates to stabilize fast range adjustments. |
| `get()` / `set(val)` | `Methods -> int` | Unified index query mechanisms to get or force selected integer values. |
| `left_click_callback` | `Callable / None` | Replaces the built-in single step taken when the left half of the canvas is clicked. Use it to move by more than one position per click. |
| `right_click_callback` | `Callable / None` | Replaces the built-in single step taken when the right half of the canvas is clicked. |
| `state(mode)` | `str` | `"normal"` or `"disabled"`. `configure(state=...)` does the same thing. Disabling removes the click, wheel and trackpad bindings and repaints from `disabled_map`. On a latching dial it also clears the latch. |
| `latching` | `bool` | Opt-in. The dial starts switched off and ignores input until armed — see [Latching](sCTkDial.md#latching). Default `False`. |
| `double_click_command` | `Callable / None` | Called on a double-click, with the dial itself. Not wired to anything by the widget; typically used to arm a latching dial. |
| `shift_double_click_command` | `Callable / None` | Called on a shift-double-click, with the dial itself. Typically used to disarm. |

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

<a name="sizing"></a>
### Sizing and Label Placement

**`knob_diameter` is the knob. `width` and `height` are the canvas.**

That distinction is new. The property was called `diameter` and set both canvas dimensions to its own value, so `diameter=300` produced a 300px *widget* with a 244px knob inside it — the name described neither. It is now honest: the knob is drawn at exactly `knob_diameter`, and the canvas is whatever `width` and `height` say.

```python
dial = sCTkDialRange(parent, knob_diameter=120)              # canvas defaults to 200x200
dial = sCTkDialRange(parent, knob_diameter=120, width=400)   # wide canvas, same knob
```

Given only `knob_diameter`, the canvas defaults to 40px larger on each side — enough for the default labels at the default font.

**Three dials sharing a `knob_diameter` have identical knobs,** however long their labels are. That is the point of the separation. An earlier version measured the labels and shrank the knob to fit them inside a fixed widget; that kept layouts predictable but made a row of controls look inconsistent, which is the case that matters most.

**Labels that do not fit are clipped.** Widen the canvas, shorten the label, or break it:

```python
labels=["Very\nLong", "12", "RTTY"]
```

Labels anchor **away** from the dial — one on the left grows leftward, one at the top grows upward — so a long label extends outward rather than across the knob face. The gap between knob and text scales with `label_font`, so larger text still clears the edge.

| Property | Type | Description |
| :--- | :--- | :--- |
| `knob_diameter` | `int` | Diameter of the knob itself, in pixels. Default 120. |
| `width` / `height` | `int` | Canvas size. Defaults to `knob_diameter + 80` when not given. |
| `label_font` | `tuple` | Font for the labels. Blank uses the theme's `label_font`. |

---


### Callbacks

Dispatches the current absolute active integer value directly to runtime tracking listeners upon position changes.

#### Command 

```python
# Fires automatically on valid mouse scrolling, touchpad rolling, or click-drag actions
def on_volume_level_changed(active_value: int):
    # active_value is hard constrained between your from_ and to boundary integers
    print(f"Active Selected Option Value position tracker = {active_value}")
```

### Colours you can set per instance

Three of this widget's colours are properties as well as theme keys — set them in the constructor, through `configure()`, or in the Designer's inspector, and leave blank for the theme's value.

| Property | Applies to |
| :--- | :--- |
| `text_color` | The labels **and** the tick marks — both are drawn with this one key. |
| `dial_color` | The knob face. |
| `pointer_color` | The pointer line on the knob. |

The remaining five — `dial_highlight_color`, `dial_shadow_color`, `dial_rim_light_color`, `dial_rim_shadow_color` and `shadow_color` — stay theme-only on purpose. They produce the shaded dome together, and changing one in isolation tends to read as broken rather than different.

There is no separate tick colour. If you want ticks and labels to differ, that needs a new theme key and a change to the draw code.

---

### Theming (`sCTkThemes.json`)

```json
{
    "sCTkDialRange": {
        "fg_color": ["#F1F5F9", "#0A0A0A"],
        "text_color": ["#7B93B0", "#915404"],
        "shadow_color": ["#DCE3EC", "#06070A"],
        "label_font": ["Arial", "9"],
        "dial_color": ["#C3C5C7", "#1C1E26"],
        "dial_highlight_color": ["#EAEEF2", "#292A2E"],
        "dial_shadow_color": ["#9FA4A8", "#070708"],
        "dial_rim_light_color": ["#F9FAFC", "#53565A"],
        "dial_rim_shadow_color": ["#8F9396", "#040404"],
        "pointer_color": ["#7B93B0", "#915404"],

        "pressed_map": {
            "text_color": ["#1A4375", "#FF9100"],
            "shadow_color": ["#CBD5E1", "#02040A"],
            "dial_color": ["#9E9E9E", "#2A2F3D"],
            "dial_highlight_color": ["#E4E8EC", "#42454B"],
            "dial_shadow_color": ["#5C6165", "#050507"],
            "dial_rim_light_color": ["#FFFFFF", "#8E949C"],
            "dial_rim_shadow_color": ["#3E4245", "#000000"],
            "pointer_color": ["#1A4375", "#FF9100"]
        },

        "disabled_map": {
            "text_color": ["#94A3B8", "#4B5563"],
            "dial_color": ["#E2E8F0", "#1A1D24"]
        }
    }
}
```

Every key above is required — construction raises `KeyError` naming any that are missing. `pressed_map` is the exception: it is read only when the dial is built with `latching=True`.

**A dial can be made to require arming before it responds.** Opt in with `latching=True` and wire the double-click callbacks; the dial then starts switched off, ignores input, and draws the resting colours until armed. The `pressed_map` above holds the operational set. See [Latching](sCTkDial.md#latching) on the base class page for the whole mechanism, including why arming and disarming use different gestures.

**A colour set at runtime survives a state change.** Disable the widget and enable it again and your value is still there; clearing the property returns it to the theme's, not to whatever was set before. See [Theming](Theming.md#changing-values-at-runtime) for the general rule.
 See [the base class page](sCTkDial.md#theme-contract) for the shared contract.

`pointer_color` is **specific to this variant and its Selector sibling**, and colours the pointer line. It was present in the theme file for a long time but read by no code path at all — the pointer drew in `text_color` instead. It is now live, so the pointer can differ from the tick labels. It has no `disabled_map` entry; a disabled pointer falls back to the disabled `text_color`.

### Known Limitations
* **Knob rendering:** the body is a shaded dome, marked with a plain straight line from dead centre out to just short of the rim. An earlier version drew an arrowhead and a raised centre cap; both are gone, along with the cap's two hardcoded outline colours. See [the base class page](sCTkDial.md#knob-rendering).
* **`.config()` now works.** This class previously had no `config = configure` alias, so `.config(...)` bypassed every override and landed on the native widget. If existing code called it expecting no effect, it will now have one.
* **Theme colours are live for the first time.** Colours were previously read from `final_kw`, which never contained them, so every dial rendered in hardcoded fallbacks regardless of the theme file. See [reading theme colours](sCTkDial.md#reading-theme-colours).
* **Inherits `ctk.CTkFrame` and `ThemeableWidget` directly,** with no intermediate template class in between. That ordering matters: the native class comes first, so every `super()` call in the dial's own methods resolves to CustomTkinter rather than to the mixin.
* **`_finalize_themeable_lifecycle()` fires at the end of the constructor,** which is what tells a Pygubu-style consumer the widget is ready. Every widget in the library does this; a missing call means an `on_first_object_cb` callback silently never runs.
* **Hard end stops.** Scrolling past `from_` or `to` clamps rather than wrapping, unlike the Selector, which wraps around to the first position. A range dial that jumped from maximum to minimum on one extra click would be a hazard on a volume control.

---

### Example

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkDialRange` alongside custom click jump hooks and an active volume gain control panel display tracker.

```python
#!/usr/bin/python3
# =====================================================================
# TESTING HARNESS IMPORTS & SETUP for Dial Range
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
        """Drops three units per click, instead of the built-in one."""
        if volume_pot.get_state() == "disabled": return
        volume_pot.set(volume_pot.get() - 3)


    def my_custom_right_click():
        """Adds three units per click, instead of the built-in one."""
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
