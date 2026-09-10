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
from scustomtkinter.sctk_frame_labeled_secondary import sCTkFrameLabeledSecondary
from scustomtkinter_pygubu.sCTkFrameLabeledSecondarybo import (sCTkFrameLabeledSecondaryBO, builder_id as sCTkFrameLabeledSecondary_builder_id)

from scustomtkinter.sctk_scrollable_frame import sCTkScrollableFrame
from scustomtkinter_pygubu.sCTkScrollableFramebo import (sCTkScrollableFrameBO, builder_id as sCTkScrollableFrame_builder_id)

from scustomtkinter.sctk_optionmenu_secondary import sCTkOptionMenuSecondary


from scustomtkinter_pygubu.sCTkOptionMenuSecondarybo import (sCTkOptionMenuSecondaryBO, builder_id as sCTkOptionMenuSecondary_builder_id)

from scustomtkinter.sctk_file_explorer import sCTkFileExplorer
from scustomtkinter_pygubu.sCTkFileExplorerbo import (sCTkFileExplorerBO, builder_id as sCTkFileExplorer_builder_id)

from scustomtkinter.sctk_path_chooser import sCTkPathChooser
from scustomtkinter_pygubu.sCTkPathChooserbo import (sCTkPathChooserBO, builder_id as sCTkPathChooser_builder_id)

from scustomtkinter.sctk_separator import sCTkSeparator
from scustomtkinter_pygubu.sCTkSeparatorbo import (sCTkSeparatorBuilder, builder_id as sCTkSeparator_builder_id)

from scustomtkinter.sctk_dial import (sCTkDialContinuous, sCTkDialRange,
                                      sCTkDialSelector)
from scustomtkinter_pygubu.sCTkDialbo import (
    sCTkDialContinuousBO, id_continuous as sCTkDialContinuous_builder_id,
    sCTkDialRangeBO, id_range as sCTkDialRange_builder_id,
    sCTkDialSelectorBO, id_selector as sCTkDialSelector_builder_id,
)

from scustomtkinter.sctk_dialog import sCTkDialog
from scustomtkinter_pygubu.sCTkDialogbo import (sCTkDialogBO, builder_id as sCTkDialog_builder_id)

from scustomtkinter.sctk_segmentedbutton import sCTkSegmentedButton
from scustomtkinter_pygubu.sCTkSegmentedButtonbo import (sCTkSegmentedButtonBO, builder_id as sCTkSegmentedButton_builder_id)

from scustomtkinter.sctk_selector import sCTkSelector
from scustomtkinter.sctk_checkbox import sCTkCheckBox       # Needs importing because selector made up of checkboxes and we need
                                            # to search to find the clickable master frame
from scustomtkinter_pygubu.sCTkSelectorbo import (sCTkSelectorBO, builder_id as sCTkSelector_builder_id)

from scustomtkinter.sctk_spinbox import sCTkSpinbox
from scustomtkinter_pygubu.sCTkSpinboxbo import (sCTkSpinboxBO, builder_id as sCTkSpinbox_builder_id)

from scustomtkinter.sctk_tableview import sCTkTableview
from scustomtkinter_pygubu.sCTkTableviewbo import (sCTkTableviewBO, builder_id as sCTkTableview_builder_id)

from scustomtkinter.sctk_radiobutton import sCTkRadioButton
from scustomtkinter_pygubu.sCTkRadioButtonbo import (sCTkRadioButtonBO, builder_id as sCTkRadioButton_builder_id)

from scustomtkinter.sctk_tabview import sCTkTabview
from scustomtkinter_pygubu.sCTkTabviewbo import (sCTkTabviewBO, builder_id as sCTkTabview_builder_id)

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


class sCTkFrameLabeledSecondaryForPreview(sCTkFrameLabeledSecondary):
    """
    Designer preview for sCTkFrameLabeledSecondary.

    NOT SELECTABLE BY CLICKING. CTkScrollableFrame inverts the usual
    arrangement: the widget IS the inner frame, created inside a canvas owned
    by a separate outer frame. So the surface the user sees is this widget's
    PARENT, and the widget has no real children of its own --
    winfo_children() reports an empty list.

    That defeats plain forwarding. The Designer's handler ends up on
    _parent_canvas, resolves event.widget to the canvas, and walking up from
    there never reaches this widget -- because the widget is a DESCENDANT of
    the canvas, not an ancestor. Binding the canvas directly is worse: it
    replaces the Designer's own handler.

    A transparent overlay was tried and Tk refuses it. The idea was to
    separate PARENT from POSITION -- an overlay whose parent is this frame, so
    the Designer resolves it correctly, displayed across the outer canvas via
    place(in_=...). But place requires its target to be the widget's own parent
    or a descendant of that parent, and the canvas is the overlay's
    GRANDPARENT:

        can't place ".!...!sctkframelabeledprimaryforpreview.!frame"
        relative to ".!...!ctkframe2.!canvas"

    A child dropped inside IS selectable, because it is a real descendant.
    Select the frame itself from the widget tree.
    """
    _THEME_BLOCK_NAME = "sCTkFrameLabeledSecondary"

    def winfo_children(self):
        return super(tk.Frame, self).winfo_children()


