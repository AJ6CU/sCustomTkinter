#!/usr/bin/python3
"""
sCTkSeparator

An advanced Separator widget supporting custom section header text,
dashed line patterns, corner roundness, and responsive orientation modes.
Inherits cleanly and directly from ctk.CTkBaseClass to preserve native canvas draw engines.

Derived from Selector class by Fastattack, 2024.
https://github.com
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkSeparator(ctk.CTkBaseClass, ThemeableWidget):
    """Advanced Separator supporting headers, dashed lines, and themes.json matrices."""

    # Required at the TOP LEVEL of the theme block. Structural parameters
    # (orientation, length, width, text, dash) are deliberately absent: they
    # are constructor arguments with sensible defaults, and although the theme
    # CAN supply them, requiring them would force layout decisions into the
    # stylesheet.
    _REQUIRED_THEME_KEYS = ("fg_color", "text_color", "font", "corner_radius")

    # Required inside disabled_map.
    _REQUIRED_DISABLED_KEYS = ("fg_color", "text_color")

    def __init__(self, master=None, **kwargs):
        # 1. Fire our shared theme logic first. It automatically finds "sCTkSeparator" in themes.json
        ThemeableWidget.__init__(self, kwargs)

        # 2. 🛠️ THE MUTATION SAFEGUARD DEEP COPY SHIELD:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)
        self._validate_theme_keys()

        # Extract structural parameters safely out of the resolved theme dictionary
        self._orientation = str(self.final_kw.pop("orientation", "vertical")).lower()
        length = int(self.final_kw.pop("length", 100))
        width = float(self.final_kw.pop("width", 4))

        self._text = str(self.final_kw.pop("text", ""))
        self._dash = self.final_kw.pop("dash", None)
        # No fallback: validated above.
        self._font = self.final_kw.pop("font")

        # 🔑 VERTICAL HOUSING REMAP: Programmatically upscale horizontal bounds to fit text
        if self._text and width <= 4:
            width = 28

        if self._orientation == "vertical":
            height = length
        elif self._orientation == "horizontal":
            height = width
            width = length
        else:
            raise ValueError(
                f"The value for orientation is incorrect: \"{self._orientation}\". Should be \"vertical\" or \"horizontal\"")

        # 3. Initialize CustomTkinter's base structure using finalized parameters
        ctk.CTkBaseClass.__init__(
            self,
            master=master,
            width=width,
            height=height,
            bg_color=self.final_kw.get("bg_color", "transparent")
        )

        self._custom_current_state = "normal"
        self._corner_radius = self.final_kw.get("corner_radius")
        self._fg_color = self._check_color_type(self.final_kw.get("fg_color"))

        # Map text color vectors safely out of the extracted dictionary layout layers
        # No CTkLabel fallback: text_color is validated above, so borrowing another
        # widget class's colour would only mask a theme gap.
        self._text_color = self._check_color_type(self.final_kw.get("text_color"))

        # 4. Canvas and render configurations
        self._canvas = ctk.CTkCanvas(self, highlightthickness=0)
        self._canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._draw_engine = ctk.DrawEngine(self._canvas)

        # 5. Bind layout adjustments to bypass CTkBaseClass strict bind filters safely
        super(ctk.CTkBaseClass, self).bind("<Configure>", lambda e: self._draw(), add="+")

        # 6. Trigger the initial render loop pass
        self._draw(no_color_updates=True)

        # 🔑 7. REGISTER LIFECYCLE HANDSHAKE HOOK: Pushes notifications up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

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

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring active or disabled tracks repaint fluidly on theme shifts."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._update_current_visual_state()
    def _update_current_visual_state(self):
        """Forwards global theme preference swipes directly to our core draw layout routine."""
        self._draw()

    def _draw(self, no_color_updates=False):
        if hasattr(super(), "_draw"):
            try: super()._draw(no_color_updates)
            except Exception: pass
        current_w = self.winfo_width() if self.winfo_width() > 1 else self._current_width
        current_h = self.winfo_height() if self.winfo_height() > 1 else self._current_height
        self._canvas.delete("all")

        detected_bg = self._detect_color_of_master()
        if detected_bg == "transparent" or detected_bg is None:
            detected_bg = ctk.ThemeManager.theme["CTk"]["fg_color"]

        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        # FIX: these previously carried hardcoded fallbacks, and since this
        # widget's theme block had no disabled_map at all, the fallbacks were
        # ALWAYS taken -- a disabled separator never used the configured
        # theme. disabled_map is now required, so no fallback is needed. (The
        # old text fallback also used the Tk colour name "gray50" rather than
        # a hex pair, the only such value in the library.)
        target_fg = self._custom_disabled_map.get("fg_color") if is_disabled else self._fg_color
        target_txt = self._custom_disabled_map.get("text_color") if is_disabled else self._text_color

        fg_rendered = self._apply_appearance_mode(self._check_color_type(target_fg))
        txt_rendered = self._apply_appearance_mode(self._check_color_type(target_txt))
        self._canvas.configure(bg=self._apply_appearance_mode(detected_bg))

        if self._orientation == "horizontal":
            line_thickness = self._current_height if self._current_height < current_h else 4
            if line_thickness > 10: line_thickness = 4
        else:
            line_thickness = self._current_width if self._current_width < current_w else 4
            if line_thickness > 10: line_thickness = 4

        if self._text:
            t_id = self._canvas.create_text(current_w / 2, current_h / 2, text=self._text, font=self._font, fill=txt_rendered)
            bbox = self._canvas.bbox(t_id)
            if bbox:
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                tw, th = text_width + 16, text_height + 8
                x1 = (current_w / 2) - (tw / 2)
                x2 = (current_w / 2) + (tw / 2)

                if self._orientation == "horizontal":
                    y1, y2 = 1, current_h - 1
                    self._canvas.create_line(x1, y1, x1, y2, fill=fg_rendered, width=2)
                    self._canvas.create_line(x2, y1, x2, y2, fill=fg_rendered, width=2)
                    mid_y = current_h / 2
                    self._canvas.create_line(0, mid_y, x1, mid_y, fill=fg_rendered, width=line_thickness, dash=self._dash)
                    self._canvas.create_line(x2, mid_y, current_w, mid_y, fill=fg_rendered, width=line_thickness, dash=self._dash)
                else:
                    x1_v, x2_v = 1, current_w - 1
                    y1 = (current_h / 2) - (th / 2)
                    y2 = (current_h / 2) + (th / 2)
                    self._canvas.create_line(x1_v, y1, x2_v, y1, fill=fg_rendered, width=2)
                    self._canvas.create_line(x1_v, y2, x2_v, y2, fill=fg_rendered, width=2)
                    mid_x = current_w / 2
                    self._canvas.create_line(mid_x, 0, mid_x, y1, fill=fg_rendered, width=line_thickness, dash=self._dash)
                    self._canvas.create_line(mid_x, y2, mid_x, current_h, fill=fg_rendered, width=line_thickness, dash=self._dash)
        else:
            if self._dash:
                if self._orientation == "horizontal":
                    self._canvas.create_line(0, current_h / 2, current_w, current_h / 2, fill=fg_rendered, width=line_thickness, dash=self._dash)
                else:
                    self._canvas.create_line(current_w / 2, 0, current_w / 2, current_h, fill=fg_rendered, width=line_thickness, dash=self._dash)
            else:
                self._draw_engine.draw_rounded_rect_with_border(current_w, current_h, self._apply_widget_scaling(self._corner_radius), 0)
                self._canvas.itemconfig("inner_parts", outline=fg_rendered, fill=fg_rendered)

    def configure(self, *args, **kwargs):
        """Processes Pygubu designer workspace queries and manages theme state updates cleanly."""
        if args and len(args) == 1:
            pname = args[0]
            if pname == "state": return ("state", "state", "state", "normal", self.get_state())
            if pname in ["fg_color", "text_color"]:
                val = self._custom_disabled_map.get(pname) if self.get_state() == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))
            return super().configure(pname)

        # FIX: was `if args and isinstance(args, dict)`. args is ALWAYS a
        # tuple, so this never fired and the dict form of configure() was
        # dead code. Same tautology fixed across the batch-one widgets.
        if len(args) == 1 and isinstance(args[0], dict): kwargs = {**args[0], **kwargs}
        if "state" in kwargs: self.state(kwargs.pop("state"))
        if "text" in kwargs: self._text = str(kwargs.pop("text"))
        if "dash" in kwargs: self._dash = kwargs.pop("dash")

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)
        if kwargs: super().configure(**kwargs)
        self._draw()

    config = configure
    def get_state(self) -> str: return str(getattr(self, "_custom_current_state", "normal")).lower()
    def state(self, mode: str = None) -> str:
        if mode is None: return self.get_state()
        self._custom_current_state = mode.lower()
        self._draw()
        return self._custom_current_state

    def cget(self, attribute_name: str):
        if attribute_name == "height": raise ValueError("Use length and width arguments instead.")
        if attribute_name == "state": return self.get_state()
        mapping = {"corner_radius": self._corner_radius, "fg_color": self._fg_color, "orientation": self._orientation, "text": self._text, "dash": self._dash}
        return mapping.get(attribute_name, super().cget(attribute_name))

    def bind(self, sequence=None, command=None, add=True):
        """
        Routes bindings to the internal canvas, which is what actually
        receives events -- CTkBaseClass filters direct binds on the widget.

        FIX: the `add` argument was previously accepted and then ignored,
        with add=True hardcoded in the forwarded call. A caller passing
        add=False expecting to REPLACE existing bindings would silently
        accumulate them instead.
        """
        self._canvas.bind(sequence, command, add=add)

    def unbind(self, sequence=None, funcid=None):
        """
        Removes a binding from the internal canvas.

        FIX: funcid was previously accepted and then discarded, so this always
        removed EVERY binding for the sequence rather than the single one the
        caller identified. That is the same destructive behaviour that made
        unbind() unusable for blocking scrollbar drags in
        sCTkScrollableFrame -- Tk's unbind() with no funcid wipes bindings
        this widget never installed, with no way to restore them.
        """
        self._canvas.unbind(sequence, funcid)