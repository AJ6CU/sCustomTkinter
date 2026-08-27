#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Slider
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkLabelSecondary, sCTk, sCTkSlider

if __name__ == "__main__":

    root = sCTk()
    root.geometry("450x220")
    root.title("Slider Real-Time Telemetry Monitor")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    lbl_telemetry = sCTkLabelSecondary(base, text="Slider Coordinate: 0.450", font=("Courier New", 12, "bold"))

    widget = sCTkSlider(base)
    widget.configure(command=lambda val: lbl_telemetry.configure(text=f"Slider Coordinate: {val:.3f}"))
    widget.pack(expand=False, fill="x", padx=40, pady=15)
    widget.set(0.450)
    lbl_telemetry.pack(pady=10)

    # Verify look states transition flawlessly on the console
    widget.state("disabled")
    print("--- DISABLED PASS ---")
    print("state (Disabled Pass) =", widget.get_state())

    widget.state("normal")
    print("\n--- NORMAL PASS ---")
    print("state (Normal Pass)   =", widget.get_state())

    root.mainloop()