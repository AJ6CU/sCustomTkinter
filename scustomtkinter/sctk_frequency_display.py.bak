#!/usr/bin/python3
"""
sCTkFrequencyDisplay

A grouped numeric readout you can click a digit of.

WHAT IT IS FOR

A frequency, shown as x.xxx.xxx.xxx, where clicking a digit selects it and
the selection IS the tuning step: pick the hundreds digit and a dial moves
100 Hz per detent. That replaces a separate step control, and with it the
possibility of the two disagreeing about which digit is being tuned.

It also does signed offsets -- RIT, XIT, anything with a direction -- which
is why it is described as a grouped numeric readout rather than strictly a
frequency. Set `digits` and `signed` and the same drawing, selection and
theming serve both.

WHY A CANVAS, NOT A ROW OF LABELS

The first version assembled ten sCTkLabelPrimary widgets and coloured the
selected one's background. Three problems, all solved by drawing:

  * The readout JITTERED. Proportional digits are not the same width, so the
    row re-flowed as the numbers changed and the whole display shifted
    sideways while tuning. Here every digit sits at a computed position and
    nothing moves, whatever the font.

  * Ten configure() calls per update, against one redraw.

  * The selection highlight was a label background, so it could only be a
    rectangle behind the glyph. Drawn, it can be anything -- and it takes its
    colours from the theme rather than from hardcoded hex, which is what the
    label version had resorted to.

A FIXED-WIDTH FONT IS THE DEFAULT for the same reason: even with computed
positions, a proportional font makes 1 and 8 different widths, so a digit
changing shifts the ink inside its own cell.
"""
import tkinter as tk
import tkinter.font as tkfont

import customtkinter as ctk

from . import themeable_widget as _tw
from .themeable_widget import ThemeableWidget


