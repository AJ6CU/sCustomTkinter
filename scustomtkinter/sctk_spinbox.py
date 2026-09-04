#!/usr/bin/python3
"""
sCTkSpinbox

A theme-compliant, highly configurable custom spinbox wrapper component.
Operates entirely programmatically via get() and set() methods, bypassing
textvariable trace conflicts to guarantee pristine placeholder rendering.

Supports a genuine three-state model: normal / readonly / disabled, matching
real ttk.Spinbox semantics. In readonly mode, the entry can't be typed into
directly, but the increment/decrement buttons stay fully clickable -- an
earlier version collapsed anything that wasn't literally "disabled" into
"normal", silently discarding any readonly request (confirmed: two separate
mechanisms both erased it -- the state-cascade applied one value uniformly to
entry and buttons, which can't express the distinction readonly needs, and
_apply_custom_theme_colors() ran a hardcoded disabled-or-normal binary check
unconditionally after every configure() call, overwriting whatever the
cascade had done). Readonly routes through sCTkEntryPrimary's own three-state
_update_current_visual_state(), which is where the actual readonly colors and
required-key validation live -- see that widget for the full detail.
"""

import customtkinter as ctk
from .themeable_widget import ThemeableWidget, parse_list_property

from .sctk_entry_primary import sCTkEntryPrimary

