#!/usr/bin/python3
"""
colorTestOverride3

colorTestOverride3

UI source file: colorTestOverrride3.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import colorTestOverride3ui as baseui


class colorTestOverride3(baseui.colorTestOverride3UI):
    def __init__(self, master=None):
        super().__init__(master)


if __name__ == "__main__":
    app = colorTestOverride3()
    app.run()
