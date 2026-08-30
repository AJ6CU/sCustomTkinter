#!/usr/bin/python3
"""
sCTkSlider

A theme-compliant linear adjustment slider widget. Inherits directly from
ctk.CTkSlider so CustomTkinter handles native mouse-drag handling, scaling,
and coordinate snapping; this class layers automatic light/dark theme
resolution and a distinct enabled/disabled visual state on top.

Base class order matters here: `class sCTkSlider(ctk.CTkSlider,
ThemeableWidget)` puts the native CTk class first, so every `super()` call in
this file's own methods resolves to ctk.CTkSlider -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring); this widget owns all of
its own runtime color-swapping logic.

Unlike every other widget in this project, state is NOT tracked in a parallel
self._custom_current_state attribute -- state() and _apply_custom_theme_colors()
both read the NATIVE widget's own "state" property directly via
super().cget("state"), treating it as the single source of truth rather than
duplicating it. Disabling routes "state" straight through to the native
widget's own configure(), which is the same underlying mechanism confirmed
correct elsewhere in this library (native state="disabled" blocks
interaction; manual event-unbinding does not).
"""
from typing import Any, Callable, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkSlider(ctk.CTkSlider, ThemeableWidget):
    """Themeable linear adjustment slider.

    Adds to native ctk.CTkSlider:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A distinct enabled/disabled visual state, read directly from the
        native widget's own state (see module docstring) rather than a
        parallel instance attribute.
      - Pygubu Designer property introspection for `state`, `fg_color`,
        `progress_color`, `button_color`, and `button_hover_color` via a
        single-argument configure() call.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox, sCTkSegmentedButton, and the button
    family. Not separately re-confirmed for this specific widget.
    """

    def __init__(self, master: Optional[Any] = None, **kw: Any) -> None:
        """
        Args:
            master: Parent container.
            **kw: `command` (callable) and `variable` (tkinter.Variable) are
                pulled out explicitly below. Everything else is either a
                native CTkSlider argument or a theme-key override (see the
                "sCTkSlider" block in sCTkThemes.json).
        """
        # 1. Capture widget-specific attributes early, before the mixin's own
        # configuration pass.
        command = kw.pop("command", None)
        variable = kw.pop("variable", None)

        # 2. Fire our shared theme logic. This resolves final_kw
        # (construction-time properties) and the disabled color map. See
        # ThemeableWidget.__init__ for what actually happens here.
        ThemeableWidget.__init__(self, kw)
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # Remove any stray "state" key from final_kw -- prevents native
        # constructor validation collisions.
        self.final_kw.pop("state", None)

        # 3. Initialize CustomTkinter natively with the clean final kwargs array.
        super().__init__(master, **self.final_kw)

        if command is not None: super().configure(command=command)
        if variable is not None: super().configure(variable=variable)

        # Deferred slightly, matching this file's original startup pattern --
        # applies the initial theme colors shortly after construction.
        self.after(10, self._apply_custom_theme_colors)
        self._finalize_themeable_lifecycle()

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally below.
                - the literal string "state": returns a Tkinter-style
                  (name, name, name, default, current) tuple.
                - one of "fg_color"/"progress_color"/"button_color"/
                  "button_hover_color": returns the same style of tuple, with
                  `current` reflecting the disabled or normal value as
                  appropriate. Note the returned value is str(value), where
                  value may itself be a (light, dark) tuple rather than a
                  single resolved color -- a known limitation shared with the
                  wider Pygubu-query investigation set aside elsewhere in this
                  project, not fixed here.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties (same limitation).
            **kwargs: Standard CTkSlider configuration options, plus:
                `command`/`variable` are routed through super().configure()
                individually. Note `state` is NOT specially intercepted here
                -- it flows straight through to the native widget's own
                configure(state=...), which is what makes this widget's
                disable mechanism correct (see module docstring).

        Returns:
            The query tuple described above for the single-argument case, or
            whatever super().configure() returns for the keyword-argument case
            (typically None).
        """
        # args[0] was already correctly unwrapped here in the original file --
        # unlike most other widgets in this library, this one never had the
        # `pname = args` tuple-comparison bug. Preserved as-is.
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname == "state":
                    return ("state", "state", "state", "normal", str(self.state()))

                if pname in ["fg_color", "progress_color", "button_color", "button_hover_color"]:
                    current_state = str(self.state()).lower()
                    val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                    return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

                return super().configure(pname)

        if "command" in kwargs: super().configure(command=kwargs.pop("command"))
        if "variable" in kwargs: super().configure(variable=kwargs.pop("variable"))

        # "state" is deliberately left in kwargs here, not popped -- it flows
        # through to super().configure(**kwargs) below, reaching the native
        # widget directly. has_state only tracks whether a repaint is needed
        # afterward.
        has_state = "state" in kwargs
        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)

        if kwargs:
            super().configure(**kwargs)

        if has_state:
            self._apply_custom_theme_colors()

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. Without this line, calling .config(...) on an instance
    # would silently skip this entire override and land on the native widget's
    # configure() directly, bypassing theming entirely.
    config = configure

    def _set_appearance_mode(self, mode_string: str) -> None:
        """
        Forwards CustomTkinter's internal light/dark mode change notification to
        the native widget.

        No longer manually re-triggers _apply_custom_theme_colors(). That
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
            try: super()._set_appearance_mode(mode_string)
            except Exception: pass

    def state(self, mode: Optional[str] = None) -> str:
        """
        Gets or sets the widget's enabled/disabled state.

        Unlike every other widget in this library, this reads the query
        directly from the native widget's own cget("state") rather than a
        parallel self._custom_current_state -- see module docstring.

        Args:
            mode: If None, returns the native widget's current "state" value
                directly. Otherwise, forwarded to configure(state=mode),
                which reaches the native widget's own state handling.

        Returns:
            If querying: whatever the native widget's "state" cget returns,
            lowercased. If setting: echoes back the `mode` argument exactly as
            given (not re-queried from the native widget afterward).
        """
        if mode is None:
            return str(super().cget("state")).lower()
        self.configure(state=mode)
        return mode

    def get_state(self) -> str:
        """Equivalent to calling state() with no argument."""
        return self.state()

    def _apply_custom_theme_colors(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, based
        on the current state (read directly from the native widget -- see
        module docstring).

        Called shortly after construction (via after(10, ...)), on every
        state()/configure(state=...) change, and (indirectly, via
        _set_appearance_mode) on appearance-mode changes.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.
        Every value here traces back to sCTkThemes.json; there are no
        hardcoded colors in this method.

        While disabled, button_hover_color is forced to match button_color --
        since hover can't trigger once natively disabled, this just ensures
        nothing else could show a stale hover color if queried directly.
        """
        is_disabled = str(super().cget("state")).lower() == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        fg_payload = {}
        for key in ("fg_color", "progress_color", "button_color", "button_hover_color"):
            val = target_map.get(key)
            if val is not None:
                fg_payload[key] = val

        if is_disabled and "button_color" in fg_payload:
            fg_payload["button_hover_color"] = fg_payload["button_color"]

        if fg_payload:
            super().configure(**fg_payload)
