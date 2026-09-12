#!/usr/bin/python3
"""
Test bench for sCTkDialContinuous.

Demonstrates the LATCHING option: the dial starts switched off and inert, and
a double-click arms it.

    tuning_dial = sCTkDialContinuous(
        base,
        latching=True,
        double_click_command=lambda d: d.toggle_pressed(),
    )

Two separate things are going on there, deliberately:

  * `latching=True` makes the dial start switched off and ignore clicks,
    drags and the wheel until something calls set_pressed(True). It draws
    from the top-level theme colours while off and from pressed_map while on.

  * `double_click_command` is a plain callback. The widget does NOT wire it to
    the latch -- toggling on double-click is one use of it and a natural one,
    but the decision belongs to the application. Pass anything you like.

TO OPT OUT, drop both arguments. A dial built without `latching` behaves the
way it always has: always live, pressed_map ignored and not required in the
theme block. That is the default, so nothing existing changes.
"""
import customtkinter as ctk
from scustomtkinter import (sCTk, sCTkFrame, sCTkButtonPrimary,
                            sCTkLabelSecondary, sCTkDialContinuous)

current_frequency_hz = 14032000


def refresh_frequency_display():
    """Formats integers into a clean MHz readout."""
    freq_str = f"{current_frequency_hz:08d}"
    formatted = f"{freq_str[-8:-6]}.{freq_str[-6:-3]}.{freq_str[-3:]}"
    if formatted.startswith("."):
        formatted = formatted[1:]
    if lbl_vfo_display.winfo_exists():
        lbl_vfo_display.configure(text=f"VFO Freq: {formatted} MHz")


def on_vfo_dial_rotated(clicks_delta):
    """Rotation callback, receiving a signed step delta."""
    global current_frequency_hz
    current_frequency_hz += clicks_delta * 100
    current_frequency_hz = max(0, current_frequency_hz)
    refresh_frequency_display()


def refresh_armed_display():
    """Shows whether the dial is currently switched on."""
    if lbl_armed.winfo_exists():
        lbl_armed.configure(
            text="ARMED -- dial is live" if tuning_dial.is_pressed()
            else "OFF -- double-click to arm")


def on_double_click(dial):
    """
    Wired to double_click_command: ARMS the dial.

    Arming only, not toggling. Every mouse button steps the dial, so a plain
    double-click competes with ordinary clicking to turn the knob -- but only
    once the dial is live. While it is off nothing is bound, so this gesture
    cannot collide with anything.

    The widget passes the dial itself, so a handler needs no closure over the
    variable name.
    """
    dial.set_pressed(True)
    refresh_armed_display()
    print(f"double-click -> pressed = {dial.is_pressed()}")


def on_shift_double_click(dial):
    """
    Wired to shift_double_click_command: DISARMS the dial.

    Its own gesture precisely because the plain one is not safe to use for
    this while the dial is live.
    """
    dial.set_pressed(False)
    refresh_armed_display()
    print(f"shift-double-click -> pressed = {dial.is_pressed()}")


def my_custom_left_click():
    """Accelerated jump: two steps left per click."""
    tuning_dial.set_position_index(-2)


def my_custom_right_click():
    """Accelerated jump: two steps right per click."""
    tuning_dial.set_position_index(2)


def toggle_operational_state():
    """
    Locks and unlocks the dial.

    Note what this does to the latch: disabling switches the dial OFF as well
    as locking it, so unlocking leaves it inert until double-clicked again.
    That is the point of the combination -- a panel coming back from a lock
    cannot be nudged by accident.
    """
    target = "disabled" if tuning_dial.cget("state") == "normal" else "normal"
    tuning_dial.configure(state=target)
    btn_toggle.configure(
        text="Lock Dial" if target == "normal" else "Unlock Dial")
    refresh_armed_display()
    print(f"state = {tuning_dial.get_state()}  pressed = {tuning_dial.is_pressed()}")


if __name__ == "__main__":
    root = sCTk()
    root.title("sCTkDialContinuous -- latching test deck")
    root.geometry("420x460")

    base = sCTkFrame(root, corner_radius=8)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    sCTkLabelSecondary(base, text="Continuous VFO wheel",
                       font=("Arial", 12, "bold")).pack(pady=(12, 2))

    tuning_dial = sCTkDialContinuous(
        base,
        divisions=24,
        knob_diameter=130,
        command=on_vfo_dial_rotated,
        left_click_callback=my_custom_left_click,
        right_click_callback=my_custom_right_click,
        # --- the opt-in. Remove these two lines for the old behaviour. ---
        latching=True,
        double_click_command=on_double_click,
        shift_double_click_command=on_shift_double_click,
        shift_double_click_command=on_shift_double_click,
    )
    tuning_dial.pack(pady=10)

    lbl_armed = sCTkLabelSecondary(base, text="", font=("Arial", 11, "bold"))
    lbl_armed.pack(pady=(0, 6))

    lbl_vfo_display = sCTkLabelSecondary(base, text="VFO Freq: 14.032.000 MHz",
                                         font=("Arial", 11, "bold"))
    lbl_vfo_display.pack(pady=4)

    btn_toggle = sCTkButtonPrimary(base, text="Lock Dial",
                                   command=toggle_operational_state)
    btn_toggle.pack(side="bottom", pady=15)

    refresh_armed_display()

    print("--- boot ---")
    print(f"state   = {tuning_dial.get_state()}")
    print(f"pressed = {tuning_dial.is_pressed()}   (False: latching dials start off)")
    print("Try the wheel before double-clicking -- it should do nothing.\nShift-double-click to switch it back off.")
    print("------------\n")

    root.mainloop()
