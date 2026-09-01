#!/usr/bin/python3
"""
sCTkDial - Piece 1 of 4

Centralized Foundable Base Class for Theme-Adaptive Rotary Encoders.
Coordinates 3D knob geometry structures, vector math layers, and hardware delta masks.
"""
import sys
import math
import time
import ast
import customtkinter as ctk
from . import themeable_widget as _tw
from .themeable_widget import ThemeableWidget
class sCTKDialBase(ctk.CTkFrame, ThemeableWidget):
    """Abstract Base Class for theme-adaptive mechanical rotary encoder widgets."""

    def __init__(self, master=None, divisions=24, state="normal", width=120, height=120, **kw):
        ThemeableWidget.__init__(self, kw)
        # THEME SOURCE -- read the RAW block, not final_kw.
        #
        # ThemeableWidget maintains a CUSTOM_VECTOR_KEYS set (dial_color,
        # shadow_color, text_color, pointer_color, pointer_glow_color,
        # diameter, ...) which it deliberately strips out of final_kw for
        # vector widgets like this one, so they never reach the native
        # CTkFrame constructor and raise ValueError. That stripping is
        # correct. What was wrong was reading colours back out of final_kw
        # afterwards: those keys were never in there.
        #
        # FIX: every `.get(key) or ("#hex", "#hex")` in the old draw code was
        # therefore ALWAYS taking the hardcoded fallback -- this widget family
        # has never rendered its configured theme colours at all. The values
        # in sCTkThemes.json for dial_color, shadow_color, text_color and
        # pointer_glow_color were decorative. Surfaced by _validate_theme_keys()
        # the first time fail-loud checking was applied here.
        #
        # Module-attribute access rather than a direct name import, because
        # load_initial_framework_themes() REBINDS GLOBAL_THEME_REGISTRY on
        # load; a `from ... import GLOBAL_THEME_REGISTRY` would capture the
        # empty dict that existed at import time.
        raw_block = _tw.GLOBAL_THEME_REGISTRY.get(self.__class__.__name__) or {}
        raw_colors = {k: v for k, v in raw_block.items() if not isinstance(v, dict)}
        self._local_defaults = ThemeableWidget._convert_lists_to_tuples(raw_colors)
        # final_kw still wins where it has a value, so constructor overrides
        # and non-vector theme keys keep their existing precedence.
        self._local_defaults.update(self.final_kw)

        self._custom_disabled_map = dict(self._widget_disabled_map)
        self._validate_theme_keys()

        target_diameter = self._local_defaults.get("diameter")
        if target_diameter is not None:
            width, height = int(target_diameter), int(target_diameter)

        FRAME_VALID_KEYS = {"width", "height", "fg_color", "border_color", "border_width", "corner_radius", "bg_color"}
        frame_kwargs = {k: self._local_defaults[k] for k in FRAME_VALID_KEYS if k in self._local_defaults and self._local_defaults[k] is not None}
        frame_kwargs.setdefault("width", width)
        frame_kwargs.setdefault("height", height)
        frame_kwargs.setdefault("fg_color", "transparent")

        super().__init__(master, **frame_kwargs)

        self._divisions = int(divisions) if int(divisions) > 0 else 24
        self._state = "normal" if state.lower() == "normal" else "disabled"
        self._current_value = 0
        self._scroll_cooldown_seconds = 0.060
        self._last_scroll_time = 0.0
        self._last_y = 0

        self.canvas = ctk.CTkCanvas(self, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.canvas.bind("<Enter>", lambda e: self._on_mouse_enter())
        self.canvas.bind("<Button-1>", self._on_left_click_step)
        self.canvas.bind("<Button-2>", self._on_right_click_step)
        self.canvas.bind("<Button-3>", self._on_right_click_step)
        self.canvas.bind("<Shift-ButtonPress-1>", self._on_button_press)
        self.canvas.bind("<Shift-B1-Motion>", self._on_button_motion)
        self.canvas.bind("<Configure>", lambda e: self._draw_dial_base())
        self.after(50, self._inject_private_layer_bindings)

    # Keys every dial reads, required at the TOP LEVEL of its theme block.
    _REQUIRED_THEME_KEYS = (
        "fg_color", "text_color", "shadow_color", "dial_color",
        "dial_highlight_color", "dial_shadow_color",
        "dial_rim_light_color", "dial_rim_shadow_color",
    )

    # Keys required inside disabled_map. Deliberately excludes fg_color: the
    # background does NOT dim when disabled, the knob face and text carry the
    # signal. Matches the choice made for sCTkScrollableFrame.
    _REQUIRED_DISABLED_KEYS = ("text_color", "dial_color")

    def _validate_theme_keys(self) -> None:
        """
        Hard-fails at construction on an incomplete theme block, naming the
        missing key and where it belongs.

        Replaces the previous pattern of `.get(key) or ("#hex", "#hex")`
        throughout the draw routine, which silently substituted a plausible
        guess whenever the theme was incomplete -- so a broken block looked
        merely slightly-off rather than broken. Same fail-loud principle used
        for sCTkTabview and sCTkScrollableFrame.

        Subclasses extend the requirements via _EXTRA_THEME_KEYS and
        _EXTRA_DISABLED_KEYS rather than overriding this, since each dial
        variant reads a slightly different set: only Continuous draws a
        dimple, and only Selector/Range draw a pointer line.

        Raises:
            KeyError: naming the first missing key found.
        """
        name = self.__class__.__name__
        required = self._REQUIRED_THEME_KEYS + getattr(self, "_EXTRA_THEME_KEYS", ())
        required_disabled = self._REQUIRED_DISABLED_KEYS + getattr(self, "_EXTRA_DISABLED_KEYS", ())

        for key in required:
            if self._local_defaults.get(key) is None:
                raise KeyError(
                    f"'{name}' theme block is missing '{key}' at the top level "
                    f"of sCTkThemes.json."
                )
        for key in required_disabled:
            if self._custom_disabled_map.get(key) is None:
                raise KeyError(
                    f"'{name}' theme block is missing '{key}' in disabled_map."
                )

    def _inject_private_layer_bindings(self):
        layers_to_bind = [self.canvas, self]
        if hasattr(self, "_canvas") and self._canvas is not None:
            layers_to_bind.append(self._canvas)
        for target_layer in layers_to_bind:
            if sys.platform == "darwin":
                target_layer.bind("<TouchpadScroll>", self._process_mac_touchpad_scroll, add="+")
            target_layer.bind("<MouseWheel>", self._process_scroll_wheel, add="+")
            target_layer.bind("<Button-4>", self._process_scroll_wheel, add="+")
            target_layer.bind("<Button-5>", self._process_scroll_wheel, add="+")

    def _on_mouse_enter(self):
        if self._state == "normal": self.canvas.focus_set()

    def _set_appearance_mode(self, mode_string):
        if hasattr(super(), "_set_appearance_mode"):
            try: super()._set_appearance_mode(mode_string)
            except Exception: pass
        if hasattr(self, "canvas") and self.canvas.winfo_exists():
            self.after(20, self._process_theme_repaint)

    def _process_theme_repaint(self):
        """🔑 TRANSPARENCY SHIELD FIXED: Resolves transparent settings to parent hex values."""
        theme_bg_raw = self._local_defaults.get("fg_color", "transparent")
        if self._state == "disabled":
            theme_bg_raw = self._custom_disabled_map.get("fg_color", "transparent")

        resolved_bg = self._resolve_color(theme_bg_raw)

        if resolved_bg == "transparent":
            current_parent = self.master
            while current_parent is not None:
                if hasattr(current_parent, "cget"):
                    try:
                        p_color = current_parent.cget("fg_color")
                        if p_color and p_color not in ("transparent", ""):
                            resolved_bg = self._resolve_color(p_color)
                            break
                    except Exception:
                        pass
                current_parent = getattr(current_parent, "master", None)

            if resolved_bg == "transparent":
                resolved_bg = "#1C1C1C" if str(ctk.get_appearance_mode()).lower() == "dark" else "#F1F5F9"

        self.canvas.configure(bg=resolved_bg)
        if hasattr(self, "_draw_dial_base"): self._draw_dial_base()

    def _decode_mac_touchpad_delta(self, raw_delta):
        raw = raw_delta & 0xFFFFFFFF
        delta_y = raw & 0xFFFF
        if delta_y >= 0x8000: delta_y -= 0x10000
        return delta_y

    def configure(self, *args, **kwargs):
        """Handles Pygubu designer queries and manages composite state updates safely."""
        if args and len(args) == 1:
            pname = args if isinstance(args, (list, tuple)) else args
            if pname == "width":
                return ('width', 'width', 'Width', 120, super().cget("width") if hasattr(self, "cget") else 120)
            if pname == "height":
                return ('height', 'height', 'Height', 120, super().cget("height") if hasattr(self, "cget") else 120)
            if pname == "state":
                return ('state', 'state', 'State', 'normal', getattr(self, "_state", "normal"))
            if pname == "labels":
                return ('labels', 'labels', 'Labels', "POS 1, POS 2, POS 3",
                        ", ".join(getattr(self, "_labels", ["POS 1", "POS 2", "POS 3"])))
            if pname in ["diameter", "divisions", "arc_angle", "from_", "to", "command", "left_click_callback",
                         "right_click_callback"]:
                return (pname, pname, pname, "", "")
            try:
                return super().configure(pname)
            except Exception:
                return (pname, pname, pname, "", "")

        # FIX: was `if args and isinstance(args, dict)`. args is ALWAYS a
        # tuple, so this never fired and the dict form of configure() was
        # dead code. Same tautology fixed across the batch-one widgets.
        if len(args) == 1 and isinstance(args[0], dict):
            kwargs = {**args[0], **kwargs}

        if "width" in kwargs:
            w = kwargs["width"]
            kwargs["width"] = int(w) if (w and str(w).strip()) else 120
        if "height" in kwargs:
            h = kwargs["height"]
            kwargs["height"] = int(h) if (h and str(h).strip()) else 120

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        if kwargs:
            for k, v in list(kwargs.items()):
                if v == "": kwargs.pop(k)
            if kwargs: return super().configure(**kwargs)
        return None


    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does NOT track whichever configure() a subclass defines.
    # Without this, .config(...) skips every override in this class and lands
    # on the native widget, bypassing divisions/command/diameter handling and
    # the theme repaint entirely. Confirmed as a critical bug on
    # sCTkSegmentedButton earlier in this project's audit. Each subclass needs
    # its own line -- inheriting the alias would point at the PARENT's
    # configure(), not the subclass's.
    config = configure
    def get_state(self) -> str:
        return str(self._state).lower()

    def state(self, mode: str = None) -> str:
        """Dedicated rotary dial operational interaction lock and visibility state controller."""
        if mode is None:
            return str(self._state).lower()

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._state = "normal"
            self._custom_current_state = "normal"

            # 🔑 1. REPAINT CANVAS LAYERS FIRST: Let Tkinter settle its color configurations
            self._process_theme_repaint()

            # 🔑 2. HARDWARE RE-BINDING MATRIX: Clamp the mouse listeners on top of the settled surface!
            try:
                self.canvas.bind("<Button-1>", self._on_left_click_step)
                self.canvas.bind("<Button-2>", self._on_right_click_step)
                self.canvas.bind("<Button-3>", self._on_right_click_step)
                self._inject_private_layer_bindings()
            except Exception:
                pass

        elif mode == "disabled":
            self._state = "disabled"
            self._custom_current_state = "disabled"
            SCROLL_EVENTS = ["<MouseWheel>", "<TouchpadScroll>", "<Button-4>", "<Button-5>", "<Shift-ButtonPress-1>",
                             "<Shift-B1-Motion>"]
            try:
                self.canvas.unbind("<Button-1>")
                self.canvas.unbind("<Button-2>")
                self.canvas.unbind("<Button-3>")
                for ev in SCROLL_EVENTS: self.canvas.unbind(ev)
            except Exception:
                pass
            self._process_theme_repaint()

        return str(self._state).lower()

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "state": return getattr(self, "_state", "normal")
        if attribute_name == "diameter": return self.winfo_width()
        if attribute_name == "divisions": return getattr(self, "_divisions", 24)
        return super().cget(attribute_name)

    # ------------------------------------------------------------------
    # Knob shading
    # ------------------------------------------------------------------
    # Number of concentric ovals used to fake a radial gradient. Tk's canvas
    # has no gradient primitive and no alpha channel, so the only way to get a
    # domed surface is to stack solid-filled ovals, each slightly smaller and
    # shifted toward the light source. Below ~12 the steps read as visible
    # contour bands; above ~24 the extra items cost more than they show.
    KNOB_SHADE_STEPS = 18

    # How far the ring stack shrinks from edge to centre, and how far each
    # step drifts toward the light. Both as fractions of the knob radius.
    KNOB_SHADE_SHRINK = 0.55
    KNOB_LIGHT_OFFSET = 0.55

    # Finger dimple, as fractions of knob radius -- NOT absolute pixels. The
    # previous code used a fixed 14px inset with a fixed 14.5px radius, so the
    # dimple was lost on a large dial and swallowed a small one.
    DIMPLE_RADIUS_FRAC = 0.36
    DIMPLE_RIM_CLEARANCE_FRAC = 0.06

    # Pointer line for Selector/Range: width in px, and how far short of the
    # rim it stops.
    POINTER_WIDTH = 3.0
    POINTER_RIM_INSET = 3

    @staticmethod
    def _lerp_color(color_a: str, color_b: str, t: float) -> str:
        """
        Blends two resolved "#RRGGBB" strings.

        Both inputs must already be resolved to a single colour by
        _resolve_color() -- this cannot accept (light, dark) tuples.

        Args:
            color_a: Start colour at t=0.
            color_b: End colour at t=1.
            t: Position between them, 0.0 to 1.0.

        Returns:
            The blended colour as "#RRGGBB".
        """
        a = tuple(int(color_a[i:i + 2], 16) for i in (1, 3, 5))
        b = tuple(int(color_b[i:i + 2], 16) for i in (1, 3, 5))
        return "#%02X%02X%02X" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

    def _draw_shaded_disc(self, cx, cy, radius, edge_color, centre_color, tag,
                          rim_light=None, rim_shadow=None, recessed=False):
        """
        Draws a domed (or recessed) disc as a stack of concentric ovals.

        The light source is the upper left. For a DOME each successive ring
        shrinks and drifts toward that light, so the bright end of the ramp
        lands off-centre where a highlight would fall. For a RECESS the drift
        is inverted -- a hole lit from the upper left is shadowed on its
        upper-left interior wall and lit on the lower right. Getting that
        backwards is what makes a dimple pop outward as a bump instead of
        sinking in.

        Args:
            cx, cy: Centre of the disc.
            radius: Outer radius.
            edge_color: Resolved colour at the outer edge.
            centre_color: Resolved colour at the lit end of the ramp.
            tag: Canvas tag applied to every item, so the whole disc can be
                deleted as a unit.
            rim_light: Optional resolved colour for the lit rim arc.
            rim_shadow: Optional resolved colour for the shaded rim arc.
            recessed: True to invert the light direction (see above).
        """
        direction = -1.0 if recessed else 1.0
        for i in range(self.KNOB_SHADE_STEPS):
            t = i / (self.KNOB_SHADE_STEPS - 1)
            r = radius * (1.0 - self.KNOB_SHADE_SHRINK * t)
            drift = (radius - r) * self.KNOB_LIGHT_OFFSET * direction
            x, y = cx - drift, cy - drift
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                    fill=self._lerp_color(edge_color, centre_color, t),
                                    outline="", tags=tag)

        # Rim lighting. On a dark knob this does most of the work: the body
        # ramp is clamped at the bottom (you can't go darker than black), so
        # the bright upper-left arc is what reads as a curved edge rather than
        # a flat cut-out.
        if rim_light:
            lit_start, shade_start = (225, 45) if not recessed else (45, 225)
            self.canvas.create_arc(cx - radius, cy - radius, cx + radius, cy + radius,
                                   start=lit_start, extent=180, style="arc",
                                   outline=rim_light, width=2.5, tags=tag)
            if rim_shadow:
                self.canvas.create_arc(cx - radius, cy - radius, cx + radius, cy + radius,
                                       start=shade_start, extent=180, style="arc",
                                       outline=rim_shadow, width=2.5, tags=tag)

    def _redraw_indicator(self):
        """
        Redraws only the moving indicator -- the dimple or the pointer line --
        leaving the knob body, ticks and labels alone.

        Call this on a VALUE change. Call _draw_dial_base() only when the
        geometry, theme or state changes.

        The body is now a stack of ~20 shaded ovals plus ticks and labels, and
        none of it changes as the dial turns. Rebuilding all of it per detent
        made the shading cost real; this makes it free while tuning. Same
        pattern as sCTkSMeter._execute_needle_draw(), which redraws its needle
        against a static face.
        """
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists(): return
        if not self.canvas.find_withtag("knob_body"):
            # Body was never drawn (first paint, or a resize wiped it), so a
            # partial update would leave the dial blank. Do the full pass.
            self._draw_dial_base()
            return
        self._draw_dial_base(indicator_only=True)

    def _draw_dial_base(self, indicator_only: bool = False):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists(): return
        if not indicator_only:
            self.canvas.delete("all")
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width < 10 or height < 10: width = height = int(self.cget("width") if hasattr(self, "cget") else 120)

        child_classname = self.__class__.__name__
        # No `or ("#hex", "#hex")` fallbacks: _validate_theme_keys() hard-failed
        # at construction if any of these were missing, so every lookup here is
        # guaranteed to resolve. A fallback would only reintroduce the silent
        # substitution that made an incomplete theme block invisible.
        bg_color = self._resolve_color(self._local_defaults.get("fg_color"))
        shadow_paint = self._resolve_color(self._local_defaults.get("shadow_color"))
        text_color = self._resolve_color(self._local_defaults.get("text_color"))
        dial_color = self._resolve_color(self._local_defaults.get("dial_color"))
        is_dark_mode = (ctk.get_appearance_mode() == "Dark")

        # Knob shading colours. Explicit rather than derived from dial_color:
        # a fixed lighten/darken percentage produces a nearly invisible rim on
        # a black knob and a blown-out one on aluminium, because the available
        # range differs enormously between them.
        knob_highlight = self._resolve_color(self._local_defaults.get("dial_highlight_color"))
        knob_shadow = self._resolve_color(self._local_defaults.get("dial_shadow_color"))
        rim_light = self._resolve_color(self._local_defaults.get("dial_rim_light_color"))
        rim_shadow = self._resolve_color(self._local_defaults.get("dial_rim_shadow_color"))

        if self._state == "disabled":
            text_color = self._resolve_color(self._custom_disabled_map.get("text_color"))
            # FIX: this previously read "fg_color" for BOTH the dial face and
            # the background, so once disabled_map actually contained fg_color
            # the knob would render the same colour as the surface behind it
            # and vanish. The two only looked different before because the map
            # was empty and their hardcoded fallbacks happened to differ.
            dial_color = self._resolve_color(self._custom_disabled_map.get("dial_color"))
            knob_highlight = self._resolve_color(
                self._custom_disabled_map.get("dial_highlight_color") or self._custom_disabled_map.get("dial_color"))
            knob_shadow = self._resolve_color(
                self._custom_disabled_map.get("dial_shadow_color") or self._custom_disabled_map.get("dial_color"))
            rim_light = self._resolve_color(
                self._custom_disabled_map.get("dial_rim_light_color") or self._custom_disabled_map.get("dial_color"))
            rim_shadow = self._resolve_color(
                self._custom_disabled_map.get("dial_rim_shadow_color") or self._custom_disabled_map.get("dial_color"))
            # Background deliberately NOT dimmed -- the knob face and border
            # carry the disabled signal, matching sCTkScrollableFrame.

        self.canvas.configure(bg=bg_color)
        center_x, center_y = width / 2, height / 2
        knob_radius = min(center_x, center_y) - 28

        has_arc_constraints = hasattr(self, "_arc_angle")
        arc_sweep = float(self._arc_angle) if has_arc_constraints else 360.0
        start_deg = -90.0 - (arc_sweep / 2.0) if has_arc_constraints else 0.0

        if child_classname == "sCTkDialSelector" and hasattr(self, "_labels"):
            if not self._labels or len(self._labels) == 0: self._labels = list(getattr(self, "_default_labels", ["POS 1", "POS 2", "POS 3"]))
            total_ticks = len(self._labels)
            self._divisions = total_ticks
        elif child_classname == "sCTkDialRange" and hasattr(self, "_divisions"):
            total_ticks = int(self._divisions) if (self._divisions and int(self._divisions) > 0) else 5
        else:
            total_ticks = int(self._divisions) if (hasattr(self, "_divisions") and self._divisions) else 24

        if not indicator_only:
            for i in range(total_ticks):
                fraction = (i / (total_ticks - 1)) if (total_ticks > 1 and has_arc_constraints) else (i / total_ticks)
                angle_deg = start_deg + (fraction * arc_sweep)
                angle_rad = math.radians(-angle_deg)
                x1, y1 = center_x + knob_radius * math.cos(angle_rad), center_y - knob_radius * math.sin(angle_rad)
                x2, y2 = center_x + (knob_radius + 6) * math.cos(angle_rad), center_y - (knob_radius + 6) * math.sin(angle_rad)
                self.canvas.create_line(x1, y1, x2, y2, fill=text_color, width=2.0)

                if child_classname == "sCTkDialSelector" and i < len(self._labels):
                    self.canvas.create_text(center_x + (knob_radius + 18) * math.cos(angle_rad), center_y - (knob_radius + 18) * math.sin(angle_rad), text=str(self._labels[i]), fill=text_color, font=("Arial", 9, "bold"))
                elif child_classname == "sCTkDialRange":
                    from_val, to_val = getattr(self, "_from", 0), getattr(self, "_to", 100)
                    range_val = int(from_val + (to_val - from_val) * fraction)
                    self.canvas.create_text(center_x + (knob_radius + 18) * math.cos(angle_rad), center_y - (knob_radius + 18) * math.sin(angle_rad), text=str(range_val), fill=text_color, font=("Arial", 9, "bold"))

            self.canvas.create_oval(center_x - knob_radius + 1, center_y - knob_radius + 4, center_x + knob_radius + 4, center_y + knob_radius + 4, fill=shadow_paint, outline="")

            if child_classname == "sCTkDialContinuous":
                num_side_teeth = 72
                teeth_shadow = "#000000" if is_dark_mode else "#334155"
                for k in range(num_side_teeth):
                    k_angle = math.radians(-(k * (360.0 / num_side_teeth)))
                    self.canvas.create_line(center_x + knob_radius * math.cos(k_angle), center_y - knob_radius * math.sin(k_angle), center_x + (knob_radius - 3) * math.cos(k_angle), center_y - (knob_radius - 3) * math.sin(k_angle), fill=teeth_shadow, width=1.5)

            # The knob body: a stack of concentric ovals stepping from
            # dial_shadow_color at the rim to dial_highlight_color off-centre,
            # replacing what used to be a single flat fill with two hardcoded
            # outline rings. See _draw_shaded_disc().
            self._draw_shaded_disc(center_x, center_y, knob_radius - 2,
                                   knob_shadow, knob_highlight, "knob_body",
                                   rim_light=rim_light, rim_shadow=rim_shadow)

        val_pct = self._get_value_fraction() if hasattr(self, "_get_value_fraction") else 0.0
        pointer_rad = math.radians(-(start_deg + (val_pct * arc_sweep)))

        # Indicator. Tagged separately from the body so a value change can
        # redraw ONLY this -- see _redraw_indicator(). The body is expensive
        # now and doesn't change while the dial is turned.
        self.canvas.delete("indicator")

        if child_classname in ["sCTkDialSelector", "sCTkDialRange"]:
            # A plain straight line from dead centre out to just short of the
            # rim, which is how these knobs are actually marked. The previous
            # version drew an arrowhead and a centre cap; both are gone, along
            # with the cap's two hardcoded outline colours.
            px = center_x + (knob_radius - self.POINTER_RIM_INSET) * math.cos(pointer_rad)
            py = center_y - (knob_radius - self.POINTER_RIM_INSET) * math.sin(pointer_rad)
            pointer_key = "pointer_color"
            raw_pointer = (self._custom_disabled_map.get(pointer_key) or self._custom_disabled_map.get("text_color")
                           if self._state == "disabled"
                           else self._local_defaults.get(pointer_key) or self._local_defaults.get("text_color"))
            self.canvas.create_line(center_x, center_y, px, py,
                                    fill=self._resolve_color(raw_pointer),
                                    width=self.POINTER_WIDTH, capstyle="round",
                                    tags="indicator")
        else:
            # Continuous only: the finger dimple a VFO operator spins the dial
            # by. Sized as a FRACTION of knob_radius so it holds its
            # proportions at any dial size.
            # Resolved HERE rather than above, because only this branch draws
            # a dimple. The previous code resolved it for every dial, so
            # Selector and Range looked up a key they never used -- which is
            # why pointer_glow_color appeared "missing" from their theme
            # blocks. It belongs to Continuous alone.
            pointer_glow = self._resolve_color(
                self._custom_disabled_map.get("pointer_glow_color") if self._state == "disabled"
                else self._local_defaults.get("pointer_glow_color"))

            ind_radius = knob_radius * self.DIMPLE_RADIUS_FRAC
            clearance = knob_radius * self.DIMPLE_RIM_CLEARANCE_FRAC
            dimple_center_radius = knob_radius - ind_radius - clearance
            dx = center_x + dimple_center_radius * math.cos(pointer_rad)
            dy = center_y - dimple_center_radius * math.sin(pointer_rad)

            # recessed=True inverts the light direction: a hole lit from the
            # upper left is shadowed on its upper-left interior wall. Drawn
            # with the body's direction it would read as a raised bump.
            self._draw_shaded_disc(dx, dy, ind_radius, knob_highlight, knob_shadow,
                                   "indicator", rim_light=rim_shadow,
                                   rim_shadow=rim_light, recessed=True)
            self.canvas.create_oval(dx - ind_radius, dy - ind_radius, dx + ind_radius, dy + ind_radius,
                                    fill="", outline=pointer_glow, width=1.5, tags="indicator")
