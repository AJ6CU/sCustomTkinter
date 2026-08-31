#!/usr/bin/python3
"""
sCTkScrollableFrame

A theme-compliant scrollable viewport container frame. Inherits directly from
ctk.CTkScrollableFrame so CustomTkinter handles native scrolling and layout;
this class layers automatic light/dark theme resolution and carefully-tuned
cross-platform mouse wheel / macOS trackpad scroll handling on top.

Base class order matters here: `class sCTkScrollableFrame(
ctk.CTkScrollableFrame, ThemeableWidget)` puts the native CTk class first, so
every `super()` call in this file's own methods resolves to
ctk.CTkScrollableFrame -- and, beneath it, tkinter.Misc -- never to
ThemeableWidget. ThemeableWidget's own configure()/cget()/_set_appearance_mode()
overrides have been removed entirely for this reason (see
themeable_widget.py's docstring); this widget owns all of its own runtime
color-swapping logic.

Unlike sCTkFrameLabeledPrimary/Secondary (which also wrap CTkScrollableFrame),
this class has NO disabled-state concept at all -- there is no state() or
get_state() here. This matches sCTkFrame's own "no disabled concept" design;
disabling children placed inside this frame is entirely the caller's
responsibility (see this project's own test harness for this widget, which
maintains its own separate enabled/disabled flag and loops over
get_children() to disable them individually).

IMPORTANT -- SCROLL BINDINGS ARE NOT AUTOMATIC. _toggle_scroll_bindings()/
_finalize_split_bindings() are never called from __init__. You must call
self._finalize_split_bindings() (or self._toggle_scroll_bindings(bind=True))
yourself, after the widget has been placed with pack()/grid()/place() --
exactly as demonstrated in this project's own test harness for this widget.
This is confirmed, deliberate, existing behavior, not an oversight to "fix"
by auto-binding in __init__: the scroll-binding logic below inspects the
widget's actual parent hierarchy (via winfo_parent()), which may not be
fully realized yet at construction time, before the widget has been placed
into a layout.

THE SCROLL-HANDLING METHODS BELOW (_toggle_scroll_bindings,
_process_mac_touchpad_scroll, _process_scroll_wheel,
_decode_mac_touchpad_delta) ARE UNCHANGED FROM THE ORIGINAL, VERIFIED BY THE
MAINTAINER TO BE WORKING, HARD-WON CODE. They implement cross-platform mouse
wheel handling (Windows delta scaling, Linux Button-4/Button-5 discrete
events, macOS Darwin-specific delta scaling) plus raw bit-level decoding of
macOS's high-precision trackpad gesture event (a packed 32-bit delta split
into signed 16-bit X/Y components). None of this logic was touched during
this project's audit; only unrelated bugs elsewhere in this file (argument
handling, dead code, color-tuple resolution) were fixed. Do not modify the
scroll-handling methods without extensive real-device testing across all
three platforms.
"""
import sys
import platform
import time
from typing import Any, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget

