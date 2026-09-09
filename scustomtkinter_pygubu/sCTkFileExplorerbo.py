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
from scustomtkinter.sctk_file_explorer import sCTkFileExplorer
from pygubu.plugins.customtkinter.widgets import CTkFrameBO

# Builder UI placement definitions
widget_namespace = "scustomtkinter.sctk_file_explorer"
widget_classname = "sCTkFileExplorer"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkFileExplorerBO(BuilderObject):
    class_ = sCTkFileExplorer

    # Define custom plugin properties (Note: 'title' has been completely removed)
    OPTIONS_CUSTOM = (
        "width", "height", "type", "initialdir", "initialfile",
        "filetypes", "state", "command", "double_click_command",
        "selection_color"
    )

    # Merge custom extensions cleanly on top of core container frame attributes
    properties = CTkFrameBO.properties + OPTIONS_CUSTOM
    command_properties = ("command", "double_click_command")

    def _process_property_value(self, pname, value):
        """Passes values directly to allow core widget validations to handle exceptions."""
        return super()._process_property_value(pname, value)

    # `type` and `filetypes` constrain each other, so setting one writes the
    # other back into the widget metadata.
    #
    # The widget already enforces the rule -- setting filetypes switches to
    # file mode, and choosing directory clears the filter -- but it does that
    # to ITSELF. The Designer keeps its own copy in wmeta, so the inspector
    # went on showing the old value: adding a filter left `type` reading blank
    # while the widget had switched to "file", and choosing "directory"
    # afterwards collided with a filter the inspector still believed was set.
    #
    # Generated code reads wmeta, so leaving it stale would also have written
    # out a combination the widget then had to correct at runtime.
    def set_property(self, name, value):
        if hasattr(self, "wmeta") and hasattr(self.wmeta, "properties"):
            props = self.wmeta.properties
            props[name] = value
            if name == "filetypes" and value:
                props["type"] = "file"
            elif name == "type" and str(value).lower() == "directory":
                props["filetypes"] = ""

        if getattr(self, "widget", None) is not None:
            self._set_property(self.widget, name, value)


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
    help='Filter by file extension. Preferred: [".py", ".txt"]. Bare comma-separated (.py, .txt) also works, but cannot contain a comma inside a value.'
)

register_custom_property(
    builder_id,
    "state",
    "choice",
    values=("", "normal", "disabled"),
    state="readonly",
    help="Set widget active visibility or input interaction lockdown state"
)

register_custom_property(
    builder_id, "selection_color", "colorentry",
    help="Colour of the highlighted row. Blank uses the theme's "
         "selection_color. Separate from btn_fg, which colours the navigation "
         "buttons -- changing one does not affect the other."
)
