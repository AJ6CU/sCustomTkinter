#!/usr/bin/python3
"""
sCTkPathChooser

Pygubu Builder Object for the compound sCTkPathChooser entry widget row.
"""
import pygubu

from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)

# Import the native custom class
from scustomtkinter.sctk_path_chooser import sCTkPathChooser
from pygubu.plugins.customtkinter.widgets import CTkFrameBO

#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_path_chooser"
widget_classname = "sCTkPathChooser"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkPathChooserBO(BuilderObject):
    class_ = sCTkPathChooser

    # Expose custom compound parameters alongside theme state configurations
    OPTIONS_CUSTOM = ("width", "height", "type", "title", "initialdir", "initialfile", "filetypes", "state", "command", "btn_width", "btn_height", "btn_text", "entry_height", "browser_width", "browser_height", "justify")
    properties = CTkFrameBO.properties + OPTIONS_CUSTOM

    command_properties = ("command",)

    def _process_property_value(self, pname, value):
        """Passes values directly to allow core widget validations to handle exceptions."""
        return super()._process_property_value(pname, value)

    def _code_define_callback_args(self, cmd_pname, cmd):
        """
        Declares what the callback receives, so the generated stub has a
        matching parameter.

        Without this, pygubu generates a stub taking no arguments and the
        widget calls it with the chosen path:

            TypeError: on_path() takes 1 positional argument but 2 were given
        """
        return ("selected_path",)

    def _code_set_property(self, targetid, pname, value, code_bag):
        """
        Emits `filetypes` as a real Python list, not a quoted string.

        The bracketed form contains double quotes, and the default handler
        wraps the whole value in double quotes again:

            sctkpathchooser1.configure(filetypes="[".py"]", ...)
                                                 ^^^^^^^^^
            SyntaxError: invalid syntax

        Emitting the literal unquoted gives valid Python and a real list. A
        bare comma-separated value has no brackets and no quotes, so it is
        emitted as a quoted string and parsed by the widget as usual.
        """
        if pname == "filetypes" and value:
            text = str(value).strip()
            if text.startswith("[") and text.endswith("]"):
                code_bag[pname] = text
                return None
        return super()._code_set_property(targetid, pname, value, code_bag)


# Register the widget into Pygubu's parsing engine
builder_id = f"{builder_namespace}.{widget_classname}"

register_widget(builder_id, sCTkPathChooserBO, 'sCTkPathChooser', ("ttk", section_name))


# Map the 'command' option directly to Pygubu's native callback editor panel
register_custom_property(
    builder_id,
    "command",
    "commandentry",
    help="Method callback string triggered on path confirmation"
)


# Register custom attribute fields to display inside the Designer properties panel

register_custom_property(
    builder_id,
    "width",
    "naturalnumber",
    help="Set total width in pixels of file entry and button. File path width = width - button width"
)

register_custom_property(
    builder_id,
    "height",
    "naturalnumber",
    help="Set height in pixels allocated to file path and button frame. Button and file path height set separately."
)

register_custom_property(
    builder_id,
    "type",
    "choice",
    values=("", "file", "directory"),
    state="readonly",
    default_value="directory",
    help="What the chooser selects. The widget's own default is 'directory'; "
         "filetypes only applies when this is 'file'."
)

register_custom_property(
    builder_id,
    "justify",
    "choice",
    values=("", "left", "right", "center"),
    state="readonly",
    help="Align long path strings to prioritize viewing starting roots or trailing filenames"
)

register_custom_property(
    builder_id,
    "title",
    "entry",
    help="Window header title string text"
)

register_custom_property(
    builder_id,
    "initialdir",
    "entry",
    help="Starting directory path location string"
)

register_custom_property(
    builder_id,
    "initialfile",
    "entry",
    help="Starting target highlight file path string"
)

register_custom_property(
    builder_id,
    "filetypes",
    "entry",
    help='Filter by file extension. Preferred: [".py", ".txt"]. Bare comma-separated (.py, .txt) also works, but cannot contain a comma inside a value.'
)

register_custom_property(
    builder_id,
    "entry_height",
    "naturalnumber",
    help="Set height in pixels of the file path field widget"
)

register_custom_property(
    builder_id,
    "btn_width",
    "naturalnumber",
    help="Set width in pixels of the button"
)

register_custom_property(
    builder_id,
    "btn_height",
    "naturalnumber",
    help="Set height in pixels of the button"
)

register_custom_property(
    builder_id,
    "btn_text",
    "entry",
    help="Override default button text (e.g. 'Select', '▶' or '>')"
)

register_custom_property(
    builder_id,
    "browser_width",
    "naturalnumber",
    help="Set width of the pop-up file browser window in pixels"
)

register_custom_property(
    builder_id,
    "browser_height",
    "naturalnumber",
    help="Set height of the pop-up file browser window in pixels"
)

register_custom_property(
    builder_id,
    "state",
    "choice",
    values=("", "normal", "disabled"),
    state="readonly",
    help="Set widget interaction state"
)
