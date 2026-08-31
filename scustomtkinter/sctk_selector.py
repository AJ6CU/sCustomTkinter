#!/usr/bin/python3
"""
sCTkSelector

An advanced theme-compliant, scrollable option tree selector widget.
Pairs an optional high-contrast search field lane with a dynamic listing frame card
to manage multi-state checkbox row configurations natively.
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget

import ast
from typing import Optional, Union, Tuple

from .sctk_frame import sCTkFrame
from .sctk_checkbox import sCTkCheckBox
from .sctk_entry_primary import sCTkEntryPrimary
from .sctk_scrollable_frame import sCTkScrollableFrame

class sCTkSelector(sCTkFrame, ThemeableWidget):
    def __init__(self, master, items: Optional[list[str]] = None, multiple_choices=True, searchBox=True, **kwargs):
        # 1. SANITIZE RUNTIME ARGUMENTS: Strip unmanaged properties out immediately
        state_init = kwargs.pop("state", "normal")
        pack_prop_init = kwargs.pop("pack_propagate", None)
        grid_prop_init = kwargs.pop("grid_propagate", None)

        # 2. ENFORCE SYSTEM REGISTRY INTERACTION:
        ThemeableWidget.__init__(self, kwargs)

        # 🛠️ THE MUTATION SAFEGUARD DEEP COPY SHIELD:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        fg_color = self._local_defaults.get("fg_color", "transparent")

        # 3. Call the parent sCTkFrame constructor safely
        super().__init__(master, **self.final_kw)

        self._state = "normal"
        self.search_var = ctk.StringVar(self)
        self.search_var.trace_add("write", self._search_modified)

        self.search_bar = None
        self._search_box_visible = bool(searchBox)

        self.checkboxes_frame = sCTkScrollableFrame(self, fg_color=fg_color)
        self.checkboxes_frame.pack(expand=True, fill="both", side="bottom")

        if hasattr(self.checkboxes_frame, "_parent_frame") and self.checkboxes_frame._parent_frame is not None:
            self.checkboxes_frame._parent_frame.pack_propagate(False)
            self.checkboxes_frame._parent_frame.grid_propagate(False)

        self.checkboxes = []
        self.selected_indexes = []
        self.multiple_choices = multiple_choices

        if items is None:
            items = []

        # 4. Route variables into the configure parser loop for execution mapping
        self.configure(
            items=items,
            multiple_choices=multiple_choices,
            searchBox=self._search_box_visible,
            pack_propagate=pack_prop_init,
            grid_propagate=grid_prop_init,
            state=state_init
        )

        # 🔑 REGISTER LIFECYCLE HANDSHAKE HOOK: Pushes notifications up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

    def _selection(self, index: int):
        if index in self.selected_indexes:
            self.selected_indexes.remove(index)
        else:
            if self.multiple_choices:
                self.selected_indexes.append(index)
            else:
                if self.selected_indexes:
                    for i in self.selected_indexes:
                        if i < len(self.checkboxes):
                            self.checkboxes[i].deselect()
                    self.selected_indexes.clear()
                    self.selected_indexes.append(index)
                else:
                    self.selected_indexes.append(index)

    def _reset_scroll(self):
        if hasattr(self.checkboxes_frame, "_parent_canvas") and self.checkboxes_frame._parent_canvas is not None:
            self.checkboxes_frame._parent_canvas.yview_moveto(0)

    def _search_modified(self, *args):
        value = self.search_var.get()
        row = 0
        for x in range(len(self.checkboxes)):
            if self.checkboxes[x].cget("text").startswith(value):
                self.checkboxes[x].grid(row=row, column=0, padx=3, pady=3, sticky="w")
                row += 1
            else:
                self.checkboxes[x].grid_forget()
        self._reset_scroll()

    def get_all_items(self) -> list:
        return [checkbox.cget("text") for checkbox in self.checkboxes]
    def configure(self, cnf=None, **kwargs):
        if cnf is not None and not kwargs and isinstance(cnf, str):
            pname = cnf
            if pname == "state": return ("state", "state", "state", "normal", str(self.state()))
            if pname == "multiple_choices": return ("multiple_choices", "multiple_choices", "multiple_choices", "True", str(self.multiple_choices))
            if pname == "searchBox": return ("searchBox", "searchBox", "searchBox", "True", str(self._search_box_visible))
            if pname == "items":
                current_items = [cb.cget("text") for cb in self.checkboxes] if hasattr(self, "checkboxes") else []
                return ("items", "items", "items", "[]", str(current_items))
            if pname in ["pack_propagate", "grid_propagate"]: return (pname, pname, pname, "None", str(getattr(self, f"_{pname}_val", None)))
            if pname in ["fg_color", "border_color", "text_color"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))
            return super().configure(cnf)

        if isinstance(cnf, dict): kwargs = cnf | kwargs

        if "items" in kwargs:
            items_val = kwargs.pop("items")
            if items_val == "" or items_val is None: items_val = []
            elif isinstance(items_val, str):
                try: items_val = ast.literal_eval(items_val)
                except Exception: items_val = []
            if items_val is not None:
                if len(set(items_val)) == len(items_val):
                    for checkbox in self.checkboxes: checkbox.destroy()
                    self.checkboxes.clear()
                    self.selected_indexes.clear()
                    for index in range(len(items_val)):
                        self.checkboxes.append(sCTkCheckBox(self.checkboxes_frame, text=items_val[index], command=lambda a=index: self._selection(a)))
                    self._search_modified()
                else: raise ValueError("There is two times or more the same item in the given items list")

        if "searchBox" in kwargs:
            sb_val = kwargs.pop("searchBox")
            if sb_val == "" or sb_val is None: sb_val = True
            elif isinstance(sb_val, str): sb_val = str(sb_val).lower() in ['true', '1', 'yes']
            self._search_box_visible = sb_val
            if self._search_box_visible:
                if not hasattr(self, "search_bar") or self.search_bar is None: self.search_bar = sCTkEntryPrimary(self, textvariable=self.search_var)
                self.search_bar.pack(anchor="n", fill="x")
                if hasattr(self, "checkboxes_frame") and self.checkboxes_frame is not None:
                    self.checkboxes_frame.pack_forget()
                    self.checkboxes_frame.pack(expand=True, fill="both", side="bottom")
                if self._state == "disabled" and self.search_bar is not None: self.search_bar.configure(state="readonly")
            else:
                if hasattr(self, "search_bar") and self.search_bar is not None: self.search_bar.pack_forget()

        if "multiple_choices" in kwargs:
            mult_val = kwargs.pop("multiple_choices")
            if mult_val == "" or mult_val is None: mult_val = True
            elif isinstance(mult_val, str): mult_val = str(mult_val).lower() in ['true', '1', 'yes']
            self.multiple_choices = mult_val

        if "state" in kwargs: self.state(kwargs.pop("state"))

        pack_prop_val = kwargs.pop("pack_propagate", None)
        grid_prop_val = kwargs.pop("grid_propagate", None)
        if pack_prop_val is not None and pack_prop_val != "": setattr(self, "_pack_propagate_val", str(pack_prop_val).lower() in ['true', '1', 'yes'])
        if grid_prop_val is not None and grid_prop_val != "": setattr(self, "_grid_propagate_val", str(grid_prop_val).lower() in ['true', '1', 'yes'])

        for k, v in list(kwargs.items()):
            if k in self._local_defaults: self.final_kw[k] = kwargs.pop(k)

        if "fg_color" in self.final_kw:
            new_fg = self.final_kw.get("fg_color")
            if hasattr(self, "checkboxes_frame"): self.checkboxes_frame.configure(fg_color=new_fg)

        w_val = int(self.final_kw.get("width", 0))
        h_val = int(self.final_kw.get("height", 0))
        if w_val > 0 or h_val > 0:
            use_pack_p = pack_prop_val if pack_prop_val is not None else getattr(self, "_pack_propagate_val", False)
            use_grid_p = grid_prop_val if grid_prop_val is not None else getattr(self, "_grid_propagate_val", False)
        else:
            self.final_kw["width"] = 200
            self.final_kw["height"] = 150
            use_pack_p = pack_prop_val if pack_prop_val is not None else getattr(self, "_pack_propagate_val", True)
            use_grid_p = grid_prop_val if grid_prop_val is not None else getattr(self, "_grid_propagate_val", True)

        if isinstance(use_pack_p, str): use_pack_p = use_pack_p.lower() in ['true', '1', 'yes']
        if isinstance(use_grid_p, str): use_grid_p = use_grid_p.lower() in ['true', '1', 'yes']
        if use_pack_p is not None: self.pack_propagate(use_pack_p)
        if use_grid_p is not None: self.grid_propagate(use_grid_p)

        if hasattr(self, "checkboxes_frame") and hasattr(self.checkboxes_frame, "_parent_frame"):
            if use_pack_p is not None: self.checkboxes_frame._parent_frame.pack_propagate(use_pack_p)
            if use_grid_p is not None: self.checkboxes_frame._parent_frame.grid_propagate(use_grid_p)

        self.final_kw.pop("pack_propagate", None)
        self.final_kw.pop("grid_propagate", None)
        self.final_kw.pop("state", None)

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)
        if kwargs: return super().configure(**kwargs)
        return None

    def _set_appearance_mode(self, mode_string: str):
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._update_current_visual_state()

    def get_state(self) -> str:
        return self.state()

    def state(self, mode: str = None) -> str:
        """Dedicated state manager controlling human inputs programmatically via canvas intercept shields."""
        if mode is None: return str(getattr(self, "_state", "normal")).lower()
        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._state = "normal"
            if hasattr(self, "search_bar") and self.search_bar is not None:
                self.search_bar.configure(state="normal")
            if hasattr(self, "checkboxes"):
                for cb in self.checkboxes:
                    cb.configure(state="normal")
                    if hasattr(cb, "_create_bindings"):
                        try:
                            cb._create_bindings()
                        except Exception:
                            pass
        elif mode == "disabled":
            self._state = "disabled"
            if hasattr(self, "search_bar") and self.search_bar is not None:
                self.search_bar.configure(state="readonly")
            if hasattr(self, "checkboxes"):
                for cb in self.checkboxes:
                    # 🔑 HARD INTERCEPT UNBIND MATRIX: Paralyzes mouse clicking tracks completely
                    try:
                        if hasattr(cb, "_canvas") and cb._canvas:
                            cb._canvas.unbind("<Enter>")
                            cb._canvas.unbind("<Leave>")
                            cb._canvas.unbind("<Button-1>")
                            cb._canvas.unbind("<ButtonRelease>")
                        if hasattr(cb, "_text_label") and cb._text_label:
                            cb._text_label.unbind("<Enter>")
                            cb._text_label.unbind("<Leave>")
                            cb._text_label.unbind("<Button-1>")
                            cb._text_label.unbind("<ButtonRelease>")
                    except Exception:
                        pass
        self._update_current_visual_state()
        return self._state

    def _update_current_visual_state(self):
        """
        Applies checkbox and search-bar colors based on the current state.

        FIX: an earlier version's disabled branch used 100% hardcoded
        literals -- self._custom_disabled_map was set up in __init__ but
        never actually consulted here, meaning a correctly-populated
        disabled_map in sCTkThemes.json had zero effect on what users
        actually saw. Now reads from self._custom_disabled_map like every
        other widget in this project, with hard-fail validation for
        required keys.

        FIX: an earlier version derived the checkbox's fill/hover color from
        this widget's OWN fg_color/hover_color theme keys -- the same keys
        that control the surrounding frame's own background -- falling back
        to a hardcoded accent color pair whenever fg_color was "transparent"
        (a common, legitimate choice for frame-type widgets, not a theme
        gap). Reusing fg_color for two different purposes doesn't work when
        the frame is meant to be transparent. Now uses dedicated
        "checkbox_fg_color"/"checkbox_hover_color" theme keys instead, with
        hard-fail validation, rather than overloading fg_color or silently
        substituting a hardcoded guess.

        FIX: an earlier version also wrote cb._inner_fg_color and cb._hover
        directly onto each checkbox instance, in both branches -- confirmed
        against sctk_checkbox.py's actual source that neither attribute is
        ever read by CheckBox's own code anywhere. These were writes to
        private attributes CheckBox never defined, with no effect. Removed
        entirely, along with the now-unused color computation that only ever
        fed into the dead cb._inner_fg_color write (which itself included a
        cross-widget reach into the checkbox's own private _local_defaults
        for a theme key, "inner_fg_color", that isn't part of CheckBox's
        documented theme key set at all).

        Passes raw (light, dark) tuples straight through to each checkbox's
        configure() instead of resolving to a single color first, matching
        the tuple-based approach validated elsewhere in this project. An
        earlier version resolved everything to a single string first, which
        still worked correctly here specifically because _set_appearance_mode
        already manually re-triggers this whole method on every light/dark
        switch -- but that's inconsistent with the more robust pattern used
        elsewhere, which doesn't depend on a manual re-trigger at all.
        """
        is_disabled = getattr(self, "_state", "normal") == "disabled"

        if hasattr(self, "search_bar") and self.search_bar is not None:
            self.search_bar._update_current_visual_state()

        if not hasattr(self, "checkboxes"):
            return

        # FIX: required-key validation, replacing the hardcoded literals an
        # earlier version used unconditionally in both branches below.
        for required_key in ("text_color", "checkbox_fg_color", "checkbox_hover_color", "border_color", "checkmark_color"):
            if self._local_defaults.get(required_key) is None:
                raise KeyError(
                    f"'{self.__class__.__name__}' theme block is missing '{required_key}' "
                    f"at the top level of sCTkThemes.json."
                )
        for required_key in ("text_color", "checkbox_fg_color", "border_color", "checkmark_color"):
            if self._custom_disabled_map.get(required_key) is None:
                raise KeyError(
                    f"'{self.__class__.__name__}' theme block is missing '{required_key}' in disabled_map."
                )

        for cb in self.checkboxes:
            if is_disabled:
                cb.configure(state="disabled")
                d_map = self._custom_disabled_map
                # FIX: an earlier version never referenced self._custom_disabled_map
                # here at all -- these four lines were 100% hardcoded literals
                # with zero theme connection. hover_color intentionally reuses
                # checkbox_fg_color, not a separate disabled hover key -- hover
                # can't meaningfully trigger while disabled anyway, matching the
                # same "no distinct disabled hover" convention used elsewhere
                # in this project (e.g. sCTkSlider).
                cb.configure(
                    text_color=d_map.get("text_color"),
                    fg_color=d_map.get("checkbox_fg_color"),
                    border_color=d_map.get("border_color"),
                    hover_color=d_map.get("checkbox_fg_color"),
                    checkmark_color=d_map.get("checkmark_color"),
                )
            else:
                cb.configure(state="normal")
                m = self._local_defaults
                # FIX: an earlier version read fg_color/hover_color here --
                # the SAME keys that control the surrounding frame's own
                # background -- with a hardcoded accent-color fallback for
                # whenever fg_color was "transparent" (the frame's own
                # default). Now uses dedicated checkbox_fg_color/
                # checkbox_hover_color keys instead, so the checkbox's accent
                # color no longer depends on what the frame's background
                # happens to be set to.
                cb.configure(
                    text_color=m.get("text_color"),
                    fg_color=m.get("checkbox_fg_color"),
                    border_color=m.get("border_color"),
                    hover_color=m.get("checkbox_hover_color"),
                    checkmark_color=m.get("checkmark_color"),
                )

            # Force an explicit redrawing pass on the inner elements safely
            if hasattr(cb, "_draw"): cb._draw()