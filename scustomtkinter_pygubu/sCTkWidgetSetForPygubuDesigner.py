import importlib
import tkinter as tk
from typing import List
from pygubu.component.plugin_engine import BuilderLoaderPlugin
from customtkinter import (CTkScrollableFrame)

#
#   EVERY WIDGET NEEDS A LINE HERE.
#
#   These imports are what register the builder objects when an APPLICATION
#   loads a .ui file. The Designer does not use them -- it imports the builder
#   objects directly through designer/plugin.py -- so a widget missing from
#   this list works perfectly while you design and fails the moment you run
#   the generated code:
#
#       AttributeError: 'list' object has no attribute 'startswith'
#
#   raised from importlib, because pygubu fell through to get_module_for().
#   sCTkNotebook, sCTkDialog and sCTkFileExplorer were all in that state.
#
#   Import the sCustomTkinter Widgets (alphabetically)
#   Format is "import foobo" for normal widgets that are selectable
#   format is
#   from foo import foo
#   from foobo import (fooBO,builder_id as foo_builder_id)
#   notice difference between "foorbo" (file name) and "fooBO" (class name within that file)
#

import scustomtkinter_pygubu.sCTkCorebo
import scustomtkinter_pygubu.sCTkToplevelbo

import scustomtkinter_pygubu.sCTkButtonPrimarybo
import scustomtkinter_pygubu.sCTkButtonSecondarybo
import scustomtkinter_pygubu.sCTkButtonTertiarybo

import scustomtkinter_pygubu.sCTkCheckBoxbo
import scustomtkinter_pygubu.sCTkComboBoxbo

import scustomtkinter_pygubu.sCTkDialbo

import scustomtkinter_pygubu.sCTkDialogbo

import scustomtkinter_pygubu.sCTkEntryPrimarybo
import scustomtkinter_pygubu.sCTkEntrySecondarybo

import scustomtkinter_pygubu.sCTkFileExplorerbo

import scustomtkinter_pygubu.sCTkFramebo

import scustomtkinter_pygubu.sCTkFrameLabeledPrimarybo
import scustomtkinter_pygubu.sCTkFrameLabeledSecondarybo

import scustomtkinter_pygubu.sCTkLabelPrimarybo
import scustomtkinter_pygubu.sCTkLabelSecondarybo
import scustomtkinter_pygubu.sCTkLabelTertiarybo

import scustomtkinter_pygubu.sCTkNotebookbo

import scustomtkinter_pygubu.sCTkOptionMenuPrimarybo
import scustomtkinter_pygubu.sCTkOptionMenuSecondarybo

import scustomtkinter_pygubu.sCTkPathChooserbo

import scustomtkinter_pygubu.sCTkProgressBarbo

import scustomtkinter_pygubu.sCTkRadioButtonbo

import scustomtkinter_pygubu.sCTkScrollableFramebo

import scustomtkinter_pygubu.sCTkScrollbarbo

import scustomtkinter_pygubu.sCTkSegmentedButtonbo
# from sCTkSegmentedButtonbo import (sCTkSegmentedButtonBO, builder_id as sCTkSegmentedButton_builder_id )

import scustomtkinter_pygubu.sCTkSelectorbo

import scustomtkinter_pygubu.sCTkSeparatorbo

import scustomtkinter_pygubu.sCTkSliderbo

import scustomtkinter_pygubu.sCTkSMeterbo
import scustomtkinter_pygubu.sCTkSMeterBarbo

import scustomtkinter_pygubu.sCTkSpinboxbo

import scustomtkinter_pygubu.sCTkSwitchbo

import scustomtkinter_pygubu.sCTkTabviewbo

import scustomtkinter_pygubu.sCTkTableviewbo

import scustomtkinter_pygubu.sCTkTextboxPrimarybo
import scustomtkinter_pygubu.sCTkTextboxSecondarybo


# import sCTkTreeviewbo         # undecied whether to include


class sCTkPlugin(BuilderLoaderPlugin):

    @classmethod
    def get_uid(cls) -> str:
        """Return plugin unique ID."""
        return "scustomtkinter"

    @classmethod
    def get_dependencies(cls) -> List[str]:
        """Return a list of required plugins UID."""
        return ["pygubu_customtkinter"]

    def do_activate(self) -> bool:
        spec = importlib.util.find_spec("scustomtkinter")
        return spec is not None

    def get_module_for(self, identifier: str) -> str:
        # A STRING, not a list.
        #
        # pygubu calls this when a class in a .ui file is not already
        # registered, then hands the result to importlib -- which does
        # name.startswith("."), so a list raised:
        #
        #     AttributeError: 'list' object has no attribute 'startswith'
        #
        # It went unnoticed for as long as it did because every widget was
        # registered by the imports at the top of this file, so the fallback
        # never ran. The first class to miss that list found it immediately.
        # get_all_modules() below DOES return a list, which is what the two
        # were confused with.
        return "scustomtkinter_pygubu"

    def get_all_modules(self):
        return ["scustomtkinter_pygubu"]

    def can_load(self, identifier: str) -> bool:
        return identifier.startswith("scustomtkinter.")

    def get_designer_plugin(self):
        from scustomtkinter_pygubu.designer.plugin import sCTkDesignerPlugin
        return sCTkDesignerPlugin()