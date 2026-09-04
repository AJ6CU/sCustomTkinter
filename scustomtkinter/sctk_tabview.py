#!/usr/bin/python3
"""
sCTkTabview

A theme-compliant custom multi-page tab container layout.
Inherits from ctk.CTkTabview and ThemeableWidget to manage dense cockpit dashboard
panels safely with full live theme repaint loops out of sCTkThemes.json.
"""
import tkinter as tk

import customtkinter as ctk
from .themeable_widget import ThemeableWidget
from .sctk_frame import sCTkFrame

class sCTkTabview(ctk.CTkTabview, ThemeableWidget):
    def __init__(self, master=None, **kw):

        # 1. Run shared mixin logic first to parse master themes.json safely
        ThemeableWidget.__init__(self, kw)

        # 2. Store your custom memory deep-copy maps cleanly onto instance structures
        self._local_defaults = dict(self.final_kw)

        # FIX: an earlier version read "disabled_map" out of self._local_defaults
        # (== dict(self.final_kw)), but ThemeableWidget.__init__ deliberately
        # excludes "disabled_map" from final_kw -- this always evaluated to the
        # empty-dict default, meaning EVERY disabled-state color lookup in
        # _apply_custom_theme_colors() silently fell back to its hardcoded
        # literal instead of the real theme. The disabled colors still LOOKED
        # plausible, because those fallbacks are reasonable values, so nothing
        # flagged it visually. Confirmed identical bug, same fix, as sCTkSwitch,
        # sCTkSpinbox, and sCTkTableview elsewhere in this project.
        self._custom_disabled_map = dict(self._widget_disabled_map)
        self._custom_current_state = "normal"

        # 2a. Hard-fail on theme gaps rather than substituting a guessed value.
        #
        # FIX: an earlier version used .get(key, hardcoded_literal) for every
        # color below and for the font above, silently substituting a plausible
        # guess whenever the real theme was incomplete rather than surfacing the
        # gap. Because those guesses looked reasonable, a broken or partial
        # theme block was invisible. Matches the hard-fail principle established
        # for sCTkSwitch, sCTkTableview, sCTkScrollableFrame, and the label
        # family elsewhere in this project.
        #
        # SCOPED TO DIRECT CONSTRUCTION. A subclass reaches here with final_kw
        # built from ITS OWN theme block -- ThemeableWidget's run-once guard
        # means this constructor never rebuilds it -- so validating this
        # widget's keys against a subclass's block would raise on every
        # construction. Same guard, same reason, as sCTkScrollableFrame.
        if type(self) is sCTkTabview:
            # Colors that visually change when disabled: required in BOTH the
            # top-level block and disabled_map.
            for required_key in ("text_color",
                                 "segmented_button_fg_color",
                                 "segmented_button_selected_color",
                                 "segmented_button_unselected_color"):
                if self._local_defaults.get(required_key) is None:
                    raise KeyError(
                        f"'{self.__class__.__name__}' theme block is missing "
                        f"'{required_key}' at the top level of sCTkThemes.json."
                    )
                if self._custom_disabled_map.get(required_key) is None:
                    raise KeyError(
                        f"'{self.__class__.__name__}' theme block is missing "
                        f"'{required_key}' in disabled_map."
                    )

            # Hover colors are top-level only. They deliberately have NO
            # disabled_map entry: a disabled tab bar must not light up under
            # the cursor, so _apply_custom_theme_colors() collapses hover to
            # the corresponding non-hover disabled color instead of reading a
            # separate one. Same reasoning as sCTkScrollableFrame's inert
            # scrollbar, resolved differently here because there's no
            # meaningful "dimmed hover" distinct from "dimmed".
            #
            # font and segmented_button_height are likewise top-level only --
            # no widget in this project has a disabled-state font, and the
            # tab bar's height doesn't change when disabled.
            for required_key in ("segmented_button_selected_hover_color",
                                 "segmented_button_unselected_hover_color",
                                 "font",
                                 "segmented_button_height"):
                if self._local_defaults.get(required_key) is None:
                    raise KeyError(
                        f"'{self.__class__.__name__}' theme block is missing "
                        f"'{required_key}' at the top level of sCTkThemes.json."
                    )

        # 3. Intercept the non-standard font key locally before initialization
        # pass. Popped from final_kw because native CTkTabview doesn't accept
        # a `font` keyword -- it goes to the segmented button instead, in
        # step 5 below. No fallback: validated above.
        target_font = self.final_kw.pop("font", self._local_defaults.get("font"))

        # Same treatment for the tab bar height. Native CTkTabview names every
        # parameter explicitly with no **kwargs catch-all, so ANY key it
        # doesn't recognize raises ValueError from super().__init__() below --
        # this must be popped, not merely ignored. Forwarded to the segmented
        # button in step 5, which is the widget that actually has a height.
        target_button_height = self.final_kw.pop(
            "segmented_button_height", self._local_defaults.get("segmented_button_height"))

        # Registry of sCTkFrame page wrappers, keyed by tab name -- see
        # _ensure_sctk_page(). Established BEFORE super().__init__() so it
        # exists no matter when the first tab gets created.
        self._sctk_pages = {}

        # 4. Initialize parent class natively with clean frame-compliant attributes safely
        super().__init__(master, **self.final_kw)

        # 5. Forward the extracted font and height parameters down to the
        # native layout bar safely. Applied once here rather than in
        # _apply_custom_theme_colors(), since neither changes with state --
        # re-pushing them on every repaint would be wasted work.
        #
        # NOTE: segmented_button_height is currently a NO-OP visually, and
        # that is expected, not a bug. The height is genuinely applied --
        # _segmented_button.cget("height") reports it back correctly -- but
        # CTkTabview grids the segmented button into a row whose minsize comes
        # from its own private spacing constants, and overlaps it with the
        # page frame below to get the connected-tab look. A taller button is
        # clipped by that row rather than expanding it; confirmed by direct
        # testing with a height of 128, which reported back correctly and
        # changed nothing on screen.
        #
        # Kept, and kept required in the theme, deliberately: it costs
        # nothing, keeps the theme contract stable, and is already wired end
        # to end, so if a future CustomTkinter release exposes the strip
        # height only the application step changes. Making it work today would
        # mean writing CTkTabview's private _top_spacing /
        # _top_button_overhang and re-running _configure_grid(), a CTk
        # internals dependency that could break on any upstream release.
        #
        # This is a CTkTabview layout constraint, NOT a segmented button
        # limitation -- a standalone sCTkSegmentedButton honors height fine.
        if hasattr(self, "_segmented_button") and self._segmented_button:
            try:
                self._segmented_button.configure(font=target_font, height=target_button_height)
            except Exception:
                pass

        # 6. Apply styles and complete lifecycle
        self._apply_custom_theme_colors()
        self._finalize_themeable_lifecycle()

    def _apply_custom_theme_colors(self):
        """Cascades structural look profiles directly out of your centralized stylesheet json."""
        if not hasattr(self, "_segmented_button") or not self._segmented_button:
            return

        is_disabled = (self._custom_current_state == "disabled")
        m = self._custom_disabled_map if is_disabled else self._local_defaults

        # No .get() fallbacks anywhere below: __init__ hard-fails on any
        # missing key, so every lookup here is guaranteed to resolve. A
        # fallback would only reintroduce the silent-substitution behavior
        # that made a broken theme block invisible.
        resolved_txt = self._resolve_color(m.get("text_color"))

        if is_disabled:
            # Hover deliberately collapses to the corresponding non-hover
            # disabled color: a disabled tab bar must not light up under the
            # cursor. This is why disabled_map has no hover keys of its own --
            # see the validation note in __init__.
            disabled_selected = self._resolve_color(m.get("segmented_button_selected_color"))
            disabled_unselected = self._resolve_color(m.get("segmented_button_unselected_color"))
            updates = {
                "fg_color": self._resolve_color(m.get("segmented_button_fg_color")),
                "selected_color": disabled_selected,
                "selected_hover_color": disabled_selected,
                "unselected_color": disabled_unselected,
                "unselected_hover_color": disabled_unselected,
            }
        else:
            updates = {
                "fg_color": self._resolve_color(m.get("segmented_button_fg_color")),
                "selected_color": self._resolve_color(m.get("segmented_button_selected_color")),
                "selected_hover_color": self._resolve_color(m.get("segmented_button_selected_hover_color")),
                "unselected_color": self._resolve_color(m.get("segmented_button_unselected_color")),
                "unselected_hover_color": self._resolve_color(m.get("segmented_button_unselected_hover_color")),
            }

        try:
            self._segmented_button.configure(**updates)
        except Exception:
            pass

        # Intercept child buttons array dictionary to forcefully assign text color mappings cleanly
        if hasattr(self._segmented_button, "_buttons_dict") and self._segmented_button._buttons_dict:
            for button in self._segmented_button._buttons_dict.values():
                try:
                    button.configure(text_color=resolved_txt)
                except Exception:
                    pass
    def configure(self, *args, **kwargs):
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        FIX: an earlier version of this class had no configure() override at
        all. Two consequences, both confirmed against how every other widget
        in this project behaves: configure(state="disabled") silently did
        nothing (state was reachable only via the state() method), and Pygubu
        Designer had no way to query or set any managed property.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally.
                - "state": returns a Tkinter-style
                  (name, name, name, default, current) tuple.
                - anything else: forwarded to the native widget's configure().
            **kwargs: `state`, plus any native CTkTabview option.

        Returns:
            The query tuple described above for the single-argument case,
            otherwise None.
        """
        # args is always a tuple -- args[0] is the actual value passed, whether
        # a string or a dict. Comparing the wrapped tuple directly (the
        # `if args and isinstance(args, dict)` pattern found elsewhere in this
        # project) is always False and makes the query branches dead code.
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname == "state":
                    return ("state", "state", "state", "normal",
                            str(getattr(self, "_custom_current_state", "normal")))
                return super().configure(pname)

        # state is this library's own property, not a native CTkTabview one,
        # and must be removed before the super() call below.
        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        if kwargs:
            super().configure(**kwargs)
            self._apply_custom_theme_colors()

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. Without this line, calling .config(...) skips the
    # override entirely and lands on the native widget's configure(),
    # bypassing theming completely -- confirmed as a critical bug on
    # sCTkSegmentedButton earlier in this project's audit.
    config = configure

    def cget(self, attribute_name):
        """
        Standard property accessor, extended to know about `state`.

        Native CTkTabview.cget() raises on any attribute it doesn't
        recognize, so this library's own property is intercepted here before
        delegating; everything else passes through unchanged.
        """
        if attribute_name == "state":
            return str(getattr(self, "_custom_current_state", "normal"))
        return super().cget(attribute_name)

    def _ensure_sctk_page(self, name: str) -> sCTkFrame:
        """
        Returns the sCTkFrame page wrapper for a tab, creating it on first use.

        Native CTkTabview.add() constructs a plain ctk.CTkFrame for each tab
        and grids it inline, with no hook to substitute a different class.
        Rather than reimplement add() against CustomTkinter's internals -- or
        mutate the created frame's __class__ at runtime, the fragile pattern
        deliberately retired from sCTkTableview elsewhere in this project --
        this embeds an sCTkFrame INSIDE the native tab frame and hands that
        back to the caller instead. The native frame stays exactly where
        CTkTabview put it and keeps doing its own show/hide/grid work
        untouched; it just becomes an invisible outer shell.

        The wrapper is transparent with no border of its own, so this is
        purely structural -- the tab looks identical, but everything placed
        in it now has an sCTk widget as its parent.

        Wrapping happens lazily here rather than only in add(), so a tab
        created by any other path (insert(), or directly by CTkTabview's own
        machinery) still comes back correctly wrapped the first time it's
        asked for.

        Args:
            name: The tab name, as passed to add().

        Returns:
            The sCTkFrame to place content into.
        """
        existing = self._sctk_pages.get(name)
        if existing is not None:
            try:
                if existing.winfo_exists():
                    return existing
            except Exception:
                pass
            # Stale entry -- the wrapper was destroyed out from under us.
            self._sctk_pages.pop(name, None)

        native_tab = super().tab(name)
        page = sCTkFrame(native_tab, fg_color="transparent", border_width=0)
        page.pack(fill="both", expand=True)
        self._sctk_pages[name] = page
        return page

    def add(self, name: str) -> sCTkFrame:
        """
        Creates a new tab and returns its sCTkFrame content page.

        Note the return type differs from native CTkTabview.add(), which
        hands back a ctk.CTkFrame. See _ensure_sctk_page() for why.
        """
        super().add(name)
        return self._ensure_sctk_page(name)

    def tab(self, name: str) -> sCTkFrame:
        """
        Returns a tab's sCTkFrame content page, creating the wrapper if this
        tab hasn't been asked for before. Native CTkTabview.tab() returns the
        underlying ctk.CTkFrame; use super().tab(name) if you specifically
        need that outer shell.
        """
        return self._ensure_sctk_page(name)

    def rename(self, old_name: str, new_name: str):
        """
        Renames a tab, keeping the page registry in step.

        Native CTkTabview.rename() updates its own _name_list and _tab_dict,
        but knows nothing about this class's _sctk_pages. Without re-keying,
        the wrapper would still be filed under the OLD name -- so tab() and
        delete() would miss it, and _ensure_sctk_page() would build a second
        wrapper inside the same native tab frame.

        Args:
            old_name: The tab's current name.
            new_name: The name to give it.
        """
        super().rename(old_name, new_name)
        if old_name in self._sctk_pages:
            self._sctk_pages[new_name] = self._sctk_pages.pop(old_name)

    def delete(self, name: str):
        """
        Deletes a tab, tearing down its sCTkFrame wrapper first so no stale
        entry is left in the page registry.
        """
        page = self._sctk_pages.pop(name, None)
        if page is not None:
            try:
                page.destroy()
            except Exception:
                pass
        return super().delete(name)

    def state(self, mode: str = None) -> str:
        """🔑 THE CORE DESIGN PATTERN GATEWAY: Aligns fully with all other repository widgets!"""
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        target_mode = str(mode).lower()
        if target_mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
            if hasattr(self, "_segmented_button") and self._segmented_button:
                try: self._segmented_button.configure(state="normal")
                except Exception: pass
        elif target_mode == "disabled":
            self._custom_current_state = "disabled"
            if hasattr(self, "_segmented_button") and self._segmented_button:
                try: self._segmented_button.configure(state="disabled")
                except Exception: pass

        self._apply_custom_theme_colors()
        return self._custom_current_state

    # 🔑 API CONTINUITY PASS-THROUGHS
    def get_state(self) -> str:
        return self.state()

    def bind(self, sequence=None, func=None, add=None):
        """Intercepts designer click loops to prevent unexpected NotImplementedError crashes."""
        try:
            return tk.Frame.bind(self, sequence, func, add)
        except Exception:
            return ""

    def _set_appearance_mode(self, mode_string: str):
        if hasattr(super(), "_set_appearance_mode"):
            try: super()._set_appearance_mode(mode_string)
            except Exception: pass
        self._apply_custom_theme_colors()

