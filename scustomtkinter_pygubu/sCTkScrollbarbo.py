#!/usr/bin/python3
"""
sCTkScrollbar

scrollbar

UI source file: sCTkScrollbar.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkScrollbar
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.widgets import CTkScrollbarBO
from pygubu.api.v1 import copy_custom_property

from sCTkScrollbar import sCTkScrollbar


#
# Builder definition section
#
widget_namespace = "sCTkScrollbar"
widget_classname = "sCTkScrollbar"
builder_namespace = "custom_widgets"
section_name = "sCustomTkinter"


class sCTkScrollbarBO(CTkScrollbarBO):
    class_ = sCTkScrollbar

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkScrollbarBO, widget_classname, ("ttk", section_name)
)

# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkScrollbar is the registered name for CTkScrollbarBO builder.
for pname in CTkScrollbarBO.properties:
    copy_custom_property(nsctk.CTkScrollbar, pname, builder_id)