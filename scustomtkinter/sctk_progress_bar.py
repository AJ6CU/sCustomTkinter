#!/usr/bin/python3
"""
sCTkProgressBar - Piece 1 of 2

A custom, theme-compliant system progression indicator bar widget.
Inherits cleanly and directly from ctk.CTkProgressBar to preserve 100% of native
CustomTkinter features, theme tracking loops, and real-time state updates.
"""
import os
import customtkinter as ctk
from .themeable_widget import ThemeableWidget

class sCTkProgressBar(ctk.CTkProgressBar, ThemeableWidget):
    def __init__(self, master=None, **kwargs):
        # 1. INITIAL RUNTIME SCRUB: Safely shield native frame from state validation checks
        state_init = kwargs.pop("state", "normal")

        # 2. ENFORCE SYSTEM REGISTRY INTERACTION:
        ThemeableWidget.__init__(self, kwargs)

        # 3. 🛠️ THE MUTATION SAFEGUARD DEEP COPY SHIELD:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # Remove custom parameters from final_kw to prevent parent collisions
        self.final_kw.pop("state", None)

        # 4. Initialize CustomTkinter natively with the clean final kwargs array safely
        super().__init__(master, **self.final_kw)

        # 5. ROUTE TO CONFIG: Safely pass parameters through your validation engine
        self._state_str = "normal"
        self.state(state_init)

        # 🔑 6. REGISTER LIFECYCLE HANDSHAKE HOOK: Pushes notifications up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Processes Pygubu designer queries and manages state changes safely."""
        if args and len(args) == 1:
            pname = args if isinstance(args, (list, tuple)) else args
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "progress_color", "border_color"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(*args, **kwargs)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        if kwargs:
            super().configure(**kwargs)
            self._update_current_visual_state()
    def cget(self, attribute_name: str) -> any:
        """Safely intercept custom properties like 'state' from throwing errors."""
        if str(attribute_name).lower() == "state":
            return self.state()
        return super().cget(attribute_name)

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring active or disabled lanes repaint fluidly on theme shifts."""
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
        """Dedicated polymorphic state manager forcing internal indicator lane repaints."""
        if mode is None:
            return str(getattr(self, "_state_str", "normal")).lower()

        target_state = mode.lower()
        self._state_str = target_state
        self._update_current_visual_state()
        return self._state_str

    def _update_current_visual_state(self):
        """MASTER VISUAL ROUTER: Automatically extracts and resolves properties out of protected memory."""
        is_disabled = getattr(self, "_state_str", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "progress_color", "border_color", "border_width", "corner_radius"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

        if config_payload:
            super().configure(**config_payload)

    def bind(self, sequence=None, command=None, add=None):
        if "PYGUBU_DESIGNER_RUNNING" in os.environ:
            return None
        return super().bind(sequence, command, add)

