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
        sctkdialcontinuous1.pack(side="top")
        sctkdialcontinuous1.configure(command=self.contValueChanged_CB)
        sctkdialcontinuous1.configure(
            left_click_callback=self.contLeftClick_CB)
        sctkdialcontinuous1.configure(
            right_click_callback=self.contRightClick_CB)
        sctkdialcontinuous1.configure(
            double_click_command=self.contDoubleClick_CB)
        sctkdialcontinuous1.configure(
            shift_double_click_command=self.contShiftDoubleClick_CB)
        sctkdialrange1 = sCTkDialRange(sctk1)
        sctkdialrange1.pack(side="top")
        sctkdialrange1.configure(command=self.rangeValueChanged_CB)
        sctkdialrange1.configure(left_click_callback=self.rangeLeftClick)
        sctkdialrange1.configure(right_click_callback=self.rangeRightClick_CB)
        sctkdialrange1.configure(double_click_command=self.rangeDoubleClick_CB)
        sctkdialrange1.configure(
            shift_double_click_command=self.rangeShiftDoubleClick_CB)
        sctkdialselector1 = sCTkDialSelector(sctk1)
        sctkdialselector1.pack(side="top")
        sctkdialselector1.configure(command=self.selValueChanged_CB)
        sctkdialselector1.configure(left_click_callback=self.selLeftClick)
        sctkdialselector1.configure(right_click_callback=self.selRightClick_CB)
        sctkdialselector1.configure(
            double_click_command=self.selDoubleClick_CB)
        sctkdialselector1.configure(
            shift_double_click_command=self.selShiftDoubleClick_CB)

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()

    def contValueChanged_CB(self, step_delta):
        pass

    def contLeftClick_CB(self):
        pass

    def contRightClick_CB(self):
        pass

    def contDoubleClick_CB(self, dial):
        pass

    def contShiftDoubleClick_CB(self, dial):
        pass

    def rangeValueChanged_CB(self, value):
        pass

    def rangeLeftClick(self):
        pass

    def rangeRightClick_CB(self):
        pass

    def rangeDoubleClick_CB(self, dial):
        pass

    def rangeShiftDoubleClick_CB(self, dial):
        pass

    def selValueChanged_CB(self, selected_index):
        pass

    def selLeftClick(self):
        pass

    def selRightClick_CB(self):
        pass

    def selDoubleClick_CB(self, dial):
        pass

    def selShiftDoubleClick_CB(self, dial):
        pass


if __name__ == "__main__":
    app = dialDoubleClickTestUI()
    app.run()
