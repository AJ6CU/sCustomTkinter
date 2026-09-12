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
  * theme     -- light and dark, since the strip is canvas-drawn and does not
                 get CustomTkinter's automatic repaint for free

Also worth trying while it runs: hover across the tabs, and resize the window
to check the pages follow.
"""
import customtkinter as ctk

from scustomtkinter import (sCTk, sCTkFrame, sCTkButtonPrimary,
                            sCTkLabelPrimary, sCTkLabelSecondary,
                            sCTkComboBox, sCTkNotebook)

TAB_NAMES = ["Receiver", "Transmitter", "Audio", "Filters", "System Logs"]


def build_page(page, name):
    """Puts one labelled frame on a page, as the brief asks."""
    panel = sCTkFrame(page, border_width=1, corner_radius=8)
    panel.pack(expand=True, fill="both", padx=12, pady=12)

    sCTkLabelPrimary(panel, text=f"This is the {name} tab").pack(
        expand=True, padx=20, pady=20)


if __name__ == "__main__":
    root = sCTk()
    root.title("sCTkNotebook test bench")
    root.geometry("640x420")

    base = sCTkFrame(root, border_width=0, fg_color="transparent")
    base.pack(expand=True, fill="both", padx=16, pady=(16, 8))

    notebook = sCTkNotebook(base, side="left", tab_width=34)
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

    width_box = sCTkComboBox(tray, values=["28px", "34px", "44px", "60px"],
                             command=on_width_changed, width=90)
    width_box.pack(side="left", padx=4)
    width_box.set("34px")

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
    print("selected  :", notebook.get())

    notebook.set("Audio")
    print("after set :", notebook.get(), "(expected Audio)")

    notebook.rename("System Logs", "Logs")
    print("renamed   :", notebook.tabs(), "(Logs keeps its position and page)")

    notebook.set(TAB_NAMES[0])
    refresh_status()
    print("------------\n")

    root.mainloop()
