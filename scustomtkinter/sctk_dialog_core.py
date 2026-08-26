#!/usr/bin/python3
"""
sCTkDialogCore

a special widget deciated to making popup dialogs consistent

UI source file: sCTkDialogCore.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import sCTkDialogCoreui as baseui


#
# Manual user code
#

class sCTkDialogCore(baseui.sCTkDialogCoreUI):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

    def setHeading(self, heading=None, anchor=None):
        if heading is not None:
            self.heading_VAR.set(heading)

        if anchor is not None and anchor.lower() in ("w","e","center"):
            self.heading_Label.configure(anchor=anchor.lower())

    def setTwoButton(self):
        self.reset_Button.destroy()

    def setApplyButton(self, buttonName=None, buttonCommand=None):
        if buttonName is not None:
            self.applyText_VAR.set(buttonName)

        if buttonCommand is not None:
            self.apply_Button.configure(command=buttonCommand)

        return True

    def setCancelButton(self, buttonName=None, ButtonCommand=None):
        if buttonName is not None:
            self.cancelText_VAR.set(buttonName)

        if ButtonCommand is not None:
            self.cancel_Button.configure(command=ButtonCommand)

        return True


    def setResetButton(self, buttonName=None, ButtonCommand=None):

        #
        #   Protect against reset button being destroyed and then values set
        #
        if self.reset_Button.winfo_exists():
            if buttonName is not None:
                self.resetText_VAR.set(buttonName)

            if ButtonCommand is not None:
                self.reset_Button.configure(command=ButtonCommand)

            return True
        else:
            return False





if __name__ == "__main__":
    root = tk.Tk()
    widget = sCTkDialogCore(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
