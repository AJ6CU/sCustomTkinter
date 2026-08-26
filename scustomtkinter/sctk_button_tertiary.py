#!/usr/bin/python3
"""
sCTkButtonTertiary - Piece 1 of 2

A custom, theme-compliant tertiary outline latching variant button widget.
Inherits cleanly and directly from ctk.CTkButton to preserve 100% of native
CustomTkinter features and eliminate baseui middleman interface crashes.
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget

class sCTkButtonTertiary(ctk.CTkButton, ThemeableWidget):
    def __init__(self, master=None, **kw):
        # 1. Run the shared theme logic to load defaults out of themes.json
        ThemeableWidget.__init__(self, kw)

        # 3. 🛠️ THE MUTATION SAFEGUARD DEEP COPY:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)
        self._custom_pressed_map = dict(self._widget_pressed_map)

        # 4. Initialize CustomTkinter natively with the clean final kwargs array safely
        super().__init__(master, **self.final_kw)

        self.is_pressed = False
        self._custom_current_state = "normal"
        self._update_current_visual_state()

        # 🔑 5. REGISTER LIFECYCLE HANDSHAKE HOOK:
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Handles Pygubu designer queries and manages state updates safely."""
        if args and len(args) == 1:
            pname = args if isinstance(args, (list, tuple)) else args
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "border_color", "text_color", "hover_color"]:
                current_state = str(self.state()).lower()
                if current_state == "disabled" and self._custom_disabled_map:
                    val = self._custom_disabled_map.get(pname)
                elif getattr(self, "is_pressed", False) and self._custom_pressed_map:
                    val = self._custom_pressed_map.get(pname)
                else:
                    val = self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(pname)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if "state" in kwargs:
            target_state = kwargs.pop("state")
            self.state(target_state)

        if kwargs:
            for k, v in list(kwargs.items()):
                if v == "":
                    kwargs.pop(k)
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

    def get_state(self):
        """Explicit getter synchronized with your standalone test harness script assertions."""
        return self.state()

    def state(self, mode: str = None):
        """Dedicated button state controller."""
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
            super().configure(state="normal", hover=True)
            if hasattr(self, "_create_bindings"):
                try: self._create_bindings()
                except Exception: pass
            self._update_current_visual_state()

        elif mode == "disabled":
            self._custom_current_state = "disabled"
            try:
                if hasattr(self, "_canvas") and self._canvas:
                    self._canvas.unbind("<Enter>")
                    self._canvas.unbind("<Leave>")
                    self._canvas.unbind("<Button-1>")
                    self._canvas.unbind("<ButtonRelease>")
            except Exception:
                pass
            super().configure(state="normal", hover=False)
            self._update_current_visual_state()

        return self._custom_current_state

    def set_pressed(self, pressed: bool):
        """Toggles the visual pressed state of the tertiary button cleanly."""
        if getattr(self, "_custom_current_state", "normal") == "disabled":
            return
        self.is_pressed = pressed
        self._update_current_visual_state()

    def _update_current_visual_state(self):
        """MASTER VISUAL ROUTER FIXED: Forces disabled outline configurations to adapt fluidly."""
        if getattr(self, "_custom_current_state", "normal") == "disabled":
            config_payload = {}
            for key in ("fg_color", "hover_color", "border_color", "text_color"):
                val = self._custom_disabled_map.get(key)
                if val is not None:
                    config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val
            if config_payload:
                super().configure(**config_payload)
            return

        if getattr(self, "is_pressed", False):
            config_payload = {}
            for key in ("fg_color", "border_color", "hover_color", "text_color"):
                val = self._custom_pressed_map.get(key)
                if val is not None:
                    config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

            config_payload.setdefault("hover_color", self._resolve_color(self._local_defaults.get("hover_color")))
            config_payload["hover"] = False
            super().configure(**config_payload)
        else:
            config_payload = {}
            for key in ("fg_color", "hover_color", "border_color", "text_color", "border_width", "corner_radius", "font"):
                val = self._local_defaults.get(key)
                if val is not None:
                    config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

            config_payload["hover"] = True
            if config_payload:
                super().configure(**config_payload)

