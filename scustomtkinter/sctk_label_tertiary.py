#!/usr/bin/python3
"""
sCTkLabelTertiary

A theme-compliant, low-emphasis inline description label widget -- the
lowest-emphasis of the library's three label tiers (see also sCTkLabelPrimary,
sCTkLabelSecondary). Inherits directly from ctk.CTkLabel so CustomTkinter
handles native rendering; this class layers automatic light/dark theme
resolution and a distinct enabled/disabled visual state on top.

Base class order matters here: `class sCTkLabelTertiary(ctk.CTkLabel,
ThemeableWidget)` puts the native CTk class first, so every `super()` call in
this file's own methods resolves to ctk.CTkLabel -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring); this widget owns all of
its own runtime color-swapping logic.

Unlike the button/checkbox family, "disabled" here is purely visual (dimmed
text color) -- CTkLabel has no native click handling to block in the first
place.

Internal state attribute is named self._custom_current_state, matching the
convention used across the rest of the library -- an earlier version of this
file used self._current_state instead, inconsistent both within the label
family (sCTkLabelSecondary already used _custom_current_state) and against
every other themed widget. Purely an internal rename; doesn't affect the
public state()/get_state() API.
"""
from typing import Any, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkLabelTertiary(ctk.CTkLabel, ThemeableWidget):
    """Themeable, low-emphasis inline description label.

    Adds to native ctk.CTkLabel:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A distinct enabled/disabled visual state -- purely a text-color dim,
        since labels have no native interactivity to block.
      - Pygubu Designer property introspection for `state`, `fg_color`, and
        `text_color` via a single-argument configure() call, plus a cget()
        override so querying "state" doesn't raise (native CTkLabel has no
        real "state" option to cget in the first place).

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
            **kwargs: `state` is pulled out explicitly below (applied after
                construction, via self.configure(), rather than passed to the
                native constructor). Everything else is either a native
                CTkLabel argument (e.g. `text`, `font`) or a theme-key override
                (see the "sCTkLabelTertiary" block in sCTkThemes.json).
        """
        # 1. Capture the initial state before ThemeableWidget's own kwargs pass,
        # so it doesn't get merged into final_kw and sent to the native
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
        self.configure(state=state_init)

        # 6. Register lifecycle handshake hook, notifying Pygubu-style consumers
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
                - "fg_color" or "text_color": returns the same style of tuple,
                  with `current` reflecting the disabled or normal value as
                  appropriate. Note the returned value is str(value), where
                  value may itself be a (light, dark) tuple rather than a
                  single resolved color -- a known limitation shared with the
                  wider Pygubu-query investigation set aside elsewhere in this
                  project, not fixed here.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties (same limitation).
            **kwargs: Standard CTkLabel configuration options, plus: passing
                `state=...` routes through self.state() rather than being
                forwarded as-is.

        Returns:
            The query tuple described above for the single-argument case, or
            whatever super().configure() returns for the keyword-argument case
            (typically None).
        """
        # args is always a tuple -- args[0] is the actual value passed, whether
        # that's a string or a dict. An earlier version of this method compared
        # the wrapped tuple directly (`pname = args`), so the query branches
        # below never matched anything. Don't reintroduce that.
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname == "state":
                    return ("state", "state", "state", "normal", str(self.state()))

                if pname in ["fg_color", "text_color"]:
                    current_state = str(self.state()).lower()
                    val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                    return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

                return super().configure(pname)

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        if kwargs:
            return super().configure(**kwargs)
        return None

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. Without this line, calling .config(...) on an instance
    # would silently skip this entire override and land on the native widget's
    # configure() directly, bypassing theming and state handling entirely.
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
            otherwise whatever the native CTkLabel.cget() returns.
        """
        if str(attribute_name).lower() == "state":
            return self.state()
        return super().cget(attribute_name)

    def get_state(self) -> str:
        """Equivalent to calling state() with no argument."""
        return self.state()

    def state(self, mode: Optional[str] = None) -> str:
        """
        Gets or sets the widget's enabled/disabled visual state.

        Args:
            mode: If None, returns the current state without changing anything.
                Otherwise, only the literal string "disabled" (case-insensitive)
                is treated as disabled; anything in ("normal", "enabled",
                "active") is treated as enabled. Any other value matches
                neither branch and leaves the state unchanged.

        Returns:
            The resulting state ("normal" or "disabled", lowercase).
        """
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
            self._update_current_visual_state()
        elif mode == "disabled":
            self._custom_current_state = "disabled"
            self._update_current_visual_state()

        return self._custom_current_state

    def _update_current_visual_state(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, based
        on the current state.

        Called after construction and on every state() change.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.

        text_color is required to be present in whichever map is active (the
        top-level block for normal state, disabled_map for disabled) -- if
        it's missing, this raises immediately rather than silently falling
        back to a default or silently omitting the property. An earlier
        version fell back to CTk's own global ThemeManager default; per this
        project's design, ThemeableWidget-based widgets are meant to fail hard
        on incomplete theme data, not paper over it.
        """
        is_disabled = self._custom_current_state == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        if target_map.get("text_color") is None:
            raise KeyError(
                f"'{self.__class__.__name__}' theme block is missing 'text_color' in its "
                f"{'disabled_map' if is_disabled else 'top-level'} section of sCTkThemes.json."
            )

        config_payload = {}
        for key in ("fg_color", "text_color", "font"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = val

        super().configure(**config_payload)
