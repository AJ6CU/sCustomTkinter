#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Path Chooser
# =====================================================================

import os
import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary, sCTkLabelSecondary, sCTk, sCTkPathChooser

if __name__ == "__main__":

    root = sCTk()
    root.title("Compound Path Chooser Test Suite")
    root.geometry("700x260")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    lbl_monitor = sCTkLabelSecondary(base, text="Active Telemetry Target: [None Selection]")
    lbl_monitor.pack(pady=10)

    def print_result(path):
        lbl_monitor.configure(text=f"Active Telemetry Target: {os.path.basename(path)}")
        print(f"MAIN CONSOLE PATH SELECTION -> {path}")

    chooser = sCTkPathChooser(
        base, type="file", title="Select Log Target", filetypes=[".py"], command=print_result,
        justify="right", width=550, height=50, state="normal", entry_height=40, btn_width=40,
        btn_height=40, btn_text="▶", browser_width=550, browser_height=500
    )
    chooser.pack(padx=20, pady=15)

    def toggle_chooser_lock():
        target = "disabled" if chooser.get_state() == "normal" else "normal"
        chooser.configure(state=target)
        btn_lock.configure(text="Lock Chooser Deck" if target == "normal" else "Unlock Chooser Deck")
        print(f"Logged Verification Hook -> chooser.get_state() = {chooser.get_state()}")

    btn_lock = sCTkButtonPrimary(base, text="Lock Chooser Deck", command=toggle_chooser_lock)
    btn_lock.pack(side="bottom", pady=5)

    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    chooser.state("disabled")
    print("state (Disabled Pass) =", chooser.get_state())
    chooser.state("normal")
    print("state (Normal Pass)   =", chooser.get_state())
    print("========================================\n")

    root.mainloop()