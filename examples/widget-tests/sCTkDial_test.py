#!/usr/bin/python3
"""
Combined test bench for the three dial variants.

This one shows BOTH sides of the latching option side by side, which the
single-widget benches cannot:

  * The SELECTOR and the RANGE dial are built with `latching=True` and a
    `double_click_command` that toggles it. They start switched off and inert;
    double-click to arm. These are the controls where an accidental brush of
    the wheel does real damage -- changing mode, or slamming the volume.

  * The CONTINUOUS VFO wheel is built WITHOUT either argument, which is the
    default and the old behaviour: always live, pressed_map ignored and not
    required in its theme block. That is what opting out looks like -- you
    simply do not pass the arguments.

The two mechanisms are independent by design. `latching=True` gates the
input; `double_click_command` is a plain callback the widget never wires to
anything. Toggling the latch on a double-click is a choice this bench makes,
not something the widget assumes.

Note also what the lock does to a latching dial: disabling switches it off as
well as locking it, so unlocking leaves it inert until armed again. Watch the
selector and range dials after using the state dropdown -- the VFO wheel,
being non-latching, simply comes back live.
"""
import customtkinter as ctk

from scustomtkinter import (sCTk, sCTkFrame, sCTkComboBox, sCTkButtonPrimary,
                            sCTkLabelSecondary, sCTkSlider)
from scustomtkinter import sCTkDialContinuous, sCTkDialSelector, sCTkDialRange

OPERATING_MODES = ["CW", "USB", "LSB", "AM", "FM", "RTTY"]
current_frequency_hz = 14032000
audio_volume_pct = 25


def refresh_frequency_display():
    """Formats raw integers into a 14.032.000 style readout."""
    freq_str = f"{current_frequency_hz:08d}"
    formatted = f"{freq_str[-8:-6]}.{freq_str[-6:-3]}.{freq_str[-3:]}"
    if formatted.startswith("."):
        formatted = formatted[1:]
    if lbl_vfo_display.winfo_exists():
        lbl_vfo_display.configure(text=f"VFO Freq: {formatted} MHz")


def on_mode_switch_rotated(active_index):
    """Selector callback, receiving the selected label's index."""
    lbl_selector_display.configure(
        text=f"Mode: {OPERATING_MODES[active_index]} [Idx {active_index}]")


def on_volume_pot_rotated(absolute_value):
    """Range callback, receiving an absolute value."""
    lbl_range_display.configure(text=f"Volume: {int(absolute_value)}%")


def on_vfo_dial_rotated(clicks_delta):
    """Continuous callback, receiving a signed step delta."""
    global current_frequency_hz
    current_frequency_hz += clicks_delta * 100
    current_frequency_hz = max(0, current_frequency_hz)
    refresh_frequency_display()


def refresh_armed_labels():
    """Reports the latch state of the two latching dials."""
    for dial, label, name in ((dial_selector, lbl_sel_armed, "Mode switch"),
                              (dial_range, lbl_rng_armed, "Volume")):
        if label.winfo_exists():
            label.configure(
                text=f"{name}: ARMED" if dial.is_pressed()
                else f"{name}: off -- double-click to arm")


def on_dial_double_clicked(dial):
    """
    Shared double_click_command for the two latching dials: ARMS them.

    Arming only, not toggling. Every mouse button steps the dial, so a plain
    double-click competes with ordinary clicking to turn the knob -- but only
    once the dial is live. While it is off nothing is bound, so this gesture
    cannot collide with anything. Disarming gets its own gesture below.

    The widget passes the dial itself, so one handler serves both without a
    closure over either name.
    """
    dial.set_pressed(True)
    refresh_armed_labels()
    print(f"double-click -> {type(dial).__name__} armed")


def on_dial_shift_double_clicked(dial):
    """Shared shift_double_click_command: DISARMS the two latching dials."""
    dial.set_pressed(False)
    refresh_armed_labels()
    print(f"shift-double-click -> {type(dial).__name__} off")


def my_custom_left_click():
    """Accelerated jump on the VFO wheel: two steps left."""
    tuning_dial.set_position_index(-2)


def my_custom_right_click():
    """Accelerated jump on the VFO wheel: two steps right."""
    tuning_dial.set_position_index(2)


