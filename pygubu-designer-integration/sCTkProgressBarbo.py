#!/usr/bin/python3
"""
sCTkProgressBar.

derived from progressBar

UI source file: sCTkProgressBar.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkProgressBar
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.widgets import CTkProgressBarBO
from pygubu.api.v1 import copy_custom_property

from sCTkProgressBar import sCTkProgressBar


#
# Builder definition section
#
widget_namespace = "sCTkProgressBar"
widget_classname = "sCTkProgressBar"
builder_namespace = "custom_widgets"
section_name = "sCustomTkinter"


class sCTkProgressBarBO(CTkProgressBarBO):
    class_ = sCTkProgressBar

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkProgressBarBO, widget_classname, ("ttk", section_name)
)

# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkProgressBar is the registered name for CTkProgressBarBO builder.
for pname in CTkProgressBarBO.properties:
    copy_custom_property(nsctk.CTkProgressBar, pname, builder_id)