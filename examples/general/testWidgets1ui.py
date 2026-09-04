#!/usr/bin/python3
"""
testWidgets1

A test of sCustomTkinter widgets and code generatgion

UI source file: testWidgets1.ui
"""
import tkinter as tk
from customtkinter import set_appearance_mode
from scustomtkinter.sctk_button_primary import sCTkButtonPrimary
from scustomtkinter.sctk_button_secondary import sCTkButtonSecondary
from scustomtkinter.sctk_button_tertiary import sCTkButtonTertiary
from scustomtkinter.sctk_checkbox import sCTkCheckBox
from scustomtkinter.sctk_combobox import sCTkComboBox
from scustomtkinter.sctk_core import sCTk
from scustomtkinter.sctk_entry_primary import sCTkEntryPrimary
from scustomtkinter.sctk_entry_secondary import sCTkEntrySecondary
from scustomtkinter.sctk_frame import sCTkFrame
from scustomtkinter.sctk_frame_labeled_primary import sCTkFrameLabeledPrimary


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


class testWidgets1UI:
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
        set_appearance_mode("System")
        # First object created
        on_first_object_cb(sctk1)

        sctkframe1 = sCTkFrame(sctk1)
        sctkbuttonprimary1 = sCTkButtonPrimary(sctkframe1)
        sctkbuttonprimary1.configure(text='Primary Button')
        sctkbuttonprimary1.pack(pady=10, side="top")
        sctkbuttonprimary1.configure(command=self.primaryButton_CB)
        sctkbuttonsecondary1 = sCTkButtonSecondary(sctkframe1)
        sctkbuttonsecondary1.configure(text='Secondary Button')
        sctkbuttonsecondary1.pack(pady="0 10", side="top")
        sctkbuttonsecondary1.configure(command=self.secondaryButton_CB)
        sctkbuttontertiary1 = sCTkButtonTertiary(sctkframe1)
        sctkbuttontertiary1.configure(text='Tertiary Button')
        sctkbuttontertiary1.pack(pady="0 10", side="top")
        sctkbuttontertiary1.configure(command=self.tertiaryButton_CB)
        sctkframe1.grid(column=0, row=0)
        sctkframe2 = sCTkFrame(sctk1)
        sctkcheckbox1 = sCTkCheckBox(sctkframe2)
        self.check1_VAR = tk.StringVar()
        sctkcheckbox1.configure(text='Check 1', variable=self.check1_VAR)
        sctkcheckbox1.pack(pady=10, side="top")
        sctkcheckbox1.configure(command=self.check1_CB)
        sctkcheckbox2 = sCTkCheckBox(sctkframe2)
        self.check2_VAR = tk.StringVar()
        sctkcheckbox2.configure(text='Check 2', variable=self.check2_VAR)
        sctkcheckbox2.pack(pady="0 10", side="top")
        sctkcheckbox2.configure(command=self.check2_CB)
        sctkcheckbox3 = sCTkCheckBox(sctkframe2)
        self.check3_VAR = tk.StringVar()
        sctkcheckbox3.configure(text='Check 3', variable=self.check3_VAR)
        sctkcheckbox3.pack(pady="0 10", side="top")
        sctkcheckbox3.configure(command=self.check3_CB)
        self.comboBox1 = sCTkComboBox(sctkframe2)
        self.comboBox_VAR = tk.StringVar()
        self.comboBox1.configure(
            values=[
                "Apple",
                "Pear",
                "Orange"],
            variable=self.comboBox_VAR)
        self.comboBox1.pack(pady=10, side="top")
        self.comboBox1.configure(command=self.comboBox_CB)
        sctkframe2.grid(column=1, row=0)
        sctkframe3 = sCTkFrame(sctk1)
        self.primaryEntry = sCTkEntryPrimary(sctkframe3)
        self.primaryEntry_VAR = tk.StringVar()
        self.primaryEntry.configure(placeholder_text="primary entry", textvariable=self.primaryEntry_VAR, validatecommand="{"name": "validatecommand", "type": "command", "cbtype": "entry_validate", "args": "", "value": "primaryEntryValidate_CB"}", xscrollcommand="{"name": "xscrollcommand", "type": "command", "cbtype": "scroll", "value": "primaryEntryxscroll_CB"}")
        self.primaryEntry.pack(side="top")
        self.secondaryEntry = sCTkEntrySecondary(sctkframe3)
        self.secondaryEntry_VAR = tk.StringVar()
        self.secondaryEntry.configure(placeholder_text="secondary entry", textvariable=self.secondaryEntry_VAR, validatecommand="{"name": "validatecommand", "type": "command", "cbtype": "entry_validate", "args": "", "value": "secondaryEntry_CB"}")
        self.secondaryEntry.pack(side="top")
        sctkframe3.grid(column=2, row=0)
        sctkframelabeledprimary1 = sCTkFrameLabeledPrimary(sctk1)
        sctkframelabeledprimary1.configure(label_text="Radio Buttons")
        sctkframelabeledprimary1.grid(column=0, row=1)
        sctkframelabeledprimary2 = sCTkFrameLabeledPrimary(sctk1)
        sctkframelabeledprimary2.grid(column=1, row=1)
        sctkframelabeledprimary3 = sCTkFrameLabeledPrimary(sctk1)
        sctkframelabeledprimary3.grid(column=2, row=1)

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()

    def primaryButton_CB(self):
        pass

    def secondaryButton_CB(self):
        pass

    def tertiaryButton_CB(self):
        pass

    def check1_CB(self):
        pass

    def check2_CB(self):
        pass

    def check3_CB(self):
        pass

    def comboBox_CB(self, value):
        pass


if __name__ == "__main__":
    app = testWidgets1UI()
    app.run()
