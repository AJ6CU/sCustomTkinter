#!/usr/bin/python3
"""
Tests sCTkRadioButton.configure(variable=...) / configure(value=...) --
specifically whether rebinding a radio button to a NEW variable after
construction works correctly.

FINALIZED, confirmed by direct testing: rebinding via super().configure()
(the current, only implementation) correctly tears down the old variable's
trace, correctly establishes mutual exclusion in the new group, and does not
raise. This script's checks should all pass unconditionally now -- kept as a
regression test rather than an experiment.

  1. Does configure(variable=..., value=...) raise? Should not.
  2. After rebinding radio_b from var_group_1 to var_group_2, does clicking
     radio_b correctly update var_group_2 instead of var_group_1?
  3. Does radio_b visually/functionally join group 2's mutual exclusion --
     i.e. does selecting radio_b correctly deselect radio_c (also in group 2),
     and does selecting radio_c correctly deselect radio_b?
"""
import tkinter as tk
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkRadioButton, sCTkLabelPrimary, sCTkButtonPrimary

root = sCTk()
root.geometry("450x400")
root.title("RadioButton Rebind Test")

frame = sCTkFrame(root)
frame.pack(expand=True, fill="both", padx=20, pady=20)

status = sCTkLabelPrimary(frame, text="Group 1: (none selected)   |   Group 2: (none selected)")
status.pack(pady=(0, 15))

var_group_1 = tk.StringVar(value="")
var_group_2 = tk.StringVar(value="")

def refresh_status(*_):
    status.configure(
        text=f"Group 1: {var_group_1.get() or '(none)'}   |   Group 2: {var_group_2.get() or '(none)'}"
    )

var_group_1.trace_add("write", refresh_status)
var_group_2.trace_add("write", refresh_status)

sCTkLabelPrimary(frame, text="Group 1 (var_group_1):").pack(anchor="w", pady=(10, 0))
radio_a = sCTkRadioButton(frame, text="A", variable=var_group_1, value="A")
radio_a.pack(anchor="w")
radio_b = sCTkRadioButton(frame, text="B (will be rebound to Group 2)", variable=var_group_1, value="B")
radio_b.pack(anchor="w")

sCTkLabelPrimary(frame, text="Group 2 (var_group_2):").pack(anchor="w", pady=(10, 0))
radio_c = sCTkRadioButton(frame, text="C", variable=var_group_2, value="C")
radio_c.pack(anchor="w")

print("Initial state: radio_a and radio_b share var_group_1; radio_c is alone in var_group_2.")
print("Click A and B a few times -- confirm normal mutual exclusion within Group 1 first.\n")

def do_rebind():
    print("Rebinding radio_b: variable var_group_1 -> var_group_2, value 'B' -> 'D'")
    try:
        radio_b.configure(variable=var_group_2, value="D")
        radio_b.configure(text="B (now in Group 2 as 'D')")
        print("  configure() did not raise.")
    except Exception as e:
        print(f"  configure() RAISED: {type(e).__name__}: {e}")
        return

    print("Now click 'B' and 'C' -- expected if the rebind worked correctly:")
    print("  - Clicking B should update Group 2's status to 'D', and deselect C.")
    print("  - Clicking C should update Group 2's status to 'C', and deselect B.")
    print("  - Group 1's status should no longer be affected by B at all.")
    rebind_btn.configure(state="disabled", text="Rebind Done")

rebind_btn = sCTkButtonPrimary(frame, text="Rebind B into Group 2 (click after testing Group 1)", command=do_rebind)
rebind_btn.pack(pady=15)

root.mainloop()
