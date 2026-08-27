#!/usr/bin/python3

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Frame Outlined
# =====================================================================

from scustomtkinter import (sCTkButtonPrimary, sCTkEntryPrimary, sCTkLabelSecondary,
                            sCTk, sCTkFrameOutlined)

if __name__ == "__main__":

    root = sCTk()
    root.title("Passive Outline Frame Test Suite")
    root.geometry("450x300")

    frame_group = sCTkFrameOutlined(root, border_width=2)
    frame_group.pack(fill="both", expand=True, padx=20, pady=20)

    lbl_title = sCTkLabelSecondary(frame_group, text="TRANSCEIVER FREQUENCY PRESET PROFILE")
    lbl_title.pack(pady=(12, 4), padx=10, fill="x")

    mock_entry = sCTkEntryPrimary(frame_group, placeholder_text="Standard data field...")
    mock_entry.pack(pady=10, padx=25, fill="x")


    def toggle_frame_states():
        """Toggles the outlined card panel and cascades the state change down to child widgets, skipping the trigger."""
        current_mode = frame_group.get_state()
        target = "disabled" if current_mode == "normal" else "normal"

        frame_group.configure(state=target)

        for child in frame_group.winfo_children():
            if child == btn_toggle:
                continue
            if hasattr(child, "configure"):
                child.configure(state=target)

        btn_toggle.configure(
            text="Lock Outline Deck (Set 'disabled')" if target == "normal" else "Unlock Outline Deck (Set 'normal')")
        print(f"Logged Verification Hook -> frame_group.get_state() = {frame_group.get_state()}")


    btn_toggle = sCTkButtonPrimary(frame_group, text="Lock Outline Deck (Set 'disabled')", command=toggle_frame_states)
    btn_toggle.pack(side="bottom", pady=15)

    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    print(f"Initial Outline Frame State = {frame_group.get_state().upper()}")
    print("========================================\n")

    root.mainloop()

