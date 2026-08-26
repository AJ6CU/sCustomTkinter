#!/usr/bin/python3
"""
sCTkProgressBar - Piece 1 of 2

A custom, theme-compliant system progression indicator bar widget.
Inherits cleanly and directly from ctk.CTkProgressBar to preserve 100% of native
CustomTkinter features, theme tracking loops, and real-time state updates.
"""
import os
import customtkinter as ctk
from ThemeableWidget import ThemeableWidget

class sCTkProgressBar(ctk.CTkProgressBar, ThemeableWidget):
    def __init__(self, master=None, **kwargs):
        # 1. INITIAL RUNTIME SCRUB: Safely shield native frame from state validation checks
        state_init = kwargs.pop("state", "normal")

        # 2. ENFORCE SYSTEM REGISTRY INTERACTION:
        ThemeableWidget.__init__(self, kwargs)

        # 3. 🛠️ THE MUTATION SAFEGUARD DEEP COPY SHIELD:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # Remove custom parameters from final_kw to prevent parent collisions
        self.final_kw.pop("state", None)

        # 4. Initialize CustomTkinter natively with the clean final kwargs array safely
        super().__init__(master, **self.final_kw)

        # 5. ROUTE TO CONFIG: Safely pass parameters through your validation engine
        self._state_str = "normal"
        self.state(state_init)

        # 🔑 6. REGISTER LIFECYCLE HANDSHAKE HOOK: Pushes notifications up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Processes Pygubu designer queries and manages state changes safely."""
        if args and len(args) == 1:
            pname = args if isinstance(args, (list, tuple)) else args
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "progress_color", "border_color"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(*args, **kwargs)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        if kwargs:
            super().configure(**kwargs)
            self._update_current_visual_state()
    def cget(self, attribute_name: str) -> any:
        """Safely intercept custom properties like 'state' from throwing errors."""
        if str(attribute_name).lower() == "state":
            return self.state()
        return super().cget(attribute_name)

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring active or disabled lanes repaint fluidly on theme shifts."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._update_current_visual_state()

    def get_state(self) -> str:
        """Explicit getter synchronized with your standalone test harness script assertions."""
        return self.state()

    def state(self, mode: str = None) -> str:
        """Dedicated polymorphic state manager forcing internal indicator lane repaints."""
        if mode is None:
            return str(getattr(self, "_state_str", "normal")).lower()

        target_state = mode.lower()
        self._state_str = target_state
        self._update_current_visual_state()
        return self._state_str

    def _update_current_visual_state(self):
        """MASTER VISUAL ROUTER: Automatically extracts and resolves properties out of protected memory."""
        is_disabled = getattr(self, "_state_str", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        config_payload = {}
        for key in ("fg_color", "progress_color", "border_color", "border_width", "corner_radius"):
            val = target_map.get(key)
            if val is not None:
                config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

        if config_payload:
            super().configure(**config_payload)

    def bind(self, sequence=None, command=None, add=None):
        if "PYGUBU_DESIGNER_RUNNING" in os.environ:
            return None
        return super().bind(sequence, command, add)


# =====================================================================
# 🛠️ TESTING HARNESS SETUP
# =====================================================================
if __name__ == "__main__":
    import sCTkThemes
    from sCTkFrame import sCTkFrame
    from sCTkButtonPrimary import sCTkButtonPrimary
    from sCTkButtonSecondary import sCTkButtonSecondary
    from sCTkLabelSecondary import sCTkLabelSecondary

    root = ctk.CTk()
    root.geometry("450x260")
    root.title("sCTkProgressBar Interactive Testing Deck")

    sCTkThemes.apply_sCTkThemes()

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    initial_val = 0.45
    lbl_status = sCTkLabelSecondary(
        base,
        text=f"Telemetry Progress Output: {int(initial_val * 100)}% / 100%"
    )
    lbl_status.pack(pady=(10, 5))

    widget = sCTkProgressBar(base)
    widget.pack(expand=False, fill="x", padx=40, pady=10)
    widget.set(initial_val)

    def step_progress():
        if widget.get_state() == "disabled":
            print("⚠️ Cannot modify progress channel: Widget is currently locked!")
            return

        current_val = widget.get()
        next_val = current_val + 0.05
        if next_val > 1.0:
            next_val = 0.0

        widget.set(next_val)
        lbl_status.configure(text=f"Telemetry Progress Output: {int(next_val * 100)}% / 100%")

    btn_step = sCTkButtonPrimary(base, text="Step Telemetry Track (+5%)", command=step_progress)
    btn_step.pack(pady=(5, 5))

    def toggle_operational_lock():
        current_mode = widget.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        widget.configure(state=target)
        btn_lock.configure(text="Lock Indicator Track" if target == "normal" else "Unlock Indicator Track")
        btn_step.configure(state=target)

    btn_lock = sCTkButtonPrimary(base, text="Lock Indicator Track", command=toggle_operational_lock)
    btn_lock.pack(side="bottom", pady=(5, 10))

    def toggle_skin_mode():
        current_skin = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_skin == "Dark" else "Dark")

    btn_theme = sCTkButtonSecondary(base, text="Simulate Global Theme Shift", command=toggle_skin_mode)
    btn_theme.pack(side="bottom", pady=5)

    root.mainloop()
