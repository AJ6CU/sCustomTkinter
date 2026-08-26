#!/usr/bin/python3
"""
sCTkSMeter - Piece 1 of 2

A custom, theme-compliant analog signal and power output instrument widget.
Inherits directly from ctk.CTkFrame to bypass sub-frame keyword replication bugs,
and integrates with ThemeableWidget to read centralized style sheets safely.
"""
import os
import math

import customtkinter as ctk
from .themeable_widget import ThemeableWidget

class sCTkSMeter(ctk.CTkFrame, ThemeableWidget):
    def __init__(self, master=None, width=250, height=130, **kw):
        # 1. Initialize our Themeable mixin tracker cleanly
        ThemeableWidget.__init__(self, kw)
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 2. 🔑 FIXED FALLBACK VALUE: Set the default background track to an adaptive Light/Dark tuple pair!
        theme_bg_raw = self._local_defaults.pop("fg_color", ("#F8FAFC", "#0A0A0A"))

        # Forcefully scrub custom canvas-drawing parameters out of self.final_kw
        for gauge_custom_key in ["fg_color", "text_color", "alarm_color", "needle_color", "font"]:
            self.final_kw.pop(gauge_custom_key, None)

        # 3. Pass dimensions and sanitized kwargs down to the parent frame engine safely
        super().__init__(master, width=width, height=height, fg_color=theme_bg_raw, **self.final_kw)
        self._current_value = 0.0

        self._default_width = 250
        self._default_height = 130
        self.start_angle = 38
        self.extent_angle = 104

        # 4. Resolve the frame backplane color string and build the Tkinter drawing canvas
        bg_resolved = self._resolve_color(theme_bg_raw)
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0, bd=0, bg=bg_resolved)
        self.canvas.pack(fill="both", expand=True, padx=0, pady=0)

        self.pack_propagate(False)
        self.grid_propagate(False)

        self.canvas.bind("<Configure>", lambda e: self._draw_meter())
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Handles Pygubu layout inspector dictionary merges and parameter modifications safely."""
        if args and len(args) == 1:
            pname = args[0]
            if pname == "width":
                return ('width', 'width', 'Width', self._default_width, super().cget("width"))
            if pname == "height":
                return ('height', 'height', 'Height', self._default_height, super().cget("height"))
            return super().configure(*args, **kwargs)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if "width" in kwargs:
            w = kwargs["width"]
            kwargs["width"] = int(w) if (w and str(w).strip()) else self._default_width
        if "height" in kwargs:
            h = kwargs["height"]
            kwargs["height"] = int(h) if (h and str(h).strip()) else self._default_height

        super().configure(**kwargs)
        if hasattr(self, "canvas") and self.canvas.winfo_exists():
            self._draw_meter()

    config = configure

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring canvas backplanes repaint fluidly on theme skin shifts."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        if hasattr(self, "canvas") and self.canvas.winfo_exists():
            self.after(15, self._update_theme_colors)

    def _update_theme_colors(self):
        """Refreshes the canvas widget background color directly from your asset maps."""
        bg_color = self._resolve_color(self._local_defaults.get("fg_color", ("#F8FAFC", "#0A0A0A")))
        self.canvas.configure(bg=bg_color)
        self._draw_meter()

    def _draw_meter(self):
        """Renders dial arcs, ticks, text readouts, and needles using a single layout coordinate base."""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 10 or height < 10: return

        # 🔑 FIXED FALLBACK VALUES: Ensure the look variables map to adaptive profiles safely
        bg = self._resolve_color(self._local_defaults.get("fg_color", ("#F8FAFC", "#0A0A0A")))
        amber = self._resolve_color(self._local_defaults.get("text_color", ("#FF9100", "#FF9100")))
        red = self._resolve_color(self._local_defaults.get("alarm_color", ("#FF2200", "#FF2200")))
        font = self._local_defaults.get("font", ("Arial", 10, "bold"))
        self.canvas.configure(bg=bg)

        # UNIFIED GEOMETRY BASELINE: Establishes a singular, shared layout pivot for lines and needles
        radius_sig = min(width * 0.52, height * 1.20)
        center_x, center_y = width * 0.48, height * 0.35 + radius_sig

        self.canvas.create_text(center_x, height * 0.12, text="SIGNAL", fill=amber, font=font)
        self.canvas.create_text(center_x, height * 0.80, text="RF OUTPUT", fill=amber, font=font)

        split_frac = 9.0 / 15.0
        split_ang = self.start_angle + (self.extent_angle * (1.0 - split_frac))
        bbox = (center_x - radius_sig, center_y - radius_sig, center_x + radius_sig, center_y + radius_sig)

        self.canvas.create_arc(bbox, start=split_ang, extent=self.start_angle + self.extent_angle - split_ang,
                               style="arc", outline=amber, width=2)
        self.canvas.create_arc(bbox, start=self.start_angle, extent=split_ang - self.start_angle, style="arc",
                               outline=red, width=2)

        for i in range(16):
            frac = i / 15.0
            ang = math.radians(self.start_angle + (self.extent_angle * (1.0 - frac)))

            major = (i in (0, 1, 5, 9, 11, 13, 15))
            is_red = (i > 9)
            l = 10 if major else 5

            x1, y1 = center_x + radius_sig * math.cos(ang), center_y - radius_sig * math.sin(ang)
            x2, y2 = center_x + (radius_sig + l) * math.cos(ang), center_y - (radius_sig + l) * math.sin(ang)
            self.canvas.create_line(x1, y1, x2, y2, fill=red if is_red else amber, width=2.5 if major else 1.2)

            if major:
                label = "" if i == 0 else (f"{i}" if i <= 9 else {11: "+20", 13: "+40", 15: "+60"}.get(i, ""))
                text_radius = radius_sig + 16
                tx, ty = center_x + text_radius * math.cos(ang), center_y - text_radius * math.sin(ang)
                if label: self.canvas.create_text(tx, ty, text=label, fill=red if is_red else amber, font=font)

                if i == 1:
                    ang_zero = math.radians(self.start_angle + (self.extent_angle * (1.0 - 0.0)))
                    sx, sy = center_x + text_radius * math.cos(ang_zero), center_y - text_radius * math.sin(ang_zero)
                    self.canvas.create_text(sx, sy, text="S", fill=amber, font=font)

        self._execute_needle_draw(center_x, center_y, radius_sig)

    def _execute_needle_draw(self, cx, cy, rad):
        """Draws the needle matching the permanent non-linear visual face scale track securely."""
        val = self._current_value
        frac = (max(0.0, val) / 9.0) * (9.0 / 15.0) if val <= 9.0 else (9.0 / 15.0) + (
                    (min(69.0, val) - 9.0) / 60.0) * (6.0 / 15.0)
        frac = max(0.0, min(1.0, frac))
        ang = math.radians(self.start_angle + (self.extent_angle * (1.0 - frac)))

        nx, ny = cx + (rad + 2) * math.cos(ang), cy - (rad + 2) * math.sin(ang)
        bx, by = cx + (rad - 60) * math.cos(ang), cy - (rad - 60) * math.sin(ang)
        color = self._resolve_color(self._local_defaults.get("needle_color", ("#94A3B8", "#FF9100")))

        self.canvas.delete("needle")
        self.canvas.create_line(bx, by, nx, ny, fill=color, width=2, tags="needle")

    def set(self, value):
        """Update the needle position indicator (Expects tracking values between 0.0 and 69.0)."""
        self._current_value = max(0.0, min(69.0, float(value)))
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w > 10 and h > 10:
            rad = min(w * 0.52, h * 1.20)
            self._execute_needle_draw(w * 0.48, h * 0.35 + rad, rad)

