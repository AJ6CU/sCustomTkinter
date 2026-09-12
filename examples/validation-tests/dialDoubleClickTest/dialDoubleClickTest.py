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


    def rangeValueChanged_CB(self, value):
        print("rangeValueChanged_CB", value)




    def selValueChanged_CB(self, selected_index):
        print("selValueChanged_CB", selected_index)




    def selLeftClick(self):
        print("selLeftClick")

    def selRightClick_CB(self):
        print("selRightClick_CB")

    def selDoubleClick_CB(self, dial):
        print("selDoubleClick_CB", dial)

    def selShiftDoubleClick_CB(self, dial):
        print("selShiftDoubleClick_CB", dial)

    def contLeftClick_CB(self):
        print("contLeftClick_CB")

    def contRightClick_CB(self):
        print("contRightClick_CB")

    def contDoubleClick_CB(self, dial):
        print("contDoubleClick_CB", dial)

    def contShiftDoubleClick_CB(self, dial):
        print("contShiftDoubleClick_CB", dial)

    def rangeValueChanged_CB(self, value):
        print("rangeValueChanged_CB", value)

    def rangeLeftClick(self):
        print("rangeLeftClick")

    def rangeRightClick_CB(self):
        print("rangeRightClick_CB")

    def rangeDoubleClick_CB(self, dial):
        print("rangeDoubleClick_CB", dial)

    def rangeShiftDoubleClick_CB(self, dial):
        print("rangeShiftDoubleClick_CB", dial)


if __name__ == "__main__":
    app = dialDoubleClickTest()
    app.run()
