#!/usr/bin/python3
"""
sCTkSelector

An advanced theme-compliant, scrollable option tree selector widget.
Pairs an optional high-contrast search field lane with a dynamic listing frame card
to manage multi-state checkbox row configurations natively.
"""
import customtkinter as ctk
from .themeable_widget import ThemeableWidget, parse_list_property

from typing import Optional, Union, Tuple

from .sctk_frame import sCTkFrame
from .sctk_checkbox import sCTkCheckBox
from .sctk_entry_primary import sCTkEntryPrimary
from .sctk_scrollable_frame import sCTkScrollableFrame

class sCTkSelector(sCTkFrame, ThemeableWidget):
    # The placeholder list a cleared `items` property falls back to.
    #
    # NOT the constructor's default -- sCTkSelector(parent) with no items is
    # legitimately empty, and stays that way. This is what the Designer's
    # inspector shows on a fresh widget, and what its builder object passes
    # when the field is blank, so restoring it here keeps the design view,
    # the preview and the generated code agreeing.
    #
    # Previously a cleared field reported "[]" as its default and every
    # checkbox vanished, which looked like the widget had broken.
    DEFAULT_ITEMS = ("Item 1", "Item 2")

    def __init__(self, master, items: Optional[list[str]] = None, multiple_choices=True, searchBox=True, **kwargs):
        # 1. SANITIZE RUNTIME ARGUMENTS: Strip unmanaged properties out immediately
        state_init = kwargs.pop("state", "normal")
        pack_prop_init = kwargs.pop("pack_propagate", None)

        # 2. ENFORCE SYSTEM REGISTRY INTERACTION:
        ThemeableWidget.__init__(self, kwargs)

        # 🛠️ THE MUTATION SAFEGUARD DEEP COPY SHIELD:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # FIX: required-key validation moved here, to construction time,
        # rather than living inside _update_current_visual_state() (called
        # only later, and repeatedly on every state change). Moved so that
        # border_color -- now also passed to both sub-widget constructors
        # below, to keep their normal-state border visually consistent with
        # this widget's own theme -- is guaranteed to exist before anything
        # tries to use it, rather than risking a confusing native error at
        # construction if a key were missing.
        for required_key in ("text_color", "checkbox_fg_color", "checkbox_hover_color", "border_color", "checkmark_color"):
            if self._local_defaults.get(required_key) is None:
                raise KeyError(
                    f"'{(getattr(self, '_THEME_BLOCK_NAME', None) or self.__class__.__name__)}' theme block is missing '{required_key}' "
                    f"at the top level of sCTkThemes.json."
                )
        for required_key in ("text_color", "checkbox_fg_color", "border_color", "checkmark_color"):
            if self._custom_disabled_map.get(required_key) is None:
                raise KeyError(
                    f"'{(getattr(self, '_THEME_BLOCK_NAME', None) or self.__class__.__name__)}' theme block is missing '{required_key}' in disabled_map."
                )

        fg_color = self._local_defaults.get("fg_color", "transparent")
        # FIX: an earlier version never coordinated border_color between this
        # widget and its two internal sub-widgets (search_bar,
        # checkboxes_frame) -- each independently used its own standalone
        # theme's border_color, which could visibly mismatch (confirmed by
        # direct testing: sCTkEntryPrimary and sCTkScrollableFrame's own
        # default border colors differ in dark mode). Passed here, once, at
        # construction, rather than forced on every _update_current_visual_state()
        # call -- that would fight with sCTkEntryPrimary's own correct
        # readonly/disabled border-color changes, undoing the whole point of
        # its three-state model. This only establishes the shared NORMAL-state
        # border; each sub-widget's own state-driven color changes afterward
        # are left completely alone.
        selector_border_color = self._local_defaults.get("border_color")

        # 3. Call the parent sCTkFrame constructor safely
        super().__init__(master, **self.final_kw)

        self._state = "normal"
        self.search_var = ctk.StringVar(self)
        self.search_var.trace_add("write", self._search_modified)

        self.search_bar = None
        self._search_box_visible = bool(searchBox)

        self.checkboxes_frame = sCTkScrollableFrame(self, fg_color=fg_color, border_color=selector_border_color)
        self.checkboxes_frame.pack(expand=True, fill="both", side="bottom")

        if hasattr(self.checkboxes_frame, "_parent_frame") and self.checkboxes_frame._parent_frame is not None:
            self.checkboxes_frame._parent_frame.pack_propagate(False)

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
                # FIX: the default slot used to be the literal "[]", so
                # clearing the field in the Designer reported "the default is
                # an empty list" and every checkbox vanished -- the widget did
                # exactly what it was told, but the answer was wrong. The
                # constructor's default is DEFAULT_ITEMS, which is also what
                # the inspector shows on a fresh widget.
                #
                # Both slots go through _query_value with the property name,
                # so a list is rendered as JSON -- the form pygubu parses and
                # the form a user types. str() of a Python list is neither.
                current_items = ([cb.cget("text") for cb in self.checkboxes]
                                 if hasattr(self, "checkboxes") else [])
                return ("items", "items", "items",
                        self._query_value(list(self.DEFAULT_ITEMS), "items"),
                        self._query_value(current_items, "items"))
            if pname == "pack_propagate": return (pname, pname, pname, "None", str(getattr(self, "_pack_propagate_val", None)))
            if pname in ["fg_color", "border_color", "text_color"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname,
                        self._query_value(self._theme_default(pname)),
                        self._query_value(val))
            # FIX: forwarding a property NAME to native configure() passes it
            # as require_redraw and returns None, where pygubu expects a
            # Tkinter-style five-tuple -- it then hands that None straight back
            # to _set_property(). Reached whenever a field is blanked in the
            # Designer inspector.
            #
            # This file uses the older (self, cnf=None, **kwargs) signature, so
            # the query arrives as `cnf`. The batch pass that fixed this across
            # the library matched on `pname` and `require_redraw` and missed it.
            return self._configure_query(cnf)

        if isinstance(cnf, dict): kwargs = cnf | kwargs

        if "items" in kwargs:
            items_val = kwargs.pop("items")
            # An empty value means "use the placeholder list", matching the
            # query above and what the builder object passes when the
            # inspector field is blank.
            if items_val == "" or items_val is None:
                items_val = list(self.DEFAULT_ITEMS)
            elif isinstance(items_val, str):
                # Shared parser: accepts the Python-literal form this
                # widget's inspector default uses AND the bare
                # comma-separated form every other widget expects.
                try: items_val = parse_list_property(items_val)
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
                # FIX: search_bar's border_color now aligned with this
                # widget's own theme at creation time, matching the same
                # fix applied to checkboxes_frame in __init__ -- see that
                # constructor call's comment for the full reasoning.
                if not hasattr(self, "search_bar") or self.search_bar is None: self.search_bar = sCTkEntryPrimary(self, textvariable=self.search_var, border_color=self._local_defaults.get("border_color"))
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

        # Runtime overrides have to reach the map a repaint reads, or the
        # repaint puts the theme value straight back -- see
        # ThemeableWidget._record_theme_overrides().
        self._record_theme_overrides(kwargs)

        if "state" in kwargs: self.state(kwargs.pop("state"))

        # grid_propagate is deliberately GONE.
        #
        # pack_propagate() and grid_propagate() control whether a container
        # resizes to fit its children, and which one applies depends on how
        # THE CHILDREN are managed -- not on how this widget is managed by its
        # own parent. This widget packs its children, so pack_propagate is the
        # meaningful call and grid_propagate could never do anything.
        #
        # It was offered anyway, so setting it looked like a knob that did
        # nothing, while pack_propagate appeared to work "regardless of
        # geometry management" -- which is simply what it does. A property that
        # provably cannot have an effect is worse than an absent one: someone
        # sets it, sees nothing, and goes looking for a bug in their layout.
        pack_prop_val = kwargs.pop("pack_propagate", None)
        # Accepted and discarded, so existing code passing it does not raise.
        kwargs.pop("grid_propagate", None)
        if pack_prop_val is not None and pack_prop_val != "": setattr(self, "_pack_propagate_val", str(pack_prop_val).lower() in ['true', '1', 'yes'])

        for k, v in list(kwargs.items()):
            if k in self._local_defaults: self.final_kw[k] = kwargs.pop(k)

        if "fg_color" in self.final_kw:
            new_fg = self.final_kw.get("fg_color")
            if hasattr(self, "checkboxes_frame"): self.checkboxes_frame.configure(fg_color=new_fg)

        # FIX: these read final_kw only, and width/height never arrive there.
        #
        # The loop above moves a keyword into final_kw only if it is a key this
        # widget's THEME block defines, and the sCTkSelector block has no width
        # or height. So an explicit height stayed in kwargs, h_val came back 0,
        # and the else branch below ran -- setting 200x150 and, worse, turning
        # ON pack_propagate. The height was then applied to the frame and
        # immediately overridden by the frame shrinking to fit its children.
        #
        # The symptom was a height property that appeared to do nothing, in the
        # Designer and in generated code alike.
        w_val = int(kwargs.get("width", self.final_kw.get("width", 0)) or 0)
        h_val = int(kwargs.get("height", self.final_kw.get("height", 0)) or 0)

        # And put the COERCED values back, because the Designer sends strings.
        #
        # h_val above is an int and is used for the propagate decision, but the
        # raw kwargs entry -- '100', with quotes -- is what reaches
        # CTkFrame.configure() at the end of this method, which wants a number.
        # The height was computed correctly, used correctly, and then forwarded
        # in a form the native widget could not act on.
        if "width" in kwargs:
            kwargs["width"] = w_val
        if "height" in kwargs:
            kwargs["height"] = h_val
        if w_val > 0 or h_val > 0:
            use_pack_p = pack_prop_val if pack_prop_val is not None else getattr(self, "_pack_propagate_val", False)
        else:
            self.final_kw["width"] = 200
            self.final_kw["height"] = 150
            use_pack_p = pack_prop_val if pack_prop_val is not None else getattr(self, "_pack_propagate_val", True)

        if isinstance(use_pack_p, str): use_pack_p = use_pack_p.lower() in ['true', '1', 'yes']
        if use_pack_p is not None: self.pack_propagate(use_pack_p)

        if hasattr(self, "checkboxes_frame") and hasattr(self.checkboxes_frame, "_parent_frame"):
            if use_pack_p is not None: self.checkboxes_frame._parent_frame.pack_propagate(use_pack_p)

        self.final_kw.pop("pack_propagate", None)
        self.final_kw.pop("grid_propagate", None)   # harmless if it was passed
        self.final_kw.pop("state", None)

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)
        if kwargs: return super().configure(**kwargs)
        return None

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. Without this line, calling .config(...) silently skips
    # this entire override and lands on sCTkFrame's configure() instead,
    # bypassing the items/searchBox/multiple_choices/state handling above.
    # Confirmed as a critical bug on sCTkSegmentedButton earlier in this
    # project's audit; this was the last widget in the library still missing
    # the alias.
    #
    # Note this class uses the older Tkinter `(self, cnf=None, **kwargs)`
    # signature rather than `*args`. That's correct here and not the source of
    # the tuple-comparison bugs found elsewhere: cnf is a real parameter
    # holding the value itself, so `isinstance(cnf, dict)` and `pname = cnf`
    # both behave as intended.
    config = configure

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

        Required-key validation for the theme keys this method (and
        __init__'s sub-widget construction) depends on happens once, in
        __init__ -- not repeated here on every call.

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