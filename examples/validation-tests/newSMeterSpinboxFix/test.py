#!/usr/bin/python3
"""
test

test

UI source file: smeterspinboxTest.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import testui as baseui


class test(baseui.testUI):
    def __init__(self, master=None):
        super().__init__(master)


if __name__ == "__main__":
    app = test()
    app.run()
