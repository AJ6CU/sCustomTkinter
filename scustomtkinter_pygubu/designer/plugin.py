import tkinter as tk

import customtkinter as ctk
from customtkinter.windows.widgets.core_widget_classes import CTkBaseClass

import scustomtkinter_pygubu.designer.properties

from pygubu.component.plugin_engine import IDesignerPlugin
from pygubu.stockimage import StockImageCache, StockImage
from pygubu.utils.widget import crop_widget
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


from scustomtkinter_pygubu.sCTkOptionMenuSecondarybo import (sCTkOptionMenuSecondaryBO, builder_id as sCTkOptionMenuSecondary_builder_id)

from scustomtkinter.sctk_path_chooser import sCTkPathChooser
from scustomtkinter_pygubu.sCTkPathChooserbo import (sCTkPathChooserBO, builder_id as sCTkPathChooser_builder_id)

from scustomtkinter.sctk_separator import sCTkSeparator
from scustomtkinter_pygubu.sCTkSeparatorbo import (sCTkSeparatorBuilder, builder_id as sCTkSeparator_builder_id)

from scustomtkinter.sctk_selector import sCTkSelector
from scustomtkinter.sctk_checkbox import sCTkCheckBox       # Needs importing because selector made up of checkboxes and we need
                                            # to search to find the clickable master frame
from scustomtkinter_pygubu.sCTkSelectorbo import (sCTkSelectorBO, builder_id as sCTkSelector_builder_id)

from scustomtkinter.sctk_spinbox import sCTkSpinbox
from scustomtkinter_pygubu.sCTkSpinboxbo import (sCTkSpinboxBO, builder_id as sCTkSpinbox_builder_id)

from scustomtkinter.sctk_tableview import sCTkTableview
from scustomtkinter_pygubu.sCTkTableviewbo import (sCTkTableviewBO, builder_id as sCTkTableview_builder_id)

# TOP-LEVEL WIDGETS.
#
# NOTE the module name for sCTk: it lives in sctk_core, NOT sctk_sctk. The
# rest of this library follows sctk_<widgetname>, but that convention produces
# an absurd name for the root window class, so this one file breaks it
# deliberately. Import sCTk from sctk_core everywhere.
from scustomtkinter.sctk_core import sCTk
from scustomtkinter.sctk_toplevel import sCTkToplevel

# The builder-object module follows the same naming break: sCTkCorebo, not
# sCTkbo, matching sctk_core on the widget side.
from scustomtkinter_pygubu.sCTkCorebo import builder_id as sCTk_builder_id
from scustomtkinter_pygubu.sCTkToplevelbo import builder_id as sCTkToplevel_builder_id


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


# =====================================================================
# TRANSPARENT BACKGROUNDS IN THE DESIGN VIEW
#
# A theme block may legitimately set a colour key to "transparent", meaning
# "show whatever is behind me". At runtime that always resolves against a
# themed parent, so it follows light/dark correctly. The Designer canvas does
# NOT participate in appearance mode -- it is a fixed light grey -- so a
# transparent widget rendered on it keeps a light background while its TEXT
# still follows the appearance mode. In dark mode that leaves dark-on-grey
# text, or a bright band where a separator should be.
#
# Confirmed against sCTkSelector and sCTkSeparator; ten theme blocks currently
# use "transparent" and any of them can show it, given text or a visible fill.
#
# preview_opaque() stamps a concrete background onto a preview subclass so the
# design view stays legible in both modes. This affects the DESIGNER ONLY --
# the real widget keeps its transparent background and its runtime appearance
# is unchanged.
#
# Written as one decorator rather than a hand-written __init__ per widget:
# this is the third widget to hit it and there will be more, so the per-widget
# version would keep growing.
PREVIEW_OPAQUE_BG = ("#FFFFFF", "#111827")


def preview_opaque(colour_key="fg_color", colour=PREVIEW_OPAQUE_BG):
    """
    Class decorator giving a preview subclass a concrete background.

    Args:
        colour_key: The theme key carrying the background. "fg_color" for
            most widgets; sCTkSeparator and sCTkTreeview use "bg_color".
        colour: The (light, dark) pair to substitute. Defaults to the pair
            used by sCTkScrollableFrame, so a stamped widget matches the
            containers it would normally sit inside.

    Returns:
        The class, with __init__ wrapped to supply the background.
    """
    def decorate(cls):
        original_init = cls.__init__

        def __init__(self, master=None, **kwargs):
            # setdefault, not assignment: an explicit value set in the
            # Designer inspector must still win.
            kwargs.setdefault(colour_key, colour)
            original_init(self, master, **kwargs)

        cls.__init__ = __init__
        return cls
    return decorate


#
# Preview class for sCTkFrame
#
@preview_opaque()
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


