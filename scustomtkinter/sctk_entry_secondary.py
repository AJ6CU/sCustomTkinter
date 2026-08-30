#!/usr/bin/python3
"""
sCTkEntrySecondary

A theme-compliant, lower-emphasis single-line text entry widget (see also
sCTkEntryPrimary). Inherits directly from ctk.CTkEntry so CustomTkinter
handles native rendering and text editing; this class layers automatic
light/dark theme resolution and a distinct enabled/disabled visual state on
top.

Base class order matters here: `class sCTkEntrySecondary(ctk.CTkEntry,
ThemeableWidget)` puts the native CTk class first, so every `super()` call in
this file's own methods resolves to ctk.CTkEntry -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring); this widget owns all of
its own runtime color-swapping logic.

IMPORTANT: disabling uses CTk's native state="disabled" -- confirmed correct
by direct testing, matching every other widget in this library. See
sCTkEntryPrimary's module docstring for the fuller history (an earlier version
used native "readonly" on an unverified claim; tested and found unnecessary).
"""
from typing import Any, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkEntrySecondary(ctk.CTkEntry, ThemeableWidget):
    """Themeable, lower-emphasis text entry field.

    Adds to native ctk.CTkEntry:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A distinct enabled/disabled visual state, using CTk's native
        state="disabled" (confirmed correct by direct testing).
      - Pygubu Designer property introspection for `state`, `fg_color`,
        `text_color`, `border_color`, and `placeholder_text_color` via a
        single-argument configure() call.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox, sCTkSegmentedButton, and the button
    family. Not separately re-confirmed for this specific widget.

    placeholder_text_color is a real, themed key (not a fallback to
    text_color) -- see sCTkEntryPrimary's docstring for the full rationale.
    CTkEntry has no separate font for placeholder text vs. typed text -- both
    always share the single `font` property; that's a ceiling in the
    underlying widget, not a gap in this theme file.
    """

    def __init__(self, master: Optional[Any] = None, **kw: Any) -> None:
        """
        Args:
            master: Parent container.
            **kw: Any native CTkEntry argument (e.g. `placeholder_text`,
                `width`), or a theme-key override (see the "sCTkEntrySecondary"
                block in sCTkThemes.json, including its disabled_map).
        """
        # 1. Fire our shared theme logic first. This resolves final_kw
        # (construction-time properties) and the disabled color map. See
        # ThemeableWidget.__init__ for what actually happens here.
        ThemeableWidget.__init__(self, kw)

        # 2. Deep-copy the resolved map onto this instance, so later changes
        # here never leak back into the shared theme registry.
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # Extract "state" from final_kw after ThemeableWidget's merge -- an
        # explicit state= kwarg correctly overrides any "state" the theme
        # JSON might define at the top level.
        state_init = self.final_kw.pop("state", "normal")

        # 3. Initialize CustomTkinter natively with the clean final kwargs array.
        super().__init__(master, **self.final_kw)

        # 4. Apply the requested initial state now that the native widget exists.
        self._custom_current_state = "normal"
        self.state(state_init)

        # 5. Register lifecycle handshake hook, notifying Pygubu-style consumers
        # that construction is complete.
        self._finalize_themeable_lifecycle()

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally below.
                - the literal string "state": returns a Tkinter-style
                  (name, name, name, default, current) tuple.
                - one of "fg_color"/"text_color"/"border_color"/
                  "placeholder_text_color": returns the same style of tuple,
                  with `current` reflecting the disabled or normal value as
                  appropriate. Note the returned value is str(value), where
                  value may itself be a (light, dark) tuple rather than a
                  single resolved color -- a known limitation shared with the
                  wider Pygubu-query investigation set aside elsewhere in this
                  project, not fixed here.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties (same limitation).
            **kwargs: Standard CTkEntry configuration options, plus: passing
                `state=...` routes through self.state() rather than being
                forwarded as-is.

        Returns:
            The query tuple described above for the single-argument case, or
            whatever super().configure() returns for the keyword-argument case
            (typically None).
        """
        # args is always a tuple -- args[0] is the actual value passed, whether
        # that's a string or a dict. An earlier version of this method compared
        # the wrapped tuple directly (`pname = args`), so the query branches
        # below never matched anything. Don't reintroduce that.
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname == "state":
                    return ("state", "state", "state", "normal", str(self.state()))

                if pname in ["fg_color", "text_color", "border_color", "placeholder_text_color"]:
                    val = self._custom_disabled_map.get(pname) if self._custom_current_state == "disabled" else self._local_defaults.get(pname)
                    return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

                return super().configure(pname)

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

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
    # configure() directly, bypassing theming and state handling entirely.
    config = configure

    def _set_appearance_mode(self, mode_string: str) -> None:
        """
        Forwards CustomTkinter's internal light/dark mode change notification to
        the native widget.

        No longer manually re-triggers _update_current_visual_state(). That
        method now passes raw (light, dark) tuples straight through to
        configure() instead of pre-resolving to a single color, so CTk's own
        appearance-mode tracking should repaint correctly on its own -- the
        same approach validated on sCTkComboBox, sCTkSegmentedButton, and the
        button family.

        Args:
            mode_string: The new appearance mode ("Light" or "Dark"), as passed
                by CustomTkinter's internal appearance-mode change machinery.
        """
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass

    def get_state(self) -> str:
        """Equivalent to calling state() with no argument."""
        return self.state()

    def state(self, state_string: Optional[str] = None) -> str:
        """
        Gets or sets the widget's enabled/disabled visual state.

        Args:
            state_string: If None, returns the current state without changing
                anything. Otherwise, only the literal string "disabled"
                (case-insensitive) is treated as disabled; anything in
                ("normal", "enabled", "active") is treated as enabled. Any
                other value leaves the internal state flag unchanged, though
                _update_current_visual_state() still runs.

        Returns:
            The resulting state ("normal" or "disabled", lowercase).
        """
        if state_string is None:
            return getattr(self, "_custom_current_state", "normal")

        mode = str(state_string).lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
        elif mode == "disabled":
            self._custom_current_state = "disabled"

        self._update_current_visual_state()
        return self._custom_current_state

    def _update_current_visual_state(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, based
        on the current state, then sets the native interactive lock.

        Called after construction and on every state() change.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.
        """
        is_disabled = self._custom_current_state == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "border_color", "text_color", "placeholder_text_color"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = val

        if config_payload:
            super().configure(**config_payload)

        # Confirmed correct by direct testing: native "disabled" properly
        # blocks interaction.
        if is_disabled:
            super().configure(state="disabled")
        else:
            super().configure(state="normal")
