#!/usr/bin/python3
"""
Test bench for sCTkFrequencyDisplay.

Three readouts, each showing a different use, and controls for everything
that changes how one looks.

WHAT TO TRY

  * Click a digit. The selection is the tuning step, and the readout below
    reports what a dial turning it would move -- which is the whole reason
    the widget owns the selection rather than the application.

  * Scroll over a readout. The bench turns the selected digit, so the
    carry behaviour and the fixed positions are both visible.

  * Change the delimiter while the numbers are moving. It is a display
    preference the whole interface shares, so it has to be settable
    mid-stream rather than fixed at construction.

  * Change the digit count between 6 and 10 and watch the leading groups
    appear. Nothing else moves: the layout is computed for the full width.

  * Switch to signed and set a negative value. The sign always draws, even
    when the leading digits do not.

  * Compare the fixed-width font against a proportional one. Turn a digit
    through 111111 and 888888 in each and watch the readout sit still or
    wander.
"""
import tkinter as tk

import customtkinter as ctk

from scustomtkinter import (
    sCTk, sCTkFrame, sCTkLabelPrimary, sCTkLabelSecondary, sCTkLabelTertiary,
    sCTkButtonPrimary, sCTkButtonSecondary, sCTkComboBox, sCTkSwitch,
    sCTkFrequencyDisplay,
)


