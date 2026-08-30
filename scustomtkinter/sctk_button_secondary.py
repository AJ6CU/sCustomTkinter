#!/usr/bin/python3
"""
sCTkButtonSecondary

A theme-compliant secondary action button widget -- a lower-emphasis sibling
of sCTkButtonPrimary (see also sCTkButtonTertiary). Inherits directly from
ctk.CTkButton so CustomTkinter handles native rendering; this class layers
automatic light/dark theme resolution and a three-state visual model
(normal/disabled/pressed) on top. Unlike sCTkButtonPrimary, there is no
"alarm" state here.

Base class order matters here: `class sCTkButtonSecondary(ctk.CTkButton,
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


class sCTkButtonSecondary(ctk.CTkButton, ThemeableWidget):
    """Themeable secondary action button.

    Adds to native ctk.CTkButton:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A three-state visual model: normal, disabled, and pressed. Precedence
        when both could apply is disabled > pressed (see
        _update_current_visual_state() and the guard clause in set_pressed()).
      - Pygubu Designer property introspection for a handful of properties via
        a single-argument configure() call.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox, sCTkSegmentedButton, and sCTkButtonPrimary.

    Disabling uses CTk's native state="disabled" rather than manually unbinding
    mouse events -- an earlier version of this widget used the manual-unbind
    approach (identical code to what sCTkButtonPrimary originally had), which
    was directly tested and confirmed NOT to block clicks on that widget. The
    fix is carried over here on the strength of both widgets sharing the same
    underlying ctk.CTkButton click-handling; a confirmatory test on this
    specific widget is still worthwhile.
    """

    def __init__(self, master: Optional[Any] = None, **kw: Any) -> None:
        """
        Args:
            master: Parent container.
            **kw: Any native CTkButton argument, or a theme-key override (see
                the "sCTkButtonSecondary" block in sCTkThemes.json, including
                its disabled_map and pressed_map sub-blocks).
        """
        # 1. Fire our shared theme logic first. This resolves final_kw
        # (construction-time properties) and the disabled/pressed color maps.
        # See ThemeableWidget.__init__ for what actually happens here.
        ThemeableWidget.__init__(self, kw)

        # 2. Deep-copy each resolved map onto this instance, so later changes
        # here never leak back into the shared theme registry.
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)
        self._custom_pressed_map = dict(self._widget_pressed_map)

        # 3. Initialize CustomTkinter natively with the clean final kwargs array.
        super().__init__(master, **self.final_kw)

        self.is_pressed = False
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
                  whichever of disabled/pressed/normal is currently active.
                  Note the returned value is str(value), where value may
                  itself be a (light, dark) tuple rather than a single
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
        approach validated on sCTkComboBox, sCTkSegmentedButton, and
        sCTkButtonPrimary.

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
            # Deferred via after_idle rather than called immediately: on
            # sCTkButtonPrimary, CTk's own state="normal" transition was found
            # to schedule its own internal repaint that can run AFTER an
            # immediate call here and silently overwrite fresh colors back to
            # something stale. Queuing our reapply via after_idle lets CTk's
            # own pending repaint settle first, so ours wins the final paint.
            self.after_idle(self._update_current_visual_state)

        elif mode == "disabled":
            self._custom_current_state = "disabled"
            # Uses CTk's native state="disabled" -- confirmed necessary (not
            # optional) on sCTkButtonPrimary, which originally used the same
            # manual-unbind code this method used to have. That approach was
            # confirmed broken: clicks still fired the button's command while
            # "disabled", almost certainly because CTkButton binds its click
            # handler at the canvas-ITEM level (tag_bind on the drawn
            # rectangle/text), not the canvas-WIDGET level -- so
            # canvas.unbind() never reached it. Don't reintroduce manual event
            # unbinding here.
            super().configure(state="disabled", hover=False)
            self.after_idle(self._update_current_visual_state)

        return self._custom_current_state

    def set_pressed(self, pressed: bool) -> None:
        """
        Toggles the visual "pressed" state.

        No-op while disabled.

        Args:
            pressed: True to show the pressed-state colors, False to return to
                normal (assuming not disabled).
        """
        if getattr(self, "_custom_current_state", "normal") == "disabled":
            return
        self.is_pressed = pressed
        self._update_current_visual_state()

    def _update_current_visual_state(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, based
        on the current state. Precedence: disabled > pressed > normal -- only
        the first matching branch applies.

        Called after construction, on every state()/set_pressed() change, and
        (indirectly, via after_idle) after every state() transition.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.
        Every value here traces back to sCTkThemes.json; there are no
        hardcoded colors in this method.

        Only the normal (final else) branch also reapplies border_width,
        corner_radius, and font -- these don't vary between
        disabled/pressed/normal, so there's no need to repeat them in every
        branch; they're set once here and otherwise left alone.
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

        if self.is_pressed:
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
