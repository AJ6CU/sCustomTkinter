#!/usr/bin/python3
import customtkinter as ctk
from scustomtkinter import sCTk, sCTkFrame, sCTkButtonPrimary, sCTkOptionMenuPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("420x260")
    root.title("OptionMenu border test")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    menu = sCTkOptionMenuPrimary(base, values=["Alpha", "Beta", "Gamma"])
    menu.pack(pady=20)

    def toggle_state():
        target = "disabled" if menu.get_state() == "normal" else "normal"
        menu.state(target)
        btn_state.configure(text="Enable" if target == "disabled" else "Disable")

    def thicker():
        menu.configure(border_width=menu.cget("border_width") + 1)
        print("coords 8:", menu._canvas.coords(8))
        print("coords 6:", menu._canvas.coords(6))
        print("item 6 width:", menu._canvas.itemcget(6, "width"))

        print("width:", menu.cget("border_width"))
        print("left items :", menu._canvas.find_withtag("border_parts_left"))
        print("right items:", menu._canvas.find_withtag("border_parts_right"))
        print("all tags   :", set(t for i in menu._canvas.find_all()
                                  for t in menu._canvas.gettags(i)))
        print("stack:", [(i, menu._canvas.gettags(i)[0]) for i in menu._canvas.find_all()])
        print("drawing method:", menu._draw_engine.preferred_drawing_method)
        print("inner 3:", menu._canvas.coords(3), " width:", menu._canvas.itemcget(3, "width"))

    def toggle_mode():
        ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")

    btn_state = sCTkButtonPrimary(base, text="Disable", command=toggle_state)
    btn_state.pack(pady=4)
    sCTkButtonPrimary(base, text="Border +1", command=thicker).pack(pady=4)
    sCTkButtonPrimary(base, text="Toggle Light/Dark", command=toggle_mode).pack(pady=4)

    root.mainloop()