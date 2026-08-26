#!/usr/bin/python3
"""
customCTK_WidgetTesterPart3

just tests each widget

UI source file: customCTK_WidgetTesterPart3.ui
"""
import tkinter.ttk as ttk
from customtkinter import (
    CTk,
    CTkCheckBox,
    CTkComboBox,
    CTkFrame,
    CTkLabel,
    CTkProgressBar,
    CTkRadioButton,
    CTkSlider,
    CTkSwitch)
from sCTkButtonPrimary import sCTkButtonPrimary
from sCTkCheckBox import sCTkCheckBox
from sCTkComboBox import sCTkComboBox
from sCTkFrame import sCTkFrame
from sCTkFrameLabeledPrimary import sCTkFrameLabeledPrimary
from sCTkFrameLabeledSecondary import sCTkFrameLabeledSecondary
from sCTkFrameOutlined import sCTkFrameOutlined
from sCTkLabelPrimary import sCTkLabelPrimary
from sCTkLabelSecondary import sCTkLabelSecondary
from sCTkLabelTertiary import sCTkLabelTertiary
from sCTkPathChooser import sCTkPathChooser
from sCTkProgressBar import sCTkProgressBar
from sCTkRadioButton import sCTkRadioButton
from sCTkScrollableFrame import sCTkScrollableFrame
from sCTkSelector import sCTkSelector
from sCTkSeparator import sCTkSeparator
from sCTkSlider import sCTkSlider
from sCTkSwitch import sCTkSwitch


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