class sCTkScrollableFrameForPreview(sCTkScrollableFrame):
    """
    Designer preview for sCTkScrollableFrame.

    NOT SELECTABLE BY CLICKING. CTkScrollableFrame inverts the usual
    arrangement: the widget IS the inner frame, created inside a canvas owned
    by a separate outer frame. So the surface the user sees is this widget's
    PARENT, and the widget has no real children of its own --
    winfo_children() reports an empty list.

    That defeats plain forwarding. The Designer's handler ends up on
    _parent_canvas, resolves event.widget to the canvas, and walking up from
    there never reaches this widget -- because the widget is a DESCENDANT of
    the canvas, not an ancestor. Binding the canvas directly is worse: it
    replaces the Designer's own handler.

    A transparent overlay was tried and Tk refuses it. The idea was to
    separate PARENT from POSITION -- an overlay whose parent is this frame, so
    the Designer resolves it correctly, displayed across the outer canvas via
    place(in_=...). But place requires its target to be the widget's own parent
    or a descendant of that parent, and the canvas is the overlay's
    GRANDPARENT:

        can't place ".!...!sctkframelabeledprimaryforpreview.!frame"
        relative to ".!...!ctkframe2.!canvas"

    A child dropped inside IS selectable, because it is a real descendant.
    Select the frame itself from the widget tree.
    """
    _THEME_BLOCK_NAME = "sCTkScrollableFrame"

    def winfo_children(self):
        return super(tk.Frame, self).winfo_children()


class sCTkFileExplorerForPreview(sCTkFileExplorer):
    """
    Designer preview for sCTkFileExplorer.

    Two problems, the second only visible once the first is fixed.

    The explorer draws on an internal canvas that CTkFrame hides from
    winfo_children(), so the Designer's binding pass never reached it and the
    widget could not be clicked at all.

    Exposing the canvas made the OUTER EDGE selectable, but nothing else: the
    path entry, the navigation buttons and every file row are widgets the
    explorer builds for itself, so they are not in the builder's map and a
    click on one resolves to None. They are hidden from the binding pass and
    bound here instead, forwarding to the canvas -- which is where
    CTkFrame.bind() puts the Designer's own handler.

    Rows are rebuilt on every navigation, so the binding is reapplied after
    each fill.
    """
    _THEME_BLOCK_NAME = "sCTkFileExplorer"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bind_own_parts_to_self()

    def _own_part_roots(self):
        """
        The widgets this explorer built for itself.

        Only the two DIRECT children matter -- `top_frame` and
        `main_container` -- because the tree walk in
        _bind_own_parts_to_self() reaches everything beneath them: the scroll
        canvas, the scrollbar, `explorer_frame` and every file row.

        An earlier version listed `canvas` and `explorer_frame` instead, which
        was wrong twice: `explorer_frame` is a child of the canvas rather than
        of the widget, so excluding it had no effect at this level, and the
        canvas sits inside `main_container` rather than directly under the
        widget -- so the Designer kept binding `main_container`, and clicking
        the empty scrolling area still resolved to None.

        `_canvas` is deliberately absent: that is CTkFrame's own background,
        where the Designer's handler actually lives, and it must stay visible
        to the binding pass or a click on the outer edge selects nothing.
        """
        return [w for w in (getattr(self, "top_frame", None),
                            getattr(self, "main_container", None))
                if w is not None]

    def _bind_own_parts_to_self(self):
        """Makes a click anywhere inside the explorer select the explorer."""
        def select_self(event, target=self):
            # _canvas, NOT canvas.
            #
            # This widget has TWO canvases: self._canvas, which CTkFrame draws
            # its background on, and self.canvas, the scroll canvas holding the
            # file rows. CTkFrame.bind() redirects every binding to _canvas, so
            # that is where the Designer's click handler ended up.
            #
            # Generating the event on self.canvas dispatched into a widget with
            # nothing bound -- the forward succeeded and nothing happened. It is
            # also why clicking the outer EDGE always worked: the edge is
            # _canvas.
            try:
                canvas = getattr(target, "_canvas", None) or target
                canvas.event_generate("<Button-1>", x=1, y=1, when="now")
            except Exception:
                pass
            return "break"

        def bind_tree(widget, depth=0):
            if widget is None or depth > 4:
                return
            for w in (widget,
                      getattr(widget, "_canvas", None),
                      getattr(widget, "_text_label", None)):
                if w is None:
                    continue
                try:
                    w.bind("<Button-1>", select_self)
                except Exception:
                    pass
            try:
                children = tk.Misc.winfo_children(widget)
            except Exception:
                children = []
            for child in children:
                bind_tree(child, depth + 1)

        for root in self._own_part_roots():
            bind_tree(root)

    def _fill_explorer(self, *args, **kwargs):
        """Rebinds the rows, which this call destroys and recreates."""
        result = super()._fill_explorer(*args, **kwargs)
        self._bind_own_parts_to_self()
        return result

    def winfo_children(self):
        """
        Hides the explorer's own parts from the Designer's binding pass.

        The internal canvas is KEPT -- it is the visible background, and
        dropping it would stop a click on empty space selecting anything.
        """
        own = set(self._own_part_roots())
        return [w for w in super(tk.Frame, self).winfo_children() if w not in own]


