#!/usr/bin/python3
"""
sCTkSMeter.py

Pygubu Builder Object for a S Meter.
"""
import ast
import pygubu

from pygubu.plugins.customtkinter.widgets import CTkFrameBO

from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)

# Import the native custom class
from scustomtkinter.themeable_widget import parse_font_property
from scustomtkinter.sctk_smeter import sCTkSMeter


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_smeter"
widget_classname = "sCTkSMeter"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkSMeterBO(BuilderObject):
    class_ = sCTkSMeter

    # Expose custom compound parameters alongside theme state configurations
    OPTIONS_CUSTOM = ("width", "height", "font", "scale_font")

    # CTkFrameBO's properties are folded in, so the frame AROUND the meter
    # can be styled from the inspector -- fg_color, border_color,
    # border_width, corner_radius. Without them this widget offered only its
    # own four properties and nothing else, unlike every other widget in the
    # library.
    #
    # The meter's OWN colours stay theme-only: there are a dozen of them and
    # they are tuned as a set, so exposing them individually invites a change
    # that reads as broken rather than different. Same call as the dial's
    # shading keys.
    properties = CTkFrameBO.properties + OPTIONS_CUSTOM

    def _process_property_value(self, pname, value):
        if pname in ("font", "scale_font"):
            # Shared parser: Pygubu's fontentry emits a Tk font STRING, and
            # "{}" for "no style selected" -- passed through, that reaches a
            # canvas item as TclError: unknown font style "".
            return parse_font_property(value)
        if pname in ("width", "height"):
            return int(value)
        return super()._process_property_value(pname, value)


# Register the widget into Pygubu's parsing engine
builder_id = f"{builder_namespace}.{widget_classname}"

register_widget(builder_id, sCTkSMeterBO, 'sCTkSMeter', ("ttk", section_name))



# Register custom attribute fields to display inside the Designer properties panel

register_custom_property(
    builder_id,
    "width",
    "naturalnumber",
    help="Set total width in pixels of the meter"
)

register_custom_property(
    builder_id,
    "height",
    "naturalnumber",
    help="Set height in pixels of the meter"
)

register_custom_property(
    builder_id, "font", "fontentry",
    help='Font for the captions -- SIGNAL, SIG, SWR and PWR. Blank uses the theme font.'
)
register_custom_property(
    builder_id, "scale_font", "fontentry",
    help='Font for the scale tick labels. Blank uses the theme scale_font. Larger values can overlap on a narrow meter.'
)
