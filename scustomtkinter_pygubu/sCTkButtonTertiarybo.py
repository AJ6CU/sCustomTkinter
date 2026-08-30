#!/usr/bin/python3
"""
sCTkButtonTertiary

ghost ctk button

UI source file: sCTkButtonTertiary.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkButton
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from scustomtkinter.sctk_button_tertiary import sCTkButtonTertiary
from pygubu.plugins.customtkinter.widgets import CTkButtonBO


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_button_tertiary"
widget_classname = "sCTkButtonTertiary"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkButtonTertiaryBO(CTkButtonBO):
    class_ = sCTkButtonTertiary

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkButtonTertiaryBO, widget_classname, ("ttk", section_name)
)

