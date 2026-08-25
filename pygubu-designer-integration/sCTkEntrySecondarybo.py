#!/usr/bin/python3
"""
sCTkEntrySecondary

Customized ctk Entry field. - Secondary version

UI source file: sCTkEntrySecondary.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkEntry
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.widgets import CTkEntryBO
from pygubu.api.v1 import copy_custom_property

from sCTkEntrySecondary import sCTkEntrySecondary


#
# Builder definition section
#
widget_namespace = "sCTkEntrySecondary"
widget_classname = "sCTkEntrySecondary"
builder_namespace = "custom_widgets"
section_name = "sCustomTkinter"


class sCTkEntrySecondaryBO(CTkEntryBO):
    class_ = sCTkEntrySecondary

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkEntrySecondaryBO, widget_classname, ("ttk", section_name)
)

# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkEntry is the registered name for CTkEntryBO builder.
for pname in CTkEntryBO.properties:
    copy_custom_property(nsctk.CTkEntry, pname, builder_id)