#!/usr/bin/python3
"""
sCTkOptionMenuSecondary

The quiet variant of the dropdown option-selection menu (see also
sCTkOptionMenuPrimary, the emphasised one). Inherits directly from
ctk.CTkOptionMenu so CustomTkinter handles native rendering and dropdown
behaviour; this class layers theme resolution, a disabled state, and a border
on top.

FORMERLY A COMPOSITE. This widget used to be a ctk.CTkFrame wrapping an inner
ctk.CTkOptionMenu, because native CTkOptionMenu has no border option and this
variant needs one -- its fill is deliberately close to the background it sits
on, so without an outline the control is hard to see at rest.

That structure cost more than it bought:

  - values, command and variable lived on the inner menu, so cget("values")
    returned None here while returning a list on Primary. Two widgets meant to
    be interchangeable, disagreeing.
  - Every option CustomTkinter adds to CTkOptionMenu had to be forwarded by
    hand, forever.
  - The outline did not line up. A frame draws its own rounded rectangle
    around a widget that draws another, and at the corners the two diverged
    visibly.
  - The widget's SHAPE was dictated by one theme's colour choices. Swap the
    Primary and Secondary palettes and the structure is wrong.

sCTkOptionMenuBorderMixin now supplies the border, so this is a plain subclass
like Primary. get(), set(), values, command and variable are all native again.

Base class order matters. The mixin comes FIRST so its _draw() replaces the
native one; ctk.CTkOptionMenu comes next, so every other super() call in this
file resolves to it -- never to ThemeableWidget, whose own
configure()/cget()/_set_appearance_mode() overrides were removed for this
reason (see themeable_widget.py).
"""
from typing import Any, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget
from .sctk_optionmenu_border_mixin import sCTkOptionMenuBorderMixin


