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
# from .sCTkButtonSecondary import CTkButtonSecondary
# from .sCTkButtonTertiary import sCTkButtonTertiary
# from .sCTkCheckBox import sCTkCheckBox
# from .sCTkComboBox import sCTkComboBox
# from .sCTkDial import sCTkDial
# from .sCTkDialogCore import sCTkDialogCore
# from .sCTkDialogMixin import sCTkDialogMixin
# from .sCTkDialogToplevel import sCTkDialogToplevel
# from .sCTkEntryPrimary import sCTkEntryPrimary
# from .sCTkEntrySecondary import sCTkEntrySecondary
# from .sCTkFileExplorer import sCTkFileExplorer
from .sctk_frame import sCTkFrame
#from .sCTkFrameLabeledPrimary import sCTkFrameLabeledPrimary
#from .sCTkFrameLabeledSecondary import sCTkFrameLabeledSecondary
#from .sCTkFrameOutlined import sCTkFrameOutlined
#from .sCTkLabelPrimary import sCTkLabelPrimary
#from .sCTkLabelSecondary import sCTkLabelSecondary
#from .sCTkLabelTertiary import sCTkLabelTertiary
#from .sCTkMessage import sCTkMessage
#from .sCTkOptionMenuPrimary import sCTkOptionMenuPrimary
#from .sCTkOptionMenuSecondary import sCTkOptionMenuSecondary
#from .sCTkPathChooser import sCTkPathChooser
#from .sCTkProgressBar import sCTkProgressBar
#from .sCTkRadioButton import sCTkRadioButton
#from .sCTkScrollableFrame import sCTkScrollableFrame
#from .sCTkScrollbar import sCTkScrollbar
#from .sCTkSegmentedButton import sCTkSegmentedButton
#from .sCTkSelector import sCTkSelector
#from .sCTkSeparator import sCTkSeparator
#from .sCTkSlider import sCTkSlider
#from .sCTkSMeter import sCTkSMeter
#from .sCTkSMeterBar import sCTkSMeterBar
#from .sCTkSpinbox import sCTkSpinbox
#from .sCTkSwitch import sCTkSwitch
#from .sCTkSwitchAlt import sCTkSwitchAlt
#from .sCTkTableview import sCTkTableview
#from .sCTkTabview import sCTkTabview
#from .sCTkTextboxPrimary import sCTkTextboxPrimary
#from .sCTkTextboxSecondary import sCTkTextboxSecondary
from .sctkthemes import sCTkThemes
#from .sCTkToplevel import sCTkToplevel
