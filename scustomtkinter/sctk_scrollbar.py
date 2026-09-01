#!/usr/bin/python3
"""
sCTkScrollbar - Piece 1 of 2

An advanced, theme-compliant custom scrollbar component and native container.
Inherits cleanly from ctk.CTkScrollbar to preserve native macOS high-precision
touchpad event streams and keep global light/dark theme tracking active.
"""
import tkinter as tk

import customtkinter as ctk
from .themeable_widget import ThemeableWidget
from .sctk_scroll_mixin import ScrollBindingMixin


class sCTkScrollbar(ctk.CTkScrollbar, ThemeableWidget):
    def __init__(self, master=None, **kwargs):
        # 1. Run shared mixin logic first to parse master themes.json safely
        ThemeableWidget.__init__(self, kwargs)
        self._local_defaults = dict(self.final_kw)

        # 2. Track orientation layout constraints cleanly
        orientation = kwargs.get("orientation", "vertical").lower()
        self._is_horizontal = orientation == "horizontal"

        # 3. Securely set default sizes based on orientation layout rules
        if self._is_horizontal:
            self.final_kw.setdefault("height", 14)
        else:
            self.final_kw.setdefault("width", 14)

        # 4. Initialize CustomTkinter natively so Apple Magic Mouse / trackpad streams stay intact
        super().__init__(master, **self.final_kw)
        self._apply_custom_theme_colors()
        self._finalize_themeable_lifecycle()

    def _apply_custom_theme_colors(self):
        """Cascades color profiles directly out of your centralized stylesheet json maps."""
        normal_color = self._local_defaults.get("button_color", ["#64748B", "#4B5563"])
        normal_hover = self._local_defaults.get("button_hover_color", ["#1A4375", "#2471A3"])

        super().configure(
            button_color=tuple(normal_color) if isinstance(normal_color, list) else normal_color,
            button_hover_color=tuple(normal_hover) if isinstance(normal_hover, list) else normal_hover
        )

    # Theme keys that _apply_custom_theme_colors() re-pushes on every repaint.
    # configure() records these into _local_defaults so a runtime override
    # survives the repaint instead of being reverted by it.
    _THEME_TRACKED_KEYS = frozenset({"button_color", "button_hover_color"})

    def configure(self, *args, **kwargs):
        """
        Processes standard configuration queries and manages visual refreshes.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally.
                - a tracked theme key name: returns a Tkinter-style
                  (name, name, name, default, current) query tuple.
                - anything else: forwarded to the native widget.
            **kwargs: Any native CTkScrollbar option.

        Returns:
            The query tuple described above for the single-argument case,
            otherwise None.
        """
        # FIX: an earlier version tested `if args and isinstance(args, dict)`.
        # args is ALWAYS a tuple, so that was never true -- the dict-merge
        # branch was dead code, and there was no query branch at all, so
        # configure("button_color") silently returned None instead of a
        # property tuple. Same tautology fixed across the batch-one widgets.
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname in self._THEME_TRACKED_KEYS:
                    val = self._local_defaults.get(pname)
                    return (pname, pname, pname, str(val), str(val))
                return super().configure(pname)

        # FIX: record theme overrides BEFORE the repaint below.
        #
        # _apply_custom_theme_colors() re-pushes button_color and
        # button_hover_color from self._local_defaults on every call. Since
        # configure() never wrote to that dict, the sequence was:
        # super().configure(button_color="red") applied red, then the repaint
        # on the very next line overwrote it with the theme value -- so
        # runtime color overrides silently did nothing.
        #
        # The repaint isn't wrong to exist (the _set_appearance_mode hook
        # needs it); it was wrong to treat _local_defaults as authoritative
        # when configure() had just introduced a newer value it never
        # recorded. Writing the override in first makes the repaint reproduce
        # it rather than revert it, and makes it survive later appearance-mode
        # changes -- matching CustomTkinter's own semantics, where
        # configure(button_color=...) sticks.
        for key in self._THEME_TRACKED_KEYS:
            if key in kwargs:
                self._local_defaults[key] = kwargs[key]

        if kwargs:
            super().configure(**kwargs)
        self._apply_custom_theme_colors()

    config = configure

    def _set_appearance_mode(self, mode_string: str):
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._apply_custom_theme_colors()


