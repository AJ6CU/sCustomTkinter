#!/usr/bin/python3
"""
ScrollBindingMixin

The single, shared implementation of cross-platform mouse wheel and macOS
trackpad scroll handling for this library.

WHY THIS EXISTS. This logic previously existed as three independent copies --
in sCTkScrollableFrame, in sCTkFileExplorer, and in sCTkScrollArea -- each
adapted by hand from the first. They drifted, as duplicated code does:

  - The two's-complement sign correction disagreed. sCTkScrollableFrame used
    `>= 0x8000`; sCTkScrollArea used `> 32768`. Those differ at exactly
    32768, which one treats as +32768 and the other as -32768.
  - sCTkScrollArea decoded the packed touchpad delta differently again,
    reading event.delta_y when present and applying a 16-bit correction to
    what may be a 32-bit packed value.
  - Windows wheel scaling disagreed: `/120` unscaled in sCTkScrollableFrame,
    `/120 * 2` in sCTkScrollArea.
  - sCTkFileExplorer had no touchpad ACCUMULATOR at all -- it scrolled on
    every raw touchpad event instead of gating on an accumulated threshold,
    making trackpad scrolling markedly faster and coarser there.
  - The nested-scrollable boundary guard existed in exactly one of the three.

Every fix had to be made three times, and none of them were. This module is
the one place that logic now lives.

CANONICAL SOURCE. The behavior here is sCTkScrollableFrame's implementation,
which is the maintainer-verified reference confirmed smooth in live testing
on macOS with both an Apple mouse and a trackpad. Where the three copies
disagreed, sCTkScrollableFrame's version wins. Adopting this mixin therefore
CHANGES BEHAVIOR in the other two hosts -- see the module's integration
notes and retest accordingly.

PLATFORM BEHAVIOR. Three genuinely different platform models are handled:
  - Windows: <MouseWheel> with a /120-scaled delta.
  - Linux:   discrete <Button-4>/<Button-5> events, no continuous delta.
  - macOS:   its own <MouseWheel> scaling, PLUS a separate, higher-precision
             <TouchpadScroll> synthetic event carrying a two-axis delta
             packed into a single 32-bit integer.

HOST REQUIREMENTS. A host class must provide:

    _scroll_target()  -> the widget to call yview_scroll() on, or None if
                         scrolling isn't currently possible.
    _scroll_layers()  -> the ordered list of widgets to bind, deduplicated.

and may optionally override:

    _scroll_permitted()      -> False to install BLOCKING handlers instead of
                                scroll handlers (default True).
    _scroll_drag_targets()   -> widgets whose click-drag should also be
                                blocked when not permitted (default none).

Hosts must call _init_scroll_state() once, before any binding happens.
"""
import sys
import tkinter as tk
import platform

import customtkinter as ctk