class sCTkDialContinuous(sCTKDialBase):
    # Only this variant draws the finger dimple, so only it requires the glow
    # ring colour -- see _draw_dial_base()'s indicator branch.
    _EXTRA_THEME_KEYS = ("pointer_glow_color",)
    _EXTRA_DISABLED_KEYS = ("pointer_glow_color",)

    def __init__(self, master=None, divisions=24, command=None, left_click_callback=None, right_click_callback=None, diameter=120, **kw):
        super().__init__(master, divisions=divisions, diameter=diameter, **kw)
        self._command = command
        self._left_click_callback = left_click_callback if (left_click_callback and str(left_click_callback).strip()) else None
        self._right_click_callback = right_click_callback if (right_click_callback and str(right_click_callback).strip()) else None
        self._current_value = 0
        self._finalize_themeable_lifecycle()

    def _get_value_fraction(self): return self._current_value / self._divisions
    def configure(self, *args, **kwargs):
        if args: return super().configure(*args, **kwargs)
        if "divisions" in kwargs: self._divisions = int(kwargs.pop("divisions"))
        if "command" in kwargs: self._command = kwargs.pop("command")
        if "left_click_callback" in kwargs: self._left_click_callback = kwargs.pop("left_click_callback")
        if "right_click_callback" in kwargs: self._right_click_callback = kwargs.pop("right_click_callback")
        if "diameter" in kwargs:
            d = int(kwargs.pop("diameter"))
            kwargs["width"], kwargs["height"] = d, d
        result = super().configure(**kwargs)
        if hasattr(self, "canvas") and self.canvas.winfo_exists(): self._draw_dial_base()
        return result


    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does NOT track whichever configure() a subclass defines.
    # Without this, .config(...) skips every override in this class and lands
    # on the native widget, bypassing divisions/command/diameter handling and
    # the theme repaint entirely. Confirmed as a critical bug on
    # sCTkSegmentedButton earlier in this project's audit. Each subclass needs
    # its own line -- inheriting the alias would point at the PARENT's
    # configure(), not the subclass's.
    config = configure
    def cget(self, attribute_name: str) -> any:
        if attribute_name == "command": return self._command
        if attribute_name == "left_click_callback": return self._left_click_callback
        if attribute_name == "right_click_callback": return self._right_click_callback
        return super().cget(attribute_name)

    def set_position_index(self, step_delta):
        self._current_value = (self._current_value + int(step_delta)) % self._divisions
        if self.canvas.winfo_exists(): self._redraw_indicator()
        if self._command is not None and self._state == "normal": self._command(int(step_delta))

    def _on_left_click_step(self, event):
        if self._state == "disabled": return
        if self._left_click_callback is not None: self._left_click_callback()
        else: self.set_position_index(-1)

    def _on_right_click_step(self, event):
        if self._state == "disabled": return
        if self._right_click_callback is not None: self._right_click_callback()
        else: self.set_position_index(1)

    def _on_button_press(self, event): self._last_y = event.y
    def _on_button_motion(self, event):
        if self._state == "disabled": return
        delta_y = self._last_y - event.y
        if abs(delta_y) > 2:
            self.set_position_index(1 if delta_y > 0 else -1)
            self._last_y = event.y

    def _process_mac_touchpad_scroll(self, event):
        if self._state == "disabled": return "break"
        current_time = time.time()
        if current_time - self._last_scroll_time < self._scroll_cooldown_seconds: return "break"
        delta_y = self._decode_mac_touchpad_delta(event.delta)
        if delta_y != 0:
            self._last_scroll_time = current_time
            self.set_position_index(1 if delta_y > 0 else -1)
        return "break"

    def _process_scroll_wheel(self, event):
        if self._state == "disabled": return
        if getattr(event, "num", 0) == 4 or (hasattr(event, "delta") and event.delta > 0): d = 1
        elif getattr(event, "num", 0) == 5 or (hasattr(event, "delta") and event.delta < 0): d = -1
        else: return
        self.set_position_index(d)
