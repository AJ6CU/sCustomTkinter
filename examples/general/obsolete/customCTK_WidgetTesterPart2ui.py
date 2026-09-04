#!/usr/bin/python3
"""
customCTK_WidgetTesterPart2

just tests each widget

UI source file: customCTK_WidgetTesterPart2.ui
"""
from customtkinter import (
    CTk,
    CTkCheckBox,
    CTkComboBox,
    CTkFrame,
    CTkLabel,
    CTkOptionMenu,
    CTkProgressBar,
    CTkRadioButton,
    CTkSegmentedButton,
    CTkSlider,
    CTkSwitch)
from sCTkButtonSecondary import sCTkButtonSecondary
from sCTkCheckBox import sCTkCheckBox
from sCTkComboBox import sCTkComboBox
from sCTkFrameLabeledPrimary import sCTkFrameLabeledPrimary
from sCTkLabelPrimary import sCTkLabelPrimary
from sCTkOptionMenuPrimary import sCTkOptionMenuPrimary
from sCTkOptionMenuSecondary import sCTkOptionMenuSecondary
from sCTkProgressBar import sCTkProgressBar
from sCTkRadioButton import sCTkRadioButton
from sCTkScrollbar import sCTkScrollbar
from sCTkSegmentedButton import sCTkSegmentedButton
from sCTkSlider import sCTkSlider
from sCTkSwitch import sCTkSwitch
from sCTkTabview import sCTkTabview
from sCTkTextboxPrimary import sCTkTextboxPrimary
from sCTkTextboxSecondary import sCTkTextboxSecondary


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


