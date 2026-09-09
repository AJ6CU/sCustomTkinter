#!/usr/bin/python3
"""
dialTest

dialTest

UI source file: dialsTest.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import dialTestui as baseui


class dialTest(baseui.dialTestUI):
    def __init__(self, master=None):
        super().__init__(master)

    def dialCont_CB(self, step_delta):
        print("dialCont_CB", step_delta)

    def left_dialCont_CB(self):
        print("left_dialCont_CB")

    def right_dialCont_CB(self):
        print("right_dialCont_CB")

    def dialRange_CB(self, value):
        print("dialRange_CB", value)

    def left_dialRange_CB(self):
        print("left_dialRange_CB")

    def right_dialRange_CB(self):
        print("right_dialRange_CB")

    def dialSelector_CB(self, selected_index):
        print("dialSelector_CB", selected_index)

    def left_dialSelector_CB(self):
        print("left_dialSelector_CB")

    def right_dialSelector_CB(self):
        print("right_dialSelector_CB")


if __name__ == "__main__":
    app = dialTest()
    app.run()
