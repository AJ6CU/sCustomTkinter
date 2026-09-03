#!/usr/bin/python3
"""
sCTkScrollableFrame

subclass of ScrollableFrame tuned for this ux

UI source file: sCTkScrollableFrame.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkScrollableFrame
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.scrollableframe import CTkScrollableFrameBO
from pygubu.api.v1 import copy_custom_property

from scustomtkinter.sctk_scrollable_frame import sCTkScrollableFrame


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_scrollable_frame"
widget_classname = "sCTkScrollableFrame"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"

container = True
# CTkScrollableFrame does some weird things
# with layout so disabled container layout here on purpose.
container_layout = False


class sCTkScrollableFrameBO(CTkScrollableFrameBO):
    class_ = sCTkScrollableFrame

    OPTIONS_CUSTOM = ('state',)
    properties = CTkScrollableFrameBO.properties + OPTIONS_CUSTOM

    OPTIONS_CUSTOM_DEFAULTS = {
        'state': 'normal'
    }

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports

builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkScrollableFrameBO, widget_classname, ("ttk", section_name)
)


# -----------------------------------------------------------------
# EXPOSE CUSTOM 'STATE' CHANNELS INSIDE PYGUBU DESIGNER PANEL
# -----------------------------------------------------------------
# 1. Define the UI element type mapping definitions
register_custom_property(builder_id,"state", "choice", values=("normal", "disabled"))
