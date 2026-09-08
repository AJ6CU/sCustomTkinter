#!/usr/bin/python3
"""
Where is sCTkOptionMenuSecondary's border?

The theme gives Secondary border_width 1.25 and a border_color, and it is
built as a composite -- an sCTkFrame wrapping an inner CTkOptionMenu -- while
Primary is a plain subclass. The question is what that frame's border is
actually outlining: the CLOSED control, or the OPEN dropdown list.

It matters because a frame can only draw around the widget it contains. The
dropdown is a separate toplevel window, so a wrapping frame cannot put a
border on it. If the outline turns out to be around the open list, something
other than the composite is responsible and the plan to convert Secondary to a
subclass rests on a wrong premise.

Put the two side by side, open both dropdowns, and look.
"""
import customtkinter as ctk

from scustomtkinter import (sCTk, sCTkFrame, sCTkButtonPrimary,
                            sCTkLabelPrimary, sCTkLabelSecondary,
                            sCTkOptionMenuPrimary, sCTkOptionMenuSecondary)

VALUES = ["Alpha", "Beta", "Gamma", "Delta"]


if __name__ == "__main__":
    root = sCTk()
    root.geometry("560x380")
    root.title("OptionMenu border: button or dropdown?")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)
    base.grid_columnconfigure(0, weight=1)
    base.grid_columnconfigure(1, weight=1)

    sCTkLabelPrimary(base, text="Primary").grid(row=0, column=0, pady=(10, 4))
    sCTkLabelPrimary(base, text="Secondary").grid(row=0, column=1, pady=(10, 4))

    primary = sCTkOptionMenuPrimary(base, values=VALUES)
    primary.grid(row=1, column=0, padx=20, pady=6)

    secondary = sCTkOptionMenuSecondary(base, values=VALUES)
    secondary.grid(row=1, column=1, padx=20, pady=6)

    sCTkLabelSecondary(
        base,
        text="Open each dropdown. Is the outline around the closed control,\n"
             "or around the open list?",
    ).grid(row=2, column=0, columnspan=2, pady=(14, 6))

    # --- what each widget actually reports ----------------------------------
    def report():
        print("\n--- Primary ---")
        for key in ("border_width", "border_color", "fg_color"):
            try:
                print(f"  {key:14} {primary.cget(key)}")
            except Exception as exc:
                print(f"  {key:14} <{exc}>")

        print("--- Secondary ---")
        for key in ("border_width", "border_color", "fg_color"):
            try:
                print(f"  {key:14} {secondary.cget(key)}")
            except Exception as exc:
                print(f"  {key:14} <{exc}>")

        # The composite question: does the OUTER widget hold the border, and
        # is there an inner menu it delegates to?
        inner = getattr(secondary, "_menu", None)
        print("  inner _menu    ", type(inner).__name__ if inner else "none")
        if inner is not None:
            for key in ("fg_color", "values"):
                try:
                    print(f"    inner {key:8} {inner.cget(key)}")
                except Exception as exc:
                    print(f"    inner {key:8} <{exc}>")

        # This is the divergence that started the whole thread.
        print("\n  primary.cget('values')  ", end="")
        try:
            print(primary.cget("values"))
        except Exception as exc:
            print(f"<{exc}>")
        print("  secondary.cget('values')", end=" ")
        try:
            print(secondary.cget("values"))
        except Exception as exc:
            print(f"<{exc}>")

    # --- make the border unmissable, to see what it surrounds ---------------
    def loud_border():
        for widget in (primary, secondary):
            try:
                widget.configure(border_width=3, border_color=("#FF0000", "#FF0000"))
            except Exception as exc:
                print(f"{type(widget).__name__}: {exc}")

    def toggle_state():
        target = "disabled" if primary.get_state() == "normal" else "normal"
        primary.state(target)
        secondary.state(target)
        btn_state.configure(text="Enable" if target == "disabled" else "Disable")

    def toggle_mode():
        ctk.set_appearance_mode(
            "Light" if ctk.get_appearance_mode() == "Dark" else "Dark")

    row = sCTkFrame(base, fg_color="transparent")
    row.grid(row=3, column=0, columnspan=2, pady=10)

    sCTkButtonPrimary(row, text="Report", command=report).pack(side="left", padx=4)
    sCTkButtonPrimary(row, text="Red border, 3px", command=loud_border).pack(side="left", padx=4)
    btn_state = sCTkButtonPrimary(row, text="Disable", command=toggle_state)
    btn_state.pack(side="left", padx=4)
    sCTkButtonPrimary(row, text="Light/Dark", command=toggle_mode).pack(side="left", padx=4)

    report()
    root.mainloop()