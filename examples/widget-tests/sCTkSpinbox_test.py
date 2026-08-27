#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Spinbox
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkComboBox, sCTkLabelSecondary, sCTkEntryPrimary, sCTk, sCTkSpinbox


if __name__ == "__main__":

    app = sCTk()
    app.title("sCTk Advanced Spinbox Tester Deck")
    app.geometry("490x740")
    app.configure(fg_color=("#F1F5F9", "#1C1C1C"))

    def on_spinbox_value_changed(val):
        if isinstance(val, float): vfo_readout.configure(text=f"Telemetry Output: {val:.3f}")
        else: vfo_readout.configure(text=f"Telemetry Output: '{str(val)}'")

    dashboard_panel = sCTkFrame(app, fg_color="transparent", border_width=0)
    dashboard_panel.pack(padx=25, pady=15, fill="both", expand=True)

    vfo_readout = sCTkLabelSecondary(dashboard_panel, text="Telemetry Output: Initializing...", font=("Arial", 22, "bold"), text_color=("#1A4375", "#FF9100"))
    vfo_readout.pack(pady=10)

    spinbox = sCTkSpinbox(dashboard_panel, from_=1.0, to=50.0, step_size=0.5, wrap=True, justify="center", placeholder_text="Click Me", command=on_spinbox_value_changed, width=180, height=34)
    spinbox.pack(pady=10)

    control_frame = sCTkFrame(dashboard_panel, fg_color=("#E2E8F0", "#262626"), corner_radius=6)
    control_frame.pack(fill="both", expand=True, padx=5, pady=10)
    control_frame.grid_columnconfigure(0, weight=1); control_frame.grid_columnconfigure(1, weight=1)

    lbl_state = sCTkLabelSecondary(control_frame, text="Component State:", font=("Arial", 11, "bold"))
    lbl_state.grid(row=0, column=0, padx=15, pady=5, sticky="w")
    state_dropdown = sCTkComboBox(control_frame, values=["Normal State (Active)", "Disabled State (Locked)"], command=lambda choice: spinbox.configure(state="disabled" if "Disabled" in choice else "normal"), width=170)
    state_dropdown.grid(row=0, column=1, padx=15, pady=5, sticky="e"); state_dropdown.set("Normal State (Active)")

    lbl_justify = sCTkLabelSecondary(control_frame, text="Text Alignment (Justify):", font=("Arial", 11, "bold"))
    lbl_justify.grid(row=1, column=0, padx=15, pady=5, sticky="w")
    justify_dropdown = sCTkComboBox(control_frame, values=["Center", "Left", "Right"], command=lambda choice: spinbox.configure(justify=choice.lower()), width=170)
    justify_dropdown.grid(row=1, column=1, padx=15, pady=5, sticky="e"); justify_dropdown.set("Center")

    lbl_format = sCTkLabelSecondary(control_frame, text="Masking Format Pattern:", font=("Arial", 11, "bold"))
    lbl_format.grid(row=2, column=0, padx=15, pady=5, sticky="w")
    format_dropdown = sCTkComboBox(control_frame, values=["None (Default)", "%.1f kHz", "{:.2f}", "{:.3f}"], command=lambda choice: spinbox.configure(format={"%.1f kHz": "%.1f kHz", "{:.2f}": "{:.2f}", "{:.3f}": "{:.3f}", "None (Default)": ""}.get(choice, "")), width=170)
    format_dropdown.grid(row=2, column=1, padx=15, pady=5, sticky="e"); format_dropdown.set("None (Default)")

    lbl_wrap = sCTkLabelSecondary(control_frame, text="Boundary Iteration Wrap:", font=("Arial", 11, "bold"))
    lbl_wrap.grid(row=3, column=0, padx=15, pady=5, sticky="w")
    wrap_dropdown = ctk.CTkComboBox(control_frame, values=["True (Loop Enabled)", "False (Hard Limits)"], command=lambda choice: spinbox.configure(wrap=True if "True" in choice else False), width=170)
    wrap_dropdown.grid(row=3, column=1, padx=15, pady=5, sticky="e"); wrap_dropdown.set("True (Loop Enabled)")

    lbl_mode = sCTkLabelSecondary(control_frame, text="Data Array Input Mode:", font=("Arial", 11, "bold"))
    lbl_mode.grid(row=4, column=0, padx=15, pady=5, sticky="w")
    def on_mode_changed(choice):
        if "Discrete List" in choice: spinbox.set_values(txt_custom_values.get())
        else: spinbox.set_values([]); spinbox.set(5.0)
    mode_dropdown = sCTkComboBox(control_frame, values=["Numerical Mode (1.0 - 50.0)", "Discrete List Mode (Strings)"], command=on_mode_changed, width=170)
    mode_dropdown.grid(row=4, column=1, padx=15, pady=5, sticky="e"); mode_dropdown.set("Numerical Mode (1.0 - 50.0)")

    lbl_custom_vals = sCTkLabelSecondary(control_frame, text="List Strings Configuration:", font=("Arial", 11, "bold"))
    lbl_custom_vals.grid(row=5, column=0, padx=15, pady=5, sticky="w")
    txt_custom_values = sCTkEntryPrimary(control_frame, width=170, height=28, placeholder_text="Item1 'Item Two' Item3...")
    txt_custom_values.grid(row=5, column=1, padx=15, pady=5, sticky="e"); txt_custom_values.insert(0, 'Slow Normal Fast "Turbo Speed" Max')
    txt_custom_values.bind("<Return>", lambda e: spinbox.set_values(txt_custom_values.get()) if "Discrete List" in mode_dropdown.get() else None)

    lbl_side = sCTkLabelSecondary(control_frame, text="Hardware Button Side:", font=("Arial", 11, "bold"))
    lbl_side.grid(row=6, column=0, padx=15, pady=5, sticky="w")
    side_dropdown = sCTkComboBox(control_frame, values=["Right", "Left", "Split"], command=lambda choice: spinbox.configure(button_side=choice.lower()), width=170)
    side_dropdown.grid(row=6, column=1, padx=15, pady=5, sticky="e"); side_dropdown.set("Right")

    lbl_orient = sCTkLabelSecondary(control_frame, text="Control Grid Orientation:", font=("Arial", 11, "bold"))
    lbl_orient.grid(row=7, column=0, padx=15, pady=5, sticky="w")
    orient_dropdown = sCTkComboBox(control_frame, values=["Vertical", "Horizontal"], command=lambda choice: spinbox.configure(orientation=choice.lower()), width=170)
    orient_dropdown.grid(row=7, column=1, padx=15, pady=5, sticky="e"); orient_dropdown.set("Vertical")

    lbl_arrow_size = sCTkLabelSecondary(control_frame, text="Arrow Glyphs Font Size:", font=("Arial", 11, "bold"))
    lbl_arrow_size.grid(row=8, column=0, padx=15, pady=5, sticky="w")
    arrow_size_dropdown = sCTkComboBox(control_frame, values=["8 pt (Default)", "11 pt (Medium)", "14 pt (Large)", "18 pt"], command=lambda choice: spinbox.configure(arrow_font_size=int(choice.split()[0])), width=170)
    arrow_size_dropdown.grid(row=8, column=1, padx=15, pady=5, sticky="e"); arrow_size_dropdown.set("8 pt (Default)")

    app.mainloop()
