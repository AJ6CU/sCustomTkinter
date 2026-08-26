#!/usr/bin/python3
"""
sCTkScrollbar - Piece 1 of 2

An advanced, theme-compliant custom scrollbar component and native container.
Inherits cleanly from ctk.CTkScrollbar to preserve native macOS high-precision
touchpad event streams and keep global light/dark theme tracking active.
"""
import sys
import os
import platform
import tkinter as tk

import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkScrollbar(ctk.CTkScrollbar, ThemeableWidget):
    def __init__(self, master=None, **kwargs):
        # 1. Run shared mixin logic first to parse master themes.json safely
        ThemeableWidget.__init__(self, kwargs)
        self._local_defaults = dict(self.final_kw)

        # 2. Track orientation layout constraints cleanly
        orientation = kwargs.get("orientation", "vertical").lower()
        self._is_horizontal = orientation == "horizontal"

        # 3. Securely set default sizes based on orientation layout rules
        if self._is_horizontal:
            self.final_kw.setdefault("height", 14)
        else:
            self.final_kw.setdefault("width", 14)

        # 4. Initialize CustomTkinter natively so Apple Magic Mouse / trackpad streams stay intact
        super().__init__(master, **self.final_kw)
        self._apply_custom_theme_colors()
        self._finalize_themeable_lifecycle()

    def _apply_custom_theme_colors(self):
        """Cascades color profiles directly out of your centralized stylesheet json maps."""
        normal_color = self._local_defaults.get("button_color", ["#64748B", "#4B5563"])
        normal_hover = self._local_defaults.get("button_hover_color", ["#1A4375", "#2471A3"])

        super().configure(
            button_color=tuple(normal_color) if isinstance(normal_color, list) else normal_color,
            button_hover_color=tuple(normal_hover) if isinstance(normal_hover, list) else normal_hover
        )

    def configure(self, *args, **kwargs):
        """Processes standard configuration queries and manages visual refreshes safely."""
        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if kwargs:
            super().configure(**kwargs)
        self._apply_custom_theme_colors()

    config = configure

    def _set_appearance_mode(self, mode_string: str):
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._apply_custom_theme_colors()


class sCTkScrollArea(ctk.CTkFrame):
    """
    An unblocked scrollable container frame supporting high-precision Apple momentum streams.
    Bypasses rigid layout masks to give developers full opt-in control over child event bundling.
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, fg_color="transparent", border_width=0, **kwargs)

        current_mode = str(ctk.get_appearance_mode()).lower()
        initial_bg = "#FAFAFA" if current_mode == "light" else "#1A1A1A"

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=initial_bg)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scroll_content = tk.Frame(self.canvas, bd=0, bg=initial_bg)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")

        # INERTIAL ACCUMULATOR BUFFER: Traps and stabilizes fine-grained Apple micro-ticks
        self._accumulated_delta = 0.0
        self._last_direction = 0

        # Integrated standard wheel and modern <TouchpadScroll> straight across the core layer
        for ev in ["<MouseWheel>", "<Button-4>", "<Button-5>", "<TouchpadScroll>"]:
            self.canvas.bind(ev, self.process_incoming_scroll)
            self.scroll_content.bind(ev, self.process_incoming_scroll)

        self.scroll_content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width()))

    def hook_scrollbar(self, scrollbar_widget):
        """Pure native alignment pass: Maps tracking parameters without forcing event shifts."""
        self.canvas.configure(yscrollcommand=scrollbar_widget.set)
        scrollbar_widget.configure(command=self.canvas.yview)

    def propagate_scroll_events(self, target_widget: tk.Widget):
        """Recursively binds viewport scroll vectors down onto a targeted widget and its children."""
        for ev in ["<MouseWheel>", "<Button-4>", "<Button-5>", "<TouchpadScroll>"]:
            target_widget.bind(ev, self.process_incoming_scroll)

        if hasattr(target_widget, "winfo_children"):
            for child in target_widget.winfo_children():
                self.propagate_scroll_events(child)

    def _set_appearance_mode(self, mode_string: str):
        if hasattr(super(), "_set_appearance_mode"):
            super()._set_appearance_mode(mode_string)
        target_bg = "#FAFAFA" if str(mode_string).lower() == "light" else "#1A1A1A"
        if hasattr(self, "canvas") and self.canvas: self.canvas.configure(bg=target_bg)
        if hasattr(self, "scroll_content") and self.scroll_content: self.scroll_content.configure(bg=target_bg)

    def process_incoming_scroll(self, event):
        """THE OVERFLOW-INSULATED VECTOR ENGINE: Decodes 16-bit unsigned hardware loops natively."""
        bbox = self.canvas.bbox("all")
        if not bbox: return

        total_height = max(1, bbox[3] - bbox[1])
        fractional_row_step = 28.0 / total_height

        if os.name == "nt" or sys.platform.startswith("win"):
            direction = int(-1 * (event.delta / 120))
            self.canvas.yview_scroll(direction * 2, "units")
            return

        # MAC OS TOUCHPAD HARDWARE NORMALIZATION PASS:
        raw_delta = getattr(event, "delta", 0.0)
        delta_y = event.delta_y if hasattr(event, "delta_y") else raw_delta

        if event.num == 4:
            delta_y = 1.0
        elif event.num == 5:
            delta_y = -1.0

        # Two's complement signed intercept: Convert unsigned 16-bit overflows back to clean negatives
        if delta_y > 32768:
            delta_y = delta_y - 65536

        if delta_y == 0:
            return

        current_tick_direction = 1 if delta_y > 0 else -1
        if current_tick_direction != self._last_direction and self._last_direction != 0:
            self._accumulated_delta = 0.0
        self._last_direction = current_tick_direction

        self._accumulated_delta += delta_y

        # DAMPED ACCUMULATION GATE: 12.0 threshold for perfectly weighted Apple trackpad precision
        if abs(self._accumulated_delta) >= 12.0:
            direction = -1 if self._accumulated_delta > 0 else 1
            try:
                self.canvas.yview_scroll(direction * 1, "units")
            except Exception:
                pass
            self._accumulated_delta = 0.0

