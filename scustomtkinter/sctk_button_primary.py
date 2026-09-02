#!/usr/bin/python3
"""
sCTkButtonPrimary

A theme-compliant, high-visibility "primary action" button widget -- the most
prominent of the library's three button tiers (see sCTkButtonSecondary,
sCTkButtonTertiary). Inherits directly from ctk.CTkButton so CustomTkinter
handles native rendering; this class layers automatic light/dark theme
resolution and a four-state visual model (normal/disabled/pressed/alarm) on top.

Base class order matters here: `class sCTkButtonPrimary(ctk.CTkButton,
ThemeableWidget)` puts the native CTk class first, so every `super()` call in
this file's own methods resolves to ctk.CTkButton -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring); this widget owns all of
its own runtime color-swapping logic.
"""
from typing import Any, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkButtonPrimary(ctk.CTkButton, ThemeableWidget):
    """Themeable, high-visibility primary action button.

    Adds to native ctk.CTkButton:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A four-state visual model, not just enabled/disabled: normal, disabled,
        pressed, and alarm. Precedence when more than one could apply is
        disabled > alarm > pressed > normal (see _update_current_visual_state()
        and the guard clauses in set_pressed()/set_alarm_state()).
      - Pygubu Designer property introspection for a handful of properties via
        a single-argument configure() call.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox and sCTkSegmentedButton.

    Disabling uses CTk's native state="disabled" rather than manually unbinding
    mouse events -- confirmed by direct testing to be the only mechanism that
    actually blocks clicks (see state() for why). The post-transition color
    reapply is deferred via after_idle rather than called immediately, since an
    immediate call was found to lose a race against CTk's own internal
    state-change repaint, leaving buttons visually stuck on the wrong palette
    after repeated disable/enable cycles.
    """

    def __init__(self, master: Optional[Any] = None, **kw: Any) -> None:
        """
        Args:
            master: Parent container.
            **kw: Any native CTkButton argument, or a theme-key override (see
                the "sCTkButtonPrimary" block in sCTkThemes.json, including its
                disabled_map, pressed_map, and alarm_map sub-blocks).
        """
        # 1. Fire our shared theme logic first. This resolves final_kw
        # (construction-time properties) and the disabled/pressed/alarm color
        # maps. See ThemeableWidget.__init__ for what actually happens here.
        ThemeableWidget.__init__(self, kw)

        # 2. Deep-copy each resolved map onto this instance, so later changes
        # here never leak back into the shared theme registry.
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)
        self._custom_pressed_map = dict(self._widget_pressed_map)
        self._custom_alarm_map = dict(self._widget_alarm_map)

        # 3. Initialize CustomTkinter natively with the clean final kwargs array.
        super().__init__(master, **self.final_kw)

        self.is_pressed = False
        self.is_alarm = False
        self._custom_current_state = "normal"
        self._update_current_visual_state()

        # 4. Register lifecycle handshake hook, notifying Pygubu-style consumers
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
                - one of "fg_color"/"border_color"/"text_color"/"hover_color":
                  returns the same style of tuple, with `current` reflecting
                  whichever of disabled/alarm/pressed/normal is currently
                  active. Note the returned value is str(value), where value
                  may itself be a (light, dark) tuple rather than a single
                  resolved color -- a known limitation shared with the wider
                  Pygubu-query investigation set aside elsewhere in this
                  project, not fixed here.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties (same limitation).
            **kwargs: Standard CTkButton configuration options, plus: passing
                `state=...` routes through self.state() rather than being
                forwarded as-is.

        Returns:
            The query tuple described above for the single-argument case, or
            whatever super().configure() returns for the keyword-argument case
            (typically None).
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

                if pname in ["fg_color", "border_color", "text_color", "hover_color"]:
                    current_state = str(self.state()).lower()
                    if current_state == "disabled" and self._custom_disabled_map:
                        val = self._custom_disabled_map.get(pname)
                    elif getattr(self, "is_alarm", False) and self._custom_alarm_map:
                        val = self._custom_alarm_map.get(pname)
                    elif getattr(self, "is_pressed", False) and self._custom_pressed_map:
                        val = self._custom_pressed_map.get(pname)
                    else:
                        val = self._local_defaults.get(pname)
                    return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

                return super().configure(pname)

        if "state" in kwargs:
            target_state = kwargs.pop("state")
            self.state(target_state)

        if kwargs:
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

    def _set_appearance_mode(self, mode_string: str) -> None:
        """
        Forwards CustomTkinter's internal light/dark mode change notification to
        the native widget.

        No longer manually re-triggers _update_current_visual_state(). That
        method now passes raw (light, dark) tuples straight through to
        configure() instead of pre-resolving to a single color, so CTk's own
        appearance-mode tracking should repaint correctly on its own -- the same
        approach validated on sCTkComboBox and sCTkSegmentedButton. If colors
        ever stop following mode changes (especially while disabled, pressed,
        or in alarm), that's the signal this doesn't hold here and the manual
        re-trigger needs to come back.

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
        Gets or sets the widget's enabled/disabled state.

        Args:
            mode: If None, returns the current state without changing anything.
                Otherwise, only the literal string "disabled" (case-insensitive)
                is treated as disabled; anything in ("normal", "enabled",
                "active") is treated as enabled. Any other value falls through
                without matching either branch, leaving the state unchanged.

        Returns:
            The resulting state ("normal" or "disabled", lowercase).
        """
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
            super().configure(state="normal", hover=True)
            # Re-establish the mouse bindings that disabling below may have
            # torn down.
            if hasattr(self, "_create_bindings"):
                try: self._create_bindings()
                except Exception: pass
            # Deferred via after_idle rather than called immediately: CTk's own
            # state="normal" transition appears to schedule its own internal
            # repaint, which can run AFTER an immediate call here and silently
            # overwrite our colors back to something stale (observed directly:
            # buttons stayed visually "disabled" after re-enabling). Queuing
            # our reapply via after_idle lets CTk's own pending repaint settle
            # first, so ours is the one that actually wins the final paint.
            self.after_idle(self._update_current_visual_state)

        elif mode == "disabled":
            self._custom_current_state = "disabled"
            # Uses CTk's native state="disabled" -- confirmed by direct testing
            # to be necessary, not optional. An earlier version instead
            # manually unbound mouse events on the canvas while keeping native
            # state at "normal", to avoid CTk's own disabled rendering
            # potentially fighting with this widget's disabled/pressed/alarm
            # color system. That approach was confirmed broken: clicks still
            # fired the button's command while "disabled", almost certainly
            # because CTkButton binds its click handler at the canvas-ITEM
            # level (tag_bind on the drawn rectangle/text), not the
            # canvas-WIDGET level -- so canvas.unbind() never reached it.
            # Native state="disabled" is what actually blocks interaction;
            # don't replace this with manual event unbinding again.
            super().configure(state="disabled", hover=False)
            self.after_idle(self._update_current_visual_state)

        return self._custom_current_state

    def set_pressed(self, pressed: bool) -> None:
        """
        Toggles the visual "pressed" state.

        No-op while disabled or in alarm state -- see the precedence order
        documented on _update_current_visual_state().

        Args:
            pressed: True to show the pressed-state colors, False to return to
                normal (assuming not disabled or in alarm).
        """
        if getattr(self, "_custom_current_state", "normal") == "disabled" or self.is_alarm:
            return
        self.is_pressed = pressed
        self._update_current_visual_state()

    def set_alarm_state(self, active: bool) -> None:
        """
        Forces the button into (or out of) a high-visibility alarm/warning state.

        No-op while disabled. Activating alarm state clears any current
        "pressed" state, since alarm takes visual precedence over pressed (see
        _update_current_visual_state()).

        Args:
            active: True to enter alarm state, False to leave it.
        """
        if getattr(self, "_custom_current_state", "normal") == "disabled":
            return
        self.is_alarm = active
        if self.is_alarm:
            self.is_pressed = False
        self._update_current_visual_state()

    def _update_current_visual_state(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, based
        on the current state. Precedence, checked in this order: disabled >
        alarm > pressed > normal -- only the first matching branch applies.

        Called after construction, on every state()/set_pressed()/
        set_alarm_state() change, and (indirectly) on appearance-mode changes
        via _set_appearance_mode().

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.
        Every value here traces back to sCTkThemes.json; there are no
        hardcoded colors in this method.

        Only the normal (final else) branch also reapplies border_width,
        corner_radius, and font -- these don't vary between
        disabled/alarm/pressed/normal, so there's no need to repeat them in
        every branch; they're set once here and otherwise left alone.
        `border_color` is checked in every branch for consistency with the
        other themed widgets, but sCTkButtonPrimary's theme block doesn't
        currently define one at all -- this button style has no themed border
        by design, so that lookup always resolves to None and is skipped.
        """
        if getattr(self, "_custom_current_state", "normal") == "disabled":
            config_payload = {}
            for key in ("fg_color", "hover_color", "border_color", "text_color"):
                val = self._custom_disabled_map.get(key)
                if val is not None:
                    config_payload[key] = val
            if config_payload:
                super().configure(**config_payload)
            return

        if self.is_alarm:
            config_payload = {}
            for key in ("fg_color", "hover_color", "border_color", "text_color"):
                val = self._custom_alarm_map.get(key)
                if val is not None:
                    config_payload[key] = val
            config_payload["hover"] = False
            super().configure(**config_payload)

        elif self.is_pressed:
            config_payload = {}
            for key in ("fg_color", "hover_color", "border_color", "text_color"):
                val = self._custom_pressed_map.get(key)
                if val is not None:
                    config_payload[key] = val
            config_payload["hover"] = False
            super().configure(**config_payload)

        else:
            config_payload = {}
            for key in ("fg_color", "hover_color", "border_color", "text_color", "border_width", "corner_radius", "font"):
                val = self._local_defaults.get(key)
                if val is not None:
                    config_payload[key] = val
            config_payload["hover"] = True
            if config_payload:
                super().configure(**config_payload)