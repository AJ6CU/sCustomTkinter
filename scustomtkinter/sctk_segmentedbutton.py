#!/usr/bin/python3
"""
sCTkSegmentedButton

A highly optimized, theme-compliant segmented button strip widget.
Inherits directly from ctk.CTkSegmentedButton to let CustomTkinter handle native
state changes, input locks, and button rendering cleanly.
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkSegmentedButton(ctk.CTkSegmentedButton, ThemeableWidget):
    def __init__(self, master=None, **kw):
        # 1. Capture widget-specific attributes early before mixin configuration passes
        values = kw.pop("values", None)
        variable = kw.pop("variable", None)
        command = kw.pop("command", None)

        # 2. Fire our shared theme logic to map properties natively out of themes.json
        ThemeableWidget.__init__(self, kw)
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 3. Clean up validation keys and remove layout-breaking border/padding parameters
        self.final_kw.pop("state", None)
        for key in ["unselected_color", "unselected_hover_color", "border_width", "border_color",
                    "selected_color_padding"]:
            self.final_kw.pop(key, None)

        # 4. Initialize CustomTkinter safely with the pristine final kwargs array
        super().__init__(master, **self.final_kw)
        self._custom_current_state = "normal"

        if values is not None: super().configure(values=values)
        if variable is not None: super().configure(variable=variable)
        if command is not None: super().configure(command=command)

        # Set up delayed look sync pass on startup boot cycles
        self.after(15, self._apply_custom_theme_colors)
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Passes layout adjustments down natively while capturing state triggers smoothly."""
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                return super().configure(args[0])

        if "values" in kwargs: super().configure(values=kwargs.pop("values"))
        if "variable" in kwargs: super().configure(variable=kwargs.pop("variable"))
        if "command" in kwargs: super().configure(command=kwargs.pop("command"))

        # FIX: previously left "state" in kwargs and let it pass straight through to
        # super().configure(), which locked the widget natively but never updated
        # self._custom_current_state -- so get_state() and the disabled color swap
        # were both silently wrong. Routing through self.state() fixes both.
        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)

        if kwargs:
            super().configure(**kwargs)

    config = configure

    def _set_appearance_mode(self, mode_string: str):
        """
        EXPERIMENTAL: no longer manually re-triggers _apply_custom_theme_colors().
        _apply_custom_theme_colors() now passes raw (light, dark) tuples straight
        through to configure() instead of pre-resolving to a single color, so CTk's
        own appearance-mode tracking should repaint correctly on its own. If colors
        stop following mode changes (especially while disabled), that's the signal
        this doesn't hold and the manual re-trigger needs to come back.
        """
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass

    def state(self, mode: str = None) -> str:
        """
        Dedicated operational state manager.

        FIX: previously read/wrote self._state, which nothing else in this class
        actually updated (the only code that did was ThemeableWidget.configure(),
        which is dead -- see the ThemeableWidget audit notes). Now consistently
        uses self._custom_current_state, matching every other sCTk widget.
        """
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        self._custom_current_state = "disabled" if mode.lower() == "disabled" else "normal"
        super().configure(state=self._custom_current_state)
        self._apply_custom_theme_colors()
        return self._custom_current_state

    def get_state(self) -> str:
        """Explicit getter synchronized with your standalone test harness script assertions."""
        return self.state()

    def set(self, *args, **kwargs):
        """Programmatic variable tracking set intercept hook."""
        super().set(*args, **kwargs)
        self._apply_custom_theme_colors()

    def _clicked(self, *args, **kwargs):
        """Human click intercept callback trigger handler pass."""
        super()._clicked(*args, **kwargs)
        self._apply_custom_theme_colors()

    def _apply_custom_theme_colors(self):
        """
        EXPERIMENTAL: passes raw (light, dark) tuples straight through to configure()
        instead of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.

        Also fixed: is_disabled now reads self._custom_current_state (see state() fix
        above) instead of the never-updated self._state.
        """
        if not hasattr(self, "_buttons_dict") or not self._buttons_dict:
            return

        is_disabled = str(getattr(self, "_custom_current_state", "normal")).lower() == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        fg_tuple = tuple(target_map.get("fg_color", ("#4F75A2", "#2B4C7E")))
        d_selected = tuple(self._custom_disabled_map.get("disabled_selected_color", ("#70777B", "#4A4E51")))
        n_selected = tuple(self._local_defaults.get("selected_color", ("#1A4375", "#1F6AA5")))
        unselected_hover = tuple(self._local_defaults.get("unselected_hover_color", ("#CBD5E1", "#334155")))

        fg_payload = {
            "fg_color": fg_tuple,
            "selected_color": d_selected if is_disabled else n_selected,
            "unselected_color": fg_tuple,
            "unselected_hover_color": fg_tuple if is_disabled else unselected_hover,
        }
        super().configure(**fg_payload)

        base_txt_tuple = tuple(target_map.get("text_color") or ("#FFFFFF", "#FFFFFF"))

        for val_name, button in self._buttons_dict.items():
            # Clear layout padding bounds flush to the container track edge
            try:
                button.grid_configure(padx=0, pady=0)
            except Exception:
                pass

            if is_disabled:
                if hasattr(self, "_current_value") and val_name == self._current_value:
                    button.configure(text_color=("#1F2937", "#FFFFFF"))
                else:
                    button.configure(text_color=("#475569", "#94A3B8"))
            else:
                button.configure(text_color=base_txt_tuple)
