#!/usr/bin/python3
"""
customCTK_WidgetTester

just tests eah widget

UI source file: customCTK_WidgetTester.ui
"""
import tkinter as tk
from buttonPrimary import buttonPrimary
from buttonSecondary import buttonSecondary
from buttonTertiary import buttonTertiary
from customtkinter import (
    CTk,
    CTkButton,
    CTkEntry,
    CTkFont,
    CTkFrame,
    CTkLabel,
    CTkOptionMenu,
    CTkScrollableFrame,
    CTkTextbox)
from entryPrimary import entryPrimary
from entrySecondary import entrySecondary
from frameLabeledPrimary import frameLabeledPrimary
from frameLabeledSecondary import frameLabeledSecondary
from frameOutlined import frameOutlined
from labelPrimary import labelPrimary
from labelSecondary import labelSecondary
from labelTertiary import labelTertiary
from optionMenuPrimary import optionMenuPrimary
from optionMenuSecondary import optionMenuSecondary
from textboxPrimary import textboxPrimary
from textboxSecondary import textboxSecondary


def safe_i18n_translator(value):
    """i18n - Setup translator in derived class file"""
    return value


def safe_fo_callback(widget):
    """on first objec callback - Setup callback in derived class file."""
    pass


def safe_image_loader(master, image_name: str):
    """Image loader - Setup image_loader in derived class file."""
    img = None
    try:
        img = tk.PhotoImage(file=image_name, master=master)
    except tk.TclError:
        pass
    return img


