#!/usr/bin/python3
"""
sCTkDial_Harness.py

A complete, self-contained interactive test bench for the sCTkDial library.
Demonstrates synchronized theme shifts, hardware sensitivity calibration,
and dual-routing state lock configurations on your monitor face.
"""
import customtkinter as ctk

# Cross-module package imports
from scustomtkinter import sCTk, sCTkFrame, sCTkComboBox, sCTkButtonPrimary, sCTkButtonPrimary, sCTkLabelSecondary, sCTkSlider


# Concrete module lookups for our child dials
from scustomtkinter import sCTkDialContinuous, sCTkDialSelector, sCTkDialRange

# Global frequency tracking registers (Simulating independent rig states)
operating_modes = ["CW", "USB", "LSB", "AM", "FM", "RTTY"]
current_frequency_hz = 14032000
audio_volume_pct = 25

def refresh_frequency_display():
    """Formats raw integers into standard 14.032.000 layout specifications."""
    global current_frequency_hz
    freq_str = f"{current_frequency_hz:08d}"
    formatted_freq = f"{freq_str[-8:-6]}.{freq_str[-6:-3]}.{freq_str[-3:]}"
    if formatted_freq.startswith("."):
        formatted_freq = formatted_freq[1:]

    if 'lbl_vfo_display' in globals() and lbl_vfo_display.winfo_exists():
        lbl_vfo_display.configure(text=f"VFO Freq: {formatted_freq} MHz")

def on_mode_switch_rotated(active_index):
    """Callback for Selector Module: Receives strict integer indexes."""
    mode_string = operating_modes[active_index]
    if 'lbl_selector_display' in globals() and lbl_selector_display.winfo_exists():
        lbl_selector_display.configure(text=f"Mode: {mode_string} [Idx {active_index}]")

def on_volume_pot_rotated(absolute_value):
    """Callback for Range Module: Receives absolute value integers."""
    if 'lbl_range_display' in globals() and lbl_range_display.winfo_exists():
        lbl_range_display.configure(text=f"Volume: {absolute_value}%")

def on_vfo_dial_rotated(clicks_delta):
    """Unified event-driven callback called automatically on rotation changes."""
    global current_frequency_hz
    current_frequency_hz += clicks_delta * 100
    current_frequency_hz = max(0, current_frequency_hz)
    refresh_frequency_display()

# Custom accelerated override routines (Moves physical dial 2 notches on click events)
def my_custom_left_click():
    if tuning_dial.cget("state") == "disabled": return
    tuning_dial.set_position_index(-2)

def my_custom_right_click():
    if tuning_dial.cget("state") == "disabled": return
    tuning_dial.set_position_index(2)

