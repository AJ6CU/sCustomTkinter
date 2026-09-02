#!/usr/bin/python3

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Frame Labeled Primary
# =====================================================================

from scustomtkinter import sCTkButtonPrimary, sCTkLabelSecondary, sCTk, sCTkFrameLabeledPrimary


if __name__ == "__main__":

    root = sCTk()
    root.geometry("450x450")
    root.title("Labeled Scrollable Frame Test Bench")

    scroll_panel = sCTkFrameLabeledPrimary(root, label_text="RIG CHANNEL MATRIX CONTROLLER")
    scroll_panel.pack(expand=True, fill="both", padx=25, pady=25)

    for i in range(1, 21):
        lbl_item = sCTkLabelSecondary(scroll_panel, text=f"Channel Lane Array Entry #{i:02d} - Active Track [100Hz]")
        lbl_item.pack(pady=4, fill="x", padx=10)


    def toggle_frame_states():
        current_mode = scroll_panel.get_state()
        target = "disabled" if current_mode == "normal" else "normal"

        scroll_panel.configure(state=target)

        true_children = scroll_panel.winfo_children()
        print(f"DEBUG ASSERTER: Successfully captured {len(true_children)} label elements...")

        for child in true_children:
            if hasattr(child, "configure"):
                child.configure(state=target)

        btn_toggle.configure(
            text="Lock Container (Set 'disabled')" if target == "normal" else "Unlock Container (Set 'normal')")
        print(f"Logged Verification Hook -> scroll_panel.get_state() = {scroll_panel.get_state()}\n")


    btn_toggle = sCTkButtonPrimary(root, text="Lock Container (Set 'disabled')", command=toggle_frame_states)
    btn_toggle.pack(pady=15)

    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    scroll_panel.state("disabled")
    print(f"state (Disabled Pass) = {scroll_panel.get_state().upper()}")

    scroll_panel.state("normal")
    print(f"state (Normal Pass)   = {scroll_panel.get_state().upper()}")
    print("========================================\n")

    root.mainloop()

