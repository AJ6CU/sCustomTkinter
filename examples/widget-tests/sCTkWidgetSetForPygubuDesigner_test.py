import tkinter as tk
from pygubu.component.plugin_engine import IDesignerPlugin
from pygubu.component.plugin_manager import PluginManager
from customtkinter import (CTkScrollableFrame)

#
#   Import the sCustomTkinter Widgets (alphabetically)
#   Format is "import foobo" for normal widgets that are selectable
#   format is
#   from foo import foo
#   from foobo import (fooBO,builder_id as foo_builder_id)
#   notice difference between "foorbo" (file name) and "fooBO" (class name within that file)
#


import sCTkButtonPrimarybo
import sCTkButtonSecondarybo
import sCTkButtonTertiarybo

import sCTkCheckBoxbo
import sCTkComboBoxbo

import sCTkDialbo

import sCTkDialogCorebo

import sCTkEntryPrimarybo
import sCTkEntrySecondarybo

#import sCTkFileExplorerbo # missing bo file


from sCTkFrame import sCTkFrame
from sCTkFramebo import (sCTkFrameBO, builder_id as sCTkFrame_builder_id)

from sCTkFrameLabeledPrimary import sCTkFrameLabeledPrimary
from sCTkFrameLabeledPrimarybo import (sCTkFrameLabeledPrimaryBO, builder_id as sCTkFrameLabeledPrimary_builder_id)
import sCTkFrameLabeledSecondarybo

from sCTkFrameOutlined import sCTkFrameOutlined
from sCTkFrameOutlinedbo import (sCTkFrameOutlinedBO, builder_id as sCTkFrameOutlined_builder_id)

import sCTkLabelPrimarybo
import sCTkLabelSecondarybo
import sCTkLabelTertiarybo

import sCTkOptionMenuPrimarybo

from sCTkOptionMenuSecondary import sCTkOptionMenuSecondary
from sCTkOptionMenuSecondarybo import (sCTkOptionMenuSecondaryBO, builder_id as sCTkOptionMenuSecondary_builder_id)

from sCTkPathChooser import sCTkPathChooser
from sCTkPathChooserbo import (sCTkPathChooserBO, builder_id as sCTkPathChooser_builder_id)

import sCTkProgressBarbo

import sCTkRadioButtonbo

import sCTkScrollableFramebo

import sCTkScrollbarbo

import sCTkSegmentedButtonbo
# from sCTkSegmentedButtonbo import (sCTkSegmentedButtonBO, builder_id as sCTkSegmentedButton_builder_id )

from sCTkSelector import sCTkSelector
from sCTkCheckBox import sCTkCheckBox       # Needs importing because selector made up of checkboxes and we need
                                            # to search to find the clickable master frame
from sCTkSelectorbo import (sCTkSelectorBO, builder_id as sCTkSelector_builder_id)

import sCTkSeparatorbo

import sCTkSliderbo

import sCTkSMeterbo
import sCTkSMeterBarbo

from sCTkSpinbox import sCTkSpinbox
from sCTkSpinboxbo import (sCTkSpinboxBO, builder_id as sCTkSpinbox_builder_id)

import sCTkSwitchbo

import sCTkTabviewbo

from sCTkTableview import sCTkTableview
from sCTkTableviewbo import (sCTkTableviewBO, builder_id as sCTkTableview_builder_id)

import sCTkTextboxPrimarybo
import sCTkTextboxSecondarybo

# import sCTkTreeviewbo         # undecied whether to include

#
# Preview class for sCTkFrame
#
class sCTkFrameForPreview(sCTkFrame):
    def winfo_children(self):
        # CTkFrame has a hidden canvas inside. So, to make it
        #  clickable on preview we need a hack.
        return super(tk.Frame, self).winfo_children()

class sCTkFrameOutlinedForPreview(sCTkFrameOutlined):
    def winfo_children(self):
        # CTkFrameOUtline has a hidden canvas inside. So, to make it
        #  clickable on preview we need a hack.
        return super(tk.Frame, self).winfo_children()

class sCTkFrameLabeledPrimaryForPreview(sCTkFrameLabeledPrimary):
    def winfo_children(self):
        # sCTkFrameLabeledPrimary has a hidden canvas inside. So, to make it
        #  clickable on preview we need a hack.
        return super(tk.Frame, self).winfo_children()

class sCTkPathChooserForPreview(sCTkPathChooser):
    def winfo_children(self):
        # sCTkPathChooser has a hidden canvas inside. So, to make it
        #  clickable on preview we need a hack.
        return super(tk.Frame, self).winfo_children()