class sCTkPathChooserForPreview(sCTkPathChooser):
    """
    Designer preview for sCTkPathChooser.

    The canvas hack alone made only the outer EDGE selectable. The entry and
    the browse button are widgets this chooser builds for itself, so they are
    not in the builder's map and a click on one resolved to None -- and they
    cover most of the widget.

    They are hidden from the Designer's binding pass and bound here instead,
    forwarding to _canvas, which is where CTkFrame.bind() puts the Designer's
    own handler. Same treatment as sCTkFileExplorer and sCTkDialog.
    """
    _THEME_BLOCK_NAME = "sCTkPathChooser"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bind_own_parts_to_self()

    def _own_part_roots(self):
        """The widgets this chooser builds for itself."""
        return [w for w in (getattr(self, "entry", None),
                            getattr(self, "btn", None))
                if w is not None]

    def _bind_own_parts_to_self(self):
        """Makes a click on the entry or the button select the chooser."""
        def select_self(event, target=self):
            try:
                canvas = getattr(target, "_canvas", None) or target
                canvas.event_generate("<Button-1>", x=1, y=1, when="now")
            except Exception:
                pass
            return "break"

        def bind_tree(widget, depth=0):
            if widget is None or depth > 3:
                return
            for w in (widget,
                      getattr(widget, "_canvas", None),
                      getattr(widget, "_text_label", None),
                      getattr(widget, "_entry", None)):
                if w is None:
                    continue
                try:
                    w.bind("<Button-1>", select_self)
                except Exception:
                    pass
            try:
                children = tk.Misc.winfo_children(widget)
            except Exception:
                children = []
            for child in children:
                bind_tree(child, depth + 1)

        for root in self._own_part_roots():
            bind_tree(root)

    def winfo_children(self):
        """
        Hides the chooser's own parts from the Designer's binding pass.

        The internal canvas is KEPT -- it is the visible background, and
        dropping it would stop a click on empty space selecting anything.
        """
        own = set(self._own_part_roots())
        return [w for w in super(tk.Frame, self).winfo_children()
                if w not in own]


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
class sCTkSegmentedButtonForPreview(sCTkSegmentedButton):
    """
    Designer preview for sCTkSegmentedButton.

    WITHOUT THIS THE DESIGNER CRASHES ON DROP. CTkSegmentedButton.bind() raises
    NotImplementedError unconditionally, and pygubu's bind_preview_widget()
    calls bind() on every widget it walks:

        File ".../ctk_segmented_button.py", line 471, in bind
            raise NotImplementedError
        NotImplementedError

    Forwarding to the children instead lets the walk complete. CustomTkinter's
    own designer plugin does exactly this for its CTkSegmentedButton, with the
    note that selection still does not work -- their comment reads "I can't
    select a segmented button in preview". So this makes the widget usable in
    the Designer without making it selectable on the canvas; select it from the
    widget tree.

    SELECTION. CustomTkinter's own attempt stops at "I can't select a
    segmented button in preview". The same problem was solved for sCTkDialog
    earlier, and the same solution applies here:

      - Pygubu resolves a clicked widget through builder.get_widget_id(). The
        segments are CTkButtons this widget creates for itself, so they are not
        in the builder's map and a click on one resolves to None.
      - winfo_children() below hides them from pygubu's binding pass, so it
        binds this widget and not the segments.
      - _bind_segments_to_self() then binds them to forward their click here.
      - The forwarded event goes to self._canvas, NOT to self. CTkFrame.bind()
        redirects every binding to its internal canvas, so that is where
        pygubu's handler actually ended up -- generating the event on the
        widget itself dispatches into nothing.
    """
    _THEME_BLOCK_NAME = "sCTkSegmentedButton"

    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self._bind_segments_to_self()

    def _segment_widgets(self):
        """The CTkButtons this widget builds for itself, canvas excluded."""
        return [w for w in super(tk.Frame, self).winfo_children()
                if isinstance(w, ctk.CTkButton)]

    def _bind_segments_to_self(self):
        """
        Makes a click on any segment select the whole widget.

        A CTkButton draws on an internal canvas that receives the click before
        the widget does, and puts its label in a separate tk.Label, so all
        three are bound.
        """
        def select_self(event, target=self):
            try:
                canvas = getattr(target, "_canvas", None) or target
                canvas.event_generate("<Button-1>", x=1, y=1, when="now")
            except Exception:
                pass
            return "break"

        for segment in self._segment_widgets():
            for widget in (segment,
                           getattr(segment, "_canvas", None),
                           getattr(segment, "_text_label", None)):
                if widget is None:
                    continue
                try:
                    widget.bind("<Button-1>", select_self)
                except Exception:
                    pass

    def configure(self, *args, **kwargs):
        """
        Rebinds after any change that could rebuild the segments.

        Setting `values` destroys the existing buttons and creates new ones,
        which would otherwise be left unbound.
        """
        result = super().configure(*args, **kwargs)
        if not (len(args) == 1 and not isinstance(args[0], dict)):
            self._bind_segments_to_self()
        return result

    def winfo_children(self):
        """
        Hides the segments from the Designer's binding pass.

        Pygubu binds a click handler to everything it finds here, and that
        handler resolves the clicked widget through get_widget_id() -- which
        knows nothing about buttons this widget created for itself. Excluding
        them leaves the bindings installed by _bind_segments_to_self() intact.

        The internal canvas is KEPT: it is this widget's visible background,
        and dropping it would stop a click on empty space selecting anything.
        """
        return [w for w in super(tk.Frame, self).winfo_children()
                if not isinstance(w, ctk.CTkButton)]

    def bind(self, sequence=None, func=None, add=None):
        for child in self.winfo_children():
            try:
                child.bind(sequence, func, True)
            except Exception:
                # A child that refuses the binding must not take the whole
                # walk down with it -- that is the failure being fixed here.
                pass


class sCTkRadioButtonForPreview(sCTkRadioButton):
    """
    Designer preview for sCTkRadioButton.

    Without this the widget cannot be selected by clicking it: CTkFrame hides
    its internal canvas from winfo_children(), the Designer walks that list to
    bind its click handler, and the canvas is the only thing there is to click.
    """
    _THEME_BLOCK_NAME = "sCTkRadioButton"

    def winfo_children(self):
        return super(tk.Frame, self).winfo_children()


