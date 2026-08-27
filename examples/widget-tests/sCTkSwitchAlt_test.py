#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Switch - alt
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkLabelSecondary, sCTkButtonPrimary, sCTk, sCTkSwitch, sCTkSwitchAlt


if __name__ == "__main__":

    root = sCTk()
    root.geometry("520x460")
    root.title("sCustomTkinter Dual Switch Validation Bench")
    root.configure(fg_color=("#F1F5F9", "#1C1C1C"))

    base = sCTkFrame(root, border_width=2)
    base.pack(expand=True, fill="both", padx=30, pady=30)

    # Configure the internal panel weights cache grid system to force left alignment
    base.grid_columnconfigure(0, weight=1)

    # =====================================================================
    # 🎛️ MODULE 1: Standard Switch (Native Inheritance Variant)
    # =====================================================================
    # 🔑 LEFT REALIGNMENT PASS: Configured with sticky="w" to lock alignment flush left!
    lbl_std = sCTkLabelSecondary(base, text="[Standard ctk.CTkSwitch Subclass]", font=("Arial", 11, "bold"))
    lbl_std.grid(row=0, column=0, padx=40, pady=(15, 2), sticky="w")

    switch_std = sCTkSwitch(
        base,
        text="Standard Pre-Amp Link Channel",
        command=lambda val: print(f"Standard Pass -> State Value: {val}")
    )
    switch_std.grid(row=1, column=0, padx=40, pady=10, sticky="w")

    # =====================================================================
    # 🎛️ MODULE 2: Alternative Switch (Custom Composite Drawing Variant)
    # =====================================================================
    lbl_alt = sCTkLabelSecondary(base, text="[Alternative sCTkSwitchAlt Custom Draw]", font=("Arial", 11, "bold"))
    lbl_alt.grid(row=2, column=0, padx=40, pady=(25, 2), sticky="w")

    switch_alt = sCTkSwitchAlt(
        base,
        text="Advanced VFO Frequency Lock Link",
        command=lambda val: print(f"Alternative Pass -> State Value: {val}")
    )
    switch_alt.grid(row=3, column=0, padx=40, pady=10, sticky="w")


    # =====================================================================
    # 🛠️ INTERACTIVE BENCH LOOK CONTROLLERS
    # =====================================================================
    def toggle_framework_locks():
        """Toggles operational locked states across both components smoothly."""
        current_std = switch_std.get_state()
        target = "disabled" if current_std == "normal" else "normal"

        switch_std.configure(state=target)
        switch_alt.configure(state=target)

        btn_lock.configure(
            text="Unlock Panel (Set 'normal')" if target == "disabled" else "Lock Panel (Set 'disabled')")


    def toggle_skin_preference():
        """Toggles between Light and Dark application window appearances dynamically."""
        ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")


    # Arrange execution buttons layout grids at the lower edge of the screen capsule
    btn_lock = sCTkButtonPrimary(root, text="Lock Panel (Set 'disabled')", command=toggle_framework_locks)
    btn_lock.pack(side="bottom", pady=5)

    btn_skin = sCTkButtonPrimary(root, text="Toggle UI Light/Dark Appearance", command=toggle_skin_preference)
    btn_skin.pack(side="bottom", pady=5)

    root.mainloop()
