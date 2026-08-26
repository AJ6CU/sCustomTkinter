#!/usr/bin/python3
"""
customCTK_WidgetTesterPart4

just tests each widget

UI source file: customCTK_WidgetTesterPart4.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import customCTK_WidgetTesterPart4ui as baseui


class customCTK_WidgetTesterPart4(baseui.customCTK_WidgetTesterPart4UI):
    def __init__(self, master=None):
        super().__init__(master)

    def scroll_CB(self, num):
        print("cont", num)

    def leftClick_CB(self):
        print("Cont leftClick")

    def rightClick_CB(self):
        print("Cont rightClick")

    def selector_CB(self, num):
        print("sel", num )

    def selectorLeft_CB(self):
        print("Sel leftClick")

    def selectorRight_CB(self):
        print("Sel rightClick")

    def pot(self, num):
        print("pot", num)

    def potLeft(self):
        # print("Pot leftClick")
        pass

    def potRight(self):
        # print("Pot rightClick")
        pass
    def callme(self, num):
        print("callme", type(num),num )

    def explorerSingle(self, name):
        print("single Click Explorer", name)

    def explorerDouble(self, name):
        print("double Click Explorer", name)


    def pathCommand(self, name):
        print("pathcommand", name)


if __name__ == "__main__":
    app = customCTK_WidgetTesterPart4()
    app.run()