class sCTkTabviewForPreview(sCTkTabview):
    """
    Designer preview for sCTkTabview.

    An EMPTY tabview could not be selected at all -- with no tabs there is
    nothing on the canvas but the widget's own hidden background, which the
    Designer never saw. Once a tab existed, the tab button was clickable and
    masked the problem.

    The internal CTkSegmentedButton is EXCLUDED from that list, for two
    reasons. Its bind() raises NotImplementedError unconditionally, so the
    Designer's binding walk crashed on load:

        File ".../ctk_segmented_button.py", line 471, in bind
            raise NotImplementedError

    And leaving it unbound keeps tab switching working -- the clicks go to
    CustomTkinter's own handler rather than being intercepted for selection.

    THE CONSEQUENCE is that clicking a tab switches the page without selecting
    that tab in the inspector, which goes on showing whatever was selected
    before. Clicking a widget inside the new page corrects it.

    An attempt to fix that has been removed rather than left in place. Binding
    the segmented button's inner buttons with add=True worked as far as it
    went -- the tab switched, the handler fired, and the newly revealed page
    was found -- but forwarding a click to that page selected nothing, because
    the pages are sCTkFrames this widget creates in add() at runtime and are
    not in the builder's widget map. get_widget_id() returns None for them, the
    same reason sCTkDialog's own parts did not resolve.

    Select tabs from the widget tree. CustomTkinter's own plugin carries a
    commented-out attempt at the same problem.
    """
    _THEME_BLOCK_NAME = "sCTkTabview"

    def winfo_children(self):
        children = super(tk.Frame, self).winfo_children()
        segmented = getattr(self, "_segmented_button", None)
        if segmented is None:
            return children
        return [w for w in children if w is not segmented]


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
        """
        FIX: this used to walk self._menu, an inner CTkOptionMenu, because the
        widget was a COMPOSITE -- a frame wrapping a menu, which was how it got
        a border that native CTkOptionMenu cannot draw. It is now a plain
        CTkOptionMenu subclass like Primary, with the border supplied by
        sCTkOptionMenuBorderMixin, so that attribute is gone and the walk
        raised:

            AttributeError: 'sCTkOptionMenuSecondaryForPreview' object has no
            attribute '_menu'

        The ordinary hack applies instead: CTkFrame hides its internal canvas
        from winfo_children(), and the Designer needs to see it to hit-test a
        click.
        """
        return super(tk.Frame, self).winfo_children()


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


class sCTkFrameLabeledSecondaryForPreviewBO(sCTkFrameLabeledSecondaryBO):
    class_ = sCTkFrameLabeledSecondaryForPreview


class sCTkScrollableFrameForPreviewBO(sCTkScrollableFrameBO):
    class_ = sCTkScrollableFrameForPreview


class sCTkFileExplorerForPreviewBO(sCTkFileExplorerBO):
    class_ = sCTkFileExplorerForPreview


class sCTkPathChooserForPreviewBO(sCTkPathChooserBO):
    class_ = sCTkPathChooserForPreview


class sCTkTableviewForPreviewBO(sCTkTableviewBO):
    class_ = sCTkTableviewForPreview


class sCTkDialContinuousForPreview(sCTkDialContinuous):
    """
    Designer preview for sCTkDialContinuous.

    Without this the dial cannot be selected by clicking it. Every dial draws
    itself on an internal canvas that CTkFrame hides from winfo_children(),
    and the Designer walks that list to bind its click handler -- so it never
    reached the only part of the widget there is to click.
    """
    _THEME_BLOCK_NAME = "sCTkDialContinuous"

    def _inject_private_layer_bindings(self):
        """
        Deliberately does nothing in the Designer.

        The real method binds the scroll sequences on three layers -- the dial
        canvas, the widget, and CTkFrame's canvas -- with add="+", and it is
        scheduled 50ms after construction. Both details defeat
        configure_for_preview(): it has already run by then, and add="+"
        appends rather than replaces, so the dial's own handlers sit alongside
        the no-ops instead of being displaced by them.

        The visible symptom was a dial that still turned under a trackpad in
        the design canvas. Not injecting at all is simpler than trying to
        neutralize afterwards, and a preview dial has no reason to scroll.
        """
        return

    def state(self, mode=None):
        """
        Re-applies the Designer's bindings after a state change.

        A dial's state() rebinds its own canvas handlers -- <Button-1>,
        <Button-2>, <Button-3> and the scroll sequences -- every time it
        returns to normal, and clears them when disabled. That wipes out
        whatever configure_for_preview() installed, so a dial stopped being
        selectable the moment its state was touched and did not recover when
        set back to normal.

        Deferred to idle so it runs after state() has finished its own
        rebinding rather than racing it.
        """
        result = super().state(mode) if mode is not None else super().state()
        if mode is not None:
            try:
                self.after_idle(self._reapply_preview_bindings)
            except Exception:
                pass
        return result

    def _reapply_preview_bindings(self):
        """
        Silences the dial's interactive bindings and forwards clicks for
        selection -- the same treatment configure_for_preview() applies, in a
        form the widget can re-run for itself.
        """
        face = getattr(self, "canvas", None)
        if face is None:
            return

        for seq in (s for s in (_HOVER_CLICK + _DIAL_EXTRA + _SCROLL)
                    if s != "<Button-1>"):
            try:
                face.bind(seq, _no_op)
            except Exception:
                pass

        def select_self(event, target=self):
            try:
                bg = getattr(target, "_canvas", None)
                if bg is not None:
                    bg.event_generate("<Button-1>", x=1, y=1, when="now")
            except Exception:
                pass
            return "break"

        try:
            face.bind("<Button-1>", select_self)
        except Exception:
            pass

    def winfo_children(self):
        """
        Hides the dial's own drawing canvas from the Designer's binding pass,
        keeping CTkFrame's background canvas so edge clicks still work.
        """
        face = getattr(self, "canvas", None)
        return [w for w in super(tk.Frame, self).winfo_children() if w is not face]


