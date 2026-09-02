#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk

from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.windows import CTkToplevelBO
from pygubu.api.v1 import copy_custom_property

from scustomtkinter.sctk_toplevel import sCTkToplevel


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_toplevel"
widget_classname = "sCTkTopLevel"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkToplevelBO(CTkToplevelBO):
    class_ = sCTkToplevel
    container = True

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkToplevelBO, widget_classname, ("ttk", section_name)
)

