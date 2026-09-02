#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkFrame
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.windows import CTkBO
from pygubu.api.v1 import copy_custom_property

from scustomtkinter.sctk_core import sCTk


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_core"
widget_classname = "sCTk"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkBO(CTkBO):
    class_ = sCTk

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkBO, widget_classname, ("ttk", section_name)
)