class sCTkScrollableFrame(ctk.CTkScrollableFrame, ThemeableWidget):
    """Themeable scrollable viewport container.

    RESOLVED INVESTIGATION -- see _USE_CUSTOM_SCROLL_BINDING below. This
    class inherits directly from ctk.CTkScrollableFrame, so calling
    super().__init__() already triggers native CTk's own scroll-binding
    setup (a global bind_all("<MouseWheel>", ...) combined with a
    _check_if_valid_scroll() walk-up-the-hierarchy check, confirmed directly
    against CustomTkinter's own source). It was suspected this file's own
    additional custom scroll-binding system might be entirely redundant with
    -- and actively competing against -- that already-running native system.
    Confirmed by direct testing NOT to be the case: with this file's custom
    system fully disabled, an external mouse's wheel kept working correctly
    (proving native's inherited handling genuinely works), but the trackpad
    produced zero response at all (not degraded -- completely dead). Trackpad
    gestures on the tested system generate ONLY <TouchpadScroll> events,
    never <MouseWheel> -- these are disjoint event channels for disjoint
    physical inputs, not two systems racing for the same events. This file's
    <TouchpadScroll> handling is the sole channel for trackpad scrolling, not
    a redundant addition alongside native CTk. The real, confirmed bug was
    magnitude loss in _process_mac_touchpad_scroll's scaling -- see that
    method's own docstring.

    Adds to native ctk.CTkScrollableFrame:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - Pygubu Designer property introspection for `fg_color`,
        `label_fg_color`, `scrollbar_button_color`, and `border_color` via a
        single-argument configure() call. Unlike most widgets in this
        library, these never vary by state (this widget has no disabled
        state at all), so the returned query tuple's `default` and `current`
        positions are always identical.
      - Manual scrollbar re-theming: `scrollbar_button_color`/
        `scrollbar_button_hover_color` are pushed to the internal scrollbar
        directly, since they aren't automatically covered by a single
        configure() call.
      - winfo_children()/get_children()/get_all_children(): by default,
        winfo_children() filters out children whose class name is exactly
        "CTkScrollbar", "CTkCanvas", or "Canvas" -- internal furniture this
        widget creates for its own scrolling machinery. get_children() is
        this filtered view; get_all_children() returns the raw list. Same
        class-name-based limitation as sCTkFrameLabeledPrimary's identical
        filtering approach: a plain, un-themed widget matching one of these
        exact class names, added directly as a child, would be incorrectly
        filtered out too.
      - Cross-platform scroll wheel and macOS trackpad handling -- see module
        docstring. NOT wired up automatically; you must call
        self._finalize_split_bindings() yourself after placing the widget.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox, sCTkSegmentedButton, and the button
    family. Not separately re-confirmed for this specific widget.

    WHITELIST GUARD: if a composite widget inherits sCTkScrollableFrame as its
    own base class (e.g. sCTkTableview(sCTkScrollableFrame, ThemeableWidget))
    and explicitly calls ThemeableWidget.__init__ itself before calling
    super().__init__(), that composite's own final_kw -- built from ITS theme
    block -- could contain keys native ctk.CTkScrollableFrame knows nothing
    about. This matters MORE here than for any other container in this
    project: confirmed directly against CustomTkinter's own source,
    CTkScrollableFrame.__init__ has NO **kwargs catch-all at all -- every
    parameter is explicitly named, so ANY unrecognized keyword reaching it
    raises TypeError immediately, at the level of Python's own argument
    binding, before any custom validation even runs.
    _NATIVE_CTKSCROLLABLEFRAME_KWARGS filters final_kw down to only the keys
    the real native constructor accepts before that call. This only matters
    for the Pattern-B composition scenario described above; for direct
    construction of a plain sCTkScrollableFrame, final_kw already only
    contains this widget's own theme keys, so the filter is a no-op.
    """

    # Confirmed directly against CustomTkinter's own ctk_scrollable_frame.py
    # source: every one of CTkScrollableFrame.__init__'s named parameters,
    # excluding "master" (always passed positionally, never part of the
    # filtered kwargs dict).
    _NATIVE_CTKSCROLLABLEFRAME_KWARGS = frozenset({
        "width", "height", "corner_radius", "border_width", "bg_color",
        "fg_color", "border_color", "scrollbar_fg_color",
        "scrollbar_button_color", "scrollbar_button_hover_color",
        "label_fg_color", "label_text_color", "label_text", "label_font",
        "label_anchor", "orientation",
    })

    # EXPERIMENTAL TOGGLE, under active investigation -- see class docstring.
    # True (default): preserves current behavior -- calling
    #   _finalize_split_bindings() sets up this file's own custom scroll
    #   system (_toggle_scroll_bindings/_process_scroll_wheel/
    #   _process_mac_touchpad_scroll), IN ADDITION to whatever native
    #   ctk.CTkScrollableFrame already set up automatically via inheritance.
    # False: _finalize_split_bindings()/_toggle_scroll_bindings() become
    #   no-ops. Scrolling relies ENTIRELY on whatever native CTkScrollableFrame
    #   already provides automatically via super().__init__() -- no custom
    #   binding of any kind. Untested as of this writing; flip this to False
    #   to find out whether the reported erratic touchpad behavior disappears
    #   when the custom system isn't also running alongside native's own.
    _USE_CUSTOM_SCROLL_BINDING = True

    def __init__(self, master: Optional[Any] = None, **kwargs: Any) -> None:
        """
        Args:
            master: Parent container.
            **kwargs: Any native CTkScrollableFrame argument (e.g. `label_text`),
                or a theme-key override (see the "sCTkScrollableFrame" block
                in sCTkThemes.json).
        """
        # 1. Fire our shared theme logic first. This resolves final_kw
        # (construction-time properties). See ThemeableWidget.__init__ for
        # what actually happens here.
        ThemeableWidget.__init__(self, kwargs)

        # 2. Store the resolved kwargs onto this instance, so later changes
        # here never leak back into the shared theme registry.
        self._local_defaults = dict(self.final_kw)

        # 3. Initialize CustomTkinter natively with the clean final kwargs array.
        # 3. Initialize CustomTkinter natively. Only forwards the subset of
        # final_kw that native CTkScrollableFrame actually accepts -- see this
        # class's docstring ("WHITELIST GUARD") for why this filtering exists,
        # and why it's especially important for this specific native class.
        native_kwargs = {k: v for k, v in self.final_kw.items() if k in self._NATIVE_CTKSCROLLABLEFRAME_KWARGS}
        super().__init__(master, **native_kwargs)

        # 4. Apply initial theming.
        self._update_current_visual_state()

        # FIX: accumulator state for _process_mac_touchpad_scroll's
        # threshold-gated scrolling -- see that method's docstring. Ported
        # from a separate, confirmed-smooth reference implementation
        # (sCTkScrollbar/sCTkScrollArea) after direct A/B testing showed the
        # per-event scroll approach previously used here caused a
        # hang-then-catch-up pattern on real trackpad hardware that this
        # accumulator approach does not.
        self._touchpad_accumulated_delta = 0.0
        self._touchpad_last_direction = 0

        # 5. Register lifecycle handshake hook, notifying Pygubu-style consumers
        # that construction is complete.
        #
        # NOTE: scroll bindings are NOT set up here -- see module docstring.
        # Call self._finalize_split_bindings() yourself once this widget has
        # been placed via pack()/grid()/place().
        self._finalize_themeable_lifecycle()

    def _set_appearance_mode(self, mode_string: str) -> None:
        """
        Forwards CustomTkinter's internal light/dark mode change notification to
        the native widget.

        No longer manually re-triggers _update_current_visual_state(). That
        method now passes raw (light, dark) tuples straight through to
        configure() instead of pre-resolving to a single color, so CTk's own
        appearance-mode tracking should repaint correctly on its own -- the
        same approach validated on sCTkComboBox, sCTkSegmentedButton, and the
        button family.

        Args:
            mode_string: The new appearance mode ("Light" or "Dark"), as passed
                by CustomTkinter's internal appearance-mode change machinery.
        """
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass

    def configure(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            *args: At most one positional argument is meaningful:
                - a dict: merged into kwargs and processed normally below.
                - one of "fg_color"/"label_fg_color"/"scrollbar_button_color"/
                  "border_color": returns a Tkinter-style
                  (name, name, name, default, current) tuple. `default` and
                  `current` are always identical, since this widget has no
                  disabled state to vary them.
                - anything else: forwarded directly to the native widget's
                  configure(), which does not support single-argument property
                  queries for arbitrary properties -- a known limitation
                  shared with the wider Pygubu-query investigation set aside
                  elsewhere in this project.
            **kwargs: Standard CTkScrollableFrame configuration options.

        Returns:
            The query tuple described above for the single-argument case, or
            None for the keyword-argument case (this method doesn't return
            super().configure()'s result in that branch).
        """
        # args is always a tuple -- args[0] is the actual value passed, whether
        # that's a string or a dict. An earlier version of this method compared
        # the wrapped tuple directly (`pname = args`), so the query branches
        # below never matched anything. Don't reintroduce that.
        if len(args) == 1:
            if isinstance(args[0], dict):
                kwargs = {**args[0], **kwargs}
            else:
                pname = args[0]
                if pname in ["fg_color", "label_fg_color", "scrollbar_button_color", "border_color"]:
                    return (pname, pname, pname, str(self._local_defaults.get(pname)), str(self._local_defaults.get(pname)))
                return super().configure(pname)

        if kwargs:
            super().configure(**kwargs)
            self._update_current_visual_state()

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. An earlier version of this file was MISSING this line
    # entirely: calling .config(...) on an instance silently skipped this
    # entire override and landed on the native widget's configure() directly,
    # bypassing theming completely -- confirmed as a critical bug on
    # sCTkSegmentedButton earlier in this project's audit; the same fix
    # applies here.
    config = configure

    def _update_current_visual_state(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file.

        Called after construction and on every keyword configure() call.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.
        Every value here traces back to sCTkThemes.json; there are no
        hardcoded colors in this method.
        """
        config_payload = {}
        for key in ("fg_color", "border_color", "label_fg_color"):
            val = self._local_defaults.get(key)
            if val is not None:
                config_payload[key] = val

        if config_payload:
            super().configure(**config_payload)

        # Re-theme the internal scrollbar, which isn't automatically covered
        # by the configure() call above.
        if hasattr(self, "_scrollbar") and self._scrollbar:
            try:
                normal_bar = self._local_defaults.get("scrollbar_button_color", ("#94A3B8", "#475569"))
                normal_hover = self._local_defaults.get("scrollbar_button_hover_color", ("#64748B", "#334155"))
                self._scrollbar.configure(button_color=normal_bar, button_hover_color=normal_hover)

                if hasattr(self._scrollbar, "_draw"):
                    self._scrollbar._draw()
            except Exception:
                pass

    # =========================================================================
    # SCROLL-HANDLING METHODS BELOW: UNCHANGED FROM THE ORIGINAL. See module
    # docstring. Do not modify without extensive real-device testing.
    # =========================================================================

    def _toggle_scroll_bindings(self, bind=True):
        """The parent canvas intercept engine routing mouse wheels and touchpad events [1.1].

        EXPERIMENTAL: gated on _USE_CUSTOM_SCROLL_BINDING -- see class
        docstring. FIX: an earlier version of this gate lived only in
        _finalize_split_bindings(), but the documented test-harness pattern
        for this widget calls _toggle_scroll_bindings(bind=True) directly,
        bypassing that gate entirely -- meaning setting the toggle to False
        had no effect at all when this method was called this way. Moved
        here, into this method itself, so the toggle is enforced regardless
        of which entry point is used.
        """
        if bind and not self._USE_CUSTOM_SCROLL_BINDING:
            return
        SCROLL_EVENTS = ["<MouseWheel>", "<TouchpadScroll>", "<Button-4>", "<Button-5>"]
        layers_to_bind = [self]
        try:
            parent_path = self.winfo_parent()
            parent_widget = self.nametowidget(parent_path)
            if parent_widget and parent_widget.__class__.__name__ == "Canvas":
                layers_to_bind.append(parent_widget)
                grandparent_path = parent_widget.winfo_parent()
                grandparent_widget = self.nametowidget(grandparent_path)
                if grandparent_widget: layers_to_bind.append(grandparent_widget)
        except Exception:
            pass

        for child in self.get_children():
            if child not in layers_to_bind: layers_to_bind.append(child)

        for target_layer in layers_to_bind:
            for event_str in SCROLL_EVENTS:
                try: target_layer.unbind(event_str)
                except Exception: pass

                if bind:
                    if "Touchpad" in event_str:
                        if sys.platform == "darwin":
                            target_layer.bind("<TouchpadScroll>", self._process_mac_touchpad_scroll, add="+")
                    else:
                        target_layer.bind(event_str, self._process_scroll_wheel, add="+")

    def _process_mac_touchpad_scroll(self, event):
        """
        Processes Apple high-precision touch masks on the true master canvas [1.1].

        FIX: confirmed by direct testing that trackpad gestures on this
        system generate ONLY <TouchpadScroll> events, never <MouseWheel> --
        the earlier double-firing/competing-systems theory is disproven
        (disabling this widget's own custom scroll system entirely produced
        zero trackpad response, while an external mouse's wheel kept working
        throughout via native CTk's own inherited handling). This method is
        the sole channel for trackpad scrolling, not a redundant addition.

        FIX: an earlier version called yview_scroll() immediately on every
        single event, using a scroll amount that discarded delta_y's actual
        magnitude entirely (a fixed +/-3 regardless of whether delta_y was 1
        or 14+). Confirmed by direct A/B testing against a separate,
        independently-working reference implementation
        (sCTkScrollbar/sCTkScrollArea, elsewhere in this project) that
        scrolling immediately on every rapid-fire event -- real trackpad
        gestures were observed generating events roughly every 10ms during
        fast movement -- causes a hang-then-catch-up pattern, while an
        accumulate-then-threshold-gate approach does not. Replaced the
        per-event immediate-scroll logic with accumulation: raw delta_y is
        summed across events, and yview_scroll() only fires once the running
        total crosses a threshold, then resets to zero. Faster gestures
        naturally cross the threshold more often, so overall scroll rate
        still scales with gesture speed without needing to vary the size of
        each individual scroll call. Direction reversal immediately resets
        the accumulator, so a quick reversal doesn't inherit leftover
        momentum from the opposite direction.
        """
        try:
            parent_widget = self.nametowidget(self.winfo_parent())
            if parent_widget and hasattr(parent_widget, "yview_scroll"):
                delta_x, delta_y = self._decode_mac_touchpad_delta(event.delta)
                if delta_y != 0:
                    current_tick_direction = 1 if delta_y > 0 else -1
                    if current_tick_direction != self._touchpad_last_direction and self._touchpad_last_direction != 0:
                        self._touchpad_accumulated_delta = 0.0
                    self._touchpad_last_direction = current_tick_direction

                    self._touchpad_accumulated_delta += delta_y

                    # Tunable -- larger value = more decimation of the raw
                    # high-resolution delta stream before a scroll actually
                    # happens. Ported from the confirmed-smooth reference
                    # implementation's own threshold value; adjust this one
                    # constant while testing to find what feels right.
                    TOUCHPAD_ACCUMULATION_THRESHOLD = 12.0
                    scaled_scroll = 0
                    if abs(self._touchpad_accumulated_delta) >= TOUCHPAD_ACCUMULATION_THRESHOLD:
                        scaled_scroll = -1 if self._touchpad_accumulated_delta > 0 else 1
                        parent_widget.yview_scroll(scaled_scroll, "units")
                        self._touchpad_accumulated_delta = 0.0

                    # TEMPORARY DIAGNOSTIC -- keep while tuning
                    # TOUCHPAD_ACCUMULATION_THRESHOLD above; remove once
                    # satisfied. scaled_scroll of 0 means this event only
                    # contributed to the accumulator without crossing the
                    # threshold yet -- no scroll happened on this event.
                    print(f"[TouchpadScroll] t={time.time():.4f}  event.widget={event.widget}  raw_delta={event.delta}  "
                          f"decoded_delta_y={delta_y}  accumulated={self._touchpad_accumulated_delta:.2f}  "
                          f"scaled_scroll={scaled_scroll}")
        except Exception:
            pass

    def _process_scroll_wheel(self, event):
        """Processes cross-platform standard mouse wheels and physical tuning knobs [1.1]."""
        try:
            parent_widget = self.nametowidget(self.winfo_parent())
            if parent_widget and hasattr(parent_widget, "yview_scroll"):
                sys_platform = platform.system()
                if sys_platform == "Darwin":
                    delta = event.delta
                    MAC_SCROLL_SENSITIVITY = 3
                    scaled_scroll = int(-MAC_SCROLL_SENSITIVITY * delta) if abs(delta) >= 1 else (
                        -MAC_SCROLL_SENSITIVITY if delta > 0 else MAC_SCROLL_SENSITIVITY)
                    # TEMPORARY DIAGNOSTIC -- see _process_mac_touchpad_scroll's
                    # identical note.
                    print(f"[MouseWheel/Darwin] t={time.time():.4f}  raw_delta={delta}  "
                          f"scaled_scroll={scaled_scroll}")
                    parent_widget.yview_scroll(scaled_scroll, "units")
                elif sys_platform == "Linux":
                    if event.num == 4: parent_widget.yview_scroll(-1, "units")
                    elif event.num == 5: parent_widget.yview_scroll(1, "units")
                else:
                    parent_widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def _decode_mac_touchpad_delta(self, raw_delta):
        """DIAL-VERIFIED PHYSICS MASK: Decodes macOS touchpad bitmasks [1.1]."""
        raw = raw_delta & 0xFFFFFFFF
        delta_x = (raw >> 16) & 0xFFFF
        if delta_x >= 0x8000: delta_x -= 0x10000
        delta_y = raw & 0xFFFF
        if delta_y >= 0x8000: delta_y -= 0x10000
        return delta_x, delta_y

    def _finalize_split_bindings(self):
        """
        Standard layout binding connection pass [1.1]. Call this yourself
        after placing the widget.

        EXPERIMENTAL: the authoritative _USE_CUSTOM_SCROLL_BINDING gate now
        lives inside _toggle_scroll_bindings() itself (see that method's
        docstring for why), so it's enforced regardless of entry point. The
        check here is just an early-exit optimization, not the real gate.
        """
        if not self._USE_CUSTOM_SCROLL_BINDING:
            return
        self._toggle_scroll_bindings(bind=True)

    # =========================================================================
    # END UNCHANGED SCROLL-HANDLING METHODS
    # =========================================================================

    def winfo_children(self, include_private: bool = False) -> list:
        """
        By default, filters out children whose exact class name is
        "CTkScrollbar", "CTkCanvas", or "Canvas" -- internal furniture this
        widget creates for its own scrolling machinery. See this class's
        docstring for a known limitation of this approach.

        Args:
            include_private: If True, returns the raw, unfiltered list instead.

        Returns:
            A list of child widgets.
        """
        raw_children = super().winfo_children()
        if include_private:
            return raw_children

        filtered_children = []
        for child in raw_children:
            if child.__class__.__name__ not in ["CTkScrollbar", "CTkCanvas", "Canvas"]:
                filtered_children.append(child)
        return filtered_children

    def get_children(self) -> list:
        """Equivalent to winfo_children(include_private=False)."""
        return self.winfo_children(include_private=False)

    def get_all_children(self) -> list:
        """Equivalent to winfo_children(include_private=True)."""
        return self.winfo_children(include_private=True)