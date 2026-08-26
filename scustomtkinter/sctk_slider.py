#!/usr/bin/python3
"""
sCTkSlider - Piece 1 of 2

A clean, theme-compliant linear adjustment tracking slider widget.
Inherits directly from ctk.CTkSlider to preserve native mouse dragging handle
calculations, scaling boundaries, and coordinate snap thresholds.
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkSlider(ctk.CTkSlider, ThemeableWidget):
    def __init__(self, master=None, **kw):
        # 1. Capture slider-specific positioning keys early
        command = kw.pop("command", None)
        variable = kw.pop("variable", None)

        # 2. Fire our shared theme logic to map parameters natively out of themes.json
        ThemeableWidget.__init__(self, kw)
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # Remove state keys to prevent native validation collisions
        self.final_kw.pop("state", None)

        # 3. Initialize CustomTkinter safely with the finalized kwargs array
        super().__init__(master, **self.final_kw)

        if command is not None: super().configure(command=command)
        if variable is not None: super().configure(variable=variable)

        # Apply look variables seamlessly on startup
        self.after(10, self._apply_custom_theme_colors)
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Processes runtime keyword configurations and handles Pygubu canvas requests cleanly."""
        if args and len(args) == 1:
            pname = args[0]
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "progress_color", "button_color", "button_hover_color"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(
                    pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(pname)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if "command" in kwargs: super().configure(command=kwargs.pop("command"))
        if "variable" in kwargs: super().configure(variable=kwargs.pop("variable"))

        # Capture native state shifts to cycle our color tracks
        has_state = "state" in kwargs
        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)

        if kwargs:
            super().configure(**kwargs)

        if has_state:
            self._apply_custom_theme_colors()

    config = configure
    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring tracking tracks repaint fluidly on skin shifts."""
        if hasattr(super(), "_set_appearance_mode"):
            try: super()._set_appearance_mode(mode_string)
            except Exception: pass
        self._apply_custom_theme_colors()

    def state(self, mode: str = None) -> str:
        """Dedicated operational state manager mapped securely to hidden variables."""
        if mode is None:
            return str(super().cget("state")).lower()
        self.configure(state=mode)
        return mode

    def get_state(self) -> str:
        """Explicit getter synchronized with your standalone test harness script assertions."""
        return self.state()

    def _apply_custom_theme_colors(self):
        """
        PURE THEME PROCESSOR:
        🔑 SAFE CONTEXT PASS: Extracts color metrics dynamically and injects resolved variables
        directly through high-level channels to eliminate loop freezes completely.
        """
        is_disabled = str(super().cget("state")).lower() == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        # Map core track variables cleanly via parent configurations
        fg_payload = {}
        for key in ("fg_color", "progress_color", "button_color", "button_hover_color"):
            val = target_map.get(key)
            if val is not None and val != "transparent":
                fg_payload[key] = self._resolve_color(val)

        if is_disabled and "button_color" in fg_payload:
            fg_payload["button_hover_color"] = fg_payload["button_color"]

        if fg_payload:
            super().configure(**fg_payload)

