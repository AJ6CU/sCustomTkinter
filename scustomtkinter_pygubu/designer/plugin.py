import tkinter as tk

import customtkinter as ctk
from customtkinter.windows.widgets.core_widget_classes import CTkBaseClass

import scustomtkinter_pygubu.designer.properties

from pygubu.component.plugin_engine import IDesignerPlugin
from pygubu.stockimage import StockImageCache, StockImage
from pygubu.plugins.pygubu.designer.basehelpers import (
    ToplevelPreviewBaseBO,
    ToplevelPreviewFactory,
    ToplevelPreviewMixin,
)

from scustomtkinter.sctk_frame import sCTkFrame
from scustomtkinter_pygubu.sCTkFramebo import (sCTkFrameBO, builder_id as sCTkFrame_builder_id)

from scustomtkinter.sctk_frame_labeled_primary import sCTkFrameLabeledPrimary
from scustomtkinter_pygubu.sCTkFrameLabeledPrimarybo import (sCTkFrameLabeledPrimaryBO, builder_id as sCTkFrameLabeledPrimary_builder_id)
import scustomtkinter_pygubu.sCTkFrameLabeledSecondarybo

from scustomtkinter.sctk_optionmenu_secondary import sCTkOptionMenuSecondary

# FIXME: missing sCTkOptionMenuSecondaryBO class
# from scustomtkinter_pygubu.sCTkOptionMenuSecondarybo import (sCTkOptionMenuSecondaryBO, builder_id as sCTkOptionMenuSecondary_builder_id)
sCTkOptionMenuSecondary_builder_id = None

from scustomtkinter.sctk_path_chooser import sCTkPathChooser
from scustomtkinter_pygubu.sCTkPathChooserbo import (sCTkPathChooserBO, builder_id as sCTkPathChooser_builder_id)

from scustomtkinter.sctk_selector import sCTkSelector
from scustomtkinter.sctk_checkbox import sCTkCheckBox       # Needs importing because selector made up of checkboxes and we need
                                            # to search to find the clickable master frame
from scustomtkinter_pygubu.sCTkSelectorbo import (sCTkSelectorBO, builder_id as sCTkSelector_builder_id)

from scustomtkinter.sctk_spinbox import sCTkSpinbox
from scustomtkinter_pygubu.sCTkSpinboxbo import (sCTkSpinboxBO, builder_id as sCTkSpinbox_builder_id)

from scustomtkinter.sctk_tableview import sCTkTableview
from scustomtkinter_pygubu.sCTkTableviewbo import (sCTkTableviewBO, builder_id as sCTkTableview_builder_id)

# TOP-LEVEL WIDGETS -- adjust these two import lines to match your actual
# module names. The builder ids are needed by get_toplevel_preview_for().
from scustomtkinter.sctk_toplevel import sCTkToplevel
from scustomtkinter_pygubu.sCTkToplevelbo import builder_id as sCTkToplevel_builder_id
from scustomtkinter_pygubu.sCTkbo import builder_id as sCTk_builder_id


# =====================================================================
# THEME BLOCK NAMING
#
# ThemeableWidget resolves a widget's theme block by self.__class__.__name__.
# Every preview subclass below has a DIFFERENT class name than the widget it
# previews -- "sCTkTableviewForPreview" rather than "sCTkTableview" -- so the
# lookup finds no block and the widget is built with an empty theme.
#
# For widgets with no theme validation that means an unthemed preview. For
# the ones that hard-fail on a missing key (sCTkTableview, sCTkSelector,
# sCTkPathChooser, sCTkSpinbox, the labeled frames) it means a KeyError and a
# dead preview panel.
#
# _THEME_BLOCK_NAME below tells ThemeableWidget which block to read instead.
# It requires this one-line change in themeable_widget.py:
#
#     class_name = getattr(self, "_THEME_BLOCK_NAME", None) or self.__class__.__name__
#
# The attribute is generally useful beyond preview: any subclass that should
# inherit its parent's theme rather than silently losing it can set it.
# =====================================================================


#
# Preview class for sCTkFrame
#
class sCTkFrameForPreview(sCTkFrame):
    _THEME_BLOCK_NAME = "sCTkFrame"

    def winfo_children(self):
        # CTkFrame has a hidden canvas inside. So, to make it
        #  clickable on preview we need a hack.
        return super(tk.Frame, self).winfo_children()


