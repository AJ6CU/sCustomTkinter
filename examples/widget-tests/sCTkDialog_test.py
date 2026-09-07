#!/usr/bin/python3
import customtkinter as ctk
from scustomtkinter import (sCTk, sCTkFrame, sCTkButtonPrimary,
                            sCTkLabelPrimary, sCTkEntryPrimary, sCTkDialog)


class SettingsDialog(sCTkDialog):
    """A dialog that reports what the user chose."""

    def __init__(self, master, **kw):
        super().__init__(master, title="Station Settings",
                         heading="Transceiver", buttons=3, **kw)
        self.result = None

        self.call_entry = sCTkEntryPrimary(
            self.contentFrame, placeholder_text="Callsign")
        self.call_entry.pack(padx=20, pady=(20, 10), fill="x")

        self.grid_entry = sCTkEntryPrimary(
            self.contentFrame, placeholder_text="Grid square")
        self.grid_entry.pack(padx=20, pady=(0, 20), fill="x")

    def apply_CB(self):
        self.result = (self.call_entry.get(), self.grid_entry.get())
        self.dialog_close()

    def cancel_CB(self):
        self.dialog_close()

    def reset_CB(self):
        self.call_entry.delete(0, "end")
        self.grid_entry.delete(0, "end")


if __name__ == "__main__":
    root = sCTk()
    root.geometry("420x220")
    root.title("sCTkDialog Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    status = sCTkLabelPrimary(base, text="No settings yet")
    status.pack(pady=10)

    def open_settings():
        dialog = SettingsDialog(base, modal=True)
        dialog.run_and_wait()
        if dialog.result:
            status.configure(text=f"{dialog.result[0]} / {dialog.result[1]}")
        else:
            status.configure(text="Cancelled")

    sCTkButtonPrimary(base, text="Settings...", command=open_settings).pack(pady=10)

    root.mainloop()