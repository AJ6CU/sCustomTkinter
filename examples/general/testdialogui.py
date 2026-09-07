#!/usr/bin/python3
"""
testdialog

testdialog

UI source file: testdialog.ui
"""
import tkinter as tk
from scustomtkinter.sctk_combobox import sCTkComboBox
from scustomtkinter.sctk_dial import sCTkDialContinuous
from scustomtkinter.sctk_dialog import sCTkDialog
from scustomtkinter.sctk_label_tertiary import sCTkLabelTertiary


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


class testdialogUI:
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
        sctkdialog1 = sCTkDialog(
            master,
            transient=False,
            heading='I am Mark',
            heading_anchor='center',
            buttons=2)
        # First object created
        on_first_object_cb(sctkdialog1)

        sctkcombobox1 = sCTkComboBox(sctkdialog1.contentFrame)
        sctkcombobox1.grid(column=0, row=0)
        sctkdialcontinuous1 = sCTkDialContinuous(sctkdialog1.contentFrame)
        sctkdialcontinuous1.grid(column=1, row=0)
        sctklabeltertiary1 = sCTkLabelTertiary(sctkdialog1.contentFrame)
        sctklabeltertiary1.configure(text='sctklabeltertiary1')
        sctklabeltertiary1.grid(column=2, row=0)
        sctkdialog1.grid(column=0, row=0)
        sctkdialog1.configure(apply_command=self.apply_cb)
        sctkdialog1.configure(cancel_command=self.cancel_cb)
        sctkdialog1.configure(reset_command=self.reset_cb)

        # Main widget
        self.mainwindow = sctkdialog1

    def run(self):
        self.mainwindow.mainloop()

    def apply_cb(self):
        pass

    def cancel_cb(self):
        pass

    def reset_cb(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = testdialogUI(root)
    app.run()
