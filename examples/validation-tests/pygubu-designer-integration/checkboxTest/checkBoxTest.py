#!/usr/bin/python3
"""
checkBoxTest

checkBoxTest

UI source file: checkBoxTest.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import checkBoxTestui as baseui


class checkBoxTest(baseui.checkBoxTestUI):
    def __init__(self, master=None):
        super().__init__(master)


    def checkbox_CB(self):
        print("checkbox_CB", self.checkbox_Value.get(), self.checkbox_VAR.get())
        self.checkbox_VAR.set("been checked")


if __name__ == "__main__":
    app = checkBoxTest()
    app.run()
