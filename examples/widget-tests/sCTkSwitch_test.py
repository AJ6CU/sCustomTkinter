#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Switch
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary, sCTk, sCTkSwitch


if __name__ == "__main__":

    root = sCTk()
    root.geometry("450x240")
    root.title("sCTkSwitch Native Container Validation Bench")

    base_container = sCTkFrame(root, border_width=2)
    base_container.pack(expand=True, fill="both", padx=30, pady=30)

    widget = sCTkSwitch(base_container, text="Lock Transceiver Pre-Amp Link")
    widget.pack(expand=True, fill="none", padx=10, pady=10)

    def toggle_panel_lock():
        current_mode = widget.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        widget.configure(state=target)
        btn_lock.configure(text="Unlock Switch (Set 'normal')" if target == "disabled" else "Lock Switch (Set 'disabled')")
        print(f"Logged Verification Hook -> widget.get_state() = {widget.get_state()}")

    btn_lock = sCTkButtonPrimary(root, text="Lock Switch (Set 'disabled')", command=toggle_panel_lock)
    btn_lock.pack(side="bottom", pady=15)

    root.mainloop()