class ScrollBindingMixin:
    """Shared scroll-binding engine. See module docstring for the contract."""

    # Bound on every layer. <TouchpadScroll> is macOS-only and is skipped
    # elsewhere; binding it on other platforms raises in Tk.
    SCROLL_EVENTS = ("<MouseWheel>", "<TouchpadScroll>", "<Button-4>", "<Button-5>")

    # Click-drag events blocked on scrollbar-like widgets when scrolling is
    # not permitted. See _set_scroll_drag_blocked().
    DRAG_EVENTS = ("<Button-1>", "<B1-Motion>", "<ButtonRelease-1>")

    # macOS wheel events carry a much smaller delta than Windows' /120 steps,
    # so they're amplified to give comparable travel per notch.
    MAC_SCROLL_SENSITIVITY = 3

    # Trackpad events arrive far more frequently and with far finer deltas
    # than wheel notches. Scrolling on each one is unusably fast, so deltas
    # accumulate and only move the view once this threshold is crossed.
    # Tuned empirically; do not change without live trackpad testing.
    TOUCHPAD_ACCUMULATION_THRESHOLD = 12.0

    # ------------------------------------------------------------------
    # Host contract
    # ------------------------------------------------------------------
    def _scroll_target(self):
        """The widget to scroll. Hosts MUST override."""
        raise NotImplementedError(
            f"{type(self).__name__} uses ScrollBindingMixin but does not "
            f"implement _scroll_target()."
        )

    def _scroll_layers(self):
        """Ordered, deduplicated list of widgets to bind. Hosts MUST override."""
        raise NotImplementedError(
            f"{type(self).__name__} uses ScrollBindingMixin but does not "
            f"implement _scroll_layers()."
        )

    def _scroll_permitted(self) -> bool:
        """
        Whether scrolling should currently respond. Hosts that support a
        disabled state override this; the default is always-on.
        """
        return True

    def _scroll_drag_targets(self):
        """
        Widgets whose click-and-drag should also be blocked when scrolling
        isn't permitted -- typically an internal scrollbar. Default: none.
        """
        return []

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _init_scroll_state(self) -> None:
        """Initializes the touchpad accumulator. Call once, before binding."""
        self._touchpad_accumulated_delta = 0.0
        self._touchpad_last_direction = 0
        self._scroll_rebind_pending = False

    def _install_scroll_activation(self, extra_map_widget=None) -> None:
        """
        Establishes automatic scroll activation and content-change rebinding.

        Call once from the host's __init__, after the widget hierarchy exists.
        Requires _init_scroll_state() to have run first.

        FOUR MECHANISMS, each covering a gap the others don't. All are
        idempotent -- _toggle_scroll_bindings() always tears down before
        rebuilding -- so overlapping coverage costs nothing:

          <Map> on self          later remaps, e.g. pack_forget() then re-place
          <Map> on extra widget  the widget the geometry manager actually sees
          after_idle()           initial activation, independent of mapping
          <Configure>, debounced content added AFTER activation

        WHY <Map> ALONE ISN'T ENOUGH. CTkScrollableFrame is not the widget
        that gets placed: it builds an internal _parent_frame plus a canvas,
        inserts ITSELF into that canvas via create_window(), and overrides
        pack()/grid()/place() to operate on _parent_frame. The widget is
        therefore a canvas-window child and may never receive <Map> the way an
        ordinarily-managed widget does. after_idle() is what actually
        establishes bindings in practice -- it fires once Tk goes idle, after
        setup code has run and placement has happened, with no dependence on
        mapping semantics at all.

        WHY THE CONTENT REBIND IS NEEDED. Activation happens once, at a moment
        when the frame is usually still empty -- callers construct, place, and
        THEN populate. Confirmed by live testing: an sCTkTableview bound at
        activation time collected 16 layers (frame, canvas, header cells)
        because load_dataset() hadn't run yet, and the 32 data cells created
        afterwards were never bound, so it scrolled beside its rows but not
        over them.

        CRITICAL -- tk.Misc.bind, NOT self.bind. CustomTkinter overrides
        CTkScrollableFrame.bind() to forward every binding to
        self._parent_canvas instead of attaching it to the widget. An earlier
        version used self.bind(), so bindings never landed on the frame and
        scroll handling was silently never installed -- the widget only
        appeared to scroll where native CTk's own global bind_all handler
        happened to cover for it. Calling tk.Misc.bind unbound reaches the
        real Tkinter implementation. This looks like a needless complication
        and is not.

        Args:
            extra_map_widget: An additional widget to watch for <Map>,
                typically the host's internal _parent_frame -- the widget the
                geometry manager actually sees. Optional.
        """
        tk.Misc.bind(self, "<Map>", self._activate_scroll_bindings, add="+")

        if extra_map_widget is not None:
            try:
                tk.Misc.bind(extra_map_widget, "<Map>", self._activate_scroll_bindings, add="+")
            except Exception:
                pass

        try:
            self.after_idle(self._activate_scroll_bindings)
        except Exception:
            pass

        tk.Misc.bind(self, "<Configure>", self._schedule_scroll_rebind, add="+")

    def _activate_scroll_bindings(self, event=None) -> None:
        """
        Binds or blocks scroll handling according to the host's current
        permitted state. The single entry point every activation path uses,
        so none of them can drift apart.

        Deliberately does NOT return early when scrolling isn't permitted: it
        runs a full pass to install the BLOCKING handlers described in
        _toggle_scroll_bindings(). That matters for the
        construct-then-disable-then-place ordering, where the earlier pass had
        no realized hierarchy to install onto.

        Args:
            event: The Tkinter event, when called from a binding. Ignored.
        """
        self._toggle_scroll_bindings(bind=self._scroll_permitted())

    def _schedule_scroll_rebind(self, event=None) -> None:
        """
        Requests a rebind, coalescing bursts into a single pass.

        Bound to <Configure>, which fires once per child added. The pending
        flag means a burst of additions schedules exactly one rebind, run
        after the burst finishes rather than during it -- so the rebind sees
        the finished widget tree, not a partial one. Building a table fires
        <Configure> once per cell; this makes that one rebind instead of 32.

        Args:
            event: The Tkinter <Configure> event. Ignored.
        """
        if getattr(self, "_scroll_rebind_pending", False):
            return
        self._scroll_rebind_pending = True
        try:
            self.after_idle(self._run_scheduled_scroll_rebind)
        except Exception:
            # Widget destroyed mid-flight; nothing to rebind.
            self._scroll_rebind_pending = False

    def _run_scheduled_scroll_rebind(self) -> None:
        """Executes a coalesced rebind. See _schedule_scroll_rebind()."""
        self._scroll_rebind_pending = False
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return
        self._activate_scroll_bindings(None)

    # ------------------------------------------------------------------
    # Layer collection
    # ------------------------------------------------------------------
    def _collect_scroll_descendants(self, widget, collected: list) -> None:
        """
        Recursively collects a widget and its descendants for binding.

        Stops at any nested CTkScrollableFrame boundary (covering
        sCTkScrollableFrame and anything built on it, such as sCTkSelector
        and sCTkTableview). Without this, an inner scrollable frame placed
        inside an outer one would have its canvas, scrollbar, and entire
        content tree bound to the OUTER host's handler as well as its own --
        and since bindings use add="+", both fire on the same event,
        scrolling both at once. Native CustomTkinter guards the same boundary
        in _check_if_valid_scroll.

        Args:
            widget: Subtree root. Never skipped itself, even if it is a
                scrollable frame -- the guard applies to descendants only, so
                a scrollable host can still bind its own layers.
            collected: Accumulator, mutated in place.
        """
        if widget is not self and isinstance(widget, ctk.CTkScrollableFrame):
            return
        if widget not in collected:
            collected.append(widget)
        try:
            for child in widget.winfo_children():
                self._collect_scroll_descendants(child, collected)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Binding
    # ------------------------------------------------------------------
    def _toggle_scroll_bindings(self, bind: bool = True) -> None:
        """
        Establishes or removes every scroll binding for this host.

        Args:
            bind: True (re)establishes all bindings -- safe to call
                repeatedly, since existing bindings are always removed first,
                so nothing accumulates. False removes them and installs
                BLOCKING handlers in their place.

        On blocking: unbinding alone does NOT stop scrolling. Native
        CTkScrollableFrame installs its own application-global
        bind_all("<MouseWheel>") handler that survives any unbind() here, and
        unbind_all() is not an option -- it would disable scrolling for every
        other scrollable widget in the application. Instead a handler
        returning "break" is installed on each layer. Tk dispatches bindings
        by bindtag in order -- widget, class, toplevel, then "all" -- and
        bind_all lands on that final tag, so a widget-level "break" halts the
        chain before the global handler is ever reached. Confirmed by live
        testing: with two independent scrollable frames side by side,
        disabling one left the other scrolling normally with both a mouse
        wheel and a trackpad.
        """
        # Hosts may expose _USE_CUSTOM_SCROLL_BINDING as a kill switch for the
        # custom binding system, falling back to whatever native CustomTkinter
        # provides. Checked here rather than at the call sites so it can't be
        # bypassed by reaching this method through a different entry point --
        # the exact bug that made the toggle ineffective in an earlier
        # sCTkScrollableFrame revision. Defaults to enabled for hosts that
        # don't define it.
        if bind and not getattr(self, "_USE_CUSTOM_SCROLL_BINDING", True):
            return

        layers = self._scroll_layers()

        for layer in layers:
            for event_str in self.SCROLL_EVENTS:
                try:
                    layer.unbind(event_str)
                except Exception:
                    pass

                # <TouchpadScroll> exists only on macOS.
                if "Touchpad" in event_str and sys.platform != "darwin":
                    continue

                if bind:
                    handler = (self._process_mac_touchpad_scroll
                               if "Touchpad" in event_str
                               else self._process_scroll_wheel)
                else:
                    handler = self._block_scroll_event

                try:
                    layer.bind(event_str, handler, add="+")
                except Exception:
                    pass

        self._set_scroll_drag_blocked(not bind)

    def _block_scroll_event(self, event=None) -> str:
        """
        Swallows a scroll event so it never reaches native CTk's global
        bind_all handler. See _toggle_scroll_bindings() for why unbinding
        alone is insufficient.

        Returns:
            "break", halting Tk's bindtag chain for this event.
        """
        return "break"

    def _set_scroll_drag_blocked(self, blocked: bool) -> None:
        """
        Blocks or restores click-and-drag on the host's _scroll_drag_targets().

        Deliberately does NOT use unbind(). Tk's unbind() removes EVERY
        binding for an event on a widget, so calling it on a scrollbar's
        <Button-1> would destroy CustomTkinter's own drag handler
        permanently, with no way to restore it. Binding a blocker with
        add="+" doesn't work either: handlers on one widget fire in the order
        added, and CustomTkinter's was added during its own construction, so
        ours would run after the drag had already been handled -- returning
        "break" at that point is too late.

        Uses bindtags instead, the mechanism Tk provides for exactly this.
        Inserting a private tag at the FRONT of a widget's tag list means the
        blocker runs before any of CustomTkinter's own bindings, so "break"
        stops them before they execute. Restoring is just removing the tag;
        CustomTkinter's bindings are never touched.

        The tag name embeds id(self), so blocking one host has no effect on
        any other in the same application.

        Args:
            blocked: True installs the block, False removes it.
        """
        targets = []
        for widget in self._scroll_drag_targets():
            if widget is None:
                continue
            targets.append(widget)
            # The click lands on a CTk composite's internal canvas, not its
            # outer frame, so children need the tag too.
            try:
                targets.extend(widget.winfo_children())
            except Exception:
                pass

        if not targets:
            return

        tag = f"sCTkScrollDragBlock{id(self)}"
        for event_str in self.DRAG_EVENTS:
            try:
                self.bind_class(tag, event_str, self._block_scroll_event)
            except Exception:
                pass

        for widget in targets:
            try:
                tags = list(widget.bindtags())
                if blocked and tag not in tags:
                    widget.bindtags(tuple([tag] + tags))
                elif not blocked and tag in tags:
                    widget.bindtags(tuple(t for t in tags if t != tag))
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Event processing
    # ------------------------------------------------------------------
    @staticmethod
    def _decode_mac_touchpad_delta(raw_delta):
        """
        Decodes macOS's packed 32-bit <TouchpadScroll> delta into signed
        16-bit X and Y components.

        The event packs both axes into one integer: X in the high 16 bits, Y
        in the low 16. Each is an UNSIGNED 16-bit field that must be
        converted back to signed, or every upward scroll reads as a large
        positive number instead of a negative one.

        The `>= 0x8000` comparison is the canonical form. An earlier copy in
        sCTkScrollArea used `> 32768`, which is off by one: 32768 is the
        smallest negative value in a signed 16-bit field (-32768), and that
        version treated it as +32768 instead.

        Args:
            raw_delta: The event's raw packed delta.

        Returns:
            (delta_x, delta_y) as signed integers.
        """
        raw = raw_delta & 0xFFFFFFFF
        delta_x = (raw >> 16) & 0xFFFF
        if delta_x >= 0x8000:
            delta_x -= 0x10000
        delta_y = raw & 0xFFFF
        if delta_y >= 0x8000:
            delta_y -= 0x10000
        return delta_x, delta_y

    def _process_mac_touchpad_scroll(self, event):
        """
        Handles macOS <TouchpadScroll>, accumulating fine-grained deltas and
        moving the view only once TOUCHPAD_ACCUMULATION_THRESHOLD is crossed.

        The accumulator resets on a direction reversal, so a change of
        direction responds immediately rather than having to first cancel out
        whatever had built up in the opposite direction.

        NOTE: sCTkFileExplorer's previous copy had no accumulator at all --
        it scrolled on every raw event, making trackpad scrolling markedly
        faster and coarser than everywhere else in the library. Adopting this
        mixin brings it in line.
        """
        target = self._scroll_target()
        if target is None:
            return
        try:
            _, delta_y = self._decode_mac_touchpad_delta(event.delta)
            if delta_y == 0:
                return

            direction = 1 if delta_y > 0 else -1
            if direction != self._touchpad_last_direction and self._touchpad_last_direction != 0:
                self._touchpad_accumulated_delta = 0.0
            self._touchpad_last_direction = direction

            self._touchpad_accumulated_delta += delta_y

            if abs(self._touchpad_accumulated_delta) >= self.TOUCHPAD_ACCUMULATION_THRESHOLD:
                scaled_scroll = -1 if self._touchpad_accumulated_delta > 0 else 1
                target.yview_scroll(scaled_scroll, "units")
                self._touchpad_accumulated_delta = 0.0
        except Exception:
            pass

    def _process_scroll_wheel(self, event):
        """
        Handles standard mouse wheel events across all three platforms.

        Windows scaling is `/120` unscaled -- the canonical form.
        sCTkScrollArea's previous copy doubled it, scrolling twice as far per
        notch as everywhere else in the library.
        """
        target = self._scroll_target()
        if target is None:
            return
        try:
            sys_platform = platform.system()
            if sys_platform == "Darwin":
                delta = event.delta
                scaled_scroll = (int(-self.MAC_SCROLL_SENSITIVITY * delta)
                                 if abs(delta) >= 1
                                 else (-self.MAC_SCROLL_SENSITIVITY if delta > 0
                                       else self.MAC_SCROLL_SENSITIVITY))
                target.yview_scroll(scaled_scroll, "units")
            elif sys_platform == "Linux":
                # Linux has no continuous delta -- discrete button events only.
                if event.num == 4:
                    target.yview_scroll(-1, "units")
                elif event.num == 5:
                    target.yview_scroll(1, "units")
            else:
                target.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass
