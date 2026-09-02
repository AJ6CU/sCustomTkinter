#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Tabview
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary, sCTkLabelPrimary, sCTk, sCTkTabview

if __name__ == "__main__":

    root = sCTk()
    root.geometry("640x480")
    root.title("sCTkTabview Container Validation Bench")
    root.configure(fg_color=("#F1F5F9", "#1C1C1C"))

    # 2. Mount custom master backplane frame capsule container
    base = sCTkFrame(root, border_width=2)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    # 3. Instantiate our custom multi-page tab container widget cleanly
    widget = sCTkTabview(base)
    widget.pack(expand=True, fill="both", padx=10, pady=10)

    # Define our targeted operational dashboard page labels string array
    tab_pages = ["Transceiver Settings", "Audio Filters", "System Logs"]

    # 4. 🔑 NESTED TAB FRAME GENERATION PASS:
    # Loops through the strings, adds the tabs, and nests an sCTkFrame containing
    # an sCTkLabelPrimary placeholder inside every viewport page cleanly!
    for page_name in tab_pages:
        # Add the structural landing track tab layer to the widget chassis
        widget.add(page_name)

        # Grab the container reference object assigned to this specific tab page.
        # NOTE: this now returns an sCTkFrame page wrapper, not the native
        # ctk.CTkFrame. The native shell is still reachable underneath.
        page_viewport = widget.tab(page_name)

        # Mount an inner sCTkFrame container capsule to pad out the sub-tab view workspace
        inner_frame = sCTkFrame(page_viewport, border_width=1, corner_radius=8)
        inner_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Drop a high-visibility sCTkLabelPrimary component right in the center slot of the sub-frame
        test_label = sCTkLabelPrimary(inner_frame, text=f"Test Contents — {page_name}")
        test_label.pack(expand=True, fill="none", padx=20, pady=20)

    # =====================================================================
    # 🔑 PAGE-WRAPPER VERIFICATION HOOKS
    # =====================================================================
    first = tab_pages[0]
    print("=== Page wrapper ===")
    print(f"  tab() returns:        {type(widget.tab(first)).__name__}")
    print(f"  stable across calls:  {widget.tab(first) is widget.tab(first)}")
    print(f"  native shell beneath: {type(ctk.CTkTabview.tab(widget, first)).__name__}")
    print("=== State API ===")
    print(f"  state():              {widget.state()}")
    print(f"  get_state():          {widget.get_state()}")
    print(f"  cget('state'):        {widget.cget('state')}")
    print(f"  configure('state'):   {widget.configure('state')}")

    # =====================================================================
    # 🛠️ INTERACTIVE BENCH OPERATION CONTROLLERS
    # =====================================================================
    def toggle_tab_lock():
        """Toggles active data page switches and flattens tab button fills."""
        current = widget.state()
        target = "disabled" if current == "normal" else "normal"

        # Deliberately routed through configure() rather than state(): this
        # path silently did NOTHING before this widget gained a configure()
        # override. Both APIs should now agree.
        widget.configure(state=target)

        btn_lock.configure(
            text="Unlock Tabview Navigation" if target == "disabled" else "Lock Tabview (Set 'disabled')")
        print(f"Logged State Verification Hook -> state()={widget.state()}  cget={widget.cget('state')}")

    def toggle_temp_page():
        """Exercises runtime add() plus delete()'s wrapper teardown."""
        if "Scratch Pad" in widget._sctk_pages:
            widget.delete("Scratch Pad")
            print(f"Deleted -> registry now: {list(widget._sctk_pages.keys())}")
            btn_temp.configure(text="Add Runtime Page")
        else:
            page = widget.add("Scratch Pad")
            sCTkLabelPrimary(page, text="Created at runtime").pack(expand=True, padx=20, pady=20)
            print(f"Added {type(page).__name__} -> registry now: {list(widget._sctk_pages.keys())}")
            btn_temp.configure(text="Delete Runtime Page")

    def toggle_skin_preference():
        """Toggles between Light and Dark interface appearance preferences."""
        ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")

    # Arrange test interaction buttons horizontally across the lower tray tray area
    control_tray = sCTkFrame(root, fg_color="transparent")
    control_tray.pack(side="bottom", fill="x", padx=20, pady=(0, 15))

    btn_lock = sCTkButtonPrimary(control_tray, text="Lock Tabview (Set 'disabled')", command=toggle_tab_lock)
    btn_lock.pack(side="left", expand=True, padx=4)

    btn_temp = sCTkButtonPrimary(control_tray, text="Add Runtime Page", command=toggle_temp_page)
    btn_temp.pack(side="left", expand=True, padx=4)

    btn_skin = sCTkButtonPrimary(control_tray, text="Toggle UI Light/Dark Appearance", command=toggle_skin_preference)
    btn_skin.pack(side="right", expand=True, padx=4)

    root.mainloop()
