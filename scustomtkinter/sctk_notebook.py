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

WHY THE STRIP IS A CANVAS. Tab labels run along the strip rather than across
it, so the text is rotated ninety degrees. A Tk button cannot rotate its text;
a canvas text item can, via its `angle` option. That one requirement decides
the whole implementation: the tabs are drawn shapes, and selection, hover and
hit-testing are this class's own code rather than a button's.

The content pages are real sCTkFrame widgets, stacked in the same cell and
raised as needed -- the same approach sCTkTabview uses, and for the same
reason: a page keeps its children and its geometry between visits.
"""
import tkinter as tk
import tkinter.font as tkfont
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
    )

    # Required inside disabled_map. The strip dims; the page area does not,
    # matching the dials and sCTkScrollableFrame -- the content carries its
    # own state, and a greyed page would hide it.
    _REQUIRED_DISABLED_KEYS = (
        "text_color", "tab_fg_color", "tab_selected_color",
    )

    # Keys this widget reads itself. They must not reach CTkFrame, which
    # raises on anything it does not recognise.
    _NATIVE_FRAME_KWARGS = frozenset({
        "width", "height", "corner_radius", "border_width", "bg_color",
        "fg_color", "border_color", "background_corner_colors",
        "overwrite_preferred_drawing_method",
    })

    # Geometry of the strip, in UNSCALED pixels. Every one of these is put
    # through _apply_widget_scaling() before it reaches the canvas, so the
    # strip grows with the rest of the interface on a scaled display. Drawing
    # raw pixels on a CTkCanvas is the easy mistake here: the canvas widget
    # scales, the coordinates inside it do not.
    #
    # Class attributes so a subclass or a single instance can retune them
    # without a theme key each.
    TAB_GAP = 2             # vertical space between adjacent tabs
    TAB_PAD = 18            # space either end of a label, along the tab
    TAB_TEXT_INSET = 3      # keeps rotated text off the strip edge
    TAB_CORNER = 6          # corner rounding on the outer edge of a tab

    def __init__(self, master=None, side="left", tab_width=34,
                 state="normal", **kw):
        """
        Args:
            master: Parent container.
            side: Which edge the strip sits on, "left" or "right".
            tab_width: Width of the strip in pixels. Explicit rather than
                measured, because the strip takes space from the pages and a
                layout that shifts when a tab is renamed is worse than one
                the caller sets.
            state: "normal" or "disabled".
            **kw: Native CTkFrame arguments, or theme-key overrides.
        """
        self._side = str(side).lower()
        if self._side not in ("left", "right"):
            raise ValueError(
                f'side must be "left" or "right", not "{side}"')
        self._tab_width = int(tab_width)

        ThemeableWidget.__init__(self, kw)

        # Colours are read from the RAW registry, not final_kw.
        #
        # ThemeableWidget strips its CUSTOM_VECTOR_KEYS -- text_color among
        # them -- out of final_kw so they cannot reach a native constructor.
        # Reading them back from final_kw afterwards finds nothing, which is
        # the trap that left the whole dial family rendering in hardcoded
        # fallbacks. See sCTkDial.md, "Reading theme colours".
        raw_block = _tw.GLOBAL_THEME_REGISTRY.get(self.__class__.__name__) or {}
        raw_colors = {k: v for k, v in raw_block.items()
                      if not isinstance(v, dict)}
        self._local_defaults = ThemeableWidget._convert_lists_to_tuples(raw_colors)
        self._local_defaults.update(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)
        self._validate_theme_keys()

        native_kwargs = {k: v for k, v in self.final_kw.items()
                         if k in self._NATIVE_FRAME_KWARGS}
        super().__init__(master, **native_kwargs)

        self._state = "normal" if str(state).lower() == "normal" else "disabled"

        # name -> sCTkFrame, in insertion order. Ordinary dicts preserve it,
        # and tab order is the insertion order.
        self._pages = {}
        self._current = None
        self._hover = None          # name under the pointer, or None
        self._tab_bounds = {}       # name -> (y_top, y_bottom) for hit-testing

        self._strip = ctk.CTkCanvas(self,
                                    width=self._apply_widget_scaling(self._tab_width),
                                    highlightthickness=0, bd=0)
        self._page_host = ctk.CTkFrame(self, fg_color="transparent",
                                       border_width=0)
        self._place_parts()

        self._strip.bind("<Button-1>", self._on_strip_click)
        self._strip.bind("<Motion>", self._on_strip_motion)
        self._strip.bind("<Leave>", self._on_strip_leave)
        self._strip.bind("<Configure>", lambda e: self._draw_strip())

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

    def _place_parts(self):
        """Packs the strip and the page area on the configured side."""
        self._strip.pack_forget()
        self._page_host.pack_forget()
        if self._side == "left":
            self._strip.pack(side="left", fill="y")
            self._page_host.pack(side="left", fill="both", expand=True)
        else:
            self._strip.pack(side="right", fill="y")
            self._page_host.pack(side="right", fill="both", expand=True)
        self._strip.configure(width=self._apply_widget_scaling(self._tab_width))

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

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def _measure(self, text):
        """
        Length a label needs ALONG the strip, in pixels.

        Measured rather than estimated from character count: a proportional
        font makes "IIII" and "WWWW" differ by more than a factor of two, and
        tabs sized by character count would collide or leave gaps.
        """
        try:
            probe = tkfont.Font(font=self._scaled_font())
            return probe.measure(str(text)) + self._sx(self.TAB_PAD * 2)
        except Exception:
            # Before the widget is mapped, or with a font Tk cannot resolve.
            # Eight pixels a character is wrong but bounded, and the next
            # <Configure> redraw measures properly.
            return self._sx((len(str(text)) * 8) + (self.TAB_PAD * 2))

    def _sx(self, value):
        """Scales a dimension for drawing. Shorthand, used on every constant."""
        return self._apply_widget_scaling(value)

    def _scaled_font(self):
        """
        The theme font with its size scaled.

        A canvas text item takes a plain font tuple, which CustomTkinter's
        own font scaling never sees -- so without this the labels would stay
        the same size while everything around them grew.
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

    def _rounded_tab(self, x0, y0, x1, y1, fill):
        """
        Draws one tab as a polygon, rounded on its OUTER edge only.

        The inner edge stays square so the selected tab reads as continuous
        with the page beside it, the way a physical tab divider does.
        """
        r = self._sx(self.TAB_CORNER)
        if self._side == "left":
            # Rounded on the left (outer) edge.
            pts = [x1, y0,
                   x0 + r, y0,
                   x0, y0 + r,
                   x0, y1 - r,
                   x0 + r, y1,
                   x1, y1]
        else:
            # Rounded on the right (outer) edge.
            pts = [x0, y0,
                   x1 - r, y0,
                   x1, y0 + r,
                   x1, y1 - r,
                   x1 - r, y1,
                   x0, y1]
        return self._strip.create_polygon(pts, fill=fill, outline=fill,
                                          smooth=False, tags="tab")

    def _draw_strip(self):
        """Repaints the whole strip and recomputes the hit-test bounds."""
        if not hasattr(self, "_strip"):
            return
        try:
            if not self._strip.winfo_exists():
                return
        except Exception:
            return

        self._strip.delete("all")
        self._tab_bounds.clear()

        bg = self._resolve_color(self._local_defaults.get("fg_color"))
        if bg == "transparent":
            bg = self._detect_color_of_master()
            if bg in (None, "transparent"):
                bg = self._resolve_color(
                    ctk.ThemeManager.theme["CTk"]["fg_color"])
        self._strip.configure(bg=bg)

        width = self._sx(self._tab_width)
        font = self._scaled_font()
        # Rotated so the text runs UP a left-hand strip and DOWN a right-hand
        # one -- in both cases reading from the outside in, which is how a
        # book's spine is set.
        angle = 90 if self._side == "left" else 270

        y = self._sx(self.TAB_GAP)
        for name in self._pages:
            length = self._measure(name)
            y0, y1 = y, y + length

            if name == self._current:
                fill = self._colour("tab_selected_color")
                text_fill = self._colour("selected_text_color")
            elif name == self._hover and self._state != "disabled":
                fill = self._colour("tab_hover_color")
                text_fill = self._colour("text_color")
            else:
                fill = self._colour("tab_fg_color")
                text_fill = self._colour("text_color")

            self._rounded_tab(0, y0, width, y1, fill)
            self._strip.create_text(width / 2, (y0 + y1) / 2,
                                    text=str(name), angle=angle,
                                    fill=text_fill, font=font, tags="tab")

            self._tab_bounds[name] = (y0, y1)
            y = y1 + self._sx(self.TAB_GAP)

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------
    def _tab_at(self, y):
        """The tab name at a y coordinate on the strip, or None."""
        for name, (y0, y1) in self._tab_bounds.items():
            if y0 <= y <= y1:
                return name
        return None

    def _on_strip_click(self, event):
        if self._state == "disabled":
            return "break"
        name = self._tab_at(event.y)
        if name is not None and name != self._current:
            self.set(name)
        return "break"

    def _on_strip_motion(self, event):
        if self._state == "disabled":
            return
        name = self._tab_at(event.y)
        if name != self._hover:
            self._hover = name
            self._draw_strip()

    def _on_strip_leave(self, event=None):
        if self._hover is not None:
            self._hover = None
            self._draw_strip()

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
        self._page_host.grid_rowconfigure(0, weight=1)
        self._page_host.grid_columnconfigure(0, weight=1)
        self._pages[name] = page
        if self._current is None:
            self._current = name
            page.tkraise()
        self._draw_strip()
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
        self._draw_strip()

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
        self._draw_strip()

    def set(self, name):
        """Selects a tab and raises its page."""
        name = str(name)
        if name not in self._pages:
            raise KeyError(f"no tab named '{name}'")
        self._current = name
        self._pages[name].tkraise()
        self._draw_strip()

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

        Disabling dims the strip and stops tab selection. It does NOT cascade
        to the widgets on a page -- same as sCTkTabview, and the caller's
        responsibility.
        """
        if mode is None:
            return self._state
        mode = str(mode).lower()
        self._state = "disabled" if mode == "disabled" else "normal"
        self._hover = None
        self._draw_strip()
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
                if pname == "tab_width":
                    return ("tab_width", "tab_width", "TabWidth", 34,
                            self._tab_width)
                return self._configure_query(pname)

        self._record_theme_overrides(kwargs)

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        if "side" in kwargs:
            new_side = str(kwargs.pop("side")).lower()
            if new_side not in ("left", "right"):
                raise ValueError(
                    f'side must be "left" or "right", not "{new_side}"')
            if new_side != self._side:
                self._side = new_side
                self._place_parts()

        if "tab_width" in kwargs:
            self._tab_width = int(kwargs.pop("tab_width"))
            self._strip.configure(
                width=self._apply_widget_scaling(self._tab_width))

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
        self._draw_strip()
        return result

    config = configure

    def cget(self, attribute_name):
        if attribute_name == "state":
            return self._state
        if attribute_name == "side":
            return self._side
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
        self._draw_strip()

    def _update_current_visual_state(self):
        """Repaint hook, found by ThemeableWidget._repaint_after_override()."""
        self._draw_strip()