class sCTkDialSelector(sCTKDialBase):
    # This variant draws a plain line pointer rather than a dimple, so it
    # requires pointer_color instead of pointer_glow_color. pointer_color was
    # present in the theme file but never read by any code path until now.
    _EXTRA_THEME_KEYS = ("pointer_color",)

    """
    Rotary switch selector module. Constrained to custom arc angles (default 270).
    Loops infinitely past outer limits and reports the active integer item index position.
    """
    def __init__(self, master=None, labels=None, arc_angle=270, command=None, left_click_callback=None, right_click_callback=None, diameter=120, **kw):
        if isinstance(labels, str) and labels.strip():
            try: labels = ast.literal_eval(labels.strip())
            except Exception: labels = [x.strip().strip("'\"") for x in labels.strip()[1:-1].split(",")]
        self._default_labels = ["POS 1", "POS 2", "POS 3"]
        self._labels = labels if labels is not None else list(self._default_labels)
        self._arc_angle = float(arc_angle)
        super().__init__(master, divisions=len(self._labels), diameter=diameter, **kw)
        self._scroll_cooldown_seconds = 0.150
        self._command = command
        self._left_click_callback = left_click_callback if (left_click_callback and str(left_click_callback).strip()) else None
        self._right_click_callback = right_click_callback if (right_click_callback and str(right_click_callback).strip()) else None
        self._current_value = 0
        self._custom_current_state = "normal" if self._state == "normal" else "disabled"
        self._finalize_themeable_lifecycle()

    def _get_value_fraction(self):
        t = len(self._labels) - 1
        return self._current_value / t if t > 0 else 0.0

    def configure(self, *args, **kwargs):
        if args: return super().configure(*args, **kwargs)
        if "labels" in kwargs:
            lbls = kwargs.pop("labels")
            if isinstance(lbls, str):
                s = lbls.strip().strip("[]\"'")
                lbls = [x.strip() for x in s.split(",")] if s else list(self._default_labels)
            self._labels = list(self._default_labels) if not lbls else lbls
            self._divisions = len(self._labels)
        if "arc_angle" in kwargs: self._arc_angle = float(kwargs.pop("arc_angle"))
        if "command" in kwargs: self._command = kwargs.pop("command")
        if "left_click_callback" in kwargs: self._left_click_callback = kwargs.pop("left_click_callback")
        if "right_click_callback" in kwargs: self._right_click_callback = kwargs.pop("right_click_callback")
        if "diameter" in kwargs:
            d = int(kwargs.pop("diameter"))
            kwargs["width"], kwargs["height"] = d, d
        result = super().configure(**kwargs)
        if hasattr(self, "canvas") and self.canvas.winfo_exists(): self._draw_dial_base()
        return result


    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does NOT track whichever configure() a subclass defines.
    # Without this, .config(...) skips every override in this class and lands
    # on the native widget, bypassing divisions/command/diameter handling and
    # the theme repaint entirely. Confirmed as a critical bug on
    # sCTkSegmentedButton earlier in this project's audit. Each subclass needs
    # its own line -- inheriting the alias would point at the PARENT's
    # configure(), not the subclass's.
    config = configure
    def cget(self, attribute_name: str) -> any:
        if attribute_name == "labels": return self._labels
        if attribute_name == "arc_angle": return self._arc_angle
        if attribute_name == "command": return self._command
        return super().cget(attribute_name)

    def set(self, value):
        t = len(self._labels)
        if t == 0: return
        target = int(value)
        if target >= t: target = 0
        elif target < 0: target = t - 1
        self._current_value = target
        if self.canvas.winfo_exists(): self._redraw_indicator()
        if self._command is not None and self._state == "normal": self._command(self._current_value)

    def get(self): return self._current_value
    def _on_left_click_step(self, event):
        if self._state == "disabled": return
        if self._left_click_callback is not None: self._left_click_callback()
        else: self.set(self._current_value - 1)

    def _on_right_click_step(self, event):
        if self._state == "disabled": return
        if self._right_click_callback is not None: self._right_click_callback()
        else: self.set(self._current_value + 1)

    def _on_button_press(self, event): self._last_y = event.y
    def _on_button_motion(self, event):
        if self._state == "disabled": return
        delta_y = self._last_y - event.y
        if abs(delta_y) > 25:
            self.set(self._current_value + (1 if delta_y > 0 else -1))
            self._last_y = event.y

    def _process_mac_touchpad_scroll(self, event):
        if self._state == "disabled": return "break"
        current_time = time.time()
        if current_time - self._last_scroll_time < self._scroll_cooldown_seconds: return "break"
        delta_y = self._decode_mac_touchpad_delta(event.delta)
        if delta_y != 0:
            self._last_scroll_time = current_time
            self.set(self._current_value + (1 if delta_y > 0 else -1))
        return "break"

    def _process_scroll_wheel(self, event):
        if self._state == "disabled": return
        if getattr(event, "num", 0) == 4 or (hasattr(event, "delta") and event.delta > 0): d = 1
        elif getattr(event, "num", 0) == 5 or (hasattr(event, "delta") and event.delta < 0): d = -1
        else: return
        self.set(self._current_value + d)
