#!/usr/bin/python3
"""
sCTkFrameLabeledSecondary

Similer to ttk.labelframe built on ctkscrollableframe with scrollbars hidden

UI source file: sCTkFrameLabeledSecondary.ui
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

from scustomtkinter.sctk_frame_labeled_secondary import sCTkFrameLabeledSecondary


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_frame_labeled_secondary"
widget_classname = "sCTkFrameLabeledSecondary"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"

container = True
# CTkScrollableFrame does some weird things
# with layout so disabled container layout here on purpose.
container_layout = False


class sCTkFrameLabeledSecondaryBO(CTkScrollableFrameBO):
    class_ = sCTkFrameLabeledSecondary

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
    builder_id, sCTkFrameLabeledSecondaryBO, widget_classname, ("ttk", section_name)
)

register_custom_property(
    builder_id, "state", "choice", values=("normal", "disabled"),
    state="readonly", default_value="normal",
    help="Disabled dims the border and the label. The contents keep their own "
         "state -- disabling the frame does not disable what is inside it."
)
