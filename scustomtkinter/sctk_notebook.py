#!/usr/bin/python3
"""
sCTkNotebook

A multi-page container with its tabs down the left or right edge, rather than
across the top. The same idea as sCTkTabview, turned ninety degrees.

WHY THIS IS NOT A SUBCLASS OF sCTkTabview. Native CTkTabview builds its tab
strip from a CTkSegmentedButton, which lays its buttons out in a single grid
ROW and offers no vertical mode. Everything about the strip -- its geometry,
its selection handling, its colours -- comes from that widget. Reusing it
would mean overriding nearly all of it, so this class owns its strip outright.

WHY EVERYTHING IS ON ONE CANVAS. Tab labels run along the strip rather than
across it, so the text is rotated ninety degrees, and a Tk button cannot
rotate its text. That alone would only need a canvas for the strip -- but the
page outline has to break where the selected tab meets it, the way a real
notebook divider does, and a border drawn by a frame cannot have a gap cut in
it. Outline and tabs are therefore drawn together, on a single canvas
spanning the whole widget, and the content pages are placed on top of it.

Selection, hover and hit-testing are consequently this class's own code
rather than a button's.
"""
import sys
import tkinter as tk
import tkinter.font as tkfont
import math
import customtkinter as ctk

from . import themeable_widget as _tw
from .themeable_widget import ThemeableWidget
from .sctk_frame import sCTkFrame


class sCTkNotebook(ctk.CTkFrame, ThemeableWidget):
    """A tabbed container with a vertical tab strip."""

    # Required at the TOP LEVEL of the theme block.
    _REQUIRED_THEME_KEYS = (
        "fg_color", "font", "text_color", "selected_text_color",
        "tab_fg_color", "tab_selected_color", "tab_hover_color",
        "border_color",
    )

    # Required inside disabled_map. The strip and the outline dim; the page
    # area does not, matching the dials and sCTkScrollableFrame -- the content
    # carries its own state, and a greyed page would hide it.
    _REQUIRED_DISABLED_KEYS = (
        "text_color", "tab_fg_color", "tab_selected_color", "border_color",
    )

    # Keys this widget reads itself must not reach CTkFrame, which raises on
    # anything it does not recognise.
    _NATIVE_FRAME_KWARGS = frozenset({
        "width", "height", "bg_color",
    })

    # Geometry, in UNSCALED pixels. Every one of these goes through
    # _apply_widget_scaling() before it reaches the canvas, so the strip grows
    # with the rest of the interface on a scaled display. Drawing raw pixels
    # on a CTkCanvas is the easy mistake here: the canvas widget scales, the
    # coordinates inside it do not.
    TAB_GAP = 2             # space between adjacent tabs
    TAB_PAD = 18            # space either end of a label, along the tab
    TAB_CORNER = 6          # corner rounding on the outer edge of a tab
    # An angled tab's corners are CHAMFERED -- a straight cut between a point
    # measured in from the corner along each edge. Independent, because the
    # two edges are not equivalent: x runs across the strip, whose width is
    # fixed, while y runs along the tab, whose length depends on the label
    # and on whether the text is rotated.
    TAB_CHAMFER_X = 6       # in from the outer corner, across the strip
    TAB_CHAMFER_Y = 6       # in from the outer corner, along the tab
    TAB_CHAMFER_MAX_FRACTION = 0.25   # ceiling on the Y cut, per end, as a
                                      # fraction of the tab's length
    PAGE_CORNER = 8         # corner rounding on the page outline
    PAGE_INSET = 8          # gap between the outline and a page's contents
    BORDER_WIDTH = 2        # page outline thickness
    STRIP_MARGIN = 6        # space above the first tab
    SEPARATOR_INSET = 5     # how far a separator stops short of each edge

    def __init__(self, master=None, side="left", tab_width=34,
                 tab_style="rounded", text_orientation="auto",
                 show_page_border=True, show_tab_separators=False,
                 state="normal", **kw):
        """
        Args:
            master: Parent container.
            side: Which edge the strip sits on, "left" or "right".
            tab_width: Width of the strip in pixels. Explicit rather than
                measured, because the strip takes space from the pages and a
                layout that shifts when a tab is renamed is worse than one the
                caller sets.
            tab_style: "rounded" or "angled". Rounded matches the rest of the
                library; angled is the shape of a real notebook divider.
            text_orientation: How the labels sit on the tabs.
                "auto" reads outside-in -- up a left strip, down a right one,
                the way a book's spine is set. "up" and "down" force one
                direction whichever side the strip is on. "horizontal" lays
                the text flat, which needs a tab_width wide enough to hold
                the longest label.
            show_page_border: Whether to draw the outline around the page,
                broken where the selected tab meets it.
            show_tab_separators: Draws a line across the strip between
                adjacent tabs. Useful with horizontal text, where stacked
                labels can otherwise run together; less so with rotated text,
                where the gap alone reads clearly. Off by default.
            state: "normal" or "disabled".
            **kw: Native CTkFrame arguments, or theme-key overrides.
        """
        self._side = self._check_side(side)
        self._tab_width = int(tab_width)
        self._tab_style = self._check_style(tab_style)
        self._text_orientation = self._check_orientation(text_orientation)
        self._show_page_border = bool(show_page_border)
        self._show_tab_separators = bool(show_tab_separators)

        ThemeableWidget.__init__(self, kw)

        # Colours come from the RAW registry, not final_kw.
        #
        # ThemeableWidget strips its CUSTOM_VECTOR_KEYS -- text_color among
        # them -- out of final_kw so they cannot reach a native constructor.
        # Reading them back from final_kw finds nothing, which is the trap
        # that left the whole dial family rendering in hardcoded fallbacks.
        # See sCTkDial.md, "Reading theme colours".
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

        # name -> sCTkFrame, in insertion order. Ordinary dicts preserve it,
        # and tab order is insertion order.
        self._pages = {}
        self._current = None
        self._hover = None          # name under the pointer, or None
        self._tab_bounds = {}       # name -> (y_top, y_bottom), for hit-testing
        self._scroll = 0            # strip scroll offset, in pixels

        # NAMED self.canvas, NOT self._canvas.
        #
        # CTkFrame keeps its own background canvas in self._canvas, so
        # assigning that name here replaces the frame's reference to it and
        # its _draw() would then paint on this widget's canvas instead. The
        # dials and the S-meters use the bare name for exactly this reason.
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0, bd=0)
        # GRIDDED, not placed, and lowered behind the pages.
        #
        # place() takes a widget out of the geometry negotiation entirely: a
        # placed page contributes nothing to what its parent requests, so the
        # notebook asked for nothing and every size had to be set by hand.
        # Grid keeps the propagation -- the cell takes the pages' requested
        # size, the notebook takes the cell's -- while lower() keeps the
        # canvas behind them.
        self.canvas.grid(row=0, column=0, columnspan=2, sticky="nsew")