class sCTkFrequencyDisplay(ctk.CTkFrame, ThemeableWidget):
    """A grouped numeric readout with per-digit selection."""

    # Required at the TOP LEVEL of the theme block.
    _REQUIRED_THEME_KEYS = (
        "fg_color", "font", "text_color", "delimiter_color",
        "selected_color", "selected_text_color",
    )

    # Required inside disabled_map.
    _REQUIRED_DISABLED_KEYS = ("text_color", "delimiter_color")

    # Keys this widget draws with must not reach CTkFrame, which raises on
    # anything it does not recognise.
    _NATIVE_FRAME_KWARGS = frozenset({"width", "height", "bg_color"})

    # Geometry, in UNSCALED pixels -- everything is put through
    # _apply_widget_scaling() before it reaches the canvas.
    PAD_X = 6               # left and right margin
    PAD_Y = 4               # top and bottom margin
    DIGIT_GAP = 0           # extra space between digits within a group
    HIGHLIGHT_PAD = 2       # how far the selection box extends past a digit
    HIGHLIGHT_RADIUS = 3

    # Groups of three from the right, as a frequency is read.
    GROUP = 3

    def __init__(self, master=None, digits=10, signed=False, value=0,
                 delimiter=".", font_size=34, selectable=True,
                 min_digit=1, state="normal", command=None, **kw):
        """
        Args:
            master: Parent container.
            digits: How many digit positions. Ten reaches into the GHz as
                x.xxx.xxx.xxx; four suits a signed offset.
            signed: Show a leading + or -, for an offset rather than a
                frequency.
            value: Initial value, in the units the caller uses -- Hz for a
                frequency.
            delimiter: What separates the groups. Settable at any time.
            font_size: Point size of the digits. The FAMILY comes from the
                theme and should stay fixed-width; see the module docstring.
            selectable: Whether clicking a digit selects it.
            min_digit: The smallest selectable digit, as a power of ten. The
                uBITX tunes in whole 10 Hz steps, so 1 means the units digit
                is shown but cannot be the thing you are moving.
            state: "normal" or "disabled".
            command: Called with the step in units when the selection
                changes -- 100 for the hundreds digit.
        """
        self._digit_count = int(digits)
        self._signed = bool(signed)
        self._value = int(value)
        self._delimiter = str(delimiter)
        self._font_size = int(font_size)
        self._selectable = bool(selectable)
        self._min_digit = max(0, int(min_digit))
        self._command = command

        ThemeableWidget.__init__(self, kw)

        # Colours come from the RAW registry, not final_kw: ThemeableWidget
        # strips its CUSTOM_VECTOR_KEYS out of final_kw, and reading them back
        # from there finds nothing. See sCTkDial.md, "Reading theme colours".
        raw_block = _tw.GLOBAL_THEME_REGISTRY.get(self.__class__.__name__) or {}
        raw_colors = {k: v for k, v in raw_block.items()
                      if not isinstance(v, dict)}
        self._local_defaults = ThemeableWidget._convert_lists_to_tuples(raw_colors)
        self._local_defaults.update(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)
        self._validate_theme_keys()

        native_kwargs = {k: v for k, v in self.final_kw.items()
                         if k in self._NATIVE_FRAME_KWARGS}
        super().__init__(master, fg_color="transparent", border_width=0,
                         **native_kwargs)

        self._state = "normal" if str(state).lower() == "normal" else "disabled"

        # The selected digit, as a power of ten. Starts at the smallest
        # selectable one, which is the least surprising default: a dial that
        # arrives set to megahertz is a trap.
        self._selected = self._min_digit

        # canvas, NOT _canvas: CTkFrame keeps its own background canvas in
        # _canvas, and assigning that name replaces the frame's reference to
        # it. The dials and S-meters use the bare name for the same reason.
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Configure>", lambda e: self._draw_display())

        self._resize_to_fit()
        self._finalize_themeable_lifecycle()

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def _validate_theme_keys(self):
        """
        Hard-fails at construction on an incomplete theme block, naming the
        missing key and where it belongs. The library-wide pattern: a missing
        key is an error, never a silently substituted colour.
        """
        name = self.__class__.__name__
        for key in self._REQUIRED_THEME_KEYS:
            if self._local_defaults.get(key) is None:
                raise KeyError(
                    f"'{name}' theme block is missing '{key}' at the top level "
                    f"of sCTkThemes.json.")
        for key in self._REQUIRED_DISABLED_KEYS:
            if self._custom_disabled_map.get(key) is None:
                raise KeyError(
                    f"'{name}' theme block is missing '{key}' in disabled_map.")

    def _sx(self, value):
        """Scales a dimension for drawing."""
        return self._apply_widget_scaling(value)

    def _scaled_font(self):
        """
        The theme font at the configured size, scaled.

        A canvas text item takes a plain tuple, which CustomTkinter's font
        scaling never sees -- so without this the digits would stay put while
        everything around them grew.

        The FAMILY comes from the theme and the SIZE from this widget: one is
        a house style, the other is how big this particular readout should be.
        """
        family, _, weight = self._font_parts()
        # THE WHOLE TUPLE, not the size.
        #
        # _apply_font_scaling takes a font and returns it with its size
        # scaled; handed a bare integer it raises:
        #
        #     ValueError: Can not scale font '38' of type <class 'int'>
        #
        # Which is easy to write and easy to miss, because a widget that
        # wraps the call in try/except just silently stops scaling.
        try:
            return self._apply_font_scaling((family, self._font_size, weight))
        except Exception:
            return (family, self._font_size, weight)

    #
    # Tk guarantees exactly three family names on every platform -- Courier,
    # Helvetica and Times -- and maps each to something local. Everything
    # else is a gamble: Menlo is macOS only, Consolas is Windows only,
    # DejaVu Sans Mono is usually Linux. A theme naming one of those looks
    # right wherever it was written and silently falls back to a
    # PROPORTIONAL default everywhere else, which is precisely the jitter
    # this widget exists to avoid.
    #
    # So the theme may name whatever it likes, and this list is tried in turn
    # when that family is not installed.
    _FIXED_WIDTH_FALLBACKS = ("Menlo", "Consolas", "DejaVu Sans Mono",
                              "Liberation Mono", "Courier New", "Courier")

    def _font_parts(self):
        """
        Family, size and weight, with the family checked for existence.

        Tk does not report a missing family -- it quietly substitutes its
        default, which is proportional. Checking means a theme can name a
        good local font without breaking the widget somewhere else.
        """
        font = self._local_defaults.get("font")
        family, size, weight = "Courier", 34, "bold"
        if isinstance(font, (list, tuple)):
            if len(font) >= 1:
                family = font[0]
            if len(font) >= 2:
                size = font[1]
            if len(font) >= 3:
                weight = font[2]
        return self._available_family(family), size, weight

    def _available_family(self, preferred):
        """
        The first installed family: the theme's, then the fallbacks.

        Cached, because tkfont.families() is not cheap and the answer cannot
        change while the application runs.
        """
        cached = getattr(self.__class__, "_resolved_family", None)
        if cached is not None and cached[0] == preferred:
            return cached[1]

        chosen = preferred
        try:
            installed = {f.lower() for f in tkfont.families()}
            if preferred.lower() not in installed:
                for candidate in self._FIXED_WIDTH_FALLBACKS:
                    if candidate.lower() in installed:
                        chosen = candidate
                        break
                else:
                    # Tk guarantees this one maps to something monospace on
                    # every platform, even when the enumeration comes back
                    # unhelpful.
                    chosen = "Courier"
        except Exception:
            chosen = "Courier"

        self.__class__._resolved_family = (preferred, chosen)
        return chosen

    # ------------------------------------------------------------------
    # Colour
    # ------------------------------------------------------------------
    def _colour(self, key):
        """The current value for a key, honouring the disabled state."""
        if self._state == "disabled":
            val = self._custom_disabled_map.get(key)
            if val is not None:
                return self._resolve_color(val)
        return self._resolve_color(self._local_defaults.get(key))

    def _canvas_background(self):
        """
        A colour the canvas can actually be set to.

        "transparent" means "take the parent's", which a raw canvas cannot
        render -- so it has to be turned into whatever is really behind the
        widget. The same accommodation sCTkNotebook and sCTkDial make.
        """
        colour = self._resolve_color(self._local_defaults.get("fg_color"))
        if colour != "transparent":
            return colour

        parent = getattr(self, "master", None)
        for _ in range(6):
            if parent is None:
                break
            try:
                candidate = self._resolve_color(parent.cget("fg_color"))
                if candidate and candidate != "transparent":
                    return candidate
            except Exception:
                pass
            parent = getattr(parent, "master", None)
        return ("#1C1C1C" if str(ctk.get_appearance_mode()).lower() == "dark"
                else "#F1F5F9")

    # ------------------------------------------------------------------
    # Layout: where each character sits
    # ------------------------------------------------------------------
    def _cells(self):
        """
        Every character to draw, left to right, as (kind, text, power).

        kind is "sign", "digit" or "delimiter". power is the digit's place
        value as a power of ten, or None -- that is what makes a click
        translate into a step without counting positions.

        LEADING GROUPS ARE SUPPRESSED until they hold something, so an HF
        frequency does not sit behind two empty groups on a ten-digit
        display. The positions do not move when a group appears: the layout
        is computed for the full width and the leading cells are simply not
        drawn.
        """
        text = f"{abs(self._value):0{self._digit_count}d}"[-self._digit_count:]
        cells = []

        if self._signed:
            cells.append(("sign", "-" if self._value < 0 else "+", None))

        for index, char in enumerate(text):
            power = self._digit_count - 1 - index
            cells.append(("digit", char, power))
            # A delimiter after every third digit from the right, except at
            # the very end.
            if power % self.GROUP == 0 and power != 0:
                cells.append(("delimiter", self._delimiter, None))
        return cells

    def _first_significant(self):
        """
        The index of the first cell worth drawing.

        Anything before the first non-zero digit is a leading zero, and a
        frequency does not show them. The last GROUP digits always draw, so a
        value of zero reads as 0.000 rather than as nothing.
        """
        cells = self._cells()
        for index, (kind, char, power) in enumerate(cells):
            if kind == "digit" and char != "0":
                return index
            if kind == "digit" and power is not None and power < self.GROUP:
                return index
        return 0

    def _metrics(self):
        """Digit width, delimiter width and line height, measured once."""
        try:
            probe = tkfont.Font(font=self._scaled_font())
            return (probe.measure("0"), probe.measure(self._delimiter),
                    probe.metrics("linespace"))
        except Exception:
            size = self._sx(self._font_size)
            return int(size * 0.6), int(size * 0.3), int(size * 1.3)

    def _positions(self):
        """
        (x, kind, text, power) for every cell, and the total width.

        Computed from the metrics rather than from where the previous glyph
        happened to end, so a digit changing cannot move its neighbours. This
        is the whole reason the widget draws instead of packing labels.
        """
        digit_w, delim_w, _ = self._metrics()
        gap = self._sx(self.DIGIT_GAP)
        x = self._sx(self.PAD_X)
        placed = []
        for kind, char, power in self._cells():
            width = delim_w if kind == "delimiter" else digit_w
            placed.append((x, kind, char, power, width))
            x += width + (gap if kind == "digit" else 0)
        return placed, x + self._sx(self.PAD_X)

    def _resize_to_fit(self):
        """
        Asks for exactly the room the readout needs.

        Requested rather than imposed: a caller that wants a different size
        can still say so, and the geometry manager decides. But the default
        should fit, because a frequency clipped at the left edge is worse
        than one that is too small.
        """
        _, width = self._positions()
        _, _, line = self._metrics()
        height = line + (2 * self._sx(self.PAD_Y))
        try:
            self.canvas.configure(width=int(width), height=int(height))
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def _draw_display(self):
        """
        Repaints the whole readout.

        NOT named _draw(): CTkFrame has its own _draw(no_color_updates=...)
        and calls it from its constructor, so a method of that name here
        overrides it and the widget cannot be built.
        """
        if not hasattr(self, "canvas"):
            return
        try:
            if not self.canvas.winfo_exists():
                return
        except Exception:
            return

        self.canvas.delete("all")
        self.canvas.configure(bg=self._canvas_background())

        font = self._scaled_font()
        placed, _ = self._positions()
        _, _, line = self._metrics()
        y = self._sx(self.PAD_Y)
        first = self._first_significant()

        text_colour = self._colour("text_color")
        delim_colour = self._colour("delimiter_color")

        for index, (x, kind, char, power, width) in enumerate(placed):
            # The SIGN always draws. It sits before the first significant
            # digit, so the leading-zero rule would suppress it -- and an
            # offset shown without its direction is worse than useless.
            if index < first and kind != "sign":
                continue        # a leading zero, or the delimiter before one

            if (kind == "digit" and power == self._selected
                    and self._selectable and self._state != "disabled"):
                pad = self._sx(self.HIGHLIGHT_PAD)
                self._rounded_box(x - pad, y - pad, x + width + pad,
                                  y + line + pad,
                                  self._colour("selected_color"))
                colour = self._colour("selected_text_color")
            elif kind == "delimiter":
                colour = delim_colour
            else:
                colour = text_colour

            self.canvas.create_text(x, y, text=char, anchor="nw",
                                    fill=colour, font=font)

    def _rounded_box(self, x0, y0, x1, y1, fill):
        """The selection highlight, with its corners taken off."""
        r = self._sx(self.HIGHLIGHT_RADIUS)
        points = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r,
                  x1, y1 - r, x1, y1, x1 - r, y1, x0 + r, y1,
                  x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
        self.canvas.create_polygon(points, fill=fill, outline=fill,
                                   smooth=True)

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------
    def _on_click(self, event):
        """Selects the digit under the pointer, if it is selectable."""
        if not self._selectable or self._state == "disabled":
            return "break"

        placed, _ = self._positions()
        for x, kind, char, power, width in placed:
            if kind != "digit" or power is None:
                continue
            if power < self._min_digit:
                continue
            if x <= event.x <= x + width:
                self.select_digit(power)
                break
        return "break"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set(self, value):
        """Sets the value. Does NOT fire the command -- see select_digit."""
        self._value = int(value)
        self._draw_display()

    def get(self):
        """The current value, as an integer."""
        return self._value

    def select_digit(self, power):
        """
        Selects a digit by its place value, and reports the new step.

        Fires `command` because this is a USER action -- the whole point of
        the widget is that choosing a digit chooses the step. set() stays
        quiet, matching CustomTkinter and everything else here.
        """
        power = max(self._min_digit, min(self._digit_count - 1, int(power)))
        if power == self._selected:
            return
        self._selected = power
        self._draw_display()
        if callable(self._command):
            try:
                self._command(self.step())
            except TypeError:
                self._command()

    def step(self):
        """The selected digit's place value, in units. 100 means 100 Hz."""
        return 10 ** self._selected

    def selected_digit(self):
        """The selected digit as a power of ten."""
        return self._selected

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------
    def get_state(self):
        """Equivalent to state() with no argument."""
        return self.state()

    def state(self, mode=None):
        """
        Gets or sets "normal"/"disabled".

        Disabling dims the digits and stops selection. The value keeps
        updating: this is a readout as well as a control, and a display that
        froze while greyed would be indistinguishable from one showing a
        current value -- which on a radio panel is actively misleading. Same
        reasoning as the S-meters.
        """
        if mode is None:
            return self._state
        mode = str(mode).lower()
        self._state = "disabled" if mode == "disabled" else "normal"
        self._draw_display()
        return self._state

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    def configure(self, *args, **kwargs):
        """Standard configuration, plus Pygubu's single-argument query form."""
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                simple = {
                    "state": ("normal", self._state),
                    "digits": (10, self._digit_count),
                    "signed": ("False", str(self._signed)),
                    "delimiter": (".", self._delimiter),
                    "font_size": (34, self._font_size),
                    "selectable": ("True", str(self._selectable)),
                    "min_digit": (1, self._min_digit),
                    "value": (0, self._value),
                }
                if pname in simple:
                    default, current = simple[pname]
                    return (pname, pname, pname, default, current)
                return self._configure_query(pname)

        self._record_theme_overrides(kwargs)

        resize = False
        if "state" in kwargs:
            self.state(kwargs.pop("state"))
        if "value" in kwargs:
            self._value = int(kwargs.pop("value"))
        if "digits" in kwargs:
            self._digit_count = int(kwargs.pop("digits"))
            resize = True
        if "signed" in kwargs:
            self._signed = self._as_bool(kwargs.pop("signed"))
            resize = True
        if "delimiter" in kwargs:
            # Settable mid-stream: it is a display preference several windows
            # share, and a readout that kept the delimiter it was born with
            # would disagree with the rest of the interface the moment the
            # setting changed.
            self._delimiter = str(kwargs.pop("delimiter"))
            resize = True
        if "font_size" in kwargs:
            self._font_size = int(kwargs.pop("font_size"))
            resize = True
        if "selectable" in kwargs:
            self._selectable = self._as_bool(kwargs.pop("selectable"))
        if "min_digit" in kwargs:
            self._min_digit = max(0, int(kwargs.pop("min_digit")))
            if self._selected < self._min_digit:
                self._selected = self._min_digit
        if "command" in kwargs:
            self._command = kwargs.pop("command")

        # Keys this widget draws with are consumed here: they are not native
        # CTkFrame options, and forwarding one raises.
        for key in list(kwargs):
            if key in self._local_defaults and key not in self._NATIVE_FRAME_KWARGS:
                kwargs.pop(key)

        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        result = super().configure(**kwargs) if kwargs else None
        if resize:
            self._resize_to_fit()
        self._draw_display()
        return result

    config = configure

    @staticmethod
    def _as_bool(value):
        """bool("False") is True, and the Designer sends strings."""
        if isinstance(value, str):
            return value.strip().lower() in ("true", "1", "yes", "on")
        return bool(value)

    def cget(self, attribute_name):
        simple = {
            "state": self._state, "digits": self._digit_count,
            "signed": self._signed, "delimiter": self._delimiter,
            "font_size": self._font_size, "selectable": self._selectable,
            "min_digit": self._min_digit, "value": self._value,
        }
        if attribute_name in simple:
            return simple[attribute_name]
        if attribute_name in self._local_defaults and \
                attribute_name not in self._NATIVE_FRAME_KWARGS:
            return self._local_defaults.get(attribute_name)
        return super().cget(attribute_name)

    def _set_appearance_mode(self, mode_string):
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._draw_display()

    def _update_current_visual_state(self):
        """Repaint hook, found by ThemeableWidget._repaint_after_override()."""
        self._draw_display()