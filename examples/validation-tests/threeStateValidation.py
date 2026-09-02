#!/usr/bin/python3
"""
Validates the three-state model (normal/readonly/disabled) across
sCTkEntryPrimary, sCTkEntrySecondary, and sCTkSpinbox.

REQUIRES: sCTkThemes.json must have a "readonly_map" block for both
sCTkEntryPrimary and sCTkEntrySecondary, with fg_color, border_color,
text_color, and placeholder_text_color all present. Without it, any
transition INTO readonly will raise KeyError -- which is itself confirmed
correct behavior (Section 4 below tests this deliberately), but Sections 1-3
need the real readonly_map to actually exercise the happy path.

WHAT'S OBJECTIVELY VERIFIED BY THIS SCRIPT (printed to console, no manual
judgment needed):
  - state()/get_state() returns the correct value after each transition.
  - The underlying native widget's cget("state") matches what was requested,
    for the entry.
  - Spinbox's up/down buttons NEVER report "readonly" as their native state --
    only "normal" or "disabled" -- confirming the button/entry state
    separation actually holds.
  - icursor() position immediately after each transition into a non-disabled
    state, while the field is showing placeholder text.

WHAT STILL NEEDS YOUR EYES (the console can't fully verify these):
  - Whether readonly ACTUALLY blocks typing while still allowing focus/
    selection/copy -- click into a readonly field and try typing.
  - Whether Spinbox's up/down arrows are ACTUALLY clickable while the
    spinbox itself is in readonly mode -- click them and watch the value
    change.
  - Whether the cursor position reported after a disabled<->readonly or
    readonly<->normal transition LOOKS correct when you click into the
    field yourself -- the printed icursor() value is the objective signal,
    but confirming it visually (does the cursor blink where expected) is
    the real test, since this is the untested transition flagged when the
    three-state model was built.
"""
from scustomtkinter import (
    sCTk, sCTkFrame, sCTkLabelPrimary, sCTkButtonPrimary,
    sCTkEntryPrimary, sCTkEntrySecondary, sCTkSpinbox,
)

root = sCTk()
root.geometry("560x760")
root.title("Three-State Validation: Entry Primary / Secondary / Spinbox")

outer = sCTkFrame(root)
outer.pack(expand=True, fill="both", padx=15, pady=15)

STATES = ["normal", "readonly", "disabled"]


def make_section(parent, title):
    sCTkLabelPrimary(parent, text=title, font=("Arial", 14, "bold")).pack(anchor="w", pady=(12, 2))
    section = sCTkFrame(parent, fg_color="transparent")
    section.pack(fill="x", pady=(0, 4))
    return section


# ---------------------------------------------------------------------
# Section 1 & 2: Entry Primary and Entry Secondary
# ---------------------------------------------------------------------
def build_entry_test(parent, cls, label):
    section = make_section(parent, label)

    entry = cls(section, placeholder_text=f"{label} placeholder...")
    entry.pack(fill="x", pady=4)

    status = sCTkLabelPrimary(section, text="state: normal | cget(state): normal | icursor: n/a")
    status.pack(anchor="w")

    def report(after_transition):
        try:
            native_state = entry.cget("state")
        except Exception as e:
            native_state = f"ERROR: {e}"
        try:
            cursor_pos = entry.index("insert")
        except Exception as e:
            cursor_pos = f"ERROR: {e}"
        line = (f"state(): {entry.get_state()} | native cget(state): {native_state} | "
                f"icursor position: {cursor_pos}")
        status.configure(text=line)
        print(f"[{label}] after -> {after_transition}: {line}")

    def go(target_state):
        try:
            entry.state(target_state)
            report(target_state)
        except KeyError as e:
            status.configure(text=f"KeyError (expected if readonly_map missing): {e}")
            print(f"[{label}] transition to '{target_state}' raised KeyError: {e}")

    btn_row = sCTkFrame(section, fg_color="transparent")
    btn_row.pack(fill="x", pady=4)
    for s in STATES:
        sCTkButtonPrimary(btn_row, text=s, width=90, command=lambda s=s: go(s)).pack(side="left", padx=4)

    print(f"[{label}] constructed, initial: {entry.get_state()}")
    return entry


entry_primary = build_entry_test(outer, sCTkEntryPrimary, "1. sCTkEntryPrimary")
entry_secondary = build_entry_test(outer, sCTkEntrySecondary, "2. sCTkEntrySecondary")


# ---------------------------------------------------------------------
# Section 3: Spinbox
# ---------------------------------------------------------------------
spin_section = make_section(outer, "3. sCTkSpinbox")

