#!/usr/bin/python3
"""
sCTkRadioButton

A theme-compliant radio selection button widget. Inherits directly from
ctk.CTkRadioButton so CustomTkinter handles native rendering, mutual
exclusion via shared variables, and click behavior; this class layers
automatic light/dark theme resolution and a distinct enabled/disabled visual
state on top.

Base class order matters here: `class sCTkRadioButton(ctk.CTkRadioButton,
ThemeableWidget)` puts the native CTk class first, so every `super()` call in
this file's own methods resolves to ctk.CTkRadioButton -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring); this widget owns all of
its own runtime color-swapping logic.

Disabling uses CTk's native state="disabled" -- an earlier version used the
same manual-unbind approach confirmed broken on the button family (clicks
still fired while "disabled" there), and additionally called
super().configure(state="normal") even while disabling, never actually
setting native state to "disabled" at all. Fixed to match the button family's
confirmed-correct approach; not independently re-tested on this specific
widget.

UNVERIFIED RISK, worth testing: configure(variable=...) and configure(value=...)
after construction bypass the native widget's own configure() entirely and
write directly to CTkRadioButton's private _variable/_value attributes
instead (see configure()'s "CRASH SHIELD PASS" comment, preserved from the
original). This was apparently done to work around a ValueError that calling
super().configure(variable=...) raised directly -- but writing to a private
attribute directly may not correctly re-establish whatever internal trace/
callback binding the native widget uses to react to variable changes.
Re-binding a RadioButton to a new variable or value after construction has
not been independently tested as part of this project's audit.
"""
import os
from typing import Any, Callable, Optional
import tkinter as tk
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkRadioButton(ctk.CTkRadioButton, ThemeableWidget):
    """Themeable radio selection button.

    Adds to native ctk.CTkRadioButton:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A distinct enabled/disabled visual state, using CTk's native
        state="disabled" (see module docstring for the fix history).
      - Pygubu Designer property introspection for `state`, `fg_color`,
        `border_color`, `text_color`, and `hover_color` via a single-argument
        configure() call.
      - A bind() override that no-ops while running inside Pygubu Designer
        (detected via the PYGUBU_DESIGNER_RUNNING environment variable) --
        the same pattern used by sCTkProgressBar.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox, sCTkSegmentedButton, and the button
    family. Not separately re-confirmed for this specific widget.

    The theme's border_width_unchecked and border_width_checked control this
    widget's border thickness based on whether it's the currently-selected
    button in its group (thicker when checked, to show the filled dot) --
    these are real, top-level-only theme keys (not in disabled_map), applied
    once at construction via final_kw and left alone afterward, the same way
    font or corner_radius are elsewhere in this library. The native widget
    handles switching between checked/unchecked appearance internally; no
    repaint-time logic is needed for these two keys. The repaint loop below
    no longer checks for "border_width", "radiobutton_width", or
    "radiobutton_height" -- an earlier version did, but none of those three
    correspond to anything in the real theme file; they were removed rather
    than renamed, since border_width_unchecked/checked don't need to be
    re-applied on disable/enable in the first place.
    """

    # EXPERIMENTAL TOGGLE -- see configure() for what this changes.
    # False (default): preserves the original behavior -- variable/value are
    #   written directly to CTkRadioButton's private _variable/_value
    #   attributes, bypassing super().configure() entirely.
    # True: routes variable/value through super().configure() the "proper"
    #   way instead. Untested as of this writing -- flip this to True locally
    #   to find out whether it actually raises the ValueError the original
    #   comment implied, and if not, whether rebinding to a new variable
    #   after construction then works correctly (does the button join the
    #   new group's mutual exclusion, does clicking it update the new
    #   variable, does it correctly reflect the new variable's current value).
    _REBIND_VIA_NATIVE_CONFIGURE = True

    def __init__(self, master: Optional[Any] = None, **kw: Any) -> None:
        """
        Args:
            master: Parent container.
            **kw: `variable` (tkinter.Variable), `value` (any), and `command`
                (callable) are read (not popped -- see below) and explicitly
                re-applied to final_kw before construction. Everything else is
                either a native CTkRadioButton argument or a theme-key
                override (see the "sCTkRadioButton" block in sCTkThemes.json).
        """
        # 1. Capture references to pass to the native constructor. Uses .get()
        # rather than .pop() -- these keys are read here AND still present in
        # kw when it's passed to ThemeableWidget.__init__ below, which will
        # also copy them into final_kw as ordinary (non-color) values. The
        # explicit re-assignment in step 3 is what guarantees they survive
        # regardless of whether ThemeableWidget's own merge logic keeps them.
        variable = kw.get("variable", None)
        value = kw.get("value", None)
        command = kw.get("command", None)

        # 2. Fire our shared theme logic. This resolves final_kw
        # (construction-time properties) and the disabled color map. See
        # ThemeableWidget.__init__ for what actually happens here.
        ThemeableWidget.__init__(self, kw)

        # 3. Deep-copy the resolved map onto this instance, so later changes
        # here never leak back into the shared theme registry.
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # Remove any stray "state" key from final_kw -- prevents native
        # constructor validation collisions.
        self.final_kw.pop("state", None)

        # Explicitly ensure these survive into the native constructor call,
        # regardless of how ThemeableWidget's merge handled them.
        if variable is not None: self.final_kw["variable"] = variable
        if value is not None: self.final_kw["value"] = value
        if command is not None: self.final_kw["command"] = command

        # 4. Initialize CustomTkinter natively, letting it wire up its own
        # StringVar/mutual-exclusion tracking bindings.
        super().__init__(master, **self.final_kw)

        self._custom_current_state = "normal"
        self._update_current_visual_state()

        # 5. Register lifecycle handshake hook, notifying Pygubu-style consumers
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
                  the disabled or normal value as appropriate. Note the
                  returned value is str(value), where value may itself be a
                  (light, dark) tuple rather than a single resolved color --
                  a known limitation shared with the wider Pygubu-query
                  investigation set aside elsewhere in this project, not
                  fixed here.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties (same limitation).
            **kwargs: Standard CTkRadioButton configuration options, plus:
                `variable`/`value` are written directly to this widget's
                private native attributes rather than routed through
                super().configure() -- see the module docstring's unverified-
                risk note before relying on re-binding these after
                construction; `command` and `state` are each routed
                individually.

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
                    val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                    return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

                return super().configure(pname)

        # EXPERIMENTAL TOGGLE -- see class docstring / _REBIND_VIA_NATIVE_CONFIGURE.
        # Default (False) preserves the original private-attribute approach.
        # An earlier version of this comment called this a "CRASH SHIELD
        # PASS... to prevent ValueError loops", implying super().configure(
        # variable=...) raised directly. Not yet independently confirmed --
        # see the toggle below to test both.
        if "variable" in kwargs:
            new_var = kwargs.pop("variable")
            if self._REBIND_VIA_NATIVE_CONFIGURE:
                super().configure(variable=new_var)
            else:
                self._variable = new_var
                if hasattr(self, "_draw"): self._draw()
        if "value" in kwargs:
            new_val = kwargs.pop("value")
            if self._REBIND_VIA_NATIVE_CONFIGURE:
                super().configure(value=new_val)
            else:
                self._value = new_val
                if hasattr(self, "_draw"): self._draw()
        if "command" in kwargs:
            super().configure(command=kwargs.pop("command"))

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)

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
        Gets or sets the widget's enabled/disabled state.

        Args:
            mode: If None, returns the current state without changing anything.
                Otherwise, only the literal string "disabled" (case-insensitive)
                is treated as disabled; anything in ("normal", "enabled",
                "active") is treated as enabled. Any other value matches
                neither branch, though colors are still harmlessly re-applied.

        Returns:
            The resulting state ("normal" or "disabled", lowercase).
        """
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
            super().configure(state="normal")
            # Re-establish the mouse bindings that disabling below may have
            # torn down.
            if hasattr(self, "_create_bindings"):
                try:
                    self._create_bindings()
                except Exception:
                    pass
            self._update_current_visual_state()

        elif mode == "disabled":
            self._custom_current_state = "disabled"
            # Uses CTk's native state="disabled" -- confirmed necessary (not
            # optional) on the button family, which originally used the same
            # manual-unbind code this method used to have, AND (unlike this
            # widget's original version) at least called state="normal" for
            # both branches -- meaning native state was NEVER actually set to
            # "disabled" at all before this fix. See module docstring.
            super().configure(state="disabled")
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
        Every value here traces back to sCTkThemes.json; there are no
        hardcoded colors in this method.

        See this class's docstring regarding "border_width" /
        "radiobutton_width" / "radiobutton_height" -- those keys have been
        removed from this loop entirely; they never matched anything in the
        real theme (see this class's docstring for what the actual keys are
        and why they don't need repaint-time handling).
        """
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "border_color", "hover_color", "text_color", "font"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = val

        if config_payload:
            super().configure(**config_payload)

    def bind(self, sequence=None, command=None, add=None):
        """
        No-ops while running inside Pygubu Designer (detected via the
        PYGUBU_DESIGNER_RUNNING environment variable), otherwise forwards to
        the native widget's bind(). Same pattern used by sCTkProgressBar.
        """
        if "PYGUBU_DESIGNER_RUNNING" in os.environ:
            return None
        return super().bind(sequence, command, add)