class sCTkDialRangeForPreview(sCTkDialRange):
    """Designer preview for sCTkDialRange. See sCTkDialContinuousForPreview."""
    _THEME_BLOCK_NAME = "sCTkDialRange"

    def _inject_private_layer_bindings(self):
        """
        Deliberately does nothing in the Designer.

        The real method binds the scroll sequences on three layers -- the dial
        canvas, the widget, and CTkFrame's canvas -- with add="+", and it is
        scheduled 50ms after construction. Both details defeat
        configure_for_preview(): it has already run by then, and add="+"
        appends rather than replaces, so the dial's own handlers sit alongside
        the no-ops instead of being displaced by them.

        The visible symptom was a dial that still turned under a trackpad in
        the design canvas. Not injecting at all is simpler than trying to
        neutralize afterwards, and a preview dial has no reason to scroll.
        """
        return

    def state(self, mode=None):
        """
        Re-applies the Designer's bindings after a state change.

        A dial's state() rebinds its own canvas handlers -- <Button-1>,
        <Button-2>, <Button-3> and the scroll sequences -- every time it
        returns to normal, and clears them when disabled. That wipes out
        whatever configure_for_preview() installed, so a dial stopped being
        selectable the moment its state was touched and did not recover when
        set back to normal.

        Deferred to idle so it runs after state() has finished its own
        rebinding rather than racing it.
        """
        result = super().state(mode) if mode is not None else super().state()
        if mode is not None:
            try:
                self.after_idle(self._reapply_preview_bindings)
            except Exception:
                pass
        return result

    def _reapply_preview_bindings(self):
        """
        Silences the dial's interactive bindings and forwards clicks for
        selection -- the same treatment configure_for_preview() applies, in a
        form the widget can re-run for itself.
        """
        face = getattr(self, "canvas", None)
        if face is None:
            return

        for seq in (s for s in (_HOVER_CLICK + _DIAL_EXTRA + _SCROLL)
                    if s != "<Button-1>"):
            try:
                face.bind(seq, _no_op)
            except Exception:
                pass

        def select_self(event, target=self):
            try:
                bg = getattr(target, "_canvas", None)
                if bg is not None:
                    bg.event_generate("<Button-1>", x=1, y=1, when="now")
            except Exception:
                pass
            return "break"

        try:
            face.bind("<Button-1>", select_self)
        except Exception:
            pass

    def winfo_children(self):
        """
        Hides the dial's own drawing canvas from the Designer's binding pass,
        keeping CTkFrame's background canvas so edge clicks still work.
        """
        face = getattr(self, "canvas", None)
        return [w for w in super(tk.Frame, self).winfo_children() if w is not face]


class sCTkDialSelectorForPreview(sCTkDialSelector):
    """Designer preview for sCTkDialSelector. See sCTkDialContinuousForPreview."""
    _THEME_BLOCK_NAME = "sCTkDialSelector"

    def _inject_private_layer_bindings(self):
        """
        Deliberately does nothing in the Designer.

        The real method binds the scroll sequences on three layers -- the dial
        canvas, the widget, and CTkFrame's canvas -- with add="+", and it is
        scheduled 50ms after construction. Both details defeat
        configure_for_preview(): it has already run by then, and add="+"
        appends rather than replaces, so the dial's own handlers sit alongside
        the no-ops instead of being displaced by them.

        The visible symptom was a dial that still turned under a trackpad in
        the design canvas. Not injecting at all is simpler than trying to
        neutralize afterwards, and a preview dial has no reason to scroll.
        """
        return

    def state(self, mode=None):
        """
        Re-applies the Designer's bindings after a state change.

        A dial's state() rebinds its own canvas handlers -- <Button-1>,
        <Button-2>, <Button-3> and the scroll sequences -- every time it
        returns to normal, and clears them when disabled. That wipes out
        whatever configure_for_preview() installed, so a dial stopped being
        selectable the moment its state was touched and did not recover when
        set back to normal.

        Deferred to idle so it runs after state() has finished its own
        rebinding rather than racing it.
        """
        result = super().state(mode) if mode is not None else super().state()
        if mode is not None:
            try:
                self.after_idle(self._reapply_preview_bindings)
            except Exception:
                pass
        return result

    def _reapply_preview_bindings(self):
        """
        Silences the dial's interactive bindings and forwards clicks for
        selection -- the same treatment configure_for_preview() applies, in a
        form the widget can re-run for itself.
        """
        face = getattr(self, "canvas", None)
        if face is None:
            return

        for seq in (s for s in (_HOVER_CLICK + _DIAL_EXTRA + _SCROLL)
                    if s != "<Button-1>"):
            try:
                face.bind(seq, _no_op)
            except Exception:
                pass

        def select_self(event, target=self):
            try:
                bg = getattr(target, "_canvas", None)
                if bg is not None:
                    bg.event_generate("<Button-1>", x=1, y=1, when="now")
            except Exception:
                pass
            return "break"

        try:
            face.bind("<Button-1>", select_self)
        except Exception:
            pass

    def winfo_children(self):
        """
        Hides the dial's own drawing canvas from the Designer's binding pass,
        keeping CTkFrame's background canvas so edge clicks still work.
        """
        face = getattr(self, "canvas", None)
        return [w for w in super(tk.Frame, self).winfo_children() if w is not face]


