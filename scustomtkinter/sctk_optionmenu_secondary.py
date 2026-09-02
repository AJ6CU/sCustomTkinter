#!/usr/bin/python3
"""
sCTkOptionMenuSecondary

A theme-compliant, composite bordered dropdown option-selection menu widget
(see also sCTkOptionMenuPrimary, a simpler direct-subclass variant). Unlike
every other widget in this library, this one is NOT a direct subclass of the
native widget it wraps -- it's a ctk.CTkFrame that contains a plain (not
sCTk-themed) ctk.CTkOptionMenu inside it, giving the dropdown a themed border
the native OptionMenu doesn't have on its own.

Base class order matters here: `class sCTkOptionMenuSecondary(ctk.CTkFrame,
ThemeableWidget)` puts the native CTk class first, so every `super()` call in
this file's own methods resolves to ctk.CTkFrame -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring); this widget owns all of
its own runtime color-swapping logic.

Because this widget is a Frame wrapping an OptionMenu rather than an OptionMenu
itself, every configure() call to the OUTER widget (via super().configure())
affects the FRAME (border, background, size) -- the INNER dropdown
(self._menu) has to be configured separately, which is why
_update_current_visual_state() below makes two distinct configure() calls.

Disabling passes state="disabled" to the INNER self._menu (not the frame,
which has no interactive state to lock) -- consistent with every widget in
this library confirmed to correctly block interaction via native "disabled".
"""
from typing import Any, Callable, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkOptionMenuSecondary(ctk.CTkFrame, ThemeableWidget):
    """Themeable, composite bordered dropdown option-selection menu.

    Adds a themed border/background frame around a plain native
    ctk.CTkOptionMenu, since the native widget has no border of its own to
    theme directly.

    Adds to native ctk.CTkFrame + ctk.CTkOptionMenu:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A distinct enabled/disabled visual state.
      - Pygubu Designer property introspection for `state`, `fg_color`,
        `border_color`, `text_color`, `width`, and `height` via a
        single-argument configure() call.
      - update_list(), get(), and set(), which delegate to the inner
        self._menu since the outer Frame has no selection of its own.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox, sCTkSegmentedButton, and the button
    family. Not separately re-confirmed for this specific widget.

    fg_color and text_color are required to be present in whichever map is
    active (the top-level block for normal state, disabled_map for disabled)
    -- if either is missing, _update_current_visual_state() raises immediately
    rather than silently substituting a hardcoded color. An earlier version of
    this method used hardcoded hex fallbacks for both; per this project's
    design, ThemeableWidget-based widgets are meant to fail hard on incomplete
    theme data, not paper over it (see sCTkLabelPrimary/Secondary/Tertiary for
    the precedent this follows).
    """

    def __init__(self, master: Optional[Any] = None, width: int = 160, height: int = 28, **kw: Any) -> None:
        """
        Args:
            master: Parent container.
            width: Native CTkFrame width fallback if not overridden by theme
                or kwargs.
            height: Native CTkFrame height fallback if not overridden by theme
                or kwargs.
            **kw: `values` (list[str]), `command` (callable), and `variable`
                (tkinter.StringVar) are pulled out explicitly below and
                forwarded to the inner ctk.CTkOptionMenu. Theme keys that
                belong to the inner menu rather than the outer frame (font,
                dropdown_font, text_color, dropdown_fg_color,
                dropdown_text_color, dropdown_hover_color, button_hover_color)
                are also extracted below, into self._menu_theme_kw, before the
                frame itself is constructed. See the "sCTkOptionMenuSecondary"
                block in sCTkThemes.json.
        """
        # 1. Capture menu-specific attributes early, before the mixin's own
        # configuration pass.
        values = kw.pop("values", [""])
        command = kw.pop("command", None)
        variable = kw.pop("variable", None)

        # 2. Apply width/height as kwarg defaults, so an explicit kwarg (or a
        # theme override) still wins over the constructor parameter defaults.
        kw.setdefault("width", width)
        kw.setdefault("height", height)

        # 3. Fire our shared theme logic. This resolves final_kw
        # (construction-time properties) and the disabled color map. See
        # ThemeableWidget.__init__ for what actually happens here.
        ThemeableWidget.__init__(self, kw)

        # 4. Deep-copy the resolved map onto this instance, so later changes
        # here never leak back into the shared theme registry.
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 5. Split out theme keys that belong to the INNER menu, not the OUTER
        # frame -- the frame's own super().__init__() below would reject most
        # of these (a Frame has no "font" or "dropdown_fg_color" option).
        MENU_KEYS = {
            "font", "dropdown_font", "text_color", "disabled_text_color",
            "dropdown_fg_color", "dropdown_text_color", "dropdown_hover_color",
            "button_hover_color"
        }
        self._menu_theme_kw = {}
        for key in MENU_KEYS:
            if key in self.final_kw:
                self._menu_theme_kw[key] = self.final_kw.pop(key)

        # 6. Initialize the native ctk.CTkFrame container with the remaining,
        # frame-appropriate kwargs.
        super().__init__(master, **self.final_kw)

        # 7. Build the inner (plain, not sCTk-themed) native option menu.
        self._menu = ctk.CTkOptionMenu(
            self,
            values=values,
            command=command,
            variable=variable
        )
        self._menu.pack(expand=True, fill="both", padx=2, pady=2)

        # 8. Apply initial theming to both the frame and the inner menu.
        self._custom_current_state = "normal"
        self._update_current_visual_state()

        # 9. Register lifecycle handshake hook, notifying Pygubu-style
        # consumers that construction is complete.
        self._finalize_themeable_lifecycle()

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally below.
                - the literal string "state": returns a Tkinter-style
                  (name, name, name, default, current) tuple.
                - one of "fg_color"/"border_color"/"text_color"/"width"/
                  "height": returns the same style of tuple, with `current`
                  reflecting the disabled or normal value as appropriate for
                  the color properties. Note the returned value is str(value),
                  where value may itself be a (light, dark) tuple rather than
                  a single resolved color -- a known limitation shared with
                  the wider Pygubu-query investigation set aside elsewhere in
                  this project, not fixed here.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties (same limitation).
            **kwargs: Standard CTkFrame configuration options for the outer
                frame, plus: `values`/`command`/`variable` are routed to the
                INNER self._menu, not the frame; `state=...` routes through
                self.state() rather than being forwarded as-is.

        Returns:
            The query tuple described above for the single-argument case, or
            None for the keyword-argument case (this method doesn't return
            super().configure()'s result in that branch).
        """
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname == "state":
                    return ("state", "state", "state", "normal", str(self.state()))

                if pname in ["fg_color", "border_color", "text_color", "width", "height"]:
                    current_state = str(self.state()).lower()
                    val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                    return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

                return super().configure(pname)

        if "values" in kwargs: self._menu.configure(values=kwargs.pop("values"))
        if "command" in kwargs: self._menu.configure(command=kwargs.pop("command"))
        if "variable" in kwargs: self._menu.configure(variable=kwargs.pop("variable"))

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)

        if kwargs:
            super().configure(**kwargs)
        return None

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. Without this line, calling .config(...) on an instance
    # would silently skip this entire override and land on the native widget's
    # configure() directly.
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
            try: super()._set_appearance_mode(mode_string)
            except Exception: pass

    def get_state(self) -> str:
        """Equivalent to calling state() with no argument."""
        return str(self.state()).lower()

    def state(self, mode: Optional[str] = None) -> str:
        """
        Gets or sets the widget's enabled/disabled visual state.

        Args:
            mode: If None, returns the current state without changing anything.
                Otherwise, only the literal string "disabled" (case-insensitive)
                is treated as disabled; anything in ("normal", "enabled",
                "active") is treated as enabled. Any other value matches
                neither branch, though _update_current_visual_state() still
                runs.

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
        Recomputes and applies colors to both the outer frame and the inner
        menu from the theme file, based on the current state.

        Called after construction and on every state() change.

        Passes raw (light, dark) tuples straight through to configure()
        instead of resolving to a single color first. Every value here traces
        back to sCTkThemes.json; there are no hardcoded colors in this method.

        fg_color and text_color are required to be present in whichever map is
        active -- see this class's docstring for why. An earlier version
        computed these with hardcoded fallback tuples, AND separately
        contained a real bug: it set the inner menu's button_hover_color
        correctly from self._menu_theme_kw in an early loop, then
        immediately overwrote that value with fg_color in a later
        .update() call -- meaning the actual themed button_hover_color from
        sCTkThemes.json was completely unreachable, always silently replaced.
        Fixed here by no longer re-setting button_hover_color in the
        state-dependent block below; the theme-driven value from the earlier
        loop is left alone.
        """
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        # 1. Update the outer frame's own border/background.
        frame_config = {}
        for key in ("border_color", "fg_color", "border_width", "corner_radius"):
            val = target_map.get(key)
            if val is not None:
                frame_config[key] = val
        if frame_config:
            super().configure(**frame_config)

        # 2. Update the inner menu's static (never state-swapped) properties.
        menu_payload = {}
        for key in ("font", "dropdown_font", "dropdown_fg_color", "dropdown_text_color", "dropdown_hover_color", "button_hover_color"):
            val = self._menu_theme_kw.get(key)
            if val is not None:
                menu_payload[key] = val

        # 3. Update the inner menu's state-dependent properties. fg_color and
        # text_color are required -- see this class's docstring.
        if target_map.get("fg_color") is None:
            raise KeyError(
                f"'{self.__class__.__name__}' theme block is missing 'fg_color' in its "
                f"{'disabled_map' if is_disabled else 'top-level'} section of sCTkThemes.json."
            )
        if target_map.get("text_color") is None:
            raise KeyError(
                f"'{self.__class__.__name__}' theme block is missing 'text_color' in its "
                f"{'disabled_map' if is_disabled else 'top-level'} section of sCTkThemes.json."
            )

        menu_fg = target_map.get("fg_color")
        menu_payload.update({
            "fg_color": menu_fg,
            "button_color": menu_fg,
            "text_color": target_map.get("text_color"),
            "state": "disabled" if is_disabled else "normal",
        })

        self._menu.configure(**menu_payload)

    def update_list(self, new_values: list, default_index: int = 0) -> None:
        """
        Replaces the inner menu's options and resets the visible selection.

        Args:
            new_values: The new list of options. If empty, the inner menu is
                set to a single blank option and the display is cleared.
            default_index: Which option to select after updating. If out of
                range for new_values, falls back to index 0 rather than
                raising.
        """
        if not new_values:
            self._menu.configure(values=[""])
            self._menu.set("")
            return

        self._menu.configure(values=new_values)
        if default_index < len(new_values):
            self._menu.set(new_values[default_index])
        else:
            self._menu.set(new_values[0])

    def set(self, value: str) -> None:
        """Delegates to the inner menu's set()."""
        self._menu.set(value)

    def get(self) -> str:
        """Delegates to the inner menu's get()."""
        return self._menu.get()
