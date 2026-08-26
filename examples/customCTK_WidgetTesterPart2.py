#!/usr/bin/python3
"""
customCTK_WidgetTesterPart2

just tests each widget

UI source file: customCTK_WidgetTesterPart2.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import customCTK_WidgetTesterPart2ui as baseui


class customCTK_WidgetTesterPart2(baseui.customCTK_WidgetTesterPart2UI):
    def __init__(self, master=None):
        super().__init__(master)

    def primary1_CB(self):
        pass

    def secondary2_CB(self):
        pass

    def ghost3_cb(self):
        pass

    def menuOption_CB(self, current_value):
        pass

    def callback(self, event=None):
        pass


if __name__ == "__main__":
    app = customCTK_WidgetTesterPart2()
    app.run()
