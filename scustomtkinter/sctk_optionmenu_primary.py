#!/usr/bin/python3
"""
sCTkOptionMenuPrimary

A theme-compliant dropdown option-selection menu widget (see also
sCTkOptionMenuSecondary, a composite bordered variant). Inherits directly from
ctk.CTkOptionMenu so CustomTkinter handles native rendering and dropdown
behavior; this class layers automatic light/dark theme resolution and a
distinct enabled/disabled visual state on top.

Base class order matters here. sCTkOptionMenuBorderMixin comes FIRST so its
_draw() runs before the native one and can add a border on top; native
ctk.CTkOptionMenu comes next, so every other `super()` call in this file's own
methods resolves to ctk.CTkOptionMenu -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring); this widget owns all of
its own runtime color-swapping logic.

Disabling uses CTk's native state="disabled", consistent with every widget in
this library confirmed to correctly block interaction this way (the button
family, sCTkSegmentedButton) -- not independently re-tested for this specific
widget, but there's no equivalent here of the manual-unbind approach that was
found broken on the buttons.
"""
from typing import Any, Callable, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget
from .sctk_optionmenu_border_mixin import sCTkOptionMenuBorderMixin


class sCTkOptionMenuPrimary(sCTkOptionMenuBorderMixin, ctk.CTkOptionMenu,
                            ThemeableWidget):
    """Themeable dropdown option-selection menu.

    Adds to native ctk.CTkOptionMenu:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A distinct enabled/disabled visual state.
      - Pygubu Designer property introspection for `state`, `fg_color`,
        `button_color`, `button_hover_color`, and `text_color` via a
        single-argument configure() call.
      - update_list(), a convenience method for replacing the dropdown's
        options and resetting the visible selection in one call.
      - border_width/border_color, via sCTkOptionMenuBorderMixin. Native
        CTkOptionMenu has no border option at all -- see that module for why
        this matters and what it depends on.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox, sCTkSegmentedButton, and the button
    family. Not separately re-confirmed for this specific widget.

    The theme block's disabled_map only covers fg_color, button_color, and
    text_color -- it has no entries for button_hover_color, dropdown_fg_color,
    or dropdown_text_color. This is consistent with every other themed widget
    in this library: once natively disabled, hover and dropdown-open
    interactions can't fire in the first place, so there's nothing for those
    disabled-state colors to ever visibly apply to.
    """

    def __init__(self, master: Optional[Any] = None, **kw: Any) -> None:
        """
        Args:
            master: Parent container.
            **kw: `values` (list[str]), `command` (callable), and `variable`
                (tkinter.StringVar) are pulled out explicitly below. Everything
                else is either a native CTkOptionMenu argument or a theme-key
                override (see the "sCTkOptionMenuPrimary" block in
                sCTkThemes.json).
        """
        # 1. Capture widget-specific attributes early, before the mixin's own
        # configuration pass, so they don't get merged into final_kw and
        # treated as theme-overridable properties.
        values = kw.pop("values", None)
        command = kw.pop("command", None)
        variable = kw.pop("variable", None)

        # 2. Fire our shared theme logic. This resolves final_kw
        # (construction-time properties) and the disabled color map. See
        # ThemeableWidget.__init__ for what actually happens here.
        ThemeableWidget.__init__(self, kw)

        # 3. Deep-copy the resolved map onto this instance, so later changes
        # here never leak back into the shared theme registry.
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 4. Initialize CustomTkinter natively.
        #
        # border_width and border_color are REMOVED first. They are this
        # library's own additions -- native CTkOptionMenu has no border option
        # and rejects any keyword it does not recognise, so leaving them in
        # final_kw would raise at construction. _local_defaults above already
        # holds copies for _init_border() to read.
        native_kw = {k: v for k, v in self.final_kw.items()
                     if k not in ("border_width", "border_color")}
        super().__init__(master, **native_kw)

        # 5. Apply the extracted values/command/variable now that the native
        # widget exists.
        if values is not None:
            super().configure(values=values)
        if command is not None:
            super().configure(command=command)
        if variable is not None:
            super().configure(variable=variable)

        # Border, after the native widget exists: the first redraw needs a
        # canvas. Absent from the theme block means no border, which is the
        # native widget's own appearance.
        self._init_border(
            border_width=self._local_defaults.get("border_width", 0),
            border_color=self._local_defaults.get("border_color"),
        )

        self._custom_current_state = "normal"
        self._update_current_visual_state()

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
                - one of "fg_color"/"button_color"/"button_hover_color"/
                  "text_color": returns the same style of tuple, with
                  `current` reflecting the disabled or normal value as
                  appropriate. Note the returned value is str(value), where
                  value may itself be a (light, dark) tuple rather than a
                  single resolved color -- a known limitation shared with the
                  wider Pygubu-query investigation set aside elsewhere in this
                  project, not fixed here.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties (same limitation).
            **kwargs: Standard CTkOptionMenu configuration options, plus:
                `values`/`command`/`variable` are routed through
                super().configure() individually; `state=...` routes through
                self.state() rather than being forwarded as-is.

        Returns:
            The query tuple described above for the single-argument case, or
            whatever super().configure() returns for the keyword-argument case
            (typically None).
        """
        # args is always a tuple -- args[0] is the actual value passed, whether
        # that's a string or a dict. An earlier version of this method set
        # `pname = args` directly, with no unwrapping attempt at all, so the
        # query branches below never matched anything and the fallback
        # forwarded the wrapped tuple itself to super().configure() -- not a
        # valid call shape for the native widget. Don't reintroduce that.
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname == "state":
                    return ("state", "state", "state", "normal", str(self.state()))

                border_value = self._cget_border(pname)
                if border_value is not self._NOT_A_BORDER_PROPERTY:
                    return (pname, pname, pname,
                            self._query_value(self._local_defaults.get(pname)),
                            self._query_value(border_value))

                if pname in ["fg_color", "button_color", "button_hover_color", "text_color"]:
                    current_state = str(self.state()).lower()
                    val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                    return (pname, pname, pname, self._query_value(self._local_defaults.get(pname)), self._query_value(val))

                return self._configure_query(pname)

        # Consumed before the native call below, which rejects both as
        # unknown options.
        self._configure_border(kwargs)

        if "values" in kwargs:
            super().configure(values=kwargs.pop("values"))
        if "command" in kwargs:
            super().configure(command=kwargs.pop("command"))
        if "variable" in kwargs:
            super().configure(variable=kwargs.pop("variable"))

        if "state" in kwargs:
            target_state = str(kwargs.pop("state")).lower()
            self.state(target_state)

        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        if kwargs:
            result =  super().configure(**kwargs)
        else:
            result =  None
        self._redraw_border()  # last, after any native redraw
        return result

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. Without this line, calling .config(...) on an instance
    # would silently skip this entire override and land on the native widget's
    # configure() directly, bypassing theming and state handling entirely.
    config = configure

    def cget(self, attribute_name: str) -> Any:
        """
        Standard cget(), extended to this widget's own border properties.

        FIX: border_width and border_color are not native CTkOptionMenu
        options, so without this they reached CTkBaseClass.cget() and raised

            ValueError: 'border_width' is not a supported argument.

        configure(pname) had a border branch already; the ordinary cget() path
        did not, so reading a border value in application code failed while
        querying it through the Designer worked.

        Args:
            attribute_name: The property to read.

        Returns:
            The property's value.
        """
        border_value = self._cget_border(attribute_name)
        if border_value is not self._NOT_A_BORDER_PROPERTY:
            return border_value
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
        Gets or sets the widget's enabled/disabled visual state.

        Args:
            mode: If None, returns the current state without changing anything.
                Otherwise, only the literal string "disabled" (case-insensitive)
                is treated as disabled; anything in ("normal", "enabled",
                "active") is treated as enabled. Any other value matches
                neither branch, though _update_current_visual_state() still
                runs (harmlessly re-applying the current state's colors).

        Returns:
            The resulting state ("normal" or "disabled", lowercase).
        """
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
        elif mode == "disabled":
            self._custom_current_state = "disabled"

        self._update_current_visual_state()
        return self._custom_current_state

    def _update_current_visual_state(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, based
        on the current state, then sets the native interactive lock.

        Called after construction and on every state() change.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.
        Every value here traces back to sCTkThemes.json; there are no
        hardcoded colors in this method.

        font, dropdown_fg_color, and dropdown_text_color are included in the
        property list below for both states, but disabled_map doesn't define
        any of them -- they simply keep whatever value was last set (from
        construction, in the normal case) when the widget is disabled. See
        this class's docstring for why that's not a problem in practice.
        """
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "button_color", "button_hover_color", "text_color", "dropdown_fg_color", "dropdown_text_color", "font"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = val

        if config_payload:
            super().configure(**config_payload)

        # The border is not a native option, so it cannot ride along in the
        # payload above. Its disabled colour comes from disabled_map like any
        # other, falling back to the normal one when unspecified.
        border_colour = target_map.get("border_color")
        if border_colour is None:
            border_colour = self._local_defaults.get("border_color")
        if border_colour is not None:
            self._border_color = border_colour
        self._redraw_border()

        if is_disabled:
            super().configure(state="disabled")
        else:
            super().configure(state="normal")

    def update_list(self, new_values: list, default_index: int = 0) -> None:
        """
        Replaces the dropdown's options and resets the visible selection.

        Args:
            new_values: The new list of options. If empty, the widget is set
                to a single blank option and the display is cleared.
            default_index: Which option to select after updating. If out of
                range for new_values, falls back to index 0 rather than
                raising.
        """
        if not new_values:
            self.configure(values=[""])
            self.set("")
            return

        self.configure(values=new_values)

        if default_index < len(new_values):
            self.set(new_values[default_index])
        else:
            self.set(new_values[0])