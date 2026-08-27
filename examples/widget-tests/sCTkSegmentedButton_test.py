#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for SegmentedButton
# =====================================================================

import os
import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary, sCTkLabelSecondary, sCTk, sCTkSegmentedButton

if __name__ == "__main__":

    root = sCTk()
    root.geometry("500x220")
    root.title("sCTkSegmentedButton Simplified Dual-Blue Pill Verification Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    widget = sCTkSegmentedButton(base, values=["DOG", "CAT", "Fish"])
    widget.pack(expand=False, fill="none", padx=10, pady=10)
    widget.set("DOG")


    def toggle_operational_lock():
        current_mode = widget.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        widget.configure(state=target)
        btn_lock.configure(text="Lock Button Row" if target == "normal" else "Unlock Button Row")


    def toggle_skin_mode():
        current_skin = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_skin == "Dark" else "Dark")


    btn_lock = sCTkButtonPrimary(base, text="Lock Button Row", command=toggle_operational_lock)
    btn_lock.pack(pady=5)

    btn_theme = sCTkButtonPrimary(base, text="Simulate Global Theme Shift", command=toggle_skin_mode)
    btn_theme.pack(side="bottom", pady=5)

    root.mainloop()