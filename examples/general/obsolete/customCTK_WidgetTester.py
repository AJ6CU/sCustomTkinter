#!/usr/bin/python3
"""
customCTK_WidgetTester

just tests eah widget

UI source file: customCTK_WidgetTester.ui
"""
import sys
import os
#
# # 1. Get the absolute directory where THIS script file lives
# current_file_dir = os.path.dirname(os.path.abspath(__file__))
#
# # 2. Join it with the widgets folder name
# subfolder_path = os.path.join(current_file_dir, "widgets")
#
# # 3. Safely insert it into the system path
# sys.path.insert(0, subfolder_path)

import tkinter as tk
import tkinter.ttk as ttk
import customCTK_WidgetTesterui as baseui



class widgettesterNew(baseui.customCTK_WidgetTesterUI):
    def __init__(self, master=None):
        super().__init__(master)
        self.myOptionMenu.update_list(["primary","apple", "banana", "orange"])
        self.secondaryOption.update_list(["secondary", "vw", "porsche","tesla"])
        self.primaryLabel_VAR.set("a primary lavel")

    def primary1_CB(self):
        pass

    def secondary2_CB(self):
        pass

    def ghost3_cb(self):
        pass

    def menuOption_CB(self, selection):
        print("menuOption selected:", self.myOptionMenu_VAR.get(), selection)


if __name__ == "__main__":
    app = widgettesterNew()
    app.run()