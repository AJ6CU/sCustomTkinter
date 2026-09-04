#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk

from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.windows import CTkBO
from pygubu.api.v1 import copy_custom_property

from scustomtkinter.sctk_core import sCTk
from pygubu.plugins.customtkinter._config import GROOT


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_core"
widget_classname = "sCTk"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkBO(CTkBO):
    class_ = sCTk
    container = True

    def code_imports(self):
        """
        Imports needed by generated code for this widget.

        FIX: this previously returned only the sCTk import, dropping the
        conditional part of CTkBO.code_imports(). CTkBO adds
        set_appearance_mode and set_default_color_theme when those properties
        are set, because _code_set_property() generates bare calls to them:

            set_appearance_mode("dark")

        Without the matching import, setting appearance_mode or color_theme in
        the Designer produced a generated file that raised NameError the
        moment it ran. Those two functions come from customtkinter itself, not
        from this library, so they are imported from there.
        """
        imports = [(widget_namespace, widget_classname)]
        if "appearance_mode" in self.wmeta.properties:
            imports.append(("customtkinter", "set_appearance_mode"))
        if "color_theme" in self.wmeta.properties:
            imports.append(("customtkinter", "set_default_color_theme"))
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"

register_widget(
    builder_id, sCTkBO, widget_classname, ("ttk", section_name), group=GROOT
)

