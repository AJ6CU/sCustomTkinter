#!/usr/bin/python3
"""
Checks for the 2026-11-11 library tidy-ups. Run it, read the console:

    python examples/validation-tests/test_tidyups_2026_11_11.py

It prints PASS or FAIL per check and a total, then closes its own window.
Every check is automatic; nothing needs clicking.

1. DIALS: the wheel, trackpad, click and drag handling now lives once in
   the dial base class. One wheel notch is one step on each of the three
   dials (the "break" that stops it repeating on three layers); a disabled
   dial ignores it; a drag needs 2 px on the continuous and range dials and
   25 px on the selector.
2. METERS: sCTkSMeter and sCTkSMeterBar now scale their canvas fonts with
   the display, as sCTkNotebook does. At widget scaling 2.0 the drawn font
   is twice the size of the theme's.
3. TEARDOWN: a widget destroyed with a deferred call still pending no
   longer prints `invalid command name "...<lambda>"`. Tk's background
   error handler is replaced for the run, so any such error is counted.
"""
import types

import customtkinter as ctk
from scustomtkinter import (sCTk, sCTkFrame, sCTkDialContinuous, sCTkDialRange,
                            sCTkDialSelector, sCTkSMeter, sCTkSMeterBar,
                            sCTkButtonPrimary, sCTkSlider, sCTkSegmentedButton)
from scustomtkinter.themeable_widget import defer

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail and not ok else ""))


root = sCTk()
root.geometry("700x500")
root.title("Tidy-ups 2026-11-11")
frame = sCTkFrame(root)
frame.pack(expand=True, fill="both", padx=10, pady=10)

# Tk's background errors -- "invalid command name ..." among them -- counted.
tk_errors = []
root.tk.createcommand("bgerror", lambda *args: tk_errors.append(" ".join(map(str, args))))
root.report_callback_exception = lambda *exc: tk_errors.append(repr(exc[1]))


def wheel(delta=0, num=0):
    return types.SimpleNamespace(delta=delta, num=num)


def drag(y):
    return types.SimpleNamespace(y=y)


def run_dial_checks():
    cont = sCTkDialContinuous(frame, divisions=24)
    rng = sCTkDialRange(frame, from_=0, to=100)
    sel = sCTkDialSelector(frame, labels=["A", "B", "C", "D"])
    for d in (cont, rng, sel):
        d.pack(side="left", padx=5)
    root.update()

    rng.set(50)
    sel.set(1)
    for name, dial in (("continuous", cont), ("range", rng), ("selector", sel)):
        before = dial._current_value
        out = dial._process_scroll_wheel(wheel(delta=120))
        step = (dial._current_value - before) % (24 if dial is cont else 1000)
        check(f"dial {name}: one wheel notch is one step", step == 1 and out == "break",
              f"moved {step}, returned {out!r}")
        before = dial._current_value
        dial._process_scroll_wheel(wheel(num=5))
        check(f"dial {name}: Button-5 steps back", dial._current_value != before)

    rng.configure(state="disabled")
    before = rng._current_value
    rng._process_scroll_wheel(wheel(delta=120))
    check("dial range: disabled ignores the wheel", rng._current_value == before)
    rng.configure(state="normal")

    for name, dial, needed in (("continuous", cont, 2), ("range", rng, 2), ("selector", sel, 25)):
        dial._on_button_press(drag(100))
        before = dial._current_value
        dial._on_button_motion(drag(100 - needed))          # exactly the threshold: no step
        same = dial._current_value == before
        dial._on_button_motion(drag(100 - needed - 1))      # one past it: a step
        check(f"dial {name}: a drag steps past {needed} px", same and dial._current_value != before)

    for d in (cont, rng, sel):
        d.destroy()


def run_meter_checks():
    ctk.set_widget_scaling(2.0)
    root.update()
    for name, cls in (("SMeter", sCTkSMeter), ("SMeterBar", sCTkSMeterBar)):
        meter = cls(frame, width=300, height=150)
        meter.pack()
        root.update()
        theme = meter._local_defaults.get("font")
        drawn = meter._scaled_font(theme)
        ok = (isinstance(theme, (list, tuple)) and isinstance(drawn, (list, tuple))
              and abs(int(drawn[1])) == abs(int(theme[1])) * 2)
        check(f"{name}: canvas font doubles at scaling 2.0", ok, f"theme {theme}, drawn {drawn}")
        meter.destroy()
    ctk.set_widget_scaling(1.0)
    root.update()


def run_teardown_checks():
    tk_errors.clear()
    # Widgets that defer work at construction, destroyed before it runs.
    for _ in range(5):
        widgets = [sCTkButtonPrimary(frame, text="x"), sCTkSlider(frame),
                   sCTkSegmentedButton(frame, values=["a", "b"]),
                   sCTkDialContinuous(frame), sCTkSMeter(frame)]
        for w in widgets:
            w.destroy()
    ran = []
    w = sCTkButtonPrimary(frame, text="y")
    defer(w, 10, lambda: ran.append("destroyed one ran"))
    alive = sCTkButtonPrimary(frame, text="z")
    defer(alive, 10, lambda: ran.append("alive"))
    w.destroy()

    def finish():
        check("teardown: no 'invalid command name' errors", not tk_errors,
              "; ".join(tk_errors[:3]))
        check("teardown: a destroyed widget's deferred call does not run",
              ran == ["alive"], f"ran {ran}")
        total = len(results)
        passed = sum(results)
        print(f"\n{passed}/{total} passed")
        root.after(300, root.destroy)

    root.after(400, finish)


run_dial_checks()
run_meter_checks()
run_teardown_checks()
root.mainloop()
