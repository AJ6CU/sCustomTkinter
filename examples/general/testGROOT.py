#!/usr/bin/python3
"""
test

ignore

UI source file: tesstGTOOT.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import testGROOTui as baseui


class testGROOT(baseui.testGROOTUI):
    def __init__(self, master=None):
        super().__init__(master)


if __name__ == "__main__":
    root = tk.Tk()
    app = testGROOT(root)
    app.run()
