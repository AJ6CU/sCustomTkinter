#!/usr/bin/python3
"""
sCTkSegmentedButton - Piece 1 of 2

A highly optimized, theme-compliant segmented button strip widget.
Inherits directly from ctk.CTkSegmentedButton to let CustomTkinter handle native
state changes, input locks, and button rendering cleanly.
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkSegmentedButton(ctk.CTkSegmentedButton, ThemeableWidget):
    def __init__(self, master=None, **kw):
        # 1. Capture widget-specific attributes early before mixin configuration passes
        values = kw.pop("values", None)
        variable = kw.pop("variable", None)
        command = kw.pop("command", None)

        # 2. Fire our shared theme logic to map properties natively out of themes.json
        ThemeableWidget.__init__(self, kw)
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 3. Clean up validation keys and remove layout-breaking border/padding parameters
        self.final_kw.pop("state", None)
        for key in ["unselected_color", "unselected_hover_color", "border_width", "border_color",
                    "selected_color_padding"]:
            self.final_kw.pop(key, None)

        # 4. Initialize CustomTkinter safely with the pristine final kwargs array
        super().__init__(master, **self.final_kw)
        self._custom_current_state = "normal"

        if values is not None: super().configure(values=values)
        if variable is not None: super().configure(variable=variable)
        if command is not None: super().configure(command=command)

        # Set up delayed look sync pass on startup boot cycles
        self.after(15, self._apply_custom_theme_colors)
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Passes layout adjustments down natively while capturing state triggers smoothly."""
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                return super().configure(args[0])

        if "values" in kwargs: super().configure(values=kwargs.pop("values"))
        if "variable" in kwargs: super().configure(variable=kwargs.pop("variable"))
        if "command" in kwargs: super().configure(command=kwargs.pop("command"))

        has_state = "state" in kwargs
        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)

        if kwargs:
            super().configure(**kwargs)

        if has_state:
            self._apply_custom_theme_colors()

    config = configure

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring tracking cells repaint fluidly on theme skin shifts."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._apply_custom_theme_colors()

    def state(self, mode: str = None) -> str:
        """Dedicated operational state manager mapped securely to hidden variables."""
        if mode is None:
            return str(getattr(self, "_state", "normal")).lower()
        self.configure(state=mode)
        return mode

    def get_state(self) -> str:
        """Explicit getter synchronized with your standalone test harness script assertions."""
        return self.state()

    def set(self, *args, **kwargs):
        """Programmatic variable tracking set intercept hook."""
        super().set(*args, **kwargs)
        self._apply_custom_theme_colors()

    def _clicked(self, *args, **kwargs):
        """Human click intercept callback trigger handler pass."""
        super()._clicked(*args, **kwargs)
        self._apply_custom_theme_colors()

    def _apply_custom_theme_colors(self):
        """
        PURE THEME PROCESSOR COMPRESSED:
        Extracts color profiles dynamically out of themes.json and flattens child button
        layout paddings to completely weld background gaps.
        """
        if not hasattr(self, "_buttons_dict") or not self._buttons_dict:
            return

        is_disabled = str(getattr(self, "_state", "normal")).lower() == "disabled"
        current_skin = str(ctk.get_appearance_mode()).lower()
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        # Resolve clean core track palettes directly out of stylesheet maps
        resolved_fg = self._resolve_color(target_map.get("fg_color", ["#4F75A2", "#2B4C7E"]))
        d_selected_bg = self._resolve_color(
            self._custom_disabled_map.get("disabled_selected_color", ["#70777B", "#4A4E51"]))
        n_selected = self._resolve_color(self._local_defaults.get("selected_color", ["#1A4375", "#1F6AA5"]))

        # Package the parent payload track updates cleanly
        fg_payload = {
            "fg_color": resolved_fg,
            "selected_color": d_selected_bg if is_disabled else n_selected,
            "unselected_color": resolved_fg,
            "unselected_hover_color": resolved_fg if is_disabled else self._resolve_color(
                self._local_defaults.get("unselected_hover_color", ["#CBD5E1", "#334155"]))
        }
        super().configure(**fg_payload)

        # Resolve typography base configurations cleanly
        raw_txt = target_map.get("text_color")
        base_txt_color = self._resolve_color(raw_txt) if raw_txt else ["#FFFFFF", "#FFFFFF"]

        for val_name, button in self._buttons_dict.items():
            # Clear layout padding bounds flush to the container track edge
            try:
                button.grid_configure(padx=0, pady=0)
            except Exception:
                pass

            if is_disabled:
                if hasattr(self, "_current_value") and val_name == self._current_value:
                    button.configure(text_color="#FFFFFF" if current_skin == "dark" else "#1F2937")
                else:
                    button.configure(text_color=self._resolve_color(["#475569", "#94A3B8"]))
            else:
                button.configure(text_color=base_txt_color)

