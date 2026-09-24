#!/usr/bin/python3
"""
Checks that a labelled frame is as tall as what is in it.

    python3 test_frame_labeled_sizing.py

WHAT WAS WRONG. These panels are modelled on ttk.LabelFrame, which is as tall
as its contents, but they are built on CTkScrollableFrame, which is 200 points
high whatever it holds. So a two-row panel stood half empty. Worse, a height
passed in was RECORDED and then overridden -- it reads back as the value you
set while the panel draws at 200 -- because the widget you hold is the inner
frame of three, and the height has to go on the outer one with propagation
off. No caller could reasonably work that out.

WHAT TO LOOK FOR. Every panel below should be as tall as its own content,
except the one given an explicit height, which should be exactly that.
The numbers are printed; the window shows the same thing.
"""
import customtkinter as ctk
from scustomtkinter import (sCTk, sCTkFrameLabeledPrimary, sCTkFrameLabeledSecondary,
                            sCTkLabelSecondary, sCTkButtonPrimary, sCTkFrame)

root = sCTk()
root.title("labelled frame sizing")
root.geometry("980x640")

page = sCTkFrame(root, fg_color="transparent", border_width=0)
page.pack(fill="both", expand=True, padx=12, pady=12)
page.grid_columnconfigure((0, 1), weight=1, uniform="cols")

panels = {}


def panel(kind, column, row, title, lines, **kw):
    box = kind(page, label_text=title, label_anchor="w", **kw)
    box.grid(row=row, column=column, sticky="new", padx=6, pady=6)
    for n in range(lines):
        sCTkLabelSecondary(box, text=f"row {n + 1}").pack(anchor="w", padx=8, pady=2)
    panels[title] = (box, lines)
    return box


panel(sCTkFrameLabeledSecondary, 0, 0, "two rows", 2)
panel(sCTkFrameLabeledSecondary, 1, 0, "five rows", 5)
panel(sCTkFrameLabeledPrimary, 0, 1, "primary, three rows", 3)
grown = panel(sCTkFrameLabeledSecondary, 1, 1, "grows when a row is added", 2)
panel(sCTkFrameLabeledSecondary, 0, 2, "height=90, given", 6, height=90)


def measure(title):
    """
    The drawn height, the content's own height, and -- the number that
    matters -- how much room the contents actually got.

    An earlier version of this test printed only the first two, which agreed
    with each other while the panels on screen were a row short. The visible
    height is the canvas inside the frame, and that is what the contents have
    to fit into.
    """
    box, lines = panels[title]
    outer = getattr(box, "_parent_frame", box.master)
    canvas = getattr(box, "_parent_canvas", None) or box.master
    root.update_idletasks()
    return (outer.winfo_height(), box.winfo_reqheight(),
            canvas.winfo_height(), lines)


def report():
    root.update_idletasks()
    print("\n  panel                         drawn   content   room   fits?")
    for title in panels:
        drawn, content, room, lines = measure(title)
        fits = "yes" if room >= content else f"NO, {content - room} short"
        print(f"    {title:28} {drawn:>5}   {content:>7}   {room:>4}   {fits}")
    print("\n  'room' is the space the contents actually got -- the canvas inside\n"
          "  the frame. Every panel should say yes, except 'height=90, given',\n"
          "  which is meant to clip.\n")


def add_row():
    """
    The panel should grow by one row's height.

    CHECKED AFTER A PAUSE. The panel measures itself a moment after the
    content changes -- deliberately, so a burst of changes becomes one
    measurement -- so looking immediately reports "did not grow" for a panel
    that grows a moment later. An earlier version of this test did exactly
    that, and called it a failure.
    """
    before = measure("grows when a row is added")[0]
    count = panels["grows when a row is added"][1] + 1
    sCTkLabelSecondary(grown, text=f"row {count}").pack(anchor="w", padx=8, pady=2)
    panels["grows when a row is added"] = (grown, count)

    def look():
        after = measure("grows when a row is added")[0]
        print(f"  added a row: {before} -> {after}   "
              f"({'grew' if after > before else 'DID NOT GROW'})")

    root.after(200, look)


sCTkButtonPrimary(page, text="add a row", command=add_row).grid(
    row=3, column=0, sticky="w", padx=6, pady=8)
sCTkButtonPrimary(page, text="measure", command=report).grid(
    row=3, column=1, sticky="w", padx=6, pady=8)

root.after(400, report)
root.mainloop()
