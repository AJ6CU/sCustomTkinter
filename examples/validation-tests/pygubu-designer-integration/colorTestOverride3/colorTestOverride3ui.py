#!/usr/bin/python3
"""
colorTestOverride3

colorTestOverride3

UI source file: colorTestOverrride3.ui
"""
from scustomtkinter.sctk_core import sCTk
from scustomtkinter.sctk_dial import (
    sCTkDialContinuous,
    sCTkDialRange,
    sCTkDialSelector)
from scustomtkinter.sctk_frame_labeled_primary import sCTkFrameLabeledPrimary
from scustomtkinter.sctk_frame_labeled_secondary import sCTkFrameLabeledSecondary
from scustomtkinter.sctk_label_secondary import sCTkLabelSecondary
from scustomtkinter.sctk_scrollable_frame import sCTkScrollableFrame


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


class colorTestOverride3UI:
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

        sctkscrollableframe1 = sCTkScrollableFrame(sctk1)
        sctkscrollableframe1.configure(
            label_text="My Scollable", state="disabled")
        sctklabelsecondary1 = sCTkLabelSecondary(sctkscrollableframe1)
        sctklabelsecondary1.configure(text='This is a Scrollable Frame')
        sctklabelsecondary1.pack(side="top")
        sctkscrollableframe1.grid(column=0, row=0)
        sctkframelabeledprimary1 = sCTkFrameLabeledPrimary(sctk1)
        sctkframelabeledprimary1.configure(
            label_text="My Primary", state="disabled")
        sctklabelsecondary2 = sCTkLabelSecondary(sctkframelabeledprimary1)
        sctklabelsecondary2.configure(text='This is a Primary Label\nFrame')
        sctklabelsecondary2.pack(side="top")
        sctkframelabeledprimary1.grid(column=1, row=0)
        sctkframelabeledsecondary1 = sCTkFrameLabeledSecondary(sctk1)
        sctkframelabeledsecondary1.configure(
            label_text="My Secondary", state="disabled")
        sctklabelsecondary3 = sCTkLabelSecondary(sctkframelabeledsecondary1)
        sctklabelsecondary3.configure(text='This is a Secondary Label\nFrame')
        sctklabelsecondary3.pack(side="top")
        sctkframelabeledsecondary1.grid(column=2, row=0)
        sctkdialcontinuous1 = sCTkDialContinuous(sctk1)
        sctkdialcontinuous1.configure(state="disabled")
        sctkdialcontinuous1.grid(column=0, row=1)
        sctkdialrange1 = sCTkDialRange(sctk1)
        sctkdialrange1.configure(state="disabled")
        sctkdialrange1.grid(column=1, row=1)
        sctkdialselector1 = sCTkDialSelector(sctk1)
        sctkdialselector1.configure(state="disabled")
        sctkdialselector1.grid(column=2, row=1)

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()


if __name__ == "__main__":
    app = colorTestOverride3UI()
    app.run()
