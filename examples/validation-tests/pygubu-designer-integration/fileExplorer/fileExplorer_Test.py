#!/usr/bin/python3
"""
fileExplorer_Test

fileExplorer_Test

UI source file: fileExplorer.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import fileExplorer_Testui as baseui


class fileExplorer_Test(baseui.fileExplorer_TestUI):
    def __init__(self, master=None):
        super().__init__(master)

    def single_cb(self):
        print("Single cb")

    def double_cb(self):
        print("Double cb")


if __name__ == "__main__":
    app = fileExplorer_Test()
    app.run()