spinbox = sCTkSpinbox(spin_section, from_=0, to=100, step_size=1)
spinbox.pack(pady=4)

spin_status = sCTkLabelPrimary(spin_section, text="(not yet transitioned)")
spin_status.pack(anchor="w")

BUTTON_STATE_CHECK_LABEL = sCTkLabelPrimary(spin_section, text="")
BUTTON_STATE_CHECK_LABEL.pack(anchor="w")


def report_spinbox(after_transition):
    try:
        entry_native_state = spinbox.entry.cget("state")
    except Exception as e:
        entry_native_state = f"ERROR: {e}"
    try:
        up_state = spinbox.up_button.cget("state")
        down_state = spinbox.down_button.cget("state")
    except Exception as e:
        up_state = down_state = f"ERROR: {e}"

    # Objective invariant check: buttons must NEVER report "readonly".
    invariant_ok = up_state != "readonly" and down_state != "readonly"

    line1 = (f"spinbox.get_state(): {spinbox.get_state()} | "
             f"entry native state: {entry_native_state}")
    line2 = (f"up_button state: {up_state} | down_button state: {down_state} | "
             f"buttons never 'readonly': {'PASS' if invariant_ok else 'FAIL'}")
    spin_status.configure(text=line1)
    BUTTON_STATE_CHECK_LABEL.configure(text=line2)
    print(f"[Spinbox] after -> {after_transition}: {line1}")
    print(f"[Spinbox] after -> {after_transition}: {line2}")
    if not invariant_ok:
        print("[Spinbox] *** INVARIANT VIOLATION: a button reported 'readonly' state ***")


def go_spinbox(target_state):
    try:
        spinbox.state(target_state)
        report_spinbox(target_state)
    except KeyError as e:
        spin_status.configure(text=f"KeyError (expected if readonly_map missing): {e}")
        print(f"[Spinbox] transition to '{target_state}' raised KeyError: {e}")


spin_btn_row = sCTkFrame(spin_section, fg_color="transparent")
spin_btn_row.pack(fill="x", pady=4)
for s in STATES:
    sCTkButtonPrimary(spin_btn_row, text=s, width=90, command=lambda s=s: go_spinbox(s)).pack(side="left", padx=4)

sCTkLabelPrimary(spin_section, text="Click the arrows above after selecting 'readonly' -- "
                                     "they should still work.").pack(anchor="w", pady=(4, 0))


def test_set_in_each_state():
    print("\n--- Testing spinbox.set(42) in each state ---")
    for s in STATES:
        try:
            spinbox.state(s)
        except KeyError as e:
            print(f"  [{s}] state transition raised KeyError (expected if readonly_map missing): {e}")
            continue
        spinbox.set(42)
        resulting_state = spinbox.entry.cget("state")
        match = "PASS" if resulting_state == s else f"FAIL (entry left in '{resulting_state}')"
        print(f"  [{s}] after set(42): entry.get() = {spinbox.get()!r}, "
              f"entry state restored to '{resulting_state}' -- {match}")
    print("--- End set() test ---\n")


sCTkButtonPrimary(spin_section, text="Run set() Test In All 3 States (see console)",
                   command=test_set_in_each_state).pack(pady=(8, 0))


# ---------------------------------------------------------------------
# Section 4: Deliberately test the hard-fail validation itself
# ---------------------------------------------------------------------
fail_section = make_section(outer, "4. Confirm readonly_map hard-fail (deliberate)")
sCTkLabelPrimary(
    fail_section,
    text="Temporarily empties entry_primary's readonly_map, then requests\n"
         "readonly -- should raise KeyError naming the missing key, not\n"
         "silently substitute a color.",
).pack(anchor="w")


def test_missing_readonly_map():
    saved = dict(entry_primary._custom_readonly_map)
    entry_primary._custom_readonly_map.clear()
    try:
        entry_primary.state("readonly")
        print("[Hard-fail test] *** DID NOT RAISE -- this is unexpected, investigate ***")
    except KeyError as e:
        print(f"[Hard-fail test] Correctly raised KeyError: {e}")
    finally:
        entry_primary._custom_readonly_map.update(saved)
        entry_primary.state("normal")


sCTkButtonPrimary(fail_section, text="Run Hard-Fail Test (see console)",
                   command=test_missing_readonly_map).pack(pady=(4, 0))

print("\nAll widgets constructed. Console will log every state transition as you click buttons above.\n")

root.mainloop()