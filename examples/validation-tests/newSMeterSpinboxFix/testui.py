#!/usr/bin/python3
"""
test

test

UI source file: smeterspinboxTest.ui
"""
import tkinter as tk
from scustomtkinter.sctk_core import sCTk
from scustomtkinter.sctk_separator import sCTkSeparator
from scustomtkinter.sctk_smeter_bar import sCTkSMeterBar
from scustomtkinter.sctk_spinbox import sCTkSpinbox


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


class testUI:
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

        sctkspinbox1 = sCTkSpinbox(sctk1)
        sctkspinbox1.configure(values=["vw", "porsche", "240Z"])
        sctkspinbox1.pack(side="top")
        sctksmeterbar1 = sCTkSMeterBar(sctk1)
        sctksmeterbar1.configure(height=50, hide_sig_row=True)
        sctksmeterbar1.pack(side="top")
        sctkseparator1 = sCTkSeparator(sctk1)
        sctkseparator1.configure(orientation="horizontal", width=200)
        sctkseparator1.pack(side="top")
        sctksmeterbar2 = sCTkSMeterBar(sctk1)
        sctksmeterbar2.configure(height=50, hide_lower_row=True)
        sctksmeterbar2.pack(side="top")

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()


if __name__ == "__main__":
    app = testUI()
    app.run()