class customCTK_WidgetTesterPart3UI:
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
        framelabeledprimary5 = sCTkFrameLabeledPrimary(ctkframe1)
        framelabeledprimary5.configure(
            label_anchor="w", label_text="CheckBox and ComboBox")
        sctklabelsecondary1 = sCTkLabelSecondary(framelabeledprimary5)
        sctklabelsecondary1.configure(state="disabled", text='ctk:')
        sctklabelsecondary1.grid(column=0, padx="0 5", row=0, sticky="e")
        ctkcheckbox1 = CTkCheckBox(framelabeledprimary5)
        ctkcheckbox1.configure(text='ctkCheckbox')
        ctkcheckbox1.grid(column=1, row=0, sticky="w")
        ctklabel2 = CTkLabel(framelabeledprimary5)
        ctklabel2.configure(text='subCTk:')
        ctklabel2.grid(column=0, padx="0 5", row=1, sticky="e")
        sctkcheckbox1 = sCTkCheckBox(framelabeledprimary5)
        sctkcheckbox1.configure(text='sctkcheckbox1')
        sctkcheckbox1.grid(column=1, row=1, sticky="w")
        ctklabel3 = CTkLabel(framelabeledprimary5)
        ctklabel3.configure(text='ctk:')
        ctklabel3.grid(column=0, padx="0 5", pady="20 0", row=2, sticky="e")
        ctkcombobox1 = CTkComboBox(framelabeledprimary5)
        ctkcombobox1.configure(values=["apple", "pear", "grape"])
        ctkcombobox1.grid(column=1, pady="20 0", row=2)
        ctklabel4 = CTkLabel(framelabeledprimary5)
        ctklabel4.configure(text='subCTk:')
        ctklabel4.grid(column=0, padx="0 5", pady="10 0", row=3, sticky="e")
        sctkcombobox1 = sCTkComboBox(framelabeledprimary5)
        sctkcombobox1.configure(values=["apple", "pear", "grape"])
        sctkcombobox1.grid(column=1, row=3)
        framelabeledprimary5.grid(
            column=0,
            padx="20 10",
            pady=20,
            row=0,
            sticky="ew")
        framelabeledprimary5.bind("<MouseWheel>", self.callback, add="")
        framelabeled1 = sCTkFrameLabeledPrimary(ctkframe1)
        framelabeled1.configure(
            label_anchor="w",
            label_text="Progressbars and Sliders")
        ctklabel5 = CTkLabel(framelabeled1)
        ctklabel5.configure(text='ctk:')
        ctklabel5.pack()
        ctkprogressbar1 = CTkProgressBar(framelabeled1)
        ctkprogressbar1.pack(side="top")
        ctklabel6 = CTkLabel(framelabeled1)
        ctklabel6.configure(text='subCTk:')
        ctklabel6.pack()
        progressbar1 = sCTkProgressBar(framelabeled1)
        progressbar1.pack(side="top")
        ctklabel7 = CTkLabel(framelabeled1)
        ctklabel7.configure(text='ctk:')
        ctklabel7.pack(pady="20 0")
        ctkslider1 = CTkSlider(framelabeled1)
        ctkslider1.configure(state="disabled")
        ctkslider1.pack(side="top")
        ctklabel8 = CTkLabel(framelabeled1)
        ctklabel8.configure(text='subCTk:')
        ctklabel8.pack()
        slider1 = sCTkSlider(framelabeled1)
        slider1.configure(from_=0, state="disabled", to=100)
        slider1.pack(side="top")
        framelabeled1.grid(column=1, padx="20 10", pady=20, row=0, sticky="ew")
        framelabeled1.bind("<MouseWheel>", self.callback, add="")
        framelabeledprimary6 = sCTkFrameLabeledPrimary(ctkframe1)
        framelabeledprimary6.configure(
            label_anchor="w",
            label_text="RadioButton and Switch")
        ctklabel9 = CTkLabel(framelabeledprimary6)
        ctklabel9.configure(text='ctk:')
        ctklabel9.grid(column=0, padx="0 5", row=0, sticky="e")
        self.ctkradiobutton = CTkRadioButton(framelabeledprimary6)
        self.ctkradiobutton.configure(text='ctkradiobutton')
        self.ctkradiobutton.grid(column=1, row=0, sticky="w")
        ctklabel10 = CTkLabel(framelabeledprimary6)
        ctklabel10.configure(text='subCTk:')
        ctklabel10.grid(column=0, padx="0 5", row=1, sticky="e")
        radiobutton1 = sCTkRadioButton(framelabeledprimary6)
        radiobutton1.configure(text='subradiobutton')
        radiobutton1.grid(column=1, row=1, sticky="w")
        ctklabel11 = CTkLabel(framelabeledprimary6)
        ctklabel11.configure(text='ctk:')
        ctklabel11.grid(column=0, padx="0 5", pady="20 0", row=2, sticky="e")
        ctkswitch1 = CTkSwitch(framelabeledprimary6)
        ctkswitch1.configure(text='ctkswitch')
        ctkswitch1.grid(column=1, pady="20 0", row=2, sticky="w")
        ctklabel12 = CTkLabel(framelabeledprimary6)
        ctklabel12.configure(text='subCTk:')
        ctklabel12.grid(column=0, padx="0 5", row=3, sticky="e")
        switch1 = sCTkSwitch(framelabeledprimary6)
        switch1.configure(text='subswitch')
        switch1.grid(column=1, row=3, sticky="w")
        framelabeledprimary6.grid(
            column=2,
            padx="20 10",
            pady=20,
            row=0,
            sticky="ew")
        framelabeledprimary6.bind("<MouseWheel>", self.callback, add="")
        sctkscrollableframe1 = sCTkScrollableFrame(
            ctkframe1, orientation="vertical")
        sctkcheckbox2 = sCTkCheckBox(sctkscrollableframe1)
        sctkcheckbox2.configure(text='sctkcheckbox2')
        sctkcheckbox2.pack(side="top")
        sctklabelprimary1 = sCTkLabelPrimary(sctkscrollableframe1)
        sctklabelprimary1.configure(
            text='sctklabelprimary1sctklabelprimary1sctklabelprimary1')
        sctklabelprimary1.pack(side="top")
        sctklabelprimary2 = sCTkLabelPrimary(sctkscrollableframe1)
        sctklabelprimary2.configure(text='sctklabelprimary1')
        sctklabelprimary2.pack(side="top")
        sctklabelprimary3 = sCTkLabelPrimary(sctkscrollableframe1)
        sctklabelprimary3.configure(text='sctklabelprimary1')
        sctklabelprimary3.pack(side="top")
        sctklabelprimary4 = sCTkLabelPrimary(sctkscrollableframe1)
        sctklabelprimary4.configure(text='sctklabelprimary1')
        sctklabelprimary4.pack(side="top")
        sctklabelprimary5 = sCTkLabelPrimary(sctkscrollableframe1)
        sctklabelprimary5.configure(text='sctklabelprimary1')
        sctklabelprimary5.pack(side="top")
        sctklabelprimary6 = sCTkLabelPrimary(sctkscrollableframe1)
        sctklabelprimary6.configure(text='sctklabelprimary1')
        sctklabelprimary6.pack(side="top")
        sctklabelprimary7 = sCTkLabelPrimary(sctkscrollableframe1)
        sctklabelprimary7.configure(text='sctklabelprimary1')
        sctklabelprimary7.pack(side="top")
        sctklabelprimary8 = sCTkLabelPrimary(sctkscrollableframe1)
        sctklabelprimary8.configure(text='sctklabelprimary1')
        sctklabelprimary8.pack(side="top")
        sctklabelprimary9 = sCTkLabelPrimary(sctkscrollableframe1)
        sctklabelprimary9.configure(text='sctklabelprimary1')
        sctklabelprimary9.pack(side="top")
        sctkscrollableframe1.grid(column=0, row=1)
        sctkframe1 = sCTkFrame(ctkframe1)
        sctklabelprimary10 = sCTkLabelPrimary(sctkframe1)
        sctklabelprimary10.configure(text='standard frame')
        sctklabelprimary10.pack(side="top")
        sctkcheckbox3 = sCTkCheckBox(sctkframe1)
        sctkcheckbox3.configure(state="normal", text='sctkcheckbox3')
        sctkcheckbox3.pack(pady="10 30", side="top")
        sctkframeoutlined1 = sCTkFrameOutlined(sctkframe1)
        sctkcheckbox4 = sCTkCheckBox(sctkframeoutlined1)
        sctkcheckbox4.configure(state="normal", text='sctkcheckbox4')
        sctkcheckbox4.pack(pady="5 30", side="top")
        sctkcombobox4 = sCTkComboBox(sctkframeoutlined1)
        sctkcombobox4.configure(values=["one", "two", "three"])
        sctkcombobox4.pack(side="top")
        sctkframeoutlined1.pack(pady="20 0", side="top")
        sctkframe1.grid(column=1, row=1)
        sctkframe2 = sCTkFrame(ctkframe1)
        sctkpathchooser1 = sCTkPathChooser(sctkframe2)
        sctkpathchooser1.configure(
            btn_width=5,
            height=100,
            state="disabled",
            width=500)
        sctkpathchooser1.pack(side="top")
        sctkframe2.grid(column=2, row=1)
        sctkframelabeledsecondary1 = sCTkFrameLabeledSecondary(ctkframe1)
        sctkframelabeledsecondary1.configure(
            label_anchor="e", label_text="Secondary Frame")
        sctklabelprimary11 = sCTkLabelPrimary(sctkframelabeledsecondary1)
        sctklabelprimary11.configure(
            state="disabled", text='sctklabelprimary11')
        sctklabelprimary11.pack(side="top")
        sctklabelsecondary2 = sCTkLabelSecondary(sctkframelabeledsecondary1)
        sctklabelsecondary2.configure(
            state="disabled", text='sctklabelsecondary2')
        sctklabelsecondary2.pack(side="top")
        sctklabeltertiary1 = sCTkLabelTertiary(sctkframelabeledsecondary1)
        sctklabeltertiary1.configure(
            state="disabled", text='sctklabeltertiary1')
        sctklabeltertiary1.pack(side="top")
        sctkcheckbox5 = sCTkCheckBox(sctkframelabeledsecondary1)
        sctkcheckbox5.configure(state="disabled", text='sctkcheckbox5')
        sctkcheckbox5.pack(side="top")
        label1 = ttk.Label(sctkframelabeledsecondary1)
        label1.configure(text='label1')
        label1.pack(side="top")
        ctklabel1 = CTkLabel(sctkframelabeledsecondary1)
        ctklabel1.configure(state="disabled", text='ctklabel1')
        ctklabel1.pack(side="top")
        sctkframelabeledsecondary1.grid(column=0, row=2)
        sctkframe3 = sCTkFrame(ctkframe1)
        sctkselector1 = sCTkSelector(sctkframe3)
        sctkselector1.configure(
            items=[
                'apple',
                'pear',
                'orange'],
            multiple_choices=True,
            state='normal')
        sctkselector1.pack(expand=True, fill="x", side="top")
        sctkframe3.grid(column=1, row=2)
        sctkframe4 = sCTkFrame(ctkframe1)
        sctkbuttonprimary1 = sCTkButtonPrimary(sctkframe4)
        sctkbuttonprimary1.configure(
            state="disabled", text='sctkbuttonprimary1')
        sctkbuttonprimary1.grid(column=0, row=0)
        sctkseparator1 = sCTkSeparator(sctkframe4)
        sctkseparator1.configure(
            dash="3,3",
            orientation="vertical",
            text='hello2',
            width=50)
        sctkseparator1.grid(column=1, padx=10, pady=20, row=0, sticky="ew")
        sctkbuttonprimary2 = sCTkButtonPrimary(sctkframe4)
        sctkbuttonprimary2.configure(text='sctkbuttonprimary2')
        sctkbuttonprimary2.grid(column=2, row=0)
        sctkframe4.grid(column=2, row=2)
        ctkframe1.pack(side="top")

        # Main widget
        self.mainwindow = ctk1

    def run(self):
        self.mainwindow.mainloop()

    def callback(self, event=None):
        pass


if __name__ == "__main__":
    app = customCTK_WidgetTesterPart3UI()
    app.run()
