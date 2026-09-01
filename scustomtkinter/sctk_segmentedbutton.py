#!/usr/bin/python3
"""
sCTkSegmentedButton

A theme-compliant segmented button strip widget: a horizontal row of connected
text buttons where selecting one automatically unselects the others (similar to
a row of radio buttons). Inherits directly from ctk.CTkSegmentedButton so that
CustomTkinter handles native state changes, input locks, and button rendering;
this class layers automatic light/dark theme resolution and a distinct
enabled/disabled visual state on top.

Base class order matters here: `class sCTkSegmentedButton(ctk.CTkSegmentedButton,
ThemeableWidget)` puts the native CTk class first. That means every `super()`
call in this file's own methods (configure(), _set_appearance_mode(), etc.)
resolves to ctk.CTkSegmentedButton -- and, beneath it, tkinter.Misc -- never to
ThemeableWidget. ThemeableWidget's own configure()/cget()/_set_appearance_mode()
overrides have been removed entirely for this reason (see themeable_widget.py's
docstring); this widget owns all of its own runtime color-swapping logic.
"""
from typing import Any, Callable, Optional
import tkinter as tk
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkSegmentedButton(ctk.CTkSegmentedButton, ThemeableWidget):
    """Themeable segmented button strip.

    Adds to native ctk.CTkSegmentedButton:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A distinct enabled/disabled visual state, tracked in
        self._custom_current_state and swapped via _apply_custom_theme_colors().
      - Per-segment text-color handling that keeps the currently-selected
        segment visually distinct even while the whole control is disabled.

    Every color this widget applies comes from sCTkThemes.json; there are no
    hardcoded hex values in this class. Colors are passed through to configure()
    as raw (light, dark) tuples rather than pre-resolved to a single value, so
    CustomTkinter's own appearance-mode tracking repaints them automatically on
    a light/dark switch -- confirmed by direct testing, including while disabled.
    """

    def __init__(self, master: Optional[Any] = None, **kw: Any) -> None:
        """
        Args:
            master: Parent container.
            **kw: `values` (list[str]), `variable` (tkinter.StringVar), and
                `command` (callable) are pulled out explicitly below. Everything
                else is either a native CTkSegmentedButton argument or a
                theme-key override (see the "sCTkSegmentedButton" block in
                sCTkThemes.json).

        Note: `unselected_color`, `unselected_hover_color`, `border_width`,
        `border_color`, and `selected_color_padding` are silently dropped from
        the constructor kwargs below, regardless of what's passed in here --
        they're only ever sourced from the theme file. See
        _apply_custom_theme_colors() for why `unselected_color` in particular
        is never independently configurable even there.
        """
        # 1. Capture widget-specific attributes early, before the mixin's own
        # configuration pass. These must come out of kw BEFORE ThemeableWidget.__init__
        # runs, since that call treats every remaining key in kw as a theme-overridable
        # property and would otherwise try to merge these into final_kw too.
        values = kw.pop("values", None)
        variable: Optional[tk.StringVar] = kw.pop("variable", None)
        command: Optional[Callable] = kw.pop("command", None)

        # 2. Fire our shared theme logic to map properties natively out of themes.json.
        # This resolves final_kw (construction-time properties) and the disabled/pressed/
        # alarm color maps. See ThemeableWidget.__init__ for what actually happens here.
        ThemeableWidget.__init__(self, kw)
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)
        self._validate_theme_keys()

        # 3. Remove keys the native CTkSegmentedButton constructor either doesn't
        # accept, or that would break its internal layout if set at construction
        # time (the border/padding options in particular). These are applied later,
        # after construction, exclusively through _apply_custom_theme_colors() --
        # except unselected_color, which is never sourced from the theme at all;
        # it's always derived from fg_color instead, by design (see that method).
        self.final_kw.pop("state", None)
        for key in ["unselected_color", "unselected_hover_color", "border_width", "border_color",
                    "selected_color_padding"]:
            self.final_kw.pop(key, None)

        # 4. Initialize CustomTkinter safely with the pristine final kwargs array.
        super().__init__(master, **self.final_kw)
        self._custom_current_state = "normal"

        if values is not None: super().configure(values=values)
        if variable is not None: super().configure(variable=variable)
        if command is not None: super().configure(command=command)

        # Set up a delayed look-sync pass on startup. This delay is necessary,
        # not cosmetic: CTkSegmentedButton builds its internal per-segment buttons
        # (self._buttons_dict) asynchronously, and they don't exist yet at the
        # moment super().__init__() returns above. _apply_custom_theme_colors()
        # bails out early if _buttons_dict isn't populated, so calling it
        # immediately here would silently do nothing.
        self.after(15, self._apply_custom_theme_colors)
        self._finalize_themeable_lifecycle()

    def configure(self, *args: Any, **kwargs: Any) -> None:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally below.
                - anything else (typically a property-name string): forwarded
                  directly to the native widget's configure(). This does NOT
                  return a Pygubu-style query tuple the way sCTkComboBox /
                  sCTkCheckBox do for a handful of hardcoded property names --
                  the wider Pygubu single-argument query behavior across the
                  library is a known follow-up item, not specific to this widget.
            **kwargs: Standard CTkSegmentedButton configuration options, plus:
                - values / variable / command: routed through super().configure()
                  individually, same as in __init__.
                - state: routed through self.state() rather than forwarded
                  as-is (see state() for why that distinction matters).

        Returns:
            None in the keyword-argument case. Whatever the native
            super().configure() returns in the single-positional-argument case.
        """
        # args is always a tuple -- args[0] is the actual value passed, whether
        # that's a string or a dict. Comparing or forwarding `args` itself
        # (instead of `args[0]`) was a real bug earlier in this project's audit;
        # don't reintroduce it.
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                return super().configure(args[0])

        if "values" in kwargs: super().configure(values=kwargs.pop("values"))
        if "variable" in kwargs: super().configure(variable=kwargs.pop("variable"))
        if "command" in kwargs: super().configure(command=kwargs.pop("command"))

        # Routing "state" through self.state() (rather than leaving it in kwargs
        # to fall through to super().configure() below) is what keeps
        # self._custom_current_state, the native interactive lock, and the
        # disabled color swap all in sync. Leaving it in kwargs previously
        # locked the widget correctly but left get_state() permanently wrong.
        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)

        if kwargs:
            super().configure(**kwargs)

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. Without this line, calling .config(...) on an instance
    # would silently skip this entire override and land on the native widget's
    # configure() directly, bypassing theming, state handling, and the
    # positional-argument handling above.
    config = configure

    def _set_appearance_mode(self, mode_string: str) -> None:
        """
        Forwards CustomTkinter's internal light/dark mode change notification to
        the native widget.

        No longer manually re-triggers _apply_custom_theme_colors(). That method
        now passes raw (light, dark) tuples straight through to configure()
        instead of pre-resolving to a single color, so CTk's own appearance-mode
        tracking repaints correctly on its own -- confirmed by direct testing.
        If colors ever stop following mode changes (especially while disabled),
        that's the signal this no longer holds and the manual re-trigger needs
        to come back.

        Args:
            mode_string: The new appearance mode ("Light" or "Dark"), as passed
                by CustomTkinter's internal appearance-mode change machinery.
        """
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass

    def state(self, mode: Optional[str] = None) -> str:
        """
        Gets or sets the widget's enabled/disabled visual state.

        Uses self._custom_current_state (not self._state) as its source of
        truth, matching every other sCTk widget. An earlier version of this
        method read/wrote self._state instead, which nothing in this class
        actually updated -- the only code that did was ThemeableWidget.configure(),
        which is dead code (see themeable_widget.py's docstring) -- so get_state()
        always silently reported "normal" regardless of the widget's real state.

        Args:
            mode: If None, returns the current state without changing anything.
                Otherwise, only the literal string "disabled" (case-insensitive)
                is treated as disabled -- any other value, including typos, is
                silently treated as "normal". No exception is raised either way.

        Returns:
            The resulting state, always exactly "normal" or "disabled" (lowercase).
        """
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        self._custom_current_state = "disabled" if mode.lower() == "disabled" else "normal"
        super().configure(state=self._custom_current_state)
        self._apply_custom_theme_colors()
        return self._custom_current_state

    def get_state(self) -> str:
        """Equivalent to calling state() with no argument."""
        return self.state()

    def set(self, *args: Any, **kwargs: Any) -> None:
        """
        Selects a segment programmatically.

        Wraps the native CTkSegmentedButton.set(), then repaints, since
        selecting a segment changes which one needs the "selected" highlight --
        native set() alone doesn't trigger that repaint on its own.
        """
        super().set(*args, **kwargs)
        self._apply_custom_theme_colors()

    def _clicked(self, *args: Any, **kwargs: Any) -> None:
        """
        Internal click handler override.

        Wraps CTkSegmentedButton's own _clicked() (which updates the native
        selection) with a repaint, for the same reason set() needs one: the
        selected segment's color needs to change to reflect the new selection.
        """
        super()._clicked(*args, **kwargs)
        self._apply_custom_theme_colors()

    # Required at the TOP LEVEL of the theme block.
    #
    # selected_hover_color is deliberately NOT listed: it exists in the theme
    # file but is read by no code path at all -- dead data, the same situation
    # pointer_color was in for the dial family. Requiring it would demand a key
    # that does nothing. Either wire it up or remove it from the theme.
    _REQUIRED_THEME_KEYS = ("fg_color", "selected_color", "text_color",
                            "unselected_hover_color")

    # Required inside disabled_map. selected_text_color lives ONLY here -- there
    # is no top-level equivalent, since a selected segment's normal text colour
    # comes from text_color.
    _REQUIRED_DISABLED_KEYS = ("fg_color", "selected_color", "text_color",
                               "selected_text_color")

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

    def _apply_custom_theme_colors(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, based
        on the current enabled/disabled state and which segment (if any) is
        selected.

        Called: after construction (via the deferred self.after(15, ...) in
        __init__), on every state() change, on every set(), and on every click.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.
        Every value here traces back to sCTkThemes.json -- there are no
        hardcoded colors in this method; the tuples on each `.get(key, ...)`
        Every colour comes from the theme block, which is validated at
        construction -- there are no fallbacks to fall through to.
        """
        # Guards against being called before CTkSegmentedButton has built its
        # internal per-segment buttons (see the __init__ comment on the 15ms delay).
        if not hasattr(self, "_buttons_dict") or not self._buttons_dict:
            return

        is_disabled = str(getattr(self, "_custom_current_state", "normal")).lower() == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        # No `.get(key, fallback)` anywhere below. Those fallbacks were
        # unreachable given the current theme file -- every key they guarded
        # is present -- but that was a property of the THEME, not the code.
        # Delete a key from the block and the fallback would silently
        # activate, producing a plausible-looking wrong colour instead of the
        # KeyError every other widget now raises. _validate_theme_keys()
        # makes that failure loud.
        fg_tuple = tuple(target_map.get("fg_color"))
        # The theme JSON's disabled_map key is "selected_color", not
        # "disabled_selected_color" -- an earlier version of this line used the
        # wrong key name, so it silently always fell back to a hardcoded default
        # that was subtly wrong in dark mode. Confirm the key name matches
        # sCTkThemes.json's disabled_map block before changing this.
        d_selected = tuple(self._custom_disabled_map.get("selected_color"))
        n_selected = tuple(self._local_defaults.get("selected_color"))
        # NOTE: unselected_hover_color is popped out of final_kw in __init__
        # (it is not a native CTkSegmentedButton constructor argument), but
        # _local_defaults is copied BEFORE that pop, so it survives here.
        # Don't move the copy.
        unselected_hover = tuple(self._local_defaults.get("unselected_hover_color"))

        # unselected_color is deliberately NOT read from the theme file --
        # unselected segments always mirror fg_color, by design, so they blend
        # into the widget's own background rather than appearing individually
        # distinct or transparent. There is no independent "unselected_color"
        # theme key for this widget at all.
        fg_payload = {
            "fg_color": fg_tuple,
            "selected_color": d_selected if is_disabled else n_selected,
            "unselected_color": fg_tuple,
            "unselected_hover_color": fg_tuple if is_disabled else unselected_hover,
        }
        super().configure(**fg_payload)

        base_txt_tuple = tuple(target_map.get("text_color"))
        # Reads disabled_map.selected_text_color / disabled_map.text_color.
        # An earlier version of this hardcoded both colors directly, ignoring
        # the theme file entirely -- don't reintroduce literal hex values here.
        selected_disabled_txt = tuple(self._custom_disabled_map.get("selected_text_color"))
        unselected_disabled_txt = tuple(self._custom_disabled_map.get("text_color"))

        for val_name, button in self._buttons_dict.items():
            # Clear layout padding bounds flush to the container track edge.
            try:
                button.grid_configure(padx=0, pady=0)
            except Exception:
                pass

            if is_disabled:
                if hasattr(self, "_current_value") and val_name == self._current_value:
                    # The selected segment keeps a more prominent text color
                    # while disabled, so the user can still tell what was chosen
                    # even though the whole control is grayed out.
                    button.configure(text_color=selected_disabled_txt)
                else:
                    button.configure(text_color=unselected_disabled_txt)
            else:
                button.configure(text_color=base_txt_tuple)