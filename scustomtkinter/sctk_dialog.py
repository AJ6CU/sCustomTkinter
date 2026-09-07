#!/usr/bin/python3
"""
sCTkDialog

A consistent popup dialog: a heading, a content area you fill, and a row of
Apply / Cancel / Reset buttons.

WINDOW OWNERSHIP. This widget creates its own sCTkDialogToplevel and packs
itself into it, so a dialog is always its own window. Callers do not create
one, and there is no mixin to add.

That replaces an earlier arrangement in which sCTkDialog was a plain frame
and a separate sCTkDialogMixin supplied the window, which required every user
to edit their generated class by hand -- adding an import and changing the
inheritance line. That step is gone.

The layout below was originally a Pygubu-generated base class,
sCTkDialogui.py, that this file inherited. It has been folded in, matching
every other widget in this library: a widget builds its own children in
__init__ rather than depending on a generated file shipped inside the package.
That file also carried imports which only resolved in the directory it was
generated in ("from sCTkFrame import sCTkFrame"), so it could not be imported
at all once installed.

The content area is `contentFrame`. In Pygubu Designer, widgets dropped onto an
sCTkDialog land there automatically -- the builder object's
get_child_master() returns it.
"""
import tkinter as tk

import customtkinter as ctk

from .sctk_frame import sCTkFrame
from .sctk_label_primary import sCTkLabelPrimary
from .sctk_button_primary import sCTkButtonPrimary
from .sctk_button_secondary import sCTkButtonSecondary
from .sctk_dialog_toplevel import sCTkDialogToplevel


