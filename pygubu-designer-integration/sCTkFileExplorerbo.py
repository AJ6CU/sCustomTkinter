#!/usr/bin/python3
"""
sCTkFileExplorerbo

Pygubu Builder Object for the compound FileExplorer entry that is used by pathchooser.
"""
import pygubu
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)

# Import the native custom class
from sCTkFileExplorer import sCTkFileExplorer

# Builder UI placement definitions
widget_namespace = "sCTkFileExplorer"
widget_classname = "sCTkFileExplorer"
builder_namespace = "custom_widgets"
section_name = "sCustomTkinter"


class sCTkFileExplorerBO(BuilderObject):
    class_ = sCTkFileExplorer

    # Define custom plugin properties (Note: 'title' has been completely removed)
    OPTIONS_CUSTOM = (
        "width", "height", "type", "initialdir", "initialfile",
        "filetypes", "state", "command", "double_click_command"
    )

    # Merge custom extensions cleanly on top of core container frame attributes
    properties = BuilderObject.properties + OPTIONS_CUSTOM
    command_properties = ("command", "double_click_command")

    def _process_property_value(self, pname, value):
        """Passes values directly to allow core widget validations to handle exceptions."""
        return super()._process_property_value(pname, value)


# Register the widget into Pygubu's layout parsing engine
builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(builder_id, sCTkFileExplorerBO, 'sCTkFileExplorer', ("ttk", section_name))

# =========================================================================
# Custom Property Designer Registration Maps
# =========================================================================

register_custom_property(
    builder_id,
    "command",
    "commandentry",
    help="Method callback string triggered on single-click file item highlight"
)

register_custom_property(
    builder_id,
    "double_click_command",
    "commandentry",
    help="Method callback string triggered on double-click selection"
)

register_custom_property(
    builder_id,
    "width",
    "naturalnumber",
    help="Total horizontal pixel constraint footprint assigned to the layout canvas wrapper"
)

register_custom_property(
    builder_id,
    "height",
    "naturalnumber",
    help="Total vertical pixel constraint footprint assigned to the layout canvas wrapper"
)

register_custom_property(
    builder_id,
    "type",
    "choice",
    values=("", "file", "directory"),
    state="readonly",
    help="Select file or directory structural filtering operation mode"
)

register_custom_property(
    builder_id,
    "initialdir",
    "entry",
    help="Default starting directory path location string"
)

register_custom_property(
    builder_id,
    "initialfile",
    "entry",
    help="Default starting highlight focus target file path string"
)

register_custom_property(
    builder_id,
    "filetypes",
    "entry",
    help="Filter by file extension lists. Format explicitly as a bracketed array: ['.py', '.txt']"
)

register_custom_property(
    builder_id,
    "state",
    "choice",
    values=("", "normal", "disabled"),
    state="readonly",
    help="Set widget active visibility or input interaction lockdown state"
)