# sCTkSeparator carries its transparency on bg_color rather than fg_color, so
# the decorator is told which key to stamp. Its _draw() calls
# _detect_color_of_master() and falls back to the CTk theme's own fg_color when
# that returns transparent, which on the Designer canvas produces a bright band
# in dark mode -- more conspicuous than the Selector's low-contrast text,
# because the band is the full canvas height rather than a few glyphs.
@preview_opaque(colour_key="bg_color")
class sCTkSeparatorForPreview(sCTkSeparator):
    _THEME_BLOCK_NAME = "sCTkSeparator"


@preview_opaque()
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


class sCTkSeparatorForPreviewBO(sCTkSeparatorBuilder):
    class_ = sCTkSeparatorForPreview


class sCTkOptionMenuSecondaryForPreviewBO(sCTkOptionMenuSecondaryBO):
    class_ = sCTkOptionMenuSecondaryForPreview


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


# Every builder id registered by this package is "scustomtkinter.<ClassName>",
# so this prefix identifies our widgets and nothing else. Note it does NOT
# collide with CustomTkinter's own "customtkinter." prefix -- their designer
# plugin correctly ignores ours, and vice versa.
namespace_prefix = "scustomtkinter."


def _no_op(event=None):
    """Swallow an event during preview."""
    pass


def _neutralize(widget, sequences):
    """
    Replace a widget's handlers for the given event sequences with no-ops.

    Each bind is attempted independently: <TouchpadScroll> exists only on
    macOS and raises elsewhere, and a widget may legitimately not support a
    sequence. One failure must not skip the rest.
    """
    if widget is None:
        return
    for seq in sequences:
        try:
            widget.bind(seq, _no_op)
        except Exception:
            pass


def _preview_canvas(widget):
    """
    Return the drawing canvas for a widget, or None.

    Widgets inherited from CustomTkinter expose it as `_canvas`; the ones this
    library builds from scratch -- the dials, both S-meters, sCTkFileExplorer --
    create their own as `canvas`. CustomTkinter's plugin only checks `_canvas`,
    which would silently return None for half of this library.
    """
    for attr in ("_canvas", "canvas"):
        found = getattr(widget, attr, None)
        if found is not None:
            return found
    return None


# Sequences that make a widget grab the pointer in the designer canvas.
_HOVER_CLICK = ("<Enter>", "<Leave>", "<Button-1>")
_FOCUS = ("<FocusIn>", "<FocusOut>")
# Wheel and trackpad. Neutralizing these matters more here than upstream:
# scrolling over an un-neutralized widget scrolls IT instead of the canvas.
_SCROLL = ("<MouseWheel>", "<TouchpadScroll>", "<Button-4>", "<Button-5>")
# The dials additionally step on middle/right click and drag with a modifier.
_DIAL_EXTRA = ("<Button-2>", "<Button-3>",
               "<Shift-ButtonPress-1>", "<Shift-B1-Motion>")


