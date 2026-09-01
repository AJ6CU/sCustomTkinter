#!/usr/bin/python3f
from scustomtkinter import sCTk, sCTkButtonPrimary, sCTkEntryPrimary, sCTkScrollableFrame

if __name__ == "__main__":
    root = sCTk()
    root.title("ScrollableFrame Example")
    root.geometry("450x420")

    log_viewport = sCTkScrollableFrame(root, width=380, height=250, label_text="Telemetry Log")
    log_viewport.pack(padx=20, pady=20, fill="both", expand=True)

    for i in range(12):
        entry = sCTkEntryPrimary(log_viewport, placeholder_text=f"Channel {i + 1}")
        entry.pack(padx=10, pady=5, fill="x")

    # No activation call needed -- scrolling is live as soon as the widget
    # is placed.

    def toggle_lock():
        target = "disabled" if log_viewport.get_state() == "normal" else "normal"
        log_viewport.configure(state=target)
        toggle_btn.configure(text="Enable All" if target == "disabled" else "Disable All")

        # Disabling the frame dims it and stops its scrolling, but does NOT
        # cascade to children -- do that explicitly.
        for child in log_viewport.get_children():
            if hasattr(child, "configure"):
                try:
                    child.configure(state=target)
                except Exception:
                    pass

    toggle_btn = sCTkButtonPrimary(root, text="Disable All", command=toggle_lock)
    toggle_btn.pack(side="bottom", pady=15)

    root.mainloop()