class sCTkFrameLabeledPrimaryForPreview(sCTkFrameLabeledPrimary):
    _THEME_BLOCK_NAME = "sCTkFrameLabeledPrimary"

    def winfo_children(self):
        # sCTkFrameLabeledPrimary has a hidden canvas inside. So, to make it
        #  clickable on preview we need a hack.
        return super(tk.Frame, self).winfo_children()


class sCTkPathChooserForPreview(sCTkPathChooser):
    _THEME_BLOCK_NAME = "sCTkPathChooser"

    def winfo_children(self):
        # sCTkPathChooser has a hidden canvas inside. So, to make it
        #  clickable on preview we need a hack.
        return super(tk.Frame, self).winfo_children()


class sCTkTableviewForPreview(sCTkTableview):
    _THEME_BLOCK_NAME = "sCTkTableview"

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
    _THEME_BLOCK_NAME = "sCTkSelector"

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


class sCTkOptionMenuSecondaryForPreview(sCTkOptionMenuSecondary):
    _THEME_BLOCK_NAME = "sCTkOptionMenuSecondary"

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
    _THEME_BLOCK_NAME = "sCTkSpinbox"

    def winfo_children(self):
        internal = [
            self.entry
        ]
        clist = []
        for widget in internal:
            for cwidget in widget.winfo_children():
                clist.append(cwidget)
        return clist


#
# Builder for Preview
#
class sCTkFramePreviewBO(sCTkFrameBO):
    class_ = sCTkFrameForPreview


class sCTkFrameLabeledPrimaryForPreviewBO(sCTkFrameLabeledPrimaryBO):
    class_ = sCTkFrameLabeledPrimaryForPreview


class sCTkPathChooserForPreviewBO(sCTkPathChooserBO):
    class_ = sCTkPathChooserForPreview


class sCTkTableviewForPreviewBO(sCTkTableviewBO):
    class_ = sCTkTableviewForPreview


class sCTkSelectorForPreviewBO(sCTkSelectorBO):
    class_ = sCTkSelectorForPreview


# FIXME: Missing sCTkOptionMenuSecondaryBO
# class sCTkOptionMenuSecondaryForPreviewBO(sCTkOptionMenuSecondaryBO):
#     class_ = sCTkOptionMenuSecondaryForPreview


class sCTkSpinboxForPreviewBO(sCTkSpinboxBO):
    class_ = sCTkSpinboxForPreview


# =====================================================================
# TOP-LEVEL WIDGET PREVIEWS: sCTkToplevel and sCTk
#
# A top-level window can't be previewed as a real window inside the designer
# canvas, so pygubu renders it as a FRAME instead. That's why the factory
# classes below list sCTkFrameForPreview among their bases rather than
# sCTkToplevel: the preview IS a frame wearing the toplevel's properties.
#
# The consequence is that a handful of options a Toplevel accepts and a Frame
# does not have to be routed around CTk's own configure(). That's what the
# two mixins do -- they intercept those names and push them straight to the
# underlying tkinter widget via super(CTkBaseClass, self).
#
# Mirrors CustomTkinter's own designer preview module.
# =====================================================================
class sCTkToplevelPreviewMixin:
    def configure(self, cnf=None, **kw):
        if cnf:
            return super().configure(cnf, **kw)
        # configure properties not supported by sCTkFrame but yes by sCTkToplevel
        props = ("borderwidth", "highlightbackground", "highlightthickness")
        for pname in props:
            if pname in kw:
                super(CTkBaseClass, self).configure(**{pname: kw.pop(pname)})
        return super().configure(cnf, **kw)


sCTkToplevelPreview = ToplevelPreviewFactory(
    "sCTkToplevelPreview",
    (sCTkToplevelPreviewMixin, ToplevelPreviewMixin, sCTkFrameForPreview, object),
    {},
)


class sCTkToplevelPreviewBO(ToplevelPreviewBaseBO):
    class_ = sCTkToplevelPreview
    ro_properties = ToplevelPreviewBaseBO.ro_properties + (
        "background",
        "fg_color",
    )

    def _process_property_value(self, pname, value):
        if pname in ("width", "height"):
            return int(value)
        return super()._process_property_value(pname, value)


