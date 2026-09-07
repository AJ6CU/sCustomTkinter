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

    # Property name -> the widget setter that applies a button command.
    _COMMAND_TARGETS = {
        "apply_command": "set_apply_button",
        "cancel_command": "set_cancel_button",
        "reset_command": "set_reset_button",
    }

    # Properties that can be applied to a LIVE widget. Everything else in
    # OPTIONS_CUSTOM affects the window or the set of buttons, and can only be
    # honoured by rebuilding -- the Designer does that on its own when the
    # design is redrawn.
    _LIVE_TEXT = {"apply_text": "applyText_VAR",
                  "cancel_text": "cancelText_VAR",
                  "reset_text": "resetText_VAR"}

    def _set_property(self, target_widget, pname, value):
        """
        Applies a property to the live preview.

        None of this widget's own properties are configure() options --
        sCTkDialog takes them as constructor arguments -- so letting any of
        them reach sCTkFrame.configure() would raise. They are handled here or
        deliberately ignored.

        Button labels ARE applied live, by setting the StringVar the button
        reads. Without this, editing a label in the inspector changed nothing
        on the canvas until the design was redrawn for some other reason.
        """
        if pname in self._LIVE_TEXT:
            var = getattr(target_widget, self._LIVE_TEXT[pname], None)
            if var is not None:
                var.set(value if value else "")
            return None

        if pname == "title":
            target_widget.set_title(value or "")
            return None

        if pname in self._COMMAND_TARGETS:
            # A command aimed at a button this dialog does not have is ignored
            # rather than raising: reducing `buttons` while a command is still
            # set on a removed button is an ordinary inspector edit.
            if value:
                getattr(target_widget, self._COMMAND_TARGETS[pname])(
                    button_command=value)
            return None

        if pname in self.OPTIONS_CUSTOM:
            # Window size, placement, modality and the button count are all
            # construction-time. realize() passes them; nothing to do here.
            return None

        return super()._set_property(target_widget, pname, value)

    def _code_set_property(self, targetid, pname, value, code_bag):
        """
        Keeps this widget's own properties OUT of the generated configure()
        call.

        FIX: without this they were emitted as configure() arguments --

            sctkdialog1.configure(apply_text=""Apply it"", buttons=3, ...)

        which is wrong twice over. The doubled quotes are a syntax error, and
        even correctly quoted the call would raise at runtime, because
        sCTkFrame.configure() does not accept these names. They belong in the
        constructor, and code_realize() already puts them there.

        The button commands are emitted as their own statements instead, since
        they are applied through setter methods rather than configure().
        """
        if pname in self._COMMAND_TARGETS:
            if value:
                method = self._COMMAND_TARGETS[pname]
                code_bag[pname] = (
                    f"{targetid}.{method}(button_command={value})",
                )
            return None

        if pname in self.OPTIONS_CUSTOM:
            return None

        return super()._code_set_property(targetid, pname, value, code_bag)

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
