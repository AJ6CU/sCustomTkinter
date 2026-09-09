#!/usr/bin/python3
"""
entryFieldTest

entryFieldTest

UI source file: entryFieldTest.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import entryFieldTestui as baseui


class entryFieldTest(baseui.entryFieldTestUI):
    def __init__(self, master=None):
        super().__init__(master)
        self.primaryText.set("no one")
        self.secondaryText.set("someone")

    def primaryValidate_CB(self, s_prev_value, w_entry_name):
        print("primaryValidate_CB", s_prev_value, w_entry_name)
        print(self.primaryText.get())

        return True

    def primaryXscroll_CB(self, first=None, last=None):
        print("primaryXscroll_CB", first, last)

    def testValidate_CB(self, d_action):
        print("testValidate_CB", d_action)
        print(self.secondaryText.get())

        return True

    def xscroll_CB(self, first=None, last=None):
        print("xscroll_CB", first, last)


if __name__ == "__main__":
    app = entryFieldTest()
    app.run()
