#!/usr/bin/python3
"""
sCTkFileExplorer

A theme-compliant, highly configurable custom file explorer wrapper component.
Inherits cleanly and directly from ctk.CTkFrame to preserve native features.
"""
import os
import time
import ast
import tkinter as tk
import tkinter.ttk as ttk

import customtkinter as ctk
from .themeable_widget import ThemeableWidget
from .sctk_scroll_mixin import ScrollBindingMixin

from typing import Literal, Optional, Union, Tuple

from .sctk_button_primary import sCTkButtonPrimary
from .sctk_button_secondary import sCTkButtonSecondary
from .sctk_label_secondary import sCTkLabelSecondary
from .sctk_entry_primary import sCTkEntryPrimary

class sCTkFileExplorer(ctk.CTkFrame, ScrollBindingMixin, ThemeableWidget):
    # NOTE: an earlier version declared a _MANAGED_PROPERTIES frozenset here,
    # never referenced anywhere else in this file -- dead code, removed. Same
    # vestigial pattern found and removed elsewhere in this project.

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

        # Scroll state and activation, owned by ScrollBindingMixin.
        # _init_scroll_state() must run before any binding happens.
        #
        # FIX: this was previously deferred with self.after(10, ...) -- an
        # arbitrary delay chosen to let the widget hierarchy settle. The mixin
        # activates via after_idle() instead, which fires when Tk is actually
        # idle rather than after a guessed interval, plus <Map> on this widget
        # and a debounced <Configure> rebind. The delay is retained below only
        # for the NON-scroll wiring _finalize_split_bindings() also does.
        self._init_scroll_state()
        self._install_scroll_activation(content_widget=self.explorer_frame)

        self.after(10, self._finalize_split_bindings)
        self._process_live_theme_repaint()

        # 🔑 REGISTER LIFECYCLE HANDSHAKE HOOK: Maps registration signals back up to Pygubu windows cleanly
        self._finalize_themeable_lifecycle()

    def _resolve_canvas_bg_color(self):
        """
        Determines what color to give the internal raw Canvas's background,
        since a raw Tkinter Canvas cannot render CTk's "transparent"
        pseudo-value at all.

        FIX: an earlier version reached into ctk.ThemeManager.theme["CTkFrame"]
        -- CustomTkinter's own native theme registry -- as an intermediate
        fallback before reaching the hardcoded literal below. Every other
        widget in this project exclusively uses sCTkThemes.json or a
        documented literal; this was the only place reaching into native
        CTk's own theme as an additional fallback layer. Removed -- goes
        directly to the documented hardcoded pair instead, matching the same
        precedent already established in sCTkFrameLabeledPrimary's
        _hide_internal_scrollbars(): this isn't a "theme is incomplete"
        situation (this widget's own fg_color being "transparent" is a
        legitimate, common choice), it's "a raw canvas needs an actual
        renderable color, and transparent isn't one" -- a different problem
        with a different, accepted solution.
        """
        canvas_bg_raw = self.cget("fg_color")
        if canvas_bg_raw == "transparent" or canvas_bg_raw is None:
            return "#1C1C1C" if str(ctk.get_appearance_mode()).lower() == "dark" else "#F3F4F6"
        resolved_hex = self._resolve_color(canvas_bg_raw)
        if resolved_hex == "transparent":
            return "#1C1C1C" if str(ctk.get_appearance_mode()).lower() == "dark" else "#F3F4F6"
        return resolved_hex

    def _set_appearance_mode(self, mode_string):
        """Intercepts appearance-mode changes and forces a valid hex string
        onto the internal raw Canvas, which cannot render CTk's "transparent"."""
        super()._set_appearance_mode(mode_string)
        if hasattr(self, "canvas") and self.canvas.winfo_exists():
            self.canvas.configure(bg=self._resolve_canvas_bg_color())
            if hasattr(self, "path_to_show"): self._fill_explorer()

    def _process_live_theme_repaint(self):
        theme, d_map = self._local_defaults, self._custom_disabled_map
        current_state = getattr(self, "_state", "normal")

        # FIX: an earlier version used hardcoded fallback literals for
        # button_color (the scrollbar's color) -- and, in the enabled branch,
        # reached into ctk.ThemeManager.theme["CTkScrollbar"] (native CTk's
        # own theme registry) as an additional fallback layer, the only place
        # in this project besides the canvas-background case above doing
        # that. Both replaced with hard-fail validation, matching the
        # principle established for sCTkSwitch, the label family, and
        # sCTkTableview elsewhere in this project.
        if theme.get("button_color") is None:
            raise KeyError(f"'{self.__class__.__name__}' theme block is missing 'button_color' at the top level.")
        if d_map.get("button_color") is None:
            raise KeyError(f"'{self.__class__.__name__}' theme block is missing 'button_color' in disabled_map.")

        if current_state == "disabled":
            btn_fg = d_map.get("btn_fg", theme.get("btn_fg"))
            btn_border = d_map.get("btn_border_color", theme.get("btn_border_color"))
            btn_text = d_map.get("btn_text_color", theme.get("btn_text_color"))
            btn_hover, entry_fg = btn_fg, d_map.get("entry_fg", theme.get("entry_fg"))
            entry_border = d_map.get("entry_border_color", theme.get("entry_border_color"))
            entry_text = d_map.get("entry_text_color", theme.get("entry_text_color"))
            sb_btn_color, sb_command = d_map.get("button_color"), None
        else:
            btn_fg, btn_border = theme.get("btn_fg"), theme.get("btn_border_color")
            btn_text, btn_hover = theme.get("btn_text_color"), theme.get("btn_hover")
            entry_fg, entry_border = theme.get("entry_fg"), theme.get("entry_border_color")
            entry_text = theme.get("entry_text_color")
            sb_btn_color = theme.get("button_color")
            sb_command = self.canvas.yview

        self.canvas.configure(bg=self._resolve_canvas_bg_color())

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
        self.after(10, self._update_scrollregion)

    def _update_scrollregion(self):
        """
        Sets the canvas scroll region to the content bounds, expanded to at
        least the visible canvas height.

        FIX: this previously set scrollregion straight from bbox("all"). When
        the files don't fill the frame that region is SHORTER than the visible
        canvas, and Tk will still scroll within it -- so dragging the
        scrollbar pushed the rows down to the bottom of the frame with empty
        space above them, instead of doing nothing. Growing the region to the
        canvas height when content is shorter leaves yview with nowhere to go,
        which is the intended "content fits, so scrolling does nothing"
        behavior.
        """
        try:
            if not self.canvas.winfo_exists():
                return
            bounds = self.canvas.bbox("all")
            if not bounds:
                return
            x0, y0, x1, y1 = bounds
            visible_height = self.canvas.winfo_height()
            if (y1 - y0) < visible_height:
                y1 = y0 + visible_height
            self.canvas.configure(scrollregion=(x0, y0, x1, y1))
        except Exception:
            pass

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

    def _move_back(self):
        p = os.path.dirname(self.path_to_show.get())
        if p != self.path_to_show.get():
            self.path_to_show.set(p)
            self.change_path = False
            self.selected_path.set(p)
            self.change_path = True
            self._fill_explorer()

    # ------------------------------------------------------------------
    # ScrollBindingMixin contract
    # ------------------------------------------------------------------
    def _scroll_target(self):
        """
        The widget to scroll. Unlike sCTkScrollableFrame -- which is wrapped
        by a native CTkScrollableFrame owning the canvas, and so has to look
        it up via winfo_parent() -- this widget builds its own canvas
        explicitly, so no lookup is needed.

        Returns:
            self.canvas, or None if it doesn't exist yet.
        """
        canvas = getattr(self, "canvas", None)
        try:
            if canvas is not None and canvas.winfo_exists():
                return canvas
        except Exception:
            pass
        return None

    def _scroll_layers(self):
        """
        Every widget that should respond to a scroll event over this explorer:
        the widget itself, its canvas, the scrollbar, and the full row tree.

        FIX: an earlier version walked only ONE level into explorer_frame
        (`for child in self.explorer_frame.winfo_children()`), so anything
        nested inside a row -- its label, its icon -- was never bound, and
        the wheel did nothing while the pointer was over those. The mixin's
        collector recurses to full depth, stopping only at nested
        CTkScrollableFrame boundaries.

        Returns:
            An ordered, deduplicated list of widgets.
        """
        layers = [self]

        canvas = self._scroll_target()
        if canvas is not None:
            layers.append(canvas)

        # The scrollbar is a sibling of the canvas inside main_container, not
        # a descendant of explorer_frame, so the content walk below would
        # never reach it -- without this the wheel does nothing while the
        # pointer is over the scrollbar itself.
        bar = getattr(self, "y_scrollbar", None)
        if bar is not None:
            self._collect_scroll_descendants(bar, layers)

        frame = getattr(self, "explorer_frame", None)
        if frame is not None:
            try:
                if frame.winfo_exists():
                    self._collect_scroll_descendants(frame, layers)
            except Exception:
                pass

        return layers

    def _finalize_split_bindings(self):
        if hasattr(self, "back_button"): self.back_button.configure(command=self._move_back)
        if hasattr(self, "path_entry"): self.path_entry.bind("<Return>", lambda e: self._on_entry_return())
        if hasattr(self, "selected_path"): self.selected_path.trace_add("write", self._user_path_changed)
        if hasattr(self, "explorer_frame"): self.explorer_frame.bind("<Configure>", self._configure_frame)
        if hasattr(self, "canvas"):
            self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig("inner_window", width=e.width))
            self._activate_scroll_bindings()
            self.bind("<Visibility>", lambda e: self._process_live_theme_repaint())
        self._fill_explorer()
    def configure(self, *args, **kwargs):
        if args and len(args) == 1:
            # FIX: was `pname = args`, leaving pname as a TUPLE -- every
            # comparison below failed, so all six single-argument queries
            # were dead and fell through to super(). Pygubu could not read
            # any of them.
            pname = args[0]
            if pname == "state": return ("state", "state", "state", "normal", getattr(self, "_state", "normal"))
            if pname == "type": return ("type", "type", "type", "directory", self.response_type)
            if pname == "initialdir": return ("initialdir", "initialdir", "initialdir", "", self.path_to_show.get())
            if pname == "initialfile": return ("initialfile", "initialfile", "initialfile", "", self.selected_path.get())
            if pname == "filetypes": return ("filetypes", "filetypes", "filetypes", "", str(self.filetypes) if self.filetypes else "")
            if pname == "double_click_command": return ("double_click_command", "double_click_command", "double_click_command", "", str(self.double_click_command))
            return super().configure(*args, **kwargs)

        # FIX: was `if args and isinstance(args, dict)`. args is ALWAYS a
        # tuple, so this never fired and the dict-merge form of configure()
        # was dead. Same tautology fixed across the batch-one widgets.
        if len(args) == 1 and isinstance(args[0], dict): kwargs = {**args[0], **kwargs}
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
            self._activate_scroll_bindings()
            return
        try: items = sorted(os.listdir(current_dir))
        except Exception:
            sCTkLabelSecondary(self.explorer_frame, text="⚠️ Directory unreadable or permission denied", text_color="red").grid(row=0, column=0, padx=10, pady=10, sticky="w")
            self._activate_scroll_bindings()
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

            # FIX: an earlier version used the hardcoded literal "gray50" for
            # row_dimmed_text (in both branches below), and reached into
            # ctk.ThemeManager.theme["CTkLabel"] (native CTk's own theme
            # registry) as a fallback for row_active_text. Both replaced with
            # hard-fail validation on first use, matching the principle
            # established for sCTkSwitch, the label family, and
            # sCTkTableview elsewhere in this project.
            if current_state == "disabled":
                if d_map.get("row_dimmed_text") is None:
                    raise KeyError(f"'{self.__class__.__name__}' theme block is missing 'row_dimmed_text' in disabled_map.")
                txt_color, row_widget_state, btn_bg = self._resolve_color(d_map.get("row_dimmed_text")), "disabled", "transparent"
            elif is_valid_row:
                if theme.get("row_active_text") is None:
                    raise KeyError(f"'{self.__class__.__name__}' theme block is missing 'row_active_text' at the top level.")
                txt_color, row_widget_state = self._resolve_color(theme.get("row_active_text")), "normal"
                btn_bg = self._resolve_color(theme.get("btn_fg")) if is_currently_highlighted else "transparent"
            else:
                if theme.get("row_dimmed_text") is None:
                    raise KeyError(f"'{self.__class__.__name__}' theme block is missing 'row_dimmed_text' at the top level.")
                txt_color, row_widget_state, btn_bg = self._resolve_color(theme.get("row_dimmed_text")), "disabled", "transparent"

            item_btn = sCTkButtonSecondary(self.explorer_frame, text=f"{icon}{item}", anchor="w", fg_color=btn_bg, text_color=txt_color, state=row_widget_state, hover_color=self._resolve_color(theme.get("btn_hover")), command=lambda p=full_path: self._on_item_clicked(p))
            item_btn.grid(row=row_idx, column=0, sticky="ew", padx=2, pady=1)

            if is_valid_row and current_state != "disabled":
                item_btn.bind("<Double-Button-1>", lambda e, p=full_path: self._on_item_double_clicked(p))
                self.item_labels[full_path] = item_btn
            row_idx += 1
        self.canvas.yview_moveto(0)
        # FIX: navigating to a new folder replaces every row widget in
        # explorer_frame -- re-bind scroll events so the newly-created rows
        # get their own handlers too, not just whatever existed at the last
        # binding pass. See _toggle_scroll_bindings()'s docstring.
        self._activate_scroll_bindings()

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
        # FIX: an earlier version called self.command(self) here, passing this
        # FileExplorer widget instance instead of the clicked path. sCTkPathChooser's
        # command=lambda p: self.set(p) expects p to be a path string -- with the
        # old code, a single click would call self.set(<widget instance>), which
        # would then try to treat str(widget) as a filesystem path. Confirmed by
        # the maintainer: command should receive the path, matching what every
        # caller of this widget actually expects. double_click_command is
        # unaffected -- it already correctly passes (self, target_path).
        if self.command and callable(self.command): self.command(target_path)

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