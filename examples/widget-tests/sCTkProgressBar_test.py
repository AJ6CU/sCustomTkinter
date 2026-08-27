#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for ProgressBar
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary, sCTkButtonSecondary, sCTkLabelSecondary, sCTk, sCTkProgressBar

if __name__ == "__main__":

    root = sCTk()
    root.geometry("450x260")
    root.title("sCTkProgressBar Interactive Testing Deck")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    initial_val = 0.45
    lbl_status = sCTkLabelSecondary(
        base,
        text=f"Telemetry Progress Output: {int(initial_val * 100)}% / 100%"
    )
    lbl_status.pack(pady=(10, 5))

    widget = sCTkProgressBar(base)
    widget.pack(expand=False, fill="x", padx=40, pady=10)
    widget.set(initial_val)

    def step_progress():
        if widget.get_state() == "disabled":
            print("⚠️ Cannot modify progress channel: Widget is currently locked!")
            return

        current_val = widget.get()
        next_val = current_val + 0.05
        if next_val > 1.0:
            next_val = 0.0

        widget.set(next_val)
        lbl_status.configure(text=f"Telemetry Progress Output: {int(next_val * 100)}% / 100%")

    btn_step = sCTkButtonPrimary(base, text="Step Telemetry Track (+5%)", command=step_progress)
    btn_step.pack(pady=(5, 5))

    def toggle_operational_lock():
        current_mode = widget.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        widget.configure(state=target)
        btn_lock.configure(text="Lock Indicator Track" if target == "normal" else "Unlock Indicator Track")
        btn_step.configure(state=target)

    btn_lock = sCTkButtonPrimary(base, text="Lock Indicator Track", command=toggle_operational_lock)
    btn_lock.pack(side="bottom", pady=(5, 10))

    def toggle_skin_mode():
        current_skin = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_skin == "Dark" else "Dark")

    btn_theme = sCTkButtonSecondary(base, text="Simulate Global Theme Shift", command=toggle_skin_mode)
    btn_theme.pack(side="bottom", pady=5)

    root.mainloop()