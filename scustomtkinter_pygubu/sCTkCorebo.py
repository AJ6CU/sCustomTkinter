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

    def _set_property(self, target_widget, pname, value):
        """
        Applies a property, guarding the two global CustomTkinter settings
        against an empty value.

        Blanking a property in the Designer inspector makes pygubu call
        unset_property(), which resolves the property's default and passes it
        through. These two have no widget-level default to read back, so that
        value is None -- and CTkBO's own version hands it straight to
        ctk.set_appearance_mode(), which does mode_string.lower() and raises
        AttributeError on NoneType.

        The two are guarded DIFFERENTLY, on purpose.

        appearance_mode falls back to "System", which is a real state and
        CustomTkinter's own default: follow the OS. A user who tries Dark,
        then Light, then wants the system to decide again needs a route back.
        Ignoring the call would strand them on the last explicit mode, which
        is exactly what they are trying to escape. This package also registers
        "System" as an explicit choice, so it is reachable without clearing
        the field -- CustomTkinter's own property offers only blank, Light
        and Dark.

        color_theme has no equivalent unset state: CustomTkinter always needs
        some theme loaded, and reverting to "blue" would be a guess rather
        than a reversion. Blank is ignored, leaving the current theme alone.
        """
        if pname == "appearance_mode":
            return super()._set_property(target_widget, pname, value or "System")
        if pname == "color_theme" and not value:
            return None
        return super()._set_property(target_widget, pname, value)

    def _code_set_property(self, targetid, pname, value, code_bag):
        """
        Same guard, for generated code.

        CTkBO interpolates the value into a string literal:

            set_appearance_mode("{value}")

        so a blank one emits set_appearance_mode("None") or
        set_appearance_mode("") -- valid Python that raises in the user's
        application rather than in the Designer, which makes it harder to
        trace back here.
        """
        if pname == "appearance_mode":
            value = value or "System"
        elif pname == "color_theme" and not value:
            return None
        return super()._code_set_property(targetid, pname, value, code_bag)


builder_id = f"{builder_namespace}.{widget_classname}"

register_widget(
    builder_id, sCTkBO, widget_classname, ("ttk", section_name), group=GROOT
)
# register_custom_property(
#     builder_id, "appearance_mode", "choice",
#     values=("System", "Light", "Dark"),
#     state="readonly",
#     help="System follows the OS setting. This is CustomTkinter's own default."
# )

