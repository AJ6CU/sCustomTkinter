## sCTkDialSelector

### Table of Contents
* [API Property Reference](#api-property-reference)
* [Constructor](#constructor)
* [Callback Signature & Usage](#callback-signature--usage)
* [Centralized Stylesheet Setup](#centralized-stylesheet-setup-sctkthemesjson)
* [Other Notes](#other-notes)
* [Implementation Example & Test Harness](#implementation-example--test-harness)

---

A concrete rotary encoder switch variant designed for stepped selector controls (e.g., band configurations, operating modes, or filter sub-selections). It uses an explicit bounding arc configuration and outputs a clean integer mapping parameter tracking list item indices natively.


![sCTkDialSelector_Dark.png](images/sCTkDialSelector_Dark.png)
![sCTkDialSelector_Light.png](images/sCTkDialSelector_Light.png)


### API Property Reference

| Property / Feature        | Type / Signature | Description |
|:--------------------------| :--- | :--- |
| **Instantiation**         | *Constructor* | `sCTkDialSelector(master)` *(Stepped Arc Selector Dial)* |
| **File Mapping**          | *Inheritance Tree* | Streamlined and compiled programmatically inside `sCTkDial.py` and `ThemeableWidget.py`. |
| `labels`                  | `list [str]` | Ordered array list mapping string tags directly above calculated step lines. Supports raw comma-separated strings inside layout inspectors. |
| `arc_angle`               | `float` | Angular geometric limit (default 270) restricting the pointer range sweep layout. |
| `_scroll_cooldown_seconds`| `float` | Throttle limiting touchpad refresh rates to stabilize fast selector rolls. |
| `get()` / `set(idx)`      | `Methods -> int` | Unified index query mechanisms to get or force selected positions. |
| `left_click_callback`     | `Callable / None` | **Custom Accelerated Click Hook:** Overrides standard single-step decrements to execute accelerated jumping intervals when clicking the left canvas edge. |
| `right_click_callback`    | `Callable / None` | **Custom Accelerated Click Hook:** Overrides standard single-step increments to execute accelerated jumping intervals when clicking the right canvas edge. |
| **State**                 | `dial.state("disabled")`<br>**OR**<br>`dial.configure(state="disabled")` | **Dual-Routing State Pipeline:** Handles both syntaxes natively. Freezes canvas mouse-wheel scrolling, disables click jump hooks, and shifts visual themes out of `disabled_map` guidelines via a strict sequential re-binding engine. |

---

### Constructor

Initialize a custom stepped rotary selector switch instance. Properties like `labels` support raw string array text list configurations natively for absolute Pygubu inspector panel compatibility. Custom attributes from Pygubu builder allocations (like string `translator` tracks) are automatically intercepted and sanitized by the `ThemeableWidget` mixin layer before the native constructor fires.

```python
# Instantiate a 5-position operating mode rotary switch selector
mode_switch = sCTkDialSelector(
    master=control_panel,
    labels=["AM", "FM", "LSB", "USB", "CW-N"],
    arc_angle=180,
    command=on_operating_mode_changed,
    left_click_callback=my_custom_left_click,
    right_click_callback=my_custom_right_click
)
```

---

### Callback Signature & Usage

Dispatches the current absolute active list item integer index directly to runtime configuration listeners.

#### Command 

```python
# Fires automatically on valid mouse scrolling, touchpad rolling, or click-drag actions
def on_operating_mode_changed(active_index: int):
    # active_index maps directly to items in your labels block list (0, 1, 2, etc.)
    print(f"Active Selected Option Index position tracker = {active_index}")
```

### Centralized Stylesheet Setup (`sCTkThemes.json`)

```json
{
    "sCTkDialSelector": {
        "fg_color": ["#F1F5F9", "#0A0A0A"],
        "text_color": ["#1A4375", "#FF9100"],
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

`pointer_color` is **specific to this variant and its Range sibling**, and colours the pointer line. It was present in the theme file for a long time but read by no code path at all — the pointer drew in `text_color` instead. It is now live, so the pointer can differ from the tick labels. It has no `disabled_map` entry; a disabled pointer falls back to the disabled `text_color`.

### Other notes
* **Knob rendering:** the body is a shaded dome, marked with a plain straight line from dead centre out to just short of the rim. An earlier version drew an arrowhead and a raised centre cap; both are gone, along with the cap's two hardcoded outline colours. See [the base class page](sCTkDial.md#knob-rendering).
* **`.config()` now works.** This class previously had no `config = configure` alias, so `.config(...)` bypassed every override and landed on the native widget. If existing code called it expecting no effect, it will now have one.
* **Theme colours are live for the first time.** Colours were previously read from `final_kw`, which never contained them, so every dial rendered in hardcoded fallbacks regardless of the theme file. See [reading theme colours](sCTkDial.md#reading-theme-colours).
* **Bypassing the BaseUI Skeletons:** This component avoids all autogenerated Pygubu intermediate templates, connecting the component straight to CustomTkinter's appearance modes via programmatic multiple inheritance tracks.
* **Automated Lifecycle Handshake:** Fires `self._finalize_themeable_lifecycle()` at the absolute end of the constructor initialization track to cleanly pass instance registration hooks straight back up to Pygubu parent controllers.
* **Rolling Selector Loops:** When spinning scroll wheels beyond boundary edges, the index modulo calculates the length of the string array, snapping the cursor back around to index 0 smoothly.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkDialSelector` alongside custom click jump hooks and an active mode switch control panel display tracker.

```python
#!/usr/bin/python3

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Dial Rotary Switch (sCTkDialSelector)
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary, sCTk, sCTkLabelSecondary, sCTkDialSelector


if __name__ == "__main__":

    root = sCTk()
    root.geometry("450x350")
    root.title("Rotary Switch Selector Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    # 1. Attach a live telemetry readout label
    lbl_mode_tag = sCTkLabelSecondary(base, text="Selected Mode: AM", font=("Arial", 11, "bold"))
    lbl_mode_tag.pack(pady=15)


    def my_custom_left_click():
        """Accelerated Jump: Moves 2 complete indexing steps left per click tap."""
        if mode_selector.get_state() == "disabled":
            return
        mode_selector.set(mode_selector.get() - 2)


    def my_custom_right_click():
        """Accelerated Jump: Moves 2 complete indexing steps right per click tap."""
        if mode_selector.get_state() == "disabled":
            return
        mode_selector.set(mode_selector.get() + 2)


    # 2. Instantiate with unique radio deck selector labels and selection trackers
    mode_selector = sCTkDialSelector(
        base,
        labels=["AM", "FM", "LSB", "USB", "CW"],
        arc_angle=180,  # Half-circle step selector arc
        command=lambda idx: lbl_mode_tag.configure(text=f"Selected Mode: {mode_selector._labels[idx]}"),
        left_click_callback=my_custom_left_click,
        right_click_callback=my_custom_right_click
    )
    mode_selector.pack(expand=True, fill="none", padx=10, pady=10)


    # 3. Standard application dashboard interaction lock toggle simulation
    def toggle_widget_lock():
        current_mode = mode_selector.get_state()
        target = "disabled" if current_mode == "normal" else "normal"

        mode_selector.configure(state=target)
        btn_lock.configure(
            text="UNLOCK CHANNELS" if target == "disabled" else "LOCK SWITCH (Set 'disabled')"
        )
        print(f"Logged Verification Hook -> mode_selector.get_state() = {mode_selector.get_state()}")


    btn_lock = ctk.CTkButton(base, text="LOCK SWITCH (Set 'disabled')", command=toggle_widget_lock)
    btn_lock.pack(side="bottom", pady=10)

    # Standard test assertions routine verification sequences
    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    mode_selector.state("disabled")
    print("state (Disabled Pass) =", mode_selector.get_state())  # Output: disabled

    mode_selector.state("normal")
    print("state (Normal Pass)   =", mode_selector.get_state())  # Output: normal
    print("========================================\n")

    root.mainloop()
```

[Return to Table of Contents](#contents)
