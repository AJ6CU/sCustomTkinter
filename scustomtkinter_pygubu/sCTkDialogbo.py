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
                      "offset_x", "offset_y", "buttons",
                      "apply_text", "cancel_text", "reset_text")
    properties = OPTIONS_CUSTOM + ("apply_command", "cancel_command",
                                   "reset_command")

    # Declared so pygubu routes these through its callback handling rather
    # than stringifying the property metadata into the generated code.
    command_properties = ("apply_command", "cancel_command", "reset_command")

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

        buttons = props.get("buttons")
        if buttons not in (None, ""):
            try:
                args["buttons"] = int(buttons)
            except (TypeError, ValueError):
                pass

        for prop, arg in (("apply_text", "apply_text"),
                          ("cancel_text", "cancel_text"),
                          ("reset_text", "reset_text")):
            value = props.get(prop)
            if value:
                args[arg] = str(value)

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

    def _set_property(self, target_widget, pname, value):
        """
        Routes the button command properties to the widget's own setters.

        These are not configure() options -- sCTkDialog exposes them as
        constructor arguments and through set_apply_button() and friends -- so
        without this they would reach sCTkFrame.configure() and raise.

        A command aimed at a button this dialog does not have is ignored
        rather than raising: reducing `buttons` while a command is still set
        on a removed button is an ordinary thing to do in the inspector.
        """
        command_targets = {
            "apply_command": "set_apply_button",
            "cancel_command": "set_cancel_button",
            "reset_command": "set_reset_button",
        }
        if pname in command_targets:
            if value:
                getattr(target_widget, command_targets[pname])(
                    button_command=value)
            return None
        if pname in self.OPTIONS_CUSTOM:
            # Applied at construction by realize(); nothing to do here.
            return None
        return super()._set_property(target_widget, pname, value)

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
register_custom_property(
    builder_id, "buttons", "choice", values=("3", "2", "1"), state="readonly",
    help="3 = Apply, Cancel, Reset. 2 = Apply, Cancel. 1 = Apply only. "
         "Apply is always present."
)
register_custom_property(
    builder_id, "apply_text", "entry", help="Apply button label. Default 'Apply'."
)
register_custom_property(
    builder_id, "cancel_text", "entry",
    help="Cancel button label. Default 'Cancel'. Ignored when buttons is 1."
)
register_custom_property(
    builder_id, "reset_text", "entry",
    help="Reset button label. Default 'Reset'. Ignored unless buttons is 3."
)
register_custom_property(
    builder_id, "apply_command", "commandentry", help="Called when Apply is clicked."
)
register_custom_property(
    builder_id, "cancel_command", "commandentry",
    help="Called when Cancel is clicked. Ignored when buttons is 1."
)
register_custom_property(
    builder_id, "reset_command", "commandentry",
    help="Called when Reset is clicked. Ignored unless buttons is 3."
)
