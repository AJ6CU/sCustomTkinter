#!/usr/bin/python3
"""
sCTkTextboxSecondary

based on ctktextbox

UI source file: sCTkTextboxSecondary.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkTextbox
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter.widgets import CTkTextboxBO
from scustomtkinter.sctk_textbox_secondary import sCTkTextboxSecondary


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_textbox_secondary"
widget_classname = "sCTkTextboxSecondary"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkTextboxSecondaryBO(CTkTextboxBO):
    class_ = sCTkTextboxSecondary

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkTextboxSecondaryBO, widget_classname, ("ttk", section_name)
)

