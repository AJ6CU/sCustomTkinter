#!/usr/bin/python3
"""
sCTkLabelTertiary

3rd level Label used for notes

UI source file: sCTkLabelTertiary.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkLabel
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.widgets import CTkLabelBO
from pygubu.api.v1 import copy_custom_property

from sCTkLabelTertiary import sCTkLabelTertiary


#
# Builder definition section
#
widget_namespace = "sCTkLabelTertiary"
widget_classname = "sCTkLabelTertiary"
builder_namespace = "custom_widgets"
section_name = "sCustomTkinter"


class sCTkLabelTertiaryBO(CTkLabelBO):
    class_ = sCTkLabelTertiary

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkLabelTertiaryBO, widget_classname, ("ttk", section_name)
)

# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkLabel is the registered name for CTkLabelBO builder.
for pname in CTkLabelBO.properties:
    copy_custom_property(nsctk.CTkLabel, pname, builder_id)
