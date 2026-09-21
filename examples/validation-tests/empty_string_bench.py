#!/usr/bin/python3
"""
Test bench for the empty-string rule.

Two things are checked on every widget that has content:

  1. CONTENT CAN BE BLANKED. configure(<content key>="") must actually clear
     it -- cget() afterwards returns "". Before the fix this silently did
     nothing and the old text stayed on screen.

  2. A CLEARED COLOUR IS STILL A NO-OP. configure(<colour>="") -- what the
     Designer sends when a field is cleared -- must neither raise nor change
     the colour. This is the job the rule was written for, and the fix must
     not undo it.

Results print to the console and show beside each widget. Nothing needs
judging by eye: each line says PASS or FAIL and why.

    python3 empty_string_bench.py
"""
import customtkinter as ctk

from scustomtkinter import (
    sCTk, sCTkFrame,
    sCTkLabelPrimary, sCTkLabelSecondary, sCTkLabelTertiary,
    sCTkButtonPrimary, sCTkButtonSecondary, sCTkButtonTertiary,
    sCTkCheckBox, sCTkRadioButton, sCTkSwitch,
    sCTkEntryPrimary, sCTkEntrySecondary,
    sCTkFrameLabeledPrimary, sCTkFrameLabeledSecondary, sCTkScrollableFrame,
    sCTkSeparator,
)

# (class, content key, constructor arguments)
CASES = [
    (sCTkLabelPrimary,          "text",             {"text": "label primary"}),
    (sCTkLabelSecondary,        "text",             {"text": "label secondary"}),
    (sCTkLabelTertiary,         "text",             {"text": "label tertiary"}),
    (sCTkButtonPrimary,         "text",             {"text": "button primary"}),
    (sCTkButtonSecondary,       "text",             {"text": "button secondary"}),
    (sCTkButtonTertiary,        "text",             {"text": "button tertiary"}),
    (sCTkCheckBox,              "text",             {"text": "checkbox"}),
    (sCTkRadioButton,           "text",             {"text": "radio button"}),
    (sCTkSwitch,                "text",             {"text": "switch"}),
    (sCTkEntryPrimary,          "placeholder_text", {"placeholder_text": "entry primary"}),
    (sCTkEntrySecondary,        "placeholder_text", {"placeholder_text": "entry secondary"}),
    (sCTkFrameLabeledPrimary,   "label_text",       {"label_text": "labelled primary", "height": 40}),
    (sCTkFrameLabeledSecondary, "label_text",       {"label_text": "labelled secondary", "height": 40}),
    (sCTkScrollableFrame,       "label_text",       {"label_text": "scrollable", "height": 40}),
    (sCTkSeparator,             "text",             {"text": "separator", "orientation": "horizontal", "length": 200}),
]

# Tried in order; the first one the widget reports is the one tested.
COLOUR_KEYS = ("text_color", "fg_color", "border_color", "label_text_color")


def safe_cget(widget, key):
    try:
        return True, widget.cget(key)
    except Exception as err:
        return False, err


def check_content(widget, key):
    """configure(key="") must leave cget(key) empty."""
    try:
        widget.configure(**{key: ""})
    except Exception as err:
        return False, f"configure({key}='') raised {type(err).__name__}: {err}"
    ok, value = safe_cget(widget, key)
    if not ok:
        return False, f"cget({key!r}) raised {value}"
    if value != "":
        return False, f"{key} is still {value!r} -- the blank was dropped"
    return True, f"{key} blanked"


def check_colour(widget):
    """configure(colour="") must not raise and must leave the colour alone."""
    for key in COLOUR_KEYS:
        ok, before = safe_cget(widget, key)
        if not ok:
            continue
        try:
            widget.configure(**{key: ""})
        except Exception as err:
            return False, f"clearing {key} raised {type(err).__name__}: {err}"
        ok, after = safe_cget(widget, key)
        if not ok:
            return False, f"cget({key!r}) raised after the clear: {after}"
        if after != before:
            return False, f"clearing {key} changed it: {before!r} -> {after!r}"
        return True, f"clearing {key} was a no-op"
    # A FAILURE, not a pass. Every widget here has colours, so finding none
    # means cget() is refusing them -- which is how the separator's cget bug
    # hid: it reported "PASS no colour key to test" while failing on every
    # property it knew.
    return False, "cget() refused every colour key"


class Bench(sCTk):

    def __init__(self):
        super().__init__()
        self.title("empty-string rule bench")
        self.geometry("900x860")

        body = sCTkFrame(self, fg_color="transparent", border_width=0)
        body.pack(fill="both", expand=True, padx=12, pady=10)
        body.grid_columnconfigure(1, weight=1)

        failures = 0
        print(f"\n{'widget':28} {'content':34} colour")
        print("-" * 96)

        for row, (cls, key, kwargs) in enumerate(CASES):
            name = cls.__name__
            try:
                widget = cls(body, **kwargs)
                widget.grid(row=row, column=0, sticky="w", padx=4, pady=3)
            except Exception as err:
                failures += 1
                self._report(body, row, name, False,
                             f"construction raised {type(err).__name__}: {err}", True, "")
                continue

            # Let it draw once, so cget reflects a real widget.
            self.update_idletasks()

            content_ok, content_msg = check_content(widget, key)
            colour_ok, colour_msg = check_colour(widget)
            failures += (not content_ok) + (not colour_ok)
            self._report(body, row, name, content_ok, content_msg,
                         colour_ok, colour_msg)

        print("-" * 96)
        summary = ("ALL PASSED" if failures == 0
                   else f"{failures} FAILURE(S) -- see above")
        print(summary + "\n")
        self.title(f"empty-string rule bench -- {summary}")

    def _report(self, parent, row, name, content_ok, content_msg,
                colour_ok, colour_msg):
        tag = lambda ok: "PASS" if ok else "FAIL"
        print(f"{name:28} {tag(content_ok)} {content_msg:29} "
              f"{tag(colour_ok)} {colour_msg}")
        text = f"{tag(content_ok)}  {content_msg}     {tag(colour_ok)}  {colour_msg}"
        colour = ("#0F6E56", "#3FB68B") if content_ok and colour_ok \
            else ("#B42318", "#F97066")
        ctk.CTkLabel(parent, text=text, text_color=colour, anchor="w",
                     font=("Arial", 11)).grid(row=row, column=1, sticky="w",
                                              padx=8)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    Bench().mainloop()
