#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkButton
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from .sctk_button_primary import sCTkButtonPrimary

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.widgets import CTkButtonBO
from pygubu.api.v1 import copy_custom_property


#
# Builder definition section
#
widget_namespace = "scustomtkinter"
widget_classname = "sCTkButtonPrimary"
builder_namespace = "custom_widgets"
section_name = "sCustomTkinter"


class sCTkButtonPrimaryBO(CTkButtonBO):
    class_ = sCTkButtonPrimary

    def code_imports(self):
        # HARDCODE your installed package directory here for Pygubu's code exporter!
        # This forces the generated code to use your library, even though
        # Pygubu itself is loading this file locally.
        imports = [(widget_namespace, widget_classname)]
        return imports



builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkButtonPrimaryBO, widget_classname, ("ttk", section_name)
)

# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkButton is the registered name for CTkButtonBO builder.
for pname in CTkButtonBO.properties:
    copy_custom_property(nsctk.CTkButton, pname, builder_id)
