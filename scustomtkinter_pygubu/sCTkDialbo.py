#!/usr/bin/python3
"""
sCTkDialbo

Unified Pygubu Builder Objects for the complete sCTkDial custom widget suite.
Houses sCTkDialContinuous, sCTkDialRange, and sCTkDialSelector builders
side-by-side, sharing the metadata configuration pipeline.
"""
import pygubu
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)

# Import the native custom classes directly out of your single-file source module
from scustomtkinter.sctk_dial import sCTkDialContinuous, sCTkDialRange, sCTkDialSelector
from scustomtkinter.themeable_widget import parse_list_property

builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


# =====================================================================
# 1. BUILDER OBJECT: INFINITE FLYWHEEL TUNING ENCODER (CONTINUOUS)
# =====================================================================
class sCTkDialContinuousBO(BuilderObject):
    class_ = sCTkDialContinuous
    classname = "sCTkDialContinuous"
    _code_classname = "sCTkDialContinuous"
    container = False

    OPTIONS_STANDARD = ("width", "height", "state")
    OPTIONS_CUSTOM = ("divisions", "diameter", "command", "left_click_callback", "right_click_callback")
    properties = OPTIONS_STANDARD + OPTIONS_CUSTOM
    command_properties = ("command", "left_click_callback", "right_click_callback")

    def realize(self, parent, *args, **kwargs):
        """Streamlined Pygubu Flywheel Tuning Wheel Lifecycle Intercept."""
        props_map = self.wmeta.properties if hasattr(self, "wmeta") else {}
        diameter_val = props_map.get("diameter", None)

        # Calculate target boundary box footprint with design fallbacks
        w = int(diameter_val) if (diameter_val and str(diameter_val).strip()) else 120
        self.wmeta.properties["width"] = str(w)
        self.wmeta.properties["height"] = str(w)

        # Call the core engine to instantiate the widget using standard xml properties
        widget = super().realize(parent, *args, **kwargs)
        return widget


# =====================================================================
# 2. BUILDER OBJECT: HARD END-STOP POTENTIOMETER (RANGE)
# =====================================================================
class sCTkDialRangeBO(BuilderObject):
    class_ = sCTkDialRange
    classname = "sCTkDialRange"
    _code_classname = "sCTkDialRange"
    container = False

    OPTIONS_STANDARD = ("width", "height", "state")
    OPTIONS_CUSTOM = ("from_", "to", "divisions", "diameter", "arc_angle","command", "left_click_callback", "right_click_callback")
    properties = OPTIONS_STANDARD + OPTIONS_CUSTOM
    command_properties = ("command", "left_click_callback", "right_click_callback")

    def realize(self, parent, *args, **kwargs):
        """Streamlined Pygubu Potentiometer Lifecycle Intercept."""
        props_map = self.wmeta.properties if hasattr(self, "wmeta") else {}
        diameter_val = props_map.get("diameter", None)

        # Calculate target boundary box footprint with design fallbacks
        w = int(diameter_val) if (diameter_val and str(diameter_val).strip()) else 120
        self.wmeta.properties["width"] = str(w)
        self.wmeta.properties["height"] = str(w)

        # Call the core engine to instantiate the widget using standard xml properties
        widget = super().realize(parent, *args, **kwargs)
        return widget


# =====================================================================
# 3. BUILDER OBJECT: DISCRETE SWITCH SELECTOR (SELECTOR)
# =====================================================================
class sCTkDialSelectorBO(BuilderObject):
    class_ = sCTkDialSelector
    classname = "sCTkDialSelector"
    _code_classname = "sCTkDialSelector"
    container = False

    OPTIONS_STANDARD = ("width", "height", "state")
    OPTIONS_CUSTOM = ("diameter", "arc_angle","command", "left_click_callback", "right_click_callback", "labels" ) #  # Note: Labels handles lists, which are usually initialized in code
    properties = OPTIONS_STANDARD + OPTIONS_CUSTOM
    command_properties = ("command", "left_click_callback", "right_click_callback")

    def _process_property_value(self, name, value):
        if name == 'labels':
            # FIX: was value.split(","), which did not strip whitespace -- so
            # "AM, FM, LSB" produced ["AM", " FM", " LSB"] and the dial drew
            # labels with leading spaces. The shared parser also accepts the
            # Python-literal form, so this property now behaves identically to
            # sCTkTableview's `columns` and sCTkSelector's `items`.
            return parse_list_property(value)
        return value

    def realize(self, parent, *args, **kwargs):
        """
        Streamlined Pygubu Selector Lifecycle Intercept.
        Calculates symmetrical geometry footprints safely using the wmeta table
        and lets the widget handle configuration changes natively on instantiation.
        """
        props_map = self.wmeta.properties if hasattr(self, "wmeta") else {}
        diameter_val = props_map.get("diameter", None)

        # Calculate target square boundary box sizes with active design fallbacks
        w = int(diameter_val) if (diameter_val and str(diameter_val).strip()) else 120
        self.wmeta.properties["width"] = str(w)
        self.wmeta.properties["height"] = str(w)

        # Instantiate the widget natively through Pygubu's master compilation loop
        widget = super().realize(parent, *args, **kwargs)
        return widget


