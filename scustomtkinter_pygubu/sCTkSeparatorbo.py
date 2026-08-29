#!/usr/bin/python3
"""
sCTkSeparatorBuilder

Pygubu Builder Object for the custom themeable sCTkSeparator widget line.
Inherits from CTkCanvasBO to secure flawless layout and parenting geometry management.
"""
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)
from pygubu.plugins.customtkinter.widgets import CTkCanvasBO
from sCTkThemes import THEME_DEFAULTS

# Import the native custom class
from sCTkSeparator import sCTkSeparator

widget_namespace = "sCTkSeparator"
widget_classname = "sCTkSeparator"
builder_namespace = "sCTkSeparator"
section_name = "sCustomTkinter"


class sCTkSeparatorBuilder(CTkCanvasBO):
    class_ = sCTkSeparator

    OPTIONS_CUSTOM = ("length", "width", "corner_radius", "orientation", "text", "dash")
    properties = OPTIONS_CUSTOM
    code_properties = OPTIONS_CUSTOM

    def _get_init_args(self, extra_init_args: dict = None):
        """Force orientation to be processed first during initialization maps."""
        args = super()._get_init_args(extra_init_args)
        ordered_args = {
            "orientation": args.get("orientation", "vertical") or "vertical",
            "length": args.get("length"),
            "width": args.get("width"),
            "corner_radius": args.get("corner_radius"),
            "text": args.get("text", ""),
            "dash": args.get("dash", None)
        }
        for k, v in args.items():
            if k not in ordered_args:
                ordered_args[k] = v
        return ordered_args

    def realize(self, parent, extra_init_args: dict = None):
        """Constructs our custom class safely using extracted parameter inputs."""
        args = self._get_init_args(extra_init_args)

        length = int(args.get("length")) if args.get("length") else 100
        width = int(args.get("width")) if args.get("width") else 4

        default_radius = THEME_DEFAULTS.get("sCTkSeparator", {}).get("corner_radius", 6)
        corner_radius = int(args.get("corner_radius")) if args.get("corner_radius") else default_radius

        orientation = args.get("orientation")
        text = args.get("text", "")

        dash_val = args.get("dash", None)
        dash = None
        if dash_val and str(dash_val).strip().lower() != "none":
            dash = tuple(
                int(x.strip()) for x in str(dash_val).replace("(", "").replace(")", "").split(",") if x.strip())

        self.widget = sCTkSeparator(
            master=parent.widget,
            length=length,
            width=width,
            corner_radius=corner_radius,
            orientation=orientation,
            text=text,
            dash=dash
        )
        return self.widget

    def _set_property(self, target, pname, value):
        """Captures live setting adjustments directly from Pygubu UI panel modifications."""
        if pname in self.OPTIONS_CUSTOM:
            if hasattr(self, "widget") and self.widget:
                if value == "" or value is None:
                    if pname == "width":
                        fallback = 4
                    elif pname == "length":
                        fallback = 100
                    elif pname == "corner_radius":
                        fallback = THEME_DEFAULTS.get("sCTkSeparator", {}).get("corner_radius", 6)
                    elif pname == "text":
                        fallback = ""
                    elif pname == "dash":
                        fallback = None
                    else:
                        fallback = "vertical"
                    self.widget.configure(**{pname: fallback}, require_redraw=True)
                else:
                    if pname in ("length", "width", "corner_radius"):
                        self.widget.configure(**{pname: int(value)}, require_redraw=True)
                    else:
                        self.widget.configure(**{pname: value}, require_redraw=True)
        else:
            super()._set_property(target, pname, value)

    def _process_property_value(self, pname, value):
        if pname in ("length", "width", "corner_radius"):
            if value:
                try:
                    return int(value)
                except ValueError:
                    return None
        return super()._process_property_value(pname, value)

    def code_imports(self):
        return [(widget_namespace, widget_classname)]

    def _code_set_properties(self, targetid, code_creator):
        super()._code_set_properties(targetid, code_creator)
        for pname in self.OPTIONS_CUSTOM:
            val = self.wproperties.get(pname, None)
            if val is not None and val != "":
                if pname in ("orientation", "text"):
                    code_creator.add_configure_line(targetid, pname, f"'{val}'")
                elif pname == "dash":
                    code_creator.add_configure_line(targetid, pname, str(val))
                else:
                    code_creator.add_configure_line(targetid, pname, str(val))


# Register the widget into Pygubu's parsing engine
builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(builder_id, sCTkSeparatorBuilder, 'sCTkSeparator', ("ttk", section_name))

# Register properties
# Register properties panel layout help labels
register_custom_property(builder_id, "length", "naturalnumber", help="Set total span length of the separator line in pixels")
register_custom_property(builder_id, "width", "naturalnumber", help="Set visual thickness profile width of the separator line in pixels")
register_custom_property(builder_id, "corner_radius", "naturalnumber", help="Define roundness sharpness limit token value for divider tips")
register_custom_property(builder_id, "orientation", "choice", values=("vertical", "horizontal"), help="Select spatial directional positioning alignment")
register_custom_property(builder_id, "text", "entry", help="Add centered section header string text directly inside the line track split")
register_custom_property(builder_id, "dash", "entry", help="Enter integer dash sequence mapping tuple format (e.g. 5,5 or 2,8)")

