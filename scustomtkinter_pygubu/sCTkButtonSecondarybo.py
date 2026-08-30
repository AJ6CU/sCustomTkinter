#!/usr/bin/python3
"""
buttonSecondary

secondary ctk button

UI source file: sCTkButtonSecondary.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkButton
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from scustomtkinter.sctk_button_secondary import sCTkButtonSecondary
from pygubu.plugins.customtkinter.widgets import CTkButtonBO


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_button_secondary"
widget_classname = "sCTkButtonSecondary"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkButtonSecondaryBO(CTkButtonBO):
    class_ = sCTkButtonSecondary

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkButtonSecondaryBO, widget_classname, ("ttk", section_name)
)

