#!/usr/bin/python3
"""
spinBoxTest

spinBoxTest

UI source file: spinBoxTest.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import spinBoxTestui as baseui


class spinBoxTest(baseui.spinBoxTestUI):
    def __init__(self, master=None):
        super().__init__(master)

    def valueChanges_CB(self, value):
        print("valueChanges_CB", value)


if __name__ == "__main__":
    app = spinBoxTest()
    app.run()
