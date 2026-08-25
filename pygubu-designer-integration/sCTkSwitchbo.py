#!/usr/bin/python3
"""
sCTKSwitch

derived from ctk switch

UI source file: sCTkSwitch.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkSwitch
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.widgets import CTkSwitchBO
from pygubu.api.v1 import copy_custom_property

from sCTkSwitch import sCTkSwitch


#
# Builder definition section
#
widget_namespace = "sCTkSwitch"
widget_classname = "sCTkSwitch"
builder_namespace = "custom_widgets"
section_name = "sCustomTkinter"


class sCTkSwitchBO(CTkSwitchBO):
    class_ = sCTkSwitch

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkSwitchBO, widget_classname, ("ttk", section_name)
)

# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkSwitch is the registered name for CTkSwitchBO builder.
for pname in CTkSwitchBO.properties:
    copy_custom_property(nsctk.CTkSwitch, pname, builder_id)