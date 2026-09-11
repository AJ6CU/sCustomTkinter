## sCTkSMeter

<a name="contents"></a>
### Table of Contents
* [Overview](#geometry)
* [Constructor](#constructor)
* [Methods](#methods)
* [State](#state)
* [Fonts and Label Placement](#fonts)
* [Centralized Stylesheet Integration](#theming)
* [Example](#example)


The `sCTkSMeter` is a standalone, theme-adaptive analog S-Meter/Power Output gauge instrument designed specifically for ham radio transceiver desktop interfaces. Natively inheriting container footprints from `customtkinter.CTkFrame`, it delivers smooth telemetry tracking sweeps without the overhead of extraneous nesting modules.


  ![sCTkSMeter_Dark.png](images/sCTkSMeter_Dark.png)&emsp; &emsp; &emsp; &emsp;
  ![sCTkSMeter_Light.png](images/sCTkSMeter_Light.png)


---

<a name="geometry"></a>
### Overview

The instrument face is split mathematically to mirror classic analog transceiver gauge divisions perfectly:
*   **The S-Unit Scale (Ticks 0–9):** Maps incoming telemetry values from `0.0` to `9.0` linearly across the first 60% of the visual arc container, rendered in your high-contrast brand or amber theme palettes.
*   **The Decibel Over S9 Scale (Ticks 9–15):** Maps advanced signal parameters from `9.0` up to `69.0` across the remaining 40% of the dial arc track (where `+20dB` sits at coordinate 29, `+40dB` at 49, and `+60dB` at 69). This region is permanently framed by your crimson/redline alert warning colors.
*   **Unified Pivot Axis Integration:** The inner rendering engines calculate lines, arcs, labels, and needle sweeps using a singular synchronized mathematical pivot point (`center_x = width * 0.48`). This entirely eliminates off-axis tracking drift or floating pointer artifacts when live data streams update.

---

<a name="constructor"></a>
### Constructor

```python
sCTkSMeter(master=None, width=250, height=130, state="normal", **kw)
```

| Parameter Name | Data Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `master` | `any` | `None` | Reference pointer tracking your root window or parent `sCTkFrame` container layout layer. |
| `width` | `int` | `250` | Panel width in pixels. Supports Pygubu geometry-default reset queries. |
| `height` | `int` | `130` | Panel height in pixels. Supports Pygubu geometry-default reset queries. |
| `state` | `str` | `"normal"` | `"normal"` or `"disabled"`. See [State](#state) below. |

---

<a name="methods"></a>
### Methods

To drive the needle tracking sweep fluidly inside background receiver threads, automatic VFO frequency scanning loops, or telemetry data parsing hooks, utilize this direct public setter:

#### Update Instrument Needle Position
```python
# Updates pointer positioning dynamically. Expects a float value clamped between 0.0 and 69.0.
smeter.set(value)
```

<a name="state"></a>
### State

| Method | Description |
| :--- | :--- |
| `state(mode=None)` | Getter with no argument; setter with `"normal"` or `"disabled"`. |
| `get_state()` | Equivalent to `state()` with no argument. |
| `configure(state=...)` | Same effect. Both routes are supported. |
| `cget("state")` | Reads the current state. |
| `configure("state")` | Pygubu-style single-argument query. |

**Disabling dims, it does not freeze.** `state("disabled")` changes only the palette. `set()` continues to update the needle, and the gauge keeps tracking live values in the dimmed colours. This is deliberate for an output-only instrument: a meter that held its last reading while greyed out would be indistinguishable from one showing a current value, which on a radio panel is actively misleading. There is no input to lock out — the state exists so a panel can disable every widget it contains uniformly.

The background is deliberately **not** dimmed; the face and needle carry the signal, matching `sCTkScrollableFrame` and the dial family.

---

<a name="fonts"></a>
### Fonts and Label Placement

`font` and `scale_font` are **per-instance properties** as well as theme keys. Set either in the constructor, through `configure()`, or in the Designer's inspector; leave it blank and the theme's value applies.

| Property | Applies to |
| :--- | :--- |
| `font` | The `"SIGNAL"` and `"RF OUTPUT"` captions |
| `scale_font` | The numeric scale tick labels |

```python
meter.configure(scale_font=("Arial", 12, "bold"))
meter.configure(scale_font="")      # back to the theme's scale_font
```

**Label positions are derived from the font, not hardcoded.** Every gap between a label and the scale it marks used to be a fixed pixel count tuned for the default size, so a larger font grew across it and overlapped the thing it was labelling. Those offsets now come from the font's own line height, so text stays clear at any reasonable size.

The scale labels are placed by angle around the arc, so an oversized `scale_font` crowds them against one another rather than clipping at the canvas edge. There is no automatic spacing: if the labels start to touch, use a smaller `scale_font` or a larger meter.
<a name="theming"></a>
### Theming (`sCTkThemes.json`)

```json
{
    "sCTkSMeter": {
        "fg_color": ["#F4F7FA", "#0A0A0A"],
        "text_color": ["#1A4375", "#FF9100"],
        "alarm_color": ["#990000", "#FF2200"],
        "needle_color": ["#112A4B", "#FF9100"],
        "font": ["Arial", 10, "bold"],
        "scale_font": ["Arial", 10, "bold"],
        "disabled_map": {
            "text_color": ["#94A3B8", "#4B5563"],
            "alarm_color": ["#CBD5E1", "#4B5563"],
            "needle_color": ["#94A3B8", "#4B5563"]
        }
    }
}
```

**Every key above is required.** Construction raises `KeyError` naming the missing key and whether it belongs at the top level or in `disabled_map`. This replaced a pattern of `.get(key, ("#hex", "#hex"))` throughout the draw code, which silently substituted a plausible guess and made an incomplete theme block look merely slightly-off rather than broken.

`font` is used for the "SIGNAL" and "RF OUTPUT" captions; `scale_font` for the numeric tick labels and the "S" marker. They're separate keys because the widget makes that distinction, even though the default values happen to match.

> **Superseded.** This page used to warn that label positions were fixed pixel offsets tuned for 10pt text and that a larger font would overlap the scale. They are now derived from the font's own metrics — see [Fonts and Label Placement](#fonts) for what still constrains a large font.

**`fg_color` is a property as well as a theme key,** and it paints the **canvas** rather than the frame behind it — the canvas covers the whole widget, so the frame is never visible. Set it in the inspector or through `configure()`; blank returns to the theme's value.

The other frame properties are deliberately **not** offered. `border_color`, `border_width` and `corner_radius` were added to the inspector at one point and taken back out: they appeared and did nothing at all, for the same reason. A property that cannot work is worse than an absent one.

`corner_radius` is the real loss. Rounding the meter would mean rounding the canvas, which Tk cannot do — it would have to be drawn, as a rounded rectangle filling the corners in the parent's colour. Possible, not free, and not done.

**A colour set at runtime survives a state change,** and clearing it returns to the theme rather than to the previous value. See [Theming](Theming.md#changing-values-at-runtime).

**Fixed:** the configured `fg_color` never actually rendered. It was popped out of the resolved defaults in the constructor (correctly — the native frame takes it separately) and then read back afterwards from the dictionary it had been removed from, so the background always fell through to a hardcoded value. Light mode is where this was visible.

---

<a name="example"></a>
### Example

Below is a complete, self-contained interactive test execution script demonstrating how to use `sCTkSMeter`.


```python
#!/usr/bin/python3
# =====================================================================
# TESTING HARNESS IMPORTS & SETUP for S Meter
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary, sCTk, sCTkSMeter
import random


if __name__ == "__main__":

    root = sCTk()
    root.title("sCTk Standalone Analog Gauge")
    root.geometry("450x260")
    root.configure(fg_color=("#F1F5F9", "#1C1C1C"))

    dashboard_frame = sCTkFrame(root, fg_color="transparent", border_width=0)
    dashboard_frame.pack(padx=20, pady=20)

    smeter = sCTkSMeter(dashboard_frame, width=340, height=130)
    smeter.pack(padx=10, pady=10)


    class SignalSimulator:
        def __init__(self, root_win, meter):
            self.root, self.meter = root_win, meter
            self.target, self.needle = 6.0, 0.0

        def shift_vfo(self):
            self.target = random.uniform(1.5, 65.0)
            self.root.after(random.randint(2500, 5000), self.shift_vfo)

        def physics_loop(self):
            jitter = random.uniform(-1.5, 1.5)
            sig = max(0.0, min(69.0, self.target + jitter))
            self.needle += (sig - self.needle) * 0.25
            self.meter.set(self.needle)
            self.root.after(25, self.physics_loop)


    sim = SignalSimulator(root, smeter)
    sim.physics_loop()
    sim.shift_vfo()


    def toggle_theme():
        ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")


    sCTkButtonPrimary(root, text="Toggle Theme mode", command=toggle_theme).pack(pady=5)
    root.mainloop()

```

[Return to Table of Contents](#contents)
