#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Selector
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkButtonPrimary, sCTk, sCTkSelector


if __name__ == "__main__":
    def on_confirm(): print(f"Active Selection Telemetry Array: {theSelector.get_selections()}")

    root = sCTk()
    root.geometry("250x420")
    root.title("sCTkSelector Validation Bench")

    items = ["vw", "porsche", "roadster", "tesla", "ferrari", "mclaren"]
    theSelector = sCTkSelector(root, items=items, multiple_choices=True)
    theSelector.pack(expand=True, fill="both", padx=15, pady=15)

    def toggle_selector_lock():
        target = "disabled" if theSelector.get_state() == "normal" else "normal"
        theSelector.configure(state=target)
        btn_lock.configure(text="Lock Selector Deck" if target == "normal" else "Unlock Selector Deck")

    def toggle_skin_mode():
        current_skin = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_skin == "Dark" else "Dark")

    confirm_btn = sCTkButtonPrimary(root, text="Confirm Selections", command=on_confirm)
    confirm_btn.pack(pady=5)
    btn_lock = sCTkButtonPrimary(root, text="Lock Selector Deck", command=toggle_selector_lock)
    btn_lock.pack(pady=5)
    btn_theme = sCTkButtonPrimary(root, text="Simulate Global Theme Shift", command=toggle_skin_mode)
    btn_theme.pack(pady=(5, 15))

    root.mainloop()