class sCTkOptionMenuSecondary(sCTkOptionMenuBorderMixin, ctk.CTkOptionMenu,
                              ThemeableWidget):
    """Themeable dropdown option-selection menu, quiet variant.

    Differs from sCTkOptionMenuPrimary in two ways, both from the theme file
    rather than from anything structural:

      - A border. border_width and border_color come from this widget's theme
        block via sCTkOptionMenuBorderMixin. Primary supports the same keys and
        simply sets border_width to 0.
      - No distinct arrow button. button_color is set from fg_color, so the
        arrow blends into the control rather than standing out as a separate
        block of colour. Primary gives it its own colour.

    fg_color and text_color are REQUIRED in whichever map is active -- top
    level for the normal state, disabled_map when disabled. Missing either
    raises rather than substituting a guess, following the library-wide
    fail-loud rule.
    """

    def __init__(self, master: Optional[Any] = None, width: int = 160,
                 height: int = 28, **kw: Any) -> None:
        """
        Args:
            master: Parent container.
            width / height: Widget dimensions in pixels.
            **kw: `values` (list[str]), `command` (callable) and `variable`
                (tkinter.StringVar) are pulled out and applied after the native
                widget exists. Everything else is either a native
                CTkOptionMenu argument or a theme-key override (see the
                "sCTkOptionMenuSecondary" block in sCTkThemes.json).
        """
        # 1. Capture widget-specific attributes before the theme pass, so they
        # are not merged into final_kw and treated as theme properties.
        values = kw.pop("values", None)
        command = kw.pop("command", None)
        variable = kw.pop("variable", None)

        kw.setdefault("width", width)
        kw.setdefault("height", height)

        # 2. Shared theme logic: resolves final_kw and the disabled map.
        ThemeableWidget.__init__(self, kw)

        # 3. Deep-copy onto this instance, so later changes never leak back
        # into the shared theme registry.
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

        # 5. Apply the extracted attributes now the native widget exists.
        if values is not None:
            super().configure(values=values)
        if command is not None:
            super().configure(command=command)
        if variable is not None:
            super().configure(variable=variable)

        # 6. Border, after the native widget exists: the first redraw needs a
        # canvas.
        self._init_border(
            border_width=self._local_defaults.get("border_width", 0),
            border_color=self._local_defaults.get("border_color"),
        )

        self._custom_current_state = "normal"
        self._update_current_visual_state()

        # 7. Lifecycle handshake, notifying Pygubu-style consumers that
        # construction is complete.
        self._finalize_themeable_lifecycle()

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally below.
                - "state": returns a Tkinter-style
                  (name, name, name, default, current) tuple.
                - "border_width" or "border_color": the same, from the mixin.
                - "fg_color"/"button_color"/"button_hover_color"/"text_color":
                  the same, with `current` reflecting the disabled or normal
                  value as appropriate.
                - anything else: handed to _configure_query(), which builds a
                  proper tuple rather than forwarding the name to the native
                  configure() -- see themeable_widget.py.
            **kwargs: Standard CTkOptionMenu options, plus `border_width` and
                `border_color`; `values`/`command`/`variable` are routed
                through super().configure() individually, and `state=...` goes
                through self.state().

        Returns:
            The query tuple for the single-argument case, otherwise whatever
            super().configure() returns.
        """
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

                if pname in ["fg_color", "button_color", "button_hover_color",
                             "text_color"]:
                    is_disabled = str(self.state()).lower() == "disabled"
                    source = (self._custom_disabled_map if is_disabled
                              else self._local_defaults)
                    return (pname, pname, pname,
                            self._query_value(self._local_defaults.get(pname)),
                            self._query_value(source.get(pname)))

                return self._configure_query(pname)

        # Consumed before the native call below, which rejects both as unknown
        # options.
        self._configure_border(kwargs)

        if "values" in kwargs:
            super().configure(values=kwargs.pop("values"))
        if "command" in kwargs:
            super().configure(command=kwargs.pop("command"))
        if "variable" in kwargs:
            super().configure(variable=kwargs.pop("variable"))

        if "state" in kwargs:
            self.state(str(kwargs.pop("state")).lower())

        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        if kwargs:
            return super().configure(**kwargs)
        return None

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not track whichever configure() a subclass defines.
    # Without this line, .config(...) would skip this override entirely and
    # land on the native widget, bypassing theming and state handling.
    config = configure

    def cget(self, attribute_name: str) -> Any:
        """
        Standard cget(), extended to this widget's own border properties.

        border_width and border_color are not native CTkOptionMenu options, so
        without this they reach CTkBaseClass.cget() and raise.
        """
        border_value = self._cget_border(attribute_name)
        if border_value is not self._NOT_A_BORDER_PROPERTY:
            return border_value
        return super().cget(attribute_name)

    def _set_appearance_mode(self, mode_string: str) -> None:
        """
        Forwards CustomTkinter's light/dark change to the native widget.

        No manual re-application is needed: colours are passed through as raw
        (light, dark) tuples, so CTk's own appearance tracking repaints them.
        The border follows because _draw() re-resolves it on every redraw.
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
            mode: None returns the current state unchanged. Otherwise only
                "disabled" (case-insensitive) disables; anything in
                ("normal", "enabled", "active") enables. Any other value
                matches neither branch, though the repaint still runs.

        Returns:
            The resulting state, lowercase.
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
        Recomputes and applies this widget's colours from the theme, based on
        the current state, then sets the native interactive lock.

        Colours are passed through as raw (light, dark) tuples so CTk's own
        appearance tracking handles light/dark repaints.

        button_color is set FROM fg_color rather than read as its own key.
        That is what makes this the quiet variant: the arrow blends into the
        control instead of standing out as a separate block, and the theme
        block accordingly has no button_color of its own. Primary gives the
        arrow its own colour.
        """
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        # fg_color and text_color are required in whichever map is active.
        # Substituting a guess would leave a broken theme block looking merely
        # slightly wrong -- see the library-wide fail-loud rule.
        section = "disabled_map" if is_disabled else "top-level"
        for required_key in ("fg_color", "text_color"):
            if target_map.get(required_key) is None:
                name = (getattr(self, "_THEME_BLOCK_NAME", None)
                        or self.__class__.__name__)
                raise KeyError(
                    f"'{name}' theme block is missing '{required_key}' in its "
                    f"{section} section of sCTkThemes.json."
                )

        payload = {}
        for key in ("font", "dropdown_font", "dropdown_fg_color",
                    "dropdown_text_color", "dropdown_hover_color",
                    "button_hover_color"):
            val = self._local_defaults.get(key)
            if val is not None:
                payload[key] = val

        fill = target_map.get("fg_color")
        payload.update({
            "fg_color": fill,
            "button_color": fill,
            "text_color": target_map.get("text_color"),
            "state": "disabled" if is_disabled else "normal",
        })
        super().configure(**payload)

        # The border is not a native option, so it cannot ride along above.
        # Its disabled colour comes from disabled_map like any other, falling
        # back to the normal one when unspecified.
        border_colour = target_map.get("border_color")
        if border_colour is None:
            border_colour = self._local_defaults.get("border_color")
        if border_colour is not None:
            self._border_color = border_colour
        self._redraw_border()

    def update_list(self, new_values: list, default_index: int = 0) -> None:
        """
        Replaces the dropdown's options and resets the visible selection.

        Args:
            new_values: The new options. An empty list sets a single blank
                option and clears the display.
            default_index: Which option to select afterwards. Out of range
                falls back to index 0 rather than raising.
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