class sCTkTableviewForPreview(sCTkTableview):
    def winfo_children(self):
        internal = []
        internal.extend(self._header_widgets)
        for row in self._cell_widgets:
            internal.extend(row)
        clist = [self._scrollbar]
        for widget in internal:
            for cwidget in widget.winfo_children():
                clist.append(cwidget)
        return clist


class sCTkSelectorForPreview(sCTkSelector):
    def winfo_children(self):
        internal = [
            self.search_bar,
            self.checkboxes_frame,
            self.checkboxes_frame._parent_frame,
            self.checkboxes_frame._parent_canvas,
        ]
        clist = []
        for widget in internal:
            for cwidget in widget.winfo_children():
                clist.append(cwidget)
                if isinstance(cwidget, sCTkCheckBox):
                    clist.append(cwidget._text_label)
                    clist.append(cwidget._canvas)
        return clist
import sys
class sCTkOptionMenuSecondaryForPreview(sCTkOptionMenuSecondary):
    def winfo_children(self):
        internal = [
            self._menu,
        ]
        clist = []
        for widget in internal:
            for cwidget in widget.winfo_children():
                clist.append(cwidget)
        return clist

class sCTkSpinboxForPreview(sCTkSpinbox):
    def winfo_children(self):
        internal = [
            self.entry
        ]
        clist = []
        for widget in internal:
            for cwidget in widget.winfo_children():
                clist.append(cwidget)
        return clist

# class sCTkSegmentedButtonForPreview(sCTkSegmentedButton):
#     def winfo_children(self):
#         # # CTkFrameOUtline has a hidden canvas inside. So, to make it
#         # #  clickable on preview we need a hack.
#         # return super(tk.Frame, self).winfo_children()
#
#         # internal = [
#         #     self.object
#         # ]
#         # clist = []
#         # for widget in internal:
#         #     for cwidget in widget.winfo_children():
#         #         clist.append(cwidget)
#         return self.winfo_children().master

#
# Builder for Preview
#
class sCTkFramePreviewBO(sCTkFrameBO):
    class_ = sCTkFrameForPreview

class sCTkFrameOutlinedForPreviewBO(sCTkFrameOutlinedBO):
    class_ = sCTkFrameOutlinedForPreview

class sCTkFrameLabeledPrimaryForPreviewBO(sCTkFrameLabeledPrimaryBO):
    class_ = sCTkFrameLabeledPrimaryForPreview

class sCTkPathChooserForPreviewBO(sCTkPathChooserBO):
    class_ = sCTkPathChooserForPreview

class sCTkTableviewForPreviewBO(sCTkTableviewBO):
    class_ = sCTkTableviewForPreview

class sCTkSelectorForPreviewBO(sCTkSelectorBO):
    class_ = sCTkSelectorForPreview

class sCTkOptionMenuSecondaryForPreviewBO(sCTkOptionMenuSecondaryBO):
    class_ = sCTkOptionMenuSecondaryForPreview

class sCTkSpinboxForPreviewBO(sCTkSpinboxBO):
    class_ = sCTkSpinboxForPreview

# class sCTkSegmentedButtonForPreviewBO(sCTkSegmentedButtonBO):
#     class_ = sCTkSegmentedButtonForPreview
#


#
# A Designer plugin for sCTk custom widgets
#
class sCTkPlugin(IDesignerPlugin):

    def get_preview_builder(self, builder_uid: str):
        """Return a BuilderObject subclass used to build a preview
        for the target builder_uid"""

        if builder_uid == sCTkFrame_builder_id:
            return sCTkFramePreviewBO
        elif builder_uid == sCTkFrameOutlined_builder_id:
            return sCTkFrameOutlinedForPreviewBO
        elif builder_uid == sCTkFrameLabeledPrimary_builder_id:
            return sCTkFrameLabeledPrimaryForPreviewBO
        elif builder_uid == sCTkPathChooser_builder_id:
            return sCTkPathChooserForPreviewBO
        elif builder_uid == sCTkTableview_builder_id:
            return sCTkTableviewForPreviewBO
        elif builder_uid == sCTkSelector_builder_id:
            return sCTkSelectorForPreviewBO
        elif builder_uid == sCTkOptionMenuSecondary_builder_id:
            return sCTkOptionMenuSecondaryForPreviewBO
        elif builder_uid == sCTkSpinbox_builder_id:
            return sCTkSpinboxForPreviewBO
        # elif builder_uid == sCTkSegmentedButton_builder_id:
        #     return sCTkSegmentedButtonForPreviewBO

        return None


#
# Create a plugin instance and inject it.
#
custom_plugin = sCTkPlugin()
PluginManager.designer_plugins.append(custom_plugin)