if __name__ == "__main__":
    app = sCTk()
    app.title("sCTkDial -- latching and non-latching side by side")
    app.geometry("1060x620")
    app.configure(fg_color=("#F1F5F9", "#1C1C1C"))

    main_deck = sCTkFrame(app, fg_color="transparent", border_width=0)
    main_deck.pack(padx=15, pady=15, fill="both", expand=True)

    # -----------------------------------------------------------------
    # 1. MODE SELECTOR -- latching
    # -----------------------------------------------------------------
    frame_selector = sCTkFrame(main_deck, fg_color=("#E2E8F0", "#262626"),
                               corner_radius=8)
    frame_selector.pack(side="left", padx=10, fill="both", expand=True)

    sCTkLabelSecondary(frame_selector, text="1. SELECTOR (latching)",
                       font=("Arial", 12, "bold")).pack(pady=(12, 2))

    lbl_selector_display = sCTkLabelSecondary(
        frame_selector, text="Mode: CW [Idx 0]", font=("Arial", 11, "bold"),
        text_color=("#1A4375", "#FF9100"))
    lbl_selector_display.pack(side="bottom", pady=(4, 20))

    lbl_sel_armed = sCTkLabelSecondary(frame_selector, text="",
                                       font=("Arial", 10))
    lbl_sel_armed.pack(side="bottom", pady=(0, 2))

    dial_selector = sCTkDialSelector(
        frame_selector, labels=OPERATING_MODES, arc_angle=270,
        command=on_mode_switch_rotated, knob_diameter=110,
        latching=True, double_click_command=on_dial_double_clicked,
        shift_double_click_command=on_dial_shift_double_clicked)
    dial_selector.pack(pady=10)
    dial_selector.set(0)

    # -----------------------------------------------------------------
    # 2. VOLUME POT -- latching
    # -----------------------------------------------------------------
    frame_range = sCTkFrame(main_deck, fg_color=("#E2E8F0", "#262626"),
                            corner_radius=8)
    frame_range.pack(side="left", padx=10, fill="both", expand=True)

    sCTkLabelSecondary(frame_range, text="2. RANGE (latching)",
                       font=("Arial", 12, "bold")).pack(pady=(12, 2))

    lbl_range_display = sCTkLabelSecondary(
        frame_range, text=f"Volume: {audio_volume_pct}%",
        font=("Arial", 11, "bold"), text_color=("#1A4375", "#FF9100"))
    lbl_range_display.pack(side="bottom", pady=(4, 20))

    lbl_rng_armed = sCTkLabelSecondary(frame_range, text="",
                                       font=("Arial", 10))
    lbl_rng_armed.pack(side="bottom", pady=(0, 2))

    dial_range = sCTkDialRange(
        frame_range, from_=0, to=100, arc_angle=270, divisions=5,
        command=on_volume_pot_rotated, knob_diameter=110,
        latching=True, double_click_command=on_dial_double_clicked,
        shift_double_click_command=on_dial_shift_double_clicked)
    dial_range.pack(pady=10)
    dial_range.set(audio_volume_pct)

    # -----------------------------------------------------------------
    # 3. VFO WHEEL -- NOT latching. This is the opt-out: no arguments.
    # -----------------------------------------------------------------
    frame_continuous = sCTkFrame(main_deck, fg_color=("#E2E8F0", "#262626"),
                                 corner_radius=8)
    frame_continuous.pack(side="left", padx=10, fill="both", expand=True)

    sCTkLabelSecondary(frame_continuous, text="3. CONTINUOUS (always live)",
                       font=("Arial", 12, "bold")).pack(pady=(12, 2))

    tuning_dial = sCTkDialContinuous(
        frame_continuous, divisions=24, command=on_vfo_dial_rotated,
        left_click_callback=my_custom_left_click,
        right_click_callback=my_custom_right_click,
        knob_diameter=130)
    tuning_dial.pack(pady=10)

    lbl_vfo_display = sCTkLabelSecondary(
        frame_continuous, text="VFO Freq: 14.032.000 MHz",
        font=("Arial", 11, "bold"), text_color=("#1A4375", "#FF9100"))
    lbl_vfo_display.pack(side="bottom", pady=(4, 20))

    sCTkLabelSecondary(frame_continuous,
                       text="no latching -- responds immediately",
                       font=("Arial", 10)).pack(side="bottom", pady=(0, 2))

    # -----------------------------------------------------------------
    # Knob size controls
    # -----------------------------------------------------------------
    for frame, dial, start in ((frame_selector, dial_selector, 110),
                               (frame_range, dial_range, 110),
                               (frame_continuous, tuning_dial, 130)):
        row = sCTkFrame(frame, fg_color="transparent", border_width=0)
        row.pack(fill="x", padx=15, pady=5)
        sCTkLabelSecondary(row, text="Knob:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w")
        slider = sCTkSlider(
            row, from_=70, to=160, width=120,
            command=lambda v, d=dial: d.configure(knob_diameter=int(v)))
        slider.grid(row=0, column=1, padx=5, pady=3, sticky="e")
        slider.set(start)

    # -----------------------------------------------------------------
    # Footer
    # -----------------------------------------------------------------
    footer = sCTkFrame(app, fg_color="transparent", border_width=0)
    footer.pack(fill="x", padx=25, pady=(5, 15))

    def on_sensitivity_changed(choice):
        ms_value = int(choice.split()[0].replace("ms", ""))
        tuning_dial._scroll_cooldown_seconds = ms_value / 1000.0
        dial_selector._scroll_cooldown_seconds = (ms_value / 1000.0) * 2.5
        dial_range._scroll_cooldown_seconds = ms_value / 1000.0

    sens_dropdown = sCTkComboBox(
        footer, values=["30ms (Fast)", "60ms (Normal)", "120ms (Slow)",
                        "250ms (Heavy)"],
        command=on_sensitivity_changed, width=150)
    sens_dropdown.pack(side="left", padx=10)
    sens_dropdown.set("60ms (Normal)")

    def on_state_toggle_changed(choice):
        """
        The panel lock.

        The two latching dials come back from this switched OFF, so they have
        to be armed again. The VFO wheel comes back live, because it does not
        latch.
        """
        target = "normal" if "Normal" in choice else "disabled"
        for d in (dial_selector, dial_range, tuning_dial):
            d.configure(state=target)
        refresh_armed_labels()
        print(f"panel {target}: "
              f"selector pressed={dial_selector.is_pressed()} "
              f"range pressed={dial_range.is_pressed()}")

    state_dropdown = sCTkComboBox(
        footer, values=["Normal State (Active)", "Disabled State (Locked)"],
        command=on_state_toggle_changed, width=180)
    state_dropdown.pack(side="left", padx=10)
    state_dropdown.set("Normal State (Active)")

    sCTkButtonPrimary(
        footer, text="Toggle Light/Dark", width=160,
        command=lambda: ctk.set_appearance_mode(
            "Light" if ctk.get_appearance_mode() == "Dark" else "Dark")
    ).pack(side="right", padx=10)

    refresh_armed_labels()

    print("--- boot ---")
    print("Selector and Range latch: inert until double-clicked.")
    print("Continuous does not: try its wheel straight away.")
    print("------------\n")

    app.mainloop()
