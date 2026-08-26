#!/usr/bin/python3
"""
sCTkDialogToplevel

the top level for a sCTkDialogToplevel

UI source file: sCTkDialogToplevel.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkToplevel


class sCTkDialogToplevel(CTkToplevel):
    """Your widget direct subclass.

    Only simple properties will be configured.
    No commands, no bindings.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        # Layout for 'ctktoplevel1' skipped in custom widget template.


if __name__ == "__main__":
    root = tk.Tk()
    widget = sCTkDialogToplevel(root)
    root.mainloop()
