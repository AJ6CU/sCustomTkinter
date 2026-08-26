#!/usr/bin/python3
"""
sCTkOptionMenuPrimary - Piece 1 of 2

A custom, theme-compliant primary option selection menu dropdown widget.
Inherits cleanly and directly from ctk.CTkOptionMenu to preserve 100% of native
CustomTkinter features, theme tracking loops, and native dropdown workflows [1.1, 1.2].
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget

class sCTkOptionMenuPrimary(ctk.CTkOptionMenu, ThemeableWidget):
    def __init__(self, master=None, **kw):
        # 1. 🛠️ PARAMETER POPPING: Capture operational list specifics early
        values = kw.pop("values", None)
        command = kw.pop("command", None)
        variable = kw.pop("variable", None)

        # 2. Fire our shared theme logic first. It automatically finds the class section inside themes.json
        ThemeableWidget.__init__(self, kw)

        # 3. 🛠️ THE MUTATION SAFEGUARD COPY:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 4. Initialize CustomTkinter natively with the clean final kwargs array safely
        super().__init__(master, **self.final_kw)

        # 5. Build your inner custom properties using your popped parameters safely
        if values is not None:
            super().configure(values=values)
        if command is not None:
            super().configure(command=command)
        if variable is not None:
            super().configure(variable=variable)

        self._custom_current_state = "normal"
        self._update_current_visual_state()

        # 🔑 6. REGISTER LIFECYCLE HANDSHAKE HOOK: Pushes notifications up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Processes Pygubu designer workspace queries and manages theme state updates cleanly [1.1]."""
        if args and len(args) == 1:
            pname = args
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "button_color", "button_hover_color", "text_color"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(pname)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if "values" in kwargs:
            super().configure(values=kwargs.pop("values"))
        if "command" in kwargs:
            super().configure(command=kwargs.pop("command"))
        if "variable" in kwargs:
            super().configure(variable=kwargs.pop("variable"))

        if "state" in kwargs:
            target_state = str(kwargs.pop("state")).lower()
            self.state(target_state)

        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        if kwargs:
            return super().configure(**kwargs)
        return None

    config = configure
    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring active or disabled cells repaint fluidly on theme shifts [1.1, 1.2]."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._update_current_visual_state()

    def get_state(self):
        """Explicit getter synchronized with your standalone test harness script assertions [1.1]."""
        return self.state()

    def state(self, mode: str = None):
        """Standard Tkinter state management mapping helper with sequential style overrides [1.1]."""
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
        elif mode == "disabled":
            self._custom_current_state = "disabled"

        self._update_current_visual_state()
        return self._custom_current_state

    def _update_current_visual_state(self):
        """
        MASTER VISUAL ROUTER FIXED:
        🔑 REPAINT LOGIC DYNAMIC MAP: Loops fluidly across both modes uniformly,
        ensuring disabled colors swap seamlessly on skin preference shifts [1.1, 1.2]!
        """
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "button_color", "button_hover_color", "text_color", "dropdown_fg_color", "dropdown_text_color", "font"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

        if config_payload:
            super().configure(**config_payload)

        # 🔑 SEQUENTIAL LOCK PASS: Native flag updates are executed at the absolute end to prevent caching blocks
        if is_disabled:
            super().configure(state="disabled")
        else:
            super().configure(state="normal")

    def update_list(self, new_values: list, default_index: int = 0):
        """Safely updates the items list and resets the visible value."""
        if not new_values:
            self.configure(values=[""])
            self.set("")
            return

        self.configure(values=new_values)

        if default_index < len(new_values):
            self.set(new_values[default_index])
        else:
            self.set(new_values[0])

