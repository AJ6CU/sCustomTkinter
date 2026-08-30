#!/usr/bin/python3
"""
sCTkCheckBox

derived from CTkCheckBox

UI source file: sCTkCheckBox.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkCheckBox
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter.widgets import CTkCheckBoxBO

from scustomtkinter.sctk_checkbox import sCTkCheckBox


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_checkbox"
widget_classname = "sCTkCheckBox"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkCheckBoxBO(CTkCheckBoxBO):
    class_ = sCTkCheckBox
    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkCheckBoxBO, widget_classname, ("ttk", section_name)
)

