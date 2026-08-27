#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for ScrollableFrame
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkButtonPrimary, sCTkEntryPrimary, sCTk, sCTkScrollableFrame

if __name__ == "__main__":

    root = sCTk()
    root.title("ScrollableFrame Pure Baseline Verification")
    root.geometry("450x420")

    test_frame = sCTkScrollableFrame(root, width=380, height=250, label_text="Telemetry Viewport Container")
    test_frame.pack(padx=20, pady=20, fill="both", expand=True)

    for i in range(12):
        mock_entry = sCTkEntryPrimary(test_frame, placeholder_text=f"Active Transceiver Channel {i + 1}")
        mock_entry.pack(padx=10, pady=5, fill="x")

    _is_locked = False
    def toggle_cascade_lockout():
        global _is_locked
        _is_locked = not _is_locked
        target = "disabled" if _is_locked else "normal"

        toggle_btn.configure(text="Enforce State: NORMAL" if _is_locked else "Enforce State: DISABLED")

        # 🔑 CLEAN APPLICATION-LEVEL LOOKOUT LOOP CASCADE:
        # The external control logic explicitly dictates when and how to update nested elements!
        for entry_widget in test_frame.get_children():
            if hasattr(entry_widget, "configure"):
                try:
                    entry_widget.configure(state=target)
                except Exception:
                    pass

    toggle_btn = sCTkButtonPrimary(root, text="Enforce State: DISABLED", command=toggle_cascade_lockout)
    toggle_btn.pack(side="bottom", pady=15)

    btn_theme = sCTkButtonPrimary(root, text="Toggle Theme Skin", command=lambda: ctk.set_appearance_mode(
        "Dark" if ctk.get_appearance_mode() == "Light" else "Light"))
    btn_theme.pack(side="bottom", pady=5)

    test_frame._toggle_scroll_bindings(bind=True)
    root.mainloop()