"""
sCTkNotebook grows in proportion when the scaling changes.

    python examples/validation-tests/test_notebook_scaling.py

The page inset was scaled twice (once by the notebook, once by CustomTkinter's
grid()): 10 px at 1x but 40 px at 2x. The same at 1x, so it never showed until
uBITX CEC Desktop ran at Windows' 200 % (2026-11-13).
"""
import time
import tkinter as tk
import customtkinter as ctk
import scustomtkinter as s

root = s.sCTk()
def pump(ms=400):
    end = time.monotonic() + ms / 1000
    while time.monotonic() < end:
        root.update(); time.sleep(0.005)

nb = s.sCTkNotebook(root, side="left", tab_width=30)
nb.pack(padx=4, pady=4)
page = nb.add("First"); nb.add("Second")
ctk.CTkButton(page, text="page", width=300, height=200).pack()
pump()
base = (nb.winfo_reqwidth(), nb.winfo_reqheight())
results = []
for scale in (2.0, 1.5):
    ctk.set_widget_scaling(scale)
    tk.Tk.wm_maxsize(root, 4000, 4000)
    pump()
    got = (nb.winfo_reqwidth(), nb.winfo_reqheight())
    want = (round(base[0] * scale), round(base[1] * scale))
    ok = abs(got[0] - want[0]) <= 2 and abs(got[1] - want[1]) <= 2
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  scaling {scale}: {got[0]}x{got[1]}, in proportion would be {want[0]}x{want[1]}")
ctk.set_widget_scaling(1.0)
root.destroy()
print(f"{sum(results)}/{len(results)} passed")
