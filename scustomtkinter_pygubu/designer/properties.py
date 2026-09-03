from pygubu.api.v1 import copy_custom_property

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.windows import (
    CTkBO,
    CTkToplevelBO
)
from pygubu.plugins.customtkinter.widgets import (
    CTkButtonBO,
    CTkCheckBoxBO,
    CTkComboBoxBO,
    CTkEntryBO,
    CTkFrameBO,
    CTkLabelBO,
    CTkOptionMenuBO,
    CTkProgressBarBO,
    CTkRadioButtonBO,
    CTkSegmentedButtonBO,
    CTkScrollbarBO,
    CTkSliderBO,
    CTkSwitchBO,
    CTkTextboxBO,
)
from pygubu.plugins.customtkinter.tabview import CTkTabviewBO
from pygubu.plugins.customtkinter.scrollableframe import CTkScrollableFrameBO


#
#   Imports  for the sCTK Widgets
#

from scustomtkinter_pygubu.sCTkCorebo import (sCTkBO, builder_id as sCTk_builder_id)
from scustomtkinter_pygubu.sCTkToplevelbo import (sCTkToplevelBO, builder_id as sCTkToplevel_builder_id)

from scustomtkinter_pygubu.sCTkButtonPrimarybo import (sCTkButtonPrimaryBO, builder_id as sCTkButtonPrimary_builder_id)
from scustomtkinter_pygubu.sCTkButtonSecondarybo import (sCTkButtonSecondaryBO, builder_id as sCTkButtonSecondary_builder_id)
from scustomtkinter_pygubu.sCTkButtonTertiarybo import (sCTkButtonTertiaryBO, builder_id as sCTkButtonTertiary_builder_id)

from scustomtkinter_pygubu.sCTkCheckBoxbo import (sCTkCheckBoxBO, builder_id as sCTkCheckBox_builder_id)
from scustomtkinter_pygubu.sCTkComboBoxbo import (sCTkComboBoxBO, builder_id as sCTkComboBox_builder_id)

# from scustomtkinter_pygubu.sCTkDialbo import (sCTkDialBO, builder_id as sCTkDial_builder_id)
# from scustomtkinter_pygubu.sCTkDialogCorebo import (sCTkDialogCoreBO, builder_id as sCTkDialogCore_builder_id)

from scustomtkinter_pygubu.sCTkEntryPrimarybo import (sCTkEntryPrimaryBO, builder_id as sCTkEntryPrimary_builder_id)
from scustomtkinter_pygubu.sCTkEntrySecondarybo import (sCTkEntrySecondaryBO, builder_id as sCTkEntrySecondary_builder_id)

# from scustomtkinter_pygubu.sCTkFileExplorerbo import (sCTkFileExplorerBO, builder_id as sCTkFileExplorer_builder_id)

from scustomtkinter_pygubu.sCTkFramebo import (sCTkFrameBO, builder_id as sCTkFrame_builder_id)
from scustomtkinter_pygubu.sCTkFrameLabeledPrimarybo import (sCTkFrameLabeledPrimaryBO, builder_id as sCTkFrameLabeledPrimary_builder_id)
from scustomtkinter_pygubu.sCTkFrameLabeledSecondarybo import (sCTkFrameLabeledSecondaryBO, builder_id as sCTkFrameLabeledSecondary_builder_id)

from scustomtkinter_pygubu.sCTkLabelPrimarybo import (sCTkLabelPrimaryBO, builder_id as sCTkLabelPrimary_builder_id)
from scustomtkinter_pygubu.sCTkLabelSecondarybo import (sCTkLabelSecondaryBO, builder_id as sCTkLabelSecondary_builder_id)
from scustomtkinter_pygubu.sCTkLabelTertiarybo import (sCTkLabelTertiaryBO, builder_id as sCTkLabelTertiary_builder_id)

from scustomtkinter_pygubu.sCTkOptionMenuPrimarybo import (sCTkOptionMenuPrimaryBO, builder_id as sCTkOptionMenuPrimary_builder_id)
from scustomtkinter_pygubu.sCTkOptionMenuSecondarybo import (sCTkOptionMenuSecondaryBO, builder_id as sCTkOptionMenuSecondary_builder_id)

