#!/usr/bin/python3
"""
Covers two separate things from this round:

1. AUTOMATED: sCTkSegmentedButton's state()/get_state() bug fix (self._state ->
   self._custom_current_state). This part is fully assertable, no eyeballing needed.

2. MANUAL/VISUAL: the tuple-based color experiment on both sCTkComboBox and
   sCTkSegmentedButton. Whether CTk's native appearance-mode tracking correctly
   repaints raw (light, dark) tuples -- without any manual _set_appearance_mode
   re-trigger -- can only really be judged by looking at it. This script opens an
   interactive window with both widgets, pre-disabled, plus a button to toggle
   light/dark mode. Watch the colors as you toggle:
     - PASS: both widgets' colors visibly follow the new mode while still disabled.
     - FAIL: colors freeze on whichever mode was active when you called .state("disabled"),
       and don't update until you interact with the widget again.
"""
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkButtonPrimary, sCTkComboBox, sCTkSegmentedButton

# ---------------------------------------------------------------------
# Part 1: automated check for the segmented-button state bug fix
# ---------------------------------------------------------------------
results = []

def check(label, fn):
    try:
        fn()
        results.append((label, "PASS", None))
    except AssertionError as e:
        results.append((label, "FAIL", str(e)))
    except Exception as e:
        results.append((label, "ERROR", f"{type(e).__name__}: {e}"))


root = sCTk()
root.geometry("500x350")
root.title("Tuple Experiment / State Fix Check")

sb_check = sCTkSegmentedButton(root, values=["X", "Y", "Z"])

def sb_state_bug_fixed():
    # Before fix: get_state() always returned "normal" no matter what, because it
    # read self._state, which nothing reachable ever updated after construction.
    assert sb_check.get_state() == "normal", f"expected 'normal' initially, got {sb_check.get_state()!r}"
    sb_check.state("disabled")
    assert sb_check.get_state() == "disabled", \
        f"expected 'disabled' after state('disabled'), got {sb_check.get_state()!r}"
    sb_check.configure(state="normal")
    assert sb_check.get_state() == "normal", \
        f"expected 'normal' after configure(state='normal'), got {sb_check.get_state()!r}"

check("SegmentedButton: get_state() correctly tracks disabled/normal (bug fix)", sb_state_bug_fixed)

print("\n" + "=" * 70)
for label, status, detail in results:
    marker = {"PASS": "[PASS]", "FAIL": "[FAIL]", "ERROR": "[ERR ]"}[status]
    print(f"{marker} {label}")
    if detail:
        print(f"        {detail}")
print("=" * 70 + "\n")

sb_check.destroy()


# ---------------------------------------------------------------------
# Part 2: manual/visual check for the tuple-based appearance-mode experiment
# ---------------------------------------------------------------------
frame = sCTkFrame(root)
frame.pack(expand=True, fill="both", padx=20, pady=20)

cb = sCTkComboBox(frame, values=["Channel A (VHF)", "Channel B (UHF)", "Direct Audio Feed"])
cb.pack(fill="x", pady=10)

sb = sCTkSegmentedButton(frame, values=["Alpha", "Beta", "Gamma"])
sb.pack(fill="x", pady=10)

# Pre-select a segment so the "selected + disabled" color branch in
# _apply_custom_theme_colors() is actually exercised -- with nothing selected,
# every button falls into the plain unselected-disabled path and the
# selected-button color (the hardcoded ("#1F2937", "#FFFFFF") tuple) never runs.
sb.set("Beta")

# Pre-disable both, matching the scenario the experiment is meant to fix.
cb.state("disabled")
sb.state("disabled")

def toggle_mode():
    current = ctk.get_appearance_mode().lower()
    new_mode = "Light" if current == "dark" else "Dark"
    ctk.set_appearance_mode(new_mode)
    mode_label.configure(text=f"Current mode: {new_mode}")
    print(f"Switched to {new_mode} mode -- check whether the (disabled) combobox and "
          f"segmented button above updated their colors on their own.")

mode_label = ctk.CTkLabel(frame, text=f"Current mode: {ctk.get_appearance_mode()}")
mode_label.pack(pady=(10, 0))

toggle_btn = sCTkButtonPrimary(frame, text="Toggle Light/Dark", command=toggle_mode)
toggle_btn.pack(pady=10)

print("Both widgets above are pre-disabled. Click 'Toggle Light/Dark' repeatedly and "
      "watch whether their colors update immediately, with no interaction needed.\n")

root.mainloop()