class customCTK_WidgetTesterUI:
    def __init__(
        self,
        master=None,
        *,
        translator=None,
        on_first_object_cb=None,
        data_pool=None,
        image_loader=None
    ):
        if translator is None:
            translator = safe_i18n_translator
        _ = translator  # i18n string marker.
        if image_loader is None:
            image_loader = safe_image_loader
        if on_first_object_cb is None:
            on_first_object_cb = safe_fo_callback
        # build ui
        ctk1 = CTk(None)
        # First object created
        on_first_object_cb(ctk1)

        ctkframe1 = CTkFrame(ctk1)
        ctkframe1.configure(border_color="green", border_width=2)
        ctkscrollableframe1 = CTkScrollableFrame(ctkframe1)
        ctkscrollableframe1.configure(
            border_color="green",
            border_width=2,
            label_anchor="s",
            label_font=CTkFont(
                "Arial",
                15,
                "bold",
                "roman",
                False,
                False),
            label_text="Buttons	",
            label_text_color="#F9FAFB")
        ctkbutton1 = CTkButton(ctkscrollableframe1)
        ctkbutton1.configure(text='myctk button')
        ctkbutton1.pack(pady=10, side="top")
        self.primary1 = buttonPrimary(ctkscrollableframe1)
        self.primary1.configure(text='primary button')
        self.primary1.pack(pady=10, side="top")
        self.primary1.configure(command=self.primary1_CB)
        self.secondary2 = buttonSecondary(ctkscrollableframe1)
        self.secondary2.configure(text='secondary button')
        self.secondary2.pack(pady=10, side="top")
        self.secondary2.configure(command=self.secondary2_CB)
        self.ghost3 = buttonTertiary(ctkscrollableframe1)
        self.ghost3.configure(text='ghost button')
        self.ghost3.pack(pady=10, side="top")
        self.ghost3.configure(command=self.ghost3_cb)
        ctkscrollableframe1.grid(column=0, padx="10 0", pady=10, row=0)
        ctkscrollableframe2 = CTkScrollableFrame(ctkframe1)
        ctkscrollableframe2.configure(
            border_color="green",
            border_width=2,
            label_anchor="w",
            label_text="Entry")
        self.testentry = CTkEntry(ctkscrollableframe2)
        self.testentry.configure(
            font=CTkFont(
                "arial",
                12,
                "bold",
                "italic",
                True,
                True),
            placeholder_text_color="gray")
        self.testentry.delete(0, "end")
        self.testentry.insert(0, 'ctk Entry')
        self.testentry.pack(pady=10, side="top")
        self.helloEntryP1 = entryPrimary(ctkscrollableframe2)
        self.helloEntryP1.delete(0, "end")
        self.helloEntryP1.insert(0, 'Entry Primary')
        self.helloEntryP1.pack(pady=10, side="top")
        secondaryentry1 = entrySecondary(ctkscrollableframe2)
        secondaryentry1.delete(0, "end")
        secondaryentry1.insert(0, 'Entry Secondary')
        secondaryentry1.pack(pady=10, side="top")
        ctkscrollableframe2.grid(column=1, padx="20 0", pady=10, row=0)
        ctkscrollableframe4 = CTkScrollableFrame(ctkframe1)
        ctkscrollableframe4.configure(
            border_color="green",
            border_width=2,
            label_anchor="w",
            label_text="Option Menus")
        ctkoptionmenu1 = CTkOptionMenu(ctkscrollableframe4)
        ctkoptionmenu1.configure(values=["apple", "orange", "grape"])
        ctkoptionmenu1.pack(pady=10, side="top")
        self.myOptionMenu = optionMenuPrimary(ctkscrollableframe4)
        self.myOptionMenu_VAR = tk.StringVar()
        self.myOptionMenu.configure(variable=self.myOptionMenu_VAR)
        self.myOptionMenu.pack(pady=10, side="top")
        self.myOptionMenu.configure(command=self.menuOption_CB)
        self.secondaryOption = optionMenuSecondary(ctkscrollableframe4)
        self.secondaryOption.pack(pady=10, side="top")
        ctkscrollableframe4.grid(column=2, padx="20 10", pady=10, row=0)
        ctkscrollableframe3 = CTkScrollableFrame(ctkframe1)
        ctkscrollableframe3.configure(
            border_color="green",
            border_width=2,
            label_anchor="w",
            label_text="Labels")
        ctklabel1 = CTkLabel(ctkscrollableframe3)
        ctklabel1.configure(
            justify="left",
            state="normal",
            text='ctkLabel',
            width=200)
        ctklabel1.pack(pady=10, side="top")
        self.primaryLabel = labelPrimary(ctkscrollableframe3)
        self.primaryLabel_VAR = tk.StringVar(value='primary Label')
        self.primaryLabel.configure(
            anchor="center",
            justify="center",
            padx=10,
            pady=10,
            state="normal",
            takefocus=False,
            text='primary Label',
            textvariable=self.primaryLabel_VAR)
        self.primaryLabel.pack(pady=10, side="top")
        secondarylabel1 = labelSecondary(ctkscrollableframe3)
        secondarylabel1.configure(
            padx=5,
            pady=5,
            state="normal",
            text='secondary Label')
        secondarylabel1.pack(pady=10, side="top")
        tertiarylabel1 = labelTertiary(ctkscrollableframe3)
        tertiarylabel1.configure(state="normal", text='tertiary label')
        tertiarylabel1.pack(side="top")
        ctkscrollableframe3.grid(column=0, padx="10 0", pady=20, row=1)
        framelabeled1 = frameLabeledPrimary(ctkframe1)
        framelabeled1.configure(
            label_anchor="w",
            label_text="frameLabeledPrimary ")
        ctkbutton2 = CTkButton(framelabeled1)
        ctkbutton2.configure(text='ctkbutton2')
        ctkbutton2.grid(column=0, row=0)
        labelsecondary1 = labelSecondary(framelabeled1)
        labelsecondary1.configure(
            anchor="center",
            justify="center",
            text='labelFrame equiv')
        labelsecondary1.grid(column=0, row=1)
        framelabeledsecondary1 = frameLabeledSecondary(framelabeled1)
        framelabeledsecondary1.configure(
            height=50,
            label_anchor="w",
            label_text="frameLabeledSecondary",
            width=150)
        ctkentry1 = CTkEntry(framelabeledsecondary1)
        ctkentry1.delete(0, "end")
        ctkentry1.insert(0, 'ctkentry1')
        ctkentry1.pack(pady=10, side="top")
        framelabeledsecondary1.grid(column=0, row=2)
        framelabeled1.grid(column=1, padx="20 10", pady=20, row=1, sticky="ew")
        framelabeled1.bind("<MouseWheel>", self.callback, add="")
        framelabeledprimary1 = frameLabeledPrimary(ctkframe1)
        framelabeledprimary1.configure(
            label_anchor="w", label_text="frameLabeledPrimary ")
        ctkbutton3 = CTkButton(framelabeledprimary1)
        ctkbutton3.grid(column=0, row=0)
        frameoutlined1 = frameOutlined(framelabeledprimary1)
        frameoutlined1.configure(height=150, width=175)
        ctklabel2 = CTkLabel(frameoutlined1)
        ctklabel2.configure(text='ctklabel2')
        ctklabel2.pack(pady=5, side="top")
        ctklabel3 = CTkLabel(frameoutlined1)
        ctklabel3.configure(text='ctklabel3')
        ctklabel3.pack(side="top")
        ctklabel5 = CTkLabel(frameoutlined1)
        ctklabel5.configure(text='ctklabel5')
        ctklabel5.pack(pady=5, side="top")
        frameoutlined1.grid(column=0, padx=10, pady=10, row=1, sticky="nsew")
        framelabeledprimary1.grid(
            column=2,
            padx="20 10",
            pady=20,
            row=1,
            sticky="ew")
        framelabeledprimary1.bind("<MouseWheel>", self.callback, add="")
        framelabeledprimary2 = frameLabeledPrimary(ctkframe1)
        framelabeledprimary2.configure(
            label_anchor="w", label_text="textboxes primary")
        textboxprimary1 = textboxPrimary(framelabeledprimary2)
        textboxprimary1.configure(
            font=CTkFont(
                "Arial",
                24,
                None,
                "roman",
                False,
                False),
            insertborderwidth=1,
            state="normal")
        _text_ = 'will this fail?\nI hope not'
        textboxprimary1.delete("0.0", "end")
        textboxprimary1.insert("0.0", _text_)
        textboxprimary1.pack(side="top")
        framelabeledprimary2.grid(column=0, row=2)
        framelabeledprimary3 = frameLabeledPrimary(ctkframe1)
        framelabeledprimary3.configure(
            label_anchor="w", label_text="outline frame")
        frameoutlined2 = frameOutlined(framelabeledprimary3)
        frameoutlined2.configure(height=150, width=150)
        ctktextbox1 = CTkTextbox(frameoutlined2)
        ctktextbox1.configure(
            font=CTkFont(
                "Times New Roman",
                20,
                "bold",
                "italic",
                True,
                True))
        _text_ = 'testfoo'
        ctktextbox1.delete("0.0", "end")
        ctktextbox1.insert("0.0", _text_)
        ctktextbox1.pack(side="top")
        frameoutlined2.pack(side="top")
        framelabeledprimary3.grid(column=2, row=2)
        framelabeledprimary4 = frameLabeledPrimary(ctkframe1)
        framelabeledprimary4.configure(
            label_anchor="w", label_text="textboxes secondary")
        textboxsecondary1 = textboxSecondary(framelabeledprimary4)
        textboxsecondary1.configure(
            font=CTkFont(
                "Times New Roman",
                16,
                "bold",
                "italic",
                True,
                True),
            insertborderwidth=2,
            insertofftime=0,
            insertontime=0,
            insertwidth=0,
            selectborderwidth=0)
        _text_ = 'Times Roman 15 normal'
        textboxsecondary1.delete("0.0", "end")
        textboxsecondary1.insert("0.0", _text_)
        textboxsecondary1.pack(side="top")
        framelabeledprimary4.grid(column=1, row=2)
        ctkframe1.grid(column=0, row=0)

        # Main widget
        self.mainwindow = ctk1

    def run(self):
        self.mainwindow.mainloop()

    def primary1_CB(self):
        pass

    def secondary2_CB(self):
        pass

    def ghost3_cb(self):
        pass

    def menuOption_CB(self, current_value):
        pass

    def callback(self, event=None):
        pass


if __name__ == "__main__":
    app = customCTK_WidgetTesterUI()
    app.run()
