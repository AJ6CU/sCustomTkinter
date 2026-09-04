#!/usr/bin/python3
"""
toplevelTest

toplevelTest

UI source file: toplevelTest.ui
"""
from scustomtkinter.sctk_combobox import sCTkComboBox
from scustomtkinter.sctk_toplevel import sCTkToplevel


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


class toplevelTestUI:
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
        sctktoplevel1 = sCTkToplevel(master)
        # First object created
        on_first_object_cb(sctktoplevel1)

        sctkcombobox1 = sCTkComboBox(sctktoplevel1)
        sctkcombobox1.configure(values=["apple", "orange", "pear"])
        sctkcombobox1.pack(side="top")

        # Main widget
        self.mainwindow = sctktoplevel1

    def run(self):
        self.mainwindow.mainloop()


if __name__ == "__main__":
    app = toplevelTestUI()
    app.run()
