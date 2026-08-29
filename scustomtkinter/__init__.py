# scustomtkinter/__init__

#from .sCTkThemes import  apply_sCTkThemes
import os

# 🔑 THE DYNAMIC FILE PATH ANCHOR: Extracts the absolute physical location on disk
_PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))

def get_asset_path(relative_path: str) -> str:
    """Safely resolves file paths to assets relative to the physical package directory."""
    return os.path.normpath(os.path.join(_PACKAGE_ROOT, relative_path))


from .sctk_core import sCTk
from .sctk_button_primary import sCTkButtonPrimary
from . import sctk_button_primarybo
__all__ = [
    "sctk_button_primarybo"
]
from .sctk_button_secondary import sCTkButtonSecondary
from .sctk_button_tertiary import sCTkButtonTertiary
from .sctk_checkbox import sCTkCheckBox
from .sctk_combobox import sCTkComboBox
from .sctk_dial import sCTkDialContinuous
from .sctk_dial import sCTkDialSelector
from .sctk_dial import sCTkDialRange
# from .sctk_dialog_core import sCTkDialogCore
# from .sctk_dialog_mixin import sCTkDialogMixin
# from .sctk_dialog_toplevel import sCTkDialogToplevel
from .sctk_entry_primary import sCTkEntryPrimary
from .sctk_entry_secondary import sCTkEntrySecondary
from .sctk_file_explorer import sCTkFileExplorer
from .sctk_frame import sCTkFrame
from .sctk_frame_labeled_primary import sCTkFrameLabeledPrimary
from .sctk_frame_labeled_secondary import sCTkFrameLabeledSecondary
from .sctk_frame_outlined import sCTkFrameOutlined
from .sctk_label_primary import sCTkLabelPrimary
from .sctk_label_secondary import sCTkLabelSecondary
from .sctk_label_tertiary import sCTkLabelTertiary
from .sctk_messagebox import sCTkMessagebox

# =====================================================================
# 📦 VIRTUAL MESSAGEBOX SUBMODULE PROXY NAMESPACE
# =====================================================================

class _VirtualMessagebox:
    """Namespace container class mimicking the native tkinter.messagebox layout hooks."""
    def __init__(self):
        self.showinfo = sCTkMessagebox.showinfo
        self.showwarning = sCTkMessagebox.showwarning
        self.showerror = sCTkMessagebox.showerror
        self.askyesno = sCTkMessagebox.askyesno
        self.askwarningyesno = sCTkMessagebox.askwarningyesno
        self.askerroryesno = sCTkMessagebox.askerroryesno

# 🚀 Expose the virtual module globally inside the storefront namespace!
messagebox = _VirtualMessagebox()


from .sctk_optionmenu_primary import sCTkOptionMenuPrimary
from .sctk_optionmenu_secondary import sCTkOptionMenuSecondary
from .sctk_path_chooser import sCTkPathChooser
from .sctk_progress_bar import sCTkProgressBar
from .sctk_radiobutton import sCTkRadioButton
from .sctk_scrollable_frame import sCTkScrollableFrame
from .sctk_scrollbar import sCTkScrollbar
from .sctk_scrollbar import sCTkScrollArea
from .sctk_segmentedbutton import sCTkSegmentedButton
from .sctk_selector import sCTkSelector
from .sctk_separator import sCTkSeparator
from .sctk_slider import sCTkSlider
from .sctk_smeter import sCTkSMeter
from .sctk_smeter_bar import sCTkSMeterBar
from .sctk_spinbox import sCTkSpinbox
from .sctk_switch import sCTkSwitch
from .sctk_switch_alt import sCTkSwitchAlt
from .sctk_tableview import sCTkTableview
from .sctk_tabview import sCTkTabview
from .sctk_textbox_primary import sCTkTextboxPrimary
from .sctk_textbox_secondary import sCTkTextboxSecondary
from .sctk_toplevel import sCTkToplevel
