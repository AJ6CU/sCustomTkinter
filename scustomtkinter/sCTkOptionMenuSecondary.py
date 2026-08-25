#!/usr/bin/python3
"""
sCTkOptionMenuSecondary - Piece 1 of 2

A custom, theme-compliant secondary option selection menu dropdown widget.
Inherits cleanly and directly from ctk.CTkFrame acting as a cleanly bordered composite
OptionMenu to preserve 100% of native CustomTkinter feature loops.
"""
import customtkinter as ctk
from ThemeableWidget import ThemeableWidget

class sCTkOptionMenuSecondary(ctk.CTkFrame, ThemeableWidget):

    def __init__(self, master=None, width=160, height=28, **kw):
        # 1. PARAMETER POPPING: Capture menu-specific operational attributes early [1]
        values = kw.pop("values", [""])
        command = kw.pop("command", None)
        variable = kw.pop("variable", None)

        # 2. Assign standard constructor fallback geometric limits directly [1]
        kw.setdefault("width", width)
        kw.setdefault("height", height)

        # 3. Fire our shared theme logic first to resolve global configurations [1]
        ThemeableWidget.__init__(self, kw)

        # 4. 🛠️ THE MUTATION SAFEGUARD DEEP COPY:
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 5. 🛠️ THE INVERSION BLACKLIST FILTER:
        MENU_KEYS = {
            "font", "dropdown_font", "text_color", "disabled_text_color",
            "dropdown_fg_color", "dropdown_text_color", "dropdown_hover_color",
            "button_hover_color"
        }
        self._menu_theme_kw = {}
        for key in MENU_KEYS:
            if key in self.final_kw:
                self._menu_theme_kw[key] = self.final_kw.pop(key)

        # 6. Initialize the native ctk.CTkFrame container using pure filtered frame options [1]
        super().__init__(master, **self.final_kw)

        # 7. Initialize inner CustomTkinter option menu using cleanly popped parameters [1]
        self._menu = ctk.CTkOptionMenu(
            self,
            values=values,
            command=command,
            variable=variable
        )
        self._menu.pack(expand=True, fill="both", padx=2, pady=2)

        # 8. Execute clean layout matching tracks smoothly [1]
        self._custom_current_state = "normal"
        self._update_current_visual_state()

        # 🔑 9. REGISTER LIFECYCLE HANDSHAKE HOOK: Pushes notifications up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

    def configure(self, *args, **kwargs):
        """Handles Pygubu designer queries and manages composite state updates safely [1]."""
        if args and len(args) == 1:
            pname = args[0]
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "border_color", "text_color", "width", "height"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(pname)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if "values" in kwargs: self._menu.configure(values=kwargs.pop("values"))
        if "command" in kwargs: self._menu.configure(command=kwargs.pop("command"))
        if "variable" in kwargs: self._menu.configure(variable=kwargs.pop("variable"))

        if "state" in kwargs:
            self.state(kwargs.pop("state"))

        for k, v in list(kwargs.items()):
            if v == "": kwargs.pop(k)

        if kwargs:
            super().configure(**kwargs)
        return None

    config = configure
    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring active or disabled dropdown blocks repaint fluidly on theme shifts [1]."""
        if hasattr(super(), "_set_appearance_mode"):
            try: super()._set_appearance_mode(mode_string)
            except Exception: pass
        self._update_current_visual_state()

    def get_state(self):
        """Explicit getter to return the current composite state string safely [1]."""
        return str(self.state()).lower()

    def state(self, mode=None):
        """Dedicated option menu composite state controller [1]."""
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
        elif mode == "disabled":
            self._custom_current_state = "disabled"

        self._update_current_visual_state()
        return self._custom_current_state

    def _update_current_visual_state(self):
        """
        MASTER VISUAL ROUTER FIXED:
        🔑 REPAINT LOGIC DYNAMIC MAP: Loops fluidly across both modes uniformly,
        ensuring disabled dropdown elements swap background tones on theme switches!
        """
        is_disabled = getattr(self, "_custom_current_state", "normal") == "disabled"
        target_map = self._custom_disabled_map if is_disabled else self._local_defaults

        # 1. Update parent frame container card shapes [1]
        frame_config = {}
        for key in ("border_color", "fg_color", "border_width", "corner_radius"):
            val = target_map.get(key)
            if val is not None:
                frame_config[key] = self._resolve_color(val) if "color" in key or "fg" in key else val
        if frame_config:
            super().configure(**frame_config)

        # 2. Update inner menu dropdown shapes cleanly out of the active registry directory maps [1]
        menu_payload = {}
        for key in ("font", "dropdown_font", "dropdown_fg_color", "dropdown_text_color", "dropdown_hover_color", "button_hover_color"):
            val = self._menu_theme_kw.get(key)
            if val is not None:
                menu_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

        if is_disabled:
            d_fg = self._resolve_color(self._custom_disabled_map.get("fg_color", ["#F3F4F6", "#1F2937"]))
            d_txt = self._resolve_color(self._custom_disabled_map.get("text_color", ["#94A3B8", "#64748B"]))
            menu_payload.update({
                "fg_color": d_fg, "button_color": d_fg, "button_hover_color": d_fg, "text_color": d_txt, "state": "disabled"
            })
        else:
            n_fg = self._resolve_color(self._local_defaults.get("fg_color", "transparent"))
            n_txt = self._resolve_color(self._local_defaults.get("text_color", ["#475569", "#94A3B8"]))
            menu_payload.update({
                "fg_color": n_fg, "button_color": n_fg, "button_hover_color": n_fg, "text_color": n_txt, "state": "normal"
            })

        if menu_payload:
            self._menu.configure(**menu_payload)

    def update_list(self, new_values: list, default_index: int = 0):
        """Safely updates the items list and resets the visible value [1]."""
        if not new_values:
            self._menu.configure(values=[""])
            self._menu.set("")
            return

        self._menu.configure(values=new_values)
        if default_index < len(new_values):
            self._menu.set(new_values[default_index])
        else:
            self._menu.set(new_values[0])

    def set(self, value: str): self._menu.set(value)
    def get(self) -> str: return self._menu.get()

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
if __name__ == "__main__":
    import sCTkThemes
    from sCTkFrame import sCTkFrame
    from sCTkLabelSecondary import sCTkLabelSecondary

    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("450x320")
    root.title("sCTkOptionMenuSecondary Real-Time Validation Bench")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    lbl_monitor = sCTkLabelSecondary(base, text="Active Selection: Filter: Narrow")
    lbl_monitor.pack(pady=10)

    menu_field = sCTkOptionMenuSecondary(
        base,
        values=["Filter: Narrow", "Filter: Medium", "Filter: Wide"],
        command=lambda choice: lbl_monitor.configure(text=f"Active Selection: {choice}")
    )
    menu_field.pack(expand=False, fill="x", padx=40, pady=10)
    menu_field.set("Filter: Narrow")

    def toggle_operational_state():
        current_mode = menu_field.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        menu_field.configure(state=target)
        btn_toggle.configure(text="Lock Dropdown (Set 'disabled')" if target == "normal" else "Unlock Dropdown (Set 'normal')")

    def toggle_skin_mode():
        current_skin = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_skin == "Dark" else "Dark")

    btn_toggle = ctk.CTkButton(base, text="Lock Dropdown (Set 'disabled')", command=toggle_operational_state)
    btn_toggle.pack(side="bottom", pady=5)

    btn_theme = ctk.CTkButton(base, text="Simulate Global Theme Shift", command=toggle_skin_mode)
    btn_theme.pack(side="bottom", pady=5)

    root.mainloop()
