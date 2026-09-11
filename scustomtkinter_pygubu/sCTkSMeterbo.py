#!/usr/bin/python3
"""
sCTkSMeter.py

Pygubu Builder Object for a S Meter.
"""
import ast
import pygubu

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
    OPTIONS_CUSTOM = ("width", "height", "fg_color", "font", "scale_font")

    # NOT CTkFrameBO.properties.
    #
    # Folding them in was tried and taken back out. The meter draws on a canvas
    # that covers the whole widget, so the frame underneath is never visible:
    # border_color, border_width and corner_radius appeared in the inspector
    # and did nothing at all. A property that cannot work is worse than an
    # absent one.
    #
    # fg_color IS listed, because the widget paints the canvas with it -- see
    # sCTkSMeter.configure(). It was reaching only one of the two meters
    # before, inherited from somewhere rather than declared, so the pair
    # disagreed about a property they both support.
    #
    # corner_radius is the real loss: rounding the meter would mean rounding
    # the canvas, which Tk cannot do to a canvas widget. It would have to be
    # drawn -- a rounded rectangle filling the canvas in the parent's colour,
    # masking the corners. Possible, not free.
    properties = OPTIONS_CUSTOM

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

register_custom_property(
    builder_id, "fg_color", "colorentry",
    help="Background the meter is drawn on. This paints the CANVAS, not the frame behind it -- the canvas covers the whole widget. Blank uses the theme's fg_color."
)