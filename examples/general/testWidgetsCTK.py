#!/usr/bin/python3
"""
testWidgetsCTK

A test of sCustomTkinter widgets and code generatgion

UI source file: testWidgetsCTK.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import testWidgetsCTKui as baseui


class testWidgetsCTK(baseui.testWidgetsCTKUI):
    def __init__(self, master=None):
        super().__init__(master)

    def CTkComboBox_CB(self, value):
        pass


if __name__ == "__main__":
    app = testWidgetsCTK()
    app.run()
