import importlib
import tkinter as tk
from typing import List
from pygubu.component.plugin_engine import BuilderLoaderPlugin
from customtkinter import (CTkScrollableFrame)

#
#   Import the sCustomTkinter Widgets (alphabetically)
#   Format is "import foobo" for normal widgets that are selectable
#   format is
#   from foo import foo
#   from foobo import (fooBO,builder_id as foo_builder_id)
#   notice difference between "foorbo" (file name) and "fooBO" (class name within that file)
#

import scustomtkinter_pygubu.sCTkCorebo
# import scustomtkinter_pygubu.sCTkToplevelbo
import scustomtkinter_pygubu.sCTkButtonPrimarybo
import scustomtkinter_pygubu.sCTkButtonSecondarybo
import scustomtkinter_pygubu.sCTkButtonTertiarybo

import scustomtkinter_pygubu.sCTkCheckBoxbo
import scustomtkinter_pygubu.sCTkComboBoxbo

import scustomtkinter_pygubu.sCTkDialbo

# import scustomtkinter_pygubu.sCTkDialogCorebo  FIXME: missing files

import scustomtkinter_pygubu.sCTkEntryPrimarybo
import scustomtkinter_pygubu.sCTkEntrySecondarybo

#import sCTkFileExplorerbo # missing bo file

import scustomtkinter_pygubu.sCTkFramebo

import scustomtkinter_pygubu.sCTkFrameLabeledPrimarybo
import scustomtkinter_pygubu.sCTkFrameLabeledSecondarybo


import scustomtkinter_pygubu.sCTkLabelPrimarybo
import scustomtkinter_pygubu.sCTkLabelSecondarybo
import scustomtkinter_pygubu.sCTkLabelTertiarybo

import scustomtkinter_pygubu.sCTkOptionMenuPrimarybo

# import scustomtkinter_pygubu.sCTkOptionMenuSecondarybo # FIXME: missing files?

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
        return ["scustomtkinter_pygubu"]

    def get_all_modules(self):
        return ["scustomtkinter_pygubu"]

    def can_load(self, identifier: str) -> bool:
        return identifier.startswith("scustomtkinter.")

    def get_designer_plugin(self):
        from scustomtkinter_pygubu.designer.plugin import sCTkDesignerPlugin
        return sCTkDesignerPlugin()

