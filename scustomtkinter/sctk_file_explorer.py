#!/usr/bin/python3
"""
sCTkFileExplorer - Piece 1 of 3

A theme-compliant, highly configurable custom file explorer wrapper component.
Inherits cleanly and directly from ctk.CTkFrame to preserve native features.
"""
import os
import sys
import platform
import time
import ast
import tkinter as tk
import tkinter.ttk as ttk

import customtkinter as ctk
from .themeable_widget import ThemeableWidget

from typing import Literal, Optional, Union, Tuple

from .sctk_button_primary import sCTkButtonPrimary
from .sctk_buttons_econdary import sCTkButtonSecondary
from .sctk_label_secondary import sCTkLabelSecondary
from .sctk_entry_primary import sCTkEntryPrimary

class sCTkFileExplorer(ctk.CTkFrame, ThemeableWidget):
    _MANAGED_PROPERTIES = frozenset({"initialdir", "initialfile", "type", "title", "filetypes", "defaultextension"})

    def __init__(self,
                 master: any,
                 type: Literal["file", "directory"] = "directory",
                 filetypes: list[str] = None,
                 initialdir: str = None,
                 initialfile: str = None,
                 command: Optional[callable] = None,
                 double_click_command: Optional[callable] = None,
                 width: int = 400,
                 height: int = 300,
                 corner_radius: Optional[Union[int, str]] = None,
                 border_width: Optional[Union[int, str]] = None,
                 bg_color: Union[str, Tuple[str, str]] = "transparent",
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 border_color: Optional[Union[str, Tuple[str, str]]] = None,
                 background_corner_colors: Union[Tuple[Union[str, Tuple[str, str]]], None] = None,
                 overwrite_preferred_drawing_method: Union[str, None] = None,
                 **kwargs):

        kwargs.pop("initialdir", None)
        kwargs.pop("initialfile", None)
        kwargs.pop("type", None)
        kwargs.pop("filetypes", None)
        kwargs.pop("defaultextension", None)
        kwargs.pop("title", None)

        self._initial_state_seed = str(kwargs.pop("state", "normal")).lower()

        ThemeableWidget.__init__(self, kwargs)

        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        super().__init__(master, width=width, height=height, corner_radius=corner_radius,
                         border_width=border_width, bg_color=bg_color, fg_color=fg_color,
                         border_color=border_color, background_corner_colors=background_corner_colors,
                         overwrite_preferred_drawing_method=overwrite_preferred_drawing_method, **kwargs)

        self._state = "normal" if self._initial_state_seed not in ("normal", "disabled") else self._initial_state_seed
        self.response_type = type.lower()
        self.change_path = True
        self.item_labels = {}
        self.command = command
        self.double_click_command = double_click_command
        self._last_double_click_time = 0.0

        self._desired_width = width
        self._desired_height = height

        self.filetypes = []
        if filetypes:
            if self.response_type != "file":
                raise ValueError("Cannot provide 'filetypes' filters when widget mode is 'directory'.")
            if isinstance(filetypes, str):
                cleaned_str = filetypes.strip()
                if not (cleaned_str.startswith("[") and cleaned_str.endswith("]")):
                    raise ValueError(f"Malformed filetypes sequence parsed: '{filetypes}'.")
                try: processed_types = ast.literal_eval(cleaned_str)
                except Exception as err: raise ValueError(f"Malformed syntax evaluating filetypes configuration: {err}")
            else: processed_types = filetypes

            if not isinstance(processed_types, list):
                raise ValueError(f"Invalid filetypes configuration format context: {type(processed_types)}.")
            for f in processed_types:
                clean_f = str(f).lower().replace("*", "").strip()
                if clean_f:
                    if not clean_f.startswith("."): clean_f = "." + clean_f
                    self.filetypes.append(clean_f)
        else:
            self.filetypes = None
        raw_file = os.path.expanduser(str(initialfile)) if initialfile else None
        raw_dir = os.path.expanduser(str(initialdir)) if initialdir else None

        if self.response_type == "directory" and raw_file:
            raw_dir = os.path.dirname(raw_file)
            raw_file = None

        if raw_dir is not None:
            init_p = raw_dir
        elif raw_file is not None:
            init_p = os.path.dirname(raw_file)
        else:
            init_p = os.getcwd()

        self.path_to_show = ctk.StringVar(self, value=os.path.normpath(os.path.abspath(init_p)))
        self.selected_path = ctk.StringVar(self,
                                           value=os.path.normpath(os.path.abspath(raw_file if raw_file else init_p)))

        self.folder_icon = "📁 "
        self.file_icon = "📄 "

        self.top_frame = ctk.CTkFrame(self, width=self._desired_width, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.top_frame.columnconfigure(1, weight=1)

        self.back_button = sCTkButtonPrimary(self.top_frame, text="▲ Up", width=45)
        self.back_button.grid(row=0, column=0, padx=(0, 5), sticky="nw")

        self.path_entry = sCTkEntryPrimary(self.top_frame, textvariable=self.selected_path)
        self.path_entry.grid(row=0, column=1, sticky="ew")

        self.main_container = ctk.CTkFrame(self, width=self._desired_width, height=self._desired_height - 60)
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(0, weight=1)

        self.canvas = ctk.CTkCanvas(self.main_container, highlightthickness=0, width=self._desired_width - 30,
                                    height=self._desired_height - 70)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.explorer_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.explorer_frame.columnconfigure(0, weight=1)

        self.y_scrollbar = ctk.CTkScrollbar(self.main_container, command=self.canvas.yview)
        self.y_scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.y_scrollbar.set)

        self.canvas.create_window((0, 0), window=self.explorer_frame, anchor="nw", tags="inner_window")

        self.after(10, self._finalize_split_bindings)
        self._process_live_theme_repaint()

        # 🔑 REGISTER LIFECYCLE HANDSHAKE HOOK: Maps registration signals back up to Pygubu windows cleanly
        self._finalize_themeable_lifecycle()

    def _set_appearance_mode(self, mode_string):
        """🔑 TRANSPARENCY CRASH PROTECTED CORE FIXED: Intercepts look sweeps and forces valid hex strings."""
        super()._set_appearance_mode(mode_string)
        if hasattr(self, "canvas") and self.canvas.winfo_exists():
            canvas_bg_raw = self.cget("fg_color")
            if canvas_bg_raw == "transparent" or canvas_bg_raw is None:
                canvas_bg_raw = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]

            resolved_hex = self._resolve_color(canvas_bg_raw)
            if resolved_hex == "transparent":
                resolved_hex = "#1C1C1C" if str(ctk.get_appearance_mode()).lower() == "dark" else "#F3F4F6"

            self.canvas.configure(bg=resolved_hex)
            if hasattr(self, "path_to_show"): self._fill_explorer()

    def _process_live_theme_repaint(self):
        theme, d_map = self._local_defaults, self._custom_disabled_map
        current_state = getattr(self, "_state", "normal")

        if current_state == "disabled":
            btn_fg = d_map.get("btn_fg", theme.get("btn_fg"))
            btn_border = d_map.get("btn_border_color", theme.get("btn_border_color"))
            btn_text = d_map.get("btn_text_color", theme.get("btn_text_color"))
            btn_hover, entry_fg = btn_fg, d_map.get("entry_fg", theme.get("entry_fg"))
            entry_border = d_map.get("entry_border_color", theme.get("entry_border_color"))
            entry_text = d_map.get("entry_text_color", theme.get("entry_text_color"))
            sb_btn_color, sb_command = d_map.get("button_color", ("#CBD5E1", "#334155")), None
        else:
            btn_fg, btn_border = theme.get("btn_fg"), theme.get("btn_border_color")
            btn_text, btn_hover = theme.get("btn_text_color"), theme.get("btn_hover")
            entry_fg, entry_border = theme.get("entry_fg"), theme.get("entry_border_color")
            entry_text = theme.get("entry_text_color")
            sb_btn_color = theme.get("button_color", ctk.ThemeManager.theme["CTkScrollbar"]["button_color"])
            sb_command = self.canvas.yview

        canvas_bg_raw = self.cget("fg_color")
        if canvas_bg_raw == "transparent" or canvas_bg_raw is None:
            canvas_bg_raw = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]

        resolved_hex = self._resolve_color(canvas_bg_raw)
        if resolved_hex == "transparent":
            resolved_hex = "#1C1C1C" if str(ctk.get_appearance_mode()).lower() == "dark" else "#F3F4F6"
        self.canvas.configure(bg=resolved_hex)

        if hasattr(self, "back_button") and self.back_button.winfo_exists():
            self.back_button.configure(state=current_state, font=theme.get("btn_font"),
                                       fg_color=self._resolve_color(btn_fg), hover_color=self._resolve_color(btn_hover),
                                       text_color=self._resolve_color(btn_text),
                                       border_color=self._resolve_color(btn_border))
        if hasattr(self, "path_entry") and self.path_entry.winfo_exists():
            self.path_entry.configure(state=current_state, font=theme.get("entry_font"),
                                      fg_color=self._resolve_color(entry_fg),
                                      border_color=self._resolve_color(entry_border),
                                      text_color=self._resolve_color(entry_text))
        if hasattr(self, "y_scrollbar") and self.y_scrollbar.winfo_exists():
            self.y_scrollbar.configure(command=sb_command, button_color=self._resolve_color(sb_btn_color),
                                       button_hover_color=self._resolve_color(sb_btn_color))
        if hasattr(self, "path_to_show"): self._fill_explorer()

    def _configure_frame(self, event=None):
        self.after(10, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def _user_path_changed(self, *args):
        if not self.change_path: return
        target = self.selected_path.get()
        if os.path.isdir(target):
            self.path_to_show.set(target)
            self._fill_explorer()

    def _on_entry_return(self):
        target = self.path_entry.get().strip()
        if os.path.exists(target) and os.path.isdir(target):
            self.path_to_show.set(target)
            self._fill_explorer()

    def _empty_explorer(self):
        for widget in self.explorer_frame.winfo_children(): widget.destroy()
        self.item_labels.clear()

    def _mousewheel(self, event):
        d = int(-1 * event.delta) if platform.system() == "Darwin" else int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(d, "units")

    def _move_back(self):
        p = os.path.dirname(self.path_to_show.get())
        if p != self.path_to_show.get():
            self.path_to_show.set(p)
            self.change_path = False
            self.selected_path.set(p)
            self.change_path = True
            self._fill_explorer()

    def _finalize_split_bindings(self):
        if hasattr(self, "back_button"): self.back_button.configure(command=self._move_back)
        if hasattr(self, "path_entry"): self.path_entry.bind("<Return>", lambda e: self._on_entry_return())
        if hasattr(self, "selected_path"): self.selected_path.trace_add("write", self._user_path_changed)
        if hasattr(self, "explorer_frame"): self.explorer_frame.bind("<Configure>", self._configure_frame)
        if hasattr(self, "canvas"):
            self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig("inner_window", width=e.width))
            self.canvas.bind_all("<MouseWheel>", self._mousewheel)
            self.bind("<Visibility>", lambda e: self._process_live_theme_repaint())
        self._fill_explorer()
    def configure(self, *args, **kwargs):
        if args and len(args) == 1:
            pname = args
            if pname == "state": return ("state", "state", "state", "normal", getattr(self, "_state", "normal"))
            if pname == "type": return ("type", "type", "type", "directory", self.response_type)
            if pname == "initialdir": return ("initialdir", "initialdir", "initialdir", "", self.path_to_show.get())
            if pname == "initialfile": return ("initialfile", "initialfile", "initialfile", "", self.selected_path.get())
            if pname == "filetypes": return ("filetypes", "filetypes", "filetypes", "", str(self.filetypes) if self.filetypes else "")
            if pname == "double_click_command": return ("double_click_command", "double_click_command", "double_click_command", "", str(self.double_click_command))
            return super().configure(*args, **kwargs)

        if args and isinstance(args, dict): kwargs = args | kwargs
        if "state" in kwargs:
            self._state = str(kwargs.pop("state")).lower()
            if self._state not in ("normal", "disabled"): self._state = "normal"
        if "type" in kwargs:
            self.response_type = str(kwargs.pop("type")).lower()
            if self.response_type not in ("file", "directory"): self.response_type = "directory"
        if "filetypes" in kwargs:
            ft_val = kwargs.pop("filetypes")
            if ft_val:
                raw_types = ast.literal_eval(ft_val.strip()) if isinstance(ft_val, str) else ft_val
                self.filetypes = []
                for f in raw_types:
                    clean_f = str(f).lower().replace("*", "").strip()
                    if clean_f:
                        if not clean_f.startswith("."): clean_f = "." + clean_f
                        self.filetypes.append(clean_f)
            else: self.filetypes = None

        if "width" in kwargs:
            self._desired_width = int(kwargs.pop("width"))
            kwargs["width"] = self._desired_width
            if hasattr(self, "top_frame"): self.top_frame.configure(width=self._desired_width)
            if hasattr(self, "main_container"): self.main_container.configure(width=self._desired_width)
            if hasattr(self, "canvas"): self.canvas.configure(width=self._desired_width - 30)
        if "height" in kwargs:
            self._desired_height = int(kwargs.pop("height"))
            kwargs["height"] = self._desired_height
            if hasattr(self, "main_container"): self.main_container.configure(height=self._desired_height - 60)
            if hasattr(self, "canvas"): self.canvas.configure(height=self._desired_height - 70)

        if "command" in kwargs: self.command = kwargs.pop("command")
        if "double_click_command" in kwargs: self.double_click_command = kwargs.pop("double_click_command")
        if "initialdir" in kwargs:
            r = kwargs.pop("initialdir")
            if r:
                init_dir = os.path.normpath(os.path.abspath(os.path.expanduser(str(r))))
                self.path_to_show.set(init_dir)
                self.change_path = False
                self.selected_path.set(init_dir)
                self.change_path = True
        if "initialfile" in kwargs:
            r = kwargs.pop("initialfile")
            if r: self.selected_path.set(os.path.normpath(os.path.abspath(os.path.expanduser(str(r)))))

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)
        if hasattr(self, "final_kw"):
            for custom_key in ["type", "filetypes", "double_click_command", "initialdir", "initialfile", "state"]:
                self.final_kw.pop(custom_key, None)

        self._process_live_theme_repaint()
        return super().configure(**kwargs)

    config = configure
    def get_state(self) -> str: return self.state()
    def state(self, mode: str = None) -> str:
        if mode is None: return str(getattr(self, "_state", "normal")).lower()
        mode = mode.lower()
        if mode in ("normal", "enabled", "active"): self._state = "normal"
        elif mode == "disabled": self._state = "disabled"
        self._process_live_theme_repaint()
        return self._state

    def set_mode(self, type_str: Literal["file", "directory"]):
        target_mode = str(type_str).lower().strip()
        if target_mode in ("file", "directory"):
            self.response_type = target_mode
            if self.response_type == "directory": self.filetypes = None
            self._process_live_theme_repaint()

    def set_initial_dir(self, path_str: str):
        if path_str:
            clean_dir = os.path.normpath(os.path.abspath(os.path.expanduser(str(path_str))))
            if os.path.isdir(clean_dir):
                self.path_to_show.set(clean_dir)
                self.change_path = False
                self.selected_path.set(clean_dir)
                self.change_path = True
                self._process_live_theme_repaint()

    def set_initial_file(self, path_str: str):
        if path_str:
            self.selected_path.set(os.path.normpath(os.path.abspath(os.path.expanduser(str(path_str)))))
            self._process_live_theme_repaint()

    def set_filetypes(self, filetypes_data: Union[list, str]):
        if self.response_type != "file": raise ValueError("Cannot apply 'filetypes' when mode is 'directory'.")
        if not filetypes_data:
            self.filetypes = None
            self._process_live_theme_repaint()
            return
        if isinstance(filetypes_data, str):
            s = filetypes_data.strip().strip("[]\"'")
            raw_types = [x.strip() for x in s.split(",") if x.strip()] if s else []
        else: raw_types = filetypes_data

        self.filetypes = []
        for f in raw_types:
            clean_f = str(f).lower().replace("*", "").strip()
            if clean_f:
                if not clean_f.startswith("."): clean_f = "." + clean_f
                self.filetypes.append(clean_f)
        self._process_live_theme_repaint()
    def _fill_explorer(self):
        self._empty_explorer()
        current_dir = self.path_to_show.get()
        current_selected = os.path.normpath(os.path.abspath(self.selected_path.get()))

        if self.filetypes and self.response_type != "file":
            sCTkLabelSecondary(self.explorer_frame, text="⚠️ UI Mismatch: Cannot filter extension when mode is 'directory'.", text_color="red").grid(row=0, column=0, padx=10, pady=10, sticky="w")
            return
        try: items = sorted(os.listdir(current_dir))
        except Exception:
            sCTkLabelSecondary(self.explorer_frame, text="⚠️ Directory unreadable or permission denied", text_color="red").grid(row=0, column=0, padx=10, pady=10, sticky="w")
            return

        row_idx = 0
        current_state = getattr(self, "_state", "normal")
        theme, d_map = self._local_defaults, self._custom_disabled_map

        for item in items:
            if item.startswith('.'): continue
            full_path = os.path.normpath(os.path.join(current_dir, item))
            is_dir = os.path.isdir(full_path)

            is_valid_row = True
            if self.response_type == "directory" and not is_dir: is_valid_row = False
            elif self.response_type == "file" and not is_dir and self.filetypes:
                _, ext = os.path.splitext(item.lower())
                if ext not in self.filetypes: is_valid_row = False

            icon = self.folder_icon if is_dir else self.file_icon
            is_currently_highlighted = (full_path == current_selected)

            if current_state == "disabled":
                txt_color, row_widget_state, btn_bg = self._resolve_color(d_map.get("row_dimmed_text", "gray50")), "disabled", "transparent"
            elif is_valid_row:
                txt_color, row_widget_state = self._resolve_color(theme.get("row_active_text", ctk.ThemeManager.theme["CTkLabel"]["text_color"])), "normal"
                btn_bg = self._resolve_color(theme.get("btn_fg")) if is_currently_highlighted else "transparent"
            else:
                txt_color, row_widget_state, btn_bg = self._resolve_color(theme.get("row_dimmed_text", "gray50")), "disabled", "transparent"

            item_btn = sCTkButtonSecondary(self.explorer_frame, text=f"{icon}{item}", anchor="w", fg_color=btn_bg, text_color=txt_color, state=row_widget_state, hover_color=self._resolve_color(theme.get("btn_hover")), command=lambda p=full_path: self._on_item_clicked(p))
            item_btn.grid(row=row_idx, column=0, sticky="ew", padx=2, pady=1)

            if is_valid_row and current_state != "disabled":
                item_btn.bind("<Double-Button-1>", lambda e, p=full_path: self._on_item_double_clicked(p))
                self.item_labels[full_path] = item_btn
            row_idx += 1
        self.canvas.yview_moveto(0)

    def _on_item_clicked(self, target_path):
        now = time.time()
        if (now - self._last_double_click_time) < 0.3: return
        target_path = os.path.normpath(target_path)
        if self.response_type == "directory" and os.path.isfile(target_path): target_path = os.path.dirname(target_path)

        self.change_path = False
        self.selected_path.set(target_path)
        self.change_path = True

        for path, btn in self.item_labels.items():
            if path == target_path: btn.configure(fg_color=self._resolve_color(self._local_defaults.get("btn_fg")))
            else: btn.configure(fg_color="transparent")
        if self.command and callable(self.command): self.command(self)

    def _on_item_double_clicked(self, target_path):
        target_path = os.path.normpath(target_path)
        if os.path.isdir(target_path):
            self.path_to_show.set(target_path)
            self.change_path = False
            self.selected_path.set(target_path)
            self.change_path = True
            self._fill_explorer()
        else:
            if self.response_type == "directory": target_path = os.path.dirname(target_path)
            now = time.time()
            if (now - self._last_double_click_time) < 0.3: return
            self._last_double_click_time = now
            if self.double_click_command and callable(self.double_click_command): self.double_click_command(self, target_path)

