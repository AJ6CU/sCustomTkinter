#!/usr/bin/python3
"""
sCTkMessage - Piece 1 of 2

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

class sCTkMessage(ctk.CTkToplevel, ThemeableWidget):
    """Advanced themeable message dialog window supporting single or dual prompt states."""

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

        # 3. Initialize CTkToplevel natively
        super().__init__(master=master, *args, **kwargs)
        self.withdraw()

        self._result = None
        self.lift()
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.grab_set()
        self.title(title)

        font_config = self._local_defaults.get("font") or ("Arial", 14)
        text_color_config = self._local_defaults.get("text_color") or ("#1A1A1A", "#E5E5E5")

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

    def configure(self, *args, **kwargs):
        if args and len(args) == 1: return super().configure(args)
        if args and isinstance(args, dict): kwargs = args | kwargs
        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)
        if kwargs: return super().configure(**kwargs)
        return None

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
    # ⚡ GLOBAL SHORTCUT FUNCTION ROUTING CHANNELS
    # =====================================================================
    def showinfo(title: str, message: str, ok_text: str = "Ok", width: int = 400, master: any = None) -> Optional[bool]:
        return sCTkMessage(title, message, "info", master=master, buttons="ok", ok_text=ok_text, width=width).wait_end()

    def showwarning(title: str, message: str, ok_text: str = "Ok", width: int = 400, master: any = None) -> Optional[bool]:
        return sCTkMessage(title, message, "warning", master=master, buttons="ok", ok_text=ok_text, width=width).wait_end()

    def showerror(title: str, message: str, ok_text: str = "Ok", width: int = 400, master: any = None) -> Optional[bool]:
        return sCTkMessage(title, message, "error", master=master, buttons="ok", ok_text=ok_text, width=width).wait_end()

    def askyesno(title: str, message: str, yes_text: str = "Yes", no_text: str = "No", width: int = 400, master: any = None) -> bool:
        val = sCTkMessage(title, message, "info", master=master, buttons="yes_no", yes_text=yes_text, no_text=no_text, width=width).wait_end()
        return True if val is True else False

    def askwarningyesno(title: str, message: str, yes_text: str = "Yes", no_text: str = "No", width: int = 400, master: any = None) -> bool:
        val = sCTkMessage(title, message, "warning", master=master, buttons="yes_no", yes_text=yes_text, no_text=no_text, width=width).wait_end()
        return True if val is True else False

    def askerroryesno(title: str, message: str, yes_text: str = "Yes", no_text: str = "No", width: int = 400, master: any = None) -> bool:
        val = sCTkMessage(title, message, "error", master=master, buttons="yes_no", yes_text=yes_text, no_text=no_text, width=width).wait_end()
        return True if val is True else False

