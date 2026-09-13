#!/usr/bin/python3
"""
sCTkToplevel

A theme-compliant top-level window wrapper, for secondary windows, modal
dialogs, and popups. Inherits directly from ctk.CTkToplevel so CustomTkinter
handles native window management; this class layers automatic light/dark
theme resolution on top.

Base class order matters here: `class sCTkToplevel(ctk.CTkToplevel,
ThemeableWidget)` puts the native CTk class first, so every `super()` call in
this file's own methods resolves to ctk.CTkToplevel -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring).

This is the simplest widget in this project's audit so far: no disabled
state, no state()/get_state() at all, and no per-state color-swapping logic.
A top-level window has no interactive "enabled/disabled" concept the way a
control does, and its theme block (see sCTkThemes.json) defines only
fg_color -- nothing else.
"""
from typing import Any, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkToplevel(ctk.CTkToplevel, ThemeableWidget):
    """Themeable top-level window.

    Adds to native ctk.CTkToplevel:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - Positional-dict support in configure(), e.g.
        toplevel.configure({"fg_color": "red"}) -- merged into keyword
        arguments and applied normally.

    Single-argument property queries go to ThemeableWidget's shared
    _configure_query(), like every other widget. This class ignored them
    until recently, which mattered as soon as sCTkToplevel was registered
    with the Designer: blanking a field there reads the property's default
    first, and an unanswered query returns None, which pygubu then applies.

    There is still no state()/get_state() and no per-state colour swapping.
    A window has no enabled/disabled concept, and nothing in this class
    reapplies colours after construction -- which is also why it needs no
    override recording: with no repaint to revert them, a runtime change
    simply stays.

    WHITELIST GUARD: if a composite widget inherits sCTkToplevel as its own
    base class and explicitly calls ThemeableWidget.__init__ itself before
    calling super().__init__(), that composite's own final_kw could contain
    keys native ctk.CTkToplevel knows nothing about. This matters MORE here
    than for most widgets: CTkToplevel's own __init__ explicitly calls
    check_kwargs_empty(kwargs, raise_error=True) after popping its known-valid
    keys, confirmed directly against CustomTkinter's own source -- meaning ANY
    unrecognized keyword reaching it is GUARANTEED to raise, not just
    incidentally likely to. _NATIVE_CTKTOPLEVEL_KWARGS filters final_kw down
    to only the keys the real native constructor accepts before that call.
    This only matters for the Pattern-B composition scenario described above;
    for direct construction of a plain sCTkToplevel, final_kw already only
    contains this widget's own theme keys (just fg_color), so the filter is a
    no-op.
    """

    # Confirmed directly against CustomTkinter's own ctk_toplevel.py source:
    # CTkToplevel's own _valid_tk_toplevel_arguments set, plus fg_color as the
    # one CTk-specific parameter defined separately in its __init__ signature.
    # "master" is excluded here since it's always passed positionally, never
    # part of the filtered kwargs dict.
    _NATIVE_CTKTOPLEVEL_KWARGS = frozenset({
        "bd", "borderwidth", "class", "container", "cursor", "height",
        "highlightbackground", "highlightthickness", "menu", "relief",
        "screen", "takefocus", "use", "visual", "width", "fg_color",
    })

    def __init__(self, master: Optional[Any] = None, **kwargs: Any) -> None:
        """
        Args:
            master: Parent window.
            **kwargs: Any native CTkToplevel argument, or an fg_color override
                (see the "sCTkToplevel" block in sCTkThemes.json, which
                currently defines only fg_color).
        """
        # 1. Fire our shared theme logic first. This resolves final_kw
        # (construction-time properties). See ThemeableWidget.__init__ for
        # what actually happens here.
        ThemeableWidget.__init__(self, kwargs)
        self._local_defaults = dict(self.final_kw)

        # 2. Initialize CustomTkinter's native top-level window. Only forwards
        # the subset of final_kw that native CTkToplevel actually accepts --
        # see this class's docstring ("WHITELIST GUARD") for why this
        # filtering exists.
        native_kwargs = {k: v for k, v in self.final_kw.items() if k in self._NATIVE_CTKTOPLEVEL_KWARGS}
        super().__init__(master, **native_kwargs)

        # 3. Register lifecycle handshake hook, notifying Pygubu-style consumers
        # that construction is complete.
        self._finalize_themeable_lifecycle()

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with positional-dict support.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally.
                - a property name: returns a Tkinter-style
                  (name, name, name, default, current) tuple from the shared
                  query helper.
            **kwargs: Standard CTkToplevel configuration options.

        Returns:
            The query tuple for the single-argument case, otherwise whatever
            super().configure() returns.
        """
        # args is always a tuple, never a dict itself -- args[0] is the actual
        # dict if one was passed. An earlier version checked
        # `isinstance(args, dict)` directly on the tuple, which can never be
        # true; that dict-merge path was unreachable. Fixed here to check
        # args[0] instead.
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                # The single-argument query, which this widget used to ignore.
                #
                # Pygubu calls configure(name) to read a property's default
                # whenever a field is blanked in the inspector. Falling through
                # to the native configure() does not answer that: CustomTkinter
                # declares configure(self, require_redraw=False, **kwargs), so
                # the property NAME arrives as require_redraw and the call
                # returns None -- which pygubu then applies.
                #
                # _configure_query() is the shared helper every other widget
                # uses; this one simply never called it.
                return self._configure_query(args[0])

        if kwargs:
            # RETURNED, not discarded. The docstring noted this was preserved
            # as-is from an earlier version; a caller reading the result got
            # None whatever the native widget said.
            return super().configure(**kwargs)
        return None

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. Without this line, calling .config(...) on an instance
    # would silently skip this entire override and land on the native widget's
    # configure() directly.
    config = configure