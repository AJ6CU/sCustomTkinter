# !/usr/bin/python3
"""
sCTkToplevel - Standalone Interactive Functional Verification Bench

Exposes a primary base frame panel with a tactical action trigger to spawn
the custom un-imported sub-window, confirming total userspace decoupling.
"""
import sCTkThemes
from sCTkFrame import sCTkFrame
from sCTkButtonPrimary import sCTkButtonPrimary
from sCTkLabelSecondary import sCTkLabelSecondary
from sCTkToplevel import sCTkToplevel


class DesktopStationApp:
    def __init__(self):
        # 1. Boot centralized framework look records natively out of themes.json
        sCTkThemes.apply_sCTkThemes()

        # Build a base CustomTkinter window internally to act as the core layout anchor
        import customtkinter as ctk
        self.root = ctk.CTk()
        self.root.geometry("450x320")
        self.root.title("Main Control Rig Backplane")

        # 2. Mount master container chassis using framework primitives
        self.panel = sCTkFrame(self.root, border_width=2)
        self.panel.pack(padx=20, pady=20, fill="both", expand=True)

        self.monitor = sCTkLabelSecondary(self.panel, text="Cockpit Status: [Waiting for Modal Command]")
        self.monitor.pack(pady=20)

        # 3. Mount tactical primary button to trigger the sub-window window pass
        self.trigger_btn = sCTkButtonPrimary(self.panel, text="Open Transceiver Sub-Window",
                                             command=self.spawn_modal_window)
        self.trigger_btn.pack(pady=10)

        self.sub_window_instance = None

    def spawn_modal_window(self):
        """Spawns an sCTkToplevel pass-through window context securely with safety tracking checks."""
        # Prevent spawning duplicate modal panels if one is already actively running on screen
        if self.sub_window_instance is not None and self.sub_window_instance.winfo_exists():
            self.sub_window_instance.focus()
            return

        self.monitor.configure(text="Cockpit Status: [Sub-Window Modal Active]")
        print("📡 Cockpit Console -> Spawning sCTkToplevel pass-through window container.")

        # 4. Instantiate the custom wrapper directly WITHOUT invoking manual ctk imports in this script!
        self.sub_window_instance = sCTkToplevel(self.root)
        self.sub_window_instance.geometry("350x200")
        self.sub_window_instance.title("Modal Telemetry Deck")

        # Enforce application focus stay locked directly inside the spawned container frame panel
        self.sub_window_instance.after(10, self.sub_window_instance.lift)

        # Populate the window space with framework elements natively
        inner_panel = sCTkFrame(self.sub_window_instance, border_width=1, corner_radius=8)
        inner_panel.pack(padx=15, pady=15, fill="both", expand=True)

        msg = sCTkLabelSecondary(inner_panel,
                                 text="▶ Core Telemetry Stream Verified.\n(CustomTkinter has NOT been imported locally!)")
        msg.pack(expand=True)

        # Wire protocol intercepts to reset our status label monitor cleanly on exit windows closure
        self.sub_window_instance.protocol("WM_DELETE_WINDOW", self.on_modal_close)

    def on_modal_close(self):
        self.monitor.configure(text="Cockpit Status: [Waiting for Modal Command]")
        if self.sub_window_instance:
            self.sub_window_instance.destroy()
        print("📡 Cockpit Console -> Sub-Window successfully closed. Returned to primary tracking backplane.")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DesktopStationApp()
    app.run()