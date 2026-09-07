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
        print("ComboBox=", self.comboBox_VAR.get(), "*", value, self.comboBox1.get())

    def primaryEntryValidate_CB(self, p_entry_value):
        print("PrimaryEntryValidate=", self.primaryEntry_VAR.get(), p_entry_value, self.primaryEntry.get())

    def primaryEntryxscroll_CB(self, mode=None, value=None, units=None):
        pass

    def secondaryEntryValidate_CB(self, i_index, p_entry_value):
        print("SecondaryEntryValidate=", self.secondaryEntry_VAR.get(), p_entry_value)

    def secondaryEntryxscroll_CB(self, mode=None, value=None, units=None):
        pass


if __name__ == "__main__":
    app = testWidgets1()
    app.run()
