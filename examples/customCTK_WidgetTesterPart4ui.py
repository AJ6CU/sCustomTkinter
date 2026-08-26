#!/usr/bin/python3
"""
customCTK_WidgetTesterPart4

just tests each widget

UI source file: customCTK_WidgetTesterPart4.ui
"""
from customtkinter import (CTk, CTkFrame)
from sCTkDial import (sCTkDialContinuous, sCTkDialRange, sCTkDialSelector)
from sCTkFileExplorer import sCTkFileExplorer
from sCTkFrame import sCTkFrame
from sCTkPathChooser import sCTkPathChooser
from sCTkSMeter import sCTkSMeter
from sCTkSMeterBar import sCTkSMeterBar
from sCTkSegmentedButton import sCTkSegmentedButton
from sCTkSpinbox import sCTkSpinbox
from sCTkTableview import sCTkTableview


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


class customCTK_WidgetTesterPart4UI:
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
        sctkframe5 = sCTkFrame(ctkframe1)
        sctktableview1 = sCTkTableview(sctkframe5)
        sctktableview1.configure(
            columns="AJ6CU, Frequency, Mode, Power, Station",
            grid_mode="zebra",
            header_line_width=4,
            num_columns=3,
            num_rows=8,
            show_headers=True,
            state="normal")
        sctktableview1.pack(side="top")
        sctkframe5.grid(column=0, row=0)
        sctkframe6 = sCTkFrame(ctkframe1)
        sctkframe6.configure(bg_color="green")
        sctksmeterbar1 = sCTkSMeterBar(sctkframe6)
        sctksmeterbar1.pack(side="top")
        sctkframe6.grid(column=1, row=0)
        sctkframe1 = sCTkFrame(ctkframe1)
        sctksmeter1 = sCTkSMeter(sctkframe1)
        sctksmeter1.pack(side="top")
        sctkframe1.grid(column=2, row=0)
        sctkframe2 = sCTkFrame(ctkframe1)
        sctkdialcontinuous2 = sCTkDialContinuous(sctkframe2)
        sctkdialcontinuous2.configure(diameter=150)
        sctkdialcontinuous2.pack(side="top")
        sctkdialcontinuous2.configure(left_click_callback=self.leftClick_CB)
        sctkdialcontinuous2.configure(right_click_callback=self.rightClick_CB)
        sctkframe2.grid(column=0, row=1)
        sctkframe3 = sCTkFrame(ctkframe1)
        sctkdialselector1 = sCTkDialSelector(sctkframe3)
        sctkdialselector1.configure(diameter=150)
        sctkdialselector1.pack(side="top")
        sctkdialselector1.configure(command=self.selector_CB)
        sctkframe3.grid(column=1, row=1)
        sctkframe4 = sCTkFrame(ctkframe1)
        sctkdialrange1 = sCTkDialRange(sctkframe4)
        sctkdialrange1.configure(arc_angle=180, diameter=150)
        sctkdialrange1.pack(side="top")
        sctkdialrange1.configure(command=self.pot)
        sctkframe4.grid(column=2, row=1)
        ctkframe1.grid(column=0, columnspan=3, row=0, sticky="ew")
        sctkframe7 = sCTkFrame(ctk1)
        sctkspinbox1 = sCTkSpinbox(sctkframe7)
        sctkspinbox1.configure(
            arrow_font_size=42,
            button_side="split",
            format="%0.4f",
            from_=1,
            justify="right",
            orientation="horizontal",
            placeholder_text="Click Me",
            state="normal",
            step_size=10,
            to=100)
        sctkspinbox1.pack(side="top")
        sctkspinbox1.configure(command=self.callme)
        sctksegmentedbutton1 = sCTkSegmentedButton(sctkframe7)
        sctksegmentedbutton1.configure(values=["one", "two", "three"])
        sctksegmentedbutton1.pack(side="top")
        sctkpathchooser1 = sCTkPathChooser(sctkframe7)
        sctkpathchooser1.configure(
            filetypes="['.py']",
            initialdir="~",
            justify="left",
            title='pick me',
            type="directory")
        sctkpathchooser1.pack(side="top")
        sctkpathchooser1.configure(command=self.pathCommand)
        sctkframe7.grid(column=0, row=1)
        sctkframe8 = sCTkFrame(ctk1)
        sctkfileexplorer1 = sCTkFileExplorer(sctkframe8)
        sctkfileexplorer1.configure(initialdir="~", type="directory")
        sctkfileexplorer1.pack(side="top")
        sctkfileexplorer1.configure(command=self.explorerSingle)
        sctkfileexplorer1.configure(double_click_command=self.explorerDouble)
        sctkframe8.grid(column=1, row=1)

        # Main widget
        self.mainwindow = ctk1

    def run(self):
        self.mainwindow.mainloop()

    def leftClick_CB(self):
        pass

    def rightClick_CB(self):
        pass

    def selector_CB(self):
        pass

    def pot(self):
        pass

    def callme(self):
        pass

    def pathCommand(self):
        pass

    def explorerSingle(self):
        pass

    def explorerDouble(self):
        pass


if __name__ == "__main__":
    app = customCTK_WidgetTesterPart4UI()
    app.run()
