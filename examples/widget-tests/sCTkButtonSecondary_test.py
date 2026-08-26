#!/usr/bin/python3

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Secondary Button
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTk, sCTkButtonSecondary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("450x320")
    root.title("Secondary Button Real-Time Validation Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    widget = sCTkButtonSecondary(base, text="System Action Button")
    widget.pack(padx=40, pady=10, fill="x")

    def toggle_disabled_lock():
        target = "disabled" if widget.get_state() == "normal" else "normal"
        widget.configure(state=target)
        btn_lock.configure(text="Lock Button" if target == "normal" else "Unlock Button")

    def toggle_skin_mode():
        current_skin = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_skin == "Dark" else "Dark")

    btn_lock = ctk.CTkButton(base, text="Lock Button", command=toggle_disabled_lock)
    btn_lock.pack(pady=5)

    btn_theme = ctk.CTkButton(base, text="Simulate Global Theme Shift", command=toggle_skin_mode)
    btn_theme.pack(side="bottom", pady=10)

    root.mainloop()
