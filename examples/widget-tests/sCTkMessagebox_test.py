#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Messagebox
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary,sCTk, sCTkMessagebox

if __name__ == "__main__":
    root = sCTk()
    root.geometry("300x520")
    root.title("Message Example")

    long_msg = "Warning: The VFO phase lock loop has lost lock synchronization with the master synthesizer. Override?"

    # 🚀 Clean functional callbacks using the messagebox namespace!
    def trigger_info_ask():
        print(f"Feedback: {sCTkMessagebox.askyesno('Info Query', 'Log parameter data?', yes_text='Log', no_text='Skip', master=root)}")

    def trigger_warning_ask():
        print(f"Feedback: {sCTkMessagebox.askwarningyesno('Band Switch', long_msg, yes_text='Override', no_text='Drop', width=450, master=root)}")

    def trigger_error_ask():
        print(f"Feedback: {sCTkMessagebox.askerroryesno('Fatal Error', 'Attempt buffer cold reset?', yes_text='Reset', no_text='Quit', master=root)}")

    # 🚀 Native drop-in style execution pass!
    sCTkButtonPrimary(root, text="Test Info (OK)", width=200, command=lambda: sCTkMessagebox.showinfo("Message Example", "Short statement alert.", ok_text="Acknowledge", master=root)).pack(pady=8)
    sCTkButtonPrimary(root, text="Test Info (Yes/No)", width=200, command=trigger_info_ask).pack(pady=(8, 25))
    sCTkButtonPrimary(root, text="Test Warning (OK)", width=200, command=lambda: sCTkMessagebox.showwarning("Warning", "Listen carefully", ok_text="Proceed", master=root)).pack(pady=8)
    sCTkButtonPrimary(root, text="Test Warning (Yes/No)", width=200, command=trigger_warning_ask).pack(pady=(8, 25))
    sCTkButtonPrimary(root, text="Test Error (OK)", width=200, command=lambda: sCTkMessagebox.showerror("Error", "Dead meat", ok_text="Close", master=root)).pack(pady=8)
    sCTkButtonPrimary(root, text="Test Error (Yes/No)", width=200, command=trigger_error_ask).pack(pady=8)

    root.mainloop()