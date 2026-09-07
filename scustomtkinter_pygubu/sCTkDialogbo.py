#!/usr/bin/python3
"""
sCTkDialog

A consistent popup dialog: heading, content area, action button row.

NOTE there is deliberately no builder object for sCTkDialogToplevel. That
class is created BY sCTkDialog and is never placed by a user, so
registering it would only offer something that cannot sensibly be dropped
anywhere. The class remains; its Designer registration does not.
"""
import tkinter as tk
import tkinter.ttk as ttk

from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property,
)

from scustomtkinter.sctk_dialog import sCTkDialog


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_dialog"
widget_classname = "sCTkDialog"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkDialogBO(BuilderObject):
    class_ = sCTkDialog
    container = True

    # Window properties. All are keyword-only constructor arguments on the
    # widget, not configure() options, so realize() and code_realize() below
    # pass them at construction rather than leaving BuilderObject to apply
    # them afterwards.
    OPTIONS_CUSTOM = ("title", "width", "height", "modal",
                      "offset_x", "offset_y")
    properties = OPTIONS_CUSTOM

    def get_child_master(self):
        """
        Children go into the content area, not into the dialog frame itself.

        This is what makes the dialog pleasant to lay out: drop widgets onto
        it in the Designer and they land between the heading and the button
        row, where they belong.
        """
        return self.widget.contentFrame

    def code_child_master(self):
        return f"{self.code_identifier()}.contentFrame"

    def _dialog_init_args(self):
        """
        Collects the window properties from the widget metadata, converted to
        the types the constructor expects.

        Omitted properties are left out entirely rather than passed as None,
        so the widget's own defaults apply.
        """
        props = getattr(getattr(self, "wmeta", None), "properties", {}) or {}
        args = {}

        title = props.get("title")
        if title:
            args["title"] = str(title)

        for name in ("width", "height", "offset_x", "offset_y"):
            raw = props.get(name)
            if raw not in (None, ""):
                try:
                    args[name] = int(raw)
                except (TypeError, ValueError):
                    pass

        modal = props.get("modal")
        if modal not in (None, ""):
            args["modal"] = str(modal).lower() in ("true", "1", "yes")

        return args

    def realize(self, parent, extra_init_args: dict = None):
        """Builds the dialog, passing the window properties at construction."""
        init_args = self._dialog_init_args()
        if extra_init_args:
            init_args.update(extra_init_args)
        master = parent.get_child_master() if hasattr(parent, "get_child_master") else parent
        self.widget = self.class_(master, **init_args)
        return self.widget

    def code_realize(self, boparent, code_identifier=None):
        """Emits the construction line with the window properties inline."""
        if code_identifier is not None:
            self._code_identifier = code_identifier
        master = boparent.code_child_master()
        args = self._dialog_init_args()

        bag = [f"{master}"]
        for name, value in args.items():
            bag.append(f"{name}={value!r}")

        return [f"{self.code_identifier()} = {self._code_class_name()}({', '.join(bag)})"]

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkDialogBO, widget_classname, ("ttk", section_name)
)

register_custom_property(
    builder_id, "title", "entry",
    help="Window title bar text."
)
register_custom_property(
    builder_id, "width", "naturalnumber",
    help="Window width in pixels. Leave blank to size to content."
)
register_custom_property(
    builder_id, "height", "naturalnumber",
    help="Window height in pixels. Leave blank to size to content."
)
register_custom_property(
    builder_id, "modal", "choice", values=("False", "True"), state="readonly",
    help="True blocks interaction with the rest of the application while the "
         "dialog is open. Call run_and_wait() instead to also block the "
         "calling code until it closes."
)
register_custom_property(
    builder_id, "offset_x", "integernumber",
    help="Pixels right of the parent window's top-left corner. Default 40."
)
register_custom_property(
    builder_id, "offset_y", "integernumber",
    help="Pixels below the parent window's top-left corner. Default 40."
)
