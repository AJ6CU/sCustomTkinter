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

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.widgets import CTkFrameBO
from pygubu.api.v1 import copy_custom_property

from sCTkFrameOutlined import sCTkFrameOutlined


#
# Builder definition section
#
widget_namespace = "sCTkFrameOutlined"
widget_classname = "sCTkFrameOutlined"
builder_namespace = "custom_widgets"
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

# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkFrame is the registered name for CTkFrameBO builder.
for pname in CTkFrameBO.properties:
    copy_custom_property(nsctk.CTkFrame, pname, builder_id)
