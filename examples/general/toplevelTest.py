#!/usr/bin/python3
"""
toplevelTest

toplevelTest

UI source file: toplevelTest.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import toplevelTestui as baseui


class toplevelTest(baseui.toplevelTestUI):
    def __init__(self, master=None):
        super().__init__(master)


if __name__ == "__main__":
    app = toplevelTest()
    app.run()
