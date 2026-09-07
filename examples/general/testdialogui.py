#!/usr/bin/python3
"""
testdialog

testdialog

UI source file: testdialog.ui
"""
from scustomtkinter.sctk_button_secondary import sCTkButtonSecondary
from scustomtkinter.sctk_dialog import sCTkDialog
from scustomtkinter.sctk_frame import sCTkFrame
from scustomtkinter.sctk_label_primary import sCTkLabelPrimary
from scustomtkinter.sctk_label_secondary import sCTkLabelSecondary


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
            title='Your Window Title',
            transient=False,
            heading='Maybe a Settings Dialog?',
            heading_anchor='center',
            buttons=2,
            cancel_text='NO Cancel',
            reset_text='Please')
        # First object created
        on_first_object_cb(sctkdialog1)

        sctkframe1 = sCTkFrame(sctkdialog1.contentFrame)
        sctklabelprimary2 = sCTkLabelPrimary(sctkframe1)
        sctklabelprimary2.configure(text='You can add widgets here')
        sctklabelprimary2.pack(side="top")
        sctklabelsecondary1 = sCTkLabelSecondary(sctkframe1)
        sctklabelsecondary1.configure(text='Secondary Label')
        sctklabelsecondary1.pack(side="top")
        sctkbuttonsecondary1 = sCTkButtonSecondary(sctkframe1)
        sctkbuttonsecondary1.configure(text='A Button')
        sctkbuttonsecondary1.pack(side="top")
        sctkframe1.pack(side="top")
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
    app = testdialogUI()
    app.run()
