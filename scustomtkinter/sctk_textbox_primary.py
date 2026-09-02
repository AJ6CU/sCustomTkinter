#!/usr/bin/python3
"""
sCTkTextboxPrimary

A theme-compliant, high-emphasis multi-line text area widget -- the more
prominent of the library's two textbox tiers (see also sCTkTextboxSecondary).
Inherits directly from ctk.CTkTextbox so CustomTkinter handles native
rendering and text editing; this class layers automatic light/dark theme
resolution and a distinct enabled/disabled visual state on top.

Base class order matters here: `class sCTkTextboxPrimary(ctk.CTkTextbox,
ThemeableWidget)` puts the native CTk class first, so every `super()` call in
this file's own methods resolves to ctk.CTkTextbox -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring); this widget owns all of
its own runtime color-swapping logic.

Disabling uses CTk's native state="disabled", consistent with every other
widget in this library confirmed to correctly block interaction this way.
"""
import os
import sys
import platform
from typing import Any, Optional
import tkinter as tk
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkTextboxPrimary(ctk.CTkTextbox, ThemeableWidget):
    """Themeable, high-emphasis multi-line text area.

    Adds to native ctk.CTkTextbox:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A distinct enabled/disabled visual state, using CTk's native
        state="disabled".
      - Pygubu Designer property introspection for `state`, `fg_color`,
        `text_color`, `border_color`, `scrollbar_button_color`, and
        `scrollbar_button_hover_color` via a single-argument configure() call.
      - A transparency fallback: if fg_color resolves to "transparent" or
        empty at construction, the widget copies its parent's fg_color
        instead. Presumably a workaround for CTkTextbox not rendering true
        transparency the way canvas-based widgets can; preserved as-is, not
        independently re-verified as part of this project's audit.
      - Manual scrollbar re-theming: CTkTextbox's internal scrollbar isn't
        automatically covered by this widget's own theme keys, so
        scrollbar_button_color/scrollbar_button_hover_color are pushed to it
        directly whenever colors are recomputed.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox, sCTkSegmentedButton, and the button
    family. Not separately re-confirmed for this specific widget.

    scrollbar_button_color and scrollbar_button_hover_color are required to be
    present in whichever map is active for the scrollbar re-theming step below
    -- if either is missing, this raises immediately rather than substituting
    a hardcoded color. An earlier version used hardcoded hex fallbacks here,
    several of which didn't even match the real theme file's actual values;
    per this project's design, ThemeableWidget-based widgets are meant to fail
    hard on incomplete theme data (see sCTkLabelPrimary/Secondary/Tertiary for
    the precedent this follows).
    """

    def __init__(self, master: Optional[Any] = None, **kw: Any) -> None:
        """
        Args:
            master: Parent container.
            **kw: `state` is pulled out explicitly below (applied after
                construction, via self.state(), rather than passed to the
                native constructor). Everything else is either a native
                CTkTextbox argument or a theme-key override (see the
                "sCTkTextboxPrimary" block in sCTkThemes.json).
        """
        # 1. Fire our shared theme logic. This resolves final_kw
        # (construction-time properties) and the disabled color map. See
        # ThemeableWidget.__init__ for what actually happens here.
        ThemeableWidget.__init__(self, kw)

        # 2. Store the resolved maps onto this instance. Note: unlike most
        # other widgets in this project, these are NOT deep-copied (dict(...))
        # here -- they reference the same dict objects final_kw/
        # _widget_disabled_map point to. Preserved as-is from the original;
        # this only matters if something elsewhere mutates those dicts after
        # construction, which doesn't currently happen anywhere in this file.
        self._local_defaults = self.final_kw
        self._custom_disabled_map = self._widget_disabled_map

        # Extract "state" from final_kw after ThemeableWidget's merge -- an
        # explicit state= kwarg correctly overrides any "state" the theme
        # JSON might define at the top level.
        state_init = self.final_kw.pop("state", "normal")

        # 3. Initialize CustomTkinter natively with the clean final kwargs array.
        super().__init__(master, **self.final_kw)

        # Transparency fallback -- see this class's docstring.
        try:
            current_fg = super().cget("fg_color")
            if current_fg in ("transparent", ""):
                parent_bg = self.master.cget("fg_color")
                if parent_bg not in ("transparent", ""):
                    super().configure(fg_color=parent_bg)
        except Exception:
            pass

        # 4. Apply the requested initial state now that the native widget exists.
        self._custom_current_state = "normal"
        self.state(state_init)

        # 5. Register lifecycle handshake hook, notifying Pygubu-style consumers
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

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally below.
                - the literal string "state": returns a Tkinter-style
                  (name, name, name, default, current) tuple.
                - one of "fg_color"/"text_color"/"border_color"/
                  "scrollbar_button_color"/"scrollbar_button_hover_color":
                  returns the same style of tuple. Note the returned value is
                  str(value), where value may itself be a (light, dark) tuple
                  rather than a single resolved color -- a known limitation
                  shared with the wider Pygubu-query investigation set aside
                  elsewhere in this project, not fixed here.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties (same limitation).
            **kwargs: Standard CTkTextbox configuration options, plus: passing
                `state=...` updates self._custom_current_state and triggers a
                repaint, rather than being forwarded as-is.

        Returns:
            The query tuple described above for the single-argument case, or
            whatever super().configure() returns for the keyword-argument case
            (typically None).
        """
        # args is always a tuple -- args[0] is the actual value passed, whether
        # that's a string or a dict. An earlier version of this method compared
        # the wrapped tuple directly (`pname = args`) and forwarded it unwrapped
        # to super().configure(), which is not a valid call shape for the
        # native widget. Don't reintroduce that.
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname == "state":
                    return ("state", "state", "state", "normal", str(self.state()))

                if pname in ["fg_color", "text_color", "border_color", "scrollbar_button_color",
                             "scrollbar_button_hover_color"]:
                    val = self._custom_disabled_map.get(pname) if self._custom_current_state == "disabled" else self._local_defaults.get(pname)
                    return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

                return super().configure(pname)

        if "state" in kwargs:
            self._custom_current_state = str(kwargs.pop("state")).lower()
            self._update_current_visual_state()

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

    def state(self, state_string: Optional[str] = None) -> str:
        """
        Gets or sets the widget's enabled/disabled visual state.

        Args:
            state_string: If given, forwarded to configure(state=state_string).
                If None, no change is made.

        Returns:
            The current state string (whatever was last set, or "normal" by
            default).
        """
        if state_string is not None:
            self.configure(state=state_string)
        return getattr(self, "_custom_current_state", "normal")

    def _update_current_visual_state(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, based
        on the current state, then sets the native interactive lock, then
        re-themes the internal scrollbar.

        Called on every state()/configure(state=...) change.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.

        scrollbar_button_color and scrollbar_button_hover_color are required
        to be present in whichever map is active -- see this class's
        docstring.
        """
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "border_color", "text_color", "scrollbar_button_color", "scrollbar_button_hover_color"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = val

        if config_payload:
            super().configure(**config_payload)

        if is_disabled:
            super().configure(state="disabled")
        else:
            super().configure(state="normal")

        # Re-theme the internal scrollbar, which isn't automatically covered
        # by the configure() call above.
        if hasattr(self, "_scrollbar") and self._scrollbar:
            try:
                if target_map.get("scrollbar_button_color") is None:
                    raise KeyError(
                        f"'{self.__class__.__name__}' theme block is missing "
                        f"'scrollbar_button_color' in its "
                        f"{'disabled_map' if is_disabled else 'top-level'} section."
                    )
                if is_disabled:
                    bar_color = target_map.get("scrollbar_button_color")
                    self._scrollbar.configure(button_color=bar_color, button_hover_color=bar_color)
                else:
                    if target_map.get("scrollbar_button_hover_color") is None:
                        raise KeyError(
                            f"'{self.__class__.__name__}' theme block is missing "
                            f"'scrollbar_button_hover_color' at the top level."
                        )
                    self._scrollbar.configure(
                        button_color=target_map.get("scrollbar_button_color"),
                        button_hover_color=target_map.get("scrollbar_button_hover_color"),
                    )

                if hasattr(self._scrollbar, "_draw"):
                    self._scrollbar._draw()
            except KeyError:
                raise
            except Exception:
                pass
