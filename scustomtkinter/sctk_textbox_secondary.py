#!/usr/bin/python3
"""
sCTkTextboxSecondary

A theme-compliant, lower-emphasis multi-line text area widget (see also
sCTkTextboxPrimary). Inherits directly from ctk.CTkTextbox so CustomTkinter
handles native rendering and text editing; this class layers automatic
light/dark theme resolution and a distinct enabled/disabled visual state on
top.

Base class order matters here: `class sCTkTextboxSecondary(ctk.CTkTextbox,
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


class sCTkTextboxSecondary(ctk.CTkTextbox, ThemeableWidget):
    """Themeable, lower-emphasis multi-line text area.

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
        instead. Same rationale as sCTkTextboxPrimary's identical fallback.
      - Manual scrollbar re-theming, same as sCTkTextboxPrimary.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox, sCTkSegmentedButton, and the button
    family. Not separately re-confirmed for this specific widget.

    scrollbar_button_color and scrollbar_button_hover_color are required to be
    present in whichever map is active for the scrollbar re-theming step below
    -- if either is missing, this raises immediately rather than substituting
    a hardcoded color. See sCTkTextboxPrimary's docstring for the full
    rationale.
    """

    def __init__(self, master: Optional[Any] = None, **kw: Any) -> None:
        """
        Args:
            master: Parent container.
            **kw: `state` is pulled out explicitly below. Everything else is
                either a native CTkTextbox argument or a theme-key override
                (see the "sCTkTextboxSecondary" block in sCTkThemes.json).
        """
        # 1. Fire our shared theme logic. This resolves final_kw
        # (construction-time properties) and the disabled color map.
        ThemeableWidget.__init__(self, kw)

        # 2. Store the resolved maps onto this instance (not deep-copied --
        # see sCTkTextboxPrimary's identical note).
        self._local_defaults = self.final_kw
        self._custom_disabled_map = self._widget_disabled_map

        # Extract "state" from final_kw after ThemeableWidget's merge.
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

        No longer manually re-triggers _update_current_visual_state() -- see
        sCTkTextboxPrimary's identical method for the full reasoning.

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
        See sCTkTextboxPrimary's identical method for full Args/Returns detail.
        """
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
        Gets or sets the widget's enabled/disabled visual state. See
        sCTkTextboxPrimary's identical method for full Args/Returns detail.
        """
        if state_string is not None:
            self.configure(state=state_string)
        return getattr(self, "_custom_current_state", "normal")

    def _update_current_visual_state(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, based
        on the current state, then sets the native interactive lock, then
        re-themes the internal scrollbar. See sCTkTextboxPrimary's identical
        method for the full reasoning, including the required-key checks for
        scrollbar_button_color/scrollbar_button_hover_color.
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
