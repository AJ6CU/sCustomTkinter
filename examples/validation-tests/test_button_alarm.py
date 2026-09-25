#!/usr/bin/python3
"""
Checks the alarm state on all three button tiers.

    python3 test_button_alarm.py

Alarm used to be Primary's alone. Secondary and Tertiary had the three
ordinary states and no way to raise an alarm at all -- so anything that
needed one had to be a Primary, whatever its place in the hierarchy, or be
hand-coloured by the caller.

WHAT TO LOOK FOR

  * Alarm on: all three turn red. The filled tiers fill; the outline tier
    colours its border and text only, and does NOT gain a fill.
  * Alarm takes precedence over pressed: press one, then alarm it, and the
    pressed look gives way.
  * Disabled beats everything: alarm a disabled button and nothing happens.
  * Leaving alarm returns each button to exactly the colours it started with.
"""
import customtkinter as ctk
from scustomtkinter import (sCTk, sCTkFrame, sCTkLabelSecondary, sCTkLabelTertiary,
                            sCTkButtonPrimary, sCTkButtonSecondary, sCTkButtonTertiary)

root = sCTk()
root.title("button alarm state")
root.geometry("640x420")

page = sCTkFrame(root, fg_color="transparent", border_width=0)
page.pack(fill="both", expand=True, padx=20, pady=20)

sCTkLabelSecondary(page, text="The three tiers",
                   font=("Arial", 14, "bold")).pack(anchor="w")
row = sCTkFrame(page, fg_color="transparent", border_width=0)
row.pack(anchor="w", pady=10)

buttons = {
    "primary": sCTkButtonPrimary(row, text="Primary", width=150),
    "secondary": sCTkButtonSecondary(row, text="Secondary", width=150),
    "tertiary": sCTkButtonTertiary(row, text="Tertiary", width=150),
}
for button in buttons.values():
    button.pack(side="left", padx=6)

status = sCTkLabelTertiary(page, text="", font=("Arial", 11), justify="left")
status.pack(anchor="w", pady=(4, 12))


def show():
    parts = []
    for name, button in buttons.items():
        parts.append(f"{name}: alarm={button.is_alarm} pressed={button.is_pressed} "
                     f"state={button.get_state()}")
    status.configure(text="\n".join(parts))
    print("\n".join(parts) + "\n")


def alarm(active):
    for button in buttons.values():
        button.set_alarm_state(active)
    show()


def press():
    """Pressed first, then alarm -- alarm should win and clear pressed."""
    for button in buttons.values():
        button.set_pressed(True)
    show()


def alarm_over_pressed():
    press()
    alarm(True)
    ok = all(not b.is_pressed and b.is_alarm for b in buttons.values())
    print(f"  alarm takes precedence over pressed: {'PASS' if ok else 'FAIL'}\n")


def alarm_while_disabled():
    """Disabled beats alarm: nothing should change."""
    for button in buttons.values():
        button.set_alarm_state(False)
        button.state("disabled")
        button.set_alarm_state(True)
    ok = all(not b.is_alarm for b in buttons.values())
    print(f"  a disabled button cannot be alarmed: {'PASS' if ok else 'FAIL'}\n")
    for button in buttons.values():
        button.state("normal")
    show()


controls = sCTkFrame(page, fg_color="transparent", border_width=0)
controls.pack(anchor="w")
for text, action in (("Alarm on", lambda: alarm(True)),
                     ("Alarm off", lambda: alarm(False)),
                     ("Press", press),
                     ("Alarm over pressed", alarm_over_pressed),
                     ("Alarm while disabled", alarm_while_disabled)):
    sCTkButtonSecondary(controls, text=text, width=150,
                        command=action).pack(side="left", padx=4, pady=4)

show()
root.mainloop()
