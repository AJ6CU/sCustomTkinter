#!/usr/bin/python3
"""
sCTkTableview

A theme-compliant custom data grid component wrapper.
Inherits cleanly from sCTkScrollableFrame and ThemeableWidget to manage
dense telemetry spreadsheets safely with full live theme repaint loops.
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget

from typing import List, Optional, Callable, Any, Literal

from .sctk_scrollable_frame import sCTkScrollableFrame
from .sctk_label_primary import sCTkLabelPrimary
from .sctk_label_secondary import sCTkLabelSecondary



class sCTkTableview(sCTkScrollableFrame, ThemeableWidget):
    def __init__(self, master: any, columns: Optional[Any] = None, width: int = 500, height: int = 300,
                 grid_mode: Literal["zebra", "grid", "none"] = "zebra", header_line_width: int = 2,
                 outline_width: float = 1.0, outline_radius: int = 4, state: Literal["normal", "disabled"] = "normal",
                 num_columns: int = 3, num_rows: int = 1, show_headers: Any = True,
                 cell_bg_color: Optional[Any] = None, cell_alt_bg_color: Optional[Any] = None, *args, **kwargs):

        # 1. Run shared mixin logic first to parse master themes.json data maps safely
        ThemeableWidget.__init__(self, kwargs)

        # 2. Resolve theme profiles FIRST, before extracting individual
        # values, so required keys can be validated before anything reads
        # them.
        self._switch_theme_profile = dict(self.final_kw)
        # FIX: an earlier version read "disabled_map" out of
        # self._switch_theme_profile (== dict(self.final_kw)), but
        # ThemeableWidget.__init__ deliberately excludes "disabled_map" from
        # final_kw -- this always evaluated to the empty-dict default, meaning
        # EVERY disabled-state color lookup in _apply_state_and_theme_updates()
        # silently fell back to its hardcoded literal instead of the real
        # theme. Confirmed identical bug, same fix, as sCTkSwitch and
        # sCTkSpinbox elsewhere in this project.
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # FIX: an earlier version used .get(key, hardcoded_literal) for every
        # color/font below, both here and in _apply_state_and_theme_updates(),
        # silently substituting a guessed value whenever the real theme was
        # incomplete rather than surfacing the gap. Matches the same hard-fail
        # principle established for sCTkSwitch and the label family elsewhere
        # in this project: required keys must be present in both the
        # top-level theme block and disabled_map, or construction raises
        # immediately with a clear message naming exactly what's missing.
        #
        # Colors need a disabled_map entry too, since they visually change
        # when disabled. Fonts don't -- BUG, confirmed by direct testing: an
        # earlier version of this validation incorrectly bundled
        # header_font/cell_font into this same loop, requiring them in
        # disabled_map too, even though no widget in this project uses a
        # disabled-state font variant (fonts are always top-level-only).
        # Split into two separate loops below to fix this.
        for required_key in ("header_bg_color", "header_text_color",
                              "cell_text_color", "grid_line_color"):
            if self._switch_theme_profile.get(required_key) is None:
                raise KeyError(
                    f"'{self.__class__.__name__}' theme block is missing '{required_key}' "
                    f"at the top level of sCTkThemes.json."
                )
            if self._custom_disabled_map.get(required_key) is None:
                raise KeyError(
                    f"'{self.__class__.__name__}' theme block is missing '{required_key}' in disabled_map."
                )

        # Fonts only need to exist at the top level.
        for required_key in ("header_font", "cell_font"):
            if self._switch_theme_profile.get(required_key) is None:
                raise KeyError(
                    f"'{self.__class__.__name__}' theme block is missing '{required_key}' "
                    f"at the top level of sCTkThemes.json."
                )

        # cell_bg_color/cell_alt_bg_color are different: they have a genuine
        # constructor-kwarg override, so it's not automatically a theme gap
        # if the theme itself doesn't define them -- only a problem if
        # NEITHER the kwarg NOR the theme provides a value. disabled_map is
        # still required either way, since there's no disabled-state kwarg
        # override.
        for ctor_key, ctor_val in (("cell_bg_color", cell_bg_color), ("cell_alt_bg_color", cell_alt_bg_color)):
            if ctor_val is None and self._switch_theme_profile.get(ctor_key) is None:
                raise KeyError(
                    f"'{self.__class__.__name__}': '{ctor_key}' must be provided either as a "
                    f"constructor argument or in the theme's top-level block."
                )
            if self._custom_disabled_map.get(ctor_key) is None:
                raise KeyError(f"'{self.__class__.__name__}' theme block is missing '{ctor_key}' in disabled_map.")

        # 3. Extract theme-driven values -- safe to read directly via .get()
        # now, without a fallback, since the validation above guarantees each
        # key exists.
        self._header_bg = self._switch_theme_profile.get("header_bg_color")
        self._header_fg = self._switch_theme_profile.get("header_text_color")
        self._header_font = self._switch_theme_profile.get("header_font")

        self._cell_bg = cell_bg_color if cell_bg_color is not None else self._switch_theme_profile.get("cell_bg_color")
        self._cell_alt_bg = cell_alt_bg_color if cell_alt_bg_color is not None else self._switch_theme_profile.get("cell_alt_bg_color")
        self._cell_fg = self._switch_theme_profile.get("cell_text_color")
        self._cell_font = self._switch_theme_profile.get("cell_font")
        self._grid_line_color = self._switch_theme_profile.get("grid_line_color")

        # FIX (related bug found while eliminating the fallback above): an
        # earlier version of _apply_state_and_theme_updates() always reverted
        # cell_bg_color/cell_alt_bg_color to the theme's value when
        # transitioning back to "normal", silently discarding a constructor
        # kwarg override (e.g. sCTkTableview(master, cell_bg_color="red"))
        # after a disable/enable cycle. Caching the actually-resolved values
        # here lets that method correctly restore whichever one this
        # constructor call actually resolved to, not just the theme default.
        self._resolved_normal_cell_bg = self._cell_bg
        self._resolved_normal_cell_alt_bg = self._cell_alt_bg

        # 3. Initialize specialized layout tracking fields
        self._grid_mode = str(grid_mode).replace("'", "").replace('"', "").strip().lower()
        self._header_line_width = int(header_line_width) if header_line_width is not None else 2
        self._outline_width = float(outline_width) if outline_width else 1.0
        self._outline_radius = int(outline_radius) if outline_radius else 4
        self._state = state

        self._num_columns = int(num_columns)
        self._num_rows = int(num_rows)
        self._show_headers = str(show_headers).replace("'", "").replace('"', "").strip().lower() in ("true", "1", "yes")

        # 🔑 FIXED LIFECYCLE REORDER: Pre-hydrate layout property variables completely
        # BEFORE running super().__init__ to eliminate asynchronous AttributeError gaps!
        self._column_widths = [120] * self._num_columns
        self._column_anchors = ["center"] * self._num_columns
        self._click_callback, self._edit_callback, self._validation_callback = None, None, None
        self._data_matrix, self._cell_widgets, self._header_widgets = [], [], []

        if isinstance(columns, str):
            clean_str = columns.replace("'", "").replace('"', "").strip()
            columns = [c.strip() for c in clean_str.split(',') if c.strip()]
        self.columns_list = list(columns) if (columns and isinstance(columns, list)) else [""] * self._num_columns

        # FIX: an earlier version temporarily overwrote self.__class__.__name__
        # to "sCTkScrollableFrame" here, then restored it immediately after --
        # a workaround for two problems that are now solved properly upstream:
        # (1) sCTkScrollableFrame.__init__'s own internal ThemeableWidget.__init__
        # call would otherwise run a second time on this instance, using
        # self.__class__.__name__ (always "sCTkTableview", regardless of which
        # class's code is executing) to look up the wrong theme block and
        # overwrite this widget's correctly-built final_kw -- now prevented by
        # ThemeableWidget's own run-once guard (see themeable_widget.py). (2)
        # even with final_kw correctly preserved, sCTkScrollableFrame's own
        # super().__init__() call would forward Tableview-specific keys like
        # header_bg_color to the native CTkScrollableFrame constructor, which
        # doesn't recognize them and has no **kwargs catch-all to fall back on
        # -- now prevented by sCTkScrollableFrame's own whitelist filtering of
        # its inbound kwargs before that call. Confirmed safe to call directly.
        super().__init__(master=master, width=width, height=height, *args)

        super().configure(border_width=0, corner_radius=0, fg_color=self._cell_bg)
        self.table_outline_frame = ctk.CTkFrame(self, fg_color=self._grid_line_color, border_width=self._outline_width, border_color=self._grid_line_color, corner_radius=self._outline_radius)
        self.table_outline_frame.grid(row=0, column=0, sticky="nw", padx=1, pady=1)

        self._create_header_bar()
        self.load_dataset([[""] * self._num_columns for _ in range(self._num_rows)])
        self.configure(state=state)
        self._finalize_themeable_lifecycle()

    def _create_header_bar(self):
        for w in self._header_widgets:
            try: w.destroy()
            except Exception: pass
        self._header_widgets = []
        if hasattr(self, "header_separator") and self.header_separator:
            try: self.header_separator.destroy()
            except Exception: pass
        self.header_separator = None

        if not self._show_headers: return
        is_none_mode = (self._grid_mode == "none")
        gap_size, edge_size = (0 if is_none_mode else 1), (0 if is_none_mode else 2)

        if self._header_line_width > 0:
            self.header_separator = ctk.CTkFrame(self.table_outline_frame, height=self._header_line_width, fg_color=self._grid_line_color, corner_radius=0)
            self.header_separator.grid(row=1, column=0, columnspan=self._num_columns, sticky="ew", padx=(edge_size, edge_size + gap_size), pady=(0, edge_size))

        render_labels = list(self.columns_list)
        if len(render_labels) < self._num_columns: render_labels += [""] * (self._num_columns - len(render_labels))
        elif len(render_labels) > self._num_columns: render_labels = render_labels[:self._num_columns]

        for col_idx, col_name in enumerate(render_labels):
            w_limit = self._column_widths[col_idx] if col_idx < len(self._column_widths) else 120
            header_cell = sCTkLabelPrimary(self.table_outline_frame, text=col_name, font=self._header_font, text_color=self._header_fg, fg_color=self._header_bg, corner_radius=0, height=28, width=w_limit)
            left_pad, right_pad = (edge_size if col_idx == 0 else gap_size), (edge_size if col_idx == len(render_labels) - 1 else 0)
            header_cell.grid(row=0, column=col_idx, sticky="ew", padx=(left_pad, right_pad), pady=(edge_size, 0))
            self.table_outline_frame.grid_columnconfigure(col_idx, weight=0)
            try: header_cell.lift()
            except Exception: pass
            self._header_widgets.append(header_cell)
    def load_dataset(self, dataset: List[List[Any]]):
        for cell in [c for row in self._cell_widgets for c in row]: cell.destroy()
        self._data_matrix, self._cell_widgets = [list(row) for row in dataset], []
        super().configure(width=0, height=0)

        row_offset = 1 if (self._show_headers and self._grid_mode == "none" and self._header_line_width == 0) else (2 if self._show_headers else 0)
        is_none_mode = (self._grid_mode == "none")
        gap_size, edge_size = (0 if is_none_mode else 1), (0 if is_none_mode else 2)

        for r_idx, r_data in enumerate(self._data_matrix):
            if len(r_data) < self._num_columns: r_data += [""] * (self._num_columns - len(r_data)); self._data_matrix[r_idx] = r_data
            elif len(r_data) > self._num_columns: r_data = r_data[:self._num_columns]; self._data_matrix[r_idx] = r_data

            current_row_bg = self._cell_alt_bg if (self._grid_mode == "zebra" and r_idx % 2 != 0) else self._cell_bg
            r_cells = []
            for c_idx in range(self._num_columns):
                val = r_data[c_idx]
                w_limit = self._column_widths[c_idx] if c_idx < len(self._column_widths) else 120
                txt_anchor = self._column_anchors[c_idx] if c_idx < len(self._column_anchors) else "center"
                display_val = "    " + str(val) if txt_anchor == "w" else (str(val) + "    " if txt_anchor == "e" else str(val))

                cell_label = sCTkLabelSecondary(self.table_outline_frame, text=display_val, font=self._cell_font, text_color=self._cell_fg, width=w_limit, height=26, corner_radius=0, anchor=txt_anchor, fg_color="transparent")
                cell_label.configure(fg_color=current_row_bg)

                if self._state == "disabled": cell_label.configure(state="disabled")

                top_pad, bot_pad = (edge_size if r_idx == 0 else gap_size), (edge_size if r_idx == len(self._data_matrix) - 1 else 0)
                left_pad, right_pad = (edge_size if c_idx == 0 else gap_size), (edge_size if c_idx == self._num_columns - 1 else 0)
                cell_label.grid(row=r_idx + row_offset, column=c_idx, sticky="ew", padx=(left_pad, right_pad), pady=(top_pad, bot_pad))

                cell_label.bind("<Button-1>", lambda e, r=r_idx: self._click_callback(r, self._data_matrix[r]) if (self._click_callback and self._state == "normal") else None)
                cell_label.bind("<Double-Button-1>", lambda e, r=r_idx, c=c_idx: self._spawn_editor(r, c) if self._state == "normal" else None)
                r_cells.append(cell_label)
            self._cell_widgets.append(r_cells)

        for hw in self._header_widgets:
            try: hw.lift()
            except Exception: pass
        if hasattr(self, "header_separator") and self.header_separator:
            try: self.header_separator.lift()
            except Exception: pass

        self.update_idletasks()
        super().configure(width=self.table_outline_frame.winfo_reqwidth() + 14, height=self.table_outline_frame.winfo_reqheight() + 18)

    def _spawn_editor(self, r_idx: int, c_idx: int):
        row_offset = 1 if (self._show_headers and self._grid_mode == "none" and self._header_line_width == 0) else (
            2 if self._show_headers else 0)
        entry = ctk.CTkEntry(self.table_outline_frame, font=self._cell_font, width=self._column_widths[c_idx],
                             height=24, corner_radius=0)
        entry.insert(0, str(self._data_matrix[r_idx][c_idx]))
        entry.grid(row=r_idx + row_offset, column=c_idx, sticky="ew", padx=1, pady=1)
        entry.focus_set()
        entry.select_range(0, "end")
        entry.bind("<Return>", lambda e: self._save_edit(r_idx, c_idx, entry))
        entry.bind("<FocusOut>", lambda e: self._save_edit(r_idx, c_idx, entry))

    def _save_edit(self, r_idx: int, c_idx: int, entry: ctk.CTkEntry):
        if not entry.winfo_exists(): return
        val = entry.get()
        entry.destroy()
        if self._validation_callback and not self._validation_callback(c_idx, val): val = self._data_matrix[r_idx][
            c_idx]

        # FIX: an earlier version compared self._data_matrix[r_idx][c_idx]
        # against val AFTER the assignment below had already written val into
        # that exact cell -- a tautology that was always true, so the edit
        # callback fired on every save regardless of whether anything had
        # actually changed. The intended behavior is change detection, so the
        # previous value has to be captured BEFORE the write.
        #
        # This also gives correct behavior on a rejected edit for free: the
        # validation check above reverts val to the cell's existing content
        # when the callback rejects it, so old_val == val and the edit
        # callback correctly stays silent.
        old_val = self._data_matrix[r_idx][c_idx]

        self._data_matrix[r_idx][c_idx] = val
        txt_anchor = self._column_anchors[c_idx]
        display_val = "    " + str(val) if txt_anchor == "w" else (str(val) + "    " if txt_anchor == "e" else str(val))
        self._cell_widgets[r_idx][c_idx].configure(text=display_val)
        if self._edit_callback and old_val != val: self._edit_callback(r_idx, c_idx, val)

    def configure(self, require_redraw=False, **kwargs):
        if require_redraw is not None and not kwargs and isinstance(require_redraw, str):
            mapping = {
                "state": ("state", "state", "state", "normal", str(getattr(self, "_state", "normal"))),
                "grid_mode": ("grid_mode", "grid_mode", "grid_mode", "zebra",
                              str(getattr(self, "_grid_mode", "zebra"))),
                "show_headers": ("show_headers", "show_headers", "show_headers", "True",
                                 str(getattr(self, "_show_headers", True)))
            }
            if require_redraw in mapping: return mapping[require_redraw]
            if require_redraw in ["num_columns", "num_rows", "header_line_width"]: return (require_redraw,
                                                                                           require_redraw,
                                                                                           require_redraw, "0",
                                                                                           str(getattr(self,
                                                                                                       f"_{require_redraw}",
                                                                                                       0)))
            # Falls through to sCTkScrollableFrame.configure()'s own
            # single-argument branch, which returns a Tkinter-style 5-tuple for
            # any name it doesn't recognise rather than forwarding the string to
            # native CTkScrollableFrame.configure() -- that signature takes no
            # positional argument and would raise TypeError. Reached from Pygubu
            # when a property is blanked in the inspector.
            return super().configure(require_redraw)

        if isinstance(require_redraw, dict): kwargs.update(require_redraw); require_redraw = False
        rebuild_layout = False

        for k in ["cell_bg_color", "cell_alt_bg_color", "num_columns", "num_rows", "header_line_width", "grid_mode",
                  "show_headers", "outline_width", "outline_radius", "columns"]:
            if k in kwargs:
                v = kwargs.pop(k)
                if k == "cell_bg_color":
                    self._cell_bg = v
                elif k == "cell_alt_bg_color":
                    self._cell_alt_bg = v
                elif k == "num_columns":
                    self._num_columns = int(v)
                elif k == "num_rows":
                    self._num_rows = int(v)
                elif k == "header_line_width":
                    self._header_line_width = int(v)
                elif k == "grid_mode":
                    self._grid_mode = str(v).replace("'", "").replace('"', "").strip().lower()
                elif k == "show_headers":
                    self._show_headers = v if isinstance(v, bool) else (str(v).lower() in ("true", "1", "yes"))
                elif k == "outline_width":
                    self._outline_width = float(v); self.table_outline_frame.configure(border_width=self._outline_width)
                elif k == "outline_radius":
                    self._outline_radius = int(v); self.table_outline_frame.configure(
                        corner_radius=self._outline_radius)
                elif k == "columns":
                    # FIX: `columns` was accepted by __init__ and registered as
                    # a Pygubu Designer property, but configure() never popped
                    # it -- so editing the column list at runtime fell straight
                    # through to native CTkScrollableFrame.configure(), whose
                    # check_kwargs_empty() raised
                    # "['columns'] are not supported arguments". Construction
                    # worked; reconfiguration did not, which is exactly what
                    # the Designer does when the field is edited.
                    #
                    # Accepts a comma-separated string as well as a list, since
                    # __init__ does and Pygubu's property editor supplies a
                    # string.
                    if isinstance(v, str):
                        clean_str = v.replace("'", "").replace('"', "").strip()
                        v = [c.strip() for c in clean_str.split(',') if c.strip()]
                    self.columns_list = list(v) if v else [""] * self._num_columns
                    # Column count follows the labels, matching how the Designer
                    # BO derives num_columns from the columns string.
                    self._num_columns = len(self.columns_list)
                rebuild_layout = True

        if rebuild_layout:
            if len(self._column_widths) < self._num_columns:
                self._column_widths += [120] * (self._num_columns - len(self._column_widths))
                self._column_anchors += ["center"] * (self._num_columns - len(self._column_anchors))
            self._create_header_bar()
            self.load_dataset([[""] * self._num_columns for _ in range(max(self._num_rows, len(self._data_matrix)))])

        self._apply_state_and_theme_updates(kwargs)
        if kwargs: super().configure(**kwargs)

    def _apply_state_and_theme_updates(self, kwargs):
        if "state" not in kwargs: return
        self._state = str(kwargs.pop("state")).lower()
        dis_map = self._custom_disabled_map
        normal_map = self._switch_theme_profile
        is_disabled = self._state == "disabled"

        # FIX: an earlier version repeated the same hardcoded fallback
        # literals here as __init__ (see that method's comments) -- removed
        # now that required keys are validated once, at construction. Also
        # fixes a related bug: cell_bg_color/cell_alt_bg_color now correctly
        # restore whatever this instance actually resolved to when
        # constructed (theme value or constructor kwarg override), instead
        # of always reverting to the theme's value and silently discarding a
        # constructor override on every return to "normal".
        self._header_bg = dis_map.get("header_bg_color") if is_disabled else normal_map.get("header_bg_color")
        self._header_fg = dis_map.get("header_text_color") if is_disabled else normal_map.get("header_text_color")
        self._cell_bg = dis_map.get("cell_bg_color") if is_disabled else self._resolved_normal_cell_bg
        self._cell_alt_bg = dis_map.get("cell_alt_bg_color") if is_disabled else self._resolved_normal_cell_alt_bg
        self._cell_fg = dis_map.get("cell_text_color") if is_disabled else normal_map.get("cell_text_color")
        self._grid_line_color = dis_map.get("grid_line_color") if is_disabled else normal_map.get("grid_line_color")

        if hasattr(self, "table_outline_frame") and self.table_outline_frame:
            self.table_outline_frame.configure(fg_color=self._grid_line_color, border_color=self._grid_line_color)

        for header_cell in self._header_widgets:
            header_cell.configure(fg_color=self._header_bg, text_color=self._header_fg)

        for r_idx, row in enumerate(self._cell_widgets):
            row_bg = self._cell_alt_bg if (self._grid_mode == "zebra" and r_idx % 2 != 0) else self._cell_bg
            for cell in row:
                cell.configure(fg_color=row_bg, text_color=self._cell_fg, state=self._state)

    # 🔑 THE CORE DESIGN PATTERN GATEWAY: Aligns fully with all other repository widgets!
    def state(self, mode: str = None) -> str:
        """Unified state tracker gateway. Acts as getter if mode is None, otherwise configures state."""
        if mode is None:
            return str(getattr(self, "_state", "normal")).lower()
        self.configure(state=mode)
        return mode

    # 🔑 API CONTINUITY PASS-THROUGHS
    def get_state(self) -> str:
        return self.state()

    config = configure

    def get_num_rows(self) -> int:
        return len(self._cell_widgets) if self._cell_widgets else self._num_rows

    def get_num_columns(self) -> int:
        return len(self._cell_widgets) if (self._cell_widgets and self._cell_widgets) else self._num_columns

    def set_column_properties(self, column_index: int, width: int, anchor: Literal["w", "center", "e"] = "center"):
        if 0 <= column_index < len(self._column_widths):
            self._column_widths[column_index], self._column_anchors[column_index] = width, anchor
            if column_index < len(self._header_widgets) and self._show_headers:
                txt = self.columns_list[column_index] if column_index < len(self.columns_list) else ""
                self._header_widgets[column_index].configure(width=width, anchor=anchor,
                                                             text="   " + txt if anchor == "w" else (
                                                                 txt + "   " if anchor == "e" else txt))

    def bind_selection_callback(self, callback: Callable):
        self._click_callback = callback

    def bind_edit_callback(self, callback: Callable):
        self._edit_callback = callback

    def bind_validation_callback(self, callback: Callable):
        self._validation_callback = callback