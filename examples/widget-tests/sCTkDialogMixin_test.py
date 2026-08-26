import tkinter as tk
from sCTkDialogToplevel import sCTkDialogToplevel


class sCTkDialogMixin:
    """Your custom logic to run dialgos with toplevels.

    Just note the init method. Can be used to inject a
    custom toplevel.

    Inplement your basic dialog logic here. I mean, showing modal
    and other issues.
    """

    def __init__(self, master, *, toplevel=None, **kw):
        self.dialog_parent = master
        if toplevel is None:
            toplevel = sCTkDialogToplevel()
        self.dialog_toplevel = toplevel
        toplevel.protocol("WM_DELETE_WINDOW", self.onDeleteWindow)

        super().__init__(self.dialog_toplevel, **kw)
        self.pack(expand=True, fill="both")
        self.dialog_toplevel.transient(self.dialog_parent)
        self.dialog_toplevel.deiconify()
        self.dialog_toplevel.wait_visibility()


    def onDeleteWindow(self):
        self.dialogClose()

    def dialogClose(self):
        self.dialog_toplevel.destroy()

    def runAndWait(self):
        print("running and wait")
        self.dialog_toplevel.grab_set()
        self.dialog_parent.wait_window(self.dialog_toplevel)


    def setTitle(self, title):
        self.dialog_toplevel.title(title)