class sCTkPreviewMixin:
    def configure(self, cnf=None, **kw):
        if cnf:
            return super().configure(cnf, **kw)
        # configure properties not supported by sCTkFrame but yes by sCTk
        props = ("padx", "pady", "relief", "takefocus")
        for pname in props:
            if pname in kw:
                super(CTkBaseClass, self).configure(**{pname: kw.pop(pname)})
        return super().configure(cnf, **kw)


sCTkPreview = ToplevelPreviewFactory(
    "sCTkPreview",
    (sCTkPreviewMixin, ToplevelPreviewMixin, sCTkFrameForPreview, object),
    {},
)


class sCTkPreviewBO(sCTkToplevelPreviewBO):
    class_ = sCTkPreview
    properties = ToplevelPreviewBaseBO.properties + ("appearance_mode",)
    ro_properties = ToplevelPreviewBaseBO.ro_properties + ("fg_color",)

    def _set_property(self, target_widget, pname, value):
        if pname == "appearance_mode":
            ctk.set_appearance_mode(value)
        elif pname == "color_theme":
            ctk.set_default_color_theme(value)
        else:
            return super()._set_property(target_widget, pname, value)


#
# A Designer plugin for sCTk custom widgets
#
class sCTkDesignerPlugin(IDesignerPlugin):

    def get_preview_builder(self, builder_uid: str):
        """Return a BuilderObject subclass used to build a preview
        for the target builder_uid"""

        if builder_uid == sCTkFrame_builder_id:
            return sCTkFramePreviewBO
        elif builder_uid == sCTkFrameLabeledPrimary_builder_id:
            return sCTkFrameLabeledPrimaryForPreviewBO
        elif builder_uid == sCTkPathChooser_builder_id:
            return sCTkPathChooserForPreviewBO
        elif builder_uid == sCTkTableview_builder_id:
            return sCTkTableviewForPreviewBO
        elif builder_uid == sCTkSelector_builder_id:
            return sCTkSelectorForPreviewBO
        # FIXME: re-enable once sCTkOptionMenuSecondaryBO exists. The branch is
        # commented out rather than left in place because the BO it returns
        # does not exist yet -- reaching it would raise NameError. The builder
        # id is None above so no uid can match it accidentally.
        # elif builder_uid == sCTkOptionMenuSecondary_builder_id:
        #     return sCTkOptionMenuSecondaryForPreviewBO
        elif builder_uid == sCTkSpinbox_builder_id:
            return sCTkSpinboxForPreviewBO
        elif builder_uid == sCTkToplevel_builder_id:
            return sCTkToplevelPreviewBO
        elif builder_uid == sCTk_builder_id:
            return sCTkPreviewBO

        return None

    def get_toplevel_preview_for(self, builder_uid: str, widget_id: str,
                                 builder, top_master):
        """Return the toplevel preview widget for a top-level builder_uid,
        or None if this plugin doesn't handle it.

        Note this does NOT instantiate a BuilderObject itself. get_preview_builder()
        above has already told pygubu which BO class to use for this uid, so
        builder.get_object() constructs it correctly -- with a real WidgetMeta,
        which is what BuilderObject.__init__ actually expects. An earlier version
        here called preview_bo(builder, widget_id).realize(top_master), passing
        the id STRING where the meta belongs; that failed with
        "'str' object has no attribute 'properties'" as soon as
        _get_init_args() looked at self.wmeta.properties.

        top_master is accepted for interface compatibility and deliberately
        unused: the builder places the preview itself.

        The image-cache reset exists because building a toplevel creates a NEW
        tk root, and a StockImageCache is bound to the root it was created
        under. Without this, images resolved against the old root either fail
        or render blank in the new one.

        Mirrors CustomTkinter's own designer plugin.
        """
        toplevel_uids = (sCTk_builder_id, sCTkToplevel_builder_id)
        if builder_uid not in toplevel_uids:
            return None

        def on_root_created(root):
            builder.image_cache = StockImageCache(root, StockImage.registry)

        builder.on_first_object = on_root_created
        return builder.get_object(widget_id)