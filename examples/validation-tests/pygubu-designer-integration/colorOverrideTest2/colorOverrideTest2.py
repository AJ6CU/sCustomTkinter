#!/usr/bin/python3
"""
colorOverrideTest2

colorOverrideTest2

UI source file: colorOverrideTest2.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import colorOverrideTest2ui as baseui


class colorOverrideTest2(baseui.colorOverrideTest2UI):
    def __init__(self, master=None):
        super().__init__(master)




if __name__ == "__main__":
    app = colorOverrideTest2()
    app.run()