#
# A Designer plugin for sCTk custom widgets
#
class sCTkDesignerPlugin(IDesignerPlugin):

    def is_toplevel_widget(self, builder_uid: str) -> bool:
        """
        Declares which builder ids are application ROOTS rather than ordinary
        widgets. Consulted by the Designer's script generator.

        WHAT BREAKS WITHOUT THIS. pygubudesigner/codegen/scriptgenerator.py
        decides which Mako template to use from:

            toplevel_uids = ("tk.Tk", "tk.Toplevel", "customtkinter.CTk",
                             "customtkinter.CTkToplevel",
                             "tkmt.ThemedTKinterFrame")
            if target_class in toplevel_uids or \
               PluginManager.is_toplevel_widget(target_class):
                main_widget_is_toplevel = True

        That tuple is hardcoded and does not include this package's ids, so
        sCTk fell to the WIDGET template, whose __main__ block reads:

            root = tk.Tk()
            app = MyApp(root)

        sCTk creates its own Tcl interpreter, so that produced a SECOND one.
        The consequence was subtle and nasty: a tk.StringVar built without an
        explicit master attaches to whichever root Tkinter considers default,
        so a variable bound to a widget in one interpreter was read from the
        other. The widget worked, the callback fired with the right value, and
        the variable came back empty forever. Every variable-bound widget in
        generated code was affected -- combo boxes, radio buttons, switches,
        check boxes.

        The `or` clause above is the supported fix. pygubu's own source carries
        a FIXME beside that tuple asking plugins to implement this method
        instead of the tuple being extended.

        Args:
            builder_uid: The registered id being tested.

        Returns:
            True if that id names an application root.
        """
        return builder_uid in (sCTk_builder_id, sCTkToplevel_builder_id)

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
        elif builder_uid == sCTkSeparator_builder_id:
            return sCTkSeparatorForPreviewBO
        elif builder_uid == sCTkOptionMenuSecondary_builder_id:
            return sCTkOptionMenuSecondaryForPreviewBO
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

    def configure_for_preview(self, builder_uid: str, widget):
        """Make a widget display with minimal functionality in the designer.

        Two jobs: crop it to its allotted space, and stop it reacting to the
        pointer. A widget that responds to clicks and scrolling fights the
        designer -- clicking selects nothing, and scrolling over it moves the
        widget instead of the canvas.

        NOTE ON A BUG UPSTREAM: CustomTkinter's own plugin tests
        `builder_uid.endswith(".CTKEntry")` -- capital K in the middle. The
        real uid is "customtkinter.CTkEntry", so that branch has never
        matched and their entry focus bindings were never actually
        neutralized. The equivalent branch below is spelled correctly.
        """
        if not builder_uid.startswith(namespace_prefix):
            return

        crop_widget(widget, recursive=True)

        canvas = _preview_canvas(widget)

        # --- Widgets built on sCTkScrollableFrame ------------------------
        # Left alone deliberately, following CustomTkinter's own early return
        # for CTkScrollableFrame. This library's scrollable frame activates
        # bindings through four separate paths and rebinds on <Configure>, so
        # a neutralizing pass would be undone by the next rebind anyway --
        # and cropping fires <Configure>, which triggers exactly that.
        scrollable_family = (
            ".sCTkScrollableFrame",
            ".sCTkFrameLabeledPrimary",
            ".sCTkFrameLabeledSecondary",
            ".sCTkTableview",
            ".sCTkSelector",
        )
        if builder_uid.endswith(scrollable_family):
            return

        # --- Direct inheritors from CustomTkinter ------------------------
        if builder_uid.endswith((".sCTkEntryPrimary", ".sCTkEntrySecondary")):
            _neutralize(canvas, _FOCUS)

        elif builder_uid.endswith(".sCTkSlider"):
            _neutralize(canvas, _HOVER_CLICK + ("<B1-Motion>",))

        elif builder_uid.endswith((".sCTkOptionMenuPrimary",
                                   ".sCTkOptionMenuSecondary")):
            _neutralize(canvas, _HOVER_CLICK)
            _neutralize(getattr(widget, "_text_label", None), _HOVER_CLICK)

        elif builder_uid.endswith(".sCTkComboBox"):
            # ComboBox binds by canvas TAG rather than on the widget, so the
            # dropdown arrow and its surrounding region need tag_bind.
            if canvas is not None:
                for tag in ("right_parts", "dropdown_arrow"):
                    for seq in _HOVER_CLICK:
                        try:
                            canvas.tag_bind(tag, seq, _no_op)
                        except Exception:
                            pass

        elif builder_uid.endswith((".sCTkSwitch", ".sCTkCheckBox")):
            # Not handled by CustomTkinter's plugin, but both toggle on click,
            # which in the designer reads as the widget refusing to be selected.
            _neutralize(canvas, _HOVER_CLICK)
            _neutralize(getattr(widget, "_text_label", None), _HOVER_CLICK)

        # --- Widgets original to this library ----------------------------
        elif builder_uid.endswith((".sCTkDialContinuous",
                                   ".sCTkDialSelector",
                                   ".sCTkDialRange")):
            # The worst offender in the library: steps on left/middle/right
            # click, drags with Shift, and turns on wheel or trackpad. Scroll
            # bindings are installed on several layers, so both the widget and
            # its canvas are neutralized.
            #
            # <Configure> is deliberately NOT neutralized -- the dial redraws
            # itself from it, and a dial that never redraws shows an empty
            # canvas in the designer.
            sequences = _HOVER_CLICK + _DIAL_EXTRA + _SCROLL
            _neutralize(canvas, sequences)
            _neutralize(widget, _SCROLL)

        elif builder_uid.endswith(".sCTkFileExplorer"):
            # Rows are created dynamically and each binds click and
            # double-click, so neutralizing the canvas alone is not enough --
            # the row widgets are separate children.
            _neutralize(canvas, _SCROLL)
            _neutralize(widget, _SCROLL)
            try:
                for row in widget.explorer_frame.winfo_children():
                    _neutralize(row, ("<Button-1>", "<Double-Button-1>"))
            except Exception:
                pass

        elif builder_uid.endswith(".sCTkPathChooser"):
            # Its browse button opens a MODAL file explorer -- clicking that
            # inside the designer would trap the user in a dialog with no
            # obvious way back. The attribute is `btn`; note that a wrong name
            # here fails silently, since _neutralize() accepts None.
            _neutralize(getattr(widget, "btn", None), ("<Button-1>",))

        # sCTkSMeter, sCTkSMeterBar and sCTkSeparator bind only <Configure>,
        # which they need in order to draw. Nothing to neutralize.