class customCTK_WidgetTesterPart2UI:
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
        ctklabel1 = CTkLabel(framelabeledprimary5)
        ctklabel1.configure(text='ctk:')
        ctklabel1.grid(column=0, padx="0 5", row=0, sticky="e")
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
        ctkslider1.pack(side="top")
        ctklabel8 = CTkLabel(framelabeled1)
        ctklabel8.configure(text='subCTk:')
        ctklabel8.pack()
        slider1 = sCTkSlider(framelabeled1)
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
        framelabeledprimary2 = sCTkFrameLabeledPrimary(ctkframe1)
        framelabeledprimary2.configure(
            label_anchor="w", label_text="Segmented Button")
        ctklabel13 = CTkLabel(framelabeledprimary2)
        ctklabel13.configure(text='ctk:')
        ctklabel13.grid(column=0, row=0)
        ctksegmentedbutton1 = CTkSegmentedButton(framelabeledprimary2)
        ctksegmentedbutton1.configure(
            dynamic_resizing=False,
            values=[
                "apple",
                "blueberry",
                "orange",
                "pear"],
            width=300)
        ctksegmentedbutton1.grid(column=0, columnspan=3, row=1, sticky="ew")
        ctklabel14 = CTkLabel(framelabeledprimary2)
        ctklabel14.configure(text='subctk:')
        ctklabel14.grid(column=0, row=2)
        segmentedbutton1 = sCTkSegmentedButton(framelabeledprimary2)
        segmentedbutton1.configure(values=["VW", "Audi", "Porsche"])
        segmentedbutton1.grid(column=0, row=3)
        sctkscrollbar1 = sCTkScrollbar(framelabeledprimary2)
        sctkscrollbar1.grid(column=1, row=0, rowspan=6)
        framelabeledprimary2.grid(column=0, row=1)
        framelabeledprimary4 = sCTkFrameLabeledPrimary(ctkframe1)
        framelabeledprimary4.configure(
            border_color="#2370a2",
            label_anchor="w",
            label_text="textboxes secondary")
        tabview1 = sCTkTabview(framelabeledprimary4)
        ctktabviewtab1 = tabview1.add("HI")
        ctkframe2 = CTkFrame(ctktabviewtab1)
        ctkframe2.configure(
            bg_color="green",
            border_color="yellow",
            border_width=2)
        sctkbuttonsecondary1 = sCTkButtonSecondary(ctkframe2)
        sctkbuttonsecondary1.configure(text='sctkbuttonsecondary1')
        sctkbuttonsecondary1.pack(side="top")
        sctkbuttonsecondary2 = sCTkButtonSecondary(ctkframe2)
        sctkbuttonsecondary2.configure(text='sctkbuttonsecondary2')
        sctkbuttonsecondary2.pack(side="top")
        ctkframe2.pack(side="top")
        ctktabviewtab2 = tabview1.add("goodbye")
        ctkframe3 = CTkFrame(ctktabviewtab2)
        sctkcheckbox2 = sCTkCheckBox(ctkframe3)
        sctkcheckbox2.configure(text='sctkcheckbox2')
        sctkcheckbox2.pack(side="top")
        sctkcheckbox3 = sCTkCheckBox(ctkframe3)
        sctkcheckbox3.configure(text='sctkcheckbox3')
        sctkcheckbox3.pack(side="top")
        ctkframe3.pack(side="top")
        ctktabviewtab3 = tabview1.add("no more")
        ctkframe4 = CTkFrame(ctktabviewtab3)
        sctklabelprimary1 = sCTkLabelPrimary(ctkframe4)
        sctklabelprimary1.configure(text='sctklabelprimary1')
        sctklabelprimary1.pack(side="top")
        sctklabelprimary2 = sCTkLabelPrimary(ctkframe4)
        sctklabelprimary2.configure(text='sctklabelprimary2')
        sctklabelprimary2.pack(side="top")
        ctkframe4.pack(side="top")
        tabview1.pack(side="top")
        framelabeledprimary4.grid(column=1, row=1)
        framelabeledprimary3 = sCTkFrameLabeledPrimary(ctkframe1)
        framelabeledprimary3.configure(
            label_anchor="w",
            label_text="Outline Frame + OptionMenu")
        ctklabel15 = CTkLabel(framelabeledprimary3)
        ctklabel15.configure(text='ctk:')
        ctklabel15.grid(column=0, row=0, sticky="e")
        ctklabel18 = CTkLabel(framelabeledprimary3)
        ctklabel18.configure(text='subCTk:')
        ctklabel18.grid(column=0, pady="10 0", row=1)
        sctkoptionmenuprimary1 = sCTkOptionMenuPrimary(framelabeledprimary3)
        sctkoptionmenuprimary1.configure(values=["VW", "Audi", "Ford"])
        sctkoptionmenuprimary1.grid(column=1, pady="10 0", row=1)
        ctkoptionmenu1 = CTkOptionMenu(framelabeledprimary3)
        ctkoptionmenu1.configure(values=["VW", "Audi", "Ford"])
        ctkoptionmenu1.grid(column=1, row=0)
        ctklabel19 = CTkLabel(framelabeledprimary3)
        ctklabel19.configure(text='2ndCTk:')
        ctklabel19.grid(column=0, pady="10 0", row=2)
        sctkoptionmenusecondary1 = sCTkOptionMenuSecondary(
            framelabeledprimary3)
        sctkoptionmenusecondary1.configure(values=["VW", "Audi", "Ford"])
        sctkoptionmenusecondary1.grid(column=1, pady="10 0", row=2)
        sctkoptionmenusecondary2 = sCTkOptionMenuSecondary(
            framelabeledprimary3)
        sctkoptionmenusecondary2.configure(values=["VW", "Audi", "Ford"])
        sctkoptionmenusecondary2.grid(column=1, pady="10 0", row=3)
        framelabeledprimary3.grid(column=2, row=1)
        sctkframelabeledprimary1 = sCTkFrameLabeledPrimary(ctkframe1)
        sctkframelabeledprimary1.configure(
            label_anchor="w", label_text="Scrollbars")
        sctkscrollbar2 = sCTkScrollbar(sctkframelabeledprimary1)
        sctkscrollbar2.grid(column=1, row=0, rowspan=6, sticky="e")
        sctkscrollbar3 = sCTkScrollbar(
            sctkframelabeledprimary1,
            orientation="horizontal")
        sctkscrollbar3.grid(column=1, row=1, rowspan=6, sticky="s")
        sctkframelabeledprimary1.grid(column=0, row=2)
        self.testlabelframe = sCTkFrameLabeledPrimary(ctkframe1)
        self.testlabelframe.configure(label_text="Primary Textbox")
        sctktextboxprimary2 = sCTkTextboxPrimary(self.testlabelframe)
        sctktextboxprimary2.configure(wrap="none")
        _text_ = 'sctktextboxprimary2'
        sctktextboxprimary2.delete("0.0", "end")
        sctktextboxprimary2.insert("0.0", _text_)
        sctktextboxprimary2.pack(side="top")
        self.testlabelframe.grid(column=1, row=2)
        self.sctkframelabeledprimary3 = sCTkFrameLabeledPrimary(ctkframe1)
        self.sctkframelabeledprimary3.configure(
            label_text="Secondary Text Box")
        sctktextboxsecondary1 = sCTkTextboxSecondary(
            self.sctkframelabeledprimary3)
        sctktextboxsecondary1.configure(wrap="none")
        _text_ = 'sctktextboxsecondary1'
        sctktextboxsecondary1.delete("0.0", "end")
        sctktextboxsecondary1.insert("0.0", _text_)
        sctktextboxsecondary1.pack(side="top")
        self.sctkframelabeledprimary3.grid(column=2, row=2)
        ctkframe1.grid(column=0, row=0)

        # Main widget
        self.mainwindow = ctk1

    def run(self):
        self.mainwindow.mainloop()

    def callback(self, event=None):
        pass


if __name__ == "__main__":
    app = customCTK_WidgetTesterPart2UI()
    app.run()
