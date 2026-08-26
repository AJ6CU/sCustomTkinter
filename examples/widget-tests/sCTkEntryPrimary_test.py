#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Entry Secondary
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrameLabeledSecondary, sCTkButtonPrimary, sCTk, sCTkLabelTertiary, sCTkEntrySecondary

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
import sCTkThemes
from sCTkFrame import sCTkFrame

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("500x450")
    root.title("sCTkEntryPrimary Real-Time Validation Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    widget = sCTkEntryPrimary(base, placeholder_text="Enter Transceiver Callsign...")
    widget.pack(fill="x", padx=20, pady=20)

    def toggle_logger_states():
        """Cycles operational states between active feed and locked desaturated tracks."""
        current_state = widget.get_state()
        target = "disabled" if current_state == "normal" else "normal"

        widget.configure(state=target)
        btn_toggle.configure(text="Activate Entry Field" if target == "disabled" else "Lock Entry Field")
        print(f"Logged Verification Hook -> widget.get_state() = {widget.get_state().upper()}")

    def toggle_appearance_skin():
        current_mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_mode == "Dark" else "Dark")

    btn_toggle = ctk.CTkButton(base, text="Lock Entry Field", command=toggle_logger_states)
    btn_toggle.pack(fill="x", padx=10, pady=5)

    btn_theme = ctk.CTkButton(base, text="Toggle Theme Skin", command=toggle_appearance_skin)
    btn_theme.pack(fill="x", padx=10, pady=5)

    root.mainloop()
