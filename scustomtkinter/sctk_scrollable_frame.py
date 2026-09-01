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

SCROLL BINDINGS ARE AUTOMATIC. __init__ binds <Map>, so scroll handling
activates by itself the first time the widget becomes visible via
pack()/grid()/place(), and again on any later remap. No separate activation
call is needed.

<Map> is used rather than binding directly in __init__ because the binding
logic inspects the widget's actual parent hierarchy (via winfo_parent()),
which isn't fully realized at construction time, before the widget has been
placed into a layout. <Map> is the earliest point at which it is.

To ship a frame that doesn't respond to scroll input, pass
scroll_enabled=False to the constructor, or call disable_scroll() -- either
one suppresses the automatic activation rather than being silently
overridden by it. See disable_scroll()'s docstring for the bulk-update
workflow this supports, and note that it governs scroll INPUT only; the
scrollbar itself stays visible and draggable.

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
        docstring. Wired up automatically on <Map>; no activation call needed.
      - A `scroll_enabled` property (default True), settable at construction
        or at runtime via configure(scroll_enabled=...), enable_scroll(), and
        disable_scroll(), and readable via cget("scroll_enabled"). Governs
        scroll INPUT handling only -- it does not hide the scrollbar.

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
                in sCTkThemes.json). Additionally accepts `scroll_enabled`
                (bool, default True) -- pass False to construct a frame that
                doesn't respond to scroll input until enable_scroll() is
                called.
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

        # 5. Scroll activation. Bindings now come up automatically the first
        # (and every) time this widget actually becomes visible via
        # pack()/grid()/place() -- see _on_map_auto_bind_scroll()'s docstring.
        # An earlier version required the caller to remember a separate,
        # manual _finalize_split_bindings() call after placement; a scrollable
        # frame that doesn't scroll by default is a confusing thing to ship,
        # given what the widget's own name promises.
        #
        # self._scroll_enabled is the single source of truth for "should this
        # widget respond to scroll input", read here from final_kw so
        # scroll_enabled=False can be passed straight to the constructor and
        # take effect before <Map> ever fires. Not a native CTk keyword; the
        # _NATIVE_CTKSCROLLABLEFRAME_KWARGS filter above already kept it out
        # of super().__init__().
        self._scroll_enabled = bool(self._local_defaults.get("scroll_enabled", True))
        self.bind("<Map>", self._on_map_auto_bind_scroll, add="+")

        # 6. Register lifecycle handshake hook, notifying Pygubu-style consumers
        # that construction is complete.
        self._finalize_themeable_lifecycle()

    def _on_map_auto_bind_scroll(self, event: Any = None) -> None:
        """
        Bound to <Map> in __init__ -- fires automatically the first time, and
        every subsequent time, this widget actually becomes visible via
        pack()/grid()/place(). This is what makes scroll bindings automatic,
        without the caller needing to remember a separate call.

        Deliberately re-fires on every remap, not just the first: if this
        widget is later pack_forget()'d/grid_forget()'d and then re-placed
        (e.g. after new content was added while it was hidden), this re-runs
        the full binding pass and picks up anything new.
        _toggle_scroll_bindings()'s unbind-then-rebind pattern makes repeated
        calls safe, with no risk of duplicate bindings piling up.

        Respects an explicit scroll_enabled=False rather than silently
        overriding it -- but does NOT simply return early in that case. When
        scrolling is disabled this still runs a full pass, installing the
        blocking handlers described in _toggle_scroll_bindings(bind=False).
        That matters for the construct-then-disable-then-pack ordering: at
        the time disable_scroll() is called before placement, the widget's
        parent hierarchy isn't realized and get_children() is typically
        empty, so that earlier pass has almost nothing to install onto. This
        is the first moment the real layer list exists.

        Args:
            event: The Tkinter <Map> event. Accepted and ignored; present only
                because Tkinter passes it to every bound callback.
        """
        self._toggle_scroll_bindings(bind=self._scroll_enabled)

    def enable_scroll(self) -> None:
        """
        Turns scroll handling back on, rebinding every layer immediately.

        Public convenience wrapper over configure(scroll_enabled=True); both
        are equivalent and go through the same code path. Safe to call
        repeatedly -- bindings are always torn down before being rebuilt, so
        nothing accumulates.
        """
        self.configure(scroll_enabled=True)

    def disable_scroll(self) -> None:
        """
        Turns scroll handling off, removing every scroll binding this widget
        knows about. The widget stops responding to wheel and trackpad input
        until enable_scroll() is called.

        Public convenience wrapper over configure(scroll_enabled=False); both
        are equivalent and go through the same code path.

        This also suppresses the automatic <Map>-triggered binding: calling
        this before the widget is first placed means scroll stays off through
        pack()/grid()/place() rather than being silently re-enabled. That
        makes the following a supported pattern for bulk content updates,
        where rebinding on every widget added would be wasted work:

            frame = sCTkScrollableFrame(master)
            frame.disable_scroll()
            frame.pack(fill="both", expand=True)
            for item in many_items:
                SomeWidget(frame, text=item).pack()
            frame.enable_scroll()

        Passing scroll_enabled=False to the constructor achieves the same
        starting state without the separate call.

        NOTE: this affects scroll INPUT handling only. The scrollbar remains
        visible and draggable -- CustomTkinter's scrollbar has no disabled
        state to lock (confirmed by direct investigation earlier in this
        project's audit). Hiding it is a separate concern, handled elsewhere
        by color-matching and zero width.

        Blocks native CTk's own global mouse-wheel handling as well as this
        file's custom bindings -- see _toggle_scroll_bindings(bind=False) for
        the mechanism, and why merely unbinding was not enough.
        """
        self.configure(scroll_enabled=False)

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
                if pname == "scroll_enabled":
                    # Unlike the color properties above, this one reports live
                    # state in the `current` position: `default` is the value
                    # the widget was constructed with, `current` is whatever
                    # enable_scroll()/disable_scroll() last set.
                    return (pname, pname, pname,
                            str(self._local_defaults.get("scroll_enabled", True)),
                            str(self._scroll_enabled))
                return super().configure(pname)

        # scroll_enabled is this library's own property, not a native CTk one.
        # It MUST be popped before the super() call below: CTkScrollableFrame
        # .configure() raises on any keyword it doesn't recognize, exactly as
        # its __init__ does (see the WHITELIST GUARD note in this class's
        # docstring).
        #
        # Deliberately does NOT write back into self._local_defaults --  that
        # dict holds construction-time defaults, and overwriting it here would
        # make the single-argument query above report the current value in its
        # `default` slot, collapsing the distinction between the two.
        if "scroll_enabled" in kwargs:
            new_state = bool(kwargs.pop("scroll_enabled"))
            self._scroll_enabled = new_state
            # Apply immediately rather than waiting for the next <Map>:
            # enable_scroll() on an already-visible widget has to take effect
            # now, and disable_scroll() has to tear bindings down now.
            # _toggle_scroll_bindings() is idempotent either way.
            self._toggle_scroll_bindings(bind=new_state)

        # Re-checked after the pop: configure(scroll_enabled=...) on its own
        # leaves kwargs empty, and there's no reason to repaint for it.
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

    def cget(self, attribute_name: str) -> Any:
        """
        Standard property accessor, extended to know about `scroll_enabled`.

        Native CTkScrollableFrame.cget() raises on any attribute it doesn't
        recognize, so this library's own property has to be intercepted here
        before delegating; everything else passes straight through unchanged.

        Args:
            attribute_name: The property to read.

        Returns:
            For "scroll_enabled", the live bool -- not the construction-time
            default. For anything else, whatever the native widget returns.
        """
        if attribute_name == "scroll_enabled":
            return self._scroll_enabled
        return super().cget(attribute_name)

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

        INTERNAL. Callers outside this class should use enable_scroll() /
        disable_scroll() or configure(scroll_enabled=...) instead. This method
        only manipulates bindings; it does NOT update self._scroll_enabled, so
        calling it directly with bind=False leaves that flag stale and the
        next <Map> will happily rebind. The public entry points set the flag
        and call this, in that order, which is why they're the supported path.

        Args:
            bind: True (re)establishes every scroll binding -- safe to call
                repeatedly, since existing bindings are always removed first
                before any new ones are added, so nothing accumulates or
                duplicates. False removes every binding and adds nothing back.

        EXPERIMENTAL: gated on _USE_CUSTOM_SCROLL_BINDING -- see class
        docstring. FIX: an earlier version of this gate lived only in
        _finalize_split_bindings(), which callers could bypass entirely by
        calling this method directly -- meaning setting the toggle to False
        had no effect at all when it was reached that way. Moved here, into
        this method itself, so the toggle is enforced regardless of which
        entry point is used.

        FIX: an earlier version only bound self.get_children() -- DIRECT
        children, one level deep. A composite widget like sCTkEntryPrimary
        isn't a single Tk widget under the hood; it has its own internal
        sub-structure. If the cursor was over a sub-component that never got
        individually bound, the scroll event simply never fired there at
        all -- Tkinter doesn't bubble unbound events up to a parent's
        binding. Ported from a separate, confirmed-smooth reference
        implementation elsewhere in this project (sCTkScrollArea's
        propagate_scroll_events()), which recurses through every descendant
        at every level, not just direct children. Now does the same here:
        get_children()'s existing top-level furniture filtering (excluding
        this widget's own internal CTkScrollbar/CTkCanvas) is preserved for
        the first level, then every child's own full descendant tree is
        bound too, via plain winfo_children() recursion -- no furniture
        filtering concern exists at that depth, since those are ordinary
        user-placed content widgets and their own sub-components.
        FIX: an earlier version also never bound the scrollbar itself.
        self._scrollbar is a SIBLING of _parent_canvas (both children of
        _parent_frame), not a descendant of self (the content area) --
        get_children()'s recursion, which walks down from self, never
        reaches it. Confirmed by direct testing: binding _parent_frame
        doesn't help either, since Tk doesn't bubble events from an
        unrelated sibling up through an ancestor's own independent binding.
        Scrollbar and its own descendants are now explicitly added.
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

        def _collect_descendants(widget, collected):
            # FIX: stop the recursion at a nested CTkScrollableFrame boundary
            # (covers sCTkScrollableFrame and anything built on it, such as
            # sCTkSelector/sCTkTableview). Without this, an inner scrollable
            # frame placed inside an outer one would have its canvas,
            # scrollbar, and entire content tree bound to the OUTER frame's
            # handler as well as its own -- and since every bind below uses
            # add="+", both handlers fire on the same event, scrolling both
            # frames at once. Native CTk guards the same boundary in
            # _check_if_valid_scroll (comparing _parent_canvas identity); this
            # is the equivalent for the custom binding system.
            if widget is not self and isinstance(widget, ctk.CTkScrollableFrame):
                return
            if widget not in collected:
                collected.append(widget)
            try:
                for child in widget.winfo_children():
                    _collect_descendants(child, collected)
            except Exception:
                pass

        for child in self.get_children():
            _collect_descendants(child, layers_to_bind)

        if hasattr(self, "_scrollbar") and self._scrollbar is not None:
            _collect_descendants(self._scrollbar, layers_to_bind)

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
                else:
                    # FIX: unbinding alone does NOT stop this frame scrolling.
                    # Native CTkScrollableFrame.__init__ installs its own
                    # bind_all("<MouseWheel>") handler, which is entirely
                    # independent of this file's custom system and survives
                    # any unbind() here -- confirmed empirically earlier in
                    # this project's audit, where disabling the custom system
                    # left mouse-wheel scrolling fully working via native's
                    # path while killing the trackpad channel completely.
                    #
                    # unbind_all() is not an option: bind_all is APPLICATION-
                    # global, so it would disable scrolling for every other
                    # scrollable frame in the app too.
                    #
                    # Instead, install a handler that returns "break". Tk
                    # dispatches bindings by bindtag in order -- widget,
                    # class, toplevel, then "all" -- and bind_all lands on
                    # that final "all" tag. A widget-level handler returning
                    # "break" halts the chain before it gets there, so
                    # native's global handler never sees events originating
                    # inside this frame, while remaining untouched for every
                    # other widget in the application.
                    try:
                        if "Touchpad" in event_str:
                            if sys.platform == "darwin":
                                target_layer.bind("<TouchpadScroll>", self._block_scroll_event, add="+")
                        else:
                            target_layer.bind(event_str, self._block_scroll_event, add="+")
                    except Exception:
                        pass

    def _block_scroll_event(self, event: Any = None) -> str:
        """
        Swallows a scroll event so it never reaches native CTk's global
        bind_all handler. Installed on every layer by
        _toggle_scroll_bindings(bind=False); see that method for why merely
        unbinding is insufficient.

        Args:
            event: The Tkinter scroll event. Accepted and ignored.

        Returns:
            "break", which tells Tk to stop processing this event -- no later
            bindtag in the chain, including "all", will fire for it.
        """
        return "break"

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
                    if abs(self._touchpad_accumulated_delta) >= TOUCHPAD_ACCUMULATION_THRESHOLD:
                        scaled_scroll = -1 if self._touchpad_accumulated_delta > 0 else 1
                        parent_widget.yview_scroll(scaled_scroll, "units")
                        self._touchpad_accumulated_delta = 0.0
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
        Standard layout binding connection pass [1.1].

        RETAINED FOR COMPATIBILITY. Calling this after placing the widget was
        once mandatory; it no longer is, since __init__ binds <Map> and
        activates scrolling automatically. Existing callers that still invoke
        it are harmless -- the underlying toggle is idempotent -- but new code
        shouldn't need it. Composite widgets in this project that rebuild
        their content dynamically (sCTkFileExplorer, sCTkTableview) do still
        call it deliberately, to bind rows created after the initial <Map>.

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