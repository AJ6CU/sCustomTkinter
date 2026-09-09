#!/usr/bin/python3
"""
dialTest

dialTest

UI source file: dialsTest.ui
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


class dialTestUI:
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
        sctkdialcontinuous1.configure(command=self.dialCont_CB)
        sctkdialcontinuous1.configure(
            left_click_callback=self.left_dialCont_CB)
        sctkdialcontinuous1.configure(
            right_click_callback=self.right_dialCont_CB)
        sctkdialrange1 = sCTkDialRange(sctk1)
        sctkdialrange1.pack(side="top")
        sctkdialrange1.configure(command=self.dialRange_CB)
        sctkdialrange1.configure(left_click_callback=self.left_dialRange_CB)
        sctkdialrange1.configure(right_click_callback=self.right_dialRange_CB)
        sctkdialselector1 = sCTkDialSelector(sctk1)
        sctkdialselector1.pack(side="top")
        sctkdialselector1.configure(command=self.dialSelector_CB)
        sctkdialselector1.configure(
            left_click_callback=self.left_dialSelector_CB)
        sctkdialselector1.configure(
            right_click_callback=self.right_dialSelector_CB)

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()

    def dialCont_CB(self, step_delta):
        pass

    def left_dialCont_CB(self, ):
        pass

    def right_dialCont_CB(self, ):
        pass

    def dialRange_CB(self, value):
        pass

    def left_dialRange_CB(self, ):
        pass

    def right_dialRange_CB(self, ):
        pass

    def dialSelector_CB(self, selected_index):
        pass

    def left_dialSelector_CB(self, ):
        pass

    def right_dialSelector_CB(self, ):
        pass


if __name__ == "__main__":
    app = dialTestUI()
    app.run()
