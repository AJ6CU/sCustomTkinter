#!/usr/bin/python3
"""
sCTkSwitch

A theme-compliant toggle switch widget. Inherits directly from ctk.CTkSwitch
so CustomTkinter handles native rendering and drag/click behavior; this class
layers automatic light/dark theme resolution and a distinct enabled/disabled
visual state on top.

Base class order matters here: `class sCTkSwitch(ctk.CTkSwitch,
ThemeableWidget)` puts the native CTk class first, so every `super()` call in
this file's own methods resolves to ctk.CTkSwitch -- and, beneath it,
tkinter.Misc -- never to ThemeableWidget. ThemeableWidget's own
configure()/cget()/_set_appearance_mode() overrides have been removed entirely
for this reason (see themeable_widget.py's docstring); this widget owns all of
its own runtime color-swapping logic.

Two things about this file are architecturally different from every other
widget in this project, worth understanding before editing it:

1. configure()'s signature is `configure(self, require_redraw=None, **kwargs)`
   rather than `configure(self, *args, **kwargs)`. This mirrors real CTk's own
   configure() signature convention (confirmed via ThemeableWidget's own
   handling of it) rather than using *args. Because of this, the single-arg
   query bug that affected almost every other widget in this project (a
   wrapped tuple never matching a string comparison) never existed here in
   the first place -- `require_redraw` receives the actual passed value
   directly (a string, a dict, whatever), with no unwrapping needed. No fix
   was required for this file's argument handling.

2. Disabling uses a different, more robust mechanism than the button family's
   original (confirmed-broken) manual canvas.unbind() approach: it prepends a
   dedicated bindtag (self._block_tag) to the canvas's and text label's
   bindtags, with a class-level binding that returns "break" on <Button-1>.
   Since Tkinter processes bindtags in order and "break" halts further
   propagation, this intercepts clicks regardless of which underlying level
   the real click handler is bound at -- unlike plain unbind(), which only
   removes widget-level bindings and was confirmed to miss the actual handler
   on CTkButton. This is combined with native state="disabled" as well
   (belt-and-suspenders). Left as-is; not confirmed broken, and the mechanism
   itself is sound, but not independently re-tested as part of this project's
   audit.
"""
from typing import Any, Callable, Optional
import customtkinter as ctk
from .themeable_widget import ThemeableWidget


