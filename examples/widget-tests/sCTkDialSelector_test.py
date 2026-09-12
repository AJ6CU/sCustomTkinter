#!/usr/bin/python3
"""
Test bench for sCTkDialSelector.

Demonstrates the LATCHING option: the dial starts switched off and inert, and
a double-click arms it.

    mode_selector = sCTkDialSelector(
        base,
        latching=True,
        double_click_command=lambda d: d.toggle_pressed(),
    )

`latching=True` makes the dial start switched off, ignoring clicks, drags and
the wheel until set_pressed(True). It draws from the top-level theme colours
while off and from pressed_map while on.

`double_click_command` is a plain callback -- the widget does not wire it to
the latch. Toggling on a double-click is the application's choice, and this
bench makes that choice explicitly.

A mode switch is the case where this earns its keep: changing band or
sideband by accidentally brushing the wheel is worse than having to arm the
control first.

TO OPT OUT, drop both arguments. A dial built without `latching` is always
live, exactly as before, and ignores pressed_map entirely. That is the
default.
"""
import customtkinter as ctk
from scustomtkinter import (sCTk, sCTkFrame, sCTkButtonPrimary,
                            sCTkLabelSecondary, sCTkDialSelector)

OPERATING_MODES = ["AM", "FM", "LSB", "USB", "CW"]


def refresh_armed_display():
    """Shows whether the dial is currently switched on."""
    if lbl_armed.winfo_exists():
        lbl_armed.configure(
            text="ARMED -- mode switch is live" if mode_selector.is_pressed()
            else "OFF -- double-click to arm")


def on_double_click(dial):
    """
    Wired to double_click_command: ARMS the dial.

    Arming only, not toggling. Every mouse button steps the dial, so a plain
    double-click competes with ordinary clicking to turn the knob -- but only
    once the dial is live. While it is off nothing is bound, so this gesture
    cannot collide with anything.
    """
    dial.set_pressed(True)
    refresh_armed_display()
    print(f"double-click -> pressed = {dial.is_pressed()}")


def on_shift_double_click(dial):
    """Wired to shift_double_click_command: DISARMS the dial."""
    dial.set_pressed(False)
    refresh_armed_display()
    print(f"shift-double-click -> pressed = {dial.is_pressed()}")


def on_mode_changed(index):
    """Rotation callback, receiving the selected label's index."""
    lbl_mode_tag.configure(text=f"Selected mode: {OPERATING_MODES[index]}")


def my_custom_left_click():
    """Accelerated jump: two positions left per click."""
    mode_selector.set(mode_selector.get() - 2)


def my_custom_right_click():
    """Accelerated jump: two positions right per click."""
    mode_selector.set(mode_selector.get() + 2)


def toggle_widget_lock():
    """
    Locks and unlocks the dial.

    Disabling switches the dial OFF as well as locking it, so unlocking leaves
    it inert until double-clicked again.
    """
    target = "disabled" if mode_selector.get_state() == "normal" else "normal"
    mode_selector.configure(state=target)
    btn_lock.configure(
        text="Unlock switch" if target == "disabled" else "Lock switch")
    refresh_armed_display()
    print(f"state = {mode_selector.get_state()}  pressed = {mode_selector.is_pressed()}")


if __name__ == "__main__":
    root = sCTk()
    root.geometry("460x430")
    root.title("sCTkDialSelector -- latching test bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    lbl_mode_tag = sCTkLabelSecondary(base, text="Selected mode: AM",
                                      font=("Arial", 11, "bold"))
    lbl_mode_tag.pack(pady=(15, 4))

    lbl_armed = sCTkLabelSecondary(base, text="", font=("Arial", 11, "bold"))
    lbl_armed.pack(pady=(0, 10))

    mode_selector = sCTkDialSelector(
        base,
        labels=OPERATING_MODES,
        arc_angle=180,
        knob_diameter=120,
        command=on_mode_changed,
        left_click_callback=my_custom_left_click,
        right_click_callback=my_custom_right_click,
        # --- the opt-in. Remove these two lines for the old behaviour. ---
        latching=True,
        double_click_command=on_double_click,
        shift_double_click_command=on_shift_double_click,
    )
    mode_selector.pack(expand=True, fill="none", padx=10, pady=10)

    btn_lock = sCTkButtonPrimary(base, text="Lock switch",
                                 command=toggle_widget_lock)
    btn_lock.pack(side="bottom", pady=15)

    refresh_armed_display()

    print("--- boot ---")
    print(f"state   = {mode_selector.get_state()}")
    print(f"pressed = {mode_selector.is_pressed()}   (False: latching dials start off)")
    print("Try the wheel before double-clicking -- it should do nothing.\nShift-double-click to switch it back off.")
    print("------------\n")

    root.mainloop()
