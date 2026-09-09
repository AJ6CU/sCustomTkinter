#!/usr/bin/python3
"""
checkBoxTest

checkBoxTest

UI source file: checkBoxTest.ui
"""
import tkinter as tk
from scustomtkinter.sctk_button_primary import sCTkButtonPrimary
from scustomtkinter.sctk_checkbox import sCTkCheckBox
from scustomtkinter.sctk_core import sCTk


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


class checkBoxTestUI:
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

        sctkcheckbox1 = sCTkCheckBox(sctk1, onvalue=1, offvalue=0)
        self.checkbox_VAR = tk.StringVar(value='my checkbox')
        self.checkbox_Value = tk.StringVar()
        sctkcheckbox1.configure(
            fg_color="yellow",
            state="disabled",
            text='my checkbox',
            text_color_disabled="yellow",
            textvariable=self.checkbox_VAR,
            variable=self.checkbox_Value)
        sctkcheckbox1.pack(side="top")
        sctkcheckbox1.configure(command=self.checkbox_CB)
        sctkbuttonprimary1 = sCTkButtonPrimary(sctk1)
        sctkbuttonprimary1.configure(
            fg_color="red",
            state="normal",
            text='sctkbuttonprimary1')
        sctkbuttonprimary1.pack(side="top")

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()

    def checkbox_CB(self):
        pass


if __name__ == "__main__":
    app = checkBoxTestUI()
    app.run()
