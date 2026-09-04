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

    # --- Workarounds for CTkEntryBO, both reported upstream -----------------
    #
    # 1. invalidcommand is REMOVED from the inspector. CTkEntry does not accept
    #    it -- the name is absent from the widget's own attribute whitelist, so
    #    configure() raises:
    #
    #        ['invalidcommand'] are not supported arguments.
    #
    #    CTkEntryBO offers it anyway. Since sCTkEntry{Primary,Secondary} pass
    #    keywords straight through to native CTkEntry, the property could never
    #    work at any layer. Better not to offer it than to offer a field that
    #    errors when used.
    #
    #    Subtracted from the inherited tuple rather than restated, so any
    #    property CustomTkinter adds later is picked up automatically.
    properties = tuple(p for p in CTkEntryBO.properties if p != "invalidcommand")

    # 2. validatecommand and xscrollcommand ARE accepted by CTkEntry, but
    #    CTkEntryBO never declares them as command properties -- so pygubu does
    #    not route them through its callback handling and instead stringifies
    #    the raw property metadata into the generated code:
    #
    #        validatecommand="{"name": "validatecommand", "type": "command", ...}"
    #
    #    Note the unescaped inner quotes: that is not merely wrong, it is a
    #    syntax error, and the whole generated module fails to import.
    #
    #    invalidcommand is deliberately NOT listed here even though it is a
    #    command property, because the widget rejects it -- see above.
    command_properties = tuple(getattr(CTkEntryBO, "command_properties", ())) + (
        "validatecommand",
        "xscrollcommand",
    )

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

