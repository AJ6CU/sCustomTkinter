#!/usr/bin/python3
"""
sCTkTextboxSecondary

A custom, theme-compliant secondary messaging and logging area widget.
Inherits cleanly and directly from ctk.CTkTextbox to preserve 100% of native
CustomTkinter features and mouse scrolling tracks without custom interference.
"""
import os
import sys
import platform
import tkinter as tk
import customtkinter as ctk
from ThemeableWidget import ThemeableWidget


class sCTkTextboxSecondary(ctk.CTkTextbox, ThemeableWidget):
    def __init__(self, master=None, **kw):
        # 1. Fire our shared theme logic first. It automatically finds "sCTkTextboxSecondary" in themes.json
        ThemeableWidget.__init__(self, kw)

        # 2. Store your custom maps safely onto instance memory channels
        self._local_defaults = self.final_kw
        self._custom_disabled_map = self._widget_disabled_map

        # Extract custom parameters from final_kw to prevent parent constructor collisions
        state_init = self.final_kw.pop("state", "normal")

        # 3. Initialize CustomTkinter natively with the clean final kwargs array safely
        super().__init__(master, **self.final_kw)

        # Camouflage Transparency Workaround: Safely fetch parent backplane hex color strings
        try:
            current_fg = super().cget("fg_color")
            if current_fg in ("transparent", ""):
                parent_bg = self.master.cget("fg_color")
                if parent_bg not in ("transparent", ""):
                    super().configure(fg_color=parent_bg)
        except Exception:
            pass

        # 4. Route cleanly to standard native state initialization via public setter
        self._virtual_state = "normal"
        self.state(state_init)

        # 🔑 5. REGISTER LIFECYCLE HANDSHAKE HOOK:
        # Synchronizes secondary logging instances with Pygubu layout registries.
        self._finalize_themeable_lifecycle()

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring text cells repaint fluidly on theme shifts."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._update_current_visual_state()

    def configure(self, *args, **kwargs):
        """Handles both standard keyword configurations and Pygubu inspector queries cleanly."""
        if args and len(args) == 1:
            pname = args if isinstance(args, (list, tuple)) else args

            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "text_color", "border_color", "scrollbar_button_color",
                         "scrollbar_button_hover_color"]:
                val = self._custom_disabled_map.get(
                    pname) if self._virtual_state == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(pname)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if "state" in kwargs:
            self._virtual_state = str(kwargs.pop("state")).lower()
            self._update_current_visual_state()

        if kwargs:
            return super().configure(**kwargs)
        return None

    config = configure

    def get_state(self):
        """Explicit getter synchronized with your standalone test harness script assertions."""
        return self.state()

    def state(self, state_string=None):
        """Standard Tkinter state management mapping."""
        if state_string is not None:
            self.configure(state=state_string)
        return getattr(self, "_virtual_state", "normal")

    def _update_current_visual_state(self):
        """MASTER VISUAL ROUTER: Enforces strict sequential order of operations to bypass the white-out bug."""
        is_disabled = getattr(self, "_virtual_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        # 1. Map styling color variables cleanly out of configuration directories
        config_payload = {}
        for key in ("fg_color", "border_color", "text_color", "scrollbar_button_color", "scrollbar_button_hover_color"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

        if config_payload:
            super().configure(**config_payload)

        # 2. SEQUENTIAL LOCK PASS: Force true native disabled flags to lock text inputs completely
        if is_disabled:
            super().configure(state="disabled")
        else:
            super().configure(state="normal")

        # 3. Force CustomTkinter's sidecar scrollbar container to redraw its vector geometry instantly
        if hasattr(self, "_scrollbar") and self._scrollbar:
            try:
                if is_disabled:
                    disabled_bar = self._resolve_color(
                        self._custom_disabled_map.get("scrollbar_button_color", ["#D1D5DB", "#374151"]))
                    self._scrollbar.configure(button_color=disabled_bar, button_hover_color=disabled_bar)
                else:
                    normal_bar = self._resolve_color(
                        self._local_defaults.get("scrollbar_button_color", ["#94A3B8", "#475569"]))
                    normal_hover = self._resolve_color(
                        self._local_defaults.get("scrollbar_button_hover_color", ["#64748B", "#334155"]))
                    self._scrollbar.configure(button_color=normal_bar, button_hover_color=normal_hover)

                if hasattr(self._scrollbar, "_draw"):
                    self._scrollbar._draw()
            except Exception:
                pass


# =====================================================================
# UTM TESTING HARNESS IMPORTS & SETUP
# =====================================================================
import sCTkThemes
from sCTkFrame import sCTkFrame

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("500x450")
    root.title("sCTkTextboxSecondary Native Pure Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    widget = sCTkTextboxSecondary(base)
    widget.pack(expand=True, fill="both", padx=10, pady=10)

    for i in range(30):
        widget.insert("end", f"[{i:02d}] SECONDARY FREQ TRANSLATION CHANNEL BUFFER -> VERIFIED\n")


    def toggle_logger_states():
        current_state = widget.get_state()
        target = "disabled" if current_state == "normal" else "normal"
        widget.configure(state=target)

        if target == "disabled":
            btn_toggle.configure(text="Activate Secondary Feed")
        else:
            btn_toggle.configure(text="Lock Secondary Feed")


    def toggle_appearance_skin():
        current_mode = ctk.get_appearance_mode()
        target = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(target)


    btn_toggle = ctk.CTkButton(base, text="Lock Secondary Feed", command=toggle_logger_states)
    btn_toggle.pack(fill="x", padx=10, pady=5)

    btn_theme = ctk.CTkButton(base, text="Toggle Theme Skin", command=toggle_appearance_skin)
    btn_theme.pack(fill="x", padx=10, pady=5)

    root.mainloop()