class sCTkDialogForPreview(sCTkDialog):
    """
    Designer preview for sCTkDialog.

    _MAKE_WINDOW = False is the whole point. At runtime this widget builds its
    own sCTkDialogToplevel and packs itself into it -- a dialog is always its
    own window. In the Designer that would spawn a real, separate, possibly
    MODAL window on every redraw, and a redraw happens on every property edit.
    A modal one would seize input and leave the Designer unusable.

    With the flag off, sCTkDialog.__init__ takes its early return and
    behaves as an ordinary frame, so the dialog renders inline on the canvas
    where it can be laid out.

    The window properties -- title, width, height, modal, offset_x, offset_y --
    remain editable in the inspector and still reach generated code. They
    simply have no effect on the preview, because there is no window for them
    to act on.

    _THEME_BLOCK_NAME names the block this preview reads. It must be
    "sCTkDialog", not "sCTkFrame": the dialog now has a block of its own
    carrying heading_font and heading_text_color, and those keys are required.
    Pointing at sCTkFrame's block resolved without them and construction failed
    with a KeyError naming a block the widget never reads.
    """
    _THEME_BLOCK_NAME = "sCTkDialog"
    _MAKE_WINDOW = False

    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self._bind_own_parts_to_self()

    def _bind_own_parts_to_self(self):
        """
        Makes a click on the heading or a button select the DIALOG.

        The Designer resolves a clicked widget through
        builder.get_widget_id(). The heading label and the three buttons are
        built by the dialog rather than by the builder, so they are not in its
        map: a click on one resolved to None and selected nothing. Only the
        very edge of the dialog -- its own background canvas -- worked.

        Forwarding the click to the dialog gives the Designer a widget it knows
        about, which is what the user meant.

        Done HERE, in the preview class's own __init__, rather than in
        configure_for_preview(): that hook was not reaching this widget, and
        this runs unconditionally at construction. It survives the Designer's
        own binding pass because winfo_children() below excludes these parts,
        so that pass never visits them.

        CTk buttons draw on an internal canvas that receives the click before
        the widget does, so _canvas and _text_label are bound as well as the
        widget itself.
        """
        def select_dialog(event, dialog=self):
            # The event goes to the dialog's internal CANVAS, not to the
            # dialog widget.
            #
            # CTkFrame.bind() redirects every binding to self._canvas rather
            # than attaching it to the frame -- the same override that made
            # scroll bindings silently vanish in sCTkScrollableFrame. So when
            # the Designer bound its click handler to this dialog, the binding
            # landed on the canvas. Generating the event on the dialog found
            # nothing bound there and did nothing, which is why clicks were
            # forwarded successfully and still selected nothing.
            #
            # It also explains why clicking the very edge always worked: the
            # edge IS the canvas.
            target = getattr(dialog, "_canvas", None) or dialog
            try:
                target.event_generate("<Button-1>", x=1, y=1, when="now")
            except Exception:
                pass
            return "break"

        # contentFrame is included, but only its CANVAS gets bound below --
        # the frame itself stays visible to the Designer's own binding pass so
        # that widgets the user drops inside it still select themselves. In
        # practice a user drops a frame in here to hold their own layout, and
        # clicking that frame should select it, not the dialog; clicking the
        # bare content area around it should reach the dialog, since there is
        # nothing else there to select.
        parts = [getattr(self, "heading_Label", None),
                 getattr(self, "titleFrame", None),
                 getattr(self, "actionFrame", None),
                 getattr(self, "contentFrame", None)]
        for name in ("apply", "cancel", "reset"):
            parts.append(getattr(self, f"{name}_Button", None))

        content = getattr(self, "contentFrame", None)
        for part in parts:
            if part is None:
                continue
            if part is content:
                # Canvas only. Binding the frame itself would intercept clicks
                # meant for the user's own widgets inside it.
                targets = (getattr(part, "_canvas", None),)
            else:
                targets = (part,
                           getattr(part, "_canvas", None),
                           getattr(part, "_text_label", None))
            for target in targets:
                if target is None:
                    continue
                try:
                    target.bind("<Button-1>", select_dialog)
                except Exception:
                    pass

    def set_buttons(self, count):
        """Rebuilds the button row, then re-binds the new buttons."""
        super().set_buttons(count)
        self._bind_own_parts_to_self()

    def winfo_children(self):
        """
        Hides this widget's OWN parts from the Designer's binding pass.

        pygubu walks winfo_children() binding a click handler to everything it
        finds, and that handler resolves the clicked widget through
        builder.get_widget_id(). The heading label and the three buttons are
        built by the dialog, not by the builder, so they are not in its map:
        clicking one resolved to None and selected nothing.

        Returning only the content area means pygubu binds the dialog itself
        and whatever the user put inside it. The dialog's own parts are bound
        separately, in _bind_own_parts_to_self() -- and because they are not in
        this list, pygubu's pass does not visit them and cannot overwrite those
        bindings.
        """
        children = super(tk.Frame, self).winfo_children()
        content = getattr(self, "contentFrame", None)
        if content is None:
            return children

        # Keep the internal canvas: it IS the dialog's visible background, so
        # dropping it stopped a click on empty space selecting anything.
        # Everything else the dialog builds for itself is excluded.
        own_parts = {getattr(self, name, None) for name in (
            "titleFrame", "actionFrame", "heading_Label",
            "apply_Button", "cancel_Button", "reset_Button")}
        keep = [w for w in children if w not in own_parts]
        if content not in keep:
            keep.append(content)
        return keep


class sCTkSegmentedButtonForPreviewBO(sCTkSegmentedButtonBO):
    class_ = sCTkSegmentedButtonForPreview


