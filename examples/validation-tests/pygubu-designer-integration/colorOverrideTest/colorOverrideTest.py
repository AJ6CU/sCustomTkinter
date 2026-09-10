#!/usr/bin/python3
"""
colorOverrideTest

colorOverrideTest

UI source file: coverOverrideTest.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import colorOverrideTestui as baseui


class colorOverrideTest(baseui.colorOverrideTestUI):
    def __init__(self, master=None):
        super().__init__(master)

    def optionMenuPrimary_CB(self, current_value):
        print("optionMenuPrimary_CB", current_value)

    def optionSecondary_CB(self, current_value):
        print("optionSecondary_CB", current_value)

    def segmentedButton_CB(self, current_value):
        print("segmentedButton_CB", current_value)

    def switchClicked_CB(self):
        print("switchClicked_CB", self.switchText_VAR.get(), self.switchValue_VAR.get())
        self.switchText_VAR.set(self.switchText_VAR.get()+"2")

    def ghostTab1_CB(self):
        print("ghostTab1_CB", self.ghostTab1_VAR.get())
        self.ghostTab1_VAR.set(self.ghostTab1_VAR.get()+"1")

    def GhostTab2_CB(self):
        print("GhostTab2_CB", self.ghostTab2_VAR.get())
        self.ghostTab2_VAR.set(self.ghostTab2_VAR.get() + "2")

    def radioButton_CB(self):
        print("radioButton_CB", self.radiobutton_VAR.get())
        print(self.button1Text_VAR.get())
        print(self.button2Text_VAR.get())
        print(self.button3Text_VAR.get())
        self.button1Text_VAR.set(self.button1Text_VAR.get()+"1")
        self.button2Text_VAR.set(self.button2Text_VAR.get()+"1")
        self.button3Text_VAR.set(self.button3Text_VAR.get()+"1")


if __name__ == "__main__":
    app = colorOverrideTest()
    app.run()
