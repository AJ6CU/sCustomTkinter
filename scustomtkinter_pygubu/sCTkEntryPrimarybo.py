#!/usr/bin/python3
"""
sCTkEntryPrimary

Customized ctk Entry field. - Primary version

UI source file: sCTkEntryPrimary.ui
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

from scustomtkinter.sctk_entry_primary import sCTkEntryPrimary


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_entry_primary"
widget_classname = "sCTkEntryPrimary"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkEntryPrimaryBO(CTkEntryBO):
    class_ = sCTkEntryPrimary

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkEntryPrimaryBO, widget_classname, ("ttk", section_name)
)

