#!/usr/bin/python3
"""
sCTkFrame - Piece 1 of 2

A clean, theme-compliant standard CustomTkinter container frame widget.
Inherits cleanly and directly from ctk.CTkFrame to preserve 100% of native
CustomTkinter features, theme tracking loops, and Pygubu container actions.
"""
import customtkinter as ctk
from .ThemeableWidget import ThemeableWidget

class sCTkFrame(ctk.CTkFrame, ThemeableWidget):
    properties = frozenset()

    def __init__(self, master=None, **kwargs):
        # 1. Fire our shared theme logic first. It automatically finds "sCTkFrame" in themes.json
        ThemeableWidget.__init__(self, kwargs)

        # 2. 🛠️ THE MUTATION SAFEGUARD DEEP COPY:
        # Clone your configuration parameters into completely independent memory structures
        # BEFORE initializing super, protecting active color values from native corruption traps.
        self._local_defaults = dict(self.final_kw)

        # 3. Initialize CustomTkinter natively with the clean final kwargs array safely
        super().__init__(master, **self.final_kw)

        # 🔑 4. REGISTER LIFECYCLE HANDSHAKE HOOK:
        # Pushes tracking notifications reachably up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Handles Pygubu designer queries and manages container configurations safely."""
        # ZONE A: Pygubu Inspector Position Intercept
        if args and len(args) == 1:
            pname = args[0]
            if pname == "state":
                return ('state', 'state', 'State', 'normal', str(self.state()))
            if pname in ["fg_color", "border_color"]:
                val = self._local_defaults.get(pname)
                return (pname, pname, pname, str(val), str(val))
            return super().configure(pname)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        # ZONE B: Safe State Bypasser (Absorbs the key to keep the harness from crashing)
        if "state" in kwargs:
            target_state = kwargs.pop("state")
            self.state(target_state)

        # Clean empty strings passed by backspacing parameters in Pygubu to prevent exceptions
        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        # ZONE C: Standard MRO Routing Handoff pass
        if kwargs:
            return super().configure(**kwargs)
        return None

    config = configure
    def get_state(self):
        """Explicit getter synchronized with your standalone test harness script assertions."""
        return self.state()

    def state(self, mode: str = None):
        """Pure Frame Operational Fallback Pass. Frame containers remain perpetually active."""
        return "normal"


# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
#
# if __name__ == "__main__":
#
#     root = ctk.CTk()
#     root.geometry("450x300")
#     root.title("sCTkFrame Container Validation Bench")
#
#     # Instantiate your custom theme-compliant frame element chassis
#     base_container = sCTkFrame(root, border_width=2)
#     base_container.pack(expand=True, fill="both", padx=30, pady=30)
#
#     # Add a simple sub-element child widget to verify structural clipping layouts
#     lbl_marker = ctk.CTkLabel(base_container, text="FRAME BACKPLANE CONTAINER OPERATIONAL")
#     lbl_marker.pack(expand=True)
#
#
#     # Standard dashboard interaction toggle simulation pass
#     def toggle_panel_lock():
#         current_mode = base_container.get_state()
#         target = "disabled" if current_mode == "normal" else "normal"
#
#         # Explicitly testing the dual-routing capability via configure()
#         base_container.configure(state=target)
#         print(f"Logged Verification Hook -> base_container.get_state() = {base_container.get_state()}")
#
#
#     btn_lock = ctk.CTkButton(root, text="Simulate Cascading Interface Lock", command=toggle_panel_lock)
#     btn_lock.pack(side="bottom", pady=15)
#
#     # Run the interactive boot tracking logs
#     print("--- BOOT INITIALIZATION PASSTHROUGH ---")
#     base_container.state("disabled")
#     print("state (Disabled Pass) =", base_container.get_state())  # Output: normal (Frames bypass disabled masks)
#
#     base_container.state("normal")
#     print("state (Normal Pass)   =", base_container.get_state())  # Output: normal
#     print("========================================\n")
#
#     root.mainloop()
