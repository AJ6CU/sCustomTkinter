#!/usr/bin/python3
"""
sCTkSMeterBar

Pygubu Builder Object for a bar style s-meter, pwr and swr.
"""
import ast
import pygubu

from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)

# Import the native custom class
from sCTkSMeterBar import sCTkSMeterBar
from sCTkFrame import sCTkFrame

#
# Builder definition section
#
widget_namespace = "sCTkSMeterBar"
widget_classname = "sCTkSMeterBar"
builder_namespace = "custom_widgets"
section_name = "sCustomTkinter"


class sCTkSMeterBarBO(BuilderObject):
    class_ = sCTkSMeterBar

    # Expose custom compound parameters alongside theme state configurations
    OPTIONS_CUSTOM = ("width", "height", "swr_max_value", "swr_visible", "pwr_visible", "hide_lower_row")
    properties = OPTIONS_CUSTOM

    def _process_property_value(self, pname, value):
        if pname in ("width", "height"):
            return int(value)
        elif pname == "swr_max_value":
            return float(value)
        elif pname in ("swr_visible", "pwr_visible", "hide_lower_row"):
            if value == "True":
                return True
            else:
                return False

        return super()._process_property_value(pname, value)


# Register the widget into Pygubu's parsing engine
builder_id = f"{builder_namespace}.{widget_classname}"

register_widget(builder_id, sCTkSMeterBarBO, 'sCTkSMeterBar', ("ttk", section_name))



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
    builder_id,
    "swr_max_value",
    "realnumber",
    help="largest value for signal on scale"
)

register_custom_property(
    builder_id,
    "swr_visible",
    "choice",values=("True","False"),
    default_value="True",
    help="Controls the visability of the SWR meter"
)

register_custom_property(
    builder_id,
    "pwr_visible",
    "choice",values=("True","False"),
    default_value="True",
    help="Controls the visability of the SWR meter"
)


register_custom_property(
    builder_id,
    "hide_lower_row",
    "choice",values=("True","False"),
    default_value="False",
    help="Hides the PWR/SWR if True"
)

