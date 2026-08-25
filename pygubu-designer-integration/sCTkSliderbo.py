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

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.widgets import CTkSliderBO
from pygubu.api.v1 import copy_custom_property

from sCTkSlider import sCTkSlider


#
# Builder definition section
#
widget_namespace = "sCTkSlider"
widget_classname = "sCTkSlider"
builder_namespace = "custom_widgets"
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

# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkSlider is the registered name for CTkSliderBO builder.
for pname in CTkSliderBO.properties:
    copy_custom_property(nsctk.CTkSlider, pname, builder_id)