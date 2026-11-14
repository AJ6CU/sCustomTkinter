"""
The dials draw their knob, ticks and labels at the widget scale, not just
their canvas.

    python examples/validation-tests/test_dial_scaling.py

At 150 % and 200 % on Windows the knobs looked small (uBITX CEC Desktop on a
ThinkPad X1 Carbon, 2026-11-14): CustomTkinter doubled the canvas but the knob
was still drawn 118 px across inside it. set_widget_scaling() does here what
the display's scale does there. Each check compares the drawn knob, and the
size of the label text, with the same dial at a scale of 1.
"""
import tkinter.font as tkfont

import customtkinter as ctk
import scustomtkinter as s

root = s.sCTk()
dials = {
    "Continuous": s.sCTkDialContinuous(root, knob_diameter=118),
    "Range": s.sCTkDialRange(root, knob_diameter=72),
    "Selector": s.sCTkDialSelector(root, knob_diameter=60),
}
for d in dials.values():
    d.pack(padx=10, pady=10)
root.update()


def knob_width(dial):
    x1, _, x2, _ = dial.canvas.bbox("knob_body")
    return x2 - x1


def label_height(dial):
    """Height of the tallest label drawn (none on Continuous)."""
    heights = [tkfont.Font(font=dial.canvas.itemcget(i, "font")).metrics("linespace")
               for i in dial.canvas.find_all() if dial.canvas.type(i) == "text"]
    return max(heights) if heights else None




def rescale(scale):
    """
    Sets the scale and lets the window grow to fit. CustomTkinter puts a
    window back to its old size on a scale change and holds it there (the app
    releases that; see uBITX CEC Desktop's _set_scaling), which would squeeze
    the dials and hide what this measures.
    """
    ctk.set_widget_scaling(scale)
    root.update()
    root.tk.call("wm", "maxsize", root._w, 10000, 10000)
    root.tk.call("wm", "geometry", root._w, "")
    root.update()


base = {name: (knob_width(d), label_height(d)) for name, d in dials.items()}
results = []
for scale in (2.0, 1.5):
    rescale(scale)
    for name, d in dials.items():
        knob = knob_width(d)
        ok = abs(knob - base[name][0] * scale) <= 4
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name} at {scale}: knob {knob} px, "
              f"expected about {base[name][0] * scale:.0f}")
        lab = label_height(d)
        if lab is not None:
            ok = lab >= base[name][1] * scale * 0.8
            results.append(ok)
            print(f"{'PASS' if ok else 'FAIL'}  {name} at {scale}: labels {lab} px high, "
                  f"expected about {base[name][1] * scale:.0f}")
rescale(1.0)
for name, d in dials.items():
    ok = knob_width(d) == base[name][0]
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name} back at 1.0: knob {knob_width(d)} px, was {base[name][0]}")
root.destroy()
print(f"{sum(results)}/{len(results)} passed")
