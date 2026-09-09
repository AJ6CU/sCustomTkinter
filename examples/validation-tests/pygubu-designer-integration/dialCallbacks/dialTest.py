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
        pass

    def left_dialCont_CB(self, ):
        pass

    def right_dialCont_CB(self, ):
        pass

    def dialRange_CB(self, value):
        pass

    def left_dialRange_CB(self, ):
        pass

    def right_dialRange_CB(self, ):
        pass

    def dialSelector_CB(self, selected_index):
        pass

    def left_dialSelector_CB(self, ):
        pass

    def right_dialSelector_CB(self, ):
        pass


if __name__ == "__main__":
    app = dialTest()
    app.run()
