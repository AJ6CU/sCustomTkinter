#!/usr/bin/python3
"""
sCTkSMeterBar - Piece 1 of 2

A standalone, low-profile horizontal discrete LED segment bar widget displaying
simultaneous, independent tracks for incoming S-Units and transmitter SWR ratio levels.
Inherits directly from ctk.CTkFrame to bypass nested framework validation bugs,
and integrates with ThemeableWidget to read centralized style sheets safely.
"""
import os
import math

import customtkinter as ctk
from .themeable_widget import ThemeableWidget

class sCTkSMeterBar(ctk.CTkFrame, ThemeableWidget):
    # Required at the TOP LEVEL of the theme block. inactive_color is distinct
    # from the disabled state: it greys the SWR/PWR labels when those ROWS are
    # switched off via configure_visibility(), which is a visibility flag, not
    # a widget state. Both can apply at once.
    _REQUIRED_THEME_KEYS = ("fg_color", "text_color", "alarm_color",
                            "led_on_color", "led_off_color",
                            "font", "scale_font", "inactive_color")

    # Required inside disabled_map. fg_color deliberately excluded -- the
    # background stays put when disabled and the face carries the signal.
    _REQUIRED_DISABLED_KEYS = ("text_color", "alarm_color",
                               "led_on_color", "led_off_color")

    def __init__(self, master=None, swr_max_value=5.0, swr_visible=True, pwr_visible=True, hide_lower_row=False, width=320, height=110, state="normal", **kw):
        # 1. Initialize our Themeable mixin tracker cleanly
        ThemeableWidget.__init__(self, kw)
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)
        self._state = "normal" if str(state).lower() == "normal" else "disabled"
        self._validate_theme_keys()

        # 2. Background track. Popped because super().__init__() takes it as a
        # separate argument -- but RETAINED on the instance, which is the fix
        # for a real bug: _draw_meter() and _update_theme_colors() both did
        # self._local_defaults.get("fg_color", hardcoded) AFTER this pop
        # removed the key, so the background always rendered the hardcoded
        # fallback and the configured fg_color never applied.
        theme_bg_raw = self._local_defaults.pop("fg_color")
        self._theme_bg_raw = theme_bg_raw

        # 🔑 THE STRUCTURAL CLEAN PURGE: Clear custom analog gauge properties explicitly out of self.final_kw
        # This completely guarantees the native CustomTkinter constructor won't throw a ValueError!
        for led_custom_key in ["fg_color", "text_color", "alarm_color", "led_on_color",
                               "led_off_color", "font", "scale_font", "inactive_color"]:
            self.final_kw.pop(led_custom_key, None)

        # 3. Pass dimensions and sanitized kwargs down to the native parent frame engine safely
        super().__init__(master, width=width, height=height, fg_color=theme_bg_raw, **self.final_kw)

        self.swr_max_value = float(swr_max_value)
        self._default_swr_max_value = 5.0
        self._default_swr_visible = True
        self._default_pwr_visible = True
        self._default_hide_lower_row = False
        self._default_width = 320
        self._default_height = 110

        self._swr_visible = bool(swr_visible)
        self._pwr_visible = bool(pwr_visible)
        self._hide_lower_row = bool(hide_lower_row)

        self._current_s_value = 0.0
        self._current_swr_value = 1.0
        self._current_pwr_value = 0.0

        # 4. Resolve the frame backplane color string and build the Tkinter drawing canvas
        bg_resolved = self._resolve_color(theme_bg_raw)
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0, bd=0, bg=bg_resolved)
        self.canvas.pack(fill="both", expand=True, padx=0, pady=0)

        self.pack_propagate(False)
        self.grid_propagate(False)

        self.canvas.bind("<Configure>", lambda e: self._draw_meter())
        self._finalize_themeable_lifecycle()

    def _validate_theme_keys(self) -> None:
        """
        Hard-fails at construction on an incomplete theme block, naming the
        missing key and where it belongs.

        Raises:
            KeyError: naming the first missing key found.
        """
        name = self.__class__.__name__
        for key in self._REQUIRED_THEME_KEYS:
            if self._local_defaults.get(key) is None:
                raise KeyError(
                    f"'{name}' theme block is missing '{key}' at the top level "
                    f"of sCTkThemes.json."
                )
        for key in self._REQUIRED_DISABLED_KEYS:
            if self._custom_disabled_map.get(key) is None:
                raise KeyError(
                    f"'{name}' theme block is missing '{key}' in disabled_map."
                )

    def _themed(self, key: str):
        """
        Returns the disabled-state value for a key when disabled and one
        exists, otherwise the normal value.

        Distinct from inactive_color, which greys the SWR/PWR labels when
        those rows are switched off. A row can be hidden on an enabled widget,
        and a disabled widget still shows whichever rows are visible.
        """
        if self._state == "disabled" and self._custom_disabled_map.get(key) is not None:
            return self._custom_disabled_map[key]
        return self._local_defaults.get(key)

    def get_state(self) -> str:
        """Returns the current state, "normal" or "disabled"."""
        return self._state

    def state(self, mode: str = None) -> str:
        """
        Gets or sets the widget state.

        This is an output-only instrument -- there is nothing to lock out --
        so disabling dims the face rather than blocking interaction. It exists
        for consistency with the rest of the library, so a panel can disable
        every widget it contains uniformly.

        Args:
            mode: None to query. "normal"/"enabled"/"active" or "disabled" to set.

        Returns:
            The resulting state.
        """
        if mode is None:
            return self._state
        target = str(mode).lower()
        self._state = "normal" if target in ("normal", "enabled", "active") else "disabled"
        if hasattr(self, "canvas") and self.canvas.winfo_exists():
            self._draw_meter()
        return self._state

    def configure_visibility(self, swr_visible=None, pwr_visible=None, hide_lower_row=None):
        """Public configuration mapping hook to alter the lower row layout matrix states live."""
        if swr_visible is not None: self._swr_visible = bool(swr_visible)
        if pwr_visible is not None: self._pwr_visible = bool(pwr_visible)
        if hide_lower_row is not None: self._hide_lower_row = bool(hide_lower_row)
        if self.canvas.winfo_exists(): self._draw_meter()

    def configure(self, *args, **kwargs):
        """Handles Pygubu layout inspector dictionary merges and parameter modifications safely."""
        if args and len(args) == 1:
            # FIX: was `pname = args`, leaving pname as a TUPLE -- every
            # comparison below failed, so all three single-argument queries
            # were dead and fell through to super(). Pygubu could not read any
            # of them. Same bug fixed in sCTkFileExplorer.
            pname = args[0]
            if pname == "state":
                return ("state", "state", "state", "normal", self._state)
            if pname in ["width", "height", "swr_max_value"]:
                fallback = self._default_width if pname == "width" else (self._default_height if pname == "height" else self._default_swr_max_value)
                current = super().cget("width") if pname == "width" else (super().cget("height") if pname == "height" else self.swr_max_value)
                return (pname, pname, pname, str(fallback), str(current))
            return super().configure(*args, **kwargs)

        # FIX: was `if args and isinstance(args, dict)`. args is ALWAYS a
        # tuple, so this never fired and the dict form was dead code.
        if len(args) == 1 and isinstance(args[0], dict): kwargs = {**args[0], **kwargs}
        # state is this library's own property, not a native CTkFrame one.
        if "state" in kwargs: self.state(kwargs.pop("state"))
        if "width" in kwargs:
            w = kwargs["width"]
            kwargs["width"] = int(w) if (w and str(w).strip()) else self._default_width
        if "height" in kwargs:
            h = kwargs["height"]
            kwargs["height"] = int(h) if (h and str(h).strip()) else self._default_height

        if "swr_max_value" in kwargs:
            val = kwargs.pop("swr_max_value")
            self.swr_max_value = self._default_swr_max_value if (val == "" or not str(val).strip()) else float(val)

        if kwargs: super().configure(**kwargs)
        if self.canvas.winfo_exists(): self._draw_meter()

    config = configure
    def cget(self, attribute_name):
        """Public register parameter property getter lookup."""
        if attribute_name == "state": return self._state
        if attribute_name == "swr_max_value": return self.swr_max_value
        if attribute_name == "swr_visible": return self._swr_visible
        if attribute_name == "pwr_visible": return self._pwr_visible
        if attribute_name == "hide_lower_row": return self._hide_lower_row
        return super().cget(attribute_name)

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring canvas backplanes repaint fluidly on theme skin shifts."""
        if hasattr(super(), "_set_appearance_mode"):
            try: super()._set_appearance_mode(mode_string)
            except Exception: pass
        if hasattr(self, "canvas") and self.canvas.winfo_exists():
            self.after(15, self._update_theme_colors)

    def _update_theme_colors(self):
        """Refreshes the canvas widget background color directly from your asset maps."""
        bg_color = self._resolve_color(self._theme_bg_raw)
        self.canvas.configure(bg=bg_color)
        self._draw_meter()

    def _draw_meter(self):
        """Wipes and paints fresh discrete LED lines, scale calibrations, and labels using adaptive look tokens."""
        self.canvas.delete("all")
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width < 10 or height < 10: return

        # No fallbacks: _validate_theme_keys() hard-failed at construction if
        # any of these were missing, so every lookup is guaranteed to resolve.
        bg_color = self._resolve_color(self._theme_bg_raw)
        amber_color = self._resolve_color(self._themed("text_color"))
        red_color = self._resolve_color(self._themed("alarm_color"))
        led_on_color = self._resolve_color(self._themed("led_on_color"))
        led_off_color = self._resolve_color(self._themed("led_off_color"))
        label_font = self._local_defaults.get("font")
        scale_font = self._local_defaults.get("scale_font")
        # FIX: was a fully hardcoded self._resolve_color(("#94A3B8", "#334155"))
        # with no theme lookup at all -- the only colour in this widget the
        # theme could not reach.
        disabled_color = self._resolve_color(self._local_defaults.get("inactive_color"))
        self.canvas.configure(bg=bg_color)

        num_led_segments = 30
        start_x, end_x = 10, width - 30
        total_length = end_x - start_x
        sig_y = int(height * 0.50) if self._hide_lower_row else int(height * 0.28)
        lower_y = int(height * 0.70)
        segment_width = (total_length / num_led_segments) - 1.5

        val = self._current_s_value
        s_fraction = (max(0.0, val) / 9.0) * 0.60 if val <= 9.0 else 0.60 + ((min(69.0, val) - 9.0) / 60.0) * 0.40
        active_sig_segments = int(num_led_segments * max(0.0, min(1.0, s_fraction)))

        for i in range(num_led_segments):
            seg_start_x = start_x + (i * (total_length / num_led_segments))
            is_sig_redzone = i >= int(num_led_segments * 0.60)
            fill = (red_color if is_sig_redzone else led_on_color) if i < active_sig_segments else led_off_color
            self.canvas.create_rectangle(seg_start_x, sig_y - 4, seg_start_x + segment_width, sig_y + 1, fill=fill, outline="")

        bar_scale_mappings = [(0.0, ""), (0.066, "1"), (0.20, "3"), (0.333, "5"), (0.466, "7"), (0.60, "9"), (0.733, "+20"), (0.866, "+40"), (1.0, "+60 dB")]
        for pct, label_str in bar_scale_mappings:
            tx = start_x + (total_length * pct)
            color = red_color if pct >= 0.60 else amber_color
            self.canvas.create_line(tx, sig_y, tx, sig_y - 6, fill=color, width=1)
            if label_str: self.canvas.create_text(tx, sig_y - 14, text=label_str, fill=color, font=scale_font, anchor="center")

        self.canvas.create_text(start_x, sig_y - 14, text="S", fill=amber_color, font=scale_font, anchor="center")
        self.canvas.create_text(start_x + (total_length * 0.5), sig_y + 6, text="SIG", fill=amber_color, font=label_font, anchor="n")

        if self._hide_lower_row: return

        mid_gap_start, mid_gap_end = 13, 17
        def get_swr_fraction(swr_val):
            if swr_val <= 1.0: return 0.0
            if swr_val >= self.swr_max_value: return 1.0
            return (math.log10(swr_val + 0.5) - math.log10(1.5)) / (math.log10(self.swr_max_value + 0.5) - math.log10(1.5))

        active_swr_segments = int(mid_gap_start * get_swr_fraction(self._current_swr_value))
        pwr_total_segments = num_led_segments - mid_gap_end
        active_pwr_segments = int(pwr_total_segments * (max(0.0, min(100.0, self._current_pwr_value)) / 100.0))

        for i in range(num_led_segments):
            seg_start_x = start_x + (i * (total_length / num_led_segments))
            if mid_gap_start <= i < mid_gap_end:
                fill = bg_color
            elif i < mid_gap_start:
                is_swr_redzone = (i / mid_gap_start) >= get_swr_fraction(2.0)
                fill = (red_color if is_swr_redzone else led_on_color) if (i < active_swr_segments and self._swr_visible) else led_off_color
            else:
                pwr_index = i - mid_gap_end
                is_pwr_redzone = pwr_index >= int(pwr_total_segments * 0.8)
                fill = (red_color if is_pwr_redzone else led_on_color) if (pwr_index < active_pwr_segments and self._pwr_visible) else led_off_color
            self.canvas.create_rectangle(seg_start_x, lower_y - 4, seg_start_x + segment_width, lower_y + 1, fill=fill, outline="")

        swr_label_color = amber_color if self._swr_visible else disabled_color
        pwr_label_color = amber_color if self._pwr_visible else disabled_color
        self.canvas.create_text(start_x + (total_length * ((mid_gap_start / num_led_segments) * 0.5)), lower_y - 20, text="SWR", fill=swr_label_color, font=label_font, anchor="n")
        self.canvas.create_text(start_x + (total_length * ((mid_gap_end / num_led_segments) + ((1.0 - (mid_gap_end / num_led_segments)) * 0.5))), lower_y - 20, text="PWR", fill=pwr_label_color, font=label_font, anchor="n")

        swr_ticks = [1.0, 1.5, 2.0]
        if self.swr_max_value > 2.0:
            swr_ticks.extend([round(2.0 + ((self.swr_max_value - 2.0) / 2.0), 1), round(self.swr_max_value, 1)])

        for val in swr_ticks:
            tx = start_x + (total_length * (get_swr_fraction(val) * (mid_gap_start / num_led_segments)))
            color = (red_color if val >= 2.0 else amber_color) if self._swr_visible else disabled_color
            label = (str(int(val)) if val.is_integer() else str(val)) + ("+" if val == self.swr_max_value else "")
            self.canvas.create_line(tx, lower_y, tx, lower_y + 6, fill=color, width=1)
            self.canvas.create_text(tx, lower_y + 12, text=label, fill=color, font=scale_font, anchor="n")

        for val, label in [(0, "0"), (50, "50"), (100, "100%")]:
            tx = start_x + (total_length * ((mid_gap_end / num_led_segments) + ((val / 100.0) * (1.0 - (mid_gap_end / num_led_segments)))))
            color = (red_color if val >= 80 else amber_color) if self._pwr_visible else disabled_color
            self.canvas.create_line(tx, lower_y, tx, lower_y + 6, fill=color, width=1)
            self.canvas.create_text(tx - 4 if val == 100 else tx, lower_y + 12, text=label, fill=color, font=scale_font, anchor="n")
    def set(self, s_value=None, swr_value=None, pwr_value=None):
        """Update any telemetry channel row independently."""
        if s_value is not None: self._current_s_value = float(s_value)
        if swr_value is not None: self._current_swr_value = float(swr_value)
        if pwr_value is not None: self._current_pwr_value = float(pwr_value)
        if self.canvas.winfo_exists(): self._draw_meter()

