#!/usr/bin/python3
"""
testWidgets1

A test of sCustomTkinter widgets and code generatgion

UI source file: testWidgets1.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import testWidgets1ui as baseui


class testWidgets1(baseui.testWidgets1UI):
    def __init__(self, master=None):
        super().__init__(master)

    def primaryButton_CB(self):
        print("Primary Button")

    def secondaryButton_CB(self):
        print("Secondary Button")

    def tertiaryButton_CB(self):
        print("Tertiary Button")

    def check1_CB(self):
        print("Check1=", self.check1_VAR.get())

    def check2_CB(self):
        print("Check2=", self.check2_VAR.get())

    def check3_CB(self):
        print("Check3=", self.check3_VAR.get())

    def comboBox_CB(self, value):
        print("ComboBox=", self.comboBox_VAR.get(), value, self.comboBox1.get())
        print("var interp:   ", self.comboBox_VAR._root)
        print("widget interp:", self.comboBox1.winfo_toplevel())
        print("same tk:      ", self.comboBox_VAR._tk is self.comboBox1.tk)

    def CTkcomboBox_CB(self, value):
        print("CTkcomboBox=", self.CTkcomboBox_VAR.get(), value, self.comboBox2.get())

    def ttkComboBox_CB(self, event=None):
        print("ttkComboBox=", self.ttkComboBox_VAR.get(), event, self.comboBox3.get())



if __name__ == "__main__":
    root = tk.Tk()
    app = testWidgets1(root)
    app.run()
