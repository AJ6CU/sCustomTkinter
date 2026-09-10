#!/usr/bin/python3
"""
colorOverrideTest2

colorOverrideTest2

UI source file: colorOverrideTest2.ui
"""
from scustomtkinter.sctk_core import sCTk
from scustomtkinter.sctk_entry_primary import sCTkEntryPrimary
from scustomtkinter.sctk_entry_secondary import sCTkEntrySecondary
from scustomtkinter.sctk_progress_bar import sCTkProgressBar
from scustomtkinter.sctk_textbox_primary import sCTkTextboxPrimary
from scustomtkinter.sctk_textbox_secondary import sCTkTextboxSecondary


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


class colorOverrideTest2UI:
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

        sctkentryprimary1 = sCTkEntryPrimary(sctk1)
        sctkentryprimary1.configure(state="disabled")
        sctkentryprimary1.delete(0, "end")
        sctkentryprimary1.insert(0, 'mark')
        sctkentryprimary1.pack(side="top")
        sctkentrysecondary1 = sCTkEntrySecondary(sctk1)
        sctkentrysecondary1.configure(state="normal")
        sctkentrysecondary1.delete(0, "end")
        sctkentrysecondary1.insert(0, 'sue')
        sctkentrysecondary1.pack(side="top")
        sctkprogressbar1 = sCTkProgressBar(sctk1)
        sctkprogressbar1.pack(pady=20, side="top")
        sctktextboxprimary1 = sCTkTextboxPrimary(sctk1)
        sctktextboxprimary1.configure(state="disabled")
        _text_ = 'sctktextboxprimary1'
        sctktextboxprimary1.configure(state="normal")
        sctktextboxprimary1.delete("0.0", "end")
        sctktextboxprimary1.insert("0.0", _text_)
        sctktextboxprimary1.configure(state="disabled")
        sctktextboxprimary1.pack(side="top")
        sctktextboxsecondary1 = sCTkTextboxSecondary(sctk1)
        sctktextboxsecondary1.configure(state="disabled")
        _text_ = 'sctktextboxsecondary1'
        sctktextboxsecondary1.configure(state="normal")
        sctktextboxsecondary1.delete("0.0", "end")
        sctktextboxsecondary1.insert("0.0", _text_)
        sctktextboxsecondary1.configure(state="disabled")
        sctktextboxsecondary1.pack(side="top")

        e = sctkentryprimary1
        print("text:", repr(e.get()))
        print("text_color:", e.cget("text_color"))
        print("fg_color:", e.cget("fg_color"))

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()


if __name__ == "__main__":
    app = colorOverrideTest2UI()
    app.run()
