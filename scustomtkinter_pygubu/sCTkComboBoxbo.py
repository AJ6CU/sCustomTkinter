#!/usr/bin/python3
"""
sCTkComboBox

derived from comboBox

UI source file: sCTkComboBox.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkComboBox
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from pygubu.plugins.customtkinter.widgets import CTkComboBoxBO

from scustomtkinter.sctk_combobox import sCTkComboBox


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_combobox"
widget_classname = "sCTkComboBox"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkComboBoxBO(CTkComboBoxBO):
    class_ = sCTkComboBox

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkComboBoxBO, widget_classname, ("ttk", section_name)
)

