#!/usr/bin/python3
"""
sCTkButtonPrimary

sublass of CTkButton

UI source file: sCTkButtonPrimary.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkButton
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from scustomtkinter.sctk_button_primary import sCTkButtonPrimary

from pygubu.plugins.customtkinter.widgets import CTkButtonBO


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_button_primary"
widget_classname = "sCTkButtonPrimary"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkButtonPrimaryBO(CTkButtonBO):
    class_ = sCTkButtonPrimary

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkButtonPrimaryBO, widget_classname, ("ttk", section_name)
)


