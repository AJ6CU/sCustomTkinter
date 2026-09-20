#!/usr/bin/python3
"""
sCTkFrequencyDisplay

Pygubu builder object for the grouped numeric readout.
"""
from pygubu.api.v1 import (
    register_widget,
    register_custom_property,
)
from pygubu.plugins.customtkinter.widgets import CTkFrameBO

from scustomtkinter.sctk_frequency_display import sCTkFrequencyDisplay

widget_namespace = "scustomtkinter.sctk_frequency_display"
widget_classname = "sCTkFrequencyDisplay"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkFrequencyDisplayBO(CTkFrameBO):
    class_ = sCTkFrequencyDisplay

    OPTIONS_CUSTOM = (
        "digits", "signed", "value", "delimiter", "font_size",
        "selectable", "min_digit", "state",
    )
    properties = CTkFrameBO.properties + OPTIONS_CUSTOM
    command_properties = ("command",)

    OPTIONS_CUSTOM_DEFAULTS = {
        "digits": "10",
        "signed": "False",
        "value": "0",
        "delimiter": ".",
        "font_size": "34",
        "selectable": "True",
        "min_digit": "1",
        "state": "normal",
    }

    container = False

    def realize(self, parent, extra_init_args: dict = None):
        """
        Builds the readout with its properties as constructor arguments.

        digits and signed change the LAYOUT, so they have to arrive as real
        values rather than being set afterwards -- a readout that builds at
        ten digits and shrinks to four flickers through the wrong size on
        every Designer repaint.
        """
        if extra_init_args is None:
            extra_init_args = {}

        props = self.wmeta.properties
        init_args = {
            "digits": int(props.get("digits", 10) or 10),
            "signed": self._as_bool(props.get("signed", "False")),
            "value": int(props.get("value", 0) or 0),
            "delimiter": props.get("delimiter", "."),
            "font_size": int(props.get("font_size", 34) or 34),
            "selectable": self._as_bool(props.get("selectable", "True")),
            "min_digit": int(props.get("min_digit", 1) or 0),
            "state": props.get("state", "normal"),
        }

        for prop in self.OPTIONS_CUSTOM:
            extra_init_args.pop(prop, None)
        init_args.update(extra_init_args)

        real_master = parent.widget if hasattr(parent, "widget") else parent
        self.widget = self.class_(real_master, **init_args)
        return self.widget

    @staticmethod
    def _as_bool(value):
        """bool("False") is True, and the Designer sends strings."""
        if isinstance(value, str):
            return value.strip().lower() in ("true", "1", "yes", "on")
        return bool(value)

    def _process_property_value(self, pname, value):
        if pname in ("digits", "value", "font_size", "min_digit"):
            return int(value)
        if pname in ("signed", "selectable"):
            return self._as_bool(value)
        return super()._process_property_value(pname, value)

    def _code_set_property(self, targetid, pname, value, code_bag):
        """Numbers and booleans emit as tokens; the rest keep their quotes."""
        if pname in ("digits", "value", "font_size", "min_digit",
                     "signed", "selectable"):
            code_bag[pname] = str(value).strip("'\"")
        elif pname in ("delimiter", "state"):
            code_bag[pname] = f"'{str(value).strip(chr(39) + chr(34))}'"
        else:
            super()._code_set_property(targetid, pname, value, code_bag)

    def _code_define_callback_args(self, cmd_pname, cmd):
        """
        Declares that `command` receives the step, so the generated stub has
        a matching parameter.

        Without this a user writing a handler has no indication that the
        selected digit's place value is being handed to them -- which is the
        entire point of the callback.
        """
        return ("step",)

    def code_imports(self):
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(builder_id, sCTkFrequencyDisplayBO, widget_classname,
                ("ttk", section_name))


# ---------------------------------------------------------------------------
# Inspector properties
# ---------------------------------------------------------------------------
register_custom_property(
    builder_id, "digits", "naturalnumber", default_value="10",
    help="How many digit positions. Ten reaches into the GHz as "
         "x.xxx.xxx.xxx; four suits a signed offset. Leading groups are "
         "hidden until they hold something, and the layout does not move "
         "when one appears.")

register_custom_property(
    builder_id, "signed", "choice", values=("True", "False"),
    state="readonly", default_value="False",
    help="Shows a leading + or -, for an offset rather than a frequency. "
         "The sign is always drawn, even when the leading digits are not.")

register_custom_property(
    builder_id, "value", "entry", default_value="0",
    help="The value shown, as an integer -- Hz for a frequency.")

register_custom_property(
    builder_id, "delimiter", "entry", default_value=".",
    help="What separates the groups of three. Changeable at any time, "
         "because it is a display preference the whole interface shares.")

register_custom_property(
    builder_id, "font_size", "naturalnumber", default_value="34",
    help="Point size of the digits. The FAMILY comes from the theme and "
         "should stay fixed-width -- a proportional font makes 1 and 8 "
         "different widths, so the digits shift as the numbers change.")

register_custom_property(
    builder_id, "selectable", "choice", values=("True", "False"),
    state="readonly", default_value="True",
    help="Whether clicking a digit selects it. The selection IS the tuning "
         "step, so a readout that is only a readout should set this False.")

register_custom_property(
    builder_id, "min_digit", "naturalnumber", default_value="1",
    help="The smallest selectable digit, as a power of ten. 1 means the "
         "units digit is shown but cannot be tuned -- right for a rig that "
         "steps in whole 10 Hz.")

register_custom_property(
    builder_id, "state", "choice", values=("normal", "disabled"),
    state="readonly", default_value="normal",
    help="Disabled dims the digits and stops selection. The value keeps "
         "updating: a display that froze while greyed would look like one "
         "showing a current reading.")

register_custom_property(
    builder_id, "command", "commandentry",
    help="Called with the new step, in units, when the selected digit "
         "changes. 100 means the hundreds digit -- 100 Hz per detent.")
