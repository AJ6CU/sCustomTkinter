#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Radiobutton
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary,sCTkLabelSecondary, sCTk, sCTkRadioButton

if __name__ == "__main__":

    root = sCTk()
    root.geometry("450x320")
    root.title("sCTkRadioButton Mutual Exclusion Validation Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    # Centralized StringVar linking both buttons together
    radio_var = ctk.StringVar(value="VFO_A")

    lbl_monitor = sCTkLabelSecondary(base, text="Active Telemetry Target: VFO_A")
    lbl_monitor.pack(pady=10)


    def print_result():
        lbl_monitor.configure(text=f"Active Telemetry Target: {radio_var.get()}")


    # 🔑 FIXED ALIGNMENT PACK ENGINE: Enforces left-anchoring with horizontal expansion
    widget = sCTkRadioButton(base, text="Primary VFO A Link Target", variable=radio_var, value="VFO_A",
                             command=print_result)
    widget.pack(expand=False, fill="x", padx=60, pady=10, anchor="w")

    widget2 = sCTkRadioButton(base, text="Secondary VFO B Link Target", variable=radio_var, value="VFO_B",
                              command=print_result)
    widget2.pack(expand=False, fill="x", padx=60, pady=10, anchor="w")


    def toggle_radio_lock():
        current_mode = widget.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        widget.configure(state=target)
        widget2.configure(state=target)
        btn_lock.configure(text="Lock Radio Switch" if target == "normal" else "Unlock Radio Switch")


    def toggle_skin_mode():
        current_skin = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_skin == "Dark" else "Dark")


    btn_lock = sCTkButtonPrimary(base, text="Lock Radio Switch", command=toggle_radio_lock)
    btn_lock.pack(pady=5)

    btn_theme = sCTkButtonPrimary(base, text="Simulate Global Theme Shift", command=toggle_skin_mode)
    btn_theme.pack(side="bottom", pady=10)

    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    widget.state("disabled")
    print("state (Disabled Pass) =", widget.get_state())
    widget.state("normal")
    print("state (Normal Pass)   =", widget.get_state())
    print("========================================\n")

    root.mainloop()