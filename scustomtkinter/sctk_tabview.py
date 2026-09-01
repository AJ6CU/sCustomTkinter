#!/usr/bin/python3
"""
sCTkTabview

A theme-compliant custom multi-page tab container layout.
Inherits from sCTkTabviewUI and ThemeableWidget to manage dense cockpit dashboard
panels safely with full live theme repaint loops out of themes.json.
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

        # 3. Intercept the non-standard font key locally before initialization pass
        target_font = self.final_kw.pop("font", self._local_defaults.get("font", ("Arial", 13, "normal")))

        # Registry of sCTkFrame page wrappers, keyed by tab name -- see
        # _ensure_sctk_page(). Established BEFORE super().__init__() so it
        # exists no matter when the first tab gets created.
        self._sctk_pages = {}

        # 4. Initialize parent class natively with clean frame-compliant attributes safely
        super().__init__(master, **self.final_kw)

        # 5. Forward the extracted font parameter down to the native layout bar safely
        if hasattr(self, "_segmented_button") and self._segmented_button:
            try:
                self._segmented_button.configure(font=target_font)
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

        # Resolve light/dark text colors cleanly from the parsed theme dictionaries
        resolved_txt = self._resolve_color(m.get("text_color", ("#1F2937", "#F9FAFB")))

        if is_disabled:
            # Re-compile clean keyword payloads to flatten background tracks safely when locked
            updates = {
                "fg_color": self._resolve_color(m.get("segmented_button_fg_color", ("#E5E7EB", "#334155"))),
                "selected_color": self._resolve_color(m.get("segmented_button_selected_color", ("#CBD5E1", "#475569"))),
                "selected_hover_color": self._resolve_color(m.get("segmented_button_selected_color", ("#CBD5E1", "#475569"))),
                "unselected_color": self._resolve_color(m.get("segmented_button_unselected_color", ("#F1F5F9", "#1F2937"))),
                "unselected_hover_color": self._resolve_color(m.get("segmented_button_unselected_color", ("#F1F5F9", "#1F2937")))
            }
        else:
            updates = {
                "fg_color": self._resolve_color(m.get("segmented_button_fg_color", ("#E2E8F0", "#1E293B"))),
                "selected_color": self._resolve_color(m.get("segmented_button_selected_color", ("#1A4375", "#1F6AA5"))),
                "selected_hover_color": self._resolve_color(m.get("segmented_button_selected_hover_color", ("#15375B", "#1A5885"))),
                "unselected_color": self._resolve_color(m.get("segmented_button_unselected_color", ("#F8FAFC", "#334155"))),
                "unselected_hover_color": self._resolve_color(m.get("segmented_button_unselected_hover_color", ("#E2E8F0", "#475569")))
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