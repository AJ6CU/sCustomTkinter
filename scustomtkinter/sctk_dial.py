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
from .themeable_widget import ThemeableWidget
class sCTKDialBase(ctk.CTkFrame, ThemeableWidget):
    """Abstract Base Class for theme-adaptive mechanical rotary encoder widgets."""

    def __init__(self, master=None, divisions=24, state="normal", width=120, height=120, **kw):
        ThemeableWidget.__init__(self, kw)
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

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

        if args and isinstance(args, dict):
            kwargs = args | kwargs

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

    def _draw_dial_base(self):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists(): return
        self.canvas.delete("all")
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width < 10 or height < 10: width = height = int(self.cget("width") if hasattr(self, "cget") else 120)

        child_classname = self.__class__.__name__
        bg_color = self._resolve_color(self._local_defaults.get("fg_color") or ("#F1F5F9", "#0A0A0A"))
        shadow_paint = self._resolve_color(self._local_defaults.get("shadow_color") or ("#CBD5E1", "#02040A"))
        text_color = self._resolve_color(self._local_defaults.get("text_color") or ("#3B8ED0", "#FF9100"))
        dial_color = self._resolve_color(self._local_defaults.get("dial_color") or ("#1E293B", "#181E2B"))
        is_dark_mode = (ctk.get_appearance_mode() == "Dark")

        if self._state == "disabled":
            text_color = self._resolve_color(self._custom_disabled_map.get("text_color") or ("#94A3B8", "#4B5563"))
            dial_color = self._resolve_color(self._custom_disabled_map.get("fg_color") or ("#E2E8F0", "#1A1D24"))
            bg_color = self._resolve_color(self._custom_disabled_map.get("fg_color") or ("#F1F5F9", "#0A0D14"))
            pointer_glow = self._resolve_color(self._custom_disabled_map.get("disabled_dimple_glow") or ("#CBD5E1", "#334155"))
        else:
            pointer_glow = self._resolve_color(self._local_defaults.get("pointer_glow_color") or ("#CBD5E1", "#3A455C"))

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

        self.canvas.create_oval(center_x - knob_radius + 2, center_y - knob_radius + 2, center_x + knob_radius - 2, center_y + knob_radius - 2, fill=dial_color, outline="#111625" if is_dark_mode else "#475569", width=1)
        self.canvas.create_oval(center_x - knob_radius + 3, center_y - knob_radius + 3, center_x + knob_radius - 3, center_y + knob_radius - 3, fill="", outline="#4A5568" if is_dark_mode else "#E2E8F0", width=1)

        val_pct = self._get_value_fraction() if hasattr(self, "_get_value_fraction") else 0.0
        pointer_rad = math.radians(-(start_deg + (val_pct * arc_sweep)))

        if child_classname in ["sCTkDialSelector", "sCTkDialRange"]:
            px, py = center_x + (knob_radius - 2) * math.cos(pointer_rad), center_y - (knob_radius - 2) * math.sin(pointer_rad)
            raw_pointer_theme = self._custom_disabled_map.get("text_color") if self._state == "disabled" else self._local_defaults.get("text_color") or ("#3B8ED0", "#FF9100")
            self.canvas.create_line(center_x, center_y, px, py, fill=self._resolve_color(raw_pointer_theme), width=3.0, arrow="last", arrowshape=(8, 10, 3))
            self.canvas.create_oval(center_x - 6, center_y - 6, center_x + 6, center_y + 6, fill=dial_color, outline="#4A5568" if is_dark_mode else "#E2E8F0", width=1)
        else:
            dimple_center_radius = knob_radius - 14
            dx, dy = center_x + dimple_center_radius * math.cos(pointer_rad), center_y - dimple_center_radius * math.sin(pointer_rad)
            ind_radius = 14.5
            self.canvas.create_oval(dx - ind_radius, dy - ind_radius, dx + ind_radius, dy + ind_radius, fill="#181E2B" if is_dark_mode else "#475569", outline="")
            self.canvas.create_oval(dx - ind_radius - 1.5, dy - ind_radius - 1.5, dx + ind_radius - 1, dy + ind_radius - 1, fill="#0A0F1D" if is_dark_mode else "#334155", outline="")
            self.canvas.create_oval(dx - ind_radius - 2.5, dy - ind_radius - 2.5, dx + ind_radius - 2, dy + ind_radius - 2, fill="#010205" if is_dark_mode else "#0F172A", outline="")
            self.canvas.create_oval(dx - ind_radius + 1.5, dy - ind_radius + 1.5, dx + ind_radius + 1.5, dy + ind_radius + 1.5, fill="", outline=pointer_glow, width=1.5)
class sCTkDialContinuous(sCTKDialBase):
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

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "command": return self._command
        if attribute_name == "left_click_callback": return self._left_click_callback
        if attribute_name == "right_click_callback": return self._right_click_callback
        return super().cget(attribute_name)

    def set_position_index(self, step_delta):
        self._current_value = (self._current_value + int(step_delta)) % self._divisions
        if self.canvas.winfo_exists(): self._draw_dial_base()
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
        if self.canvas.winfo_exists(): self._draw_dial_base()
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
            if self.canvas.winfo_exists(): self._draw_dial_base()
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
