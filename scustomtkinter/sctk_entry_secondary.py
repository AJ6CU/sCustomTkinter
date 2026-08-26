#!/usr/bin/python3
"""
sCTkFrameLabeledSecondary - Piece 1 of 2

A custom, theme-compliant secondary header-labeled scrollable container panel.
Inherits cleanly and directly from ctk.CTkScrollableFrame to preserve native features
while hiding internal scrollbars smoothly across all mode changes.
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidgett

class sCTkFrameLabeledSecondary(ctk.CTkScrollableFrame, ThemeableWidget):
    properties = frozenset()

    def __init__(self, master=None, **kwargs):
        # 1. Fire our shared theme logic first. It automatically finds the class section inside themes.json
        ThemeableWidget.__init__(self, kwargs)

        # 2. 🛠️ THE MUTATION SAFEGUARD DEEP COPY:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 3. Initialize CustomTkinter ScrollableFrame natively with final kwargs safely
        super().__init__(master, **self.final_kw)

        self._custom_current_state = "normal"

        # 4. Force initial scrollbar hiding execution pass
        self._hide_internal_scrollbars()

        # 🔑 5. REGISTER LIFECYCLE HANDSHAKE HOOK: Pushes notifications up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Handles Pygubu designer queries and manages composite state updates safely."""
        if args and len(args) == 1:
            pname = args if isinstance(args, (list, tuple)) else args
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "border_color", "label_text_color"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(pname)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if "state" in kwargs:
            target_state = kwargs.pop("state")
            self.state(target_state)

        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        if kwargs:
            result = super().configure(**kwargs)
            self._hide_internal_scrollbars()
            return result
        return None

    config = configure

    def winfo_children(self, include_private: bool = False) -> list:
        """🛠️ UNIFIED STRUCTURE INTERCEPTOR OVERRIDE: Filters private title bars out."""
        raw_children = super().winfo_children()
        if include_private:
            return raw_children

        filtered_children = []
        for child in raw_children:
            if child.__class__.__name__ not in ["CTkLabel", "Label", "CTkFrame", "Frame"]:
                filtered_children.append(child)
        return filtered_children
    def get_children(self) -> list:
        """Convenience function providing a clean, application-level custom widget layout array."""
        return self.winfo_children(include_private=False)

    def get_all_children(self) -> list:
        """Convenience function providing direct, unfiltered access to the entire tree."""
        return self.winfo_children(include_private=True)

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring the labeled frame and internal scrollbars follow theme changes."""
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
        """Dedicated container frame state controller."""
        if mode is None:
            return getattr(self, "_custom_current_state", "normal")

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
        🔑 REPAINT LOGIC DYNAMIC MAP: Evaluates active vs desaturated tracks on every single swipe,
        ensuring background tokens translate perfectly when theme shifts strike while disabled!
        """
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "border_color", "label_text_color", "border_width", "label_font"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

        if config_payload:
            super().configure(**config_payload)
        self._hide_internal_scrollbars()

    def _hide_internal_scrollbars(self):
        """Forces the scrollbar track elements to match the frame background color seamlessly."""
        try:
            bg_color_raw = super().cget("fg_color")
            resolved_bg = self._resolve_color(bg_color_raw)

            if resolved_bg == "transparent":
                current_mode = str(ctk.get_appearance_mode()).lower()
                resolved_bg = "#2B2B2B" if current_mode == "dark" else "#DBDBDB"

            if hasattr(self, "_scrollbar") and self._scrollbar is not None:
                self._scrollbar.configure(
                    fg_color=resolved_bg,
                    button_color=resolved_bg,
                    button_hover_color=resolved_bg,
                    width=0
                )
        except Exception:
            pass

    def get_container(self):
        return self
