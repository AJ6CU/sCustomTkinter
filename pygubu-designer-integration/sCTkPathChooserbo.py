#!/usr/bin/python3
"""
sCTkPathChooser

Pygubu Builder Object for the compound sCTkPathChooser entry widget row.
"""
import ast
import pygubu

from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)

# Import the native custom class
from sCTkPathChooser import sCTkPathChooser

#
# Builder definition section
#
widget_namespace = "sCTkPathChooser"
widget_classname = "sCTkPathChooser"
builder_namespace = "custom_widgets"
section_name = "sCustomTkinter"


class sCTkPathChooserBO(BuilderObject):
    class_ = sCTkPathChooser

    # Expose custom compound parameters alongside theme state configurations
    OPTIONS_CUSTOM = ("width", "height", "type", "title", "initialdir", "initialfile", "filetypes", "state", "command", "btn_width", "btn_height", "btn_text", "entry_height", "browser_width", "browser_height", "justify")
    properties = OPTIONS_CUSTOM

    command_properties = ("command",)

    def _process_property_value(self, pname, value):
        """Passes values directly to allow core widget validations to handle exceptions."""
        return super()._process_property_value(pname, value)


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
    help="Select file or directory selection mode"
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
    help="Filter by file extension - formats list array format: ['.py', '.txt']"
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
