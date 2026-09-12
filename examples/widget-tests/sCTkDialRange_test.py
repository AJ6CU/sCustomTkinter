#!/usr/bin/python3
"""
Test bench for sCTkDialRange.

Demonstrates the LATCHING option: the dial starts switched off and inert, and
a double-click arms it.

    volume_pot = sCTkDialRange(
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

TO OPT OUT, drop both arguments. A dial built without `latching` is always
live, exactly as before, and ignores pressed_map entirely. That is the
default.
"""
import customtkinter as ctk
from scustomtkinter import (sCTk, sCTkFrame, sCTkButtonPrimary,
                            sCTkLabelSecondary, sCTkDialRange)


def refresh_armed_display():
    """Shows whether the dial is currently switched on."""
    if lbl_armed.winfo_exists():
        lbl_armed.configure(
            text="ARMED -- dial is live" if volume_pot.is_pressed()
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


def my_custom_left_click():
    """Accelerated jump: three units down per click."""
    volume_pot.set(volume_pot.get() - 3)


def my_custom_right_click():
    """Accelerated jump: three units up per click."""
    volume_pot.set(volume_pot.get() + 3)


def toggle_pot_lock():
    """
    Locks and unlocks the dial.

    Disabling switches the dial OFF as well as locking it, so unlocking leaves
    it inert until double-clicked again -- a panel coming back from a lock
    cannot be nudged by accident.
    """
    target = "disabled" if volume_pot.get_state() == "normal" else "normal"
    volume_pot.configure(state=target)
    btn_toggle.configure(
        text="Unlock volume" if target == "disabled" else "Lock volume")
    refresh_armed_display()
    print(f"state = {volume_pot.get_state()}  pressed = {volume_pot.is_pressed()}")


if __name__ == "__main__":
    root = sCTk()
    root.geometry("460x430")
    root.title("sCTkDialRange -- latching test bench")

    base = sCTkFrame(root, corner_radius=8)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    lbl_volume = sCTkLabelSecondary(base, text="AF Volume: 5 %",
                                    font=("Arial", 11, "bold"))
    lbl_volume.pack(pady=(15, 4))

    lbl_armed = sCTkLabelSecondary(base, text="", font=("Arial", 11, "bold"))
    lbl_armed.pack(pady=(0, 10))

    volume_pot = sCTkDialRange(
        base,
        from_=0,
        to=100,
        divisions=5,
        arc_angle=270,
        knob_diameter=120,
        command=lambda val: lbl_volume.configure(text=f"AF Volume: {int(val)} %"),
        left_click_callback=my_custom_left_click,
        right_click_callback=my_custom_right_click,
        # --- the opt-in. Remove these two lines for the old behaviour. ---
        latching=True,
        double_click_command=on_double_click,
        shift_double_click_command=on_shift_double_click,
    )
    volume_pot.pack(expand=True, fill="none", padx=10, pady=10)
    volume_pot.set(5)

    btn_toggle = sCTkButtonPrimary(base, text="Lock volume",
                                   command=toggle_pot_lock)
    btn_toggle.pack(side="bottom", pady=15)

    refresh_armed_display()

    print("--- boot ---")
    print(f"state   = {volume_pot.get_state()}")
    print(f"pressed = {volume_pot.is_pressed()}   (False: latching dials start off)")
    print("Try the wheel before double-clicking -- it should do nothing.\nShift-double-click to switch it back off.")
    print("------------\n")

    root.mainloop()
