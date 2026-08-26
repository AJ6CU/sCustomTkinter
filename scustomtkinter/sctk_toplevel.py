#!/usr/bin/python3
"""
sCTkToplevel

A theme-compliant custom top-level window layout wrapper.
Inherits from customtkinter.CTkToplevel and ThemeableWidget to manage
amateur radio modal dialogs, popup logs, and sub-window cockpit panels
safely without requiring manual customtkinter imports in user space.
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget

class sCTkToplevel(ctk.CTkToplevel, ThemeableWidget):
    def __init__(self, master=None, **kwargs):
        # 1. Run shared mixin logic first to parse master themes.json data safely
        ThemeableWidget.__init__(self, kwargs)
        self._local_defaults = dict(self.final_kw)

        # 2. Extract specific fallback styling configurations if gridded in JSON
        self._fg_color = self.final_kw.get("fg_color", None)

        # 3. Initialize CustomTkinter's native top-level container window chassis
        super().__init__(master, **self.final_kw)

        # 4. Finalize framework lifecycle parameters
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Processes standard geometry queries and configuration dictionary payloads."""
        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if kwargs:
            super().configure(**kwargs)

    config = configure



