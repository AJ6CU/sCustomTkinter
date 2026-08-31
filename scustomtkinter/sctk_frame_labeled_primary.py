#!/usr/bin/python3
"""
sCTkFrameLabeledPrimary

A theme-compliant labeled scrollable container panel -- the higher-emphasis
of the library's two labeled scrollable frame tiers (see also
sCTkFrameLabeledSecondary). Inherits directly from ctk.CTkScrollableFrame so
CustomTkinter handles native scrolling and layout; this class layers
automatic light/dark theme resolution, a visual-only "disabled" state, and
scrollbar-hiding on top.

Base class order matters here: `class sCTkFrameLabeledPrimary(
ctk.CTkScrollableFrame, ThemeableWidget)` puts the native CTk class first, so
every `super()` call in this file's own methods resolves to
ctk.CTkScrollableFrame -- and, beneath it, tkinter.Misc -- never to
ThemeableWidget. ThemeableWidget's own configure()/cget()/_set_appearance_mode()
overrides have been removed entirely for this reason (see
themeable_widget.py's docstring); this widget owns all of its own runtime
color-swapping logic.

"Disabled" here is purely visual -- there is no native way to lock a
CTkFrame-derived container's own interactivity the way a control can be
locked (see sCTkFrameOutlined's docstring for the same reasoning, explicitly
confirmed there). Disabling this widget dims its own colors; it does NOT
automatically disable child widgets placed inside it -- that's the caller's
responsibility, exactly as demonstrated in this project's own test harness
for this widget (looping over the frame's children and calling
.configure(state=...) on each one individually).

Deliberately not scrollable: this widget uses ctk.CTkScrollableFrame purely
to access its native label_text/label_font/label_text_color feature (plain
CTkFrame has no built-in label option) -- not because scrolling is wanted.
The model here is ttk.LabelFrame, which doesn't scroll at all. The scrollbar
is suppressed by matching its colors to the frame background and collapsing
its width to 0, which removes the visible/interactive scrollbar entirely.
Confirmed by the maintainer: this is the intended design, not a gap.
"""
import customtkinter as ctk
from typing import Any, Optional
from .themeable_widget import ThemeableWidget


