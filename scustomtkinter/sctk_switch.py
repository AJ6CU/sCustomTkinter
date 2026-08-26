#!/usr/bin/python3
"""
sCTkSwitch - Piece 1 of 2

A clean, theme-compliant custom toggle switch component.
Inherits cleanly and directly from ctk.CTkSwitch to preserve 100% of native
CustomTkinter features, theme tracking loops, and Pygubu builder layout actions.
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget

class sCTkSwitch(ctk.CTkSwitch, ThemeableWidget):
    def __init__(self, master=None, onvalue=1, offvalue=0, command=None, **kw):

        # 1. Run shared mixin logic first to parse themes.json safely
        ThemeableWidget.__init__(self, kw)

        # 2. Store your custom memory maps onto instance structures
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = self._local_defaults.get("disabled_map", {})

        # 3. Extract interactive state configurations and value limits early
        state_val = kw.pop("state", "normal")
        self._state = "normal" if str(state_val).lower() == "normal" else "disabled"
        self._onvalue_payload = onvalue
        self._offvalue_payload = offvalue
        self._user_command = command

        # 4. Scrub custom theme dictionary properties to protect parent validation
        for pop_key in ["fg_color", "progress_color", "button_color", "button_hover_color",
                        "text_color", "font", "disabled_map"]:
            self.final_kw.pop(pop_key, None)

        # 5. 🔑 FIXED PIPELINE ROUTER: Intercept the callback map to build a type-safe forwarder.
        # This completely shatters CustomTkinter's zero-argument crash!
        wrapped_command = None
        if self._user_command:
            wrapped_command = self._execute_safe_command_forwarding

        # 6. Initialize CustomTkinter natively with the clean kwargs array safely
        super().__init__(master, onvalue=onvalue, offvalue=offvalue, command=wrapped_command, **self.final_kw)

        # 🔑 AIR-TIGHT EVENT INTERCEPTOR SHIELD: Pre-append custom validation tags
        self._block_tag = f"sCTkSwitchBlock_{id(self)}"
        if hasattr(self, "_canvas") and self._canvas.winfo_exists():
            self._canvas.bind_class(self._block_tag, "<Button-1>", lambda e: "break")
            self._canvas.bindtags((self._block_tag,) + self._canvas.bindtags())
        if hasattr(self, "_text_label") and self._text_label.winfo_exists():
            self._text_label.bind_class(self._block_tag, "<Button-1>", lambda e: "break")
            self._text_label.bindtags((self._block_tag,) + self._text_label.bindtags())

        # 7. Apply styles and complete lifecycle
        self._apply_custom_theme_colors()
        if self._state == "disabled":
            self.configure(state="disabled")
        self._finalize_themeable_lifecycle()

    def _execute_safe_command_forwarding(self):
        """🔑 FORWARDING MATRIX: Safely extracts active state parameters and forwards them to commands."""
        if self._user_command:
            try:
                active_val = self.get()
                try:
                    self._user_command(active_val)
                except TypeError:
                    self._user_command()
            except Exception:
                pass

    def configure(self, require_redraw=None, **kwargs):
        """Standardized configuration handler supporting Pygubu workspace properties switches."""
        if require_redraw is not None and not kwargs and isinstance(require_redraw, str):
            if require_redraw == "state":
                return ('state', 'state', 'State', 'normal', str(getattr(self, "_state", "normal")))
            return super().configure(require_redraw)

        if isinstance(require_redraw, dict):
            kwargs = require_redraw | kwargs

        if "state" in kwargs:
            self._state = str(kwargs.pop("state")).lower()
            super().configure(state=self._state)

        if "command" in kwargs:
            self._user_command = kwargs.pop("command")
            super().configure(command=self._execute_safe_command_forwarding if self._user_command else None)

        if "onvalue" in kwargs: self._onvalue_payload = kwargs["onvalue"]
        if "offvalue" in kwargs: self._offvalue_payload = kwargs["offvalue"]

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)

        if kwargs: super().configure(**kwargs)
        self._apply_custom_theme_colors()

    config = configure

    def cget(self, attribute_name: str):
        pname = str(attribute_name).lower()
        if pname == "state": return getattr(self, f"_{pname}")
        if pname == "command": return self._user_command
        return super().cget(attribute_name)

    def _set_appearance_mode(self, mode_string: str):
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._apply_custom_theme_colors()

    def state(self, mode: str = None) -> str:
        if mode is None: return str(getattr(self, "_state", "normal")).lower()
        self.configure(state=mode)
        return mode

    def get_state(self) -> str:
        return self.state()

    def _apply_custom_theme_colors(self):
        """Cascades color profiles. Intentionally leaves track colors untouched when disabled."""
        is_disabled = self._state == "disabled"
        m = self._custom_disabled_map if is_disabled else self._local_defaults
        dm = self._custom_disabled_map

        d_b_text = self._resolve_color(dm.get("text_color", ("#94A3B8", "gray50")))

        # Standard native configuration payload pass mapping safely down to the base class
        theme_payload = {
            "text_color": self._resolve_color(m.get("text_color", ("#1F2937", "#F9FAFB"))),
            "text_color_disabled": d_b_text,
            "fg_color": self._resolve_color(self._local_defaults.get("fg_color", ("#94A3B8", "#475569"))),
            "progress_color": self._resolve_color(self._local_defaults.get("progress_color", ("#1A4375", "#1F6AA5"))),
            "button_color": self._resolve_color(self._local_defaults.get("button_color", ("#FFFFFF", "#CBD5E1"))),
            "button_hover_color": self._resolve_color(
                self._local_defaults.get("button_hover_color", ("#E5E7EB", "#94A3B8")))
        }
        super().configure(**theme_payload)

        # Update dynamic security execution blocking maps dynamically based on active state parameters
        if is_disabled:
            if self._block_tag not in self._canvas.bindtags():
                self._canvas.bindtags((self._block_tag,) + self._canvas.bindtags())
            if hasattr(self, "_text_label") and self._block_tag not in self._text_label.bindtags():
                self._text_label.bindtags((self._block_tag,) + self._text_label.bindtags())
        else:
            if self._block_tag in self._canvas.bindtags():
                tags = list(self._canvas.bindtags());
                tags.remove(self._block_tag);
                self._canvas.bindtags(tuple(tags))
            if hasattr(self, "_text_label") and self._block_tag in self._text_label.bindtags():
                tags = list(self._text_label.bindtags());
                tags.remove(self._block_tag);
                self._text_label.bindtags(tuple(tags))