class sCTkRadioButtonForPreviewBO(sCTkRadioButtonBO):
    class_ = sCTkRadioButtonForPreview


class sCTkTabviewForPreviewBO(sCTkTabviewBO):
    class_ = sCTkTabviewForPreview


class sCTkSelectorForPreviewBO(sCTkSelectorBO):
    class_ = sCTkSelectorForPreview


class sCTkSeparatorForPreviewBO(sCTkSeparatorBuilder):
    class_ = sCTkSeparatorForPreview


class sCTkDialContinuousForPreviewBO(sCTkDialContinuousBO):
    class_ = sCTkDialContinuousForPreview


class sCTkDialRangeForPreviewBO(sCTkDialRangeBO):
    class_ = sCTkDialRangeForPreview


class sCTkDialSelectorForPreviewBO(sCTkDialSelectorBO):
    class_ = sCTkDialSelectorForPreview


class sCTkDialogForPreviewBO(sCTkDialogBO):
    class_ = sCTkDialogForPreview

    def realize(self, parent, extra_init_args: dict = None):
        """
        Builds the preview WITHOUT the window properties.

        sCTkDialogBO.realize() passes title/width/height/modal and the
        offsets to the constructor. With _MAKE_WINDOW False there is no
        toplevel to receive them, and modal=True in particular must not reach
        anything -- so they are dropped rather than passed and ignored.
        """
        master = parent.get_child_master() if hasattr(parent, "get_child_master") else parent
        self.widget = self.class_(master)
        return self.widget


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
        """
        Applies a property to the preview.

        appearance_mode and color_theme are global CustomTkinter settings
        rather than widget options, so they are routed to the module-level
        setters instead of reaching the widget.

        FIX: both setters are guarded against an empty value. Blanking a
        property in the Designer inspector makes pygubu call
        unset_property(), which resolves the property's default -- None here,
        since these have no widget-level default to read back -- and passes
        it straight through. CustomTkinter's set_appearance_mode() then does
        mode_string.lower() and raises AttributeError on NoneType, taking out
        the whole preview update. CustomTkinter's own CTkPreviewBO has the
        same unguarded code and the same crash.

        The two are guarded DIFFERENTLY, on purpose.

        appearance_mode falls back to "System", which is a real state --
        CustomTkinter's own default, meaning "follow the OS". A user who
        picks Dark, then Light, then wants the system to decide again needs a
        way back, and clearing the field is that way. Ignoring the call would
        strand them on the last explicit mode, which is precisely what they
        are trying to escape. This package registers "System" as an explicit
        choice as well, so it is reachable without clearing anything --
        CustomTkinter's own property offers only blank, Light and Dark.

        color_theme has no equivalent "unset" state: CustomTkinter always
        needs some theme loaded, and reverting to "blue" would be a guess
        rather than a reversion. Blank is therefore ignored, leaving the
        current theme in place.
        """
        if pname == "appearance_mode":
            ctk.set_appearance_mode(value or "System")
        elif pname == "color_theme":
            if value:
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
        The consequence was nothing like the cause: a tk.StringVar built
        without an explicit master attaches to whichever root Tkinter
        considers default, so a variable bound to a widget in one interpreter
        was read from the other. The widget worked, the command callback fired
        with the right value, and variable.get() returned empty forever. Every
        variable-bound widget in generated code was affected -- combo boxes,
        radio buttons, switches, check boxes.

        The `or` clause above is the supported fix. pygubu's own source carries
        a FIXME beside that tuple asking plugins to implement this method
        rather than the tuple being extended.

        sCTkDialog is included for the same reason even though it is not a
        Toplevel subclass: it always BUILDS one. Without it the generated
        __main__ read

            root = tk.Tk()
            app = MyDialog(root)

        which put a small empty window on screen beside the dialog -- the
        application root, with nothing in it, because everything the design
        contains lives inside the dialog's own window. Setting `transient` made
        no difference, since the two are separate roots rather than parent and
        child.

        Note that group=GROOT on register_widget() is a DIFFERENT thing --
        palette placement only. It does not affect code generation.

        Args:
            builder_uid: The registered id being tested.

        Returns:
            True if that id names an application root.
        """
        return builder_uid in (sCTk_builder_id, sCTkToplevel_builder_id,
                               sCTkDialog_builder_id)

    def get_preview_builder(self, builder_uid: str):
        """Return a BuilderObject subclass used to build a preview
        for the target builder_uid"""

        if builder_uid == sCTkFrame_builder_id:
            return sCTkFramePreviewBO
        elif builder_uid == sCTkFrameLabeledPrimary_builder_id:
            return sCTkFrameLabeledPrimaryForPreviewBO
        elif builder_uid == sCTkFrameLabeledSecondary_builder_id:
            return sCTkFrameLabeledSecondaryForPreviewBO
        elif builder_uid == sCTkScrollableFrame_builder_id:
            return sCTkScrollableFrameForPreviewBO
        elif builder_uid == sCTkFileExplorer_builder_id:
            return sCTkFileExplorerForPreviewBO
        elif builder_uid == sCTkPathChooser_builder_id:
            return sCTkPathChooserForPreviewBO
        elif builder_uid == sCTkTableview_builder_id:
            return sCTkTableviewForPreviewBO
        elif builder_uid == sCTkSegmentedButton_builder_id:
            return sCTkSegmentedButtonForPreviewBO
        elif builder_uid == sCTkRadioButton_builder_id:
            return sCTkRadioButtonForPreviewBO
        elif builder_uid == sCTkTabview_builder_id:
            return sCTkTabviewForPreviewBO
        elif builder_uid == sCTkSelector_builder_id:
            return sCTkSelectorForPreviewBO
        elif builder_uid == sCTkSeparator_builder_id:
            return sCTkSeparatorForPreviewBO
        elif builder_uid == sCTkDialContinuous_builder_id:
            return sCTkDialContinuousForPreviewBO
        elif builder_uid == sCTkDialRange_builder_id:
            return sCTkDialRangeForPreviewBO
        elif builder_uid == sCTkDialSelector_builder_id:
            return sCTkDialSelectorForPreviewBO
        elif builder_uid == sCTkDialog_builder_id:
            return sCTkDialogForPreviewBO
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

        def on_root_created(root):
            builder.image_cache = StockImageCache(root, StockImage.registry)

        if builder_uid in toplevel_uids:
            builder.on_first_object = on_root_created
            return builder.get_object(widget_id)

        # sCTkDialog is not a toplevel, but it BUILDS one -- it always creates
        # its own sCTkDialogToplevel and packs itself into it.
        #
        # Returning None here let pygubu fall back to creating a host window of
        # its own, and that fallback constructs through the ordinary builder
        # object rather than the preview one -- so _MAKE_WINDOW = False never
        # applied, the real widget built its own window, and the result was TWO
        # windows: an empty host, and the dialog beside it.
        #
        # Handing back the dialog's own window instead means no host is created
        # and you preview the real thing, correctly sized and placed.
        if builder_uid == sCTkDialog_builder_id:
            builder.on_first_object = on_root_created
            widget = builder.get_object(widget_id)
            window = getattr(widget, "dialog_toplevel", None)
            if window is not None:
                return window
            # _MAKE_WINDOW was False, so there is no window of its own; fall
            # back to whatever it was built inside.
            return widget.winfo_toplevel()

        return None

    def ensure_visibility_in_preview(self, builder, selected_uid: str):
        """
        Switches the canvas to whichever tab holds the selected widget.

        Selecting a tab in the widget tree previously did nothing visible: the
        canvas stayed on the tab it was already showing, so the selection
        outline was drawn around a widget that is not mapped -- which collapses
        to a small square near the origin. Selecting something INSIDE another
        tab had the same problem, and together they made the tree and the canvas
        disagree with no way to reconcile them.

        This is the hook for the tree-to-canvas direction, and this plugin
        simply never implemented it. Modelled on CustomTkinter's own, which
        does the same for its CTkTabview.

        Both tab class names are searched. Tabs may be registered as this
        library's own type or, where that registration is commented out,
        inherited from CustomTkinter -- and a .ui file written under either is
        still valid.

        Args:
            builder: The preview builder, giving access to the parsed .ui and
                the realized objects.
            selected_uid: The id of the widget selected in the tree.
        """
        tab_classes = ("scustomtkinter.sCTkTabviewTab",
                       "scustomtkinter.sCTkTabview.Tab",
                       "customtkinter.CTkTabviewTab")

        tabs = []
        for class_name in tab_classes:
            found = builder.uidefinition.root.findall(
                f".//object[@class='{class_name}']")
            if found:
                tabs.extend(found)
        if not tabs:
            return

        for tab in tabs:
            tab_id = tab.get("id")
            if tab_id is None:
                continue

            # The tab itself, or anything nested inside it.
            activate = tab_id == selected_uid
            if not activate:
                activate = tab.find(f".//object[@id='{selected_uid}']") is not None
            if not activate:
                continue

            tab_builder = builder.objects.get(tab_id)
            if tab_builder is None or tab_builder.widget is None:
                return
            try:
                top = tab_builder.widget.winfo_toplevel()
                tabview = top.nametowidget(tab_builder.widget.winfo_parent())
                tabname = tab_builder.wmeta.properties.get("label")
                if tabname and tabview.get() != tabname:
                    tabview.set(tabname)
                    top.update()
            except Exception:
                # A tab that is not realized yet, or a parent that is not the
                # tabview. Failing to switch is a cosmetic loss; raising here
                # would break selection entirely.
                pass
            return

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
            # The dial's OWN canvas, not _preview_canvas()'s answer.
            #
            # A dial has TWO canvases: CTkFrame's background `_canvas`, and
            # `canvas`, which the dial creates and draws itself on.
            # _preview_canvas() returns _canvas first -- and that is where
            # CTkFrame.bind() puts the DESIGNER's click handler. Neutralizing
            # <Button-1> there removed the selection binding itself, so a dial
            # could not be selected on the canvas at all.
            #
            # The interactive bindings that need silencing are on the dial's
            # own canvas. _canvas keeps its handler.
            face = getattr(widget, "canvas", None)

            # Everything EXCEPT <Button-1> is neutralized outright.
            sequences = tuple(s for s in (_HOVER_CLICK + _DIAL_EXTRA + _SCROLL)
                              if s != "<Button-1>")
            _neutralize(face, sequences)
            _neutralize(widget, _SCROLL)

            # <Button-1> is FORWARDED rather than swallowed.
            #
            # A no-op would stop the click at the dial face, so it never
            # reaches _canvas -- where CTkFrame.bind() puts the Designer's own
            # selection handler. The dial would stay unselectable, which is
            # what "the dial captures the click" looked like.
            #
            # Done here rather than in the preview class because this function
            # runs afterwards and would otherwise replace that binding.
            if face is not None:
                def _select_dial(event, target=widget):
                    try:
                        bg = getattr(target, "_canvas", None)
                        if bg is not None:
                            bg.event_generate("<Button-1>", x=1, y=1, when="now")
                    except Exception:
                        pass
                    return "break"
                try:
                    face.bind("<Button-1>", _select_dial)
                except Exception:
                    pass

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