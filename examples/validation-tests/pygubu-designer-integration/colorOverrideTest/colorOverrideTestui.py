#!/usr/bin/python3
"""
colorOverrideTest

colorOverrideTest

UI source file: coverOverrideTest.ui
"""
import tkinter as tk
from scustomtkinter.sctk_button_primary import sCTkButtonPrimary
from scustomtkinter.sctk_button_secondary import sCTkButtonSecondary
from scustomtkinter.sctk_button_tertiary import sCTkButtonTertiary
from scustomtkinter.sctk_core import sCTk
from scustomtkinter.sctk_frame import sCTkFrame
from scustomtkinter.sctk_label_primary import sCTkLabelPrimary
from scustomtkinter.sctk_label_secondary import sCTkLabelSecondary
from scustomtkinter.sctk_optionmenu_primary import sCTkOptionMenuPrimary
from scustomtkinter.sctk_optionmenu_secondary import sCTkOptionMenuSecondary
from scustomtkinter.sctk_radiobutton import sCTkRadioButton
from scustomtkinter.sctk_segmentedbutton import sCTkSegmentedButton
from scustomtkinter.sctk_spinbox import sCTkSpinbox
from scustomtkinter.sctk_switch import sCTkSwitch
from scustomtkinter.sctk_tabview import sCTkTabview


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


