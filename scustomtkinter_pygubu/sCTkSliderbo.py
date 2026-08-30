#!/usr/bin/python3
"""
sCTkSlider

derived from slider

UI source file: sCTkSlider.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkSlider
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter.widgets import CTkSliderBO
from scustomtkinter.sctk_slider import sCTkSlider


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_slider"
widget_classname = "sCTkSlider"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkSliderBO(CTkSliderBO):
    class_ = sCTkSlider

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkSliderBO, widget_classname, ("ttk", section_name)
)

