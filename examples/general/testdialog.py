#!/usr/bin/python3
"""
testdialog

testdialog

UI source file: testdialog.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import testdialogui as baseui


class testdialog(baseui.testdialogUI):
    def __init__(self, master=None):
        super().__init__(master)


if __name__ == "__main__":
    root = tk.Tk()
    app = testdialog(root)
    app.run()
