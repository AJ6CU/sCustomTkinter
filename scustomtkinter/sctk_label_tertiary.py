#!/usr/bin/python3
"""
sCTkLabelTertiary

A custom, theme-compliant inline description label widget.
Fortified with direct appearance mode listeners and virtual state hooks to permanently
conquer text color freezing bugs across light/dark skin transitions.
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget

class sCTkLabelTertiary(ctk.CTkLabel, ThemeableWidget):
    _MANAGED_PROPERTIES = frozenset({"state"})

    def __init__(self, master=None, **kwargs):
        # 1. Trace and capture state parameters early out of input footprint
        state_init = kwargs.pop("state", "normal")

        # 2. Fire our shared theme logic first. It automatically finds "sCTkLabelTertiary" in themes.json
        ThemeableWidget.__init__(self, kwargs)

        # 3. 🛠️ THE MUTATION SAFEGUARD DEEP COPY:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # Remove state keys to prevent native validation collisions
        self.final_kw.pop("state", None)

        # 4. Initialize CustomTkinter natively with the clean final kwargs array safely
        super().__init__(master, **self.final_kw)

        # 5. INITIALIZE STATE REGISTRY VARIABLES
        self._current_state = "normal"
        self.configure(state=state_init)

        # 🔑 6. REGISTER LIFECYCLE HANDSHAKE HOOK: Pushes notifications up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

    def _set_appearance_mode(self, mode_string: str):
        """
        🛠️ AUTHENTIC LIFEHOOK INTERCEPTOR:
        Intercepts CustomTkinter's private theme updates, forwards them up the MRO,
        and forcefully re-triggers a state check pass.
        """
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass

        # FORCE REPAINT EVENT: Re-run our state engine to push the new light/dark colors
        self._update_current_visual_state()

    def configure(self, *args, **kwargs):
        """Extended configure to handle Pygubu designer queries and state text dimming passes."""
        if args and len(args) == 1:
            pname = args if isinstance(args, (list, tuple)) else args
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "text_color"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(*args, **kwargs)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        if kwargs:
            return super().configure(**kwargs)
        return None

    config = configure

    def get_state(self):
        """Explicit getter synchronized with your standalone test harness script assertions."""
        return self.state()

    def state(self, mode: str = None):
        """Dedicated label state controller with explicit repaint routing."""
        if mode is None:
            return str(getattr(self, "_current_state", "normal")).lower()

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._current_state = "normal"
            self._update_current_visual_state()
        elif mode == "disabled":
            self._current_state = "disabled"
            self._update_current_visual_state()

        return self._current_state

    def _update_current_visual_state(self):
        """🔑 MASTER REPAINT CORE ENGINE: Automatically extracts and resolves properties out of protected memory."""
        config_payload = {}
        target_map = self._custom_disabled_map if self._current_state == "disabled" else self._local_defaults

        for key in ("fg_color", "text_color", "font"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = self._resolve_color(val) if "color" in key else val

        if "text_color" not in config_payload:
            if self._current_state == "disabled":
                config_payload["text_color"] = "gray50"
            else:
                config_payload["text_color"] = self._local_defaults.get("text_color") or \
                                               ctk.ThemeManager.theme["CTkLabel"]["text_color"]

        if config_payload:
            super().configure(**config_payload)
