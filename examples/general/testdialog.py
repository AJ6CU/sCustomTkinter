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

    def apply_cb(self):
        print("apply_cb")

    def cancel_cb(self):
        print("cancel_cb")

    def reset_cb(self):
        print("reset_cb")


if __name__ == "__main__":
    root = tk.Tk()
    app = testdialog(root)
    app.run()
