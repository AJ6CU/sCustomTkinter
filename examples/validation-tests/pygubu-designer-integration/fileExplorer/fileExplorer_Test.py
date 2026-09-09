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

    def single_cb(self, selected_path):
        print("Single cb", selected_path)

    def double_cb(self, explorer, selected_path):
        print("Double cb", selected_path)


if __name__ == "__main__":
    app = fileExplorer_Test()
    app.run()
