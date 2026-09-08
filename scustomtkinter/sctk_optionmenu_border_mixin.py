#!/usr/bin/python3
"""
sCTkOptionMenuBorderMixin

Gives a CTkOptionMenu subclass a real border.

WHY THIS EXISTS. Native ctk.CTkOptionMenu has no border option -- its
constructor accepts corner_radius and fg_color but neither border_width nor
border_color. That single gap is what forced sCTkOptionMenuSecondary to be a
COMPOSITE: a CTkFrame wrapping a plain option menu, because the frame could
draw the outline the option menu could not.

The composite cost more than it looked. Secondary's values, command and
variable live on the inner menu, so cget("values") on the widget itself
returned None while Primary returned a list -- two widgets meant to be
interchangeable, disagreeing. Every option CustomTkinter adds to CTkOptionMenu
has to be forwarded by hand, forever. And the widget's SHAPE was dictated by
one theme's colour choices: Secondary needs a border only because its fill is
nearly the same as the background it sits on. Swap the two themes and the
structure is wrong.

CustomTkinter can already draw this border. CTkOptionMenu._draw() calls

    self._draw_engine.draw_rounded_rect_with_border_vertical_split(
        width, height, corner_radius, 0, left_section_width)

with a hardcoded 0 where the border width belongs. The draw engine supports it
and tags the result 'border_parts_left' and 'border_parts_right'; the widget
simply never asks. This mixin asks.

UPSTREAM DEPENDENCY. This overrides a private method and calls a private draw
engine, which the rest of this library avoids -- sCTkTabview explicitly
declined to write CTkTabview's private spacing attributes for exactly this
reason. It is justified here because the alternative is two widgets with
different shapes and a forwarding list that grows forever. But it is a real
dependency on CustomTkinter internals and could break on an upstream release.
If it does, the symptom is a missing border, not a crash: _draw() falls back to
whatever the native widget drew.
"""
from typing import Any, Optional, Tuple, Union


class sCTkOptionMenuBorderMixin:
    """
    Adds `border_width` and `border_color` to a CTkOptionMenu subclass.

    Use it before the native class in the base list, so this class's _draw()
    runs first and can call super() to let the native one draw underneath:

        class sCTkOptionMenuPrimary(sCTkOptionMenuBorderMixin,
                                    ctk.CTkOptionMenu, ThemeableWidget):
    """

    def _init_border(self, border_width=0, border_color=None):
        """
        Records the border settings. Call from __init__ AFTER the native
        constructor has run, since the first redraw needs the canvas.

        Args:
            border_width: Thickness in pixels. 0 draws nothing, which is the
                native widget's own appearance.
            border_color: A colour, or a (light, dark) pair. None with a
                non-zero width draws nothing, since there would be no colour
                to draw in.
        """
        self._border_width = float(border_width or 0)
        self._border_color = border_color
        self._redraw_border()

    def _draw(self, no_color_updates=False):
        """
        Draws the widget, with a border when one is set.

        REPLACES ctk.CTkOptionMenu._draw() rather than extending it. That is a
        deliberate fork of a private method, and the reason is in the draw
        engine: draw_rounded_rect_with_border_vertical_split() only insets the
        inner fill when border_width > 0 --

            if corner_radius >= border_width:
                inner_corner_radius = corner_radius - border_width

        -- and CTkOptionMenu calls it with a hardcoded 0. The fill therefore
        covers the full area, and a border drawn afterwards is painted over no
        matter how it is stacked or raised. Calling the engine a second time
        does not help either: the inner parts from the first call are still
        there at full size.

        One call at the real border width draws both parts correctly.

        With no border set this defers to the native method, so the widget
        behaves exactly as CustomTkinter's when the feature is unused.

        UPSTREAM DEPENDENCY. This reproduces the body of a private method. If
        CustomTkinter changes CTkOptionMenu._draw(), we do not inherit the
        change. Contained to this one method, and the failure mode is visual.
        """
        if not getattr(self, "_border_width", 0) or self._border_color is None:
            super()._draw(no_color_updates)
            return

        left_section_width = self._current_width - self._current_height
        requires_recoloring = self._draw_engine.draw_rounded_rect_with_border_vertical_split(
            self._apply_widget_scaling(self._current_width),
            self._apply_widget_scaling(self._current_height),
            self._apply_widget_scaling(self._corner_radius),
            self._apply_widget_scaling(self._border_width),
            self._apply_widget_scaling(left_section_width),
        )
        requires_recoloring_2 = self._draw_engine.draw_dropdown_arrow(
            self._apply_widget_scaling(self._current_width - (self._current_height / 2)),
            self._apply_widget_scaling(self._current_height / 2),
            self._apply_widget_scaling(self._current_height / 3),
        )

        if no_color_updates is False or requires_recoloring or requires_recoloring_2:
            self._canvas.configure(bg=self._apply_appearance_mode(self._bg_color))
            self._canvas.itemconfig(
                "inner_parts_left",
                outline=self._apply_appearance_mode(self._fg_color),
                fill=self._apply_appearance_mode(self._fg_color))
            self._canvas.itemconfig(
                "inner_parts_right",
                outline=self._apply_appearance_mode(self._button_color),
                fill=self._apply_appearance_mode(self._button_color))

            # The part the native method has no equivalent for. Both tags,
            # because the shape is split into body and arrow button -- missing
            # either leaves half the outline in the wrong colour.
            border_colour = self._apply_appearance_mode(self._border_color)
            for tag in ("border_parts_left", "border_parts_right"):
                self._canvas.itemconfig(tag, outline=border_colour,
                                        fill=border_colour)

            self._text_label.configure(
                fg=self._apply_appearance_mode(self._text_color))
            if self._state == "disabled":
                self._text_label.configure(
                    fg=self._apply_appearance_mode(self._text_color_disabled))
                self._canvas.itemconfig(
                    "dropdown_arrow",
                    fill=self._apply_appearance_mode(self._text_color_disabled))
            else:
                self._canvas.itemconfig(
                    "dropdown_arrow",
                    fill=self._apply_appearance_mode(self._text_color))

    def _redraw_border(self):
        """
        Triggers a redraw after a border property changes.

        The drawing itself is in _draw() -- the border cannot be added
        separately, because the inner fill has to be inset by the border width
        in the same engine call.
        """
        try:
            self._draw()
        except Exception:
            # An upstream change to the engine or to the attributes read above
            # lands here. Losing the border is a visual regression; raising
            # would take the whole widget down.
            pass

    # ------------------------------------------------------------------
    # Property access
    # ------------------------------------------------------------------
    def _configure_border(self, kwargs):
        """
        Consumes border_width and border_color from a configure() call.

        Call from configure() BEFORE forwarding to the native widget, which
        would reject both as unknown options.

        Args:
            kwargs: The keyword dict. Consumed keys are removed in place.

        Returns:
            True if either was present, so the caller knows to redraw.
        """
        touched = False
        if "border_width" in kwargs:
            self._border_width = float(kwargs.pop("border_width") or 0)
            touched = True
        if "border_color" in kwargs:
            self._border_color = kwargs.pop("border_color")
            touched = True
        if touched:
            self._redraw_border()
        return touched

    def _cget_border(self, key):
        """
        Returns a border property, or the sentinel below if `key` is neither.

        Written this way rather than returning None because None is a valid
        value for border_color.
        """
        if key == "border_width":
            return getattr(self, "_border_width", 0)
        if key == "border_color":
            return getattr(self, "_border_color", None)
        return self._NOT_A_BORDER_PROPERTY

    _NOT_A_BORDER_PROPERTY = object()