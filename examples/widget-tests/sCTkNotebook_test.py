#!/usr/bin/python3
"""
Test bench for sCTkNotebook.

Five tabs, each holding a frame with one label naming it. Controls along the
bottom exercise the things most likely to be wrong:

  * side      -- the strip moves between the left and right edges, and the
                 rotated labels flip with it so they always read outside-in
  * tab_width -- the strip is an explicit width, not measured
  * state     -- disabled dims the strip and stops selection, but does NOT
                 disable what is on the pages
  * tab_style -- rounded, matching the rest of the library, or angled, the
                 shape of a real notebook divider
  * text      -- "auto" reads outside-in and flips with the side; "up" and
                 "down" pin the direction; "horizontal" lays it flat, which
                 needs a wider strip
  * border    -- the page outline, drawn with a gap where the selected tab
                 meets it
  * theme     -- light and dark, since the strip is canvas-drawn and does not
                 get CustomTkinter's automatic repaint for free

Shrink the window vertically until the tabs no longer fit: the strip scrolls
under the wheel. required_length() reports the height it would rather have.

Also worth trying while it runs: hover across the tabs, and resize the window
to check the pages follow.
"""
import customtkinter as ctk

from scustomtkinter import (sCTk, sCTkFrame, sCTkButtonPrimary,
                            sCTkLabelPrimary, sCTkLabelSecondary,
                            sCTkComboBox, sCTkNotebook)

TAB_NAMES = ["Receiver", "Transmitter", "Audio", "Filters", "System Logs"]


def build_page(page, name):
    """
    Puts one labelled frame on a page.

    The frame is borderless on purpose. The notebook draws the page outline
    itself, broken where the selected tab meets it -- a second border here
    would sit just inside the first and hide the join.
    """
    panel = sCTkFrame(page, border_width=0, fg_color="transparent")
    panel.pack(expand=True, fill="both")

    sCTkLabelPrimary(panel, text=f"This is the {name} tab").pack(
        expand=True, padx=20, pady=20)


if __name__ == "__main__":
    root = sCTk()
    root.title("sCTkNotebook test bench")
    root.geometry("640x420")

    base = sCTkFrame(root, border_width=0, fg_color="transparent")
    base.pack(expand=True, fill="both", padx=16, pady=(16, 8))

    notebook = sCTkNotebook(base, side="left", tab_width=34,
                            tab_style="rounded", show_page_border=True)
    notebook.pack(expand=True, fill="both")

    for tab_name in TAB_NAMES:
        build_page(notebook.add(tab_name), tab_name)

    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------
    tray = sCTkFrame(root, fg_color="transparent", border_width=0)
    tray.pack(fill="x", padx=16, pady=(0, 14))

    status = sCTkLabelSecondary(tray, text="")
    status.pack(side="left", padx=(4, 16))

    def refresh_status():
        status.configure(
            text=f"selected: {notebook.get()}   state: {notebook.get_state()}")

    def flip_side():
        new_side = "right" if notebook.cget("side") == "left" else "left"
        notebook.configure(side=new_side)
        btn_side.configure(text=f"Move strip to "
                                f"{'left' if new_side == 'right' else 'right'}")
        refresh_status()

    btn_side = sCTkButtonPrimary(tray, text="Move strip to right",
                                 command=flip_side, width=150)
    btn_side.pack(side="left", padx=4)

    def on_width_changed(choice):
        notebook.configure(tab_width=int(choice.replace("px", "")))

    width_box = sCTkComboBox(tray, values=["28px", "34px", "44px", "60px", "100px"],
                             command=on_width_changed, width=90)
    width_box.pack(side="left", padx=4)
    width_box.set("34px")

    def flip_style():
        new_style = "angled" if notebook.cget("tab_style") == "rounded" else "rounded"
        notebook.configure(tab_style=new_style)
        btn_style.configure(text=f"Tabs: {new_style}")

    btn_style = sCTkButtonPrimary(tray, text="Tabs: rounded",
                                  command=flip_style, width=120)
    btn_style.pack(side="left", padx=4)

    def on_orientation_changed(choice):
        notebook.configure(text_orientation=choice)
        # Flat text needs room across the strip rather than along it.
        if choice == "horizontal" and notebook.cget("tab_width") < 90:
            notebook.configure(tab_width=100)
            width_box.set("100px")

    orient_box = sCTkComboBox(
        tray, values=["auto", "up", "down", "horizontal"],
        command=on_orientation_changed, width=110)
    orient_box.pack(side="left", padx=4)
    orient_box.set("auto")

    def toggle_border():
        on = not notebook.cget("show_page_border")
        notebook.configure(show_page_border=on)
        btn_border.configure(text=f"Border: {'on' if on else 'off'}")

    btn_border = sCTkButtonPrimary(tray, text="Border: on",
                                   command=toggle_border, width=110)
    btn_border.pack(side="left", padx=4)

    def toggle_state():
        target = "disabled" if notebook.get_state() == "normal" else "normal"
        notebook.configure(state=target)
        btn_state.configure(
            text="Enable notebook" if target == "disabled" else "Disable notebook")
        refresh_status()
        print(f"state = {notebook.get_state()}  "
              f"(the labels on the pages stay live -- disabling does not cascade)")

    btn_state = sCTkButtonPrimary(tray, text="Disable notebook",
                                  command=toggle_state, width=150)
    btn_state.pack(side="left", padx=4)

    sCTkButtonPrimary(
        tray, text="Light / Dark", width=110,
        command=lambda: ctk.set_appearance_mode(
            "Light" if ctk.get_appearance_mode() == "Dark" else "Dark")
    ).pack(side="right", padx=4)

    refresh_status()

    # ------------------------------------------------------------------
    # A quick pass over the API, so a breakage shows on the console rather
    # than only on screen.
    # ------------------------------------------------------------------
    print("--- boot ---")
    print("tabs      :", notebook.tabs())
    print("wants     :", notebook.required_length(),
          "px of height for all tabs without scrolling")
    print("selected  :", notebook.get())

    notebook.set("Audio")
    print("after set :", notebook.get(), "(expected Audio)")

    notebook.rename("System Logs", "Logs")
    print("renamed   :", notebook.tabs(), "(Logs keeps its position and page)")

    notebook.set(TAB_NAMES[0])
    refresh_status()
    print("------------\n")

    root.mainloop()
