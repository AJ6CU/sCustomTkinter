#!/usr/bin/python3
"""
dialSelectorTest

dialSelectorTest

UI source file: dialSelectorTest.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import dialSelectorTestui as baseui


class dialSelectorTest(baseui.dialSelectorTestUI):
    def __init__(self, master=None):
        super().__init__(master)


if __name__ == "__main__":
    app = dialSelectorTest()
    app.run()
