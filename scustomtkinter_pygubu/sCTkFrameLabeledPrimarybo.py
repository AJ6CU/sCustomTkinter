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

from pygubu.plugins.customtkinter.scrollableframe import CTkScrollableFrameBO

from scustomtkinter.sctk_frame_labeled_primary import sCTkFrameLabeledPrimary


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_frame_labeled_primary"
widget_classname = "sCTkFrameLabeledPrimary"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


container = True
# CTkScrollableFrame does some weird things
# with layout so disabled container layout here on purpose.
container_layout = False


class sCTkFrameLabeledPrimaryBO(CTkScrollableFrameBO):
    class_ = sCTkFrameLabeledPrimary

    # state was never declared here, so the property did not reach the
    # inspector at all -- even though the widget implements it fully, with its
    # own state()/get_state() and a disabled_map that dims the border and the
    # label. sCTkScrollableFramebo declares it the same way.
    OPTIONS_CUSTOM = ("state",)
    properties = CTkScrollableFrameBO.properties + OPTIONS_CUSTOM

    OPTIONS_CUSTOM_DEFAULTS = {
        "state": "normal",
    }


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

register_custom_property(
    builder_id, "state", "choice", values=("normal", "disabled"),
    state="readonly", default_value="normal",
    help="Disabled dims the border and the label. The contents keep their own "
         "state -- disabling the frame does not disable what is inside it."
)
