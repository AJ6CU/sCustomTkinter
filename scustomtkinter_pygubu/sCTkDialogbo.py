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
    OPTIONS_CUSTOM = ("title", "width", "height", "modal", "transient",
                      "offset_x", "offset_y", "heading", "heading_anchor",
                      "heading_font", "heading_color", "buttons",
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

    @staticmethod
    def _parse_font(value):
        """
        Converts Pygubu's font string into the tuple CustomTkinter expects.

        The `fontentry` editor produces a Tk font specification -- a family,
        optionally brace-wrapped when it contains spaces, then a size, then
        zero or more styles:

            {Comic Sans MS} 14 bold
            Arial 12

        CTkLabel accepts a tuple or a CTkFont, not that string, so it is parsed
        here rather than passed through.

        Returns:
            A (family, size) or (family, size, style) tuple, or None if the
            value is empty or unparseable -- in which case the theme's
            heading_font applies, which is the right fallback.
        """
        if not value:
            return None
        if isinstance(value, (tuple, list)):
            return tuple(value)

        text = str(value).strip()
        if not text:
            return None

        if text.startswith("{"):
            end = text.find("}")
            if end == -1:
                return None
            family = text[1:end]
            rest = text[end + 1:].split()
        else:
            parts = text.split()
            family, rest = parts[0], parts[1:]

        if not rest:
            return None
        try:
            size = int(rest[0])
        except (TypeError, ValueError):
            return None

        styles = " ".join(rest[1:]).strip()
        return (family, size, styles) if styles else (family, size)

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

        for flag in ("modal", "transient"):
            raw = props.get(flag)
            if raw not in (None, ""):
                args[flag] = str(raw).lower() in ("true", "1", "yes")

        for prop in ("heading", "heading_anchor"):
            value = props.get(prop)
            if value:
                args[prop] = str(value)

        font = self._parse_font(props.get("heading_font"))
        if font is not None:
            args["heading_font"] = font

        colour = props.get("heading_color")
        if colour:
            args["heading_color"] = str(colour)

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

    # The widget's own defaults. Clearing a field in the inspector must restore
    # these, not blank the button: an empty label looks like a broken widget,
    # and the generated code correctly falls back to them because the property
    # is simply omitted from the constructor call.
    _TEXT_DEFAULTS = {"apply_text": "Apply", "cancel_text": "Cancel",
                      "reset_text": "Reset", "heading": "Heading Title"}

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
            # FIX: an empty value used to blank the button. Clearing a field
            # means "use the default", which is what the generated code does --
            # the property is omitted and the constructor default applies. The
            # design view now agrees with it.
            text = value if value else self._TEXT_DEFAULTS[pname]
            # set_button_text() records the label as well as displaying it, so
            # it survives the rebuild that a `buttons` change triggers.
            target_widget.set_button_text(pname.split("_")[0], text)
            return None

        if pname == "heading_font":
            target_widget.set_heading_font(
                self._parse_font(value)
                or target_widget.final_kw.get("heading_font"))
            return None

        if pname == "heading_color":
            # Empty restores the theme's text_color, matching what the
            # generated code does: the property is omitted and the theme
            # applies.
            target_widget.set_heading_color(value or None)
            return None

        if pname == "buttons":
            # FIX: this used to rely on builder.recreate_widget(), which did
            # not reach us -- the canvas kept the old button count while the
            # preview and generated code showed the new one. The widget rebuilds
            # its own button row instead, which depends on nothing outside it.
            target_widget.set_buttons(value)
            return None

        if pname == "heading":
            target_widget.set_heading(
                heading=value if value else self._TEXT_DEFAULTS["heading"])
            return None

        if pname == "heading_anchor":
            target_widget.set_heading(anchor=value or "center")
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
        # The button commands are deliberately NOT intercepted here. Pygubu
        # emits command properties through its own code path, which this
        # override is not consulted for -- the earlier attempt to redirect them
        # produced generated code that still called
        # configure(apply_command=...) and raised ValueError at the widget.
        #
        # sCTkDialog.configure() now accepts them instead, so the ordinary
        # emission works and there is nothing to redirect.
        if pname in self.OPTIONS_CUSTOM:
            # Passed at construction by code_realize(); keeping them out of the
            # configure() call avoids setting the same thing twice.
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
    builder_id, "transient", "choice", values=("True", "False"),
    state="readonly",
    help="True ties the window to its parent -- above it, minimises with it, "
         "usually not in the taskbar. False gives an independent window."
)
register_custom_property(
    builder_id, "heading", "entry",
    help="Text shown above the content area. Clear to restore the default."
)
register_custom_property(
    builder_id, "heading_anchor", "choice",
    values=("center", "w", "e"), state="readonly",
    help="Heading alignment."
)
register_custom_property(
    builder_id, "heading_font", "fontentry",
    help="Heading font. Leave blank to use the theme's heading_font."
)
register_custom_property(
    builder_id, "heading_color", "colorentry",
    help="Heading colour. Leave blank to use the theme's text_color."
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
