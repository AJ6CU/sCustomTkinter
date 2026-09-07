#!/usr/bin/python3
"""
sCTkDialogToplevel

The window that holds an sCTkDialog. Owns everything to do with the
WINDOW -- title, size, placement, modality -- so that sCTkDialog can
concern itself only with the content inside it.

Previously this class was an empty subclass of CTkToplevel and all of the
window behaviour lived in a separate sCTkDialogMixin, which callers had to
add by hand to their generated class. Folding it in here removes that step:
see Dialogs.md.
"""
import tkinter as tk

import customtkinter as ctk


class sCTkDialogToplevel(ctk.CTkToplevel):
    """
    A top-level window sized, placed and (optionally) made modal on creation.

    Placement is expressed RELATIVE to another window rather than in screen
    coordinates, because that is what dialogs actually want: appear over the
    window that opened me, nudged down and right so the parent is still
    visible behind. Absolute coordinates break the moment the user moves the
    application window.
    """

    def __init__(self, master=None, *, title=None, width=None, height=None,
                 locate_over=None, offset_x=40, offset_y=40, modal=False,
                 **kw):
        """
        Args:
            master: The Tk parent. Required for the window to belong to the
                right interpreter -- see the note below.
            title: Window title bar text.
            width: Window width in pixels. Omit to size to content.
            height: Window height in pixels. Omit to size to content.
            locate_over: The window this dialog should appear over, and be
                transient to. Defaults to master's own toplevel.

                Deliberately separate from `master`: a dialog is often
                parented to a frame or a controller widget while needing to
                position itself over the main application window. Passing the
                two separately avoids having to choose.
            offset_x: Pixels right of locate_over's top-left corner.
            offset_y: Pixels below it.
            modal: True to grab input and block interaction with the rest of
                the application. See _apply_modal() for the ordering this
                requires.
            **kw: Any native CTkToplevel argument.
        """
        # FIX: an extra blank window appeared when master was None.
        #
        # tkinter creates a default root implicitly the first time any widget
        # is made without one -- and that root is a real, visible, empty
        # window. A dialog constructed with no master therefore produced TWO
        # windows: the dialog, and a blank one behind it.
        #
        # If a root already exists we adopt it. If not, one is created and
        # immediately withdrawn, so it services the Tcl interpreter without
        # ever being seen. Withdrawing rather than avoiding it is necessary:
        # Tk requires a root, and letting tkinter make one silently is exactly
        # what caused the problem.
        self._implicit_root = None
        if master is None:
            existing = getattr(tk, "_default_root", None)
            if existing is None:
                self._implicit_root = ctk.CTk()
                self._implicit_root.withdraw()
                master = self._implicit_root
            else:
                master = existing

        super().__init__(master, **kw)

        # locate_over defaults to whichever window owns master. winfo_toplevel()
        # walks up for us, so a dialog parented to a deeply nested frame still
        # positions itself over the right window.
        if locate_over is None and master is not None:
            try:
                locate_over = master.winfo_toplevel()
            except Exception:
                locate_over = None
        self._locate_over = locate_over
        self._offset_x = int(offset_x)
        self._offset_y = int(offset_y)
        self._requested_width = width
        self._requested_height = height

        if title:
            self.title(title)

        # transient() ties the dialog to its parent for the window manager:
        # it stays above that window and usually skips the taskbar. Done
        # before placement so the WM has the relationship when the window maps.
        if self._locate_over is not None:
            try:
                self.transient(self._locate_over)
            except Exception:
                pass

        self.place_over()

        if modal:
            self._apply_modal()

    def place_over(self, locate_over=None, offset_x=None, offset_y=None):
        """
        Positions the window relative to another one.

        Callable again later -- if the parent window moves and the dialog
        should follow, or to re-place after a resize.

        Falls back to centring on screen when there is no reference window,
        which is better than landing at whatever coordinates the window
        manager chose.

        Args:
            locate_over: Reference window. Defaults to the one given at
                construction.
            offset_x: Pixels right of its top-left corner.
            offset_y: Pixels below it.
        """
        if locate_over is not None:
            self._locate_over = locate_over
        if offset_x is not None:
            self._offset_x = int(offset_x)
        if offset_y is not None:
            self._offset_y = int(offset_y)

        # Required before any winfo_* geometry query: without it the values
        # are whatever they were before the pending layout ran, which for a
        # freshly created window is 1x1 at 0,0.
        self.update_idletasks()

        width = self._requested_width or self.winfo_reqwidth()
        height = self._requested_height or self.winfo_reqheight()

        ref = self._locate_over
        try:
            usable_ref = ref is not None and ref.winfo_exists()
        except Exception:
            usable_ref = False

        if usable_ref:
            # rootx/rooty rather than x/y: these are screen coordinates, which
            # is what geometry() expects. x/y would be relative to the parent's
            # own parent and place the dialog somewhere unrelated.
            x = ref.winfo_rootx() + self._offset_x
            y = ref.winfo_rooty() + self._offset_y
        else:
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)

        # Keep the window on screen. A large offset from a parent near the
        # right edge would otherwise put the dialog partly or wholly off it.
        x = max(0, min(x, self.winfo_screenwidth() - width))
        y = max(0, min(y, self.winfo_screenheight() - height))

        if self._requested_width or self._requested_height:
            self.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.geometry(f"+{x}+{y}")

    def _apply_modal(self):
        """
        Takes an input grab, blocking interaction with the rest of the
        application.

        wait_visibility() first is NOT optional: on X11 a grab on a window
        that is not yet viewable raises TclError. It is harmless on macOS and
        Windows, so it is done unconditionally rather than platform-tested.
        """
        try:
            self.wait_visibility()
            self.grab_set()
        except Exception:
            # Window destroyed between construction and this call.
            pass

    def destroy(self):
        """
        Destroys the window, and the implicit root if this widget created one.

        Without this, a dialog built with no master would leave the withdrawn
        root alive after closing and the interpreter would never exit.
        """
        implicit = getattr(self, "_implicit_root", None)
        super().destroy()
        if implicit is not None:
            try:
                implicit.destroy()
            except Exception:
                pass

    def release_modal(self):
        """Releases the input grab, leaving the window open but non-blocking."""
        try:
            self.grab_release()
        except Exception:
            pass


if __name__ == "__main__":
    root = ctk.CTk()
    ctk.CTkButton(
        root, text="Open dialog window",
        command=lambda: sCTkDialogToplevel(
            root, title="Example", width=320, height=200, modal=True),
    ).pack(padx=40, pady=40)
    root.mainloop()
