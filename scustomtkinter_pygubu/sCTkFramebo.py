#!/usr/bin/python3
"""
sCTkFrame

subclass of Frame tuned for this ux

UI source file: sCTkFrame.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkFrame
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.widgets import CTkFrameBO
from pygubu.api.v1 import copy_custom_property

from scustomtkinter.sctk_frame import sCTkFrame


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_frame"
widget_classname = "sCTkFrame"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkFrameBO(CTkFrameBO):
    class_ = sCTkFrame

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkFrameBO, widget_classname, ("ttk", section_name)
)
