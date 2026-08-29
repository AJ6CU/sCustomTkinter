#!/usr/bin/python3
"""
sCTkSegmentedButton

segmentedButton

UI source file: sCTkSegmentedButton.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkSegmentedButton
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.widgets import CTkSegmentedButtonBO
from pygubu.api.v1 import copy_custom_property

from sCTkSegmentedButton import sCTkSegmentedButton


#
# Builder definition section
#
widget_namespace = "sCTkSegmentedButton"
widget_classname = "sCTkSegmentedButton"
builder_namespace = "custom_widgets"
section_name = "sCustomTkinter"


class sCTkSegmentedButtonBO(CTkSegmentedButtonBO):
    class_ = sCTkSegmentedButton

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkSegmentedButtonBO, widget_classname, ("ttk", section_name)
)

# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkSegmentedButton is the registered name for CTkSegmentedButtonBO builder.
try:
    for pname in CTkSegmentedButtonBO.properties:
        copy_custom_property(nsctk.CTkSegmentedButton, pname, builder_id)
except:
    pass
