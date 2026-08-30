#!/usr/bin/python3
"""
sCTkCheckBox

A theme-compliant binary selection checkbox widget. Inherits directly from
ctk.CTkCheckBox so CustomTkinter handles native rendering, click toggling, and
input locking; this class layers automatic light/dark theme resolution and a
distinct enabled/disabled visual state on top.

Base class order matters here: `class sCTkCheckBox(ctk.CTkCheckBox,
ThemeableWidget)` puts the native CTk class first, so every `super()` call in
this file's own methods resolves to ctk.CTkCheckBox -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring); this widget owns all of
its own runtime color-swapping logic.
"""
from typing import Any, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkCheckBox(ctk.CTkCheckBox, ThemeableWidget):
    """Themeable checkbox.

    Adds to native ctk.CTkCheckBox:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A distinct enabled/disabled visual state, tracked in
        self._custom_current_state and swapped via _update_current_visual_state().
      - Pygubu Designer property introspection for a handful of properties via
        a single-argument configure() call.

    Every color this widget applies, including the checkmark itself, comes
    from sCTkThemes.json -- checkmark_color was added as a real theme key
    during this project's audit; previously the theme block didn't define it
    at all, so the checkmark silently always used CTkCheckBox's native default
    regardless of theme.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking should repaint them automatically on a light/dark switch -- the
    same approach validated on sCTkComboBox, sCTkSegmentedButton, and
    sCTkButtonPrimary. Not separately re-confirmed for this specific widget.

    Unlike the button family, this widget already used CTk's native
    state="disabled"/state="normal" rather than manual event unbinding, so its
    click-blocking was never suspected to be broken the way the buttons' was.
    The color-then-state call order was reversed during this audit (state is
    now set first, colors reapplied second via after_idle) as a precaution
    based on a race condition confirmed on sCTkButtonPrimary between CTk's own
    state-change repaint and an immediately-following manual color update --
    this specific reordering has not been independently confirmed necessary
    for this widget, only carried over as a defensive measure.
    """

    def __init__(self, master: Optional[Any] = None, **kw: Any) -> None:
        """
        Args:
            master: Parent container.
            **kw: Any native CTkCheckBox argument, or a theme-key override
                (see the "sCTkCheckBox" block in sCTkThemes.json, including its
                disabled_map sub-block).
        """
        # 1. Fire our shared theme logic first. This resolves final_kw
        # (construction-time properties) and the disabled color map. See
        # ThemeableWidget.__init__ for what actually happens here.
        ThemeableWidget.__init__(self, kw)

        # 2. Deep-copy the resolved map onto this instance, so later changes
        # here never leak back into the shared theme registry.
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 3. Initialize CustomTkinter natively with the clean final kwargs array.
        super().__init__(master, **self.final_kw)
        self._custom_current_state = "normal"

        # 4. Register lifecycle handshake hook, notifying Pygubu-style consumers
        # that construction is complete.
        self._finalize_themeable_lifecycle()

    def _set_appearance_mode(self, mode_string: str) -> None:
        """
        Forwards CustomTkinter's internal light/dark mode change notification to
        the native widget.

        No longer manually re-triggers _update_current_visual_state(). That
        method now passes raw (light, dark) tuples straight through to
        configure() instead of pre-resolving to a single color, so CTk's own
        appearance-mode tracking should repaint correctly on its own -- the
        same approach validated on sCTkComboBox, sCTkSegmentedButton, and
        sCTkButtonPrimary.

        Args:
            mode_string: The new appearance mode ("Light" or "Dark"), as passed
                by CustomTkinter's internal appearance-mode change machinery.
        """
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally below.
                - the literal string "state": returns a Tkinter-style
                  (name, name, name, default, current) tuple.
                - one of "fg_color"/"border_color"/"text_color"/"hover_color"/
                  "checkmark_color": returns the same style of tuple, with
                  `current` reflecting the disabled or normal value as
                  appropriate. Note the returned value is str(value), where
                  value may itself be a (light, dark) tuple rather than a
                  single resolved color -- a known limitation shared with the
                  wider Pygubu-query investigation set aside elsewhere in this
                  project, not fixed here.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties (same limitation).
            **kwargs: Standard CTkCheckBox configuration options, plus: passing
                `state=...` routes through self.state() rather than being
                forwarded as-is.

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

                if pname in ["fg_color", "border_color", "text_color", "hover_color", "checkmark_color"]:
                    current_state = str(self.state()).lower()
                    val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                    return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

                return super().configure(pname)

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        if kwargs:
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

    def get_state(self) -> str:
        """Equivalent to calling state() with no argument."""
        return self.state()

    def state(self, mode: Optional[str] = None) -> str:
        """
        Gets or sets the widget's enabled/disabled state.

        Args:
            mode: If None, returns the current state without changing anything.
                Otherwise, only the literal string "disabled" (case-insensitive)
                is treated as disabled; anything in ("normal", "enabled",
                "active") is treated as enabled. Any other value falls through
                without matching either branch, leaving the state unchanged.

        Returns:
            The resulting state ("normal" or "disabled", lowercase). An
            earlier version of this method didn't return anything when setting
            a mode (only the query branch returned a value) -- fixed here for
            consistency with every other themed widget's state().
        """
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
        elif mode == "disabled":
            self._custom_current_state = "disabled"

        self._update_current_visual_state()
        return self._custom_current_state

    def _update_current_visual_state(self) -> None:
        """
        Sets the native enabled/disabled flag, then recomputes and applies
        this widget's colors from the theme file, deferred via after_idle.

        Called after every state() change.

        Native state is set FIRST, colors reapplied SECOND via after_idle --
        this order is a precaution, not a confirmed fix for this widget
        specifically. On sCTkButtonPrimary, an immediate color reapply
        following a state change was found to lose a race against CTk's own
        internal state-change repaint, leaving stale colors after repeated
        disable/enable cycles. That fix is carried over here defensively;
        see this class's docstring.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.
        Every value here traces back to sCTkThemes.json; there are no
        hardcoded colors in this method.
        """
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"

        super().configure(state="disabled" if is_disabled else "normal")
        self.after_idle(self._apply_theme_colors)

    def _apply_theme_colors(self) -> None:
        """
        Applies fg_color, border_color, hover_color, text_color,
        checkmark_color, border_width, and font from whichever theme map
        matches the current state. Called only via after_idle from
        _update_current_visual_state() -- see that method for why the
        deferral exists.
        """
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "border_color", "hover_color", "text_color", "checkmark_color", "border_width", "font"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = val

        if config_payload:
            super().configure(**config_payload)
