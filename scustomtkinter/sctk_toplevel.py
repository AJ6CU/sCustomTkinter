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

    Unlike every other widget in this project, there's no single-argument
    property query support here (no "state" or color-tuple special-casing) --
    a bare positional string like configure("fg_color") is not intercepted
    and currently has no effect at all, since the only positional-argument
    handling implemented is the dict-merge case. Consistent with this
    widget's overall minimalism; add single-argument passthrough
    (`return super().configure(pname)`) here if Pygubu-style introspection is
    ever needed for top-level windows specifically.
    """

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

        # 2. Initialize CustomTkinter's native top-level window.
        super().__init__(master, **self.final_kw)

        # 3. Register lifecycle handshake hook, notifying Pygubu-style consumers
        # that construction is complete.
        self._finalize_themeable_lifecycle()

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with positional-dict support.

        Args:
            *args: At most one positional argument is meaningful: a dict,
                merged into kwargs and processed normally. Any other single
                positional value (e.g. a property-name string) is currently
                not handled at all -- see this class's docstring.
            **kwargs: Standard CTkToplevel configuration options.

        Returns:
            Whatever super().configure() returns (typically None). Note this
            method doesn't explicitly `return` that value -- preserved as-is
            from the original.
        """
        # args is always a tuple, never a dict itself -- args[0] is the actual
        # dict if one was passed. An earlier version checked
        # `isinstance(args, dict)` directly on the tuple, which can never be
        # true; that dict-merge path was unreachable. Fixed here to check
        # args[0] instead.
        if len(args) == 1 and isinstance(args[0], dict):
            kwargs = {**args[0], **kwargs}

        if kwargs:
            super().configure(**kwargs)

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. Without this line, calling .config(...) on an instance
    # would silently skip this entire override and land on the native widget's
    # configure() directly.
    config = configure
