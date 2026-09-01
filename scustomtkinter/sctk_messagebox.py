#!/usr/bin/python3
"""
sCTkMessage

An advanced, themeable dialog window system subclassed from ctk.CTkToplevel.
Supports customizable single prompt text or dual choice prompts returning boolean states.
Derived from Selector class by Fastattack, 2024.
"""
import os
import textwrap

import customtkinter as ctk
from .themeable_widget import ThemeableWidget

from PIL import Image
from typing import Literal, Union, Tuple, Optional

from .sctk_button_primary import sCTkButtonPrimary
from .sctk_button_secondary import sCTkButtonSecondary
from .sctk_label_primary import sCTkLabelPrimary

class sCTkMessagebox(ctk.CTkToplevel, ThemeableWidget):
    """Advanced themeable message dialog window supporting single or dual prompt states."""

    # Required at the TOP LEVEL of the theme block.
    _REQUIRED_THEME_KEYS = ("font", "text_color", "fg_color")

    # WHITELIST GUARD. Native CTkToplevel names fg_color explicitly and passes
    # everything else through to tkinter.Toplevel, which raises TclError on any
    # option it doesn't know. Theme keys like `font` and `text_color` are for
    # this widget's own label, NOT for the window, so final_kw is filtered down
    # to this set before the native constructor sees it.
    _NATIVE_CTKTOPLEVEL_KWARGS = frozenset({"fg_color"})

    # There is no disabled_map and no state(): this is a modal dialog. It grabs
    # input on construction and destroys itself on dismissal, so there is no
    # window of time in which a disabled appearance would mean anything.

    def __init__(self,
                 title: str,
                 message: str,
                 typ: Literal["info", "warning", "error"],
                 master: any = None,
                 buttons: Literal["ok", "yes_no"] = "ok",
                 ok_text: str = "Ok",
                 yes_text: str = "Yes",
                 no_text: str = "No",
                 width: int = 400,
                 *args, **kwargs):

        # 1. Fire our shared theme logic first to extract registry configurations safely
        ThemeableWidget.__init__(self, kwargs)

        # 2. 🛠️ THE MUTATION SAFEGUARD DEEP COPY:
        self._local_defaults = dict(self.final_kw)
        self._validate_theme_keys()

        # 3. Initialize CTkToplevel natively.
        #
        # FIX: this previously forwarded the RAW kwargs dict rather than the
        # resolved final_kw, so the theme block never reached the native
        # constructor at all -- the dialog window itself was unthemed, and
        # ThemeableWidget's resolution work was discarded for everything
        # except the two keys read back manually below. Passing final_kw
        # through the whitelist above fixes that and simultaneously protects
        # the native constructor: a caller passing font= to this widget would
        # previously have had it forwarded to tkinter.Toplevel, which raises
        # TclError on an option it doesn't recognize.
        native_kwargs = {k: v for k, v in self.final_kw.items()
                         if k in self._NATIVE_CTKTOPLEVEL_KWARGS}
        super().__init__(master=master, *args, **native_kwargs)
        self.withdraw()

        self._result = None
        self.lift()
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.grab_set()
        self.title(title)

        # No fallbacks: validated at construction, so both lookups resolve.
        font_config = self._local_defaults.get("font")
        text_color_config = self._local_defaults.get("text_color")

        # 4. Custom Local Icon Asset Extraction Loops
        # 4. 🔑 DYNAMIC ASSET PATH ANCHOR: Safely navigates down into assets/images/
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.normpath(os.path.join(current_script_dir, "assets", "images"))

        light_icon_path = os.path.join(images_dir, f"{typ}.png")
        dark_icon_path = os.path.join(images_dir, f"{typ}_dark.png")

        # Fallback to standard light version if an explicit dark-theme variant is missing
        if not os.path.exists(dark_icon_path):
            dark_icon_path = light_icon_path

        if os.path.exists(light_icon_path):
            try:
                pil_light = Image.open(light_icon_path)
                pil_dark = Image.open(dark_icon_path)
                ctk_image = ctk.CTkImage(light_image=pil_light, dark_image=pil_dark, size=(85, 85))
                self.image_label = sCTkLabelPrimary(self, text="", image=ctk_image, width=85, height=85)
                self.image_label.grid(row=0, column=0, padx=(15, 5), pady=20, sticky="n")
            except Exception as image_err:
                # Graceful extraction safety recovery trace
                print(f"⚠️ sCustomTkinter Warning -> Image format initialization error: {image_err}")
                self.image_label = sCTkLabelPrimary(self, text=f"[{typ.upper()}]", font=("Arial", 12, "bold"))
                self.image_label.grid(row=0, column=0, padx=(15, 5), pady=20, sticky="n")
        else:
            # Safe text-based interface fallback if filesystem layout tracks vanish
            print(f"⚠️ sCustomTkinter Warning -> Missing visual alert asset from target path: {light_icon_path}")
            self.image_label = sCTkLabelPrimary(self, text=f"[{typ.upper()}]", font=("Arial", 12, "bold"))
            self.image_label.grid(row=0, column=0, padx=(15, 5), pady=20, sticky="n")

        max_text_width_pixels = width - 180
        char_limit_per_line = max(20, int(max_text_width_pixels / 11.5))
        wrapped_message = "\n".join(textwrap.wrap(message, width=char_limit_per_line))

        self.label = sCTkLabelPrimary(self, text=wrapped_message, font=font_config, text_color=text_color_config, justify="left", anchor="w", wraplength=max_text_width_pixels)
        self.label.grid(row=0, column=1, padx=(10, 35), pady=20, sticky="w")

        if buttons == "yes_no":
            self.yes_button = sCTkButtonPrimary(self, text=yes_text, command=self.on_yes)
            self.yes_button.grid(row=1, column=0, padx=(15, 5), pady=15, sticky="ew")
            self.no_button = sCTkButtonSecondary(self, text=no_text, command=self.on_no)
            self.no_button.grid(row=1, column=1, padx=(5, 15), pady=15, sticky="ew")
            self.bind("<Return>", self.on_yes)
            self.grid_columnconfigure(0, weight=1, uniform="dialog_buttons")
            self.grid_columnconfigure(1, weight=1, uniform="dialog_buttons")
        else:
            self.ok_button = sCTkButtonPrimary(self, text=ok_text, command=self.on_ok)
            self.ok_button.grid(row=1, column=0, columnspan=2, padx=15, pady=15)
            self.bind("<Return>", self.on_ok)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

        self._center_window(target_width=width)
        self.deiconify()

        # 🔑 REGISTER LIFECYCLE HANDSHAKE HOOK: Unlocks full Pygubu parent support out of the box
        self._finalize_themeable_lifecycle()
    def _center_window(self, target_width: int):
        self.update_idletasks()
        width = target_width
        height = self.winfo_reqheight()
        if self.master and hasattr(self.master, "winfo_x"):
            x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (width // 2)
            y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (height // 2)
        else:
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")

    def _validate_theme_keys(self) -> None:
        """
        Hard-fails at construction on an incomplete theme block, naming the
        missing key.

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

    def configure(self, *args, **kwargs):
        """
        Standard configuration with positional-argument handling.

        Three separate bugs were fixed here:

        1. `super().configure(args)` passed the whole TUPLE as one positional
           argument rather than unwrapping it, so every single-argument query
           forwarded a malformed value.
        2. `if args and isinstance(args, dict)` -- args is ALWAYS a tuple, so
           the dict-merge branch was dead code. Same tautology fixed across
           the batch-one widgets.
        3. No `config = configure` alias existed, so `.config(...)` bypassed
           this override entirely and landed on the native widget.
        """
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                return super().configure(args[0])

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)
        if kwargs: return super().configure(**kwargs)
        return None

    # Tkinter binds .config to .configure as a SEPARATE class attribute -- it
    # does not track a subclass's override. Without this, .config(...) skips
    # everything above.
    config = configure

    def _close_dialog(self):
        self.grab_release()
        self.destroy()

    def on_ok(self, event=None):
        self._result = True
        self._close_dialog()

    def on_yes(self, event=None):
        self._result = True
        self._close_dialog()

    def on_no(self, event=None):
        self._result = False
        self._close_dialog()

    def wait_end(self) -> Optional[bool]:
        if self.master: self.master.wait_window(self)
        else: self.wait_window(self)
        return self._result

# =====================================================================
# ⚡ STANDALONE RE-ROUTING CHANNELS (OUTDENTED TO ZERO INDENT SPACES!)
# =====================================================================
def showinfo(title: str, message: str, ok_text: str = "Ok", width: int = 400, master: any = None) -> Optional[bool]:
    return sCTkMessagebox(title, message, "info", master=master, buttons="ok", ok_text=ok_text, width=width).wait_end()

def showwarning(title: str, message: str, ok_text: str = "Ok", width: int = 400, master: any = None) -> Optional[bool]:
    return sCTkMessagebox(title, message, "warning", master=master, buttons="ok", ok_text=ok_text, width=width).wait_end()

def showerror(title: str, message: str, ok_text: str = "Ok", width: int = 400, master: any = None) -> Optional[bool]:
    return sCTkMessagebox(title, message, "error", master=master, buttons="ok", ok_text=ok_text, width=width).wait_end()

def askyesno(title: str, message: str, yes_text: str = "Yes", no_text: str = "No", width: int = 400, master: any = None) -> bool:
    val = sCTkMessagebox(title, message, "info", master=master, buttons="yes_no", yes_text=yes_text, no_text=no_text, width=width).wait_end()
    return True if val is True else False

def askwarningyesno(title: str, message: str, yes_text: str = "Yes", no_text: str = "No", width: int = 400, master: any = None) -> bool:
    val = sCTkMessagebox(title, message, "warning", master=master, buttons="yes_no", yes_text=yes_text, no_text=no_text, width=width).wait_end()
    return True if val is True else False

def askerroryesno(title: str, message: str, yes_text: str = "Yes", no_text: str = "No", width: int = 400, master: any = None) -> bool:
    val = sCTkMessagebox(title, message, "error", master=master, buttons="yes_no", yes_text=yes_text, no_text=no_text, width=width).wait_end()
    return True if val is True else False


# =====================================================================
# 🔑 THE DYNAMIC BACK-BIND: Injects attributes onto the Class token namespace!
# =====================================================================
# This forces sCTkMessage.showinfo(...) to work perfectly everywhere!
sCTkMessagebox.showinfo = showinfo
sCTkMessagebox.showwarning = showwarning
sCTkMessagebox.showerror = showerror
sCTkMessagebox.askyesno = askyesno
sCTkMessagebox.askwarningyesno = askwarningyesno
sCTkMessagebox.askerroryesno = askerroryesno