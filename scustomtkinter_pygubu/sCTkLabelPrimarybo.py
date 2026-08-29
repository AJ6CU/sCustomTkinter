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

from sCTkLabelPrimary import sCTkLabelPrimary

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.widgets import CTkLabelBO
from pygubu.api.v1 import copy_custom_property


#
# Builder definition section
#
widget_namespace = "sCTkLabelPrimary"
widget_classname = "sCTkLabelPrimary"
builder_namespace = "custom_widgets"
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

# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkLabel is the registered name for CTkLabelBO builder.
for pname in CTkLabelBO.properties:
    copy_custom_property(nsctk.CTkLabel, pname, builder_id)
