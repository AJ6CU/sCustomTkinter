#!/usr/bin/python3
"""
sCTkFrameLabeledPrimary

Similer to ttk.labelframe built on ctkscrollableframe with scrollbars hidden

UI source file: sCTkFrameLabeledPrimary.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkScrollableFrame
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.scrollableframe import CTkScrollableFrameBO
from pygubu.api.v1 import copy_custom_property

from sCTkFrameLabeledPrimary import sCTkFrameLabeledPrimary


#
# Builder definition section
#
widget_namespace = "sCTkFrameLabeledPrimary"
widget_classname = "sCTkFrameLabeledPrimary"
builder_namespace = "custom_widgets"
section_name = "sCustomTkinter"


container = True
# CTkScrollableFrame does some weird things
# with layout so disabled container layout here on purpose.
container_layout = False


class sCTkFrameLabeledPrimaryBO(CTkScrollableFrameBO):
    class_ = sCTkFrameLabeledPrimary


    def code_imports(self):
            # should return an iterable of (module, classname/function) to import
            # or None
            imports = [(widget_namespace, widget_classname)]
            imports.extend(self.code_extra_imports())
            return imports

builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkFrameLabeledPrimaryBO, widget_classname, ("ttk", section_name)
)

# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkScrollableFrame is the registered name for CTkScrollableFrameBO builder.
for pname in CTkScrollableFrameBO.properties:
    try:
        copy_custom_property(nsctk.CTkScrollableFrame, pname, builder_id)
    except:
        pass