class sCTkSwitch(ctk.CTkSwitch, ThemeableWidget):
    """Themeable toggle switch.

    Adds to native ctk.CTkSwitch:
      - Automatic light/dark theme resolution from sCTkThemes.json (via
        ThemeableWidget.__init__ -- see that class's docstring for what it does,
        and just as importantly, what it no longer does).
      - A distinct enabled/disabled visual state, using both native
        state="disabled" and a bindtag-based click interceptor (see module
        docstring).
      - Pygubu Designer property introspection for "state" via a single-
        argument configure() call, plus a cget() override for both "state"
        and "command".
      - A command-forwarding wrapper that tries calling the user's command
        with the switch's current value, falling back to calling it with no
        arguments if that raises TypeError -- accommodating both
        `command=lambda val: ...` and `command=lambda: ...` styles.

    Colors are passed through to configure() as raw (light, dark) tuples rather
    than pre-resolved to a single value, so CustomTkinter's own appearance-mode
    tracking repaints them automatically on a light/dark switch -- the same
    approach validated on sCTkComboBox, sCTkSegmentedButton, and the button
    family. Not separately re-confirmed for this specific widget.

    HISTORY: an earlier version of this file only ever varied text_color by
    state, leaving fg_color/progress_color/button_color/button_hover_color
    fixed regardless of disabled state, with a comment claiming this was
    deliberate. It wasn't -- full dimming had previously been attempted and
    abandoned after repeated failures, which is also why a separate widget
    (sCTkSwitchAlt) exists, built specifically to work around this and a
    related light-mode visibility problem (the button/handle, white in the
    stock theme, visually fades into a light background). Full dimming is now
    confirmed working by direct testing, once several infrastructure bugs
    elsewhere in this file were fixed (the tuple-vs-resolved-color pattern,
    an always-empty _custom_disabled_map caused by reading "disabled_map" out
    of final_kw -- where ThemeableWidget deliberately never puts it -- instead
    of the correctly-populated _widget_disabled_map, and hardcoded fallback
    colors masking the real theme values). The handle-fading-into-background
    problem is separate and still open -- see _resolve_bg_color() below for
    an experimental fix targeting that specifically, adapted from the
    approach sCTkSwitchAlt already uses successfully.
    """



    # EXPERIMENTAL TOGGLE -- see _resolve_bg_color() for what this changes.
    # False (default): bg_color is left at whatever CTkSwitch's own default
    #   handling produces -- the current behavior, and the source of the
    #   confirmed handle-fading-into-background problem in light mode (a
    #   white button_color against a bg_color that doesn't correctly match
    #   the actual parent background).
    # True: explicitly resolves and sets bg_color to the parent's real
    #   fg_color at construction, adapted from the same approach
    #   sCTkSwitchAlt already uses successfully (its _apply_parent_bg_handshake()),
    #   but passing a real (light, dark) tuple rather than a single resolved
    #   string, since sCTkSwitch's bg_color -- unlike a raw tk.Canvas's "bg"
    #   option -- is a genuine CTk color property that supports tuples.
    #   Untested as of this writing.
    _EXPLICITLY_RESOLVE_BG_COLOR = False

    def __init__(
        self,
        master: Optional[Any] = None,
        onvalue: Any = 1,
        offvalue: Any = 0,
        command: Optional[Callable] = None,
        **kw: Any,
    ) -> None:
        """
        Args:
            master: Parent container.
            onvalue: Value reported when the switch is on.
            offvalue: Value reported when the switch is off.
            command: Called on toggle. May accept the new value as a single
                argument, or no arguments at all -- see this class's docstring.
            **kw: `state` is pulled out explicitly below. Everything else is
                either a native CTkSwitch argument or a theme-key override
                (see the "sCTkSwitch" block in sCTkThemes.json). Color-related
                theme keys and "disabled_map" itself are stripped out of the
                kwargs sent to the native constructor -- they're applied
                separately via _apply_custom_theme_colors() below.
        """
        # 1. Fire our shared theme logic. This resolves final_kw
        # (construction-time properties). See ThemeableWidget.__init__ for
        # what actually happens here.
        ThemeableWidget.__init__(self, kw)

        # 2. Store the resolved maps onto this instance.
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 3. Extract the initial state and value-related config early.
        state_val = kw.pop("state", "normal")
        self._custom_current_state = "normal" if str(state_val).lower() == "normal" else "disabled"
        self._onvalue_payload = onvalue
        self._offvalue_payload = offvalue
        self._user_command = command

        # 4. Strip color-related theme keys (and disabled_map itself) out of
        # final_kw before construction -- these are applied afterward via
        # _apply_custom_theme_colors(), not passed to the native constructor.
        for pop_key in ["fg_color", "progress_color", "button_color", "button_hover_color",
                        "text_color", "font", "disabled_map"]:
            self.final_kw.pop(pop_key, None)

        # 5. Wrap the user's command so it can be called with or without an
        # argument -- see this class's docstring.
        wrapped_command = None
        if self._user_command:
            wrapped_command = self._execute_safe_command_forwarding

        # 5b. EXPERIMENTAL (see _EXPLICITLY_RESOLVE_BG_COLOR): resolve and
        # pass bg_color explicitly, so it doesn't fall back to whatever
        # CTkSwitch's own default handling produces.
        if self._EXPLICITLY_RESOLVE_BG_COLOR:
            self.final_kw["bg_color"] = self._resolve_bg_color(master)

        # 6. Initialize CustomTkinter natively with the clean final kwargs array.
        super().__init__(master, onvalue=onvalue, offvalue=offvalue, command=wrapped_command, **self.final_kw)

        # 7. Set up the bindtag-based click interceptor -- see module docstring.
        self._block_tag = f"sCTkSwitchBlock_{id(self)}"
        if hasattr(self, "_canvas") and self._canvas.winfo_exists():
            self._canvas.bind_class(self._block_tag, "<Button-1>", lambda e: "break")
            self._canvas.bindtags((self._block_tag,) + self._canvas.bindtags())
        if hasattr(self, "_text_label") and self._text_label.winfo_exists():
            self._text_label.bind_class(self._block_tag, "<Button-1>", lambda e: "break")
            self._text_label.bindtags((self._block_tag,) + self._text_label.bindtags())

        # 8. Apply initial theming and complete lifecycle registration.
        self._apply_custom_theme_colors()
        if self._custom_current_state == "disabled":
            self.configure(state="disabled")
        self._finalize_themeable_lifecycle()

    def _resolve_bg_color(self, master: Any) -> Any:
        """
        EXPERIMENTAL (see _EXPLICITLY_RESOLVE_BG_COLOR): determines what
        bg_color this widget should use so it doesn't fall back to some
        default that can cause a light-colored button/handle to visually
        blend into the actual background -- confirmed happening in light
        mode via direct testing (screenshot review).

        Adapted from sCTkSwitchAlt's _apply_parent_bg_handshake(), which
        solves the same underlying problem for a raw tk.Canvas (which cannot
        render CTk's "transparent" pseudo-color at all, unlike this widget's
        bg_color, which is a real CTk color property). Returns a (light, dark)
        tuple rather than a single resolved string, so CTk's own
        appearance-mode tracking can handle the two variants automatically,
        consistent with the tuple-based approach used throughout this project
        -- unlike sCTkSwitchAlt, which had to resolve to one literal color
        immediately because a raw Canvas has no such tracking of its own.

        Args:
            master: This widget's parent, whose fg_color is used as the
                basis for the resolved bg_color.

        Returns:
            A (light, dark) tuple. Falls back to a fixed neutral pair if the
            parent's fg_color can't be read, or is itself "transparent".
        """
        fallback = ("#F1F5F9", "#1C1C1C")

        try:
            parent_fg = master.cget("fg_color")
        except Exception:
            return fallback

        if isinstance(parent_fg, str) and parent_fg.lower() == "transparent":
            return fallback
        if isinstance(parent_fg, (tuple, list)) and len(parent_fg) == 2:
            return tuple(parent_fg)
        if isinstance(parent_fg, str):
            return (parent_fg, parent_fg)
        return fallback

    def _execute_safe_command_forwarding(self) -> None:
        """
        Calls the user's command, first trying with the switch's current
        value as a single argument, falling back to calling with no arguments
        if that raises TypeError.

        Confirmed by direct testing: exceptions from the user's command
        propagate normally (an earlier version swallowed all of them
        silently -- no error, no traceback, nothing, which hid real bugs
        completely). Tkinter's own default callback-exception handling
        reports propagated exceptions to the console without crashing the
        running application.

        KNOWN, UNFIXED ISSUE: the inner `except TypeError` can't distinguish
        "your command doesn't accept an argument" from "your command raised a
        TypeError for some unrelated reason inside its own body." Either one
        triggers the same fallback -- calling the command AGAIN, with no
        arguments. A genuine TypeError bug in a one-argument command will
        therefore raise a second, confusing "missing required argument" error
        on top of the real one -- confirmed by direct testing. Python's
        exception chaining keeps both tracebacks visible (the real bug prints
        first, followed by "During handling of the above exception..."), so
        the bug isn't hidden, just noisier than necessary. Fixing this
        properly would mean checking the command's actual signature (e.g. via
        inspect.signature(...).bind(...)) before calling it, rather than
        inferring compatibility from a caught exception -- not yet
        implemented.
        """
        if not self._user_command:
            return

        active_val = self.get()

        try:
            self._user_command(active_val)
        except TypeError:
            self._user_command()

    def configure(self, require_redraw: Any = None, **kwargs: Any) -> Any:
        """
        Standard widget configuration, with Pygubu/positional-argument handling.

        Args:
            require_redraw: Despite the name (matching real CTk's own
                configure() signature), this parameter doubles as the
                Pygubu single-argument query slot when called positionally:
                - the literal string "state": returns a Tkinter-style
                  (name, name, name, default, current) tuple.
                - a dict: merged into kwargs and processed normally below.
                - anything else (a string): forwarded directly to the native
                  widget's configure().
                When called as an actual keyword (require_redraw=True/False),
                behaves as CTk's native redraw-control flag.
            **kwargs: Standard CTkSwitch configuration options, plus:
                `state` updates self._custom_current_state and is also
                forwarded to the native configure(); `command` is re-wrapped
                through _execute_safe_command_forwarding(); `onvalue`/
                `offvalue` update the cached payload values used by that
                wrapper.

        Returns:
            The query tuple described above for the single-string-argument
            case, or None otherwise (colors are always reapplied via
            _apply_custom_theme_colors() before returning).
        """
        if require_redraw is not None and not kwargs and isinstance(require_redraw, str):
            if require_redraw == "state":
                return ('state', 'state', 'State', 'normal', str(getattr(self, "_custom_current_state", "normal")))
            return super().configure(require_redraw)

        if isinstance(require_redraw, dict):
            kwargs = require_redraw | kwargs

        if "state" in kwargs:
            self._custom_current_state = str(kwargs.pop("state")).lower()
            super().configure(state=self._custom_current_state)

        if "command" in kwargs:
            self._user_command = kwargs.pop("command")
            super().configure(command=self._execute_safe_command_forwarding if self._user_command else None)

        if "onvalue" in kwargs: self._onvalue_payload = kwargs["onvalue"]
        if "offvalue" in kwargs: self._offvalue_payload = kwargs["offvalue"]

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)

        if kwargs: super().configure(**kwargs)
        self._apply_custom_theme_colors()

    # Tkinter/CTk convention binds .config to .configure as a SEPARATE class
    # attribute -- it does not automatically track whichever configure() a
    # subclass defines. Without this line, calling .config(...) on an instance
    # would silently skip this entire override and land on the native widget's
    # configure() directly, bypassing theming and state handling entirely.
    config = configure

    def cget(self, attribute_name: str) -> Any:
        """
        Intercepts "state" and "command" queries, since both are tracked on
        this instance rather than delegated to the native widget for these
        two properties specifically.

        Args:
            attribute_name: The property name being queried.

        Returns:
            self._custom_current_state if querying "state"; self._user_command
            if querying "command"; otherwise whatever the native
            CTkSwitch.cget() returns.
        """
        pname = str(attribute_name).lower()
        if pname == "state": return getattr(self, "_custom_current_state", "normal")
        if pname == "command": return self._user_command
        return super().cget(attribute_name)

    def _set_appearance_mode(self, mode_string: str) -> None:
        """
        Forwards CustomTkinter's internal light/dark mode change notification to
        the native widget, then reapplies theme colors.

        Args:
            mode_string: The new appearance mode ("Light" or "Dark"), as passed
                by CustomTkinter's internal appearance-mode change machinery.
        """
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._apply_custom_theme_colors()

    def state(self, mode: Optional[str] = None) -> str:
        """
        Gets or sets the widget's enabled/disabled state.

        Args:
            mode: If None, returns the current state without changing
                anything. Otherwise forwarded to configure(state=mode).

        Returns:
            If querying: the current state string. If setting: echoes back
            `mode` exactly as given (not re-queried afterward).
        """
        if mode is None: return str(getattr(self, "_custom_current_state", "normal")).lower()
        self.configure(state=mode)
        return mode

    def get_state(self) -> str:
        """Equivalent to calling state() with no argument."""
        return self.state()

    def _apply_custom_theme_colors(self) -> None:
        """
        Recomputes and applies this widget's colors from the theme file, based
        on the current state, and updates the bindtag-based click interceptor
        to match.

        Called after construction, on every configure()/state() call, and
        (via _set_appearance_mode) on appearance-mode changes.

        Passes raw (light, dark) tuples straight through to configure() instead
        of resolving to a single color first, so CTk's native tracking can
        handle appearance-mode repaints without help from _set_appearance_mode.

        All five properties (fg_color, progress_color, button_color,
        button_hover_color, text_color) are required to be present in both
        the top-level theme block and disabled_map -- missing any raises
        immediately rather than substituting a hardcoded color. This full
        dimming is confirmed working by direct testing; see this class's
        docstring for the history of why it wasn't always the behavior here.
        """
        is_disabled = self._custom_current_state == "disabled"
        normal_map = self._local_defaults
        disabled_map = self._custom_disabled_map

        for required_key in ("fg_color", "progress_color", "button_color", "button_hover_color", "text_color"):
            if normal_map.get(required_key) is None:
                raise KeyError(
                    f"'{self.__class__.__name__}' theme block is missing '{required_key}' "
                    f"at the top level of sCTkThemes.json."
                )
            if disabled_map.get(required_key) is None:
                raise KeyError(
                    f"'{self.__class__.__name__}' theme block is missing '{required_key}' in disabled_map."
                )

        color_map = disabled_map if is_disabled else normal_map

        theme_payload = {
            "text_color": color_map.get("text_color"),
            "text_color_disabled": disabled_map.get("text_color"),
            "fg_color": color_map.get("fg_color"),
            "progress_color": color_map.get("progress_color"),
            "button_color": color_map.get("button_color"),
            "button_hover_color": color_map.get("button_hover_color"),
        }
        super().configure(**theme_payload)

        # Toggle the click-interceptor bindtag to match the current state.
        if is_disabled:
            if self._block_tag not in self._canvas.bindtags():
                self._canvas.bindtags((self._block_tag,) + self._canvas.bindtags())
            if hasattr(self, "_text_label") and self._block_tag not in self._text_label.bindtags():
                self._text_label.bindtags((self._block_tag,) + self._text_label.bindtags())
        else:
            if self._block_tag in self._canvas.bindtags():
                tags = list(self._canvas.bindtags())
                tags.remove(self._block_tag)
                self._canvas.bindtags(tuple(tags))
            if hasattr(self, "_text_label") and self._block_tag in self._text_label.bindtags():
                tags = list(self._text_label.bindtags())
                tags.remove(self._block_tag)
                self._text_label.bindtags(tuple(tags))