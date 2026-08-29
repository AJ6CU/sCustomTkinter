#!/usr/bin/python3
"""
Targeted regression test for the configure()/config bugs fixed in:
  - sctk_combobox.py       (single-arg query bug, unreachable dict-merge branch)
  - sctk_segmentedbutton.py (same two, plus missing `config = configure` alias)

This does NOT rerun the existing docs/examples demos -- those only ever call
configure() with keyword arguments, so they never touch the code paths that
were broken. Each check below isolates one specific fixed behavior.

Run this against your branch, then (optionally) check it back out against
main to see which checks fail there, for a clear before/after.
"""
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkComboBox, sCTkSegmentedButton

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
root.geometry("300x200")

# ---------------------------------------------------------------------
# sCTkComboBox
# ---------------------------------------------------------------------
cb = sCTkComboBox(root, values=["A", "B", "C"])

def cb_single_string_query():
    # Before fix: pname was bound to the tuple ("state",), so the "state"
    # comparison never matched and a 1-tuple was forwarded to super().configure(),
    # which is not a valid single positional argument for CTk's configure.
    result = cb.configure("state")
    assert isinstance(result, tuple), f"expected tuple, got {type(result)}"
    assert result[0] == "state", f"expected first element 'state', got {result[0]!r}"
    assert len(result) == 5, f"expected 5-tuple, got {result}"

check("ComboBox: configure('state') returns proper query tuple", cb_single_string_query)

def cb_positional_dict_merge():
    # Before fix: a positional dict was caught by the single-arg branch too
    # (len(args) == 1 doesn't care whether args[0] is a str or a dict), so it
    # never reached the (dead) isinstance(args, dict) branch and was forwarded
    # incorrectly to super().configure() as a wrapped tuple.
    cb.configure({"fg_color": "#ff0000"})
    assert cb.cget("fg_color") in ("#ff0000", ("#ff0000", "#ff0000")), \
        f"fg_color not applied, got {cb.cget('fg_color')!r}"

check("ComboBox: configure({...}) positional dict is applied", cb_positional_dict_merge)

def cb_regression_keyword_state():
    # Baseline: ordinary keyword usage must behave exactly as before the fix.
    cb.configure(state="disabled")
    assert cb.get_state() == "disabled"
    cb.configure(state="normal")
    assert cb.get_state() == "normal"

check("ComboBox: keyword configure(state=...) still works (regression)", cb_regression_keyword_state)


# ---------------------------------------------------------------------
# sCTkSegmentedButton
# ---------------------------------------------------------------------
sb = sCTkSegmentedButton(root, values=["X", "Y", "Z"])

def sb_positional_dict_merge():
    sb.configure({"fg_color": "#00ff00"})
    # No direct getter for fg_color on this widget; absence of an exception
    # plus a values check is the meaningful signal here.
    assert sb.cget("fg_color") is not None

check("SegmentedButton: configure({...}) positional dict doesn't error", sb_positional_dict_merge)

def sb_config_alias_routes_through_override():
    # Before fix: sb.config(...) resolved to the ORIGINAL base configure()
    # (bound at class-definition time in tkinter.Misc), completely bypassing
    # sCTkSegmentedButton's own configure() -- so _apply_custom_theme_colors()
    # never ran and _state was never updated via the custom path.
    sb.config(state="disabled")
    assert sb.get_state() == "disabled", \
        f"expected 'disabled' after .config(), got {sb.get_state()!r} -- config likely bypassed configure()"
    sb.config(state="normal")
    assert sb.get_state() == "normal"

check("SegmentedButton: .config() routes through custom configure()", sb_config_alias_routes_through_override)

def sb_regression_keyword_configure():
    sb.configure(state="disabled")
    assert sb.get_state() == "disabled"
    sb.configure(state="normal")
    assert sb.get_state() == "normal"

check("SegmentedButton: keyword configure(state=...) still works (regression)", sb_regression_keyword_configure)


# ---------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------
print("\n" + "=" * 70)
for label, status, detail in results:
    marker = {"PASS": "[PASS]", "FAIL": "[FAIL]", "ERROR": "[ERR ]"}[status]
    print(f"{marker} {label}")
    if detail:
        print(f"        {detail}")
print("=" * 70)

failed = [r for r in results if r[1] != "PASS"]
if failed:
    print(f"\n{len(failed)} of {len(results)} checks did not pass.")
else:
    print(f"\nAll {len(results)} checks passed.")

root.destroy()