class Bench(sCTk):

    def __init__(self):
        super().__init__()
        self.title("sCTkFrequencyDisplay test bench")
        self.geometry("820x560")

        base = sCTkFrame(self, fg_color="transparent", border_width=0)
        base.pack(expand=True, fill="both", padx=16, pady=14)

        # -- the three readouts -------------------------------------------
        self.vfo = self._readout(
            base, "VFO — ten digits, reaching into the GHz",
            digits=10, signed=False, value=14_029_400, font_size=38)

        self.offset = self._readout(
            base, "RIT offset — four digits, signed",
            digits=4, signed=True, value=-700, font_size=28, min_digit=0)

        self.plain = self._readout(
            base, "Read-only — selection switched off",
            digits=8, signed=False, value=7_074_000, font_size=24,
            selectable=False)

        # -- what the selection means -------------------------------------
        self.step_label = sCTkLabelSecondary(
            base, text="", font=("Arial", 13))
        self.step_label.pack(anchor="w", pady=(4, 12))
        self._report_step(self.vfo.display.step())

        # -- controls ------------------------------------------------------
        self._controls(base)

    # ------------------------------------------------------------------
    def _readout(self, parent, caption, **kw):
        """One captioned readout, wired to the wheel and to the step label."""
        box = sCTkFrame(parent, border_width=1, corner_radius=6)
        box.pack(fill="x", pady=4)

        sCTkLabelTertiary(box, text=caption, font=("Arial", 11)
                          ).pack(anchor="w", padx=10, pady=(6, 0))

        display = sCTkFrequencyDisplay(box, command=self._report_step, **kw)
        display.pack(anchor="w", padx=10, pady=(2, 8))

        # The wheel turns whichever digit is selected. The widget reports the
        # step; moving the value is the application's business, which is the
        # division this bench is demonstrating.
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            display.canvas.bind(
                seq, lambda e, d=display: self._turn(d, e))

        box.display = display
        return box

    def _turn(self, display, event):
        """One detent: move the selected digit up or down."""
        if display.get_state() == "disabled" or not display.cget("selectable"):
            return "break"

        if getattr(event, "num", None) == 4:
            direction = 1
        elif getattr(event, "num", None) == 5:
            direction = -1
        else:
            direction = 1 if getattr(event, "delta", 0) > 0 else -1

        display.set(display.get() + direction * display.step())
        return "break"

    def _report_step(self, step):
        """The widget hands us the place value of the digit just selected."""
        readable = f"{step // 1000} kHz" if step >= 1000 else f"{step} Hz"
        self.step_label.configure(
            text=f"selected digit is worth {step} — a dial would move "
                 f"{readable} per detent")

    # ------------------------------------------------------------------
    def _controls(self, parent):
        row_one = sCTkFrame(parent, fg_color="transparent", border_width=0)
        row_one.pack(fill="x", pady=(8, 2))

        sCTkLabelTertiary(row_one, text="delimiter", font=("Arial", 11)
                          ).pack(side="left", padx=(0, 6))
        delim = sCTkComboBox(row_one, width=90,
                             values=[".", ",", " ", "'", "-"],
                             command=self._set_delimiter)
        delim.pack(side="left", padx=(0, 16))
        delim.set(".")

        sCTkLabelTertiary(row_one, text="vfo digits", font=("Arial", 11)
                          ).pack(side="left", padx=(0, 6))
        digits = sCTkComboBox(row_one, width=80,
                              values=["6", "7", "8", "9", "10", "12"],
                              command=self._set_digits)
        digits.pack(side="left", padx=(0, 16))
        digits.set("10")

        sCTkLabelTertiary(row_one, text="font", font=("Arial", 11)
                          ).pack(side="left", padx=(0, 6))
        family = sCTkComboBox(
            row_one, width=150, command=self._set_family,
            values=["Courier", "Menlo", "Consolas", "DejaVu Sans Mono",
                    "Arial", "Helvetica"])
        family.pack(side="left")
        family.set("Courier")
        sCTkLabelTertiary(
            row_one,
            text="the last two are proportional — watch the digits wander",
            font=("Arial", 10)).pack(side="left", padx=8)

        row_two = sCTkFrame(parent, fg_color="transparent", border_width=0)
        row_two.pack(fill="x", pady=2)

        self.signed_switch = sCTkSwitch(
            row_two, text="vfo signed", command=self._toggle_signed)
        self.signed_switch.pack(side="left", padx=(0, 20))

        self.enabled_switch = sCTkSwitch(
            row_two, text="enabled", command=self._toggle_enabled)
        self.enabled_switch.pack(side="left", padx=(0, 20))
        self.enabled_switch.select()

        sCTkButtonSecondary(row_two, text="negative", width=88,
                            command=self._make_negative).pack(side="left", padx=2)
        sCTkButtonSecondary(row_two, text="zero", width=70,
                            command=lambda: self.vfo.display.set(0)
                            ).pack(side="left", padx=2)
        sCTkButtonSecondary(row_two, text="1.2 GHz", width=84,
                            command=lambda: self.vfo.display.set(1_296_100_000)
                            ).pack(side="left", padx=2)
        sCTkButtonSecondary(row_two, text="111 / 888", width=92,
                            command=self._jitter_test).pack(side="left", padx=2)

        sCTkButtonPrimary(
            row_two, text="Light / Dark", width=110,
            command=lambda: ctk.set_appearance_mode(
                "Light" if ctk.get_appearance_mode() == "Dark" else "Dark")
        ).pack(side="right")

    # ------------------------------------------------------------------
    def _each(self):
        return (self.vfo.display, self.offset.display, self.plain.display)

    def _set_delimiter(self, choice):
        # Changed on all three at once, mid-stream, which is the case that
        # matters: a readout that kept the delimiter it was born with would
        # disagree with the rest of the interface the moment the preference
        # changed.
        for display in self._each():
            display.configure(delimiter=choice)

    def _set_digits(self, choice):
        self.vfo.display.configure(digits=int(choice))

    def _set_family(self, choice):
        # Through the THEME, since that is where the family belongs. An
        # unavailable name falls back rather than silently going
        # proportional -- try Menlo on Windows or Consolas on a Mac.
        for display in self._each():
            size = display.cget("font_size")
            display.configure(font=(choice, size, "bold"))

    def _toggle_signed(self):
        self.vfo.display.configure(
            signed=bool(self.signed_switch.get()))

    def _toggle_enabled(self):
        state = "normal" if self.enabled_switch.get() else "disabled"
        for display in self._each():
            display.configure(state=state)

    def _make_negative(self):
        # Only means anything when signed: unsigned shows the magnitude, so
        # this is also a way to see what signed=False does with one.
        self.vfo.display.set(-abs(self.vfo.display.get() or 14_029_400))

    def _jitter_test(self):
        """
        Flips between all-1s and all-8s.

        The narrowest and widest digits in most proportional fonts. With a
        fixed-width family the readout does not move; with Arial selected
        above, it visibly breathes -- which is the whole argument for
        drawing at computed positions AND using a monospace font.
        """
        current = self.vfo.display.get()
        self.vfo.display.set(88_888_888 if current == 11_111_111
                             else 11_111_111)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    Bench().mainloop()