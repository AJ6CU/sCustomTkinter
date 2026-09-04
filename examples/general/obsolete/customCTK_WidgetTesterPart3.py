#!/usr/bin/python3
"""
customCTK_WidgetTesterPart3

just tests each widget

UI source file: customCTK_WidgetTesterPart3.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import customCTK_WidgetTesterPart3ui as baseui


class customCTK_WidgetTesterPart3(baseui.customCTK_WidgetTesterPart3UI):
    def __init__(self, master=None):
        super().__init__(master)

    def callback(self, event=None):
        pass


if __name__ == "__main__":
    app = customCTK_WidgetTesterPart3()
    app.run()
