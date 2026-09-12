#!/usr/bin/python3
"""
dialDoubleClickTest

dialDoubleClickTest

UI source file: dialDoubleClickTest.ui
"""
from scustomtkinter.sctk_core import sCTk
from scustomtkinter.sctk_dial import (
    sCTkDialContinuous,
    sCTkDialRange,
    sCTkDialSelector)


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


class dialDoubleClickTestUI:
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

        sctkdialcontinuous1 = sCTkDialContinuous(sctk1)
        sctkdialcontinuous1.configure(pressed=True)
        sctkdialcontinuous1.pack(side="top")
        sctkdialcontinuous1.configure(command=self.contValueChanged_CB)
        sctkdialcontinuous1.configure(left_click_callback=self.contLeft_CB)
        sctkdialcontinuous1.configure(right_click_callback=self.contRight_CB)
        sctkdialcontinuous1.configure(double_click_command=self.contDouble_CB)
        sctkdialcontinuous1.configure(
            shift_double_click_command=self.contShiftDouble_CB)
        sctkdialrange1 = sCTkDialRange(sctk1)
        sctkdialrange1.pack(side="top")
        sctkdialrange1.configure(command=self.rangeValueChanged_CB)
        sctkdialrange1.configure(left_click_callback=self.rangeLeft_CB)
        sctkdialrange1.configure(right_click_callback=self.rangeRight_CB)
        sctkdialrange1.configure(double_click_command=self.rangeDouble_CB)
        sctkdialrange1.configure(
            shift_double_click_command=self.rangeShiftDouble_CB)
        sctkdialselector1 = sCTkDialSelector(sctk1)
        sctkdialselector1.pack(side="top")
        sctkdialselector1.configure(command=self.selValueChanged_CB)
        sctkdialselector1.configure(left_click_callback=self.selLeft_CB)
        sctkdialselector1.configure(right_click_callback=self.selRight_CB)
        sctkdialselector1.configure(double_click_command=self.selDouble_CB)
        sctkdialselector1.configure(
            shift_double_click_command=self.selShiftDouble_CB)

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()

    def contValueChanged_CB(self, step_delta):
        pass

    def contLeft_CB(self):
        pass

    def contRight_CB(self):
        pass

    def contDouble_CB(self, dial):
        pass

    def contShiftDouble_CB(self, dial):
        pass

    def rangeValueChanged_CB(self, value):
        pass

    def rangeLeft_CB(self):
        pass

    def rangeRight_CB(self):
        pass

    def rangeDouble_CB(self, dial):
        pass

    def rangeShiftDouble_CB(self, dial):
        pass

    def selValueChanged_CB(self, selected_index):
        pass

    def selLeft_CB(self):
        pass

    def selRight_CB(self):
        pass

    def selDouble_CB(self, dial):
        pass

    def selShiftDouble_CB(self, dial):
        pass


if __name__ == "__main__":
    app = dialDoubleClickTestUI()
    app.run()
