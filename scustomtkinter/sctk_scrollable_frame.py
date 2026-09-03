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

Unlike sCTkFrame (which has no disabled concept at all), this class DOES
have a disabled state, via configure(state="disabled")/get_state(). That's
justified here where it isn't for a plain frame: this widget owns real
behavior to disable, not just colors. Disabling dims the border and the
scrollbar and stops all scrolling -- wheel, trackpad, and scrollbar drag.

It does NOT cascade to child widgets. Disabling children placed inside this
frame is entirely the caller's responsibility, exactly as with the labeled
frame variants -- loop over get_children() and configure(state=...) each one.

state and scroll_enabled are independent axes; see _scroll_effective(). A
frame explicitly set non-scrolling stays non-scrolling across a
disable/enable round trip rather than being switched on by the state change.

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
scrollbar itself stays visible, but is made inert -- it can't be dragged
while scrolling is disabled.

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
import tkinter as tk
from typing import Any, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget
from .sctk_scroll_mixin import ScrollBindingMixin

class sCTkScrollableFrame(ctk.CTkScrollableFrame, ScrollBindingMixin, ThemeableWidget):
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
        `label_fg_color`, `scrollbar_button_color`, `border_color`, `state`,
        and `scroll_enabled` via a single-argument configure() call. For the
        color keys the returned tuple's `default` and `current` positions are
        identical; for `state` and `scroll_enabled` they can differ, since
        those two carry live runtime values.
      - A disabled state (see module docstring): dims border and scrollbar
        and stops all scroll input. Does not cascade to children.
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

    # Theme keys that _update_current_visual_state() re-pushes on every
    # repaint. configure() records these into _local_defaults so a runtime
    # override survives the repaint instead of being reverted by it -- see
    # configure()'s docstring.
    _THEME_TRACKED_KEYS = frozenset({
        "fg_color",
        "border_color",
        "label_fg_color",
        "scrollbar_button_color",
        "scrollbar_button_hover_color",
    })

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

        # 2a. Capture the disabled-state color map. Read from
        # self._widget_disabled_map, NOT from final_kw: ThemeableWidget.__init__
        # deliberately excludes "disabled_map" from final_kw, so reading it
        # there yields an empty dict and every disabled lookup silently falls
        # back -- the confirmed bug pattern fixed in sCTkSwitch, sCTkSpinbox,
        # and sCTkTableview elsewhere in this project.
        # hasattr-guarded for the same reason as _state below: sCTkTableview
        # builds this from the same source before calling super().__init__().
        if not hasattr(self, "_custom_disabled_map"):
            self._custom_disabled_map = dict(self._widget_disabled_map)

        # 2b. Hard-fail on theme gaps rather than substituting a guessed
        # color, matching the principle established across this project.
        # Only the keys that actually change when disabled are required in
        # disabled_map; fg_color deliberately is NOT among them (the content
        # background stays put when disabled -- only the border and the now-
        # inert scrollbar dim).
        #
        # SCOPED TO DIRECT CONSTRUCTION ONLY. A subclass that inherits this
        # class (e.g. sCTkTableview) reaches here with self.final_kw built
        # from ITS OWN theme block, not this one -- ThemeableWidget's
        # run-once guard means the parent's __init__ never rebuilds it. So
        # validating this widget's theme keys against a subclass's theme
        # block would demand scrollbar colors from, say, the sCTkTableview
        # block, and raise KeyError on every construction. Subclasses own
        # their own theme contract and validate it themselves (sCTkTableview
        # does exactly this); this check is for the concrete class only.
        if type(self) is sCTkScrollableFrame:
            for required_key in ("border_color", "scrollbar_button_color",
                                 "scrollbar_button_hover_color"):
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

        # 2c. State and scroll intent. Both must exist before step 4's
        # _update_current_visual_state() call, which reads them.
        #
        # These are two INDEPENDENT axes, deliberately not collapsed into one.
        # _state is the user-facing enabled/disabled presentation;
        # _scroll_enabled is the developer's own intent about whether this
        # frame should scroll at all. Effective scrolling is the AND of the
        # two -- see _scroll_effective(). Because state changes never write
        # to _scroll_enabled, a frame that was constructed or configured
        # non-scrolling stays non-scrolling after a disable/enable round
        # trip, instead of being silently switched on by the state change.
        # A subclass may legitimately establish either of these before calling
        # super().__init__() -- sCTkTableview sets self._state from its own
        # constructor argument, and would otherwise have it silently reset to
        # the default here. hasattr-guarded so the subclass's value wins.
        if not hasattr(self, "_state"):
            self._state = str(self._local_defaults.get("state", "normal"))
        if not hasattr(self, "_scroll_enabled"):
            self._scroll_enabled = bool(self._local_defaults.get("scroll_enabled", True))

        # 3. Initialize CustomTkinter natively with the clean final kwargs array.
        # 3. Initialize CustomTkinter natively. Only forwards the subset of
        # final_kw that native CTkScrollableFrame actually accepts -- see this
        # class's docstring ("WHITELIST GUARD") for why this filtering exists,
        # and why it's especially important for this specific native class.
        native_kwargs = {k: v for k, v in self.final_kw.items() if k in self._NATIVE_CTKSCROLLABLEFRAME_KWARGS}
        super().__init__(master, **native_kwargs)

        # 4. Apply initial theming.
        self._update_current_visual_state()

        # Touchpad accumulator state, owned by ScrollBindingMixin. Must run
        # before any binding happens.
        self._init_scroll_state()

        # 5. Scroll activation. Bindings come up automatically -- no caller
        # action required. An earlier version needed a manual
        # _finalize_split_bindings() call after placement; a scrollable frame
        # that doesn't scroll by default is a confusing thing to ship, given
        # what the widget's own name promises.
        #
        # _state and _scroll_enabled were both established in step 2c, since
        # step 4 above needs them.
        #
        # ScrollBindingMixin installs all four activation mechanisms -- <Map>
        # on this widget, <Map> on _parent_frame, after_idle(), and the
        # debounced <Configure> content rebind -- and documents why each is
        # needed. _parent_frame is passed because it is the widget the
        # geometry manager actually sees; this widget itself is a canvas-window
        # child and may never receive <Map> at all.
        self._install_scroll_activation(
            extra_map_widget=getattr(self, "_parent_frame", None))

    # ------------------------------------------------------------------
    # ScrollBindingMixin contract
    # ------------------------------------------------------------------
    def _scroll_target(self):
        """
        The widget to scroll: this frame's parent canvas, resolved through the
        Tk widget path rather than a CustomTkinter private attribute.

        Returns:
            The canvas, or None if the hierarchy isn't realized yet.
        """
        try:
            parent_widget = self.nametowidget(self.winfo_parent())
            if parent_widget and parent_widget.__class__.__name__ == "Canvas":
                return parent_widget
        except Exception:
            pass
        return None

    def _scroll_layers(self):
        """
        Every widget that should respond to a scroll event over this frame:
        the frame itself, its parent canvas and that canvas's own parent, the
        internal scrollbar, and the full content tree.

        The content walk stops at nested CTkScrollableFrame boundaries -- see
        ScrollBindingMixin._collect_scroll_descendants().

        Returns:
            An ordered, deduplicated list of widgets.
        """
        layers = [self]

        canvas = self._scroll_target()
        if canvas is not None:
            layers.append(canvas)
            try:
                grandparent = self.nametowidget(canvas.winfo_parent())
                if grandparent:
                    layers.append(grandparent)
            except Exception:
                pass

        # The scrollbar is a SIBLING of the canvas, not a descendant of this
        # frame, so the content walk below would never reach it -- it has to
        # be added explicitly or the wheel does nothing while the pointer is
        # over the scrollbar itself.
        if getattr(self, "_scrollbar", None) is not None:
            self._collect_scroll_descendants(self._scrollbar, layers)

        self._collect_scroll_descendants(self, layers)
        return layers

    def _scroll_permitted(self) -> bool:
        """The AND of scroll_enabled and state. See _scroll_effective()."""
        return self._scroll_effective()

    def _scroll_drag_targets(self):
        """The internal scrollbar, whose dragging is blocked when disabled."""
        bar = getattr(self, "_scrollbar", None)
        return [bar] if bar is not None else []


    def _scroll_effective(self) -> bool:
        """
        Whether this widget should actually respond to scroll input right now.

        The AND of the two independent axes described in __init__ step 2c:

            scroll_enabled | state     | scrolls?
            ---------------+-----------+---------
            True           | normal    | yes
            True           | disabled  | no
            False          | normal    | no
            False          | disabled  | no

        Every place that binds or unbinds routes through here rather than
        reading either flag directly, so the two can't drift apart.

        Returns:
            True only if scrolling is both wanted and permitted.
        """
        return self._scroll_enabled and self._state == "normal"

    def is_scrolling(self) -> bool:
        """
        Whether this widget currently responds to scroll input.

        Distinct from cget("scroll_enabled"), which reports stored INTENT.
        A frame with scroll_enabled=True that has been disabled via
        configure(state="disabled") reports True from cget and False from
        here -- that difference is the point: the intent survives the state
        change so it can be restored when the state goes back to normal.

        Returns:
            The live effective scroll state.
        """
        return self._scroll_effective()

    def get_state(self) -> str:
        """
        Returns the current state, "normal" or "disabled". Mirrors the same
        accessor on sCTkFrameLabeledPrimary/Secondary.
        """
        return self._state

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

        Blocks native CTk's own global mouse-wheel handling as well as this
        file's custom bindings, and blocks click-and-drag on the internal
        scrollbar -- see _toggle_scroll_bindings(bind=False) and
        ScrollBindingMixin._set_scroll_drag_blocked() for the two mechanisms.

        NOTE: the scrollbar remains VISIBLE, just inert -- it can't be
        dragged, but it isn't hidden. CustomTkinter's scrollbar has no
        disabled state to lock (confirmed by direct investigation earlier in
        this project's audit), so there's no greyed-out appearance to switch
        to either. Hiding it entirely is a separate concern, handled
        elsewhere in this project by color-matching and zero width.
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
                if pname == "state":
                    return (pname, pname, pname,
                            str(self._local_defaults.get("state", "normal")),
                            str(self._state))
                if pname == "scroll_enabled":
                    # Unlike the color properties above, this one reports live
                    # state in the `current` position: `default` is the value
                    # the widget was constructed with, `current` is whatever
                    # enable_scroll()/disable_scroll() last set.
                    return (pname, pname, pname,
                            str(self._local_defaults.get("scroll_enabled", True)),
                            str(self._scroll_enabled))
                # FIX: do NOT forward pname to native configure(). Unlike
                # CTkFrame -- whose signature is configure(require_redraw=False,
                # **kwargs) and so silently swallows a positional --
                # CTkScrollableFrame.configure() is declared configure(self,
                # **kwargs) and accepts NO positional argument at all. Passing
                # one raised "CTkScrollableFrame.configure() takes 1 positional
                # argument but 2 were given".
                #
                # This surfaced through Pygubu Designer: blanking a property in
                # the inspector makes it call widget.configure(pname) to
                # discover that property's default value, which reaches this
                # branch for any name not handled above.
                #
                # A Tkinter-style 5-tuple is returned instead, built from
                # cget() so the reported value is real. Returning None is not an
                # option -- callers index into the tuple.
                try:
                    current = self.cget(pname)
                except Exception:
                    current = None
                return (pname, pname, pname, current, current)

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
            # _toggle_scroll_bindings() is idempotent either way. Routed
            # through _scroll_effective() so enable_scroll() on a widget
            # that's currently state="disabled" records the intent without
            # actually re-enabling scrolling behind the disabled presentation.
            self._toggle_scroll_bindings(bind=self._scroll_effective())

        # state is likewise this library's own property, not a native CTk one,
        # and must be popped before the super() call for the same reason.
        if "state" in kwargs:
            self._state = str(kwargs.pop("state"))
            self._toggle_scroll_bindings(bind=self._scroll_effective())
            self._update_current_visual_state()

        # FIX: record theme overrides BEFORE the repaint below.
        #
        # _update_current_visual_state() re-pushes every tracked color from
        # self._local_defaults. Since configure() never wrote to that dict,
        # the sequence was: super().configure(fg_color="red") turns the widget
        # red, then the repaint immediately overwrites it with the theme value
        # -- so runtime color overrides silently did nothing.
        #
        # The repaint isn't wrong to exist (appearance-mode switches and state
        # changes both need it); it was wrong to treat _local_defaults as
        # authoritative when configure() had just introduced a newer value it
        # never recorded. Writing the override in first makes the repaint
        # reproduce it rather than revert it, and makes the override survive
        # later appearance-mode and state changes -- matching CustomTkinter's
        # own semantics, where configure(fg_color=...) sticks.
        #
        # Note this stores exactly what the caller passed: a single color
        # replaces the theme's (light, dark) tuple for that key, so appearance
        # tracking for it is intentionally given up. That's what asking for
        # one specific color means.
        #
        # disabled_map still wins while disabled -- an override here sets the
        # NORMAL-state color. See _update_current_visual_state()'s themed().
        for key in self._THEME_TRACKED_KEYS:
            if key in kwargs:
                self._local_defaults[key] = kwargs[key]

        # Re-checked after the pops above: configure(scroll_enabled=...) or
        # configure(state=...) on its own leaves kwargs empty, and there's no
        # reason to call through to the native widget for it.
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
        if attribute_name == "state":
            return self._state
        return super().cget(attribute_name)

    def _update_current_visual_state(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file.

        Called after construction and on every keyword configure() call.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.
        Every value here traces back to sCTkThemes.json; there are no
        hardcoded colors in this method. The .get() calls carry no fallback
        because __init__ already hard-failed on any missing key.
        """
        is_disabled = self._state == "disabled"

        def themed(key: str) -> Any:
            """Disabled-state value when disabled and one exists, else normal."""
            if is_disabled and self._custom_disabled_map.get(key) is not None:
                return self._custom_disabled_map[key]
            return self._local_defaults.get(key)

        config_payload = {}
        for key in ("fg_color", "border_color", "label_fg_color"):
            val = themed(key)
            if val is not None:
                config_payload[key] = val

        if config_payload:
            super().configure(**config_payload)

        # Re-theme the internal scrollbar, which isn't automatically covered
        # by the configure() call above.
        if hasattr(self, "_scrollbar") and self._scrollbar:
            try:
                normal_bar = themed("scrollbar_button_color")
                # When disabled the scrollbar is inert (drag is blocked), so
                # it must not light up on hover either -- a bright hover would
                # falsely advertise it as draggable. Read from disabled_map
                # like any other dimmed color; themed() falls back to the
                # normal hover color automatically when not disabled.
                normal_hover = themed("scrollbar_button_hover_color")
                self._scrollbar.configure(button_color=normal_bar, button_hover_color=normal_hover)

                if hasattr(self._scrollbar, "_draw"):
                    self._scrollbar._draw()
            except Exception:
                pass

    # =========================================================================
    # SCROLL-HANDLING METHODS BELOW: UNCHANGED FROM THE ORIGINAL. See module
    # docstring. Do not modify without extensive real-device testing.
    # =========================================================================


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
        # Routed through _scroll_effective() rather than forcing bind=True:
        # composite widgets in this project call this after rebuilding their
        # content, and a rebuild must not silently re-enable scrolling on a
        # frame that is disabled or was explicitly set non-scrolling.
        self._toggle_scroll_bindings(bind=self._scroll_effective())

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