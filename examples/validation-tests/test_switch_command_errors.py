#!/usr/bin/python3
"""
Demonstrates two distinct problems in sCTkSwitch's command-error handling.

Both are now FINALIZED, confirmed-correct behavior (no more toggle) --
exceptions from user commands propagate normally rather than being silently
swallowed. Running this script should reproduce, unconditionally:

  1. switch_valuerror: raises ValueError visibly (Tkinter's default
     callback-exception handling reports it to the console; the app keeps
     running).
  2. switch_typeerror: raises a confusing SECOND error (a "missing required
     argument" TypeError from the retry-with-no-arguments fallback) chained
     on top of the real bug's TypeError -- Python's exception chaining keeps
     both visible ("During handling of the above exception..."), so the real
     bug is still findable, just not the last thing printed. This masking
     behavior is a known, unfixed issue (see sctk_switch.py's
     _execute_safe_command_forwarding docstring) -- not addressed by this
     script, just demonstrated by it.
  3. switch_ok_noarg: a control case, correctly defined as taking no
     arguments at all. Should keep working with no errors either way.
"""
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkSwitch, sCTkLabelPrimary

root = sCTk()
root.geometry("500x350")
root.title("Switch Command Error Handling Test")

frame = sCTkFrame(root)
frame.pack(expand=True, fill="both", padx=20, pady=20)


# ---------------------------------------------------------------------
# 1. A command with an ordinary, unrelated bug (ValueError)
# ---------------------------------------------------------------------
def buggy_command_valueerror(value):
    print(f"[switch_valuerror] command started running (value={value!r})")
    raise ValueError("deliberate ordinary bug, unrelated to argument count")

sCTkLabelPrimary(frame, text="1. Command raises ValueError (an ordinary bug):").pack(anchor="w", pady=(0, 2))
switch_valuerror = sCTkSwitch(frame, text="Toggle me", command=buggy_command_valueerror)
switch_valuerror.pack(anchor="w", pady=(0, 15))

# ---------------------------------------------------------------------
# 2. A command that raises TypeError for a reason UNRELATED to arg count
# ---------------------------------------------------------------------
call_count = {"n": 0}

def buggy_command_typeerror(value):
    call_count["n"] += 1
    print(f"[switch_typeerror] command started running, call #{call_count['n']} (value={value!r})")
    count_label.configure(text=f"switch_typeerror call count: {call_count['n']}")
    # This TypeError has nothing to do with the number of arguments --
    # it's a genuine bug: trying to add a string and an int.
    result = "five" + 5

sCTkLabelPrimary(frame, text="2. Command raises TypeError (also an ordinary bug, not an arg-count issue):").pack(anchor="w", pady=(0, 2))
switch_typeerror = sCTkSwitch(frame, text="Toggle me", command=buggy_command_typeerror)
switch_typeerror.pack(anchor="w")
count_label = sCTkLabelPrimary(frame, text="switch_typeerror call count: 0")
count_label.pack(anchor="w", pady=(0, 15))

# ---------------------------------------------------------------------
# 3. Control case: a correctly-defined no-argument command
# ---------------------------------------------------------------------
def working_command_noarg():
    print("[switch_ok_noarg] command ran successfully with no arguments")

sCTkLabelPrimary(frame, text="3. Control: command genuinely takes no arguments (should always work):").pack(anchor="w", pady=(0, 2))
switch_ok_noarg = sCTkSwitch(frame, text="Toggle me", command=working_command_noarg)
switch_ok_noarg.pack(anchor="w")

print("Toggle each switch above and watch the console + call-count label.\n")

root.mainloop()