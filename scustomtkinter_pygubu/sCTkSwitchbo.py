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

from pygubu.plugins.customtkinter.widgets import CTkSwitchBO
from scustomtkinter.sctk_switch import sCTkSwitch


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_switch"
widget_classname = "sCTkSwitch"
builder_namespace = "scustomtkinter"
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

