#!/usr/bin/python3
"""
sCTkRadioButton - Piece 1 of 2

A custom, theme-compliant primary radio selection button widget.
Inherits cleanly and directly from ctk.CTkRadioButton to preserve 100% of native
CustomTkinter features, mutual exclusion variables, and real-time state updates.
"""
import os
import tkinter as tk

import customtkinter as ctk
from .themeable_widget import ThemeableWidget

class sCTkRadioButton(ctk.CTkRadioButton, ThemeableWidget):
    def __init__(self, master=None, **kw):
        # 1. 🔑 SYNC BACKPLANE MUTUAL EXCLUSION: Clone references to pass to both constructors safely
        variable = kw.get("variable", None)
        value = kw.get("value", None)
        command = kw.get("command", None)

        # 2. Fire our shared theme logic first. It automatically finds the class section inside themes.json
        ThemeableWidget.__init__(self, kw)

        # 3. 🛠️ THE MUTATION SAFEGUARD DEEP COPY SHIELD:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # Remove state keys to prevent native validation collisions
        self.final_kw.pop("state", None)

        # Ensure core connection properties remain intact for the native constructor pass
        if variable is not None: self.final_kw["variable"] = variable
        if value is not None: self.final_kw["value"] = value
        if command is not None: self.final_kw["command"] = command

        # 4. Initialize CustomTkinter natively letting it sew low-level StringVar tracking bindings
        super().__init__(master, **self.final_kw)

        self._custom_current_state = "normal"
        self._update_current_visual_state()

        # 🔑 5. REGISTER LIFECYCLE HANDSHAKE HOOK: Pushes notifications up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Processes Pygubu designer workspace queries and manages theme state updates cleanly."""
        if args and len(args) == 1:
            pname = args if isinstance(args, (list, tuple)) else args
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "border_color", "text_color", "hover_color"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(pname)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        # 🔑 CRASH SHIELD PASS: Updates properties natively using hidden hooks to prevent ValueError loops
        if "variable" in kwargs:
            self._variable = kwargs.pop("variable")
            if hasattr(self, "_draw"): self._draw()
        if "value" in kwargs:
            self._value = kwargs.pop("value")
            if hasattr(self, "_draw"): self._draw()
        if "command" in kwargs:
            super().configure(command=kwargs.pop("command"))

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)

        if kwargs:
            return super().configure(**kwargs)
        return None

    config = configure

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring active or disabled cells repaint fluidly on theme shifts."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._update_current_visual_state()

    def get_state(self) -> str:
        """Explicit getter synchronized with your standalone test harness script assertions."""
        return self.state()

    def state(self, mode: str = None) -> str:
        """Dedicated button state controller with safe mouse trigger isolation blocks."""
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
            super().configure(state="normal")
            if hasattr(self, "_create_bindings"):
                try:
                    self._create_bindings()
                except Exception:
                    pass
            self._update_current_visual_state()

        elif mode == "disabled":
            self._custom_current_state = "disabled"
            # 🔑 HARD INTERCEPT UNBIND MATRIX: Freezes clicking pathways securely
            try:
                if hasattr(self, "_canvas") and self._canvas:
                    self._canvas.unbind("<Enter>")
                    self._canvas.unbind("<Leave>")
                    self._canvas.unbind("<Button-1>")
                    self._canvas.unbind("<ButtonRelease>")
                if hasattr(self, "_text_label") and self._text_label:
                    self._text_label.unbind("<Enter>")
                    self._text_label.unbind("<Leave>")
                    self._text_label.unbind("<Button-1>")
                    self._text_label.unbind("<ButtonRelease>")
            except Exception:
                pass
            super().configure(state="normal")
            self._update_current_visual_state()

        return self._custom_current_state

    def _update_current_visual_state(self):
        """MASTER VISUAL ROUTER: Automatically extracts and resolves theme palettes cleanly."""
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "radiobutton_width", "radiobutton_height", "border_width", "border_color",
                    "hover_color", "text_color", "font"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

        if config_payload:
            super().configure(**config_payload)

    def bind(self, sequence=None, command=None, add=None):
        if "PYGUBU_DESIGNER_RUNNING" in os.environ:
            return None
        return super().bind(sequence, command, add)


