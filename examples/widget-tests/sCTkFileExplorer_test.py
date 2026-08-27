#!/usr/bin/python3

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for FIle Explorer
# =====================================================================

import os
import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkEntryPrimary, sCTkButtonPrimary
from scustomtkinter import sCTkOptionMenuPrimary, sCTk, sCTkLabelSecondary, sCTkFileExplorer

if __name__ == "__main__":
    root = sCTk()
    root.title("Standalone Embedded sCTkFileExplorer Panel View")
    root.geometry("600x720")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    lbl_monitor = sCTkLabelSecondary(base, text="Active Highlight Track: [None Selection]")
    lbl_monitor.pack(pady=10)

    def track_selection(explorer_instance):
        path = explorer_instance.selected_path.get()
        lbl_monitor.configure(text=f"Active Highlight Track: {os.path.basename(path)}")
        print(f"SINGLE-CLICK HIGHLIGHT: {path}")

    def execute_file(explorer_instance, path):
        print(f"DOUBLE-CLICK CONFIRMED! Launching: {path}")

    user_home_dir = os.path.expanduser("~")
    explorer = sCTkFileExplorer(base, type="file", initialdir=user_home_dir, filetypes=[".py", ".md", ".json"], command=track_selection, double_click_command=execute_file, width=540, height=350)
    explorer.pack(fill="both", expand=True, padx=15, pady=10)

    control_deck = sCTkFrame(base, border_width=1, corner_radius=6)
    control_deck.pack(fill="x", padx=15, pady=10)

    row1 = sCTkFrame(control_deck)
    row1.pack(fill="x", padx=10, pady=5)
    sCTkLabelSecondary(row1, text="Explorer Mode:", width=100, anchor="w").pack(side="left", padx=5)

    def on_mode_menu_changed(choice):
        mode_type = "file" if "File" in choice else "directory"
        explorer.set_mode(mode_type)
        entry_filter.configure(state="disabled" if mode_type == "directory" else "normal")

    opt_mode = sCTkOptionMenuPrimary(row1, values=["File Mode (Show Items)", "Directory Mode (Folders Only)"], command=on_mode_menu_changed, width=250)
    opt_mode.pack(side="left", padx=5)
    opt_mode.set("File Mode (Show Items)")

    row2 = sCTkFrame(control_deck)
    row2.pack(fill="x", padx=10, pady=5)
    sCTkLabelSecondary(row2, text="File Filter List:", width=100, anchor="w").pack(side="left", padx=5)

    entry_filter = sCTkEntryPrimary(row2, placeholder_text="['.py', '.md', '.json', '.txt']")
    entry_filter.pack(side="left", fill="x", expand=True, padx=5)
    entry_filter.bind("<Return>", lambda e: explorer.set_filetypes(entry_filter.get().strip()))

    row3 = sCTkFrame(control_deck)
    row3.pack(fill="x", padx=10, pady=5)
    sCTkLabelSecondary(row3, text="Jump to Path:", width=100, anchor="w").pack(side="left", padx=5)

    entry_path = sCTkEntryPrimary(row3, placeholder_text="Enter absolute directory path...")
    entry_path.insert(0, user_home_dir)
    entry_path.pack(side="left", fill="x", expand=True, padx=5)
    entry_path.bind("<Return>", lambda e: explorer.set_initial_dir(entry_path.get().strip()))

    def toggle_explorer_lock():
        target = "disabled" if explorer.get_state() == "normal" else "normal"
        explorer.configure(state=target)
        opt_mode.configure(state=target)
        entry_filter.configure(state=target)
        entry_path.configure(state=target)
        btn_lock.configure(text="Lock Explorer Deck" if target == "normal" else "Unlock Explorer Deck")

    btn_lock = sCTkButtonPrimary(base, text="Lock Explorer Deck", command=toggle_explorer_lock)
    btn_lock.pack(side="bottom", pady=10)
    root.mainloop()
