#!/usr/bin/python3
"""
sCTkProgressBar

A theme-compliant progress indicator bar widget. Inherits directly from
ctk.CTkProgressBar so CustomTkinter handles native rendering; this class
layers automatic light/dark theme resolution and a distinct "disabled" visual
state on top.

Base class order matters here: `class sCTkProgressBar(ctk.CTkProgressBar,
ThemeableWidget)` puts the native CTk class first, so every `super()` call in
this file's own methods resolves to ctk.CTkProgressBar -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring); this widget owns all of
its own runtime color-swapping logic.

Progress bars have no native interactivity to block (no click handling at
all), so "disabled" here is purely a visual "looks inactive" state -- it never
touches CTk's native state machinery, unlike interactive widgets.
"""
import os
from typing import Any, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkProgressBar(ctk.CTkProgressBar, ThemeableWidget):
    """Themeable progress bar.

    Adds to native ctk.CTkProgressBar:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A purely visual "disabled" state, tracked in self._custom_current_state.
        Since progress bars have no click behavior to block, this only swaps
        colors -- it never calls the native configure(state=...).
      - Pygubu Designer property introspection for `state`, `fg_color`,
        `progress_color`, and `border_color` via a single-argument configure()
        call, plus a cget() override so querying "state" doesn't raise (native
        CTkProgressBar has no real "state" option to cget in the first place).
      - A bind() override that no-ops while running inside Pygubu Designer
        (detected via the PYGUBU_DESIGNER_RUNNING environment variable) --
        the same pattern used by sCTkRadioButton, presumably to avoid event
        bindings misbehaving during design-time layout.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox, sCTkSegmentedButton, and the button
    family. Not separately re-confirmed for this specific widget.

    There's no `border_color` anywhere in this widget's theme block (not even
    at the top level), even though the repaint loop checks for one. This
    style simply has no themed border; the lookup always resolves to nothing
    and is skipped, the same situation as sCTkButtonPrimary's border_color.
    """

    def __init__(self, master: Optional[Any] = None, **kwargs: Any) -> None:
        """
        Args:
            master: Parent container.
            **kwargs: `state` is pulled out explicitly below (applied after
                construction, via self.state(), rather than passed to the
                native constructor). Everything else is either a native
                CTkProgressBar argument or a theme-key override (see the
                "sCTkProgressBar" block in sCTkThemes.json).
        """
        # 1. Capture the initial state before ThemeableWidget's own kwargs
        # pass, so it doesn't get merged into final_kw and sent to the native
        # constructor.
        state_init = kwargs.pop("state", "normal")

        # 2. Fire our shared theme logic. This resolves final_kw
        # (construction-time properties) and the disabled color map. See
        # ThemeableWidget.__init__ for what actually happens here.
        ThemeableWidget.__init__(self, kwargs)

        # 3. Deep-copy the resolved map onto this instance, so later changes
        # here never leak back into the shared theme registry.
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # Remove any stray "state" key from final_kw -- already extracted
        # above, but guards against it being reintroduced by a theme override.
        self.final_kw.pop("state", None)

        # 4. Initialize CustomTkinter natively with the clean final kwargs array.
        super().__init__(master, **self.final_kw)

        # 5. Apply the requested initial state now that the native widget exists.
        self._custom_current_state = "normal"
        self.state(state_init)

        # 6. Register lifecycle handshake hook, notifying Pygubu-style consumers
        # that construction is complete.
        self._finalize_themeable_lifecycle()

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally below.
                - the literal string "state": returns a Tkinter-style
                  (name, name, name, default, current) tuple.
                - one of "fg_color"/"progress_color"/"border_color": returns
                  the same style of tuple, with `current` reflecting the
                  disabled or normal value as appropriate. Note the returned
                  value is str(value), where value may itself be a
                  (light, dark) tuple rather than a single resolved color --
                  a known limitation shared with the wider Pygubu-query
                  investigation set aside elsewhere in this project, not
                  fixed here.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties (same limitation).
            **kwargs: Standard CTkProgressBar configuration options, plus:
                passing `state=...` routes through self.state() rather than
                being forwarded as-is.

        Returns:
            The query tuple described above for the single-argument case, or
            None for the keyword-argument case.
        """
        # args is always a tuple -- args[0] is the actual value passed, whether
        # that's a string or a dict. An earlier version of this method compared
        # the wrapped tuple directly (`pname = args`); its fallback used *args
        # unpacking so it didn't crash, but the query branches below never
        # matched anything. Don't reintroduce the tuple comparison.
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname == "state":
                    return ("state", "state", "state", "normal", str(self.state()))

                if pname in ["fg_color", "progress_color", "border_color"]:
                    current_state = str(self.state()).lower()
                    val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                    return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

                return super().configure(pname)

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        if kwargs:
            super().configure(**kwargs)
            self._update_current_visual_state()

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. An earlier version of this file was MISSING this line
    # entirely: calling .config(...) on an instance silently skipped this
    # entire override and landed on the native widget's configure() directly,
    # bypassing theming and state handling completely -- confirmed as a
    # critical bug on sCTkSegmentedButton earlier in this project's audit; the
    # same fix applies here.
    config = configure

    def cget(self, attribute_name: str) -> Any:
        """
        Intercepts "state" queries so they route through state() instead of
        being forwarded to the native widget, which has no real "state" option
        to cget in the first place and would otherwise raise.

        Args:
            attribute_name: The property name being queried.

        Returns:
            self.state() if attribute_name is "state" (case-insensitive),
            otherwise whatever the native CTkProgressBar.cget() returns.
        """
        if str(attribute_name).lower() == "state":
            return self.state()
        return super().cget(attribute_name)

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

    def get_state(self) -> str:
        """Equivalent to calling state() with no argument."""
        return self.state()

    def state(self, mode: Optional[str] = None) -> str:
        """
        Gets or sets the widget's visual "disabled" state.

        Unlike most widgets in this library, any string is accepted and
        stored verbatim (lowercased) -- there's no validation against a fixed
        set of recognized values, since progress bars don't have a real
        native "state" concept to validate against in the first place. Only
        the literal value "disabled" actually changes the rendered colors;
        anything else is treated as "not disabled" by _update_current_visual_state().

        Args:
            mode: If None, returns the current state without changing anything.
                Otherwise, stored directly (lowercased) as the new state.

        Returns:
            The resulting state string (lowercase).
        """
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        target_state = mode.lower()
        self._custom_current_state = target_state
        self._update_current_visual_state()
        return self._custom_current_state

    def _update_current_visual_state(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, based
        on the current state.

        Called after construction, on every state() change, and after any
        keyword configure() call.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.
        Every value here traces back to sCTkThemes.json; there are no
        hardcoded colors in this method.
        """
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "progress_color", "border_color", "border_width", "corner_radius"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = val

        if config_payload:
            super().configure(**config_payload)

    def bind(self, sequence=None, command=None, add=None):
        """
        No-ops while running inside Pygubu Designer (detected via the
        PYGUBU_DESIGNER_RUNNING environment variable), otherwise forwards to
        the native widget's bind(). Presumably guards against event bindings
        misbehaving during design-time layout, since progress bars have no
        real interactive purpose for the Designer to preview anyway.
        """
        if "PYGUBU_DESIGNER_RUNNING" in os.environ:
            return None
        return super().bind(sequence, command, add)
