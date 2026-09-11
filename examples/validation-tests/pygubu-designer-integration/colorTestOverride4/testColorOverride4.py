#!/usr/bin/python3
"""
testColorOverride4

testColorOverride4

UI source file: colorTestOverride4.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import testColorOverride4ui as baseui


class testColorOverride4(baseui.testColorOverride4UI):
    def __init__(self, master=None):
        super().__init__(master)


if __name__ == "__main__":
    app = testColorOverride4()
    app.run()
