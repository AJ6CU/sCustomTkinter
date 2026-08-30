#!/usr/bin/python3
"""
sCTkFrameOutlined

Standard CTk form but with an outline border

UI source file: sCTkFrameOutlined.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkFrame
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)

from pygubu.plugins.customtkinter.widgets import CTkFrameBO
from scustomtkinter.sctk_frame_outlined import sCTkFrameOutlined


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_frame_outlined"
widget_classname = "sCTkFrameOutlined"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkFrameOutlinedBO(CTkFrameBO):
    class_ = sCTkFrameOutlined

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkFrameOutlinedBO, widget_classname, ("ttk", section_name)
)

