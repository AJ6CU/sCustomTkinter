#!/usr/bin/python3
"""
sCTkPathChooser - Piece 1 of 4

A custom, compound theme-compliant path selection tool pairing an entry line with a browse button.
Inherits cleanly and directly from ctk.CTkFrame to preserve 100% of native CustomTkinter loops.
"""
import os
import sys
import ast
import tkinter as tk

import customtkinter as ctk
from .themeable_widget import ThemeableWidget

from .sctk_file_explorer import sCTkFileExplorer

# Framework-compliant component imports
from .sctk_button_primary import sCTkButtonPrimary
from .sctk_entry_primary import sCTkEntryPrimary

class sCTkPathChooser(ctk.CTkFrame, ThemeableWidget):
    _MANAGED_PROPERTIES = frozenset({
        "initialdir", "initialfile", "type", "title", "filetypes", "defaultextension",
        "btn_width", "btn_height", "btn_text", "entry_height", "browser_width", "browser_height", "justify"
    })

    def __init__(self, master=None, **kwargs):
        # Forcefully extract custom properties out so ctk.CTkFrame never throws a kwargs error
        self.type = str(kwargs.pop("type", "directory") or "directory").lower()
        self.title = str(kwargs.pop("title", "Select Path"))
        self.command = kwargs.pop("command", None)

        # Pull standard layout sizing constraints explicitly, cleansing them from kwargs pass
        desired_width = kwargs.pop("width", 350)
        desired_height = kwargs.pop("height", 32)

        # Pop text alignment parameters or fall back to left orientation
        self.justify = str(kwargs.pop("justify", "left")).lower()
        if self.justify not in ("left", "right", "center"):
            self.justify = "left"

        # Pop entry custom height dimensions or fall back to global layout height
        self.entry_height = int(kwargs.pop("entry_height", desired_height))

        # Pop button custom dimensions or fall back to defaults
        self.btn_width = int(kwargs.pop("btn_width", 110))
        self.btn_height = int(kwargs.pop("btn_height", desired_height))

        # Pop custom button label override text parameter
        self.btn_text = kwargs.pop("btn_text", None)
        if self.btn_text is not None:
            self.btn_text = str(self.btn_text)

        # Pop modal document viewer window geometry attributes safely
        self.browser_width = int(kwargs.pop("browser_width", 500))
        self.browser_height = int(kwargs.pop("browser_height", 450))

        # SAFE INTERCEPTION FIX: Clean and extract state out of kwargs before calling base class constructor
        self._initial_state_seed = str(kwargs.pop("state", "normal")).lower()

        # Clean out other potential custom property parameter leaks
        kwargs.pop("defaultextension", None)
        kwargs.pop("entry_width", None)

        raw_file = kwargs.pop("initialfile", None)
        raw_dir = kwargs.pop("initialdir", None)
        ft_raw = kwargs.pop("filetypes", None)

        self.initialfile = os.path.normpath(os.path.expanduser(str(raw_file))) if raw_file else None
        self.initialdir = os.path.normpath(os.path.expanduser(str(raw_dir))) if raw_dir else os.getcwd()

        if self.type == "directory" and self.initialfile:
            self.initialdir = os.path.dirname(self.initialfile)
            self.initialfile = None

        self.filetypes = []
        if ft_raw:
            if self.type != "file":
                raise ValueError("Cannot configure filetypes filter attributes when widget type matches 'directory'.")
            if isinstance(ft_raw, str):
                cleaned_ft = ft_raw.strip()
                if not (cleaned_ft.startswith("[") and cleaned_ft.endswith("]")):
                    raise ValueError(f"Malformed filetypes string array sequence: '{ft_raw}'.")
                try:
                    self.filetypes = ast.literal_eval(cleaned_ft)
                except Exception as err:
                    raise ValueError(f"Malformed syntax encountered processing filetypes configuration string: {err}")
            else:
                self.filetypes = ft_raw
        else:
            self.filetypes = None
        # Enforce name introspection by passing kwargs directly up into ThemeableWidget
        ThemeableWidget.__init__(self, kwargs)

        # 🛠️ THE MUTATION SAFEGUARD DEEP COPY SHIELD:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # Initialize base container passing standard frame parameters safely with no extra keyword arguments leaking
        super().__init__(master, width=desired_width, height=desired_height, **kwargs)

        self._state = "normal" if self._initial_state_seed not in ("normal", "disabled") else self._initial_state_seed

        # Enforce strict pixel dimensional footprints to withstand parent scale bounds
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)  # Column 0 (Entry) gets all available stretch space
        self.columnconfigure(1, weight=0)  # Column 1 (Button) stays fixed to btn_width
        self.rowconfigure(0, weight=1)

        self.entry = sCTkEntryPrimary(self, justify=self.justify, width=0, height=self.entry_height)
        entry_v_padding = max(0, (desired_height - self.entry_height) // 2)
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=entry_v_padding)

        default_seed = self.initialfile if self.initialfile else self.initialdir
        self.set(default_seed)

        self.btn = sCTkButtonPrimary(self, width=self.btn_width, height=self.btn_height, command=self._launch_browser)
        btn_v_padding = max(0, (desired_height - self.btn_height) // 2)
        self.btn.grid(row=0, column=1, sticky="ew", pady=btn_v_padding)

        # Force structural tracking state initialization loops
        self._process_live_theme_repaint()
        if self._state == "disabled":
            self.state("disabled")

        # 🔑 REGISTER LIFECYCLE HANDSHAKE HOOK: Pushes notifications up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring active or desaturated elements follow theme shifts fluidly."""
        if hasattr(super(), "_set_appearance_mode"):
            try: super()._set_appearance_mode(mode_string)
            except Exception: pass
        self._update_current_visual_state()

    def _update_current_visual_state(self):
        """Helper to catch theme broadcasts and refresh internal components seamlessly."""
        self._process_live_theme_repaint()
    def _process_live_theme_repaint(self):
        """Centralized theme-repaint pipeline resolving aesthetic look parameters."""
        theme = self._local_defaults
        btn_txt = self.btn_text if self.btn_text is not None else ("Browse Folders..." if self.type == "directory" else "Browse Files...")

        current_state = getattr(self, "_state", "normal")
        if current_state == "disabled":
            d_map = self._custom_disabled_map
            entry_bg = d_map.get("entry_fg", theme.get("entry_fg"))
            entry_border = d_map.get("entry_border_color", theme.get("entry_border_color"))
            entry_text = d_map.get("entry_text_color", theme.get("entry_text_color"))
            btn_bg = d_map.get("btn_fg", theme.get("btn_fg"))
            btn_border = d_map.get("btn_border_color", theme.get("btn_border_color"))
            btn_text = d_map.get("btn_text_color", theme.get("btn_text_color"))
            btn_hover = btn_bg
        else:
            entry_bg = theme.get("entry_fg")
            entry_border = theme.get("entry_border_color")
            entry_text = theme.get("entry_text_color")
            btn_bg = theme.get("btn_fg")
            btn_border = theme.get("btn_border_color")
            btn_text = theme.get("btn_text_color")
            btn_hover = theme.get("btn_hover")

        if hasattr(self, "entry") and self.entry.winfo_exists():
            self.entry.configure(
                font=theme.get("entry_font"),
                fg_color=self._resolve_color(entry_bg),
                border_color=self._resolve_color(entry_border),
                text_color=self._resolve_color(entry_text)
            )

        if hasattr(self, "btn") and self.btn.winfo_exists():
            self.btn.configure(
                text=btn_txt,
                font=theme.get("btn_font"),
                fg_color=self._resolve_color(btn_bg),
                hover_color=self._resolve_color(btn_hover),
                text_color=self._resolve_color(btn_text),
                border_color=self._resolve_color(btn_border)
            )

    def configure(self, *args, **kwargs):
        """Extended configure to handle Pygubu queries and dynamic look modifications."""
        if args and len(args) == 1:
            pname = args
            if pname == "state": return ("state", "state", "state", "normal", getattr(self, "_state", "normal"))
            if pname == "type": return ("type", "type", "type", "directory", self.type)
            if pname == "justify": return ("justify", "justify", "justify", "left", self.justify)
            if pname == "btn_text": return ("btn_text", "btn_text", "btn_text", "", str(self.btn_text) if self.btn_text else "")
            if pname == "title": return ("title", "title", "title", "Select Path", self.title)
            if pname == "entry_height": return ("entry_height", "entry_height", "entry_height", "32", self.entry_height)
            if pname == "btn_width": return ("btn_width", "btn_width", "btn_width", "110", self.btn_width)
            if pname == "btn_height": return ("btn_height", "btn_height", "btn_height", "32", self.btn_height)
            return super().configure(*args, **kwargs)

        if args and isinstance(args, dict): kwargs = args | kwargs

        if "btn_text" in kwargs: self.btn_text = str(kwargs.pop("btn_text")) if kwargs["btn_text"] is not None else None
        if "type" in kwargs: self.type = str(kwargs.pop("type")).lower()
        if "title" in kwargs: self.title = str(kwargs.pop("title"))

        if "justify" in kwargs:
            self.justify = str(kwargs.pop("justify")).lower()
            if self.justify not in ("left", "right", "center"): self.justify = "left"
            if hasattr(self, "entry"):
                self.entry.configure(justify=self.justify)
                self.set(self.entry.get())

        if "entry_height" in kwargs:
            self.entry_height = int(kwargs.pop("entry_height"))
            if hasattr(self, "entry"):
                self.entry.configure(height=self.entry_height)
                self.entry.grid_configure(pady=max(0, (self.cget("height") - self.entry_height) // 2))

        if "btn_width" in kwargs:
            self.btn_width = int(kwargs.pop("btn_width"))
            if hasattr(self, "btn"): self.btn.configure(width=self.btn_width)

        if "btn_height" in kwargs:
            self.btn_height = int(kwargs.pop("btn_height"))
            if hasattr(self, "btn"):
                self.btn.configure(height=self.btn_height)
                self.btn.grid_configure(pady=max(0, (self.cget("height") - self.btn_height) // 2))

        if "browser_width" in kwargs: self.browser_width = int(kwargs.pop("browser_width"))
        if "browser_height" in kwargs: self.browser_height = int(kwargs.pop("browser_height"))
        if "command" in kwargs: self.command = kwargs.pop("command")

        if "width" in kwargs: super().configure(width=int(kwargs.pop("width")))
        if "height" in kwargs:
            h_val = int(kwargs.pop("height"))
            super().configure(height=h_val)
            if hasattr(self, "entry"):
                te = min(self.entry_height, h_val)
                self.entry.configure(height=te)
                self.entry.grid_configure(pady=max(0, (h_val - te) // 2))
            if hasattr(self, "btn"):
                tb = min(self.btn_height, h_val)
                self.btn.configure(height=tb)
                self.btn.grid_configure(pady=max(0, (h_val - tb) // 2))

        if "state" in kwargs: self.state(kwargs.pop("state"))

        if hasattr(self, "final_kw"):
            for custom_key in ["type", "justify", "btn_text", "title", "entry_height", "btn_width", "btn_height", "browser_width", "browser_height"]:
                self.final_kw.pop(custom_key, None)

        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        kwargs.pop("defaultextension", None)
        kwargs.pop("entry_width", None)
        kwargs.pop("initialdir", None)
        kwargs.pop("initialfile", None)
        kwargs.pop("filetypes", None)

        self._process_live_theme_repaint()
        if kwargs: return super().configure(**kwargs)
        return None

    config = configure
    def _launch_browser(self):
        """Launches the theme-compliant popup modal browser window without layout stutters."""
        popup = ctk.CTkToplevel(self.winfo_toplevel())
        popup.withdraw()

        final_title = self.title
        if self.type == "file" and self.filetypes:
            formatted_exts = [f"*{ext}" for ext in self.filetypes] if isinstance(self.filetypes, list) else [f"*{self.filetypes}"]
            final_title = f"{self.title} ({', '.join(formatted_exts)})"

        popup.title(final_title)
        popup.geometry(f"{self.browser_width}x{self.browser_height}")
        popup.resizable(False, False)
        popup.transient(self.winfo_toplevel())
        popup.grab_set()

        popup.columnconfigure(0, weight=1)
        popup.rowconfigure(0, weight=1)

        entry_val = self.entry.get().strip()
        seed_dir, seed_file = self.initialdir, self.initialfile

        if entry_val: entry_val = os.path.normpath(os.path.expanduser(entry_val))
        if entry_val and os.path.exists(entry_val):
            if os.path.isdir(entry_val): seed_dir, seed_file = entry_val, None
            else: seed_dir, seed_file = os.path.dirname(entry_val), entry_val

        explorer = sCTkFileExplorer(
            popup, type=self.type, filetypes=self.filetypes, initialdir=seed_dir, initialfile=seed_file,
            width=self.browser_width - 25, height=self.browser_height - 60,
            command=lambda p: self.set(p),
            double_click_command=lambda *args: (self.set(args[-1]), popup.grab_release(), popup.destroy())
        )
        explorer.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        from sCTkFrame import sCTkFrame
        from sCTkButtonPrimary import sCTkButtonPrimary
        from sCTkButtonSecondary import sCTkButtonSecondary

        bottom_bar = sCTkFrame(popup, fg_color="transparent")
        bottom_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        def submit():
            chosen = explorer.selected_path.get()
            if self.type == "file" and os.path.isdir(chosen): return
            self.set(chosen)
            close()

        def close():
            popup.grab_release()
            popup.destroy()

        sCTkButtonSecondary(bottom_bar, text="Cancel", fg_color="transparent", border_width=2, command=close).pack(side="left")
        sCTkButtonPrimary(bottom_bar, text="Select", command=submit).pack(side="right")

        popup.update_idletasks()
        width, height = self.browser_width, self.browser_height
        parent = self.winfo_toplevel()
        if parent and hasattr(parent, "winfo_x"):
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        else:
            x = (popup.winfo_screenwidth() // 2) - (width // 2)
            y = (popup.winfo_screenheight() // 2) - (height // 2)

        popup.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
        popup.deiconify()

    def set(self, path_string: str):
        """Forces fully absolute tilde user expansion when paths are applied via button selections."""
        self.entry.configure(state="normal")
        self.entry.delete(0, tk.END)
        expanded_path = os.path.normpath(os.path.abspath(os.path.expanduser(str(path_string))))
        self.entry.insert(0, expanded_path)
        if self.justify == "right": self.entry.xview_moveto(1.0)
        else: self.entry.xview_moveto(0.0)
        if getattr(self, "_state", "normal") == "disabled": self.entry.configure(state="disabled")
        if self.command and callable(self.command):
            try: self.command(expanded_path)
            except TypeError: self.command()

    def get(self) -> str: return self.entry.get()
    def get_state(self) -> str: return self.state()
    def state(self, mode: str = None) -> str:
        if mode is None: return str(getattr(self, "_state", "normal")).lower()
        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._state = "normal"
            if hasattr(self, "entry"): self.entry.configure(state="normal")
            if hasattr(self, "btn"): self.btn.configure(state="normal")
            self._process_live_theme_repaint()
        elif mode == "disabled":
            self._state = "disabled"
            if hasattr(self, "entry"): self.entry.configure(state="disabled")
            if hasattr(self, "btn"): self.btn.configure(state="disabled")
            self._process_live_theme_repaint()
        return self._state