class sCTkDialog(sCTkFrame):
    """Popup dialog with a heading, a content area and an action button row."""

    # Set False on a subclass to suppress window creation. Used by the Pygubu
    # Designer preview, which renders the dialog inline on its canvas and must
    # not spawn a real window on every redraw -- a modal one would seize input
    # and leave the Designer unusable.
    _MAKE_WINDOW = True

    # Required in the "sCTkDialog" block of sCTkThemes.json.
    #
    # NOTE the CustomTkinter naming: fg_color is the BACKGROUND fill, not the
    # text colour. It is a native frame option and reaches CTkFrame on its own.
    # text_color is the dialog's foreground -- used for the heading, and
    # available to caller content through cget("text_color"). heading_font is
    # read in _build_layout().
    _REQUIRED_THEME_KEYS = ("fg_color", "text_color", "heading_font")

    # How many buttons each setting shows, in order. Apply is always present:
    # a dialog with no way to accept is a message box, not a dialog.
    _BUTTON_ORDER = ("apply", "cancel", "reset")

    def __init__(self, master=None, *, title=None, width=None, height=None,
                 locate_over=None, offset_x=40, offset_y=40, modal=False,
                 transient=True, heading="Heading Title",
                 heading_anchor="center", heading_font=None,
                 heading_color=None,
                 buttons=3, apply_text="Apply", cancel_text="Cancel",
                 reset_text="Reset", apply_command=None, cancel_command=None,
                 reset_command=None, toplevel=None, **kw):
        """
        Args:
            master: Parent widget. Also the default for locate_over.
            title: Window title bar text.
            width / height: Window size in pixels. Omit to size to content.
            locate_over: The window to appear over and be transient to.
                Defaults to master's own toplevel. Kept separate from master
                because a dialog is often parented to a frame or a controller
                while needing to position over the main application window --
                see sCTkDialogToplevel.
            offset_x / offset_y: Pixels right of and below locate_over's
                top-left corner.
            modal: True to block interaction with the rest of the application
                while the dialog is open. run_and_wait() additionally blocks
                the calling code until it closes.
            transient: True to tie the window to its parent -- it stays above
                that window, minimises with it, and usually keeps out of the
                taskbar. False gives an independent window, which is what a
                long-lived tool panel wants.
            heading: Text shown above the content area.
            heading_anchor: "w", "e" or "center".
            heading_font: Overrides the theme's heading_font for this instance.
                A (family, size) or (family, size, style) tuple, or a CTkFont.
                None uses the theme value.
            heading_color: Overrides the theme's text_color for the heading on
                this instance. None uses the theme value.
            buttons: How many action buttons to show -- 3 (Apply, Cancel,
                Reset), 2 (Apply, Cancel) or 1 (Apply). Apply is always
                present: a dialog with no way to accept is a message box.
                Buttons not shown are never created, so `reset_Button` does
                not exist when buttons is 2 or 1 -- use has_button() to test.
            apply_text / cancel_text / reset_text: Button labels.
            apply_command / cancel_command / reset_command: Click callbacks.
                A callback given here takes precedence over the corresponding
                apply_CB / cancel_CB / reset_CB method, which remain available
                to override in a subclass.
            toplevel: An existing window to use instead of creating one.
                Rarely needed; present so a caller can supply a pre-configured
                window.
            **kw: Any native sCTkFrame argument.
        """
        self.dialog_parent = master
        self._heading_text = heading
        self._heading_anchor = heading_anchor
        self._heading_font_override = heading_font
        self._heading_color_override = heading_color

        try:
            self._button_count = max(1, min(3, int(buttons)))
        except (TypeError, ValueError):
            self._button_count = 3
        self._button_text = {"apply": apply_text, "cancel": cancel_text,
                             "reset": reset_text}
        self._button_command = {"apply": apply_command,
                                "cancel": cancel_command,
                                "reset": reset_command}

        if self._MAKE_WINDOW:
            if toplevel is None:
                # master is passed explicitly. Creating a Toplevel with no
                # master attaches it to whichever root Tkinter considers
                # default, which is wrong in any application with more than one
                # window -- and a real source of silently orphaned Tk variables.
                toplevel = sCTkDialogToplevel(
                    master, title=title, width=width, height=height,
                    locate_over=locate_over, offset_x=offset_x,
                    offset_y=offset_y, modal=modal, transient=transient,
                )
            self.dialog_toplevel = toplevel
            self.dialog_toplevel.protocol(
                "WM_DELETE_WINDOW", self.on_delete_window)
            # The content is built INSIDE the new window, so the toplevel has
            # to exist before this call.
            super().__init__(self.dialog_toplevel, **kw)
            self.pack(expand=True, fill="both")
        else:
            self.dialog_toplevel = None
            super().__init__(master, **kw)

        self._validate_theme_keys()
        self._build_layout()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def _validate_theme_keys(self):
        """
        Hard-fails on an incomplete theme block, naming the missing key.

        Follows the library-wide fail-loud rule: substituting a plausible
        default hides a broken block behind output that merely looks slightly
        wrong.

        Raises:
            KeyError: naming the first missing key.
        """
        # FIX: this read self.__class__.__name__, which for a subclass is the
        # SUBCLASS's name -- so the Designer preview class reported
        # "'sCTkDialogForPreview' theme block is missing 'heading_font'" while
        # the block it actually reads is named by _THEME_BLOCK_NAME. Validation
        # must resolve the block the same way ThemeableWidget does, or it
        # reports a block that was never consulted.
        name = getattr(self, "_THEME_BLOCK_NAME", None) or self.__class__.__name__
        for key in self._REQUIRED_THEME_KEYS:
            if self.final_kw.get(key) is None:
                raise KeyError(
                    f"'{name}' theme block is missing '{key}' at the top "
                    f"level of sCTkThemes.json."
                )

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_layout(self):
        """
        Builds the three regions: heading, content, action row.

        Every StringVar is given an explicit master. A variable created without
        one attaches to whichever root Tkinter considers default, which in an
        application with more than one window silently binds it to the wrong
        interpreter -- the widget updates one variable while the application
        reads another, and the symptom is a value that is always empty.
        """
        # --- heading -------------------------------------------------------
        self.titleFrame = sCTkFrame(self)
        self.heading_VAR = tk.StringVar(master=self, value=self._heading_text)
        self.heading_Label = sCTkLabelPrimary(self.titleFrame)
        # font and colour come from THIS widget's theme block, not from
        # sCTkLabelPrimary's. A dialog heading is a distinct role and should be
        # restyleable without moving every primary label in the application.
        self.heading_Label.configure(
            anchor=self._heading_anchor,
            textvariable=self.heading_VAR,
            # A font passed to the constructor wins over the theme, so a
            # single dialog can be restyled without touching the theme file.
            font=self._heading_font_override or self.final_kw.get("heading_font"),
            text_color=(self._heading_color_override
                        or self.final_kw.get("text_color")),
        )
        self.heading_Label.pack(expand=True, fill="x", side="top")
        self.titleFrame.pack(anchor="n", expand=True, fill="x",
                             padx=10, pady="20 10", side="top")

        # --- content area --------------------------------------------------
        # Where caller content goes. The Designer's builder object returns this
        # from get_child_master(), so widgets dropped on the dialog land here
        # rather than beside the heading or the buttons.
        self.contentFrame = sCTkFrame(self)
        self.contentFrame.configure(width=500)
        self.contentFrame.pack(expand=True, fill="both", padx=5, side="top")

        # --- action row ----------------------------------------------------
        self._build_action_row()

    def _build_action_row(self):
        """
        Builds the button row from the current button count.

        Separate from _build_layout() so set_buttons() can rebuild just this
        part. Only the requested buttons are created; attributes for the others
        are set to None rather than left undefined, so `self.reset_Button` is
        always a valid expression -- code reaching for a button that was not
        requested gets None instead of AttributeError.
        """
        self.actionFrame = sCTkFrame(self)

        self.apply_Button = self.cancel_Button = self.reset_Button = None
        self.applyText_VAR = self.cancelText_VAR = self.resetText_VAR = None

        button_classes = {"apply": sCTkButtonPrimary,
                          "cancel": sCTkButtonSecondary,
                          "reset": sCTkButtonSecondary}

        for column, name in enumerate(self._BUTTON_ORDER[:self._button_count]):
            var = tk.StringVar(master=self, value=self._button_text[name])
            button = button_classes[name](self.actionFrame)
            # A command passed to the constructor wins; otherwise the
            # overridable method is used, so a subclass that only defines
            # apply_CB() still works.
            command = self._button_command[name] or getattr(self, f"{name}_CB")
            button.configure(textvariable=var, command=command)
            button.grid(column=column, padx=10, row=0)
            setattr(self, f"{name}_Button", button)
            setattr(self, f"{name}Text_VAR", var)

        self.actionFrame.pack(anchor="s", expand=True, fill="x",
                              padx=5, pady="10 20", side="top")
        self.actionFrame.grid_anchor("s")

    def set_buttons(self, count):
        """
        Changes how many action buttons the dialog shows, rebuilding the row.

        The row is built once at construction, so changing the count means
        destroying and rebuilding it -- there is no way to add a button that
        was never created. Labels and commands set through the constructor are
        preserved, since they live in _button_text and _button_command rather
        than on the widgets.

        Exists so the Pygubu Designer can honour a change to `buttons` on a
        live widget. Relying on the Designer to rebuild the whole widget did
        not work: the canvas kept showing the old count while the preview and
        the generated code showed the new one.

        Args:
            count: 1, 2 or 3. Clamped into that range.
        """
        try:
            count = max(1, min(3, int(count)))
        except (TypeError, ValueError):
            return
        if count == self._button_count:
            return

        self._button_count = count
        if getattr(self, "actionFrame", None) is not None:
            self.actionFrame.destroy()
        self._build_action_row()

    def set_button_text(self, name, text):
        """
        Sets one button's label, remembering it across a rebuild.

        set_buttons() recreates the buttons, so a label set only on the widget
        would be lost. This records it too.

        Args:
            name: "apply", "cancel" or "reset".
            text: The label.
        """
        if name not in self._button_text:
            return False
        self._button_text[name] = text
        var = getattr(self, f"{name}Text_VAR", None)
        if var is not None:
            var.set(text)
        return True

    # ------------------------------------------------------------------
    # Button callbacks -- override in a subclass
    # ------------------------------------------------------------------
    def apply_CB(self):
        """Called when Apply is clicked. Override."""
        pass

    def cancel_CB(self):
        """Called when Cancel is clicked. Override."""
        pass

    def reset_CB(self):
        """Called when Reset is clicked. Override."""
        pass

    # ------------------------------------------------------------------
    # Window
    # ------------------------------------------------------------------
    def on_delete_window(self):
        """Bound to the window manager's close button. Override to intercept."""
        self.dialog_close()

    def dialog_close(self):
        """Closes and destroys the dialog window."""
        if self.dialog_toplevel is not None:
            self.dialog_toplevel.destroy()

    def run_and_wait(self):
        """
        Makes the dialog modal and blocks until it closes.

        Use when the calling code needs the result before continuing. A dialog
        constructed with modal=True already blocks *interaction*; this also
        blocks *execution*, which is the difference between a dialog you can
        ignore and one you must answer.
        """
        if self.dialog_toplevel is None:
            return
        self.dialog_toplevel._apply_modal()
        parent = self.dialog_parent or self.dialog_toplevel
        parent.wait_window(self.dialog_toplevel)

    def set_title(self, title):
        """Sets the window title bar text."""
        if self.dialog_toplevel is not None:
            self.dialog_toplevel.title(title)

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------
    def set_heading(self, heading=None, anchor=None):
        """
        Sets the heading text above the content area, and optionally its
        alignment.

        Args:
            heading: New text. None leaves it unchanged.
            anchor: "w", "e" or "center". Any other value is ignored. None
                leaves it unchanged.
        """
        if heading is not None:
            self.heading_VAR.set(heading)
        if anchor is not None and str(anchor).lower() in ("w", "e", "center"):
            self._heading_anchor = str(anchor).lower()
            self.heading_Label.configure(anchor=self._heading_anchor)

    def set_heading_font(self, font):
        """Overrides the heading font for this instance."""
        self.heading_Label.configure(font=font)

    def set_heading_color(self, text_color):
        """
        Overrides the heading colour for this instance.

        Passing None restores the theme's text_color.
        """
        self.heading_Label.configure(
            text_color=text_color or self.final_kw.get("text_color"))

    def has_button(self, name):
        """
        Whether a given button exists on this dialog.

        Args:
            name: "apply", "cancel" or "reset".

        Returns:
            True if that button was created and still exists.
        """
        button = getattr(self, f"{name}_Button", None)
        if button is None:
            return False
        try:
            return bool(button.winfo_exists())
        except Exception:
            return False

    def set_two_button(self):
        """
        Reduces the action row to Apply and Cancel by removing Reset.

        Retained from the original API. Prefer buttons=2 at construction --
        this destroys a button that was built a moment earlier. Irreversible;
        set_reset_button() returns False afterwards rather than raising.
        """
        if self.has_button("reset"):
            self.reset_Button.destroy()
        self._button_count = min(self._button_count, 2)

    def set_apply_button(self, button_name=None, button_command=None):
        """
        Sets the Apply button's label and callback.

        Args:
            button_name: New label. None leaves it unchanged.
            button_command: New callback. None leaves it unchanged.

        Returns:
            True, or False if the button does not exist on this dialog.
        """
        if not self.has_button("apply"):
            return False
        if button_name is not None:
            self.applyText_VAR.set(button_name)
        if button_command is not None:
            self.apply_Button.configure(command=button_command)
        return True

    def set_cancel_button(self, button_name=None, button_command=None):
        """Sets the Cancel button's label and callback. See set_apply_button()."""
        if not self.has_button("cancel"):
            return False
        if button_name is not None:
            self.cancelText_VAR.set(button_name)
        if button_command is not None:
            self.cancel_Button.configure(command=button_command)
        return True

    def set_reset_button(self, button_name=None, button_command=None):
        """
        Sets the Reset button's label and callback.

        Returns:
            False if the button has been removed by set_two_button(), in which
            case nothing is changed. True otherwise.
        """
        if not self.has_button("reset"):
            return False
        if button_name is not None:
            self.resetText_VAR.set(button_name)
        if button_command is not None:
            self.reset_Button.configure(command=button_command)
        return True

    # ------------------------------------------------------------------
    # Backwards-compatible aliases.
    #
    # The original methods were camelCase and inconsistent with each other:
    # setApplyButton took `buttonCommand` while setCancelButton and
    # setResetButton took `ButtonCommand`, so the documented call failed on one
    # of the three. The snake_case methods above are the supported API; these
    # keep existing code working.
    # ------------------------------------------------------------------
    setTitle = set_title
    setHeading = set_heading
    setTwoButton = set_two_button
    setApplyButton = set_apply_button
    setCancelButton = set_cancel_button
    setResetButton = set_reset_button
    onDeleteWindow = on_delete_window
    dialogClose = dialog_close
    runAndWait = run_and_wait
