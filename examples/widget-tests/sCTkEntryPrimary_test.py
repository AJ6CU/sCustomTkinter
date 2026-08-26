#!/usr/bin/python3
"""
sCTkEntryPrimary - Piece 1 of 2

A custom, theme-compliant dominant data and frequency entry field widget.
Fortified with explicit platform look-caching and an inline readonly state shift
to permanently guarantee entry fields update fluidly across all mode shifts.
"""
import tkinter as tk
import customtkinter as ctk
from ThemeableWidget import ThemeableWidget

class sCTkEntryPrimary(ctk.CTkEntry, ThemeableWidget):
    def __init__(self, master=None, **kw):
        print("\n[Forensic Check] SHTKENTRYPRIMARY ACTIVE AND MONITORED!\n")

        # 1. Fire our shared theme logic first. It automatically finds "sCTkEntryPrimary" in themes.json
        ThemeableWidget.__init__(self, kw)

        # 2. Store your custom maps safely onto instance memory channels using explicit dict copies
        self._local_defaults = dict(self.final_kw)
        self._widget_custom_disabled_map = dict(self._widget_disabled_map)

        # Extract custom parameters from final_kw to prevent parent constructor collisions
        state_init = self.final_kw.pop("state", "normal")

        # 3. Initialize CustomTkinter natively as a pure programmatic entry asset
        super().__init__(master, **self.final_kw)

        # Execute initialization state routing safely via public channels
        self._virtual_state = "normal"
        self.state(state_init)

        # 🔑 4. REGISTER LIFECYCLE HANDSHAKE HOOK:
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Handles both standard keyword configurations and Pygubu inspector queries cleanly."""
        if args and len(args) == 1:
            pname = args if isinstance(args, (list, tuple)) else args
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "text_color", "border_color", "placeholder_text_color"]:
                val = self._widget_custom_disabled_map.get(pname) if self._virtual_state == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(pname)

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
    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring active or disabled text lanes repaint fluidly on theme shifts."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._update_current_visual_state()

    def get_state(self):
        """Explicit getter synchronized with your standalone test harness script assertions."""
        return self.state()

    def state(self, state_string=None):
        """Standard Tkinter state management mapping helper."""
        if state_string is None:
            return getattr(self, "_virtual_state", "normal")

        mode = str(state_string).lower()
        if mode in ("normal", "enabled", "active"):
            self._virtual_state = "normal"
        elif mode == "disabled":
            self._virtual_state = "disabled"

        self._update_current_visual_state()
        return self._virtual_state

    def _update_current_visual_state(self):
        """
        MASTER VISUAL ROUTER FIXED:
        🔑 REPAINT LOGIC DYNAMIC MAP: Loops fluidly across both modes uniformly, routing input
        blocks via native "readonly" states to completely prevent light/dark whiteout freezes!
        """
        is_disabled = self._virtual_state == "disabled"
        target_map = self._widget_custom_disabled_map if is_disabled else self._local_defaults

        # 1. Map styling color variables cleanly out of configuration directories
        config_payload = {}
        for key in ("fg_color", "border_color", "text_color", "placeholder_text_color"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

        if config_payload:
            super().configure(**config_payload)

        # 2. SEQUENTIAL READONLY LOCK PASS:
        # We execute the native state flag configuration using "readonly" instead of "disabled".
        # This completely seals keyboard entries without freezing internal text rendering engines!
        if is_disabled:
            super().configure(state="readonly")
        else:
            super().configure(state="normal")


# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
import sCTkThemes
from sCTkFrame import sCTkFrame

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("500x450")
    root.title("sCTkEntryPrimary Real-Time Validation Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    widget = sCTkEntryPrimary(base, placeholder_text="Enter Transceiver Callsign...")
    widget.pack(fill="x", padx=20, pady=20)

    def toggle_logger_states():
        """Cycles operational states between active feed and locked desaturated tracks."""
        current_state = widget.get_state()
        target = "disabled" if current_state == "normal" else "normal"

        widget.configure(state=target)
        btn_toggle.configure(text="Activate Entry Field" if target == "disabled" else "Lock Entry Field")
        print(f"Logged Verification Hook -> widget.get_state() = {widget.get_state().upper()}")

    def toggle_appearance_skin():
        current_mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_mode == "Dark" else "Dark")

    btn_toggle = ctk.CTkButton(base, text="Lock Entry Field", command=toggle_logger_states)
    btn_toggle.pack(fill="x", padx=10, pady=5)

    btn_theme = ctk.CTkButton(base, text="Toggle Theme Skin", command=toggle_appearance_skin)
    btn_theme.pack(fill="x", padx=10, pady=5)

    root.mainloop()
