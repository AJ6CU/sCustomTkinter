#!/usr/bin/python3
"""
Covers three things for sCTkButtonPrimary:

1. AUTOMATED: the configure() single-argument query bug fix. Fully assertable.
2. MANUAL/VISUAL: the tuple-based appearance-mode experiment (same approach
   already validated on sCTkComboBox and sCTkSegmentedButton).
3. MANUAL/VISUAL: the disable mechanism. Native state="disabled" (with a
   deferred after_idle color reapply) is the finalized, confirmed-working
   behavior -- an earlier manual-unbind approach was tested and confirmed
   broken (clicks still fired while "disabled"). This script exercises the
   disable/enable cycle repeatedly to confirm that finalized behavior holds:
   clicks silent while disabled, colors correctly returning on every
   re-enable, not just the first one.

   There's no automated check for the color/repaint behavior -- it's a
   visual check as you cycle the toggle button below.
"""
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkButtonPrimary, sCTkLabelPrimary

# ---------------------------------------------------------------------
# Part 1: automated check for the configure() query bug fix
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
root.geometry("500x400")
root.title("Button Primary Checks")

btn_check = sCTkButtonPrimary(root, text="Check Button")

def query_state_returns_tuple():
    # Before fix: pname was bound to the wrapped tuple, so "state" never
    # matched and a malformed argument was forwarded to the native widget.
    result = btn_check.configure("state")
    assert isinstance(result, tuple), f"expected tuple, got {type(result)}"
    assert result[0] == "state", f"expected first element 'state', got {result[0]!r}"
    assert len(result) == 5, f"expected 5-tuple, got {result}"

check("configure('state') returns a proper query tuple", query_state_returns_tuple)

def query_color_property_returns_tuple():
    result = btn_check.configure("fg_color")
    assert isinstance(result, tuple) and len(result) == 5, f"got {result}"

check("configure('fg_color') returns a proper query tuple", query_color_property_returns_tuple)

def positional_dict_applies():
    btn_check.configure({"text": "Changed via dict"})
    assert btn_check.cget("text") == "Changed via dict"

check("configure({...}) positional dict is applied", positional_dict_applies)

def config_alias_works():
    btn_check.config(text="Changed via .config()")
    assert btn_check.cget("text") == "Changed via .config()"

check(".config() routes through the same override as .configure()", config_alias_works)

def state_regression():
    btn_check.state("disabled")
    assert btn_check.get_state() == "disabled"
    btn_check.state("normal")
    assert btn_check.get_state() == "normal"

check("state()/get_state() still work (regression)", state_regression)

print("\n" + "=" * 70)
for label, status, detail in results:
    marker = {"PASS": "[PASS]", "FAIL": "[FAIL]", "ERROR": "[ERR ]"}[status]
    print(f"{marker} {label}")
    if detail:
        print(f"        {detail}")
print("=" * 70 + "\n")

btn_check.destroy()


# ---------------------------------------------------------------------
# Part 2 & 3: manual/visual checks -- tuple experiment + disable mechanism
# ---------------------------------------------------------------------
frame = sCTkFrame(root)
frame.pack(expand=True, fill="both", padx=20, pady=20)

toggle_label = sCTkLabelPrimary(
    frame,
    text="Disable mechanism: native state=\"disabled\" (finalized, no longer a toggle)",
)
toggle_label.pack(pady=(0, 10))

normal_btn = sCTkButtonPrimary(frame, text="Normal")
normal_btn.pack(pady=5)

pressed_btn = sCTkButtonPrimary(frame, text="Forced Pressed")
pressed_btn.pack(pady=5)
pressed_btn.set_pressed(True)

alarm_btn = sCTkButtonPrimary(frame, text="Forced Alarm")
alarm_btn.pack(pady=5)
alarm_btn.set_alarm_state(True)

disabled_btn = sCTkButtonPrimary(frame, text="Disabled -- click me, hover me")
disabled_btn.pack(pady=5)
disabled_btn.state("disabled")

click_count = {"n": 0}
def on_click():
    click_count["n"] += 1
    print(f"disabled_btn was clicked ({click_count['n']} times) -- this should NEVER print "
          f"while the button is disabled.")
disabled_btn.configure(command=on_click)

def toggle_mode():
    current = ctk.get_appearance_mode().lower()
    new_mode = "Light" if current == "dark" else "Dark"
    ctk.set_appearance_mode(new_mode)
    print(f"Switched to {new_mode} -- check that all four buttons above "
          f"(normal/pressed/alarm/disabled) updated their colors correctly, "
          f"including the disabled one.")

mode_btn = sCTkButtonPrimary(frame, text="Toggle Light/Dark", command=toggle_mode)
mode_btn.pack(pady=(15, 5))

def toggle_disabled_btn():
    target = "disabled" if disabled_btn.get_state() == "normal" else "normal"
    disabled_btn.state(target)
    toggle_state_btn.configure(
        text=f"Toggle disabled_btn (currently: {disabled_btn.get_state()})"
    )
    print(f"disabled_btn is now: {disabled_btn.get_state()}")

toggle_state_btn = sCTkButtonPrimary(
    frame, text="Toggle disabled_btn (currently: disabled)", command=toggle_disabled_btn
)
toggle_state_btn.pack(pady=5)

print("Final verification of sCTkButtonPrimary's disable mechanism:")
print("disabled_btn starts disabled -- clicking/hovering it now should do nothing.")
print("Use 'Toggle disabled_btn' to cycle it disabled -> enabled -> disabled -> ... several")
print("times. After EACH toggle to 'enabled', click disabled_btn once to confirm it responds;")
print("after EACH toggle to 'disabled', click it a few times to confirm it stays silent and")
print("its colors visibly return to the gray disabled palette, not stuck on whatever it looked")
print("like before. Repeat at least 3-4 cycles -- a fix that only holds on the first cycle")
print("isn't actually fixed.\n")

root.mainloop()