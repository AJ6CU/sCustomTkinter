#!/usr/bin/python3
"""
sCTkCheckBox

A custom, theme-compliant binary selection check box widget.
Inherits cleanly and directly from ctk.CTkCheckBox to preserve 100% of native
CustomTkinter features, theme tracking loops, and native input locks [1.1, 1.2].
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget

class sCTkCheckBox(ctk.CTkCheckBox, ThemeableWidget):
    def __init__(self, master=None, **kw):
        # 1. Fire our shared theme logic first. It automatically finds "sCTkCheckBox" in the JSON
        ThemeableWidget.__init__(self, kw)

        # 2. 🛠️ THE MUTATION SAFEGUARD DEEP COPY:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 3. Initialize CustomTkinter natively with the clean final kwargs array safely
        super().__init__(master, **self.final_kw)
        self._custom_current_state = "normal"

        # 🔑 4. REGISTER LIFECYCLE HANDSHAKE HOOK:
        self._finalize_themeable_lifecycle()

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring checkbox cells repaint fluidly on theme shifts [1.1, 1.2]."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._update_current_visual_state()

    def configure(self, *args, **kwargs):
        """Handles Pygubu designer queries and manages composite state updates safely [1.1]."""
        if args and len(args) == 1:
            pname = args[0]
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "border_color", "text_color", "hover_color", "checkmark_color"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(pname)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        if kwargs:
            for k, v in list(kwargs.items()):
                if v == "":
                    kwargs.pop(k)
            if kwargs:
                return super().configure(**kwargs)
        return None

    config = configure

    def get_state(self):
        """Explicit getter synchronized with your standalone test harness script assertions [1.1]."""
        return self.state()

    def state(self, mode: str = None):
        """Dedicated checkbox operational availability state controller [1.1]."""
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
            self._update_current_visual_state()

        elif mode == "disabled":
            self._custom_current_state = "disabled"
            self._update_current_visual_state()

    def _update_current_visual_state(self):
        """MASTER VISUAL ROUTER: Dynamically applies extensible theme properties [1.1, 1.2]."""
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "border_color", "hover_color", "text_color", "checkmark_color", "border_width", "font"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

        if config_payload:
            super().configure(**config_payload)

        # 🔑 SEQUENTIAL LOCK PASS: Native flag updates are executed at the absolute end
        if is_disabled:
            super().configure(state="disabled")
        else:
            super().configure(state="normal")