# from scustomtkinter_pygubu.sCTkPathChooserbo import (sCTkPathChooserBO, builder_id as sCTkPathChooser_builder_id)

from scustomtkinter_pygubu.sCTkProgressBarbo import (sCTkProgressBarBO, builder_id as sCTkProgressBar_builder_id)
from scustomtkinter_pygubu.sCTkRadioButtonbo import (sCTkRadioButtonBO, builder_id as sCTkRadioButton_builder_id)

from scustomtkinter_pygubu.sCTkScrollbarbo import (sCTkScrollbarBO, builder_id as sCTkScrollbar_builder_id)
from scustomtkinter_pygubu.sCTkScrollableFramebo import (sCTkScrollableFrameBO, builder_id as sCTkScrollableFrame_builder_id)

from scustomtkinter_pygubu.sCTkSegmentedButtonbo import (sCTkSegmentedButtonBO, builder_id as sCTkSegmentedButton_builder_id)

from scustomtkinter_pygubu.sCTkSelectorbo import (sCTkSelectorBO, builder_id as sCTkSelector_builder_id)

# from scustomtkinter_pygubu.sCTkSeparatorbo import (sCTkSeparatorBO, builder_id as sCTkSeparator_builder_id)

from scustomtkinter_pygubu.sCTkSliderbo import (sCTkSliderBO, builder_id as sCTkSlider_builder_id)

# from scustomtkinter_pygubu.sCTkSMeterbo import (sCTkSMeterBO, builder_id as sCTkSMeter_builder_id)
# from scustomtkinter_pygubu.sCTkSMeterBarbo import (sCTkSMeterBarBO, builder_id as sCTkSMeterBar_builder_id)

from scustomtkinter_pygubu.sCTkSpinboxbo import (sCTkSpinboxBO, builder_id as sCTkSpinbox_builder_id)

from scustomtkinter_pygubu.sCTkSwitchbo import (sCTkSwitchBO, builder_id as sCTkSwitch_builder_id)

from scustomtkinter_pygubu.sCTkTabviewbo import (sCTkTabviewBO, builder_id as sCTkTabview_builder_id)

from scustomtkinter_pygubu.sCTkTableviewbo import (sCTkTableviewBO, builder_id as sCTkTableview_builder_id)

from scustomtkinter_pygubu.sCTkTextboxPrimarybo import (sCTkTextboxPrimaryBO, builder_id as sCTkTextboxPrimary_builder_id)
from scustomtkinter_pygubu.sCTkTextboxSecondarybo import (sCTkTextboxSecondaryBO, builder_id as sCTkTextboxSecondary_builder_id)


# Copy properties before we define our own properties.
#
# nsctk is the customtkinter plugin namespace
# nsctk.CTkButton is the registered name for CTkButtonBO builder.
for pname in CTkButtonBO.properties:
    try:
        copy_custom_property(nsctk.CTkButton, pname, sCTkButtonPrimary_builder_id)
        copy_custom_property(nsctk.CTkButton, pname, sCTkButtonSecondary_builder_id)
        copy_custom_property(nsctk.CTkButton, pname, sCTkButtonTertiary_builder_id)
    except RuntimeError:
        pass  # uconfigured property?

for pname in CTkCheckBoxBO.properties:
    try:
        copy_custom_property(nsctk.CTkCheckBox, pname, sCTkCheckBox_builder_id)
    except RuntimeError:
        pass

for pname in CTkComboBoxBO.properties:
    copy_custom_property(nsctk.CTkComboBox, pname, sCTkComboBox_builder_id)

for pname in CTkEntryBO.properties:
    try:
        copy_custom_property(nsctk.CTkEntry, pname, sCTkEntryPrimary_builder_id)
        copy_custom_property(nsctk.CTkEntry, pname, sCTkEntrySecondary_builder_id)
    except RuntimeError:
        pass


for pname in CTkLabelBO.properties:
    try:
        copy_custom_property(nsctk.CTkLabel, pname, sCTkLabelPrimary_builder_id)
        copy_custom_property(nsctk.CTkLabel, pname, sCTkLabelSecondary_builder_id)
        copy_custom_property(nsctk.CTkLabel, pname, sCTkLabelTertiary_builder_id)
    except RuntimeError:
        pass