class sCTkDialRange(sCTKDialBase):
    # This variant draws a plain line pointer rather than a dimple, so it
    # requires pointer_color instead of pointer_glow_color. pointer_color was
    # present in the theme file but never read by any code path until now.
    _EXTRA_THEME_KEYS = ("pointer_color",)

    """
    Ranged potentiometer module tracking discrete integer boundaries.
    Enforces absolute dead stops (does not loop at thresholds) and reports absolute integer states.
    """
    def __init__(self, master=None, from_=0, to=100, arc_angle=270, command=None, left_click_callback=None, right_click_callback=None, diameter=120, divisions=5, **kw):
        self._from = int(from_)
        self._to = int(to)
        self._arc_angle = float(arc_angle)
        super().__init__(master, divisions=divisions, diameter=diameter, **kw)
        self._command = command
        self._left_click_callback = left_click_callback if (left_click_callback and str(left_click_callback).strip()) else None
        self._right_click_callback = right_click_callback if (right_click_callback and str(right_click_callback).strip()) else None
        self._current_value = self._from
        self._custom_current_state = "normal" if self._state == "normal" else "disabled"
        self._finalize_themeable_lifecycle()

    def _get_value_fraction(self):
        r = self._to - self._from
        return (self._current_value - self._from) / r if r > 0 else 0.0

    def configure(self, *args, **kwargs):
        if args: return super().configure(*args, **kwargs)
        if "from_" in kwargs or "min_value" in kwargs: self._from = int(kwargs.pop("from_", kwargs.pop("min_value", 0)))
        if "to" in kwargs or "max_value" in kwargs: self._to = int(kwargs.pop("to", kwargs.pop("max_value", 100)))
        if "arc_angle" in kwargs: self._arc_angle = float(kwargs.pop("arc_angle"))
        if "divisions" in kwargs: self._divisions = int(kwargs.pop("divisions"))
        if "command" in kwargs: self._command = kwargs.pop("command")
        if "left_click_callback" in kwargs: self._left_click_callback = kwargs.pop("left_click_callback")
        if "right_click_callback" in kwargs: self._right_click_callback = kwargs.pop("right_click_callback")
        if "diameter" in kwargs:
            d = int(kwargs.pop("diameter"))
            kwargs["width"], kwargs["height"] = d, d
        result = super().configure(**kwargs)
        if hasattr(self, "canvas") and self.canvas.winfo_exists(): self._draw_dial_base()
        return result


    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does NOT track whichever configure() a subclass defines.
    # Without this, .config(...) skips every override in this class and lands
    # on the native widget, bypassing divisions/command/diameter handling and
    # the theme repaint entirely. Confirmed as a critical bug on
    # sCTkSegmentedButton earlier in this project's audit. Each subclass needs
    # its own line -- inheriting the alias would point at the PARENT's
    # configure(), not the subclass's.
    config = configure
    def cget(self, attribute_name: str) -> any:
        if attribute_name in ["from_", "min_value"]: return self._from
        if attribute_name in ["to", "max_value"]: return self._to
        if attribute_name == "arc_angle": return self._arc_angle
        if attribute_name == "command": return self._command
        if attribute_name == "divisions": return self._divisions
        return super().cget(attribute_name)

    def set(self, value):
        target = max(self._from, min(self._to, int(value)))
        if target != self._current_value:
            self._current_value = target
            if self.canvas.winfo_exists(): self._redraw_indicator()
            if self._command is not None and self._state == "normal": self._command(self._current_value)

    def get(self): return self._current_value
    def _on_left_click_step(self, event):
        if self._state == "disabled": return
        if self._left_click_callback is not None: self._left_click_callback()
        else: self.set(self._current_value - 1)

    def _on_right_click_step(self, event):
        if self._state == "disabled": return
        if self._right_click_callback is not None: self._right_click_callback()
        else: self.set(self._current_value + 1)

    def _on_button_press(self, event): self._last_y = event.y
    def _on_button_motion(self, event):
        if self._state == "disabled": return
        delta_y = self._last_y - event.y
        if abs(delta_y) > 2:
            self.set(self._current_value + (1 if delta_y > 0 else -1))
            self._last_y = event.y

    def _process_mac_touchpad_scroll(self, event):
        if self._state == "disabled": return "break"
        current_time = time.time()
        if current_time - self._last_scroll_time < self._scroll_cooldown_seconds: return "break"
        delta_y = self._decode_mac_touchpad_delta(event.delta)
        if delta_y != 0:
            self._last_scroll_time = current_time
            self.set(self._current_value + (1 if delta_y > 0 else -1))
        return "break"

    def _process_scroll_wheel(self, event):
        if self._state == "disabled": return
        if getattr(event, "num", 0) == 4 or (hasattr(event, "delta") and event.delta > 0): d = 1
        elif getattr(event, "num", 0) == 5 or (hasattr(event, "delta") and event.delta < 0): d = -1
        else: return
        self.set(self._current_value + d)