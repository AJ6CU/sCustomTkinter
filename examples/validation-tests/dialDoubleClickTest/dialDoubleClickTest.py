#!/usr/bin/python3
"""
dialDoubleClickTest

dialDoubleClickTest

UI source file: dialDoubleClickTest.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import dialDoubleClickTestui as baseui


class dialDoubleClickTest(baseui.dialDoubleClickTestUI):
    def __init__(self, master=None):
        super().__init__(master)

    def contValueChanged_CB(self, step_delta):
        print("contValueChanged_CB", step_delta)


    def contLeft_CB(self):
        print("contLeft_CB")

    def contRight_CB(self):
        print("contRight_CB")

    def contDouble_CB(self, dial):
        print("contDouble_CB", dial)

    def contShiftDouble_CB(self, dial):
        print("contShiftDouble_CB", dial)

    def rangeValueChanged_CB(self, value):
        print("rangeValueChanged_CB", value)

    def rangeLeft_CB(self):
        print("rangeLeft_CB")

    def rangeRight_CB(self):
        print("rangeRight_CB")

    def rangeDouble_CB(self, dial):
        print("rangeDouble_CB", dial)

    def rangeShiftDouble_CB(self, dial):
        print("rangeShiftDouble_CB", dial)

    def selValueChanged_CB(self, selected_index):
        print("selValueChanged_CB", selected_index)

    def selLeft_CB(self):
        print("selLeft_CB")

    def selRight_CB(self):
        print("selRight_CB")

    def selDouble_CB(self, dial):
        print("selDouble_CB", dial)

    def selShiftDouble_CB(self, dial):
        print("selShiftDouble_CB", dial)


if __name__ == "__main__":
    app = dialDoubleClickTest()
    app.run()
