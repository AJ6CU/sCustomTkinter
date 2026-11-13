"""
sCTkFrequencyDisplay resizes when the scaling changes, so its digits are not cut off.

    python examples/validation-tests/test_frequency_display_scaling.py

On Windows the display's scale reaches CustomTkinter just after a window is
made; the readout had already measured its room at the old scale, and at 200 %
showed "13.991." with the rest off the edge (uBITX CEC Desktop on a ThinkPad
X1 Carbon, 2026-11-13). set_widget_scaling() does here what that does there.
"""
import customtkinter as ctk
import scustomtkinter as s

root = s.sCTk()
display = s.sCTkFrequencyDisplay(root)
display.pack(padx=10, pady=10)
display.set(14032000) if hasattr(display, "set") else display.configure(value=14032000)
root.update()

results = []
for scale in (1.0, 2.0, 1.5, 0.75):
    ctk.set_widget_scaling(scale)
    root.update()
    _, needed = display._positions()
    has = int(display.canvas.cget("width"))
    ok = has == int(needed)
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  scaling {scale}: the canvas asks for {has} px, the digits need {int(needed)}")
ctk.set_widget_scaling(1.0)
root.destroy()
print(f"{sum(results)}/{len(results)} passed")