if __name__ == "__main__":

    app = sCTk()
    app.title("sCTkDial Core System Validation Bench")
    app.geometry("1060x580")
    app.configure(fg_color=("#F1F5F9", "#1C1C1C"))

    main_deck = sCTkFrame(app, fg_color="transparent", border_width=0)
    main_deck.pack(padx=15, pady=15, fill="both", expand=True)

    # -----------------------------------------------------------------
    # CONTAINER 1: THE DISCRETE MODE SELECTOR SWITCH
    # -----------------------------------------------------------------
    frame_selector = sCTkFrame(main_deck, fg_color=("#E2E8F0", "#262626"), corner_radius=8)
    frame_selector.pack(side="left", padx=10, fill="both", expand=True)

    lbl_sel_title = sCTkLabelSecondary(frame_selector, text="1. SELECTOR SWITCH", font=("Arial", 12, "bold"))
    lbl_sel_title.pack(pady=(12, 2))

    lbl_selector_display = sCTkLabelSecondary(frame_selector, text="Mode: CW [Idx 0]", font=("Arial", 11, "bold"), text_color=("#1A4375", "#FF9100"))
    lbl_selector_display.pack(side="bottom", pady=20)

    dial_selector = sCTkDialSelector(frame_selector, labels=operating_modes, arc_angle=270, command=on_mode_switch_rotated, diameter=110)
    dial_selector.pack(pady=10)
    dial_selector.set(0)

    # -----------------------------------------------------------------
    # CONTAINER 2: THE HARD END-STOP POTENTIOMETER (RANGE)
    # -----------------------------------------------------------------
    frame_range = sCTkFrame(main_deck, fg_color=("#E2E8F0", "#262626"), corner_radius=8)
    frame_range.pack(side="left", padx=10, fill="both", expand=True)

    lbl_rng_title = sCTkLabelSecondary(frame_range, text="2. POTENTIOMETER (RANGE)", font=("Arial", 12, "bold"))
    lbl_rng_title.pack(pady=(12, 2))

    lbl_range_display = sCTkLabelSecondary(frame_range, text=f"Volume: {audio_volume_pct}%", font=("Arial", 11, "bold"), text_color=("#1A4375", "#FF9100"))
    lbl_range_display.pack(side="bottom", pady=20)

    dial_range = sCTkDialRange(frame_range, from_=0, to=100, arc_angle=270, command=on_volume_pot_rotated, diameter=110, divisions=5)
    dial_range.pack(pady=10)
    dial_range.set(audio_volume_pct)

    # -----------------------------------------------------------------
    # CONTAINER 3: THE INFINITE FLYWHEEL VFO ENCODER (CONTINUOUS)
    # -----------------------------------------------------------------
    frame_continuous = sCTkFrame(main_deck, fg_color=("#E2E8F0", "#262626"), corner_radius=8)
    frame_continuous.pack(side="left", padx=10, fill="both", expand=True)

    lbl_vfo_title = sCTkLabelSecondary(frame_continuous, text="3. INFINITE VFO WHEEL", font=("Arial", 12, "bold"))
    lbl_vfo_title.pack(pady=(12, 2))

    tuning_dial = sCTkDialContinuous(
        frame_continuous,
        divisions=24,
        command=on_vfo_dial_rotated,
        left_click_callback=my_custom_left_click,
        right_click_callback=my_custom_right_click,
        diameter=130
    )
    tuning_dial.pack(pady=10)

    lbl_vfo_display = sCTkLabelSecondary(frame_continuous, text="VFO Freq: 14.032.000 MHz", font=("Arial", 11, "bold"), text_color=("#1A4375", "#FF9100"))
    lbl_vfo_display.pack(side="bottom", pady=20)

    # Sliders and controls packing
    f_sel_ctrl = sCTkFrame(frame_selector, fg_color="transparent", border_width=0)
    f_sel_ctrl.pack(fill="x", padx=15, pady=5)
    sCTkLabelSecondary(f_sel_ctrl, text="Size:", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
    s_sel_size = sCTkSlider(f_sel_ctrl, from_=70, to=160, command=lambda v: dial_selector.configure(diameter=int(v)), width=120)
    s_sel_size.grid(row=0, column=1, padx=5, pady=3, sticky="e")
    s_sel_size.set(110)

    f_rng_ctrl = sCTkFrame(frame_range, fg_color="transparent", border_width=0)
    f_rng_ctrl.pack(fill="x", padx=15, pady=5)
    sCTkLabelSecondary(f_rng_ctrl, text="Size:", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
    s_rng_size = sCTkSlider(f_rng_ctrl, from_=70, to=160, command=lambda v: dial_range.configure(diameter=int(v)), width=120)
    s_rng_size.grid(row=0, column=1, padx=5, pady=3, sticky="e")
    s_rng_size.set(110)

    f_vfo_ctrl = sCTkFrame(frame_continuous, fg_color="transparent", border_width=0)
    f_vfo_ctrl.pack(fill="x", padx=15, pady=5)
    sCTkLabelSecondary(f_vfo_ctrl, text="Size:", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
    s_vfo_size = sCTkSlider(f_vfo_ctrl, from_=70, to=160, command=lambda v: tuning_dial.configure(diameter=int(v)), width=120)
    s_vfo_size.grid(row=0, column=1, padx=5, pady=3, sticky="e")
    s_vfo_size.set(130)

    footer = sCTkFrame(app, fg_color="transparent", border_width=0)
    footer.pack(fill="x", padx=25, pady=(5, 15))

    def on_sensitivity_changed(choice):
        numeric_part = choice.split()
        ms_value = int(numeric_part[0].replace("ms", ""))
        tuning_dial._scroll_cooldown_seconds = ms_value / 1000.0
        dial_selector._scroll_cooldown_seconds = (ms_value / 1000.0) * 2.5
        dial_range._scroll_cooldown_seconds = ms_value / 1000.0

    sens_dropdown = sCTkComboBox(footer, values=["30ms (Fast)", "60ms (Normal)", "120ms (Slow)", "250ms (Heavy)"], command=on_sensitivity_changed, width=150)
    sens_dropdown.pack(side="left", padx=10)
    sens_dropdown.set("60ms (Normal)")

    def on_state_toggle_changed(choice):
        target_state = "normal" if "Normal" in choice else "disabled"
        dial_selector.configure(state=target_state)
        dial_range.configure(state=target_state)
        tuning_dial.configure(state=target_state)
        s_sel_size.configure(state=target_state)
        s_rng_size.configure(state=target_state)
        s_vfo_size.configure(state=target_state)

    state_dropdown = sCTkComboBox(footer, values=["Normal State (Active)", "Disabled State (Locked)"], command=on_state_toggle_changed, width=180)
    state_dropdown.pack(side="left", padx=10)
    state_dropdown.set("Normal State (Active)")

    theme_btn = sCTkButtonPrimary(footer, text="Toggle Layout Themes", command=lambda: ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark"), width=160)
    theme_btn.pack(side="right", padx=10)

    app.mainloop()
