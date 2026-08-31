#!/usr/bin/python3
"""
sCTkFrameLabeledSecondary

A theme-compliant labeled scrollable container panel -- the lower-emphasis
of the library's two labeled scrollable frame tiers (see also
sCTkFrameLabeledPrimary). Inherits directly from ctk.CTkScrollableFrame so
CustomTkinter handles native scrolling and layout; this class layers
automatic light/dark theme resolution, a visual-only "disabled" state, and
scrollbar-hiding on top.

Base class order matters here: `class sCTkFrameLabeledSecondary(
ctk.CTkScrollableFrame, ThemeableWidget)` puts the native CTk class first, so
every `super()` call in this file's own methods resolves to
ctk.CTkScrollableFrame -- and, beneath it, tkinter.Misc -- never to
ThemeableWidget. ThemeableWidget's own configure()/cget()/_set_appearance_mode()
overrides have been removed entirely for this reason (see
themeable_widget.py's docstring); this widget owns all of its own runtime
color-swapping logic.

"Disabled" here is purely visual, same reasoning as sCTkFrameLabeledPrimary
and sCTkFrameOutlined -- there is no native way to lock a CTkFrame-derived
container's own interactivity. Disabling this widget dims its own colors; it
does NOT automatically disable child widgets placed inside it.

Deliberately not scrollable, same as sCTkFrameLabeledPrimary -- this widget
uses ctk.CTkScrollableFrame purely for its native label feature, modeled on
ttk.LabelFrame (which never scrolls), not because scrolling is wanted. The
internal scrollbar is deliberately suppressed via _hide_internal_scrollbars().
Confirmed by the maintainer: this is the intended design.
"""
from typing import Any, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkFrameLabeledSecondary(ctk.CTkScrollableFrame, ThemeableWidget):
    """Themeable, lower-emphasis labeled scrollable container.

    Adds to native ctk.CTkScrollableFrame:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A visual-only "disabled" state -- see module docstring.
      - Pygubu Designer property introspection for `state`, `fg_color`,
        `border_color`, and `label_text_color` via a single-argument
        configure() call.
      - Scrollbar hiding: the internal scrollbar's colors are forced to match
        the frame's own background and its width collapsed to 0.
      - winfo_children()/get_children()/get_all_children() -- same filtering
        behavior and same known limitation as sCTkFrameLabeledPrimary; see
        that class's docstring for the full explanation.

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
                or a theme-key override (see the "sCTkFrameLabeledSecondary"
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
        # that construction is complete. FIX: an earlier version of this file
        # never called this at all -- meaning any on_first_object_cb callback
        # provided to this widget would silently never fire. Every other
        # widget in this project calls this at the end of __init__; this one
        # was a genuine omission, not a deliberate difference.
        self._finalize_themeable_lifecycle()

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally below.
                - the literal string "state": returns a Tkinter-style
                  (name, name, name, default, current) tuple.
                - one of "fg_color"/"border_color"/"label_text_color":
                  returns the same style of tuple. Note the returned value is
                  str(value), where value may itself be a (light, dark) tuple
                  rather than a single resolved color -- a known limitation
                  shared with the wider Pygubu-query investigation set aside
                  elsewhere in this project, not fixed here.
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
        # that's a string or a dict. An earlier version of this method set
        # `pname = args` directly, with no unwrapping attempt at all, so the
        # query branches below never matched anything, and the fallback
        # forwarded the wrapped tuple itself to super().configure() -- not a
        # valid call shape for the native widget. Don't reintroduce that.
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
    # subclass defines. An earlier version of this file was MISSING this line
    # entirely: calling .config(...) on an instance silently skipped this
    # entire override and landed on the native widget's configure() directly,
    # bypassing theming and state handling completely -- confirmed as a
    # critical bug on sCTkSegmentedButton earlier in this project's audit; the
    # same fix applies here.
    config = configure

    def get_state(self) -> str:
        """Equivalent to calling state() with no argument."""
        return self.state()

    def state(self, mode: Optional[str] = None) -> str:
        """
        Gets or sets the widget's visual "disabled" state. Purely cosmetic --
        see module docstring.

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
                if key in self._custom_disabled_map and self._custom_disabled_map[key] is not None:
                    super_payload[key] = self._custom_disabled_map[key]

            if super_payload:
                super().configure(**super_payload)

            self._custom_current_state = "disabled"
            self._hide_internal_scrollbars()
        return self._custom_current_state

    def _update_current_visual_state(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, for
        the normal (enabled) state.

        Passes raw (light, dark) tuples straight through to configure() --
        this file already did so before this project's audit, unlike most
        other widgets that needed the pre-resolved-color pattern removed.
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
        """
        try:
            bg_color = super().cget("fg_color")
            if hasattr(self, "_scrollbar") and self._scrollbar is not None:
                self._scrollbar.configure(
                    fg_color=bg_color,
                    button_color=bg_color,
                    button_hover_color=bg_color,
                    width=0
                )
        except Exception:
            pass

    def winfo_children(self, include_private: bool = False) -> list:
        """
        By default, filters out children whose exact class name is "CTkLabel",
        "Label", "CTkFrame", or "Frame". See sCTkFrameLabeledPrimary's
        docstring for the known limitation of this approach.

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

    def get_container(self):
        """Returns self. Provided for API symmetry with composite widgets that wrap a separate inner container."""
        return self
