#!/usr/bin/python3
"""
pathChooserTest

pathChooserTest

UI source file: pathChooser_test.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import pathChooserTestui as baseui


class pathChooserTest(baseui.pathChooserTestUI):
    def __init__(self, master=None):
        super().__init__(master)

    def single_CB(self, selected_path):
        print("Single CB", selected_path)


if __name__ == "__main__":
    app = pathChooserTest()
    app.run()
