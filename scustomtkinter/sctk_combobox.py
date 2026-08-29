#!/usr/bin/python3
"""
sCTkComboBox

A custom, theme-compliant parameter selection dropdown combobox widget.
Inherits cleanly and directly from ctk.CTkComboBox to preserve 100% of native
CustomTkinter features, theme tracking loops, and native input locks [1.1, 1.2].
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget

class sCTkComboBox(ctk.CTkComboBox, ThemeableWidget):
    def __init__(self, master=None, **kw):
        # 1. PARAMETER POPPING: Capture combobox-specific tracking parameters early
        values = kw.pop("values", [""])
        command = kw.pop("command", None)
        variable = kw.pop("variable", None)

        # 2. Fire our shared theme logic first. It automatically finds "sCTkComboBox" in the JSON
        ThemeableWidget.__init__(self, kw)

        # 3. 🛠️ THE MUTATION SAFEGUARD DEEP COPY:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 4. Initialize CustomTkinter natively with the clean final kwargs array safely
        super().__init__(master, **self.final_kw)

        # 5. Build your inner custom properties using your popped parameters safely
        if values:
            super().configure(values=values)
            if isinstance(values, list) and len(values) > 0 and values[0] != "":
                self.set(values[0])

        if command: super().configure(command=command)
        if variable: super().configure(variable=variable)

        self._custom_current_state = "normal"

        # 🔑 6. REGISTER LIFECYCLE HANDSHAKE HOOK:
        self._finalize_themeable_lifecycle()

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring combobox components follow global theme shifts fluidly [1.1, 1.2]."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._update_current_visual_state()

    def configure(self, *args, **kwargs):
        """Handles Pygubu designer queries and manages composite state updates safely."""
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname == "state":
                    return ("state", "state", "state", "normal", str(self.state()))

                if pname in ["fg_color", "border_color", "text_color", "hover_color"]:
                    current_state = str(self.state()).lower()
                    val = self._custom_disabled_map.get(
                        pname) if current_state == "disabled" else self._local_defaults.get(pname)
                    return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

                return super().configure(pname)

        if "values" in kwargs: super().configure(values=kwargs.pop("values"))
        if "command" in kwargs: super().configure(command=kwargs.pop("command"))
        if "variable" in kwargs: super().configure(variable=kwargs.pop("variable"))

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
        """Dedicated combobox state controller [1.1]."""
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
        for key in ("fg_color", "border_color", "text_color", "button_color", "button_hover_color",
                    "dropdown_fg_color", "dropdown_text_color", "dropdown_hover_color", "border_width", "font"):
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
