#!/usr/bin/python3

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Frame
# =====================================================================

from scustomtkinter import sCTkButtonPrimary, sCTkLabelPrimary, sCTk, sCTkFrame


if __name__ == "__main__":

    root = sCTk()
    root.geometry("500x300")
    root.title("sCTkFrame Container Validation Bench")

    # Instantiate your custom theme-compliant frame element chassis
    base_container = sCTkFrame(root, border_width=2)
    base_container.pack(expand=True, fill="both", padx=30, pady=30)
#
#     # Add a simple sub-element child widget to verify structural clipping layouts
    lbl_marker = sCTkLabelPrimary(base_container, text="FRAME BACKPLANE CONTAINER OPERATIONAL\n"+
                                  "Border Visible for Testing Purposes only")
    lbl_marker.pack(expand=True)

#
#     # Standard dashboard interaction toggle simulation pass
    def toggle_panel_lock():
        current_mode = base_container.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
#
#         # Explicitly testing the dual-routing capability via configure()
        base_container.configure(state=target)
        print(f"Logged Verification Hook -> base_container.get_state() = {base_container.get_state()}")

#
    btn_lock = sCTkButtonPrimary(root, text="Simulate Cascading Interface Lock", command=toggle_panel_lock)
    btn_lock.pack(side="bottom", pady=15)
#
#     # Run the interactive boot tracking logs
    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    base_container.state("disabled")
    print("state (Disabled Pass) =", base_container.get_state())  # Output: normal (Frames bypass disabled masks)

    base_container.state("normal")
    print("state (Normal Pass)   =", base_container.get_state())  # Output: normal
    print("========================================\n")

    root.mainloop()

