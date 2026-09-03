#!/usr/bin/python3
"""
sCTkSegmentedButton

segmentedButton

UI source file: sCTkSegmentedButton.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkSegmentedButton
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.widgets import CTkSegmentedButtonBO
from pygubu.api.v1 import copy_custom_property

from scustomtkinter.sctk_segmentedbutton import sCTkSegmentedButton


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_segmentedbutton"
widget_classname = "sCTkSegmentedButton"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkSegmentedButtonBO(CTkSegmentedButtonBO):
    class_ = sCTkSegmentedButton

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkSegmentedButtonBO, widget_classname, ("ttk", section_name)
)

# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkSegmentedButton is the registered name for CTkSegmentedButtonBO builder.
# FIX: the try previously wrapped the WHOLE loop rather than each iteration,
# so the first property that failed to copy aborted the loop and every
# remaining property was silently skipped -- a partial copy that leaves the
# Designer inspector missing definitions with no indication why. The other
# builder-object modules in this package wrap each iteration individually,
# which is the correct shape.
#
# The bare `except:` is also narrowed to RuntimeError. A bare except here
# catches NameError too, which is exactly how a missing "s" in a builder-id
# variable went unnoticed in designer/properties.py.
for pname in CTkSegmentedButtonBO.properties:
    try:
        copy_custom_property(nsctk.CTkSegmentedButton, pname, builder_id)
    except RuntimeError:
        pass  # unconfigured property
