#!/usr/bin/python3
"""
entryFieldTest

entryFieldTest

UI source file: entryFieldTest.ui
"""
import tkinter as tk
from scustomtkinter.sctk_core import sCTk
from scustomtkinter.sctk_entry_primary import sCTkEntryPrimary
from scustomtkinter.sctk_entry_secondary import sCTkEntrySecondary


def safe_i18n_translator(value):
    """i18n - Setup translator in derived class file"""
    return value


def safe_fo_callback(widget):
    """on first objec callback - Setup callback in derived class file."""
    pass


def safe_image_loader(master, image_name: str):
    """Image loader - Setup image_loader in derived class file."""
    img = None
    try:
        img = tk.PhotoImage(file=image_name, master=master)
    except tk.TclError:
        pass
    return img


class entryFieldTestUI:
    def __init__(
        self,
        master=None,
        *,
        translator=None,
        on_first_object_cb=None,
        data_pool=None,
        image_loader=None
    ):
        if translator is None:
            translator = safe_i18n_translator
        _ = translator  # i18n string marker.
        if image_loader is None:
            image_loader = safe_image_loader
        if on_first_object_cb is None:
            on_first_object_cb = safe_fo_callback
        # build ui
        sctk1 = sCTk(None)
        # First object created
        on_first_object_cb(sctk1)

        sctkentryprimary1 = sCTkEntryPrimary(sctk1)
        self.primaryText = tk.StringVar()
        sctkentryprimary1.configure(
            textvariable=self.primaryText,
            validate="focusout")
        sctkentryprimary1.pack(side="top")
        _validatecmd = (
            sctkentryprimary1.register(
                self.primaryValidate_CB), "%s", "%W")
        sctkentryprimary1.configure(validatecommand=_validatecmd)
        sctkentryprimary1.configure(xscrollcommand=self.primaryXscroll_CB)
        sctkentrysecondary1 = sCTkEntrySecondary(sctk1)
        self.secondaryText = tk.StringVar()
        sctkentrysecondary1.configure(
            textvariable=self.secondaryText,
            validate="focusout")
        sctkentrysecondary1.pack(side="top")
        _validatecmd = (
            sctkentrysecondary1.register(
                self.testValidate_CB), "%d")
        sctkentrysecondary1.configure(validatecommand=_validatecmd)
        sctkentrysecondary1.configure(xscrollcommand=self.xscroll_CB)

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()

    def primaryValidate_CB(self, s_prev_value, w_entry_name):
        pass

    def primaryXscroll_CB(self, first=None, last=None):
        pass

    def testValidate_CB(self, d_action):
        pass

    def xscroll_CB(self, first=None, last=None):
        pass


if __name__ == "__main__":
    app = entryFieldTestUI()
    app.run()
