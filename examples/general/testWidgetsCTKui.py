#!/usr/bin/python3
"""
testWidgetsCTK

A test of sCustomTkinter widgets and code generatgion

UI source file: testWidgetsCTK.ui
"""
import tkinter as tk
from customtkinter import (CTk, CTkComboBox, CTkEntry, CTkFrame)


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


class testWidgetsCTKUI:
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
        ctk1 = CTk(None)
        # First object created
        on_first_object_cb(ctk1)

        ctkframe1 = CTkFrame(ctk1)
        self.CTkComboBox = CTkComboBox(ctkframe1)
        self.CTkComboBox_VAR = tk.StringVar()
        self.CTkComboBox.configure(
            values=[
                "Apple",
                "Pear",
                "Orange"],
            variable=self.CTkComboBox_VAR)
        self.CTkComboBox.pack(side="top")
        self.CTkComboBox.configure(command=self.CTkComboBox_CB)
        ctkentry1 = CTkEntry(ctkframe1)
        ctkentry1.configure(invalidcommand="{"name": "invalidcommand", "type": "command", "cbtype": "entry_validate", "args": " % d", "value": "testCTkinvalid"}", validate="focus", validatecommand="{"name": "validatecommand", "type": "command", "cbtype": "entry_validate", "args": " % d", "value": "testCTkValidate_CB"}", xscrollcommand="{"name": "xscrollcommand", "type": "command", "cbtype": "scroll", "value": "testCTkXScroll_CB"}")
        ctkentry1.delete(0, "end")
        ctkentry1.insert(0, 'ctkentry1')
        ctkentry1.pack(side="top")
        ctkframe1.pack(side="top")

        # Main widget
        self.mainwindow = ctk1

    def run(self):
        self.mainwindow.mainloop()

    def CTkComboBox_CB(self, value):
        pass


if __name__ == "__main__":
    app = testWidgetsCTKUI()
    app.run()
