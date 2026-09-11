#!/usr/bin/python3
"""
testColorOverride4

testColorOverride4

UI source file: colorTestOverride4.ui
"""
from scustomtkinter.sctk_core import sCTk
from scustomtkinter.sctk_file_explorer import sCTkFileExplorer
from scustomtkinter.sctk_selector import sCTkSelector
from scustomtkinter.sctk_slider import sCTkSlider
from scustomtkinter.sctk_smeter import sCTkSMeter
from scustomtkinter.sctk_smeter_bar import sCTkSMeterBar


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


class testColorOverride4UI:
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

        sctksmeter1 = sCTkSMeter(sctk1)
        sctksmeter1.pack(side="top")
        sctksmeterbar1 = sCTkSMeterBar(sctk1)
        sctksmeterbar1.pack(side="top")
        sctkselector1 = sCTkSelector(sctk1)
        sctkselector1.configure(
            items=[
                "vw",
                "porsche",
                "240z"],
            state='disabled')
        sctkselector1.pack(side="top")
        sctkfileexplorer1 = sCTkFileExplorer(sctk1)
        sctkfileexplorer1.configure(state="disabled")
        sctkfileexplorer1.pack(side="top")
        sctkslider1 = sCTkSlider(sctk1)
        sctkslider1.configure(state="disabled")
        sctkslider1.pack(side="top")

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()


if __name__ == "__main__":
    app = testColorOverride4UI()
    app.run()
