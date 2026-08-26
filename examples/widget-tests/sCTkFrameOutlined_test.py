#!/usr/bin/python3
"""
sCTkFrameOutlined

A clean, theme-compliant outlined CustomTkinter container frame.
Acts as a passive layout group following native Tkinter patterns.
"""
import customtkinter as ctk
from ThemeableWidget import ThemeableWidget


class sCTkFrameOutlined(ctk.CTkFrame, ThemeableWidget):
    properties = frozenset()

    def __init__(self, master=None, **kwargs):
        # 1. Fire our shared theme logic first. It automatically finds "sCTkFrameOutlined" inside themes.json
        ThemeableWidget.__init__(self, kwargs)

        # 2. 🛠️ THE MUTATION SAFEGUARD DEEP COPY:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 3. Initialize CustomTkinter CTkFrame natively with final clean kwargs safely
        super().__init__(master, **self.final_kw)

        self._custom_current_state = "normal"

        # 🔑 4. REGISTER LIFECYCLE HANDSHAKE HOOK: Pushes notifications up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring active or desaturated outlines follow theme switches fluidly."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._update_current_visual_state()

    def configure(self, *args, **kwargs):
        """Handles Pygubu designer queries and manages container configurations safely."""
        if args and len(args) == 1:
            pname = args if isinstance(args, (list, tuple)) else args
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "border_color"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(
                    pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(pname)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if "state" in kwargs:
            target_state = kwargs.pop("state")
            self.state(target_state)

        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        if kwargs:
            return super().configure(**kwargs)
        return None

    config = configure

    def get_state(self):
        """Explicit getter synchronized with your standalone test harness script assertions."""
        return self.state()

    def state(self, mode: str = None):
        """Dedicated container frame state controller."""
        if mode is None:
            return getattr(self, "_custom_current_state", "normal")

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
            self._update_current_visual_state()

        elif mode == "disabled":
            # 🛠️ THE ABSORPTION GUARD:
            # We bypass calling super().configure(state="disabled") because plain frames
            # don't support an execution state parameter. Instead, we safely strip the
            # key and apply our custom faded gray outline styling rules directly.
            super_payload = {}
            for key in ("fg_color", "border_color"):
                val = self._custom_disabled_map.get(key)
                if val is not None:
                    super_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

            if super_payload:
                super().configure(**super_payload)

            self._custom_current_state = "disabled"
        return self._custom_current_state

    def _update_current_visual_state(self):
        """MASTER VISUAL ROUTER: Restores active theme layouts out of memory."""
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "border_color", "border_width", "corner_radius"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

        if config_payload:
            super().configure(**config_payload)


# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
if __name__ == "__main__":
    import sCTkThemes
    from sCTkLabelSecondary import sCTkLabelSecondary
    from sCTkEntryPrimary import sCTkEntryPrimary

    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.title("Passive Outline Frame Test Suite")
    root.geometry("450x300")

    frame_group = sCTkFrameOutlined(root, border_width=2)
    frame_group.pack(fill="both", expand=True, padx=20, pady=20)

    lbl_title = sCTkLabelSecondary(frame_group, text="TRANSCEIVER FREQUENCY PRESET PROFILE")
    lbl_title.pack(pady=(12, 4), padx=10, fill="x")

    mock_entry = sCTkEntryPrimary(frame_group, placeholder_text="Standard data field...")
    mock_entry.pack(pady=10, padx=25, fill="x")


    def toggle_frame_states():
        """Toggles the outlined card panel and cascades the state change down to child widgets, skipping the trigger."""
        current_mode = frame_group.get_state()
        target = "disabled" if current_mode == "normal" else "normal"

        frame_group.configure(state=target)

        for child in frame_group.winfo_children():
            if child == btn_toggle:
                continue
            if hasattr(child, "configure"):
                child.configure(state=target)

        btn_toggle.configure(
            text="Lock Outline Deck (Set 'disabled')" if target == "normal" else "Unlock Outline Deck (Set 'normal')")
        print(f"Logged Verification Hook -> frame_group.get_state() = {frame_group.get_state()}")


    btn_toggle = ctk.CTkButton(frame_group, text="Lock Outline Deck (Set 'disabled')", command=toggle_frame_states)
    btn_toggle.pack(side="bottom", pady=15)

    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    print(f"Initial Outline Frame State = {frame_group.get_state().upper()}")
    print("========================================\n")

    root.mainloop()
