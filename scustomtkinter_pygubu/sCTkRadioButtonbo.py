#!/usr/bin/python3
"""
sCTkRadioButton

derived from radioButton

UI source file: sCTkRadioButton.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkRadioButton
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter.widgets import CTkRadioButtonBO
from scustomtkinter.sctk_radiobutton import sCTkRadioButton


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_radiobutton"
widget_classname = "sCTkRadioButton"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkRadioButtonBO(CTkRadioButtonBO):
    class_ = sCTkRadioButton

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkRadioButtonBO, widget_classname, ("ttk", section_name)
)

