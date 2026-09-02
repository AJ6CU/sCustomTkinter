#!/usr/bin/python3

from scustomtkinter import sCTkButtonPrimary, sCTkLabelPrimary, sCTk, sCTkFrame


if __name__ == "__main__":

    root = sCTk()
    root.geometry("500x300")
    root.title("sCTkFrame Container Validation Bench")

    # Instantiate your custom theme-compliant frame element chassis
    base_container = sCTkFrame(root, border_width=2)
    base_container.pack(expand=True, fill="both", padx=30, pady=30)
#
#     # Add a simple sub-element child widget to verify structural clipping layouts
    lbl_marker = sCTkLabelPrimary(base_container, text="FRAME BACKPLANE CONTAINER OPERATIONAL\n"+
                                  "Border Visible for Testing Purposes only")
    lbl_marker.pack(expand=True)

    root.mainloop()