class sCTkScrollArea(ctk.CTkFrame, ScrollBindingMixin):
    """
    An unblocked scrollable container frame supporting high-precision Apple momentum streams.
    Bypasses rigid layout masks to give developers full opt-in control over child event bundling.
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, fg_color="transparent", border_width=0, **kwargs)

        current_mode = str(ctk.get_appearance_mode()).lower()
        initial_bg = "#FAFAFA" if current_mode == "light" else "#1A1A1A"

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=initial_bg)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scroll_content = tk.Frame(self.canvas, bd=0, bg=initial_bg)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")

        # Widgets registered through propagate_scroll_events() that aren't
        # descendants of scroll_content -- see that method.
        self._extra_scroll_targets = []

        # A scrollbar attached via hook_scrollbar(), so the wheel keeps
        # working while the pointer is over the bar itself.
        self._hooked_scrollbar = None

        # Scroll handling now comes from ScrollBindingMixin, the library's
        # single shared implementation. This class previously carried its own
        # copy, which had drifted from the canonical version in three ways,
        # all corrected by this change:
        #
        #   - Two's-complement sign correction used `> 32768` rather than
        #     `>= 0x8000`. Those differ at exactly 32768, which is the
        #     smallest NEGATIVE value in a signed 16-bit field: the old form
        #     read it as +32768, inverting scroll direction at that value.
        #   - Windows wheel scaling doubled the delta (`/120 * 2`), scrolling
        #     twice as far per notch as everywhere else in the library.
        #   - The packed touchpad delta was decoded by reading event.delta_y
        #     when present and otherwise applying a 16-bit correction to what
        #     may be a 32-bit packed value, instead of bit-shifting out the
        #     signed 16-bit X and Y components.
        #
        # It also gains the nested-scrollable boundary guard, blocking
        # handlers when scrolling is switched off, and the debounced
        # content rebind.
        self._init_scroll_state()
        self._install_scroll_activation(content_widget=self.scroll_content)

        self.scroll_content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width()))

    # ------------------------------------------------------------------
    # ScrollBindingMixin contract
    # ------------------------------------------------------------------
    def _scroll_target(self):
        """This area builds its own canvas, so no parent lookup is needed."""
        canvas = getattr(self, "canvas", None)
        try:
            if canvas is not None and canvas.winfo_exists():
                return canvas
        except Exception:
            pass
        return None

    def _scroll_layers(self):
        """
        The area itself, its canvas, any hooked scrollbar, the full content
        tree, and anything explicitly registered via propagate_scroll_events().

        Returns:
            An ordered, deduplicated list of widgets.
        """
        layers = [self]

        canvas = self._scroll_target()
        if canvas is not None:
            layers.append(canvas)

        if self._hooked_scrollbar is not None:
            self._collect_scroll_descendants(self._hooked_scrollbar, layers)

        content = getattr(self, "scroll_content", None)
        if content is not None:
            try:
                if content.winfo_exists():
                    self._collect_scroll_descendants(content, layers)
            except Exception:
                pass

        for widget in list(self._extra_scroll_targets):
            try:
                if widget.winfo_exists():
                    self._collect_scroll_descendants(widget, layers)
                else:
                    self._extra_scroll_targets.remove(widget)
            except Exception:
                pass

        return layers

    def hook_scrollbar(self, scrollbar_widget):
        """
        Connects a scrollbar to this area's canvas in both directions.

        The scrollbar is also recorded as a scroll layer, so the wheel keeps
        working while the pointer is over the bar itself rather than dying
        the moment it leaves the content.
        """
        self.canvas.configure(yscrollcommand=scrollbar_widget.set)
        scrollbar_widget.configure(command=self.canvas.yview)
        self._hooked_scrollbar = scrollbar_widget
        self._activate_scroll_bindings()

    def propagate_scroll_events(self, target_widget: tk.Widget):
        """
        Registers a widget outside this area's own content tree to receive
        scroll events, along with its descendants.

        RARELY NEEDED NOW. Content placed inside scroll_content is bound
        automatically, and re-bound whenever it changes, so this is only for
        widgets that sit outside that tree. Registered widgets are remembered
        and re-bound on every subsequent pass, rather than bound once and
        forgotten as the previous implementation did.

        Args:
            target_widget: The widget to register. Its descendants are
                included automatically.
        """
        if target_widget not in self._extra_scroll_targets:
            self._extra_scroll_targets.append(target_widget)
        self._activate_scroll_bindings()

    def process_incoming_scroll(self, event):
        """
        COMPATIBILITY SHIM. Scroll events are dispatched by
        ScrollBindingMixin directly; this remains only for external callers
        that bound this method themselves before the consolidation.

        Delegates to the shared wheel handler. Trackpad <TouchpadScroll>
        events are routed to the mixin's own accumulator-gated handler by its
        bindings, so they do not pass through here.
        """
        return self._process_scroll_wheel(event)

    def _set_appearance_mode(self, mode_string: str):
        if hasattr(super(), "_set_appearance_mode"):
            super()._set_appearance_mode(mode_string)
        target_bg = "#FAFAFA" if str(mode_string).lower() == "light" else "#1A1A1A"
        if hasattr(self, "canvas") and self.canvas: self.canvas.configure(bg=target_bg)
        if hasattr(self, "scroll_content") and self.scroll_content: self.scroll_content.configure(bg=target_bg)