# =====================================================================
# UNIFIED MODULE-LEVEL PYGUBU REGISTRATION LEDGER
# Registers all three semantic variations simultaneously inside the palette.
# =====================================================================

# --- 1. CONTINUOUS VFO ENCODER MATRIX REGISTRY ---
id_continuous = f"{builder_namespace}.sCTkDialContinuous"
register_widget(id_continuous, sCTkDialContinuousBO, "sCTkDialContinuous", ("ttk", section_name))
# `state` appears in OPTIONS_STANDARD for all three dials but was
# registered for none of them, so Pygubu supplied its own definition --
# which is why the Selector and Range dials offered a third value that
# the Continuous dial did not. Registering it explicitly makes all
# three agree and matches the widget's real two-state model.
register_custom_property(id_continuous, "state", "choice", values=("normal", "disabled"), help="Enabled or dimmed and inert.")
register_custom_property(id_continuous, "width", "naturalnumber", help="Width in pixels.")
register_custom_property(id_continuous, "height", "naturalnumber", help="Height in pixels.")
register_custom_property(id_continuous, "divisions", "naturalnumber", default_value=24, help="Flywheel detents per 360 turn.")
register_custom_property(id_continuous, "diameter", "naturalnumber", default_value=120, help="Knob circle size.")
register_custom_property(id_continuous, "command", "commandentry", help="Callback for knob turn by mousewheel.")
register_custom_property(id_continuous, "left_click_callback", "commandentry", help="Callback for left mouse click.")
register_custom_property(id_continuous, "right_click_callback", "commandentry", help="Callback for right mouse click.")

# --- 2. RANGED POTENTIOMETER MATRIX REGISTRY ---
id_range = f"{builder_namespace}.sCTkDialRange"
register_widget(id_range, sCTkDialRangeBO, "sCTkDialRange", ("ttk", section_name))
# `state` appears in OPTIONS_STANDARD for all three dials but was
# registered for none of them, so Pygubu supplied its own definition --
# which is why the Selector and Range dials offered a third value that
# the Continuous dial did not. Registering it explicitly makes all
# three agree and matches the widget's real two-state model.
register_custom_property(id_range, "state", "choice", values=("normal", "disabled"), help="Enabled or dimmed and inert.")
register_custom_property(id_range, "width", "naturalnumber", help="Width in pixels.")
register_custom_property(id_range, "height", "naturalnumber", help="Height in pixels.")
register_custom_property(id_range, "from_", "integernumber", default_value=0, help="Absolute minimum boundary limit.")
register_custom_property(id_range, "to", "integernumber", default_value=100, help="Absolute maximum boundary limit.")
register_custom_property(id_range, "divisions", "naturalnumber", default_value=5, help="Number of calibration tick lines drawn.")
register_custom_property(id_range, "diameter", "naturalnumber", default_value=120, help="Knob circle size.")
register_custom_property(id_range, "arc_angle", "naturalnumber", default_value=270, help="Symmetrical active arc sweep.")
register_custom_property(id_range, "command", "commandentry", help="Callback for knob turn by mousewheel.")
register_custom_property(id_range, "left_click_callback", "commandentry", help="Callback for left mouse click.")
register_custom_property(id_range, "right_click_callback", "commandentry", help="Callback for right mouse click.")

# --- 3. MODE SELECTOR MATRIX REGISTRY ---
id_selector = f"{builder_namespace}.sCTkDialSelector"
register_widget(id_selector, sCTkDialSelectorBO, "sCTkDialSelector", ("ttk", section_name))
# `state` appears in OPTIONS_STANDARD for all three dials but was
# registered for none of them, so Pygubu supplied its own definition --
# which is why the Selector and Range dials offered a third value that
# the Continuous dial did not. Registering it explicitly makes all
# three agree and matches the widget's real two-state model.
register_custom_property(id_selector, "state", "choice", values=("normal", "disabled"), help="Enabled or dimmed and inert.")
register_custom_property(id_selector, "width", "naturalnumber", help="Width in pixels.")
register_custom_property(id_selector, "height", "naturalnumber", help="Height in pixels.")
register_custom_property(id_selector, "diameter", "naturalnumber", default_value=120, help="Knob circle size.")
register_custom_property(id_selector, "arc_angle", "naturalnumber", default_value=270, help="Symmetrical active arc sweep.")
register_custom_property(id_selector, "command", "commandentry", help="Callback for knob turn by mousewheel.")
register_custom_property(id_selector, "left_click_callback", "commandentry", help="Callback for left mouse click.")
register_custom_property(id_selector, "right_click_callback", "commandentry", help="Callback for right mouse click.")
register_custom_property(id_selector, "labels", "entry", help='Preferred: ["A", "B", "C"]. Bare comma-separated (A, B, C) also works, but cannot contain a comma inside a value.')

