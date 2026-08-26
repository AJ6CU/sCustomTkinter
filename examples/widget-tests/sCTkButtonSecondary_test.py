#!/usr/bin/python3
"""
sCTkButtonSecondary - Piece 1 of 2

A custom, theme-compliant secondary latching button widget.
Inherits cleanly and directly from ctk.CTkButton to preserve 100% of native
CustomTkinter features and mouse tracks without middleman interface tearing.
"""
import customtkinter as ctk
from ThemeableWidget import ThemeableWidget

class sCTkButtonSecondary(ctk.CTkButton, ThemeableWidget):
    def __init__(self, master=None, **kw):
        # 1. Fire our shared theme logic first. It automatically finds "sCTkButtonSecondary" in the JSON
        ThemeableWidget.__init__(self, kw)

        # 2. 🛠️ THE MUTATION SAFEGUARD DEEP COPY:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)
        self._custom_pressed_map = dict(self._widget_pressed_map)

        # 3. Initialize CustomTkinter natively with the clean final kwargs array safely
        super().__init__(master, **self.final_kw)

        self.is_pressed = False
        self._custom_current_state = "normal"
        self._update_current_visual_state()

        # 🔑 4. REGISTER LIFECYCLE HANDSHAKE HOOK:
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Handles Pygubu designer queries and manages composite state updates safely."""
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
        """Dedicated secondary button latching toggle state controller."""
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
        """Toggles the visual pressed state of the secondary button cleanly."""
        if getattr(self, "_custom_current_state", "normal") == "disabled":
            return
        self.is_pressed = pressed
        self._update_current_visual_state()

    def _update_current_visual_state(self):
        """MASTER VISUAL ROUTER FIXED: Forces disabled colors to track theme changes natively."""
        if getattr(self, "_custom_current_state", "normal") == "disabled":
            config_payload = {}
            for key in ("fg_color", "hover_color", "border_color", "text_color"):
                val = self._custom_disabled_map.get(key)
                if val is not None:
                    config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val
            if config_payload:
                super().configure(**config_payload)
            return

        if self.is_pressed:
            config_payload = {}
            for key in ("fg_color", "hover_color", "border_color", "text_color"):
                val = self._custom_pressed_map.get(key)
                if val is not None:
                    config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val
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

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
import sCTkThemes
from sCTkFrame import sCTkFrame

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()
    root = ctk.CTk()
    root.geometry("450x320")
    root.title("Secondary Button Real-Time Validation Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    widget = sCTkButtonSecondary(base, text="System Action Button")
    widget.pack(padx=40, pady=10, fill="x")

    def toggle_disabled_lock():
        target = "disabled" if widget.get_state() == "normal" else "normal"
        widget.configure(state=target)
        btn_lock.configure(text="Lock Button" if target == "normal" else "Unlock Button")

    def toggle_skin_mode():
        current_skin = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_skin == "Dark" else "Dark")

    btn_lock = ctk.CTkButton(base, text="Lock Button", command=toggle_disabled_lock)
    btn_lock.pack(pady=5)

    btn_theme = ctk.CTkButton(base, text="Simulate Global Theme Shift", command=toggle_skin_mode)
    btn_theme.pack(side="bottom", pady=10)

    root.mainloop()
