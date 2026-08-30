#!/usr/bin/python3
"""
sCTkFrame

A theme-compliant container frame widget. Inherits directly from ctk.CTkFrame
so CustomTkinter handles native rendering and layout; this class layers
automatic light/dark theme resolution on top.

Base class order matters here: `class sCTkFrame(ctk.CTkFrame,
ThemeableWidget)` puts the native CTk class first, so every `super()` call in
this file's own methods resolves to ctk.CTkFrame -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring).

Unlike every other widget in this library, sCTkFrame has no disabled state and
no _update_current_visual_state() at all -- frames are containers, not
interactive controls, so there's nothing to dim or lock. Colors are set once
at construction (as raw (light, dark) tuples, via final_kw) and never touched
again; CustomTkinter's own native appearance-mode tracking handles light/dark
repaints on its own, the same underlying mechanism validated more deliberately
on sCTkComboBox, sCTkSegmentedButton, and the button family. There's also no
_set_appearance_mode() override here, for the same reason -- there's nothing
for it to re-trigger.
"""
from typing import Any, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkFrame(ctk.CTkFrame, ThemeableWidget):
    """Themeable container frame.

    Adds to native ctk.CTkFrame:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - Pygubu Designer property introspection for `state`, `fg_color`, and
        `border_color` via a single-argument configure() call.
      - A no-op state()/get_state() pair, so generic test harnesses that call
        .state() uniformly across every widget type don't crash when handed a
        Frame. This is deliberate, not a bug -- see state()'s docstring.
    """

    def __init__(self, master: Optional[Any] = None, **kwargs: Any) -> None:
        """
        Args:
            master: Parent container.
            **kwargs: Any native CTkFrame argument, or a theme-key override
                (see the "sCTkFrame" block in sCTkThemes.json). There is no
                disabled_map for this widget -- frames have no disabled state.
        """
        # 1. Fire our shared theme logic first. This resolves final_kw
        # (construction-time properties). See ThemeableWidget.__init__ for
        # what actually happens here.
        ThemeableWidget.__init__(self, kwargs)

        # 2. Deep-copy the resolved kwargs onto this instance, so later
        # changes here never leak back into the shared theme registry.
        self._local_defaults = dict(self.final_kw)

        # 3. Initialize CustomTkinter natively with the clean final kwargs array.
        super().__init__(master, **self.final_kw)

        # 4. Register lifecycle handshake hook, notifying Pygubu-style consumers
        # that construction is complete.
        self._finalize_themeable_lifecycle()

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally below.
                - the literal string "state": returns a Tkinter-style
                  (name, name, name, default, current) tuple. Since frames
                  have no real state, `default` and `current` are always the
                  same value: "normal".
                - "fg_color" or "border_color": returns the same style of
                  tuple. Since these never vary by state for a frame,
                  `default` and `current` are always identical here too.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties -- a known limitation
                  shared with the wider Pygubu-query investigation set aside
                  elsewhere in this project.
            **kwargs: Standard CTkFrame configuration options, plus: passing
                `state=...` is silently absorbed via self.state() (a no-op)
                rather than forwarded to the native widget, which has no real
                concept of "state" to configure in the first place.

        Returns:
            The query tuple described above for the single-argument case, or
            whatever super().configure() returns for the keyword-argument case
            (typically None).
        """
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname == "state":
                    return ("state", "state", "state", "normal", str(self.state()))
                if pname in ["fg_color", "border_color"]:
                    val = self._local_defaults.get(pname)
                    return (pname, pname, pname, str(val), str(val))
                return super().configure(pname)

        # Absorbs "state" so generic test harnesses that call
        # configure(state=...) uniformly across widget types don't raise on a
        # Frame, which has no native "state" option.
        if "state" in kwargs:
            target_state = kwargs.pop("state")
            self.state(target_state)

        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        if kwargs:
            return super().configure(**kwargs)
        return None

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. Without this line, calling .config(...) on an instance
    # would silently skip this entire override and land on the native widget's
    # configure() directly.
    config = configure

    def get_state(self) -> str:
        """Equivalent to calling state() with no argument. Always returns "normal"."""
        return self.state()

    def state(self, mode: Optional[str] = None) -> str:
        """
        No-op state controller. Frames have no disabled concept -- this exists
        purely so code written generically against every widget's state()/
        get_state()/configure(state=...) API doesn't need a special case for
        Frame. Whatever `mode` is passed, it's ignored and never stored.

        Args:
            mode: Ignored entirely.

        Returns:
            Always "normal".
        """
        return "normal"
