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

    def _code_define_callback_args(self, cmd_pname, cmd):
        """
        Declares what each callback receives, so the generated stub has
        matching parameters.

        FIX: without this, pygubu generated a stub with no arguments --

            def single_cb(self):
                pass

        -- and the widget called it with the selected path:

            TypeError: single_cb() takes 1 positional argument but 2 were given

        The two callbacks differ. `command` receives the path alone;
        `double_click_command` receives the WIDGET and the path, which is how
        sCTkPathChooser drives it (it reads args[-1] to get the path).
        """
        if cmd_pname == "double_click_command":
            return ("explorer", "selected_path")
        return ("selected_path",)

    def _code_set_property(self, targetid, pname, value, code_bag):
        """
        Emits `filetypes` as a real Python list, not a quoted string.

        FIX: the bracketed form contains double quotes, and the default
        handler wraps the whole value in double quotes again:

            sctkfileexplorer1.configure(filetypes="[".py"]", ...)
                                                  ^^^^^^^^^
            SyntaxError: invalid syntax

        Emitting the literal unquoted gives valid Python and a real list, so
        the widget receives one directly rather than parsing a string back
        out of it. Same approach sCTkSelectorbo uses for `items`.

        A bare comma-separated value -- the other accepted form -- has no
        brackets and no quotes, so it is emitted as a quoted string and parsed
        by the widget as usual.
        """
        if pname == "filetypes" and value:
            text = str(value).strip()
            if text.startswith("[") and text.endswith("]"):
                code_bag[pname] = text
                return None
        return super()._code_set_property(targetid, pname, value, code_bag)

    # NOTE: `type` and `filetypes` constrain each other in the WIDGET, but the
    # inspector does not follow.
    #
    # Setting filetypes switches the widget to file mode, and choosing
    # directory clears the filter -- see sCTkFileExplorer. The widget applies
    # that to itself, and generated code is correct either way, because the
    # widget corrects the combination at construction.
    #
    # The Designer keeps its own copy of the properties, so the inspector goes
    # on showing the old value: adding a filter leaves `type` reading blank
    # while the widget has switched to file mode. A set_property() override
    # writing the companion value back into wmeta was tried and does not
    # reach the live tree node, so it has been removed rather than left as
    # dead code implying a behaviour that does not happen.


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
    default_value="directory",
    help="What the explorer selects. The widget's own default is 'directory'; "
         "setting filetypes switches it to 'file'."
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