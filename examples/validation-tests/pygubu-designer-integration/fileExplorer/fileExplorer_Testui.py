#!/usr/bin/python3
"""
fileExplorer_Test

fileExplorer_Test

UI source file: fileExplorer.ui
"""
from scustomtkinter.sctk_core import sCTk
from scustomtkinter.sctk_file_explorer import sCTkFileExplorer
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


class fileExplorer_TestUI:
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

        sctkfileexplorer1 = sCTkFileExplorer(sctk1)
        sctkfileexplorer1.configure(
            initialdir="~/Downloads",
            initialfile="doc.txt",
            state="normal",
            type="file")
        sctkfileexplorer1.pack(side="top")
        sctkfileexplorer1.configure(command=self.single_cb)
        sctkfileexplorer1.configure(double_click_command=self.double_cb)
        sctklabelsecondary1 = sCTkLabelSecondary(sctk1)
        sctklabelsecondary1.configure(text='sctklabelsecondary1')
        sctklabelsecondary1.pack(side="top")

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()

    def single_cb(self, selected_path):
        pass

    def double_cb(self, explorer, selected_path):
        pass


if __name__ == "__main__":
    app = fileExplorer_TestUI()
    app.run()
