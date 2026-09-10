#!/usr/bin/python3
"""
checkBoxTest

checkBoxTest

UI source file: checkBoxTest.ui
"""
from scustomtkinter.sctk_button_primary import sCTkButtonPrimary
from scustomtkinter.sctk_button_secondary import sCTkButtonSecondary
from scustomtkinter.sctk_button_tertiary import sCTkButtonTertiary
from scustomtkinter.sctk_checkbox import sCTkCheckBox
from scustomtkinter.sctk_combobox import sCTkComboBox
from scustomtkinter.sctk_core import sCTk
from scustomtkinter.sctk_label_primary import sCTkLabelPrimary
from scustomtkinter.sctk_label_secondary import sCTkLabelSecondary
from scustomtkinter.sctk_label_tertiary import sCTkLabelTertiary


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


class checkBoxTestUI:
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

        sctkbuttonprimary1 = sCTkButtonPrimary(sctk1)
        sctkbuttonprimary1.configure(
            state="disabled",
            text='sctkbuttonprimary1',
            text_color_disabled="red")
        sctkbuttonprimary1.pack(side="top")
        sctkbuttonprimary2 = sCTkButtonPrimary(sctk1)
        sctkbuttonprimary2.configure(state="normal", text='sctkbuttonprimary2')
        sctkbuttonprimary2.pack(side="top")
        sctkbuttonsecondary1 = sCTkButtonSecondary(sctk1)
        sctkbuttonsecondary1.configure(
            state="disabled",
            text='sctkbuttonsecondary1',
            text_color_disabled="red")
        sctkbuttonsecondary1.pack(side="top")
        sctkbuttonsecondary2 = sCTkButtonSecondary(sctk1)
        sctkbuttonsecondary2.configure(text='sctkbuttonsecondary2')
        sctkbuttonsecondary2.pack(side="top")
        sctkbuttontertiary1 = sCTkButtonTertiary(sctk1)
        sctkbuttontertiary1.configure(
            state="disabled",
            text='sctkbuttontertiary1',
            text_color_disabled="red")
        sctkbuttontertiary1.pack(side="top")
        sctkbuttontertiary2 = sCTkButtonTertiary(sctk1)
        sctkbuttontertiary2.configure(text='sctkbuttontertiary2')
        sctkbuttontertiary2.pack(side="top")
        sctkcheckbox1 = sCTkCheckBox(sctk1)
        sctkcheckbox1.configure(
            fg_color="red",
            state="normal",
            text='sctkcheckbox1')
        sctkcheckbox1.pack(side="top")
        sctkcombobox1 = sCTkComboBox(sctk1)
        sctkcombobox1.configure(
            dropdown_text_color="yellow",
            fg_color="purple",
            state="normal",
            values=[
                "vw",
                "240z"])
        sctkcombobox1.pack(side="top")
        sctkcombobox2 = sCTkComboBox(sctk1)
        sctkcombobox2.configure(values=["VW", "240z"])
        sctkcombobox2.pack(side="top")
        sctklabelprimary1 = sCTkLabelPrimary(sctk1)
        sctklabelprimary1.configure(state="disabled", text='sctklabelprimary1')
        sctklabelprimary1.pack(side="top")
        sctklabelprimary2 = sCTkLabelPrimary(sctk1)
        sctklabelprimary2.configure(state="normal", text='sctklabelprimary2')
        sctklabelprimary2.pack(side="top")
        sctklabelsecondary1 = sCTkLabelSecondary(sctk1)
        sctklabelsecondary1.configure(
            state="disabled", text='sctklabelsecondary1')
        sctklabelsecondary1.pack(side="top")
        sctklabelsecondary2 = sCTkLabelSecondary(sctk1)
        sctklabelsecondary2.configure(text='sctklabelsecondary2')
        sctklabelsecondary2.pack(side="top")
        sctklabeltertiary1 = sCTkLabelTertiary(sctk1)
        sctklabeltertiary1.configure(
            state="disabled", text='sctklabeltertiary1')
        sctklabeltertiary1.pack(side="top")
        sctklabeltertiary2 = sCTkLabelTertiary(sctk1)
        sctklabeltertiary2.configure(text='sctklabeltertiary2')
        sctklabeltertiary2.pack(side="top")

        # Main widget
        self.mainwindow = sctk1

    def run(self):
        self.mainwindow.mainloop()


if __name__ == "__main__":
    app = checkBoxTestUI()
    app.run()
