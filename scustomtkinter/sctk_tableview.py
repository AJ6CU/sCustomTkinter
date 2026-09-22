#!/usr/bin/python3
"""
sCTkTableview

A theme-compliant custom data grid component wrapper.
Inherits cleanly from sCTkScrollableFrame and ThemeableWidget to manage
dense telemetry spreadsheets safely with full live theme repaint loops.
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget, parse_list_property

from typing import List, Optional, Callable, Any, Literal

from .sctk_scrollable_frame import sCTkScrollableFrame
from .sctk_label_primary import sCTkLabelPrimary
from .sctk_label_secondary import sCTkLabelSecondary
from .sctk_entry_primary import sCTkEntryPrimary
from .sctk_optionmenu_primary import sCTkOptionMenuPrimary



class sCTkTableview(sCTkScrollableFrame, ThemeableWidget):
    def __init__(self, master: any, columns: Optional[Any] = None, width: int = 500, height: int = 300,
                 grid_mode: Literal["zebra", "grid", "none"] = "zebra", header_line_width: int = 2,
                 outline_width: float = 1.0, outline_radius: int = 4, state: Literal["normal", "disabled"] = "normal",
                 num_columns: int = 3, num_rows: int = 1, show_headers: Any = True,
                 cell_bg_color: Optional[Any] = None, cell_alt_bg_color: Optional[Any] = None,
                 editable_columns: Optional[Any] = None,
                 edit_trigger: Literal["double", "select"] = "double",
                 select_rows: Any = False, column_choices: Optional[dict] = None,
                 *args, **kwargs):

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
                    f"'{(getattr(self, '_THEME_BLOCK_NAME', None) or self.__class__.__name__)}' theme block is missing '{required_key}' "
                    f"at the top level of sCTkThemes.json."
                )
            if self._custom_disabled_map.get(required_key) is None:
                raise KeyError(
                    f"'{(getattr(self, '_THEME_BLOCK_NAME', None) or self.__class__.__name__)}' theme block is missing '{required_key}' in disabled_map."
                )

        # Fonts only need to exist at the top level.
        for required_key in ("header_font", "cell_font"):
            if self._switch_theme_profile.get(required_key) is None:
                raise KeyError(
                    f"'{(getattr(self, '_THEME_BLOCK_NAME', None) or self.__class__.__name__)}' theme block is missing '{required_key}' "
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
                    f"'{(getattr(self, '_THEME_BLOCK_NAME', None) or self.__class__.__name__)}': '{ctor_key}' must be provided either as a "
                    f"constructor argument or in the theme's top-level block."
                )
            if self._custom_disabled_map.get(ctor_key) is None:
                raise KeyError(f"'{(getattr(self, '_THEME_BLOCK_NAME', None) or self.__class__.__name__)}' theme block is missing '{ctor_key}' in disabled_map.")

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

        # OPTIONAL, unlike the colours above: a theme written before rows
        # could be selected has no such key, and requiring it would break
        # every one of them. Absent, the header colour stands in -- still a
        # theme value, never a hardcoded one.
        self._selected_bg = (self._switch_theme_profile.get("cell_selected_color")
                             or self._header_bg)

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
        # COLUMNS SETS THE COLUMN COUNT, as the documentation always said. It
        # did not: only the Designer's builder and configure() applied it, so
        # a table built in code with five column names showed three -- the
        # default count -- and silently dropped every column after the third,
        # headers, cells and set_column_properties() alike. Worked out here,
        # before the per-column widths below are sized from it.
        if isinstance(columns, str):
            columns = parse_list_property(columns)
        if columns and isinstance(columns, (list, tuple)):
            self._num_columns = len(columns)
        self._num_rows = int(num_rows)
        self._show_headers = str(show_headers).replace("'", "").replace('"', "").strip().lower() in ("true", "1", "yes")

        # 🔑 FIXED LIFECYCLE REORDER: Pre-hydrate layout property variables completely
        # BEFORE running super().__init__ to eliminate asynchronous AttributeError gaps!
        self._column_widths = [120] * self._num_columns
        self._column_anchors = ["center"] * self._num_columns
        self._click_callback, self._edit_callback, self._validation_callback = None, None, None

        # --- editing and selection --------------------------------------
        # All three default to what the table always did -- every column
        # editable, by double-click, and no row highlighted -- so an existing
        # table is unchanged unless it asks for something else.
        #
        # editable_columns: None for all, else the column indices that may be
        #   edited. The rest are read-only, which a column such as a row
        #   number or a computed note needs.
        # edit_trigger: "double" opens the editor on a double-click, as ever.
        #   "select" opens it on a click in the row that is ALREADY selected
        #   -- the spreadsheet and file-manager convention -- which frees the
        #   double-click to mean something else; see bind_activate_callback.
        # select_rows: highlight the row last clicked. Implied by "select",
        #   which cannot work without a selection.
        self._editable_columns = self._parse_columns(editable_columns)
        self._edit_trigger = ("select" if str(edit_trigger).strip().lower() == "select"
                              else "double")
        self._select_rows = (self._edit_trigger == "select"
                             or str(select_rows).strip().lower() in ("true", "1", "yes"))
        self._selected_row = None
        self._activate_callback = None
        self._cell_editable_callback = None
        # column index -> the values it may hold. Such a column is edited with
        # a dropdown rather than typed: a fixed set of choices typed by hand
        # invites typos, and each needs a rule for what counts as valid.
        self._column_choices = {int(c): list(v) for c, v in (column_choices or {}).items()}
        self._validation_with_row = False
        self._editor = None
        self._pending_edit = None
        self._data_matrix, self._cell_widgets, self._header_widgets = [], [], []

        self.columns_list = (list(columns) if (columns and isinstance(columns, (list, tuple)))
                             else [""] * self._num_columns)

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
        # The height asked for is a CEILING, not a suggestion: see load_dataset.
        self._max_height = int(height)
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
        # An editor open over the old cells would be left floating over the
        # new ones. Cancelled, not saved: the data it was editing is being
        # replaced.
        self._cancel_pending_edit()
        self._close_editor(save=False)
        for cell in [c for row in self._cell_widgets for c in row]: cell.destroy()
        self._data_matrix, self._cell_widgets = [list(row) for row in dataset], []
        super().configure(width=0, height=0)

        row_offset = 1 if (self._show_headers and self._grid_mode == "none" and self._header_line_width == 0) else (2 if self._show_headers else 0)
        is_none_mode = (self._grid_mode == "none")
        gap_size, edge_size = (0 if is_none_mode else 1), (0 if is_none_mode else 2)

        for r_idx, r_data in enumerate(self._data_matrix):
            if len(r_data) < self._num_columns: r_data += [""] * (self._num_columns - len(r_data)); self._data_matrix[r_idx] = r_data
            elif len(r_data) > self._num_columns: r_data = r_data[:self._num_columns]; self._data_matrix[r_idx] = r_data

            current_row_bg = self._row_bg(r_idx)
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

                cell_label.bind("<Button-1>", lambda e, r=r_idx, c=c_idx: self._on_cell_click(r, c))
                cell_label.bind("<Double-Button-1>", lambda e, r=r_idx, c=c_idx: self._on_cell_double(r, c))
                r_cells.append(cell_label)
            self._cell_widgets.append(r_cells)

        # A selection beyond the new rows is dropped; one within them stays.
        if self._selected_row is not None and self._selected_row >= len(self._data_matrix):
            self._selected_row = None

        for hw in self._header_widgets:
            try: hw.lift()
            except Exception: pass
        if hasattr(self, "header_separator") and self.header_separator:
            try: self.header_separator.lift()
            except Exception: pass

        self.update_idletasks()
        # Fits its WIDTH to the columns, and its height to the rows -- but no
        # taller than the height it was given. Beyond that it scrolls, which
        # is what a scrolling frame is for. It used to fit the height to every
        # row, so a long table asked for enough room never to scroll and
        # pushed whatever else shared its parent out of the window.
        super().configure(width=self.table_outline_frame.winfo_reqwidth() + 14,
                          height=min(self.table_outline_frame.winfo_reqheight() + 18,
                                     self._max_height))

    # ------------------------------------------------------------------
    # Clicks
    # ------------------------------------------------------------------
    # How long a click on the selected row waits before opening the editor.
    # A double-click begins with an ordinary click, so without this pause a
    # double-click on the selected row would open the editor AND activate the
    # row. The click waits; a double-click arriving in the meantime cancels
    # it. The same pause file managers use before renaming.
    EDIT_DELAY_MS = 500

    def _on_cell_click(self, r_idx: int, c_idx: int):
        if self._state != "normal":
            return
        # A text editor closes itself when it loses focus; a dropdown does
        # not, so a click on any cell closes one left open -- keeping nothing
        # unless a value was chosen.
        if self._editor and getattr(self._editor[0], "_is_choice", False):
            self._close_editor(save=True)
        was_selected = (self._selected_row == r_idx)
        if self._select_rows:
            self._set_selection(r_idx)
        if self._click_callback:
            self._click_callback(r_idx, self._data_matrix[r_idx])
        if (self._edit_trigger == "select" and was_selected
                and self._is_editable(r_idx, c_idx)):
            self._cancel_pending_edit()
            self._pending_edit = self.after(
                self.EDIT_DELAY_MS, lambda: self._begin_pending_edit(r_idx, c_idx))

    def _on_cell_double(self, r_idx: int, c_idx: int):
        if self._state != "normal":
            return
        self._cancel_pending_edit()
        if self._edit_trigger == "double" and self._is_editable(r_idx, c_idx):
            self._spawn_editor(r_idx, c_idx)
        elif self._activate_callback:
            self._activate_callback(r_idx, self._data_matrix[r_idx])

    def _begin_pending_edit(self, r_idx: int, c_idx: int):
        self._pending_edit = None
        if self._state == "normal" and r_idx < len(self._data_matrix):
            self._spawn_editor(r_idx, c_idx)

    def _cancel_pending_edit(self):
        if self._pending_edit is not None:
            try:
                self.after_cancel(self._pending_edit)
            except Exception:
                pass
            self._pending_edit = None

    def _is_editable(self, r_idx: int, c_idx: int) -> bool:
        """
        The column must be editable, and -- if a cell check is bound -- so
        must this particular cell. A cell that may not be edited never opens
        an editor, rather than opening one and then throwing the typing away.
        """
        if self._editable_columns is not None and c_idx not in self._editable_columns:
            return False
        if self._cell_editable_callback is not None:
            return bool(self._cell_editable_callback(r_idx, c_idx))
        return True

    @staticmethod
    def _parse_columns(value):
        """None for every column, else a set of column indices."""
        if value is None:
            return None
        if isinstance(value, str):
            value = parse_list_property(value) if value.strip() else []
        return {int(v) for v in value}

    # ------------------------------------------------------------------
    # Editing a cell
    # ------------------------------------------------------------------
    def _spawn_editor(self, r_idx: int, c_idx: int):
        # One editor at a time. A second one is only opened by a deliberate
        # edit elsewhere, so the first is kept, as a spreadsheet would.
        self._close_editor(save=True)
        row_offset = 1 if (self._show_headers and self._grid_mode == "none" and self._header_line_width == 0) else (
            2 if self._show_headers else 0)
        choices = self._column_choices.get(c_idx)
        if choices:
            self._spawn_choice_editor(r_idx, c_idx, choices, row_offset)
            return

        # sCTkEntryPrimary, not a bare CTkEntry, so the editor follows the
        # theme like every other control in the library.
        entry = sCTkEntryPrimary(self.table_outline_frame, font=self._cell_font,
                                 width=self._column_widths[c_idx], height=24,
                                 corner_radius=0)
        entry.insert(0, str(self._data_matrix[r_idx][c_idx]))
        entry.grid(row=r_idx + row_offset, column=c_idx, sticky="ew", padx=1, pady=1)
        entry.focus_set()
        entry.select_range(0, "end")
        entry.bind("<Return>", lambda e: self._save_edit(r_idx, c_idx, entry))
        entry.bind("<FocusOut>", lambda e: self._save_edit(r_idx, c_idx, entry))
        # ESCAPE CANCELS. Without it, the only way out of an editor opened by
        # mistake was to retype the old value -- Return and a click away both
        # save.
        entry.bind("<Escape>", lambda e: self._cancel_editor(entry))
        self._editor = (entry, r_idx, c_idx)

    def _spawn_choice_editor(self, r_idx, c_idx, choices, row_offset):
        """
        A dropdown over the cell, open straight away.

        ONLY A CHOICE IS KEPT. The menu has to show something when it opens,
        and for a cell holding none of the choices -- empty, say -- that is
        the first one. Closing it without choosing must not store that first
        choice as though it had been picked, so the value is saved from the
        menu's command, and nowhere else.
        """
        current = str(self._data_matrix[r_idx][c_idx])
        menu = sCTkOptionMenuPrimary(self.table_outline_frame, values=list(choices),
                                     width=self._column_widths[c_idx], height=24)
        menu.set(current if current in choices else choices[0])
        menu._is_choice = True
        menu.configure(command=lambda value: self._choose(r_idx, c_idx, menu))
        menu.grid(row=r_idx + row_offset, column=c_idx, sticky="ew", padx=1, pady=1)
        menu.bind("<Escape>", lambda e: self._cancel_editor(menu))
        self._editor = (menu, r_idx, c_idx)
        # Open the list at once, so choosing takes one click, like typing.
        # _open_dropdown_menu is CTkOptionMenu's own; guarded in case a
        # future version renames it, when the menu simply opens on a click.
        opener = getattr(menu, "_open_dropdown_menu", None)
        if callable(opener):
            self.after_idle(lambda: menu.winfo_exists() and opener())

    def _choose(self, r_idx, c_idx, menu):
        """A value was chosen from a dropdown editor: keep it."""
        menu._chosen = True
        self._save_edit(r_idx, c_idx, menu)

    def _cancel_editor(self, entry):
        entry._cancelled = True
        if self._editor and self._editor[0] is entry:
            self._editor = None
        if entry.winfo_exists():
            entry.destroy()

    def _close_editor(self, save: bool):
        """Closes the open editor, if there is one, saving or not."""
        if not self._editor:
            return
        entry, r_idx, c_idx = self._editor
        # A dropdown is kept only if something was chosen from it.
        if getattr(entry, "_is_choice", False) and not getattr(entry, "_chosen", False):
            save = False
        if save:
            self._save_edit(r_idx, c_idx, entry)
        else:
            self._cancel_editor(entry)

    def _save_edit(self, r_idx: int, c_idx: int, entry):
        # Cancelled by Escape: the FocusOut that follows the editor's removal
        # must not save what was cancelled.
        if getattr(entry, "_cancelled", False) or not entry.winfo_exists(): return
        val = entry.get()
        entry._cancelled = True           # nothing after this saves it twice
        if self._editor and self._editor[0] is entry:
            self._editor = None
        entry.destroy()
        if r_idx >= len(self._data_matrix): return

        # VALIDATION. The callback may answer:
        #   a string -- accept, but store THIS instead (a value tidied up,
        #               such as a frequency typed "14.074" shown as
        #               "14.074.000")
        #   truthy   -- accept as typed
        #   falsy    -- reject; the cell keeps its old value
        # A plain True/False callback behaves exactly as it always did.
        if self._validation_callback:
            verdict = (self._validation_callback(r_idx, c_idx, val) if self._validation_with_row
                       else self._validation_callback(c_idx, val))
            if isinstance(verdict, str):
                val = verdict
            elif not verdict:
                val = self._data_matrix[r_idx][c_idx]

        # FIX: an earlier version compared self._data_matrix[r_idx][c_idx]
        # against val AFTER the assignment below had already written val into
        # that exact cell -- a tautology that was always true, so the edit
        # callback fired on every save regardless of whether anything had
        # actually changed. The previous value has to be captured BEFORE the
        # write. A rejected edit reverts val to the old value above, so the
        # callback correctly stays silent for it too.
        old_val = self._data_matrix[r_idx][c_idx]

        self._data_matrix[r_idx][c_idx] = val
        self._cell_widgets[r_idx][c_idx].configure(
            text=self._display(val, self._column_anchors[c_idx]))
        if self._edit_callback and old_val != val: self._edit_callback(r_idx, c_idx, val)

    @staticmethod
    def _display(val, anchor):
        """A cell's text, padded away from the edge it is anchored to."""
        return ("    " + str(val) if anchor == "w"
                else (str(val) + "    " if anchor == "e" else str(val)))

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------
    def _row_bg(self, r_idx: int):
        if self._select_rows and r_idx == self._selected_row:
            return self._selected_bg
        return self._cell_alt_bg if (self._grid_mode == "zebra" and r_idx % 2 != 0) else self._cell_bg

    def _paint_row(self, r_idx):
        if r_idx is None or not 0 <= r_idx < len(self._cell_widgets):
            return
        bg = self._row_bg(r_idx)
        for cell in self._cell_widgets[r_idx]:
            cell.configure(fg_color=bg)

    def _set_selection(self, r_idx):
        previous, self._selected_row = self._selected_row, r_idx
        if previous != r_idx:
            self._paint_row(previous)
        self._paint_row(r_idx)

    def select_row(self, r_idx: Optional[int]):
        """
        Selects a row from code -- or clears the selection, given None.

        Does NOT call the selection callback: selecting from code is the
        application saying what it already knows. The same rule as set() on
        every other widget in the library.
        """
        if r_idx is not None and not 0 <= r_idx < len(self._data_matrix):
            r_idx = None
        self._set_selection(r_idx)

    def get_selected_row(self) -> Optional[int]:
        """The selected row's index, or None."""
        return self._selected_row

    def clear_selection(self):
        self.select_row(None)

    def set_row(self, r_idx: int, values: List[Any]):
        """
        Replaces one row's values in place, without rebuilding the table.

        load_dataset() destroys and recreates every cell. For a table that
        changes often -- one row at a time, as data arrives -- that is a
        great deal of work and a visible flicker; this updates only the text.
        """
        if not 0 <= r_idx < len(self._data_matrix):
            return
        values = list(values)[:self._num_columns]
        values += [""] * (self._num_columns - len(values))
        self._data_matrix[r_idx] = values
        for c_idx, val in enumerate(values):
            anchor = self._column_anchors[c_idx] if c_idx < len(self._column_anchors) else "center"
            self._cell_widgets[r_idx][c_idx].configure(text=self._display(val, anchor))

    # Native constructor defaults, for the single-argument query below.
    # Anything not listed reports its current value as its default.
    _NATIVE_QUERY_DEFAULTS = {"width": 500, "height": 300}

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
            # FIX: this used to be `return super().configure(require_redraw)`.
            #
            # The native configure() is declared
            # configure(self, require_redraw=False, **kwargs), so the property
            # NAME was passed as require_redraw and the call returned None.
            # Pygubu's _get_default_value() expects a five-element tuple, got
            # None, and handed that None back to _set_property() -- where
            # CustomTkinter raised "float() argument must be a string or a real
            # number, not 'NoneType'".
            #
            # Reached whenever a field is blanked in the Designer inspector,
            # which calls configure(name) to read the property's default.
            #
            # A proper Tkinter-style tuple is returned instead, built from
            # cget() so the reported current value is real. Properties with no
            # known native default report their current value as the default,
            # making a blank a no-op rather than a jump to a guessed value.
            try:
                _current = self.cget(require_redraw)
            except Exception:
                _current = None
            # FIX: the default came from _NATIVE_QUERY_DEFAULTS or, failing
            # that, from cget() -- the CURRENT value. So clearing a themed
            # property in the Designer reported whatever override was in place
            # as its own default and put it straight back.
            #
            # The THEME's value is the right answer, taken from an untouched
            # copy so a runtime override cannot corrupt it -- see
            # ThemeableWidget._theme_default(). The native table still wins
            # where it has an entry, for properties the theme says nothing
            # about.
            _default = self._NATIVE_QUERY_DEFAULTS.get(require_redraw)
            if _default is None:
                _default = self._theme_default(require_redraw)
            if _default is None:
                _default = _current
            return (require_redraw, require_redraw, require_redraw,
                    self._query_value(_default, require_redraw),
                    self._query_value(_current, require_redraw))

        if isinstance(require_redraw, dict): kwargs.update(require_redraw); require_redraw = False

        # Runtime overrides have to reach the map a repaint reads, or the
        # repaint puts the theme value straight back -- see
        # ThemeableWidget._record_theme_overrides(). Placed after the dict form
        # is merged, so a value passed that way is recorded too.
        self._record_theme_overrides(kwargs)

        rebuild_layout = False

        # A new height is a new ceiling -- and is still passed on below.
        if "height" in kwargs:
            self._max_height = int(kwargs["height"])

        if "editable_columns" in kwargs:
            self._editable_columns = self._parse_columns(kwargs.pop("editable_columns"))
        if "edit_trigger" in kwargs:
            self._edit_trigger = ("select" if str(kwargs.pop("edit_trigger")).strip().lower()
                                  == "select" else "double")
            self._select_rows = self._select_rows or self._edit_trigger == "select"
        if "select_rows" in kwargs:
            self._select_rows = (self._edit_trigger == "select"
                                 or str(kwargs.pop("select_rows")).strip().lower()
                                 in ("true", "1", "yes"))
            for r in range(len(self._cell_widgets)):
                self._paint_row(r)

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
                    parsed = parse_list_property(v)
                    self.columns_list = parsed if parsed else [""] * self._num_columns
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
        # The selection colour follows the state too -- optional in both maps,
        # falling back to the header colour, as at construction.
        self._selected_bg = ((dis_map if is_disabled else normal_map).get("cell_selected_color")
                             or self._header_bg)

        if hasattr(self, "table_outline_frame") and self.table_outline_frame:
            self.table_outline_frame.configure(fg_color=self._grid_line_color, border_color=self._grid_line_color)

        for header_cell in self._header_widgets:
            header_cell.configure(fg_color=self._header_bg, text_color=self._header_fg)

        for r_idx, row in enumerate(self._cell_widgets):
            row_bg = self._row_bg(r_idx)
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

    def set_column_choices(self, column_index: int, choices: Optional[List[str]]):
        """
        Makes a column edited by choosing from a list rather than typing --
        or, given None, typed again.
        """
        if choices:
            self._column_choices[int(column_index)] = list(choices)
        else:
            self._column_choices.pop(int(column_index), None)

    def bind_cell_editable_callback(self, callback: Callable):
        """
        callback(row_index, column_index) -> bool: whether one cell may be
        edited, for the cases a column rule cannot express -- a column
        editable in some rows and not others. Consulted after
        editable_columns: a column left out there stays read-only whatever
        this says. None removes the check.
        """
        self._cell_editable_callback = callback

    def bind_activate_callback(self, callback: Callable):
        """
        callback(row_index, row_values), on a double-click that does not open
        an editor -- every double-click when edit_trigger is "select", or one
        on a read-only column otherwise. The natural "open this row" action.
        """
        self._activate_callback = callback

    def bind_validation_callback(self, callback: Callable, with_row: bool = False):
        """
        callback(column_index, value) -- or, with with_row=True,
        callback(row_index, column_index, value) -- checks an edit before it
        is stored. Return a string to store that instead, anything truthy to
        accept the edit as typed, or anything falsy to reject it.

        with_row exists because some checks depend on the row: which rows
        may carry a value at all, say. It is a separate switch rather than a
        change of signature, so existing two-argument callbacks go on working.
        """
        self._validation_callback = callback
        self._validation_with_row = bool(with_row)