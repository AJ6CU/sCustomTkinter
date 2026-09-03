#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkOptionMenu
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter.widgets import CTkOptionMenuBO
from scustomtkinter.sctk_optionmenu_secondary import sCTkOptionMenuSecondary


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_optionmenu_secondary"
widget_classname = "sCTkOptionMenuSecondary"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkOptionMenuSecondaryBO(CTkOptionMenuBO):
    class_ = sCTkOptionMenuSecondary

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkOptionMenuSecondaryBO, widget_classname, ("ttk", section_name)
)

