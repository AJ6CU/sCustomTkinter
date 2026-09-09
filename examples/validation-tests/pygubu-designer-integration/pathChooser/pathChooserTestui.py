#!/usr/bin/python3
"""
pathChooserTest

pathChooserTest

UI source file: pathChooser_test.ui
"""
from scustomtkinter.sctk_checkbox import sCTkCheckBox
from scustomtkinter.sctk_core import sCTk
from scustomtkinter.sctk_path_chooser import sCTkPathChooser


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


class pathChooserTestUI:
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
        sctk2 = sCTk(None)
        # First object created
        on_first_object_cb(sctk2)

        sctkpathchooser1 = sCTkPathChooser(sctk2)
        sctkpathchooser1.configure(
            filetypes=[
                ".py",
                ".txt"],
            initialdir="/Users/markjhatch/Documents/GitHub/sCustomTkinter/scustomtkinter",
            initialfile="doc.txt",
            justify="right",
            title='Hello',
            type="file")
        sctkpathchooser1.pack(side="top")
        sctkpathchooser1.configure(command=self.single_CB)
        sctkcheckbox1 = sCTkCheckBox(sctk2)
        sctkcheckbox1.configure(text='sctkcheckbox1')
        sctkcheckbox1.pack(side="top")

        # Main widget
        self.mainwindow = sctk2

    def run(self):
        self.mainwindow.mainloop()

    def single_CB(self, selected_path):
        pass


if __name__ == "__main__":
    app = pathChooserTestUI()
    app.run()