class sCTkSpinbox(ctk.CTkFrame, ThemeableWidget):
    def __init__(self, master=None, from_=0.0, to=100.0, step_size=1.0, command=None,
                 state="normal", wrap=False, justify="left", show=None,
                 placeholder_text=None, exportselection=True, width=140, height=32, **kw):

        ThemeableWidget.__init__(self, kw)
        self._local_defaults = dict(self.final_kw)
        # FIX: an earlier version read "disabled_map" out of self._local_defaults
        # (== dict(self.final_kw)), but ThemeableWidget.__init__ deliberately
        # excludes "disabled_map" from final_kw -- this always evaluated to the
        # empty-dict default, meaning EVERY disabled-state color lookup below
        # silently fell back to its hardcoded literal instead of the real
        # theme. Confirmed identical bug, same fix, as sCTkSwitch and
        # sCTkTableview elsewhere in this project.
        self._custom_disabled_map = dict(self._widget_disabled_map)
        # readonly_map: mirrors sCTkEntryPrimary's own pattern -- required
        # only when readonly is actually requested, validated in
        # _apply_custom_theme_colors().
        self._custom_readonly_map = dict(self._widget_readonly_map)

        button_width = self._local_defaults.pop("button_width", 22)
        button_height = self._local_defaults.pop("button_height", None)
        button_side = self._local_defaults.pop("button_side", "right")
        orientation = self._local_defaults.pop("orientation", "vertical")
        # FIX: an earlier version only ever looked for "arrow_font_size" (a
        # bare number) here, but the real theme key is "arrow_font" -- a full
        # (family, size, weight) tuple, matching the convention used for
        # every other font in this theme file. Since "arrow_font_size" never
        # actually existed in the theme, this always silently fell back to
        # its hardcoded default (11), and the font family/weight were
        # separately hardcoded to "Arial"/"normal" a few lines down --
        # meaning the real theme's arrow_font value was never applied at
        # all. Now reads arrow_font properly, while still allowing
        # arrow_font_size to independently override just the size (e.g. via
        # configure(arrow_font_size=14)) without needing to respecify the
        # full tuple.
        arrow_font_theme = self._local_defaults.pop("arrow_font", None)
        if isinstance(arrow_font_theme, (list, tuple)) and len(arrow_font_theme) >= 2:
            default_arrow_family = str(arrow_font_theme[0])
            default_arrow_size = arrow_font_theme[1]
            default_arrow_weight = str(arrow_font_theme[2]) if len(arrow_font_theme) >= 3 else "normal"
        else:
            default_arrow_family, default_arrow_size, default_arrow_weight = "Arial", 11, "normal"
        arrow_font_size = self._local_defaults.pop("arrow_font_size", default_arrow_size)
        format_str = self._local_defaults.pop("format", None)
        values = self._local_defaults.pop("values", None)
        wrap_val = kw.pop("wrap", wrap)

        self.final_kw.pop("state", None)
        for pop_key in ["fg_color", "text_color", "entry_color", "border_color", "border_width",
                        "corner_radius", "font", "placeholder_text_color", "button_color",
                        "button_hover_color", "disabled_text_color", "disabled_entry_color",
                        "disabled_border_color", "disabled_button_color",
                        "arrow_font", "arrow_up_char", "arrow_down_char", "arrow_right_char", "arrow_left_char",
                        "button_width", "button_height", "button_side", "orientation", "format", "values", "wrap"]:
            self.final_kw.pop(pop_key, None)

        super().__init__(master, width=width, height=height, fg_color="transparent", **self.final_kw)

        self._arrow_font_family = default_arrow_family
        self._arrow_font_weight = default_arrow_weight
        self._arrow_font_size = int(arrow_font_size)
        self._from, self._to, self._step_size = float(from_), float(to), float(step_size)
        self._wrap = wrap_val if isinstance(wrap_val, bool) else (str(wrap_val).lower() in ("true", "1", "yes"))
        self._command, self._placeholder_text, self._format = command, placeholder_text, (str(format_str) if format_str else "")
        self._current_numeric_value = self._from

        self._values = self._parse_string_list(values) if values else []
        self._current_index = 0 if self._values else -1
        self._button_width, self._button_side, self._orientation = int(button_width), str(button_side).lower(), str(orientation).lower()
        # FIX: an earlier version collapsed anything that wasn't literally
        # "normal" into "disabled" -- meaning state="readonly" passed to the
        # constructor was silently treated as disabled. Now supports a
        # genuine three-state model matching ttk.Spinbox's real semantics
        # (normal/readonly/disabled); see class docstring.
        _initial_state = str(state).lower()
        self._state = _initial_state if _initial_state in ("normal", "readonly", "disabled") else "normal"
        self._button_height = int(button_height) if button_height is not None else ((height // 2) - 1 if self._orientation == "vertical" else height)

        used_buttons = 2 if self._button_side == "split" or self._orientation == "horizontal" else 1
        self.entry = sCTkEntryPrimary(self, width=width - (self._button_width * used_buttons), height=height, justify=justify, show=show, placeholder_text=self._placeholder_text, exportselection=exportselection)
        self.up_button = ctk.CTkButton(self, text="▲" if self._orientation == "vertical" else "▶", width=self._button_width, height=self._button_height, corner_radius=2, command=self._increment_callback)
        self.down_button = ctk.CTkButton(self, text="▼" if self._orientation == "vertical" else "◀", width=self._button_width, height=self._button_height, corner_radius=2, command=self._decrement_callback)

        if not self._placeholder_text or str(self._placeholder_text).strip() == "":
            self.entry.insert(0, str(self._values) if self._values else self._format_value(self._from))

        self.entry.bind("<FocusOut>", lambda e: self._validate_and_sanitize_input())
        self.entry.bind("<Return>", lambda e: self._validate_and_sanitize_input())

        self._rebuild_grid_layout()
        self._apply_custom_theme_colors()
        if self._state == "disabled": super().configure(state="disabled")
        self._finalize_themeable_lifecycle()

    def _parse_string_list(self, input_data) -> list:
        """
        Parses this widget's `values` property.

        Delegates to the library-wide parse_list_property() so `values`
        behaves identically to sCTkTableview's `columns`, sCTkSelector's
        `items` and sCTkDialSelector's `labels`. Retained as a method rather
        than replaced at each call site because set_values() and configure()
        both use it.

        FIX: this previously used shlex.split() whenever the input contained
        no comma, making SPACE a value separator here and nowhere else in the
        library -- so "Meat Loaf" was two values in a spinbox and one value in
        every other widget. Space separation is deliberately dropped rather
        than propagated; a value containing a comma should be quoted.
        """
        return parse_list_property(input_data)

    def set_values(self, list_of_strings):
        self._values = self._parse_string_list(list_of_strings)
        self._current_index = 0 if self._values else -1
        self.set(self._values if self._values else getattr(self, "_from", 0.0))

    def _rebuild_grid_layout(self):
        if not hasattr(self, "entry") or not self.entry.winfo_exists(): return
        for i in range(3): self.grid_columnconfigure(i, weight=0, minsize=0)
        for i in range(2): self.grid_rowconfigure(i, weight=0, minsize=0)
        self.entry.grid_forget(); self.up_button.grid_forget(); self.down_button.grid_forget()

        up_char = self._local_defaults.get("arrow_right_char", "▶") if self._orientation == "horizontal" else self._local_defaults.get("arrow_up_char", "▲")
        down_char = self._local_defaults.get("arrow_left_char", "◀") if self._orientation == "horizontal" else self._local_defaults.get("arrow_down_char", "▼")
        self.up_button.configure(text=up_char, font=(self._arrow_font_family, self._arrow_font_size, self._arrow_font_weight))
        self.down_button.configure(text=down_char, font=(self._arrow_font_family, self._arrow_font_size, self._arrow_font_weight))

        if self._orientation == "horizontal":
            self.grid_rowconfigure(0, weight=1); self.grid_columnconfigure(1, weight=1)
            if self._button_side == "left":
                self.down_button.grid(row=0, column=0, padx=(0, 1), sticky="nsew"); self.up_button.grid(row=0, column=1, padx=(1, 1), sticky="nsew"); self.entry.grid(row=0, column=2, padx=(1, 0), sticky="nsew")
            elif self._button_side == "split":
                self.down_button.grid(row=0, column=0, padx=(0, 2), sticky="nsew"); self.entry.grid(row=0, column=1, padx=(2, 2), sticky="nsew"); self.up_button.grid(row=0, column=2, padx=(2, 0), sticky="nsew")
            else:
                self.entry.grid(row=0, column=0, padx=(0, 1), sticky="nsew"); self.down_button.grid(row=0, column=1, padx=(1, 1), sticky="nsew"); self.up_button.grid(row=0, column=2, padx=(1, 0), sticky="nsew")
        else:
            self.grid_rowconfigure((0, 1), weight=1); self.grid_columnconfigure(0, weight=1)
            if self._button_side == "left":
                self.grid_columnconfigure(1, weight=1); self.up_button.grid(row=0, column=0, padx=(0, 1), pady=(0, 1), sticky="nsew"); self.down_button.grid(row=1, column=0, padx=(0, 1), pady=(1, 0), sticky="nsew"); self.entry.grid(row=0, column=1, rowspan=2, padx=(1, 0), sticky="nsew")
            elif self._button_side == "split":
                self.grid_columnconfigure(1, weight=1); self.down_button.grid(row=0, column=0, rowspan=2, padx=(0, 2), sticky="nsew"); self.entry.grid(row=0, column=1, rowspan=2, padx=(2, 2), sticky="nsew"); self.up_button.grid(row=0, column=2, rowspan=2, padx=(2, 0), sticky="nsew")
            else:
                self.entry.grid(row=0, column=0, rowspan=2, padx=(0, 2), sticky="nsew"); self.up_button.grid(row=0, column=1, padx=(1, 0), pady=(0, 1), sticky="nsew"); self.down_button.grid(row=1, column=1, padx=(1, 0), pady=(1, 0), sticky="nsew")
        self.update_idletasks()
    def configure(self, require_redraw=None, **kwargs):
        """Standardized configuration handler supporting Pygubu workspace properties switches."""
        if require_redraw is not None and not kwargs and isinstance(require_redraw, str):
            mapping = {
                "state": ("state", "state", "state", "normal", str(getattr(self, "_state", "normal"))),
                "from_": ("from_", "from_", "from_", "0.0", str(getattr(self, "_from", 0.0))),
                "to": ("to", "to", "to", "100.0", str(getattr(self, "_to", 100.0))),
                "step_size": ("step_size", "step_size", "step_size", "1.0", str(getattr(self, "_step_size", 1.0))),
                "button_width": ("button_width", "button_width", "button_width", "22", str(getattr(self, "_button_width", 22))),
                "button_height": ("button_height", "button_height", "button_height", "", str(getattr(self, "_button_height", ""))),
                "button_side": ("button_side", "button_side", "button_side", "right", str(getattr(self, "_button_side", "right"))),
                "orientation": ("orientation", "orientation", "orientation", "vertical", str(getattr(self, "_orientation", "vertical"))),
                "justify": ("justify", "justify", "justify", "left", str(self.entry.cget("justify"))),
                "placeholder_text": ("placeholder_text", "placeholder_text", "placeholder_text", "", str(getattr(self, "_placeholder_text", ""))),
                "format": ("format", "format", "format", "", str(getattr(self, "_format", ""))),
                "wrap": ("wrap", "wrap", "wrap", "False", str(getattr(self, "_wrap", False))),
                "values": ("values", "values", "values", "", " ".join([f'"{v}"' if ' ' in v else v for v in getattr(self, "_values", [])]))
            }
            if require_redraw in mapping: return mapping[require_redraw]
            return super().configure(require_redraw)

        if isinstance(require_redraw, dict): kwargs.update(require_redraw)
        if "wrap" in kwargs: self._wrap = kwargs.pop("wrap") if isinstance(kwargs["wrap"], bool) else (str(kwargs.pop("wrap")).lower() in ("true", "1", "yes"))
        if "values" in kwargs:
            self._values = self._parse_string_list(kwargs.pop("values"))
            self._current_index = 0 if self._values else -1
            if self._values: self.set(self._values)

        for key in ["from_", "to", "step_size"]:
            if key in kwargs: setattr(self, f"_{key}", float(kwargs.pop(key) or (0.0 if key == 'from_' else 100.0 if key == 'to' else 1.0)))

        if "command" in kwargs: self._command = kwargs.pop("command")
        if "format" in kwargs:
            self._format = str(kwargs.pop("format") or "")
            if not self._values: self.set(self._current_numeric_value)

        rebuild_grid = False
        if "button_width" in kwargs: self._button_width = int(kwargs.pop("button_width")); self.up_button.configure(width=self._button_width); self.down_button.configure(width=self._button_width); rebuild_grid = True
        if "button_height" in kwargs: self._button_height = int(kwargs.pop("button_height")); self.up_button.configure(width=self._button_width, height=self._button_height); self.down_button.configure(width=self._button_width, height=self._button_height); rebuild_grid = True
        if "button_side" in kwargs: self._button_side = str(kwargs.pop("button_side") or "right").strip().lower(); rebuild_grid = True
        if "orientation" in kwargs:
            self._orientation = str(kwargs.pop("orientation") or "vertical").strip().lower()
            if not kwargs.get("button_height") and hasattr(self, "cget"):
                self._button_height = (int(self.cget("height")) // 2) - 1 if self._orientation == "vertical" else int(self.cget("height"))
                self.up_button.configure(height=self._button_height); self.down_button.configure(height=self._button_height)
            rebuild_grid = True

        if "arrow_font_size" in kwargs: self._arrow_font_size = int(kwargs.pop("arrow_font_size")); rebuild_grid = True
        # New: allows setting the full (family, size, weight) tuple at once,
        # now that these attributes are genuinely used rather than
        # hardcoded. arrow_font_size above remains available too, for
        # changing just the size without respecifying family/weight.
        if "arrow_font" in kwargs:
            new_arrow_font = kwargs.pop("arrow_font")
            if isinstance(new_arrow_font, (list, tuple)) and len(new_arrow_font) >= 2:
                self._arrow_font_family = str(new_arrow_font[0])
                self._arrow_font_size = int(new_arrow_font[1])
                self._arrow_font_weight = str(new_arrow_font[2]) if len(new_arrow_font) >= 3 else "normal"
                rebuild_grid = True
        if "placeholder_text" in kwargs:
            self._placeholder_text = kwargs["placeholder_text"]
            if self._placeholder_text and str(self._placeholder_text).strip() != "" and hasattr(self, "entry") and self.entry.winfo_exists():
                # FIX: this compared the entry text against str(self._from) --
                # "0.0" -- but __init__ inserts self._format_value(self._from),
                # which with a format string produces something like "0.00".
                # The strings never matched, so setting placeholder_text at
                # runtime left the initial value in place and the placeholder
                # never showed. The formatted form is now compared too.
                _auto_initial = {"", "0", "0.0", str(getattr(self, "_from", 0.0))}
                try:
                    _auto_initial.add(self._format_value(self._from))
                except Exception:
                    pass
                if str(self.entry.get()).strip() in _auto_initial:
                    old = self.entry.cget("state"); self.entry.configure(state="normal"); self.entry.delete(0, "end"); self.entry.configure(state=old)

        for entry_attr in ["justify", "show", "placeholder_text", "exportselection"]:
            if entry_attr in kwargs:
                if hasattr(self, "entry") and self.entry.winfo_exists(): self.entry.configure(**{entry_attr: kwargs[entry_attr]})
                kwargs.pop(entry_attr)

        if rebuild_grid and hasattr(self, "cget") and hasattr(self, "entry"):
            self.entry.configure(width=int(self.cget("width")) - (self._button_width * (2 if self._button_side == "split" or self._orientation == "horizontal" else 1)))
            self._rebuild_grid_layout()

        if "state" in kwargs:
            self._state = str(kwargs.pop("state")).lower()
            if self._state not in ("normal", "readonly", "disabled"):
                self._state = "normal"
            # Entry gets the full three-way state -- routed through its own
            # state() so sCTkEntryPrimary's own readonly_map/disabled_map
            # color logic applies correctly. Buttons only ever get normal/
            # disabled -- "readonly" is not a real native CTkButton state,
            # and per ttk.Spinbox's own readonly semantics, the
            # increment/decrement arrows stay fully clickable in readonly
            # mode; only the entry becomes non-typable.
            if hasattr(self.entry, "winfo_exists") and self.entry.winfo_exists():
                if hasattr(self.entry, "state"):
                    self.entry.state(self._state)
                else:
                    self.entry.configure(state=self._state)
            button_state = "disabled" if self._state == "disabled" else "normal"
            for child in [self.up_button, self.down_button]:
                if hasattr(child, "winfo_exists") and child.winfo_exists(): child.configure(state=button_state)

        for pop_custom_key in ["from_", "to", "step_size", "button_width", "button_height", "button_side", "orientation", "arrow_font_size", "arrow_font", "format", "values", "wrap"]: kwargs.pop(pop_custom_key, None)
        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)

        if kwargs: super().configure(**kwargs)
        self._apply_custom_theme_colors()

    config = configure

    def cget(self, attribute_name):
        pname = str(attribute_name).lower()
        if pname == "arrow_font":
            # Special case: no single self._arrow_font attribute exists --
            # family/size/weight are tracked separately (see __init__), so
            # the generic dynamic-lookup pattern below can't be reused here.
            return (self._arrow_font_family, self._arrow_font_size, self._arrow_font_weight)
        if pname in ["state", "from_", "to", "step_size", "button_width", "button_height", "button_side", "orientation",
                     "arrow_font_size", "format", "wrap", "values"]: return getattr(self, f"_{pname}")
        return super().cget(attribute_name)

    def _format_value(self, val: float) -> str:
        fmt = self._format.strip() if hasattr(self, "_format") and self._format else ""
        if fmt:
            if "{" in fmt and "}" in fmt:
                try:
                    return fmt.format(val)
                except Exception:
                    pass
            elif ":" in fmt and not "{" in fmt:
                try:
                    return ("{" + fmt + "}").format(val)
                except Exception:
                    pass
            elif "%" in fmt:
                try:
                    return fmt % val
                except Exception:
                    pass
        dec_places = len(str(self._step_size).split('.')) if '.' in str(self._step_size) else 0
        return f"{val:.{dec_places}f}"

    def get(self) -> str:
        return str(self.entry.get()) if (hasattr(self, "entry") and self.entry.winfo_exists()) else str(
            getattr(self, "_from", "0.0"))

    def set(self, value):
        try:
            if not getattr(self, "_values", None):
                num = float(value)
                if num < self._from: num = self._from
                if num > self._to: num = self._to
                self._current_numeric_value = num
                display_text, callback_val = self._format_value(num), num
            else:
                display_text = str(value)
                if display_text in self._values: self._current_index = self._values.index(display_text)
                callback_val = display_text

            old = self.entry.cget("state");
            self.entry.configure(state="normal");
            self.entry.delete(0, "end");
            self.entry.insert(0, display_text);
            self.entry.configure(state=old)
            if self._command:
                try:
                    self._command(callback_val)
                except TypeError:
                    self._command()
        except ValueError:
            if getattr(self, "_values", None):
                display_text = str(value)
                if display_text in self._values: self._current_index = self._values.index(display_text)
                # FIX: an earlier version hardcoded state="normal" if self._state
                # == "normal" else "readonly" here -- meaning a disabled spinbox
                # would incorrectly end up "readonly" instead of staying
                # disabled. Uses the same save/restore pattern already correct
                # in the success path above, which works regardless of which
                # of the three real states (normal/readonly/disabled) was
                # actually active.
                old = self.entry.cget("state")
                self.entry.configure(state="normal")
                self.entry.delete(0, "end")
                self.entry.insert(0, display_text)
                self.entry.configure(state=old)

    def _increment_callback(self):
        if self._state == "disabled": return
        if hasattr(self, "_values") and self._values:
            i = self._current_index + 1
            if i >= len(self._values): i = 0 if self._wrap else (len(self._values) - 1)
            self._current_index = i;
            self.set(self._values[i]);
            return
        try:
            n = self._current_numeric_value + self._step_size
            if n > self._to: n = self._from if self._wrap else self._to
            self.set(n)
        except Exception:
            self.set(self._from)

    def _decrement_callback(self):
        if self._state == "disabled": return
        if hasattr(self, "_values") and self._values:
            i = self._current_index - 1
            if i < 0: i = (len(self._values) - 1) if self._wrap else 0
            self._current_index = i;
            self.set(self._values[i]);
            return
        try:
            n = self._current_numeric_value - self._step_size
            if n < self._from: n = self._to if self._wrap else self._from
            self.set(n)
        except Exception:
            self.set(self._from)

    def _validate_and_sanitize_input(self):
        if getattr(self, "_values", None):
            if self.get() in self._values: self._current_index = self._values.index(self.get())
            return
        try:
            raw = self.get().strip()
            if not raw: self.set(self._from); return
            for clean_token in [self._format, "kHz", "MHz", "dB", "%", "Hz", "{", "}", " "]:
                if clean_token: raw = raw.replace(clean_token, "")
            self.set(float(raw))
        except ValueError:
            self.set(self._current_numeric_value)

    def _set_appearance_mode(self, mode_string: str):
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._apply_custom_theme_colors()

    def state(self, mode: str = None) -> str:
        """
        Gets or sets the widget's normal/readonly/disabled visual state.

        Args:
            mode: If None, returns the current state without changing
                anything. Otherwise forwarded to configure(state=mode), which
                validates against ("normal", "readonly", "disabled") and
                cascades correctly: the entry gets the full three-way state
                (routed through its own state()), while the up/down buttons
                only ever receive "normal" or "disabled" -- "readonly" is not
                a real native CTkButton state, and per ttk.Spinbox's own
                semantics, the arrows stay clickable in readonly mode anyway.

        Returns:
            If setting: echoes back `mode` exactly as given (not re-queried
            afterward -- may not match self._state if configure() rejected
            an invalid value). If querying: the current state string.
        """
        if mode is None: return str(getattr(self, "_state", "normal")).lower()
        self.configure(state=mode)
        return mode

    def get_state(self) -> str:
        return self.state()

    def _apply_custom_theme_colors(self):
        """
        Applies colors and native state to the entry and both buttons, based
        on self._state (normal/readonly/disabled).

        The entry's own colors are handled by its own state() call, which
        triggers sCTkEntryPrimary's own three-state _update_current_visual_state()
        -- see that widget for the full readonly-color logic and its required-
        key validation. This method THEN overrides the entry's fg_color/
        border_color/text_color with Spinbox's own theme keys ("entry_color"/
        "border_color"/"text_color" from Spinbox's own theme block) for all
        three states -- a deliberate, pre-existing design choice: Spinbox
        controls its own entry's look via Spinbox-specific theme keys, not
        the entry's own defaults. entry_color, border_color, and text_color
        are required to be present in readonly_map specifically when readonly
        is the current state -- if any are missing, this raises immediately
        rather than silently falling back to normal/disabled colors, matching
        the same principle used in sCTkEntryPrimary's own readonly validation.

        Buttons only ever receive "normal" or "disabled" -- never "readonly",
        which is not a real native CTkButton state, and which ttk.Spinbox's
        own semantics require to stay clickable anyway. Button colors are
        always read from self._local_defaults (normal) unless disabled, so
        buttons look completely ordinary in readonly mode -- no readonly-
        specific button color key exists or is needed.
        """
        if not hasattr(self, "entry") or not self.entry.winfo_exists(): return
        current = self._state
        is_disabled = current == "disabled"
        is_readonly = current == "readonly"

        # FIX: an earlier version used .get(key, hardcoded_literal) throughout
        # this method for entry_color/border_color/text_color/button_color/
        # button_hover_color -- silently substituting a guessed value whenever
        # the real theme was incomplete. Matches the same hard-fail principle
        # applied to sCTkSwitch, the label family, and sCTkTableview elsewhere
        # in this project.
        for required_key in ("entry_color", "border_color", "button_color", "button_hover_color", "text_color"):
            if self._local_defaults.get(required_key) is None:
                raise KeyError(
                    f"'{self.__class__.__name__}' theme block is missing '{required_key}' "
                    f"at the top level of sCTkThemes.json."
                )
        for required_key in ("entry_color", "border_color", "text_color", "button_color"):
            if self._custom_disabled_map.get(required_key) is None:
                raise KeyError(
                    f"'{self.__class__.__name__}' theme block is missing '{required_key}' in disabled_map."
                )

        if is_disabled:
            m = self._custom_disabled_map
        elif is_readonly:
            m = self._custom_readonly_map
            for required_key in ("entry_color", "border_color", "text_color"):
                if m.get(required_key) is None:
                    raise KeyError(
                        f"'{self.__class__.__name__}' theme block is missing '{required_key}' "
                        f"in readonly_map -- required because state 'readonly' was requested."
                    )
        else:
            m = self._local_defaults

        dm = self._custom_disabled_map
        d_b_text = dm.get("text_color")

        # 🔑 NATIVE ACTION ROUTING:
        # Route the full three-way state through sCTkEntryPrimary's own
        # public state tracker, so its own readonly_map/disabled_map color
        # logic (and required-key validation for readonly) applies correctly.
        if hasattr(self.entry, "state"):
            self.entry.state(current)
        else:
            self.entry.configure(state=current)

        # Spinbox-specific color override, applied for all three states now.
        entry_override = {
            "fg_color": m.get("entry_color"),
            "border_color": m.get("border_color"),
        }
        if is_readonly:
            # text_color is only overridden for readonly -- normal/disabled
            # never included it here originally, and sCTkEntryPrimary's own
            # state() call already applies the correct text_color for those
            # two states. Readonly needs it here too since Spinbox's own
            # readonly_map is the source of truth for this override.
            entry_override["text_color"] = m.get("text_color")
        self.entry.configure(**entry_override)

        b_color = self._local_defaults.get("button_color")
        b_hover = self._local_defaults.get("button_hover_color")
        b_text = self._local_defaults.get("text_color")
        d_b_color = dm.get("button_color")

        # Buttons only ever get normal/disabled -- never readonly.
        button_state = "disabled" if is_disabled else "normal"

        for b in [self.up_button, self.down_button]:
            if hasattr(b, "winfo_exists") and b.winfo_exists():
                b.configure(
                    fg_color=d_b_color if is_disabled else b_color,
                    hover_color=d_b_color if is_disabled else b_hover,
                    text_color=d_b_text if is_disabled else b_text,
                    text_color_disabled=d_b_text,
                    state=button_state
                )