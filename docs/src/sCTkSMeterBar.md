## sCTkSMeterBar

The `sCTkSMeterBar` is a standalone, low-profile horizontal discrete 30-segment LED bar instrumentation widget displaying independent telemetry tracks for incoming receiver S-Units, transmitter SWR ratio levels, and forward RF Power output percentage. Like all sCTk widgets, it is fully theme-adaptive.


Dark Mode:  ![sCTkSMeterBar_Dark.png](images/sCTkSMeterBar_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode:  ![sCTkSMeterBar_Light.png](images/sCTkSMeterBar_Light.png)


---

### 🛠️ Subsystem Layout & Multi-Track Physics

The discrete LED matrix map shifts automatically based on the device operational path constraints:
*   **The S-Meter Track (Top Row):** Maps incoming telemetry values across 30 linear segments. Signals from `0.0` to `9.0` utilize the first 60% of the bar, while advanced signal ranges up to `+60dB` expand into the remaining 40% redline warning zone.
*   **The Transmitter Track (Split Bottom Row):** Splices the lower segment path down the center into two separate monitoring zones. The left half maps a logarithmic SWR reflection track up to your custom `swr_max_value`, while the right half tracks forward RF power from `0%` to `100%`.
*   **Post-Boot Geometry Flattening:** Overrides native internal grid layout constraints programmatically to force all 30 LED rectangles to sit perfectly flush. This completely removes horizontal spacing holes, keeping your panel elements locked into a solid hardware console bar.

---

### 📋 API Constructor Reference

```python
sCTkSMeterBar(master=None, swr_max_value=5.0, swr_visible=True, pwr_visible=True,
              hide_lower_row=False, width=320, height=110, state="normal", **kw)
```

| Parameter Name | Data Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `master` | `any` | `None` | Reference pointer tracking your root window or parent `sCTkFrame` container layout layer. |
| `swr_max_value` | `float` | `5.0` | The explicit maximum scale boundary representing the far right edge limit tracking your transmitter's SWR track. |
| `swr_visible` | `bool` | `True` | Visibility flag for the SWR cluster. `False` greys its text, ticks and LEDs to `inactive_color`. Distinct from widget state — see [State](#state). |
| `pwr_visible` | `bool` | `True` | Visibility flag for the PWR cluster. `False` greys its text, ticks and LEDs to `inactive_color`. Distinct from widget state — see [State](#state). |
| `hide_lower_row` | `bool` | `False` | Layout override command. When `True`, the entire lower instrumentation cluster collapses and vanishes, pushing the `SIG` bar to the true vertical center of the card footprint. |
| `width` | `int` | `320` | Panel width in pixels. Supports Pygubu geometry-default reset queries. |
| `height` | `int` | `110` | Panel height in pixels. Supports Pygubu geometry-default reset queries. |
| `state` | `str` | `"normal"` | `"normal"` or `"disabled"`. See [State](#state) below. |

---

### ⚡ Global Object Instance Methods

#### Update Instrument Telemetry Channels
```python
# Pass parameters to update any of the 3 telemetry rows independently on the fly.
# Expects floats matching your radio data streams.
led_bar_gauge.set(s_value=9.2, swr_value=1.4, pwr_value=45.0)
```

#### Live Layout Configuration Modifier
```python
# Updates layout presentation properties on the fly without reconstruction overhead.
led_bar_gauge.configure_visibility(swr_visible=False, pwr_visible=True, hide_lower_row=False)
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

**Disabling dims, it does not freeze.** `state("disabled")` changes only the palette. `set()` continues to update all three telemetry rows, and the bar keeps tracking live values in the dimmed colours. This is deliberate for an output-only instrument: a meter that held its last reading while greyed out would be indistinguishable from one showing a current value, which on a radio panel is actively misleading. There is no input to lock out — the state exists so a panel can disable every widget it contains uniformly.

**State and row visibility are independent.** `state("disabled")` dims the whole widget via `disabled_map`. `configure_visibility(swr_visible=False)` greys just that cluster to `inactive_color`. A row can be hidden on an enabled widget, and a disabled widget still shows whichever rows are visible. Both can apply at once.

The background is deliberately **not** dimmed; the LEDs and labels carry the signal.

---

### 🎨 Centralized Stylesheet Integration (`sCTkThemes.json`)

```json
{
    "sCTkSMeterBar": {
        "fg_color": ["#FFFFFF", "#0A0A0A"],
        "text_color": ["#1A4375", "#FF9100"],
        "alarm_color": ["#DC2626", "#FF2200"],
        "led_on_color": ["#2471A3", "#FF9100"],
        "led_off_color": ["#E2E8F0", "#1A1D20"],
        "inactive_color": ["#94A3B8", "#334155"],
        "font": ["Arial", 10, "bold"],
        "scale_font": ["Arial", 9, "bold"],
        "disabled_map": {
            "text_color": ["#94A3B8", "#4B5563"],
            "alarm_color": ["#CBD5E1", "#4B5563"],
            "led_on_color": ["#CBD5E1", "#374151"],
            "led_off_color": ["#F1F5F9", "#1A1D20"]
        }
    }
}
```

**Every key above is required.** Construction raises `KeyError` naming the missing key and whether it belongs at the top level or in `disabled_map`. This replaced a pattern of `.get(key, ("#hex", "#hex"))` throughout the draw code, which silently substituted a plausible guess and made an incomplete theme block look merely slightly-off rather than broken.

`inactive_color` greys the SWR or PWR cluster when that row is switched off via `configure_visibility()`. It has no `disabled_map` entry because it is not a state colour — see [State](#state). This value was previously hardcoded in the draw routine with no theme lookup at all, the only colour in this widget the theme could not reach.

`font` is used for the "SIG", "SWR" and "PWR" section labels; `scale_font` for the numeric scale markings — S units, SWR values and power percentages. These were previously hardcoded across eight separate `create_text` calls and never consulted the theme.

> **Font size has layout consequences.** Label positions are computed from fixed pixel offsets tuned for 9pt and 10pt text. A noticeably larger font will overlap the tick marks and the LED rows — the widget does not measure text and adjust. Change these values in small steps and look at the result.

**Fixed:** the configured `fg_color` never actually rendered. It was popped out of the resolved defaults in the constructor (correctly — the native frame takes it separately) and then read back afterwards from the dictionary it had been removed from, so the background always fell through to a hardcoded value. Light mode is where this was visible.

---

### Implementation Example & Test Harness

Below is a complete, self-contained interactive test execution script demonstrating how to use `sCTkSMeterBar`.


```python
#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for S Meter Bar
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary, sCTk, sCTkSMeterBar
import random


if __name__ == "__main__":

    app = sCTk()
    app.title("sCTk Bar Instrument Test Harness")
    app.geometry("440x240")
    app.configure(fg_color=("#F1F5F9", "#1C1C1C"))

    panel_container = sCTkFrame(app, fg_color="transparent", border_width=0)
    panel_container.pack(padx=20, pady=15, fill="both", expand=True)

    led_bar_gauge = sCTkSMeterBar(panel_container, width=340, height=110)
    led_bar_gauge.pack()

    class HarnessSimulator:
        def __init__(self, root_win, bar):
            self.root, self.bar = root_win, bar
            self.s_target, self.s_curr = 4.0, 0.0
            self.swr_target, self.pwr_target = 1.0, 0.0
            self.swr_curr, self.pwr_curr = 1.0, 0.0
            self.tx_active = False

        def tuning_cycle(self):
            self.s_target = random.uniform(0.5, 13.5)
            if not self.tx_active and random.random() > 0.4:
                self.tx_active = True
                self.swr_target = random.uniform(1.1, 4.5)
                self.pwr_target = random.uniform(35.0, 95.0)
                self.root.after(random.randint(1500, 3000), self._release)
            self.root.after(random.randint(4000, 8000), self.tuning_cycle)

        def _release(self):
            self.tx_active = False
            self.swr_target, self.pwr_target = 1.0, 0.0

        def physics_tick(self):
            self.s_curr += ((max(0.0, min(15.0, self.s_target + random.uniform(-1.2, 1.2)))) - self.s_curr) * 0.35
            self.swr_curr += (((max(1.0, min(5.0, self.swr_target + random.uniform(-0.15, 0.15))) if self.tx_active else 1.0)) - self.swr_curr) * 0.20
            self.pwr_curr += (((max(0.0, min(100.0, self.pwr_target + random.uniform(-2.5, 2.5))) if self.tx_active else 0.0)) - self.pwr_curr) * 0.20
            self.bar.set(s_value=self.s_curr, swr_value=self.swr_curr, pwr_value=self.pwr_curr)
            self.root.after(20, self.physics_tick)

    sim = HarnessSimulator(app, led_bar_gauge)
    sim.physics_tick()
    sim.tuning_cycle()

    def toggle_theme():
        ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")

    sCTkButtonPrimary(app, text="Toggle Theme", command=toggle_theme).pack(pady=5)
    app.mainloop()

```