# NOT lowered.
        #
        # Lowering this canvas put it beneath CTkFrame's OWN background
        # canvas, and "transparent" in CustomTkinter does not mean "do not
        # paint" -- it means "paint the parent's colour". So the frame's
        # background covered the tab strip completely and the widget rendered
        # as an empty rectangle, while every print said the tabs were there.
        #
        # Nothing needs lowering anyway: this canvas is created before the
        # page host, so it is already below it in the stacking order, which is
        # the only relationship that matters.

        # Pages sit ON TOP of the canvas, inside the outline.
        # Created AFTER the canvas, so it stacks above it -- see the note
        # there. lift() states it rather than relying on creation order.
        self._page_host = ctk.CTkFrame(self, fg_color="transparent",
                                       border_width=0)
        self._page_host.lift()
        self._page_host.grid_rowconfigure(0, weight=1)
        self._page_host.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", self._on_leave)
        self.canvas.bind("<Configure>", lambda e: self._relayout())
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.bind(seq, self._on_wheel)
        # macOS trackpads deliver <TouchpadScroll>, a separate event from
        # <MouseWheel>, with far more of them and far finer values. Binding
        # only the wheel means a real mouse scrolls the strip and a trackpad
        # does nothing at all. Same split ScrollBindingMixin handles for the
        # scrolling containers.
        if sys.platform == "darwin":
            self.canvas.bind("<TouchpadScroll>", self._on_touchpad)

        # Laid out ONCE at construction, not only when a tab is added.
        #
        # _relayout() is what configures the grid columns -- the strip's
        # minsize and the page column's weight. Without this call an empty
        # notebook had neither, so both columns collapsed and the canvas,
        # gridded across them, had no width to draw in. The widget rendered
        # as nothing at all until the first tab arrived.
        self._relayout()

        self._finalize_themeable_lifecycle()

    # ------------------------------------------------------------------
    # Argument checking
    # ------------------------------------------------------------------
    @staticmethod
    def _check_side(value):
        side = str(value).lower()
        if side not in ("left", "right"):
            raise ValueError(f'side must be "left" or "right", not "{value}"')
        return side

    @staticmethod
    def _check_style(value):
        style = str(value).lower()
        if style not in ("rounded", "angled"):
            raise ValueError(
                f'tab_style must be "rounded" or "angled", not "{value}"')
        return style

    @staticmethod
    def _check_orientation(value):
        orientation = str(value).lower()
        if orientation not in ("auto", "up", "down", "horizontal"):
            raise ValueError(
                'text_orientation must be "auto", "up", "down" or '
                f'"horizontal", not "{value}"')
        return orientation

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

    # ------------------------------------------------------------------
    # Scaling helpers
    # ------------------------------------------------------------------
    # Geometry keys the theme may override. Absent from a block, the class
    # attribute of the same name in upper case applies -- so a theme need
    # only mention the ones it wants to change, and none of them are
    # required.
    _THEMEABLE_GEOMETRY = {
        "tab_corner": "TAB_CORNER",
        "tab_chamfer_x": "TAB_CHAMFER_X",
        "tab_chamfer_y": "TAB_CHAMFER_Y",
        "tab_gap": "TAB_GAP",
        "tab_pad": "TAB_PAD",
        "page_corner": "PAGE_CORNER",
        "page_inset": "PAGE_INSET",
        "border_width": "BORDER_WIDTH",
        "separator_inset": "SEPARATOR_INSET",
        "strip_margin": "STRIP_MARGIN",
    }

    def _geom(self, key):
        """
        A geometry value, scaled, from the theme or the class attribute.

        Theme first so a palette can carry its own proportions -- a squarer
        theme wants a smaller tab_corner -- while the class attributes stay
        the defaults and remain settable per instance for one-off tuning.
        """
        value = self._local_defaults.get(key)
        if value is None:
            value = getattr(self, self._THEMEABLE_GEOMETRY[key])
        return self._apply_widget_scaling(float(value))

    def _sx(self, value):
        """Scales a dimension for drawing. Used on every geometry constant."""
        return self._apply_widget_scaling(value)

    def _scaled_font(self):
        """
        The theme font with its size scaled.

        A canvas text item takes a plain font tuple, which CustomTkinter's own
        font scaling never sees -- so without this the labels would stay the
        same size while everything around them grew.
        """
        font = self._local_defaults.get("font")
        try:
            if isinstance(font, (list, tuple)) and len(font) >= 2:
                scaled = list(font)
                scaled[1] = int(self._apply_font_scaling(font[1]))
                return tuple(scaled)
        except Exception:
            pass
        return font

    # ------------------------------------------------------------------
    # Colour resolution
    # ------------------------------------------------------------------
    def _colour(self, key):
        """The current value for a key, honouring the disabled state."""
        if self._state == "disabled":
            val = self._custom_disabled_map.get(key)
            if val is not None:
                return self._resolve_color(val)
        return self._resolve_color(self._local_defaults.get(key))

    def _page_background(self):
        """
        The colour behind the pages, resolved to something drawable.

        A raw canvas cannot render CustomTkinter's "transparent" pseudo-value,
        so a transparent theme falls back to whatever is actually behind the
        widget -- the same accommodation sCTkFileExplorer's canvas makes.
        """
        bg = self._resolve_color(self._local_defaults.get("fg_color"))
        if bg == "transparent":
            detected = self._detect_color_of_master()
            if detected in (None, "transparent"):
                return self._resolve_color(
                    ctk.ThemeManager.theme["CTk"]["fg_color"])
            return self._resolve_color(detected)
        return bg

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _content_rect(self):
        """
        (x0, y0, x1, y1) of the page area, in canvas coordinates.

        The strip occupies tab_width on the chosen side; the page area is
        everything else.
        """
        w = max(self.canvas.winfo_width(), 1)
        h = max(self.canvas.winfo_height(), 1)
        strip = self._sx(self._tab_width)
        if self._side == "left":
            return strip, 0, w, h
        return 0, 0, w - strip, h

    def _relayout(self):
        """
        Reserves the strip's column, insets the page host, then redraws.

        The strip is a grid column with a minimum size rather than a placed
        rectangle, so the pages keep contributing their requested size to the
        notebook's own -- see the note where the canvas is gridded.
        """
        strip = int(self._sx(self._tab_width))
        pad = int(self._geom("page_inset") + self._geom("border_width")) \
            if self._show_page_border else 0

        strip_col, page_col = (0, 1) if self._side == "left" else (1, 0)
        self.grid_columnconfigure(strip_col, minsize=strip, weight=0)
        self.grid_columnconfigure(page_col, weight=1)

        self._page_host.grid(row=0, column=page_col, sticky="nsew",
                             padx=pad, pady=pad)
        self._draw_notebook()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def _text_angle(self):
        """
        The canvas rotation for a label, in degrees.

        "auto" reads outside-in: up a left-hand strip, down a right-hand one,
        which is how a book's spine is set and stays readable whichever side
        the strip moves to. The other three override that -- "up" and "down"
        pin the direction regardless of side, which matters if a panel has
        notebooks on both edges and you want their labels to match.
        """
        if self._text_orientation == "horizontal":
            return 0
        if self._text_orientation == "up":
            return 90
        if self._text_orientation == "down":
            return 270
        return 90 if self._side == "left" else 270

    def _measure(self, text):
        """
        Length a label needs ALONG the strip, in pixels.

        Measured rather than estimated from character count: a proportional
        font makes "IIII" and "WWWW" differ by more than a factor of two, and
        tabs sized by character count would collide or leave gaps.
        """
        try:
            probe = tkfont.Font(font=self._scaled_font())
            if self._text_orientation == "horizontal":
                # Flat text runs ACROSS the strip, so what a tab needs along
                # it is the line height, not the label's width. The width
                # becomes tab_width's problem -- see the note in the
                # constructor.
                return probe.metrics("linespace") + self._geom("tab_pad")
            return probe.measure(str(text)) + self._geom("tab_pad") * 2
        except Exception:
            # Before the widget is mapped, or with a font Tk cannot resolve.
            # Eight pixels a character is wrong but bounded, and the next
            # <Configure> redraw measures properly.
            return self._sx((len(str(text)) * 8) + (self._geom("tab_pad") * 2))

    def _tab_polygon(self, y0, y1, selected=False):
        """
        Points for one tab, in the current style.

        The INNER edge -- the one against the page -- is always square, so a
        selected tab reads as continuous with the page beside it. Only the
        outer edge is shaped.
        """
        x_out = 0 if self._side == "left" else self.canvas.winfo_width()
        strip = self._sx(self._tab_width)
        # Only the SELECTED tab overlaps the page outline.
        #
        # It needs to: the outline is a stroked line centred on its path, so
        # butting exactly against it leaves a hairline, and reaching past it
        # closes the join.
        #
        # An unselected tab must NOT, and did at first. Every tab covered the
        # border where it sat while the gaps between them left it showing,
        # which turned a continuous edge into a dashed one.
        # The selected tab crosses the outline; an unselected one reaches
        # only to the middle of it.
        #
        # The outline is stroked, so it straddles its path -- half inside the
        # page, half out. A tab stopping at the path's coordinate leaves that
        # outer half uncovered, which reads as the border being a pixel
        # thinner beside the tabs than it is elsewhere.
        bw = self._geom("border_width")
        overlap = bw if selected else (bw / 2.0)
        if self._side == "left":
            x_in = strip + overlap
            direction = 1
        else:
            x_in = self.canvas.winfo_width() - strip - overlap
            direction = -1

        if self._tab_style == "angled":
            # A rectangle with its two OUTER corners cut off.
            #
            # The cut runs between a point dx in from the corner along the
            # outer edge and a point dy in from it along the top or bottom
            # edge -- so the tab still reaches the edge of the strip, and only
            # the corners are missing.
            #
            # This replaces a trapezium whose entire outer edge was inset by
            # the slant, leaving the tab floating clear of the strip edge
            # rather than sitting against it. At small slants the shape read
            # as wrong without it being obvious why.
            dx = min(self._geom("tab_chamfer_x"),
                     abs(x_in - x_out) * 0.4)
            dy = min(self._geom("tab_chamfer_y"),
                     (y1 - y0) * self.TAB_CHAMFER_MAX_FRACTION)
            return [x_in, y0,
                    x_out + (dx * direction), y0,
                    x_out, y0 + dy,
                    x_out, y1 - dy,
                    x_out + (dx * direction), y1,
                    x_in, y1]

        # Genuine quarter circles, not a chamfer.
        #
        # Joining the two corner points with a straight line -- which is what
        # this did first -- reads as a 45-degree cut, visibly different from
        # the rounded corners on a CTkButton sitting beside it. Six segments
        # per corner is enough to look like a curve at any sane tab width.
        r = self._geom("tab_corner")
        cx = x_out + (r * direction)
        pts = [x_in, y0]
        if direction > 0:
            # Left strip: top corner sweeps 270 -> 180, bottom 180 -> 90.
            pts += self._arc_points(cx, y0 + r, 270, 180, r)
            pts += self._arc_points(cx, y1 - r, 180, 90, r)
        else:
            # Right strip: 270 -> 360, then 360 -> 450.
            #
            # 450, not 90. _arc_points interpolates linearly between the two
            # angles, so 360 -> 90 sweeps BACKWARDS through 300, 200, 100 --
            # 270 degrees the long way round instead of 90 the short way. The
            # polygon looped back on itself and left a white notch at the
            # corner of every right-hand tab.
            pts += self._arc_points(cx, y0 + r, 270, 360, r)
            pts += self._arc_points(cx, y1 - r, 360, 450, r)
        pts += [x_in, y1]
        return pts

    @staticmethod
    def _arc_points(cx, cy, start_deg, end_deg, radius, steps=6):
        """Points along a circular arc, for building rounded polygons."""
        pts = []
        for i in range(steps + 1):
            a = math.radians(start_deg + (end_deg - start_deg) * i / steps)
            pts.extend([cx + radius * math.cos(a), cy + radius * math.sin(a)])
        return pts

    def _page_outline_points(self, gap):
        """
        An open path around the page area, broken where the selected tab is.

        `gap` is (y_top, y_bottom) on the strip-side edge to leave out, or
        None to close the rectangle. Returned as a single polyline starting at
        one lip of the gap and running the long way round to the other, which
        is what makes the outline appear to curve into the tab.
        """
        x0, y0, x1, y1 = self._content_rect()
        r = self._geom("page_corner")
        bw = self._geom("border_width")
        # Half the stroke, so the drawn line sits inside the rectangle rather
        # than straddling its edge and clipping at the widget boundary.
        h = bw / 2.0
        x0, y0, x1, y1 = x0 + h, y0 + h, x1 - h, y1 - h

        arc = self._arc_points

        if self._side == "left":
            edge = x0              # the strip-side edge
            top_start = [edge, y0 + r]
            path = []
            if gap:
                path += [edge, gap[0]]          # upper lip of the gap
            path += [edge, y0 + r]
            path += arc(x0 + r, y0 + r, 180, 270, r)     # top-left
            path += [x1 - r, y0]
            path += arc(x1 - r, y0 + r, 270, 360, r)     # top-right
            path += [x1, y1 - r]
            path += arc(x1 - r, y1 - r, 0, 90, r)        # bottom-right
            path += [x0 + r, y1]
            path += arc(x0 + r, y1 - r, 90, 180, r)      # bottom-left
            if gap:
                path += [edge, gap[1]]          # lower lip of the gap
            else:
                path += [edge, y0 + r]
            return path

        edge = x1
        path = []
        if gap:
            path += [edge, gap[0]]
        path += [edge, y0 + r]
        path += arc(x1 - r, y0 + r, 0, -90, r)           # top-right
        path += [x0 + r, y0]
        path += arc(x0 + r, y0 + r, 270, 180, r)         # top-left
        path += [x0, y1 - r]
        path += arc(x0 + r, y1 - r, 180, 90, r)          # bottom-left
        path += [x1 - r, y1]
        path += arc(x1 - r, y1 - r, 90, 0, r)            # bottom-right
        if gap:
            path += [edge, gap[1]]
        else:
            path += [edge, y0 + r]
        return path

    def _total_tab_length(self):
        """Pixels the tabs need along the strip, including the gaps."""
        gap = self._geom("tab_gap")
        total = self._geom("strip_margin")
        for name in self._pages:
            total += self._measure(name) + gap
        return total

    def required_length(self):
        """
        The height this widget wants, so every tab is reachable without
        scrolling.

        Provided because the widget cannot insist: a parent packing it with
        fill="both" decides its size regardless. Use it to set a minimum on
        the containing window, or ignore it and let the strip scroll.
        """
        return int(self._total_tab_length() + self._geom("strip_margin"))

    def _max_scroll(self):
        """How far the strip can scroll before the last tab is flush."""
        overflow = self._total_tab_length() - max(self.canvas.winfo_height(), 1)
        return max(int(overflow), 0)

    def _draw_notebook(self):
        """
        Repaints outline and tabs, and recomputes the hit-test bounds.

        NOT named _draw(). CTkFrame has its own _draw(no_color_updates=...)
        and calls it from its constructor, so a method of that name here
        overrides it and the widget fails to build:

            TypeError: _draw() got an unexpected keyword argument
            'no_color_updates'

        Worth knowing for any widget that subclasses a CustomTkinter class
        and wants a drawing method of its own.
        """
        if not hasattr(self, "_canvas"):
            return
        try:
            if not self.canvas.winfo_exists():
                return
        except Exception:
            return

        self.canvas.delete("all")
        self._tab_bounds.clear()
        self.canvas.configure(bg=self._page_background())

        font = self._scaled_font()
        angle = self._text_angle()

        # Pass one: work out where every tab sits, so the outline knows where
        # to leave its gap before anything is drawn.
        gap_amount = self._geom("tab_gap")
        y = self._geom("strip_margin") - self._scroll
        for name in self._pages:
            length = self._measure(name)
            self._tab_bounds[name] = (y, y + length)
            y += length + gap_amount

        # Separators go under the tabs, so a selected tab covers the two
        # beside it and reads as sitting in front.
        if self._show_tab_separators:
            strip = self._sx(self._tab_width)
            sx0 = 0 if self._side == "left" else self.canvas.winfo_width() - strip
            sx1 = strip if self._side == "left" else self.canvas.winfo_width()
            half = self._geom("tab_gap") / 2.0
            # Stopped short at both ends. A separator running the full width
            # of the strip reads as a division of the whole panel rather than
            # a line between two tabs, and collides with the page border at
            # its inner end.
            # The OUTER end stops where the tab corners start -- matched to
            # the shape actually being drawn, so it ends with the curve or the
            # cut rather than a pixel or two past it.
            #
            # The INNER end runs all the way to the page border. Stopping
            # short of it left the separator floating, most visibly on a
            # right-hand strip: the tabs meet the frame, so a line between two
            # of them should too.
            shape_inset = self._geom("tab_corner") \
                if self._tab_style == "rounded" else self._geom("tab_chamfer_x")
            outer_inset = max(shape_inset, self._geom("separator_inset"))
            inner_inset = 0
            if self._side == "left":
                sx0, sx1 = sx0 + outer_inset, sx1 - inner_inset
            else:
                sx0, sx1 = sx0 + inner_inset, sx1 - outer_inset
            names = list(self._tab_bounds)
            for i, name in enumerate(names[:-1]):
                y_between = self._tab_bounds[name][1] + half
                self.canvas.create_line(sx0, y_between, sx1, y_between,
                                         fill=self._colour("border_color"),
                                         width=max(self._sx(1), 1))

        # DRAW ORDER MATTERS, and this is the third arrangement.
        #
        # Unselected tabs, then the page outline, then the selected tab. The
        # outline running OVER the unselected tabs is what keeps it crisp
        # along the strip edge: any attempt to have the tabs meet it exactly
        # leaves a half-pixel of the stroke uncovered, because the stroke
        # straddles its own path. Letting the border win is simpler than
        # trying to butt against it.
        #
        # The selected tab goes last, so it covers the border and reads as
        # sitting in front of the page -- and the outline is drawn with a gap
        # there anyway, so there is nothing to cover but the lips.
        for name, (y0, y1) in self._tab_bounds.items():
            if name == self._current:
                continue
            self._paint_tab(name, y0, y1, font, angle)

        if self._show_page_border:
            gap = self._tab_bounds.get(self._current) if self._current else None
            self.canvas.create_line(
                *self._page_outline_points(gap),
                fill=self._colour("border_color"),
                width=self._geom("border_width"),
                capstyle="round", joinstyle="round", smooth=False)

        if self._current in self._tab_bounds:
            y0, y1 = self._tab_bounds[self._current]
            self._paint_tab(self._current, y0, y1, font, angle)

    def _paint_tab(self, name, y0, y1, font, angle):
        """Draws one tab and its label."""
        if name == self._current:
            fill = self._colour("tab_selected_color")
            text_fill = self._colour("selected_text_color")
        elif name == self._hover and self._state != "disabled":
            fill = self._colour("tab_hover_color")
            text_fill = self._colour("text_color")
        else:
            fill = self._colour("tab_fg_color")
            text_fill = self._colour("text_color")

        outline = self._colour("border_color") if name == self._current else fill
        self.canvas.create_polygon(
            self._tab_polygon(y0, y1, selected=(name == self._current)),
            fill=fill, outline=outline,
            width=self._geom("border_width") if name == self._current else 1)

        strip = self._sx(self._tab_width)
        cx = strip / 2 if self._side == "left" \
            else self.canvas.winfo_width() - (strip / 2)
        self.canvas.create_text(cx, (y0 + y1) / 2, text=str(name),
                                 angle=angle, fill=text_fill, font=font)

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------
    def _on_strip(self, x):
        """Whether an x coordinate falls on the tab strip."""
        strip = self._sx(self._tab_width)
        if self._side == "left":
            return x <= strip
        return x >= self.canvas.winfo_width() - strip

    def _tab_at(self, x, y):
        """The tab name at a canvas coordinate, or None."""
        if not self._on_strip(x):
            return None
        for name, (y0, y1) in self._tab_bounds.items():
            if y0 <= y <= y1:
                return name
        return None

    def _on_click(self, event):
        if self._state == "disabled":
            return "break"
        name = self._tab_at(event.x, event.y)
        if name is not None and name != self._current:
            self.set(name)
        return "break"

    def _on_motion(self, event):
        if self._state == "disabled":
            return
        name = self._tab_at(event.x, event.y)
        if name != self._hover:
            self._hover = name
            self._draw_notebook()

    def _on_leave(self, event=None):
        if self._hover is not None:
            self._hover = None
            self._draw_notebook()

    def _on_wheel(self, event):
        """
        Scrolls the strip when the tabs do not fit.

        Only over the strip, and only when there is something to scroll --
        otherwise the wheel belongs to whatever is on the page.
        """
        if not self._on_strip(getattr(event, "x", 0)):
            return
        ceiling = self._max_scroll()
        if ceiling <= 0:
            return

        if getattr(event, "num", None) == 4:
            delta = -1
        elif getattr(event, "num", None) == 5:
            delta = 1
        else:
            delta = -1 if getattr(event, "delta", 0) > 0 else 1

        self._scroll_by(delta)
        return "break"

    # Accumulated trackpad movement, and the threshold it must cross before
    # the strip moves. Acting on every event is unusably fast -- the same
    # reason ScrollBindingMixin accumulates.
    TOUCHPAD_THRESHOLD = 12.0

    @staticmethod
    def _decode_touchpad_delta(raw_delta):
        """
        Pulls the signed Y component out of a packed <TouchpadScroll> delta.

        Tk packs X and Y into one 32-bit value. The low sixteen bits are Y,
        two's complement -- so the test is `>= 0x8000`, not `> 32768`. Those
        differ at exactly 32768, the smallest NEGATIVE value, which the looser
        test reads as positive and inverts the direction.
        """
        raw = raw_delta & 0xFFFFFFFF
        delta_y = raw & 0xFFFF
        if delta_y >= 0x8000:
            delta_y -= 0x10000
        return delta_y

    def _on_touchpad(self, event):
        """Trackpad equivalent of _on_wheel, gated by an accumulator."""
        if not self._on_strip(getattr(event, "x", 0)):
            return
        if self._max_scroll() <= 0:
            return

        delta_y = self._decode_touchpad_delta(getattr(event, "delta", 0))
        if delta_y == 0:
            return

        accumulated = getattr(self, "_touch_accum", 0.0)
        # Reversing direction resets, so a change of direction responds at
        # once rather than having to cancel out what built up going the other
        # way.
        if (accumulated > 0) != (delta_y > 0):
            accumulated = 0.0
        accumulated += delta_y

        if abs(accumulated) >= self.TOUCHPAD_THRESHOLD:
            self._scroll_by(-1 if accumulated > 0 else 1)
            accumulated = 0.0
        self._touch_accum = accumulated
        return "break"

    def _scroll_by(self, steps):
        """Moves the strip, clamped to what there is to scroll."""
        ceiling = self._max_scroll()
        new = min(max(self._scroll + steps * self._sx(24), 0), ceiling)
        if new != self._scroll:
            self._scroll = new
            self._draw_notebook()

    # ------------------------------------------------------------------
    # Public API -- mirrors sCTkTabview where the two overlap
    # ------------------------------------------------------------------
    def add(self, name):
        """
        Creates a tab and returns its content page, an sCTkFrame.

        Returns the page directly rather than requiring a separate tab()
        call, matching sCTkTabview.
        """
        name = str(name)
        if name in self._pages:
            raise ValueError(f"tab '{name}' already exists")
        page = sCTkFrame(self._page_host, fg_color="transparent",
                         border_width=0)
        page.grid(row=0, column=0, sticky="nsew")
        self._pages[name] = page
        if self._current is None:
            self._current = name
            page.tkraise()
        self._relayout()
        return page

    def tab(self, name):
        """The content page for a tab. Raises KeyError if it does not exist."""
        name = str(name)
        if name not in self._pages:
            raise KeyError(f"no tab named '{name}'")
        return self._pages[name]

    def delete(self, name):
        """Removes a tab and destroys its page."""
        name = str(name)
        if name not in self._pages:
            raise KeyError(f"no tab named '{name}'")
        page = self._pages.pop(name)
        try:
            page.destroy()
        except Exception:
            pass
        if self._current == name:
            self._current = next(iter(self._pages), None)
            if self._current is not None:
                self._pages[self._current].tkraise()
        self._relayout()

    def rename(self, old_name, new_name):
        """
        Renames a tab, keeping its position and its page.

        Re-keys the page registry as well as the label. Renaming by deleting
        and re-adding would move the tab to the end and destroy its children.
        """
        old_name, new_name = str(old_name), str(new_name)
        if old_name not in self._pages:
            raise KeyError(f"no tab named '{old_name}'")
        if new_name in self._pages:
            raise ValueError(f"tab '{new_name}' already exists")
        # Rebuilt rather than mutated, to keep the insertion order.
        self._pages = {(new_name if k == old_name else k): v
                       for k, v in self._pages.items()}
        if self._current == old_name:
            self._current = new_name
        self._draw_notebook()

    def set(self, name):
        """Selects a tab and raises its page."""
        name = str(name)
        if name not in self._pages:
            raise KeyError(f"no tab named '{name}'")
        self._current = name
        self._pages[name].tkraise()
        self._draw_notebook()

    def get(self):
        """The selected tab's name, or None when there are no tabs."""
        return self._current

    def tabs(self):
        """Tab names, in order."""
        return list(self._pages)

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------
    def get_state(self):
        """Equivalent to state() with no argument."""
        return self.state()

    def state(self, mode=None):
        """
        Gets or sets "normal"/"disabled".

        Disabling dims the strip and the outline and stops tab selection. It
        does NOT cascade to the widgets on a page -- same as sCTkTabview, and
        the caller's responsibility.
        """
        if mode is None:
            return self._state
        mode = str(mode).lower()
        self._state = "disabled" if mode == "disabled" else "normal"
        self._hover = None
        self._draw_notebook()
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
                if pname == "state":
                    return ("state", "state", "state", "normal", self._state)
                if pname == "side":
                    return ("side", "side", "Side", "left", self._side)
                if pname == "tab_style":
                    return ("tab_style", "tab_style", "TabStyle", "rounded",
                            self._tab_style)
                if pname == "text_orientation":
                    return ("text_orientation", "text_orientation",
                            "TextOrientation", "auto", self._text_orientation)
                if pname == "show_tab_separators":
                    return ("show_tab_separators", "show_tab_separators",
                            "ShowTabSeparators", "False",
                            str(self._show_tab_separators))
                if pname == "show_page_border":
                    return ("show_page_border", "show_page_border",
                            "ShowPageBorder", "True", str(self._show_page_border))
                if pname == "tab_width":
                    return ("tab_width", "tab_width", "TabWidth", 34,
                            self._tab_width)
                return self._configure_query(pname)

        self._record_theme_overrides(kwargs)

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        if "side" in kwargs:
            new_side = self._check_side(kwargs.pop("side"))
            if new_side != self._side:
                self._side = new_side

        if "tab_style" in kwargs:
            self._tab_style = self._check_style(kwargs.pop("tab_style"))

        if "text_orientation" in kwargs:
            self._text_orientation = self._check_orientation(
                kwargs.pop("text_orientation"))

        if "show_tab_separators" in kwargs:
            val = kwargs.pop("show_tab_separators")
            if isinstance(val, str):
                val = val.strip().lower() in ("true", "1", "yes", "on")
            self._show_tab_separators = bool(val)

        if "show_page_border" in kwargs:
            val = kwargs.pop("show_page_border")
            if isinstance(val, str):
                val = val.strip().lower() in ("true", "1", "yes", "on")
            self._show_page_border = bool(val)

        if "tab_width" in kwargs:
            self._tab_width = int(kwargs.pop("tab_width"))

        # Keys this widget draws with are consumed here: they are not native
        # CTkFrame options, and forwarding one raises
        # "['tab_fg_color'] are not supported arguments".
        for key in list(kwargs):
            if key in self._local_defaults and key not in self._NATIVE_FRAME_KWARGS:
                kwargs.pop(key)

        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        result = super().configure(**kwargs) if kwargs else None
        self._relayout()
        return result

    config = configure

    def cget(self, attribute_name):
        if attribute_name == "state":
            return self._state
        if attribute_name == "side":
            return self._side
        if attribute_name == "tab_style":
            return self._tab_style
        if attribute_name == "text_orientation":
            return self._text_orientation
        if attribute_name == "show_tab_separators":
            return self._show_tab_separators
        if attribute_name == "show_page_border":
            return self._show_page_border
        if attribute_name == "tab_width":
            return self._tab_width
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
        self._draw_notebook()

    def _update_current_visual_state(self):
        """Repaint hook, found by ThemeableWidget._repaint_after_override()."""
        self._draw_notebook()