class sCTkFrameLabeledPrimary(ctk.CTkScrollableFrame, ThemeableWidget):
    """Themeable, high-emphasis labeled scrollable container.

    Adds to native ctk.CTkScrollableFrame:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A visual-only "disabled" state (see module docstring) -- dims border,
        fill, and label text colors; does not lock interactivity, and does
        not cascade to child widgets automatically.
      - Pygubu Designer property introspection for `state`, `fg_color`,
        `border_color`, and `label_text_color` via a single-argument
        configure() call.
      - Scrollbar hiding: the internal scrollbar's colors are forced to match
        the frame's own background and its width collapsed to 0, making it
        invisible while (presumably) leaving scrolling itself functional.
      - winfo_children()/get_children()/get_all_children(): by default,
        winfo_children() filters out children whose class name is exactly
        "CTkLabel", "Label", "CTkFrame", or "Frame" -- internal furniture
        CTkScrollableFrame creates for its own title row and canvas wrapper,
        which would otherwise clutter a naive "what did I add to this frame"
        query. get_children() is this filtered view; get_all_children()
        returns the raw, unfiltered list.

    KNOWN LIMITATION: the winfo_children() filter is a class-NAME string
    check, not a "was this created internally" check. A plain,
    un-themed customtkinter.CTkLabel or customtkinter.CTkFrame added
    directly as a child (bypassing the sCTk-prefixed equivalents) would be
    incorrectly filtered out of get_children() too, since its class name
    matches the same strings being excluded. Themed sCTk widgets (e.g.
    sCTkLabelPrimary) are unaffected, since their class names don't match.

    Deliberately not scrollable -- unlike sCTkScrollableFrame, this class has
    no scroll-binding code (no _toggle_scroll_bindings, no macOS touchpad
    handling), despite both wrapping the same native CTkScrollableFrame. This
    is intentional, confirmed by the maintainer: the model here is
    ttk.LabelFrame, which never scrolls. CTkScrollableFrame is used purely
    for its built-in label feature, and the internal scrollbar is
    deliberately suppressed (see _hide_internal_scrollbars()) rather than
    left functional.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox, sCTkSegmentedButton, and the button
    family. Not separately re-confirmed for this specific widget.
    """

    def __init__(self, master: Optional[Any] = None, **kwargs: Any) -> None:
        """
        Args:
            master: Parent container.
            **kwargs: Any native CTkScrollableFrame argument (e.g. `label_text`),
                or a theme-key override (see the "sCTkFrameLabeledPrimary"
                block in sCTkThemes.json, including its disabled_map).
        """
        # 1. Fire our shared theme logic first. This resolves final_kw
        # (construction-time properties) and the disabled color map. See
        # ThemeableWidget.__init__ for what actually happens here.
        ThemeableWidget.__init__(self, kwargs)

        # 2. Deep-copy the resolved map onto this instance, so later changes
        # here never leak back into the shared theme registry.
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 3. Initialize CustomTkinter natively with the clean final kwargs array.
        super().__init__(master, **self.final_kw)

        self._custom_current_state = "normal"

        # 4. Hide the scrollbar visually on first construction.
        self._hide_internal_scrollbars()

        # 5. Register lifecycle handshake hook, notifying Pygubu-style consumers
        # that construction is complete.
        self._finalize_themeable_lifecycle()

    def _set_appearance_mode(self, mode_string: str) -> None:
        """
        Forwards CustomTkinter's internal light/dark mode change notification to
        the native widget.

        No longer manually re-triggers _update_current_visual_state(). That
        method now passes raw (light, dark) tuples straight through to
        configure() instead of pre-resolving to a single color, so CTk's own
        appearance-mode tracking should repaint correctly on its own -- the
        same approach validated on sCTkComboBox, sCTkSegmentedButton, and the
        button family.

        Args:
            mode_string: The new appearance mode ("Light" or "Dark"), as passed
                by CustomTkinter's internal appearance-mode change machinery.
        """
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally below.
                - the literal string "state": returns a Tkinter-style
                  (name, name, name, default, current) tuple.
                - one of "fg_color"/"border_color"/"label_text_color":
                  returns the same style of tuple, with `current` reflecting
                  the disabled or normal value as appropriate. Note the
                  returned value is str(value), where value may itself be a
                  (light, dark) tuple rather than a single resolved color --
                  a known limitation shared with the wider Pygubu-query
                  investigation set aside elsewhere in this project, not
                  fixed here.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties (same limitation).
            **kwargs: Standard CTkScrollableFrame configuration options, plus:
                passing `state=...` routes through self.state() rather than
                being forwarded as-is.

        Returns:
            The query tuple described above for the single-argument case, or
            whatever super().configure() returns for the keyword-argument case.
        """
        # args is always a tuple -- args[0] is the actual value passed, whether
        # that's a string or a dict. An earlier version of this method compared
        # the wrapped tuple directly (`pname = args`) and forwarded it unwrapped
        # to super().configure(), which is not a valid call shape for the
        # native widget. Don't reintroduce that.
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname == "state":
                    return ("state", "state", "state", "normal", str(self.state()))
                if pname in ["fg_color", "border_color", "label_text_color"]:
                    current_state = str(self.state()).lower()
                    val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                    return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))
                return super().configure(pname)

        if "state" in kwargs:
            target_state = kwargs.pop("state")
            self.state(target_state)

        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        if kwargs:
            result = super().configure(**kwargs)
            self._hide_internal_scrollbars()
            return result
        return None

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. Without this line, calling .config(...) on an instance
    # would silently skip this entire override and land on the native widget's
    # configure() directly, bypassing theming and state handling entirely.
    config = configure

    def winfo_children(self, include_private: bool = False) -> list:
        """
        By default, filters out children whose exact class name is "CTkLabel",
        "Label", "CTkFrame", or "Frame" -- internal furniture CTkScrollableFrame
        creates for its own title row and canvas wrapper. See this class's
        docstring for a known limitation of this approach.

        Args:
            include_private: If True, returns the raw, unfiltered list instead.

        Returns:
            A list of child widgets.
        """
        raw_children = super().winfo_children()
        if include_private:
            return raw_children

        filtered_children = []
        for child in raw_children:
            if child.__class__.__name__ not in ["CTkLabel", "Label", "CTkFrame", "Frame"]:
                filtered_children.append(child)
        return filtered_children

    def get_children(self) -> list:
        """Equivalent to winfo_children(include_private=False)."""
        return self.winfo_children(include_private=False)

    def get_all_children(self) -> list:
        """Equivalent to winfo_children(include_private=True)."""
        return self.winfo_children(include_private=True)

    def get_state(self) -> str:
        """Equivalent to calling state() with no argument."""
        return self.state()

    def state(self, mode: Optional[str] = None) -> str:
        """
        Gets or sets the widget's visual "disabled" state. This is purely
        cosmetic -- see module docstring for why there's no native
        interactivity lock, and why child widgets are not automatically
        disabled along with the frame.

        Args:
            mode: If None, returns the current state without changing
                anything. Otherwise, only the literal string "disabled"
                (case-insensitive) is treated as disabled; anything in
                ("normal", "enabled", "active") is treated as enabled.

        Returns:
            The resulting state ("normal" or "disabled").
        """
        if mode is None:
            return getattr(self, "_custom_current_state", "normal")

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
            self._update_current_visual_state()

        elif mode == "disabled":
            super_payload = {}
            for key in ("fg_color", "border_color", "label_text_color"):
                val = self._custom_disabled_map.get(key)
                if val is not None:
                    super_payload[key] = val

            if super_payload:
                super().configure(**super_payload)

            self._custom_current_state = "disabled"
            self._hide_internal_scrollbars()
        return self._custom_current_state

    def _update_current_visual_state(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, for
        the normal (enabled) state.

        Called after construction (indirectly) and on every state("normal")
        call.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.
        """
        config_payload = {}
        for key in ("fg_color", "border_color", "label_text_color", "border_width", "label_font"):
            val = self._local_defaults.get(key)
            if val is not None:
                config_payload[key] = val

        if config_payload:
            super().configure(**config_payload)
        self._hide_internal_scrollbars()

    def _hide_internal_scrollbars(self) -> None:
        """
        Forces the internal scrollbar's colors to match the frame's own
        background and collapses its width to 0, making it visually
        invisible.

        If fg_color resolves to the literal string "transparent" (e.g. if a
        caller explicitly overrides it), falls back to a hardcoded neutral
        pair rather than passing "transparent" through to the scrollbar,
        since there's no single real background color to match in that case.
        This fallback is not theme-driven and is a deliberate exception to
        this project's general "no hardcoded colors" principle -- there's no
        required theme key this could reasonably read from instead, since the
        whole point is handling the case where the real background is
        genuinely ambiguous (transparent).
        """
        try:
            bg_color_raw = super().cget("fg_color")
            resolved_bg = bg_color_raw

            if bg_color_raw == "transparent":
                current_mode = str(ctk.get_appearance_mode()).lower()
                resolved_bg = "#2B2B2B" if current_mode == "dark" else "#DBDBDB"

            if hasattr(self, "_scrollbar") and self._scrollbar is not None:
                self._scrollbar.configure(
                    fg_color=resolved_bg,
                    button_color=resolved_bg,
                    button_hover_color=resolved_bg,
                    width=0
                )
        except Exception:
            pass

    def get_container(self):
        """Returns self. Provided for API symmetry with composite widgets that wrap a separate inner container."""
        return self
