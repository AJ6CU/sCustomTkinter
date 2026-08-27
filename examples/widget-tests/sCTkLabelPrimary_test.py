#!/usr/bin/python3

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Label Secondary
# =====================================================================

from scustomtkinter import sCTkFrame, sCTkButtonPrimary, sCTkLabelSecondary,sCTk, sCTkLabelPrimary

if __name__ == "__main__":

    root = sCTk()
    root.geometry("450x280")
    root.title("sCTkLabelPrimary Testing Deck")

    container = sCTkFrame(root, fg_color="transparent")
    container.pack(expand=True, fill="both", padx=30, pady=30)

    primary_label = sCTkLabelPrimary(container, text="MAIN RADIO DECK CONSOLE")
    primary_label.pack(expand=True, pady=10)

    lbl_status = sCTkLabelSecondary(container, text="Current State Assertion: NORMAL", font=("Arial", 10, "italic"))
    lbl_status.pack(side="bottom", pady=5)

    def toggle_label_states():
        """Cycles the dominant header label states between normal and disabled profiles."""
        current_state = primary_label.get_state()
        target = "disabled" if current_state == "normal" else "normal"

        primary_label.configure(state=target)

        if target == "disabled":
            btn_toggle.configure(text="Activate Header (Set 'normal')")
            lbl_status.configure(text="Current State Assertion: DISABLED")
        else:
            btn_toggle.configure(text="Dim Header (Set 'disabled')")
            lbl_status.configure(text="Current State Assertion: NORMAL")

        print(f"Logged Verification Hook -> primary_label.get_state() = {primary_label.get_state()}")

    btn_toggle = sCTkButtonPrimary(
        container,
        text="Dim Header (Set 'disabled')",
        command=toggle_label_states,
        fg_color=("#1A4375", "#3B8ED0"),
        hover_color=("#112A4B", "#1F6AA5")
    )
    btn_toggle.pack(expand=True, pady=15)

    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    primary_label.state("disabled")
    print(f"state (Disabled Pass) = {primary_label.get_state().upper()}")

    primary_label.state("normal")
    print(f"state (Normal Pass)   = {primary_label.get_state().upper()}")
    print("========================================\n")

    root.mainloop()

