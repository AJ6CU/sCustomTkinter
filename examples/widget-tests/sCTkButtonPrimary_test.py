# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Primary Button
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary,sCTk


if __name__ == "__main__":

    root = sCTk()
    root.geometry("450x340")
    root.title("Primary Command Button Real-Time Validation Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    command_btn = sCTkButtonPrimary(base, text="Primary Action Control")
    command_btn.pack(expand=False, fill="x", padx=40, pady=10)

    def toggle_system_alarm():
        new_alarm_mode = not command_btn.is_alarm
        command_btn.set_alarm_state(new_alarm_mode)
        btn_alarm_switch.configure(text="System Alarm (ACTIVE - Click to Clear)" if new_alarm_mode else "System Alarm")

    def toggle_disabled_lock():
        target = "disabled" if command_btn.get_state() == "normal" else "normal"
        command_btn.configure(state=target)
        btn_lock.configure(text="Lock Button (Set 'disabled')" if target == "normal" else "Unlock Button (Set 'normal')")

    def toggle_skin_mode():
        current_skin = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_skin == "Dark" else "Dark")

    btn_alarm_switch = sCTkButtonPrimary(base, text="System Alarm", command=toggle_system_alarm)
    btn_alarm_switch.pack(pady=5)

    btn_lock = sCTkButtonPrimary(base, text="Lock Button (Set 'disabled')", command=toggle_disabled_lock)
    btn_lock.pack(pady=5)

    btn_theme = sCTkButtonPrimary(base, text="Simulate Global Theme Shift", command=toggle_skin_mode)
    btn_theme.pack(side="bottom", pady=10)

    root.mainloop()
