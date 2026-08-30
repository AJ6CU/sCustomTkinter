#!/usr/bin/python3
"""
sCTkLabelPrimary

The primary label used for headers etc.

UI source file: sCTkLabelPrimary.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkLabel
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from scustomtkinter.sctk_label_primary import sCTkLabelPrimary
from pygubu.plugins.customtkinter.widgets import CTkLabelBO


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_label_primary"
widget_classname = "sCTkLabelPrimary"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkLabelPrimaryBO(CTkLabelBO):
    class_ = sCTkLabelPrimary

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkLabelPrimaryBO, widget_classname, ("ttk", section_name)
)