class colorOverrideTestUI:
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
        sctk1 = sCTk(None)
        # First object created
        on_first_object_cb(sctk1)

        sctkoptionmenuprimary1 = sCTkOptionMenuPrimary(sctk1)
        self.optionMenuPrimary_VAR = tk.StringVar()
        sctkoptionmenuprimary1.configure(
            state="disabled",
            values=[
                "School",
                "Canyon",
                "Sandringham"],
            variable=self.optionMenuPrimary_VAR)
        sctkoptionmenuprimary1.pack(side="top")
        sctkoptionmenuprimary1.configure(command=self.optionMenuPrimary_CB)
        sctkoptionmenusecondary1 = sCTkOptionMenuSecondary(sctk1)
        self.optionMenuSecondary_VAR = tk.StringVar()
        sctkoptionmenusecondary1.configure(
            state="disabled",
            values=[
                "School",
                "Canyon",
                "Sandringham"],
            variable=self.optionMenuSecondary_VAR)
        sctkoptionmenusecondary1.pack(side="top")
        sctkoptionmenusecondary1.configure(command=self.optionSecondary_CB)
        sctksegmentedbutton1 = sCTkSegmentedButton(sctk1)
        self.segmentedButton_VAR = tk.StringVar()
        sctksegmentedbutton1.configure(
            state="disabled",
            values=[
                "VW",
                "Porshe",
                "240Z"],
            variable=self.segmentedButton_VAR)
        sctksegmentedbutton1.pack(side="top")
        sctksegmentedbutton1.configure(command=self.segmentedButton_CB)
        sctkswitch1 = sCTkSwitch(sctk1, onvalue=1, offvalue=0)
        self.switchText_VAR = tk.StringVar(value='make choice')
        self.switchValue_VAR = tk.StringVar()
        sctkswitch1.configure(
            state="disabled",
            text='make choice',
            textvariable=self.switchText_VAR,
            variable=self.switchValue_VAR)
        sctkswitch1.pack(side="top")
        sctkswitch1.configure(command=self.switchClicked_CB)
        sctktabview1 = sCTkTabview(sctk1)
        sctktabview1.configure(state="disabled")
        sctktabviewtab1 = sctktabview1.add("tab1")  # returns an sCTkFrame
        sctklabelsecondary1 = sCTkLabelSecondary(sctktabviewtab1)
        sctklabelsecondary1.configure(
            state="disabled",
            text='this is secondary label tab 1\n')
        sctklabelsecondary1.pack(side="top")
        sctkbuttontertiary1 = sCTkButtonTertiary(sctktabviewtab1)
        self.ghostTab1_VAR = tk.StringVar(value='GhostTab 1')
        sctkbuttontertiary1.configure(
            state="disabled",
            text='GhostTab 1',
            textvariable=self.ghostTab1_VAR)
        sctkbuttontertiary1.pack(side="top")
        sctkbuttontertiary1.configure(command=self.ghostTab1_CB)
        sctktabviewtab2 = sctktabview1.add("tab2")  # returns an sCTkFrame
        sctklabelprimary1 = sCTkLabelPrimary(sctktabviewtab2)
        sctklabelprimary1.configure(
            state="disabled",
            text='this is primary label on tab 2')
        sctklabelprimary1.pack(side="top")
        sctkbuttontertiary2 = sCTkButtonTertiary(sctktabviewtab2)
        self.ghostTab2_VAR = tk.StringVar(value='Ghost Tab2')
        sctkbuttontertiary2.configure(
            state="disabled",
            text='Ghost Tab2',
            textvariable=self.ghostTab2_VAR)
        sctkbuttontertiary2.pack(side="top")
        sctkbuttontertiary2.configure(command=self.GhostTab2_CB)
        sctktabview1.pack(side="top")
        sctkframe1 = sCTkFrame(sctk1)
        sctkradiobutton1 = sCTkRadioButton(sctkframe1, value=1)
        self.button1Text_VAR = tk.StringVar(value='button1')
        self.radiobutton_VAR = tk.StringVar(value='1')
        sctkradiobutton1.configure(
            state="disabled",
            text='button1',
            textvariable=self.button1Text_VAR,
            variable=self.radiobutton_VAR)
        sctkradiobutton1.pack(pady="20 0", side="top")
        sctkradiobutton1.configure(command=self.radioButton_CB)
        sctkradiobutton2 = sCTkRadioButton(sctkframe1, value=2)
        self.button2Text_VAR = tk.StringVar(value='button2')
        sctkradiobutton2.configure(
            state="normal",
            text='button2',
            textvariable=self.button2Text_VAR,
            variable=self.radiobutton_VAR)
        sctkradiobutton2.pack(side="top")
        sctkradiobutton2.configure(command=self.radioButton_CB)
        sctkradiobutton3 = sCTkRadioButton(sctkframe1, value=3)
        self.button3Text_VAR = tk.StringVar(value='button3')
        sctkradiobutton3.configure(
            state="disabled",
            text='button3',
            textvariable=self.button3Text_VAR,
            variable=self.radiobutton_VAR)
        sctkradiobutton3.pack(pady="0 20", side="top")
        sctkradiobutton3.configure(command=self.radioButton_CB)
        sctkframe1.pack(side="top")
        sctkbuttonprimary1 = sCTkButtonPrimary(sctk1)
        sctkbuttonprimary1.configure(state="disabled", text='first')
        sctkbuttonprimary1.pack(side="top")
        sctkbuttonsecondary1 = sCTkButtonSecondary(sctk1)
        sctkbuttonsecondary1.configure(state="disabled", text='second')
        sctkbuttonsecondary1.pack(side="top")
        sctkbuttontertiary3 = sCTkButtonTertiary(sctk1)
        sctkbuttontertiary3.configure(state="disabled", text='ghost')
        sctkbuttontertiary3.pack(side="top")
        sctkspinbox1 = sCTkSpinbox(sctk1)
        sctkspinbox1.configure(state="disabled", values=["vw", "datsun"])
        sctkspinbox1.pack(side="top")

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()

    def optionMenuPrimary_CB(self, current_value):
        pass

    def optionSecondary_CB(self, current_value):
        pass

    def segmentedButton_CB(self, current_value):
        pass

    def switchClicked_CB(self):
        pass

    def ghostTab1_CB(self):
        pass

    def GhostTab2_CB(self):
        pass

    def radioButton_CB(self):
        pass


if __name__ == "__main__":
    app = colorOverrideTestUI()
    app.run()
