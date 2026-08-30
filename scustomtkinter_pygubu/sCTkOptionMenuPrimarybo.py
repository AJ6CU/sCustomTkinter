#!/usr/bin/python3
"""
sCTkOptionMenuPrimary

Tailored version of the standard ctkOptionMenu

UI source file: sCTkOptionMenuPrimary.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkOptionMenu
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter.widgets import CTkOptionMenuBO
from scustomtkinter.sctk_optionmenu_primary import sCTkOptionMenuPrimary


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_optionmenu_primary"
widget_classname = "sCTkOptionMenuPrimary"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkOptionMenuPrimaryBO(CTkOptionMenuBO):
    class_ = sCTkOptionMenuPrimary

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkOptionMenuPrimaryBO, widget_classname, ("ttk", section_name)
)

