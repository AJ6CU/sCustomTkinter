#!/usr/bin/python3
"""
sCTkDialogToplevel

the top level for a sCTkDialogToplevel

UI source file: sCTkDialogToplevel.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkToplevel
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from sCTkDialogToplevel import sCTkDialogToplevel


#
# Builder definition section
#
widget_namespace = "sCTkDialogToplevel"
widget_classname = "sCTkDialogToplevel"
builder_namespace = "custom_widgets"
section_name = "Project Widgets"


class sCTkDialogToplevelBO(BuilderObject):
    class_ = sCTkDialogToplevel

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkDialogToplevelBO, widget_classname, ("ttk", section_name)
)