for pname in CTkOptionMenuBO.properties:
    copy_custom_property(nsctk.CTkOptionMenu, pname, sCTkOptionMenuPrimary_builder_id)
    copy_custom_property(nsctk.CTkOptionMenu, pname, sCTkOptionMenuSecondary_builder_id)

for pname in CTkProgressBarBO.properties:
    try:
        copy_custom_property(nsctk.CTkProgressBar, pname, sCTkProgressBar_builder_id)
    except RuntimeError:
        pass

for pname in CTkRadioButtonBO.properties:
    copy_custom_property(nsctk.CTkRadioButton, pname, sCTkRadioButton_builder_id)

for pname in CTkScrollbarBO.properties:
    try:
        copy_custom_property(nsctk.CTkScrollbar, pname, sCTkScrollbar_builder_id)
    except RuntimeError:
        pass

for pname in CTkSliderBO.properties:
    copy_custom_property(nsctk.CTkSlider, pname, sCTkSlider_builder_id)

for pname in CTkSwitchBO.properties:
    try:
        copy_custom_property(nsctk.CTkSwitch, pname, sCTkSwitch_builder_id)
    except RuntimeError:
        pass

for pname in CTkTabviewBO.properties:
    try:
        copy_custom_property(nsctk.CTkTabview, pname, sCTkTabview_builder_id)
    except RuntimeError:
        pass

for pname in CTkTextboxBO.properties:
    try:
        copy_custom_property(nsctk.CTkTextbox, pname, sCTkTextboxPrimary_builder_id)
        copy_custom_property(nsctk.CTkTextbox, pname, sCTkTextboxSecondary_builder_id)
    except RuntimeError:
        pass

for pname in CTkBO.properties:
    try:
        copy_custom_property(nsctk.CTk, pname, sCTk_builder_id)
    except RuntimeError:
        pass

for pname in CTkToplevelBO.properties:
    try:
        copy_custom_property(nsctk.CTkToplevel, pname, sCTkToplevel_builder_id)
    except RuntimeError:
        pass

# FIX: this block previously referenced CTkScrollableFrame_builder_id -- a name
# that is defined NOWHERE in this file (note the missing leading "s"). Every
# iteration raised NameError, and the bare `except:` swallowed all of them, so
# no property definition was ever copied to sCTkScrollableFrame. The designer
# therefore knew the property NAMES, inherited from CTkScrollableFrameBO's own
# properties tuple, but had no registered definition for any of them -- no type,
# no permitted values, no default. The visible symptom was `orientation`
# displaying as "horizontal" in the inspector when the widget's real default is
# "vertical".
#
# The bare except is narrowed to RuntimeError, matching every other block here.
# A bare except would hide this class of typo again.
for pname in CTkScrollableFrameBO.properties:
    try:
        copy_custom_property(nsctk.CTkScrollableFrame, pname, sCTkScrollableFrame_builder_id)
        copy_custom_property(nsctk.CTkScrollableFrame, pname, sCTkFrameLabeledPrimary_builder_id)
        copy_custom_property(nsctk.CTkScrollableFrame, pname, sCTkFrameLabeledSecondary_builder_id)
        copy_custom_property(nsctk.CTkScrollableFrame, pname, sCTkTableview_builder_id)

    except RuntimeError:
        pass  # unconfigured property

for pname in CTkFrameBO.properties:
    try:
        copy_custom_property(nsctk.CTkFrame, pname, sCTkFrame_builder_id)
        copy_custom_property(nsctk.CTkFrame, pname, sCTkSelector_builder_id)
        copy_custom_property(nsctk.CTkFrame, pname, sCTkSpinbox_builder_id)
    except RuntimeError:
        pass  # unconfigured property

for pname in CTkSegmentedButtonBO.properties:
    try:
        for pname in CTkSegmentedButtonBO.properties:
            copy_custom_property(nsctk.CTkSegmentedButton, pname, sCTkSegmentedButton_builder_id)
    except RuntimeError:
        pass  # unconfigured property